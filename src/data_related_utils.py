
### Aviso ###
### Este archivo contiene funciones que sirven para obtener variables del mdl necesarias para iterar y hacer gráficos.
### Esto No se modifica con solo un cambio de números en los datos de entrada.
### Solo cambia cuando cambia el formato en que están las production_vars (ej subíndice "DemandMin_") y el array de products.

LITTLE_M = 0.01


### Aux: Esto podría ser una clase que reciba mdl, products, production_vars y encapsule el acceso los arrays,
# los plot_kind e iterators podrían incluso recibir una instancia de esto en lugar de esas tres variables por separado.
# Es solo para [ver] en el futuro.

##############################################
### RELACIONADAS CON MDL Y PRODUCTION_VARS ###
##############################################

def get_constraint_by_name(constraint_nameX, mdl):
    "Obtiene la restricción a partir de su nombre."
    constraint_nameY = mdl.get_constraint_by_name(constraint_nameX)
    if constraint_nameY is None: 
        raise ValueError(f"ERROR: no se encontró la restricción: {constraint_nameX}.")
    return constraint_nameY

def get_prod_var_for(prod_name, production_vars):
    "Obtiene la variable correspondiente a un producto, a partir del nombre del producto."
    # esto da, por ejemplo prod_var_or_min_dem_constraint=list(production_vars.values())[0] ## "A"
    # Aux: es necesario que la key sea una tupla? Sería mucho más simple / legible si la key fuera directamente "A"
    prod_var = next((value for key, value in production_vars.items() if key[0] == prod_name), None)
    if prod_var is None:
        raise ValueError(f"ERROR: no se encontró {prod_name} en production_vars.")
    return prod_var

# Notar que es la obtención 'cruzada', es obt constraint_nameY pero no a partir de constraint_nameX sino de prod_NAME.
def get_min_dem_constraint_for(prod_name, mdl):
    "Obtiene la restricción de demanda mínima del producto, a partir del nombre del producto."
    constraint_nameY = f"DemandMin_{prod_name}"
    min_dem_constraint = mdl.get_constraint_by_name(constraint_nameY)
    return min_dem_constraint


#########################################
### RELACIONADAS EL ARRAY DE PRODUCTS ###
#########################################

DEM_MIN_POSITION = 3 # position in products vector (0=name, 1=benefit, 2=max demand, 3=min demand)
PRICE_POSITION_IN_PRODUCTS = 1 # price position in products vector (0=name, 1=benefit, 2=max demand, 3=min demand)

def get_product_element_from_products(prod_name, products):
    "Obtiene el elemento correspondiente al prod_name, del array products."
    # Buscamos el product_name en el array "products" para consultar en su tercera posición si el mismo tiene demanda mínima
        # (aux: products tiene tuplas, esto obtiene la tupla que tiene 'product_name' como primer valor)
    idx = next((i for i, prod in enumerate(products) if prod[0] == prod_name), None)
    if idx is None:
        raise ValueError(f"ERROR: no se encontró el product_name: {prod_name} en el array products.")
    return products[idx]