# data.py

def create_data_dict():
    name = "asignacion_empleados_supermercado"

    empleados = list(range(18))

    tareas = ["Reponer", "Ordenar", "Marcar"]

    dias = ["Viernes", "Sabado", "Domingo"]

    eficiencia = {
        "Reponer": 15,
        "Ordenar": 30,
        "Marcar": 35
    }

    demanda = {
        ("Reponer", "Viernes"): 500, #uso la misma cantidad que el sabado
        ("Reponer", "Sabado"): 350,
        ("Reponer", "Domingo"): 450,
        ("Ordenar", "Viernes"): 300,
        ("Ordenar", "Domingo"): 300, #uso lo mismo que el viernes
        ("Marcar", "Viernes"): 150,
        ("Marcar", "Sabado"): 139,
        ("Marcar", "Domingo"): 143,
    }

    jornada_horas = 8
    costo_diario = 12
    bonificacion_por_cambio = 0.10

    return {
        "name": name,
        "empleados": empleados,
        "tareas": tareas,
        "dias": dias,
        "eficiencia": eficiencia,
        "demanda": demanda,
        "jornada_horas": jornada_horas,
        "costo_diario": costo_diario,
        "bonificacion": bonificacion_por_cambio
    }

def unpack_data(data_dict):
    try:
        return (
            data_dict["name"],
            data_dict["empleados"],
            data_dict["tareas"],
            data_dict["dias"],
            data_dict["eficiencia"],
            data_dict["demanda"],
            data_dict["jornada_horas"],
            data_dict["costo_diario"],
            data_dict["bonificacion"]
        )
    except Exception as e:
        raise ValueError(f"ERROR: faltan datos de entrada: {e}")
