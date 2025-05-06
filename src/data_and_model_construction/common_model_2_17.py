# Import libs
import sys
from docplex.mp.model import Model
from docplex.mp.constants import ComparisonType

from data_related_utils import BIG_M

#def load_data():
from .data_2_17 import unpack_data


def create_model(data_dict):
    name, dias, tareas, eficiencia, products, resources, consumptions = unpack_data(data_dict)
    
    tareas_cap = set(p[0].split('_')[0] for p in products)
    tareas = list(tareas_cap) 
    mdl = Model(name)

    prod_names = [p[0] for p in products]
    productos_dict = {p[0]: p for p in products}

    trabajadores = {}
    x = {}

    for d in dias:
        for t in tareas:
            var_name = f"{t.capitalize()}_{d}"
            if var_name in prod_names:
                if d == "viernes":
                    trabajadores[var_name] = mdl.integer_var(name=f"trab_{var_name}")
                else:
                    for t_ant in tareas:
                        x[(t, d, t_ant)] = mdl.integer_var(name=f"x_{t}_{d}_de_{t_ant}")

    for d in dias:
        for t in tareas:
            var_name = f"{t.capitalize()}_{d}"
            if var_name in prod_names and d != "viernes":
                trabajadores[var_name] = mdl.sum(x[(t, d, t_ant)] for t_ant in tareas)

    for d in dias:
        for t in tareas:
            p_name = f"{t.capitalize()}_{d}"
            if p_name not in prod_names:
                continue

            eff = eficiencia[t.lower()]
            if d == "viernes":
                produccion = trabajadores[p_name] * eff * 8
            else:
                produccion = mdl.sum(
                    x[(t, d, t_ant)] * (eff * 1.1 * 8 if t != t_ant else eff * 8)
                    for t_ant in tareas
                )

            _, _, dmax, dmin = productos_dict[p_name]
            mdl.add_constraint(produccion >= dmin, f"DemMin_{p_name}")
            if dmax != BIG_M:
                mdl.add_constraint(produccion <= dmax, f"DemMax_{p_name}")

    for d in dias:
        tareas_dia = [f"{t}_{d}" for t in tareas if f"{t}_{d}" in trabajadores]
        suma_trab = mdl.sum(trabajadores[t] for t in tareas_dia)
        mdl.add_constraint(suma_trab <= 18, f"Limite_{d}")

    costo_total = mdl.sum(trabajadores[p[0]] * 12 for p in products if p[0] in trabajadores)
    mdl.minimize(costo_total)

    return mdl, trabajadores, products


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
