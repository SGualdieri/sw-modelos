# Import libs
import sys
from docplex.mp.model import Model

#def load_data():
from .data import unpack_data

# Create the model with constraints and objective
def create_model(data_dict):
    name, products, resources, consumptions = unpack_data(data_dict)
    mdl = Model(name)

    produccion_vars = mdl.continuous_var_dict(products, name='produccion')

    # --- constraints ---

    # resources disp equipo and consumptions
    mdl.add_constraints((mdl.sum(produccion_vars[p] * consumptions[res[0]][products.index(p)] for p in products) <= res[1], 'Disp_%s' % res[0]) for res in resources)

    # max demand
    mdl.add_constraints((produccion_vars[p] <= p[2], 'DemandMax_%s' % p[0]) for p in products)

    # min demand
    mdl.add_constraints((produccion_vars[p] >= p[3], 'DemandMin_%s' % p[0]) for p in products)

    # --- print information ---
    mdl.print_information()

    total_benefit = mdl.sum(produccion_vars[p] * p[1] for p in products)

    # --- set the objective ---
    mdl.maximize(total_benefit)

    return mdl, produccion_vars, products

# Solve the model
def solve_model(mdl, produccion_vars, products):
    solution = mdl.solve()

    if not solution:
        print("Model cannot be solved.")
        sys.exit(1)

    obj = mdl.objective_value

    print("* Production model solved with objective: {:g}".format(obj))
    print("* Total benefit=%g" % mdl.objective_value)
    for p in products:
        print("Production of {product}: {prod_var}".format(product=p[0], prod_var=produccion_vars[p].solution_value))
