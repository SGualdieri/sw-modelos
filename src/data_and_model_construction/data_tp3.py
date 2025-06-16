from data_related_utils import BIG_M

def create_data_dict():
    name = "produccion_muebles_hogar"

    # Variables de decisión para escritorios
    products = [("EB", 500, BIG_M, 300),   # Escritorio Básico
                ("EL", 900, 150, 0)]       # Escritorio Lujo

    # Recursos disponibles (nombre, capacidad)
    resources = [
        ("Madera", 5000),        # kg
        ("Metal", 3000),         # kg
        ("Barniz", BIG_M),
        ("Hs Mano CPM", BIG_M),
        ("Hs Mano CEA", 800),
        ("Hs Maq CEA", 600),
        ("Hs Maq CFCM", BIG_M),
        ("Caja Inicial", 30000),   # cambiamos la caja inicial a 30000
    ]

    # Consumos por unidad de producto
    consumptions = {
        "Madera":       (10*1 + 15*1, 10*2 + 15*2),   # derivados de componentes madera
        "Metal":        (2*4, 2*6 + 3*2),             # patas + soportes
        "Barniz":       (0.5, 0.8),
        "Hs Mano CPM":  (0.5*1 + 0.7*1, 0.5*2 + 0.7*2),
        "Hs Mano CEA":  (1.5, 2.5),
        "Hs Maq CEA":   (1.0, 1.8),
        "Hs Maq CFCM":  (0.2*4, 0.2*6 + 0.3*2),
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
