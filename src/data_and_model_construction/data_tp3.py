from data_related_utils import BIG_M

def create_data_dict():
    name = "produccion_muebles_hogar"

    # Variables de decisión para escritorios
    products = [("EB", 600, BIG_M, 30),   # Escritorio Básico
                ("EL", 1100, 30, 15)]       # Escritorio Lujo

    # Recursos disponibles (nombre, capacidad)
    resources = [
        ("Madera", 15000),        # kg
        ("Metal", 9000),         # kg
        ("Barniz", BIG_M),
        ("Hs Mano CPM", 320),
        ("Hs Mano CEA", 320),
        ("Hs Maq CEA", 320),
        ("Hs Maq CFCM", 320),
        ("Caja Inicial", 50000),
    ]

    # Consumos por unidad de producto
    consumptions = {
        "Madera":       (7, 10),  # tabla, estructura
        "Metal":        (2,3), # patas , soportes
        "Barniz":       (0.5, 0.8),
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
