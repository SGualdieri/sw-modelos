from data_related_utils import BIG_M

def create_data_dict():
    name = "produccion_muebles_hogar"

     # Variables de decisión para escritorios
    products = [("EB", 700, BIG_M, 30),   # Escritorio Básico
                ("EL", 1200, 30, 0)]       # Escritorio Lujo

    # Recursos disponibles (nombre, capacidad)
    resources = [
        ("Madera", 15000),        # kg
        ("Metal", 9000),         # kg
        ("Barniz", BIG_M),
        ("Hs Mano CPM", 640),  #640hs/mes = 8hs/dia * 20 dias * 4 empleados
        ("Hs Mano CEA", 640),
        ("Hs Maq CEA", 640),  #640hs/mes = 16hs/dia * 20 dias * 2 maquinas 
        ("Hs Maq CFCM", 640),
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
