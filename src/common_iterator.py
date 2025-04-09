###################
##### ITERATE #####
###################

from abc import ABC, abstractmethod
from data import LITTLE_M

class Iterator(ABC):

    def __init__(self, products, production_vars):
        self.products = products
        self.production_vars = production_vars
    
    @abstractmethod
    def perform_sensitivity_analysis(self, mdl, constraint):
        "Debe ser implementado por cada subclase"
        pass

    @abstractmethod
    def solve(self, constraint_nameX, rhs_value, mdl):
        "Debe ser implementado por cada subclase"
        pass    

    # Función genérica, llamada desde wrappers.
    #   constraint_nameX, constraint_nameY
    #   current_* se registran en los resultados en el orden correcto
    #   mdl necesario para resolver el modelo y para encontrar variables
    #   get_y_function, perform_function, solve_function son funciones específicas de cada tipo de gráfico,
    def iterate_internal(self, constraint_nameX, constraint_nameY, current_x_value, current_y_value, mdl, get_y_function):
        # Inicializo listas para acumular los resultados
        x_values = [] # rhs values or prices
        y_values = [] # dual value or quantities
        
        # Obtengo lower y upper iniciales
        initial_lower, initial_upper = self.perform_sensitivity_analysis(mdl, constraint_nameX)
        print("[debug] (lower, upper):", (initial_lower, initial_upper)) 

        # Guardo puntos hacia atrás
        #Decrease x_coord starting from lower bound - m
        left_x_list, left_y_list = self.iterate_left(initial_lower, mdl, constraint_nameX, constraint_nameY, get_y_function)
        x_values.extend(reversed(left_x_list))
        y_values.extend(reversed(left_y_list))

        # Guardo lower inicial, actual, y upper inicial
        if initial_lower >= 0: ### AUX: agrego este check, xq da -1e20 para curva de oferta
            self.store(x_values, y_values, initial_lower, current_y_value) #aux: puede ser none xq sol infeaseable, pero recién en la sgte vuelta de lower-m (y no aća)
        self.store(x_values, y_values, current_x_value, current_y_value)
        x_coord = initial_upper
        if x_coord < mdl.infinity:
            self.store(x_values, y_values, x_coord, current_y_value)
        
        # Guardo puntos hacia adelante
        # Increase x_coord starting from upper bound + m
        right_x_list, right_y_list = self.iterate_right(initial_upper, mdl, constraint_nameX, constraint_nameY, get_y_function)
        x_values.extend(right_x_list)
        y_values.extend(right_y_list)
        
        # Devuelvo el current y las listas    
        return current_x_value, x_values, y_values

    
    def iterate_left(self, lower, mdl, constraint_nameX, constraint_nameY, get_y_function):
        x_list = []
        y_list = []

        x_coord = lower - LITTLE_M # rhs value or price

        while True:
            #print("[debug] Viendo para rhs:", x_coord)
            if x_coord < 0:
                break ## Stop if x is lower than 0         
        
            solution = self.solve(constraint_nameX, x_coord, mdl)
            if solution is None:
                break  # Stop if the model is infeasible
            else:
                #print("[debug al append] x_coord:", x_coord)            
                self.store(x_list, y_list, x_coord + LITTLE_M, get_y_function(constraint_nameY))
                
            # Perform sensitivity analysis to get the new lower bound
            new_lower, _ = self.perform_sensitivity_analysis(mdl, constraint_nameX)
            #print("[debug] sensitivity", new_sensitivity)            
            # for c_new_sens, (new_lower, _) in zip(mdl.iter_constraints(), new_sensitivity):
            #     if c_new_sens.name == constraint_nameX:

            x_coord = new_lower
            if x_coord < 0:
                break ## Stop if the x_coord is lower than 0                
                
            solution = self.solve(constraint_nameX, x_coord, mdl)
            if solution is None:
                break  # Stop if the model is infeasible
            self.store(x_list, y_list, x_coord, get_y_function(constraint_nameY))
            
            x_coord = new_lower - LITTLE_M
        
        return x_list, y_list
    

    def iterate_right(self, upper, mdl, constraint_nameX, constraint_nameY, get_y_function):
        x_list = []
        y_list = []

        x_coord = upper + LITTLE_M # rhs value or price
        
        while True:
            #print("[debug] Viendo para x_coord:", x_coord)
            if x_coord >= mdl.infinity:
                break ## Stop if the x_coord reaches or exceeds 'infinity'

            solution = self.solve(constraint_nameX, x_coord, mdl)
            if solution is None:
                break  # Stop if the model is infeasible
            else:
                self.store(x_list, y_list, x_coord-LITTLE_M, get_y_function(constraint_nameY))

            # Perform sensitivity analysis to get the new upper bound
            _, new_upper = self.perform_sensitivity_analysis(mdl, constraint_nameX)
            # for c_new_sens, (_, new_upper) in zip(mdl.iter_constraints(), new_sensitivity):
            #     if c_new_sens.name == constraint_nameX:
            
            x_coord = new_upper
            if x_coord >= mdl.infinity:
                break ## Stop if the x_coord reaches or exceeds 'infinity'

            solution = self.solve(constraint_nameX, x_coord, mdl)
            if solution is None:
                break  # Stop if the model is infeasible
            self.store(x_list, y_list, x_coord, get_y_function(constraint_nameY))
            
            x_coord = new_upper + LITTLE_M
            
        return x_list, y_list


    #################################
    #################################

    # Almacena lo recibido, el 'y' recibido ya es el literal a guardar.
    def store(self, x_list, y_list, x_value, y_value):
        x_list.append(x_value)
        y_list.append(y_value) 