# Import libs
import sys
from docplex.mp.model import Model
from docplex.mp.constants import ComparisonType

from data_related_utils import BIG_M

#def load_data():
from .data import unpack_data

# Create the model with constraints and objective
def create_model(data_dict):
    name, products, resources, consumptions = unpack_data(data_dict)
    mdl = Model(name)
    
    prod_names = [prod[0] for prod in products]
    production_vars = mdl.continuous_var_dict(prod_names, name=prod_names)#, key_format="%s")

    # Debug
    # print(f"products: {products}")
    # print(f"prod_names: {prod_names}")
    # print(f"production_vars: {production_vars}")
    # print(f"resources: {resources}")
    # print(f"consumptions: {consumptions}")
    # print(f"")
    # print(f"production_vars['A']: {production_vars['A']}")
    # --- constraints ---

    # resources disp equipo and consumptions
    mdl.add_constraints((mdl.sum(production_vars[p[0]] * consumptions[res[0]][products.index(p)] for p in products) <= res[1], 'Disp_%s' % res[0]) for res in resources)

    # max demand
    mdl.add_constraints((production_vars[p[0]] <= p[2], 'DemandMax_%s' % p[0]) for p in products)

    # min demand
    mdl.add_constraints((production_vars[p[0]] >= p[3], 'DemandMin_%s' % p[0]) for p in products)

    # --- print information ---
    mdl.print_information()

    total_benefit = mdl.sum(production_vars[p[0]] * p[1] for p in products)

    # --- set the objective ---
    mdl.maximize(total_benefit)

    return mdl, production_vars, products

# Print model human friendly name, restrictions and objective.
# Do not print restrictions such as ">=0" nor "<= inf".
def print_model(mdl):

    print("--------------------")
    print(f"Model: {mdl.name}")

    print("Constraints:")

    # Print all constraints, except for ">= 0" and "<= inf"
    for constraint in mdl.iter_constraints():
        # Only attemp to get rhs if constraint has that attr
        # (there exist other constraint types that do not have it)
        if hasattr(constraint, "rhs"):
           
            # This way of comparing is the only way that works (not "!=", do not attemp "==")
            le_to_inf = constraint.rhs.equals(BIG_M) and constraint.sense == ComparisonType.LE
            if le_to_inf: # ignore "<= inf"
                continue
            
            ge_to_zero = constraint.sense == ComparisonType.GE and constraint.rhs.equals(0)
            if ge_to_zero: # ignore ">= 0"
                continue

            print(f"   {constraint}")

    print(f"Objective: {mdl.objective_expr}")
    print(f" {mdl.objective_sense.name}")
    
    print("--------------------")

# Solve the model
def solve_model(mdl, production_vars, products):
    solution = mdl.solve()

    if not solution:
        print("Model cannot be solved.")
        sys.exit(1)

    obj = mdl.objective_value

    print("* Production model solved with objective: {:g}".format(obj))
    print("* Total benefit=%g" % mdl.objective_value)
    for p in products:
        print("Production of {product}: {prod_var}".format(product=p[0], prod_var=production_vars[p[0]].solution_value))
