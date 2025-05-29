from data_related_utils import get_prod_var_for
from .plot_kind import PlotKind
from iterators.price_iterator import PriceIterator
from plot_kind_plotter import plot

class CurvaDeOferta(PlotKind):

    def __init__(self, mdl, products, production_vars):
        super().__init__(mdl, products, production_vars)
        
        # Estos tres atributos en el futuro podrían no existir, xq podría haber un método que haga iterate and plot
        self.current_price_value = None
        self.prices = None
        self.dual_values = None


    # Get quantity of the product in the solution
    def get_y(self, prod_var):
        return prod_var.solution_value

    def get_text_for_plot(self, product_name, xunit, yunit):
        xlabel='Precio {0}\n{1}'.format(product_name, xunit)
        ylabel='Cantidad\nProducida {0}\n{1}'.format(product_name, yunit)
        title='Curva de Oferta del Producto {}'.format(product_name)

        return {"xlabel": xlabel, "ylabel": ylabel, "title": title}
    
    # AUX: will extract pms later, and make these abstract methods as well
    
    def iterate(self, product_name):
        self.current_price_value, self.prices, self.quantities = self.iterate_over_price_for_var(product_name, self.mdl, self.products, self.production_vars)
        
        return self.current_price_value, self.prices, self.quantities
    
    def plot(self, product_name, x_unit, y_unit):
        plot_text = self.get_text_for_plot(product_name, x_unit, y_unit)
        plot(self.prices, self.quantities, self.current_price_value, plot_text)
    
    #################################

    def iterate_over_price_for_var(self, product_name, mdl, products, production_vars):
        prod_var = get_prod_var_for(product_name, production_vars)
        # Iteramos
        iterator = PriceIterator(product_name, products, production_vars)
        current_price_value, prices, quantities = iterator.iterate_over_price(mdl, self.get_y)
        
        return current_price_value, prices, quantities


### Comentarios de debug, entre iterate y plot
# print("prices:", prices)
# print("quantities:", quantities) 
# print("current:", current_price_value) 

# Round all values in the prices list to 2 decimal places    
#prices = [round(price, 2) for price in prices] #