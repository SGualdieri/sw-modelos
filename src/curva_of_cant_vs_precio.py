from docplex.mp.relax_linear import LinearRelaxer
from common import iterate_internal

def get_prod_var_for(product_name, produccion_vars):
    prod_var = next((value for key, value in produccion_vars.items() if key[0] == product_name), None)
    
    if prod_var is None:
        raise ValueError(f"ERROR: no se encontró {product_name} en produccion_vars.")
    return prod_var

# Get quantity of the product in the solution
def get_y(prod_var):
    return prod_var.solution_value

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


# aux: ver cantidad de parámetros.
# pre: se resolvió el modelo y existe solución.
#def iterate_over_price_en_construccion(constraint_nameX, constraint_nameY, mdl, products, produccion_vars, get_y_function): # aux: var mdl, 'm', y funciones.
def iterate_over_price_en_construccion(prod_name, prod_var, mdl, products, produccion_vars): # aux: var mdl, 'm', y funciones.
    PRICE_POSITION_IN_PRODUCTS = 1 # price position in products vector (0=name, 1=benefit, 2=max demand, 3=min demand)

    # Obtengo punto actual
    # Obs: Esto, a diferencia la iteración para otros gráficos (rhs) No requiere llamar a perform_sensitivity_analysis.
    # Buscamos el product_name en el array "products" para consultar en su primera posición su precio
    # (aux: products tiene tuplas, esto obtiene la tupla que tiene 'product_name' como primer valor)
    idx = next((i for i, prod in enumerate(products) if prod[0] == prod_name), None)
    current_price_value = products[idx][PRICE_POSITION_IN_PRODUCTS]
    current_quantity_value = get_y(prod_var)

    return iterate_internal(prod_name, prod_var, current_price_value, current_quantity_value, mdl, products, produccion_vars, get_y, perform_sensitivity_analysis, solve_model_for_price) # aux: var mdl, 'm', y funciones.

#################################

def iterate_over_price_for_var(product_name, mdl, products, produccion_vars):
    # esto da, por ejemplo prod_var_or_min_dem_constraint=list(produccion_vars.values())[0] ## "A"
    prod_var = next((value for key, value in produccion_vars.items() if key[0] == product_name), None)
    #print(f"[debug] prod_var: {prod_var}")
    if prod_var is None:
        raise ValueError(f"ERROR: no se encontró {product_name} en produccion_vars.")
    
    # Iteramos
    current_price_value, prices, quantities = iterate_over_price_en_construccion(product_name, prod_var, mdl, products, produccion_vars)
    
    # Le agregamos el punto de x=0 al inicio, porque la función que itera solo contempla números no negativos    
    price = 0     
    _ = solve_model_for_price(product_name, price, mdl, products, produccion_vars)
    quantity = get_y(prod_var)
    x_values = [price] + prices
    y_values = [quantity] + quantities

    return current_price_value, x_values, y_values

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


def get_text_for_plot(product_name, xunit, yunit):
    xlabel='Precio {0}\n{1}'.format(product_name, xunit)
    ylabel='Cantidad\nProducida {0}\n{1}'.format(product_name, yunit)
    title='Curva de Oferta del Producto {}'.format(product_name)

    return {"xlabel": xlabel, "ylabel": ylabel, "title": title}


### Comentarios de debug, entre iterate y plot
# print("prices:", prices)
# print("quantities:", quantities) 
# print("current:", current_price_value) 

# Round all values in the prices list to 2 decimal places    
#prices = [round(price, 2) for price in prices] #