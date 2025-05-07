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

    # Número de empleados asignados a cada tarea cada día
    x = mdl.integer_var_dict([(t, d) for t in tareas for d in dias], lb=0, ub=len(empleados), name="x")

    # Total de empleados trabajando cada día
    trabaja = mdl.integer_var_dict(dias, lb=0, ub=len(empleados), name="trabaja")

    # Relación: empleados trabajando = suma de tareas ese día
    for d in dias:
        mdl.add_constraint(
            trabaja[d] == mdl.sum(x[t, d] for t in tareas),
            f"trabajadores_dia_{d}"
        )
        mdl.add_constraint(
            trabaja[d] <= len(empleados),
            f"limite_empleados_{d}"
        )

    # Eficiencia
    for i, d in enumerate(dias):
        for t in tareas:
            if (t, d) not in demanda:
                continue
            prod_base = x[t, d] * eficiencia[t] * jornada_horas
            if i > 0:
                # Aumenta 10% si cambia de tarea respecto al día anterior
                prod_base *= (1 + 0.1)

            mdl.add_constraint(
                prod_base >= demanda[(t, d)],
                f"demanda_{t}_{d}"
            )

    total_costo = mdl.sum(trabaja[d] * costo_diario for d in dias)
    mdl.minimize(total_costo)

    return mdl, x, trabaja


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


def solve_model(mdl, x, trabaja):
    solution = mdl.solve()

    if not solution:
        print("No se pudo resolver el modelo.")
        return

    print(f"\n Costo total mínimo: ${mdl.objective_value}\n")

    print("Asignación de empleados por tarea y día:")
    for (t, d), var in x.items():
        cantidad = int(round(var.solution_value))
        if cantidad > 0:
            print(f"{cantidad} empleados hacen '{t}' el {d}")

    print("\n Empleados trabajando por día:")
    for d, var in trabaja.items():
        cantidad = int(round(var.solution_value))
        print(f" {d}: {cantidad} empleados")

