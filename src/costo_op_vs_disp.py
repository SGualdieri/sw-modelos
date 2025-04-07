from plot_kind import PlotKind
from rhs_iterator import iterate_over_rhs
from plot_kind_plotter import plot

class CostoOportunidad(PlotKind):

    def __init__(self):
        super().__init__()
        # Estos tres atributos en el futuro podrían no existir, xq podría haber un método que haga iterate and plot
        self.current_rhs_value = None,
        self.rhs_values = None,
        self.dual_values = None,

        self._get_y = None,
        self._min_dem_constraint = None,
        self._prod_var = None


    # A possible implementarion [revisar después, si no conviene un setter privado]
    def get_y(self, _constraint_nameY):
        #return self._get_y
        if self._min_dem_constraint:
            return -1 * self._min_dem_constraint.dual_value
        else:
            return -1 * self._prod_var.reduced_cost
    
    def get_text_for_plot(self, constraint_nameX, product_name, xunit, yunit):
        xlabel='{0} {1}'.format(constraint_nameX, xunit)
        ylabel='C. Oport \nprod min {}\n{}'.format(yunit, product_name)
        title='Costo de oportunidad del producto {}'.format(product_name)
        return {"xlabel": xlabel, "ylabel": ylabel, "title": title}
    

    def iterate(self, constraint_nameX, product_name, products, produccion_vars, mdl):
        self.current_rhs_value, self.rhs_values, self.dual_values = self.iterate_over_rhs_checking_prod_min_dem(constraint_nameX, product_name, products, produccion_vars, mdl)
        
        return self.current_rhs_value, self.rhs_values, self.dual_values # returned for debugging purposes


    def plot(self, constraint_nameX, product_name, x_unit, y_unit):
        # Graficamos
        plot_text = self.get_text_for_plot(constraint_nameX, product_name, x_unit, y_unit)
        plot(self.rhs_values, self.dual_values, self.current_rhs_value, plot_text)

    #######################

    # Funciones para obtener la componente 'y' a registrar.
    def get_y_with_min_dem(self, min_dem_constraint):
        return -1 * min_dem_constraint.dual_value    
    def get_y_without_min_dem(self, prod_var):    
        return -1 * prod_var.reduced_cost
    
    # Al iterar, si el product_name tiene demanda mínima se desea obtener el VM (dual_value) de dicha restricción,
    # o caso contrario el Costo de oportunidad (reduced_cost) del product_name. Esta función analiza si existe o no demanda mínima
    # y le indica a iterate_over_rhs cuál de los dos valores se desea obtener al iterar.
    def iterate_over_rhs_checking_prod_min_dem(self, constraint_nameX, product_name, products, produccion_vars, mdl):
        # Buscamos el product_name en el array "products" para consultar en su tercera posición si el mismo tiene demanda mínima
        # (aux: products tiene tuplas, esto obtiene la tupla que tiene 'product_name' como primer valor)
        idx = next((i for i, prod in enumerate(products) if prod[0] == product_name), None)
        if idx is None:
            raise ValueError(f"ERROR: no se encontró el product_name: {product_name} en el array products.")

        # Obtenemos la restricción (a la que tomarle el dual_value) si el producto tiene demanda mínima
        # o la variable del producto en caso contrario (al que tomarle el reduced_cost), para llamar a iterar
        DEM_MIN_POSITION = 3 # position in products vector (0=name, 1=benefit, 2=max demand, 3=min demand)
        
        dem_min = products[idx][DEM_MIN_POSITION] > 0
        if dem_min:
            print(f"Demanda mínima encontrada para el producto {product_name}.")
            constraint_nameY = f"DemandMin_{product_name}"
            prod_var_or_min_dem_constraint = mdl.get_constraint_by_name(constraint_nameY)
            get_y_function = self.get_y_with_min_dem
            self._min_dem_constraint = prod_var_or_min_dem_constraint # [] esto se va a mejorar con el refactor de los iterators
        else:
            print(f"Demanda mínima No encontrada para el producto {product_name}.")
            # esto da, por ejemplo prod_var_or_min_dem_constraint=list(produccion_vars.values())[0] ## "A"
            # Aux: es necesario que la key sea una tupla? Sería mucho más simple / legible si la key fuera directamente "A"
            prod_var_or_min_dem_constraint = next((value for key, value in produccion_vars.items() if key[0] == product_name), None)
            if prod_var_or_min_dem_constraint is None:
                raise ValueError(f"ERROR: no se encontró {product_name} en produccion_vars.")
            get_y_function = self.get_y_without_min_dem
            self._prod_var = prod_var_or_min_dem_constraint # []
            
        return iterate_over_rhs(constraint_nameX, prod_var_or_min_dem_constraint, mdl, products, produccion_vars, get_y_function)




# Comentarios de debug, entreiterate y plot
# print("rhs_values", rhs_values)
# print("dual_values", dual_values)