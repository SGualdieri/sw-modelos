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
    
    # Crear variables de producción, de acuerdo con los productos
    prod_names = [prod[0] for prod in products]
    production_vars = mdl.continuous_var_dict(prod_names, name=prod_names)

    # --- Función objetivo ---
    total_benefit = mdl.sum(production_vars[p[0]] * p[1] for p in products)
    mdl.maximize(total_benefit)

    # --- Restricciones ---

    # Disponibilidad de lana
    mdl.add_constraint(1.6 * production_vars['A'] + 1.2 * production_vars['C'] <= 20, 'LanaMejoradaDisp')
    mdl.add_constraint(1.8 * production_vars['B'] <= 36, 'LanaNormalDisp')

    # Relación de productos tipo B
    mdl.add_constraint(production_vars['B'] == production_vars['B1'] + production_vars['B2'], 'RelB')

    # Restricciones de disponibilidad de máquinas
    mdl.add_constraint(5 * production_vars['A'] + 6 * production_vars['B1'] <= 80, 'MaquinasDisp1')
    mdl.add_constraint(4 * production_vars['B2'] + 4 * production_vars['C'] <= 80, 'MaquinasDisp2')

    # Restricciones de demanda máxima y mínima
    mdl.add_constraints((production_vars[p[0]] <= p[2], 'DemandMax_%s' % p[0]) for p in products)
    mdl.add_constraints((production_vars[p[0]] >= p[3], 'DemandMin_%s' % p[0]) for p in products)

    # --- Mostrar la información del modelo ---
    mdl.print_information()

    # --- Retornar modelo y variables ---
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
