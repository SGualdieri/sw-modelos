from plot_kind import PlotKind
from price_iterator import PriceIterator
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

    def iterate_over_price_for_var(self, product_name, mdl, products, produccion_vars):
        # esto da, por ejemplo prod_var_or_min_dem_constraint=list(produccion_vars.values())[0] ## "A"
        prod_var = next((value for key, value in produccion_vars.items() if key[0] == product_name), None)
        #print(f"[debug] prod_var: {prod_var}")
        if prod_var is None:
            raise ValueError(f"ERROR: no se encontró {product_name} en produccion_vars.")
        
        # Iteramos
        iterator = PriceIterator(products, produccion_vars)
        current_price_value, prices, quantities = iterator.iterate_over_price(product_name, prod_var, mdl, self.get_y)
        
        # Le agregamos el punto de x=0 al inicio, porque la función que itera solo contempla números no negativos
        # AUX: esto puede ir adentro de iterator []    
        price = 0     
        _ = iterator.solve(product_name, price, mdl)
        quantity = self.get_y(prod_var)
        x_values = [price] + prices
        y_values = [quantity] + quantities

        return current_price_value, x_values, y_values


### Comentarios de debug, entre iterate y plot
# print("prices:", prices)
# print("quantities:", quantities) 
# print("current:", current_price_value) 

# Round all values in the prices list to 2 decimal places    
#prices = [round(price, 2) for price in prices] #