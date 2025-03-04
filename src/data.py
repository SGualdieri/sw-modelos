
LITTLE_M = 0.01

def load_data():
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
                #("Equipo3", 110)] ### Aux: orig, así estaba
                ("Equipo3", 300)] ### Probando

    consumptions = {("A", "Equipo1"): 0.8,
                    ("B", "Equipo1"): 0.8,
                    ("C", "Equipo1"): 0.3,
                    ("A", "Equipo2"): 0.6,
                    ("B", "Equipo2"): 1.2,
                    ("C", "Equipo2"): 0,
                    ("A", "Equipo3"): 0.6,
                    ("B", "Equipo3"): 1,
                    ("C", "Equipo3"): 0.6}
    return name, products, resources, consumptions