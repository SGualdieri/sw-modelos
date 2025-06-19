import sys
from docplex.mp.model import Model
from docplex.mp.constants import ComparisonType

from data_related_utils import BIG_M
from .data_tp3 import unpack_data

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

    CANT_TAB = mdl.integer_var(name="CANT_TAB")
    CANT_ESTRU = mdl.integer_var(name="CANT_ESTRU")
    CANT_PATA = mdl.integer_var(name="CANT_PATA")
    CANT_SOP = mdl.integer_var(name="CANT_SOP")

    CANT_MDO_CPM = mdl.continuous_var(name="CANT_MDO_CPM")
    CANT_MDO_CEA = mdl.continuous_var(name="CANT_MDO_CEA")
    CANT_MAQ_CEA = mdl.continuous_var(name="CANT_MAQ_CEA")
    CANT_MAQ_CFCM = mdl.continuous_var(name="CANT_MAQ_CFCM")

    EXCESO = mdl.integer_var(name="EXCESO")
    
    MAX_PRESTAMO = 15000
    DEFECTO = mdl.integer_var(name="DEFECTO", ub=MAX_PRESTAMO)

    INT_GANADO = mdl.integer_var(name="INT_GANADO")
    INT_PAGADO = mdl.integer_var(name="INT_PAGADO")

    # Restricciones técnicas
    mdl.add_constraint(CANT_MET == 2*CANT_PATA + 3*CANT_SOP)
    mdl.add_constraint(CANT_PINT == 0.5*EB + 0.8*EL)

    mdl.add_constraint(CANT_TAB == 1*EB + 2*EL)
    mdl.add_constraint(CANT_ESTRU == 1*EB + 2*EL)
    mdl.add_constraint(CANT_PATA == 4*EB + 6*EL)
    mdl.add_constraint(CANT_SOP == 2*EL)

    mdl.add_constraint(CANT_MDO_CPM == 0.5*CANT_TAB + 0.7*CANT_ESTRU)
    mdl.add_constraint(CANT_MDO_CEA == 1.5*EB + 2.5*EL)
    mdl.add_constraint(CANT_MAQ_CEA == 1.0*EB + 1.8*EL)
    mdl.add_constraint(CANT_MAQ_CFCM == 0.8*EB + 2.4*EL)
    
    mdl.add_constraint(CANT_MAD == 10*CANT_TAB + 15*CANT_ESTRU)


    # Restricciones de recursos

    mdl.add_constraint(CANT_MAD <= resources[0][1], ctname="Disp_Madera")
    mdl.add_constraint(CANT_MET <= resources[1][1], ctname="Disp_Metal")
    mdl.add_constraint(CANT_MDO_CEA <= resources[4][1], ctname="Disp_MDO_CEA")
    mdl.add_constraint(CANT_MAQ_CEA <= resources[5][1], ctname="Disp_MAQ_CEA")

    # Caja disponible
    costo_insumos = 5*CANT_MAD + 8*CANT_MET + 10*CANT_PINT
    costo_horas = 20*CANT_MDO_CPM + 25*CANT_MDO_CEA + 12*CANT_MAQ_CEA + 15*CANT_MAQ_CFCM
    costos_mes = costo_horas

    SALDO_CAJA_MINIMO = 8000
    mdl.add_constraint(resources[7][1] - costos_mes - SALDO_CAJA_MINIMO == EXCESO - DEFECTO)

    mdl.add_constraint(INT_GANADO == 0.08 * EXCESO)
    mdl.add_constraint(INT_PAGADO == 0.1 * DEFECTO)

    # Demanda
    mdl.add_constraint(EB >= products[0][3], ctname="DemandaMin_EB")

    mdl.add_constraint(EL <= products[1][2], ctname="DemandaMax_EL")
    mdl.add_constraint(EL >= products[1][3], ctname="DemandaMin_EL")


    # Función objetivo
    ventas = products[0][1]*EB + products[1][1]*EL
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
