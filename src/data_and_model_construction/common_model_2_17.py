# common_model.py

from docplex.mp.model import Model
from docplex.mp.constants import ComparisonType
from .data_2_17 import unpack_data

def create_model(data_dict):
    (
        name, empleados, tareas, dias,
        eficiencia, demanda, jornada_horas,
        costo_diario, bonificacion
    ) = unpack_data(data_dict)

    mdl = Model(name)

    # --- VARIABLES ---
    x = mdl.binary_var_cube(empleados, tareas, dias, name="x")
    trabaja = mdl.binary_var_matrix(empleados, dias, name="trabaja")
    cambia = mdl.binary_var_matrix(empleados, dias[1:], name="cambia")

    # Nueva variable auxiliar para linealizar eficiencia bonificada
    z = {
        (e, t, d): mdl.binary_var(name=f"z_{e}_{t}_{d}")
        for e in empleados for t in tareas for d in dias[1:]
    }

    # --- RESTRICCIONES ---

    # 1 tarea por empleado por día
    for e in empleados:
        for d in dias:
            mdl.add_constraint(mdl.sum(x[e, t, d] for t in tareas) <= 1, f"una_tarea_{e}_{d}")

    # trabajar si tiene alguna tarea
    for e in empleados:
        for d in dias:
            mdl.add_constraint(mdl.sum(x[e, t, d] for t in tareas) == trabaja[e, d], f"trabaja_{e}_{d}")

    # detectar cambio de tarea
    for e in empleados:
        for i in range(1, len(dias)):
            d = dias[i]
            d_ant = dias[i - 1]
            for t1 in tareas:
                for t2 in tareas:
                    if t1 != t2:
                        mdl.add_constraint(
                            cambia[e, d] >= x[e, t1, d_ant] + x[e, t2, d] - 1,
                            f"cambio_{e}_{d}_{t1}_{t2}"
                        )

    # Linealización de bonificación: z[e,t,d] = x[e,t,d] AND cambia[e,d]
    for e in empleados:
        for d in dias[1:]:
            for t in tareas:
                mdl.add_constraint(z[e, t, d] <= x[e, t, d], f"z1_{e}_{t}_{d}")
                mdl.add_constraint(z[e, t, d] <= cambia[e, d], f"z2_{e}_{t}_{d}")
                mdl.add_constraint(z[e, t, d] >= x[e, t, d] + cambia[e, d] - 1, f"z3_{e}_{t}_{d}")

    # cubrir demanda diaria por tarea
    for d in dias:
        for t in tareas:
            if (t, d) not in demanda:
                continue
            demanda_t_d = demanda[(t, d)]

            if d == dias[0]:  # viernes
                eficiencia_total = mdl.sum(
                    x[e, t, d] * eficiencia[t] * jornada_horas
                    for e in empleados
                )
            else:
                eficiencia_total = mdl.sum(
                    eficiencia[t] * jornada_horas * (x[e, t, d] + bonificacion * z[e, t, d])
                    for e in empleados
                )

            mdl.add_constraint(eficiencia_total >= demanda_t_d, f"demanda_{t}_{d}")

    # --- OBJETIVO ---
    total_costo = mdl.sum(trabaja[e, d] * costo_diario for e in empleados for d in dias)
    mdl.minimize(total_costo)
    mdl.print_information()

    return mdl, x, trabaja, cambia

def print_model(mdl):
    print("--------------------")
    print(f"Model: {mdl.name}")
    print("Constraints:")
    for constraint in mdl.iter_constraints():
        if hasattr(constraint, "rhs"):
            le_to_inf = constraint.rhs.equals(float('inf')) and constraint.sense == ComparisonType.LE
            ge_to_zero = constraint.sense == ComparisonType.GE and constraint.rhs.equals(0)
            if le_to_inf or ge_to_zero:
                continue
            print(f"   {constraint}")
    print(f"Objective: {mdl.objective_expr}")
    print(f" {mdl.objective_sense.name}")
    print("--------------------")

def solve_model(mdl, x, trabaja, cambia):
    solution = mdl.solve()

    if not solution:
        print("❌ No se pudo resolver el modelo.")
        return

    print(f"\n✅ Costo total mínimo: ${mdl.objective_value}\n")
    for (e, t, d), var in x.items():
        if var.solution_value > 0.5:
            print(f"🧑 Empleado {e} hace tarea '{t}' el {d}")
