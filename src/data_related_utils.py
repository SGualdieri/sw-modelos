
# Aux: esto podría estar en otro lado, hay varias funciones de este estilo,
#      que ya tengan mdl, products, production_Vars y encapsulen estas cosas.
# Notar que es la obtención 'cruzada', es obt constraint_nameY pero no a partir de constraint_nameX sino de prod_NAME.
def get_min_dem_constraint_for(prod_name, mdl):
    "Obtiene la restricción de demanda mínima del producto, a partir del nombre del producto."
    constraint_nameY = f"DemandMin_{prod_name}"
    min_dem_constraint = mdl.get_constraint_by_name(constraint_nameY)
    return min_dem_constraint

def get_prod_var_for(prod_name, production_vars):
    "Obtiene la variable correspondiente a un producto, a partir del nombre del producto."
    # esto da, por ejemplo prod_var_or_min_dem_constraint=list(production_vars.values())[0] ## "A"
    # Aux: es necesario que la key sea una tupla? Sería mucho más simple / legible si la key fuera directamente "A"
    prod_var = next((value for key, value in production_vars.items() if key[0] == prod_name), None)
    if prod_var is None:
        raise ValueError(f"ERROR: no se encontró {prod_name} en production_vars.")
    return prod_var