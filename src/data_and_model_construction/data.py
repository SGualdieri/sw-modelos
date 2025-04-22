
from data_related_utils import BIG_M

def create_data_dict():
    # human friendly problem name
    name = "produccion_pullover"

    # name, benefit, max demand, min demand
    # IMPORTANT: KEEP this format, if you'll want to use plot_kind/* later.
    products = [("A", 10, BIG_M, 0),
                ("B", 15, BIG_M, 10),
                ("B1", 0, BIG_M, 0),  
                ("B2", 0, BIG_M, 0),
                ("C", 18, BIG_M, 0)]


    # resources are ast of simple tuples (name, capacity)
    resources = [("Maquina I", 80),
                 ("Maquina II", 80),
                 ("Lana Mejorada", 20),
                 ("Lana Normal", 36)]

    
    consumptions = {
        "Maquina I": (5, 6, 0, 0),    # A y B1 consumen Maquina I
        "Maquina II": (0, 4, 4, 0),   # B2 y C consumen Maquina II
        "Lana Mejorada": (1.6, 0, 1.2, 0),  # A y C consumen Lana Mejorada
        "Lana Normal": (0, 1.8, 0, 0) # B consume Lana Normal
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