from data_related_utils import DEM_MIN_POSITION, get_min_dem_constraint_for, get_prod_var_for, get_product_element_from_products
from plot_kind import PlotKind
from rhs_iterator import RhsIterator
from plot_kind_plotter import plot

class CostoOportunidad(PlotKind):

    def __init__(self, mdl, products, production_vars):
        super().__init__(mdl, products, production_vars)
        
        # Estos tres atributos en el futuro podrían no existir, xq podría haber un método que haga iterate and plot
        self.current_rhs_value = None
        self.rhs_values = None
        self.dual_values = None

        self._get_y = None
        self._min_dem_constraint = None
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
    

    def iterate(self, constraint_nameX, product_name):
        self.current_rhs_value, self.rhs_values, self.dual_values = self.iterate_over_rhs_checking_prod_min_dem(constraint_nameX, product_name, self.products, self.production_vars, self.mdl)
        
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
    def iterate_over_rhs_checking_prod_min_dem(self, constraint_nameX, product_name, products, production_vars, mdl):
        # Buscamos el product_name en el array "products" para consultar en su tercera posición si el mismo tiene demanda mínima
        prod_element = get_product_element_from_products(product_name, products)

        # Obtenemos la restricción (a la que tomarle el dual_value) si el producto tiene demanda mínima
        # o la variable del producto en caso contrario (al que tomarle el reduced_cost), para llamar a iterar            
        dem_min = prod_element[DEM_MIN_POSITION] > 0
        if dem_min:
            print(f"Demanda mínima encontrada para el producto {product_name}.")            
            prod_var_or_min_dem_constraint = get_min_dem_constraint_for(product_name, mdl)
            get_y_function = self.get_y_with_min_dem
            self._min_dem_constraint = prod_var_or_min_dem_constraint # [] esto se va a mejorar con el refactor de los iterators
        else:
            print(f"Demanda mínima No encontrada para el producto {product_name}.")
            prod_var_or_min_dem_constraint = get_prod_var_for(product_name, production_vars)
            get_y_function = self.get_y_without_min_dem
            self._prod_var = prod_var_or_min_dem_constraint # []

        iterator = RhsIterator(products, production_vars, constraint_nameX, prod_var_or_min_dem_constraint)
        return iterator.iterate_over_rhs(constraint_nameX, prod_var_or_min_dem_constraint, mdl, get_y_function)


# Comentarios de debug, entreiterate y plot
# print("rhs_values", rhs_values)
# print("dual_values", dual_values)