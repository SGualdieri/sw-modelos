import sys
from docplex.mp.model import Model
from docplex.mp.constants import ComparisonType

from data_related_utils import BIG_M
from .data import unpack_data

def create_model(data_dict):
    name, products, resources, consumptions = unpack_data(data_dict)
    mdl = Model(name)

    # Variables de producción
    prod_names = [prod[0] for prod in products]
    production_vars = mdl.integer_var_dict(prod_names, name=prod_names)

    EB = production_vars["EB"]
    EL = production_vars["EL"]

    # Variables auxiliares de costos
    CANT_MAD = mdl.integer_var(name="CANT_MAD")
    CANT_MET = mdl.integer_var(name="CANT_MET")
    CANT_PINT = mdl.continuous_var(name="CANT_PINT")

    CANT_MDO_CPM = mdl.continuous_var(name="CANT_MDO_CPM")
    CANT_MDO_CEA = mdl.continuous_var(name="CANT_MDO_CEA")
    CANT_MAQ_CEA = mdl.continuous_var(name="CANT_MAQ_CEA")
    CANT_MAQ_CFCM = mdl.continuous_var(name="CANT_MAQ_CFCM")

    EXCESO = mdl.integer_var(name="EXCESO")
    DEFECTO = mdl.integer_var(name="DEFECTO", ub=15000)

    INT_GANADO = mdl.integer_var(name="INT_GANADO")
    INT_PAGADO = mdl.integer_var(name="INT_PAGADO")

    # Restricciones técnicas
    mdl.add_constraint(CANT_MAD == 10*EB + 30*EL)
    mdl.add_constraint(CANT_MET == 8*EB + 24*EL)
    mdl.add_constraint(CANT_PINT == 0.5*EB + 0.8*EL)

    mdl.add_constraint(CANT_MDO_CPM == 1.2*EB + 2.4*EL)
    mdl.add_constraint(CANT_MDO_CEA == 1.5*EB + 2.5*EL)
    mdl.add_constraint(CANT_MAQ_CEA == 1.0*EB + 1.8*EL)
    mdl.add_constraint(CANT_MAQ_CFCM == 0.8*EB + 2.4*EL)

    # Restricciones de recursos
    mdl.add_constraint(CANT_MAD <= 5000)
    mdl.add_constraint(CANT_MET <= 3000)
    mdl.add_constraint(CANT_MDO_CEA <= 800)
    mdl.add_constraint(CANT_MAQ_CEA <= 600)

    # Caja disponible
    costo_insumos = 5*CANT_MAD + 8*CANT_MET + 10*CANT_PINT
    costo_horas = 20*CANT_MDO_CPM + 25*CANT_MDO_CEA + 12*CANT_MAQ_CEA + 15*CANT_MAQ_CFCM
    costos_mes = costo_horas

    mdl.add_constraint(30000 - costos_mes - 8000 == EXCESO - DEFECTO)  #Agregar variable caja inicial

    mdl.add_constraint(INT_GANADO == 0.08 * EXCESO)
    mdl.add_constraint(INT_PAGADO == 0.1 * DEFECTO)

    # Demanda
    mdl.add_constraint(EB >= 300)
    mdl.add_constraint(EL <= 150)

    # Función objetivo
    ventas = 500*EB + 900*EL
    beneficio = ventas - costo_insumos - costo_horas + INT_GANADO - INT_PAGADO

    mdl.maximize(beneficio)

    mdl.print_information()

    return mdl, production_vars, products

def print_model(mdl):
    print("--------------------")
    print(f"Model: {mdl.name}")
    print("Constraints:")
    for constraint in mdl.iter_constraints():
        if hasattr(constraint, "rhs"):
            le_to_inf = constraint.rhs.equals(BIG_M) and constraint.sense == ComparisonType.LE
            ge_to_zero = constraint.sense == ComparisonType.GE and constraint.rhs.equals(0)
            if not (le_to_inf or ge_to_zero):
                print(f"   {constraint}")
    print(f"Objective: {mdl.objective_expr}")
    print(f" {mdl.objective_sense.name}")
    print("--------------------")

def solve_model(mdl, production_vars, products):
    solution = mdl.solve()

    if not solution:
        print("Model cannot be solved.")
        sys.exit(1)

    obj = mdl.objective_value

    print("* Production model solved with objective: {:g}".format(obj))
    for p in products:
        print("Production of {product}: {prod_var}".format(product=p[0], prod_var=production_vars[p[0]].solution_value))
