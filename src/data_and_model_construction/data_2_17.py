from data_related_utils import BIG_M

def create_data_dict():
    name = "supermercado_3dias"

    dias = ["viernes", "sabado", "domingo"]
    tareas = ["reponer", "ordenar", "marcar"]

    eficiencia = {
        "reponer": 15,
        "ordenar": 30,
        "marcar": 35
    }

    products = [
        ("Reponer_viernes", 12, BIG_M, 400),
        ("Ordenar_viernes", 12, BIG_M, 300),
        ("Marcar_viernes", 12, BIG_M, 150),
        ("Reponer_sabado", 12, BIG_M, 500),
        ("Marcar_sabado", 12, BIG_M, 139),
        ("Reponer_domingo", 12, BIG_M, 350),
        ("Ordenar_domingo", 12, BIG_M, 300),
        ("Marcar_domingo", 12, BIG_M, 143)
    ]

    resources = [
        ("Trabajadores_viernes", 18),
        ("Trabajadores_sabado", 18),
        ("Trabajadores_domingo", 18)
    ]

    consumptions = {
        "Trabajadores_viernes": {
            "Reponer_viernes": 1 / (15 * 8),
            "Ordenar_viernes": 1 / (30 * 8),
            "Marcar_viernes": 1 / (35 * 8),
        },
        "Trabajadores_sabado": {
            "Reponer_sabado": 1 / (15 * 8),
            "Marcar_sabado": 1 / (35 * 8),
        },
        "Trabajadores_domingo": {
            "Reponer_domingo": 1 / (15 * 8),
            "Ordenar_domingo": 1 / (30 * 8),
            "Marcar_domingo": 1 / (35 * 8),
        }
    }

    return {
        "name": name,
        "dias": dias,
        "tareas": tareas,
        "eficiencia": eficiencia,
        "products": products,
        "resources": resources,
        "consumptions": consumptions
    }

def unpack_data(data_dict):
    try:
        return (data_dict["name"],
                data_dict["dias"],
                data_dict["tareas"],
                data_dict["eficiencia"],
                data_dict["products"],
                data_dict["resources"],
                data_dict["consumptions"])
    except Exception as e:
        raise ValueError(f"Faltan datos de entrada: {e}")
