# common_model.py

from docplex.mp.model import Model
from docplex.mp.constants import ComparisonType
from .data_2_17 import unpack_data
from data_related_utils import BIG_M

def create_model(data_dict):
    (
        name, empleados, tareas, dias,
        eficiencia, demanda, jornada_horas,
        costo_diario
    ) = unpack_data(data_dict)

    mdl = Model(name)

    y = mdl.binary_var_dict([(e, t, d) for e in empleados for t in tareas for d in dias], name="y")

    for e in empleados:
        for d in dias:
            mdl.add_constraint(
                mdl.sum(y[e, t, d] for t in tareas) <= 1,
                f"unica_tarea_{e}_{d}"
            )

    x = {(t, d): mdl.sum(y[e, t, d] for e in empleados) for t in tareas for d in dias}

    trabaja = {d: mdl.sum(y[e, t, d] for e in empleados for t in tareas) for d in dias}

    for d in dias:
        mdl.add_constraint(
            trabaja[d] <= len(empleados),
            f"limite_empleados_{d}"
        )

    for i, d in enumerate(dias):
        for t in tareas:
            if (t, d) not in demanda:
                continue
            prod_base = x[(t, d)] * eficiencia[t] * jornada_horas
            if i > 0:
                prod_base *= (1 + 0.1)
            mdl.add_constraint(
                prod_base >= demanda[(t, d)],
                f"demanda_{t}_{d}"
            )

    total_costo = mdl.sum(trabaja[d] * costo_diario for d in dias)
    mdl.minimize(total_costo)

    return mdl, y, trabaja


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


def solve_model(mdl, y, trabaja):
    solution = mdl.solve()

    if not solution:
        print("No se pudo resolver el modelo.")
        return

    print(f"\n Costo total mínimo: ${mdl.objective_value}\n")

    print("Asignación de empleados por tarea y día:")
    # Mostrar qué empleado hace qué tarea cada día
    for (e, t, d), var in y.items():
        if int(round(var.solution_value)) == 1:
            print(f"Empleado {e} hace '{t}' el {d}")

    print("\n Empleados trabajando por día:")
    for d, var in trabaja.items():
        cantidad = int(round(var.solution_value))
        print(f" {d}: {cantidad} empleados")

