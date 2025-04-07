from docplex.mp.relax_linear import LinearRelaxer
from common_iterator import iterate_internal

def get_prod_var_for(product_name, produccion_vars):
    prod_var = next((value for key, value in produccion_vars.items() if key[0] == product_name), None)
    
    if prod_var is None:
        raise ValueError(f"ERROR: no se encontró {product_name} en produccion_vars.")
    return prod_var

# Aux: específica de Curva de oferta
# Perform sensitivity analysis of the objective
# Devuelve el lower y upper del rango actual para el coeficiente del funcional
# de la variable prod_var.
def perform_sensitivity_analysis(mdl, prod_name, produccion_vars):
    lp = LinearRelaxer.make_relaxed_model(mdl)
    lp.solve()
    cpx = lp.get_engine().get_cplex()
    
    prod_var=get_prod_var_for(prod_name, produccion_vars)

    idx=prod_var.index
    ranges = cpx.solution.sensitivity.objective()
    #print("[debug] lower, upper:", ranges[idx])

    return ranges[idx]

# Aux: específica de Curva de oferta
# Solves the model for a given price por a product
# price: price to consider
# prod_name: product name ("A", "B", "C")
# Al prod_name le pone el price, y resuelve.
def solve_model_for_price(prod_name, price, mdl, products, produccion_vars):

    # Función objetivo
    # Toma los coeficientes de los datos excepto por el de la variable prod_name para la cual considera el coeficiente 'price'
    total_benefit = mdl.sum(produccion_vars[p] * (p[1] if p[0] != prod_name else price) for p in products)
    mdl.maximize(total_benefit)

    solution = mdl.solve()
    if solution is not None:
        print("* Production model solved with objective: {:g}".format(solution.objective_value))
        print("* Total benefit=%g" % solution.objective_value)
        for p in products:
            print("Production of {product}: {prod_var}".format(product=p[0], prod_var=produccion_vars[p].solution_value))

        return solution
    else:
        print("No solution found for price value: {0}".format(price))
        return None  # Return None to indicate that the model is infeasible at this point
    
# aux: ver cantidad de parámetros.
# pre: se resolvió el modelo y existe solución.
#def iterate_over_price(constraint_nameX, constraint_nameY, mdl, products, produccion_vars, get_y_function): # aux: var mdl, 'm', y funciones.
def iterate_over_price(prod_name, prod_var, mdl, products, produccion_vars, get_y_function): # aux: var mdl, 'm', y funciones.
    PRICE_POSITION_IN_PRODUCTS = 1 # price position in products vector (0=name, 1=benefit, 2=max demand, 3=min demand)

    # Obtengo punto actual
    # Obs: Esto, a diferencia la iteración para otros gráficos (rhs) No requiere llamar a perform_sensitivity_analysis.
    # Buscamos el product_name en el array "products" para consultar en su primera posición su precio
    # (aux: products tiene tuplas, esto obtiene la tupla que tiene 'product_name' como primer valor)
    idx = next((i for i, prod in enumerate(products) if prod[0] == prod_name), None)
    current_price_value = products[idx][PRICE_POSITION_IN_PRODUCTS]
    current_quantity_value = get_y_function(prod_var)

    return iterate_internal(prod_name, prod_var, current_price_value, current_quantity_value, mdl, products, produccion_vars, get_y_function, perform_sensitivity_analysis, solve_model_for_price) # aux: var mdl, 'm', y funciones.