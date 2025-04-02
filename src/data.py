
LITTLE_M = 0.01

def create_data_dict():
    # human friendly problem name
    name = "guia5problematipo2"

    # name, benefit, max demand, min demand
    products = [("A", 50, 100, 0),### original, así estaba
    ###products = [("A", 10, 100, 0), # aux probando
    #products = [("A", 70, 100, 0), # aux probando
                ("B", 40, 120, 80),
                ("C", 30, 999999999999999, 0)]

    # resources are a list of simple tuples (name, capacity)
    resources = [("Equipo1", 160),
                ("Equipo2", 180),
                ("Equipo3", 110)] ### Aux: orig, así estaba
                #("Equipo3", 300)] ### Probando
    
    consumptions = {
        "Equipo1": (0.8, 0.8, 0.3),  # ex 0.8*A + 0.8*B + 0.3*C
        "Equipo2": (0.6, 1.2, 0),    # Consumptions for Equipo2
        "Equipo3": (0.6, 1, 0.6)     # Consumptions for Equipo3
    }

    return {"name": name, "products": products, "resources": resources, "consumptions": consumptions}

def unpack_data(data_dict):
    
    try:
        name = data_dict["name"]
        products = data_dict["products"]
        resources = data_dict["resources"]
        consumptions = data_dict["consumptions"]
    except Exception as e:
        raise ValueError(f"ERROR: faltan datos de entrada: {e}")
                            
    return name, products, resources, consumptions