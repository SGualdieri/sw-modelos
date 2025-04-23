from docplex.mp.relax_linear import LinearRelaxer
from .common_iterator import Iterator
from data_related_utils import PRICE_POSITION_IN_PRODUCTS, get_prod_var_for, get_product_element_from_products

class PriceIterator(Iterator):

    def __init__(self, prod_name, products, production_vars):
        super().__init__(products, production_vars)

        self.prod_name = prod_name
        self.prod_var = get_prod_var_for(prod_name, production_vars)
    

    # Aux: específica de Curva de oferta
    # Perform sensitivity analysis of the objective
    # Devuelve el lower y upper del rango actual para el coeficiente del funcional
    # de la variable prod_var.
    def perform_sensitivity_analysis(self, mdl):
        lp = LinearRelaxer.make_relaxed_model(mdl)
        lp.solve()
        cpx = lp.get_engine().get_cplex()

        idx=self.prod_var.index
        ranges = cpx.solution.sensitivity.objective()
        #print("[debug] lower, upper:", ranges[idx])

        return ranges[idx]

    # Aux: específica de Curva de oferta
    # Solves the model for a given price por a product
    # price: price to consider
    # prod_name: product name ("A", "B", "C")
    # Al prod_name le pone el price recibido, y resuelve.
    def solve(self, price, mdl):

        # Función objetivo
        # Toma los coeficientes de los datos excepto por el de la variable prod_name para la cual considera el coeficiente 'price'
        total_benefit = mdl.sum(self.production_vars[p[0]] * (p[1] if p[0] != self.prod_name else price) for p in self.products)
        mdl.maximize(total_benefit)

        solution = mdl.solve()
        if solution is not None:
            print("* Production model solved with objective: {:g}".format(solution.objective_value))
            print("* Total benefit=%g" % solution.objective_value)
            for p in self.products:
                print("Production of {product}: {prod_var}".format(product=p[0], prod_var=self.production_vars[p[0]].solution_value))

            return solution
        else:
            print("No solution found for price value: {0}".format(price))
            return None  # Return None to indicate that the model is infeasible at this point
    
    # Deja el mdl como estaba antes de ser modificado por el proceso de iteración.
    def reestablish_initial_value(self, current_price_value, mdl):
        self.solve(current_price_value, mdl)
    
    def add_zero_point_at_the_beginning(self, mdl, prices, quantities, get_y):
        # Le agregamos el punto de x=0 al inicio, porque la función que itera solo contempla números no negativos
        price = 0     
        _ = self.solve(price, mdl)
        quantity = get_y(self.prod_var)
        x_values = [price] + prices
        y_values = [quantity] + quantities
        return x_values, y_values
    # Pre: se resolvió el modelo y existe solución.
    # Itera sobre el valor de price del producto de nombre prod_name.
    def iterate_over_price(self, mdl, get_y_function):

        # Obtengo punto actual
        # Obs: Esto, a diferencia la iteración para otros gráficos (rhs) No requiere llamar a perform_sensitivity_analysis.
        # Buscamos el product_name en el array "products" para consultar en su primera posición su precio
        # (aux: products tiene tuplas, esto obtiene la tupla que tiene 'product_name' como primer valor)
        prod_element = get_product_element_from_products(self.prod_name, self.products)
        current_price_value = prod_element[PRICE_POSITION_IN_PRODUCTS]
        current_quantity_value = get_y_function(self.prod_var)

        current_price_value, prices, quantities = super().iterate_internal(self.prod_name, self.prod_var, current_price_value, current_quantity_value, mdl, get_y_function)

        # Le agregamos el punto de x=0 al inicio, porque la función que itera solo contempla números no negativos
        updated_prices, updated_quantities = self.add_zero_point_at_the_beginning(mdl, prices, quantities, get_y_function)

        # Restablezco el valor original, que fue modificado por solve durante la iteración
        self.reestablish_initial_value(current_price_value, mdl)

        return current_price_value, updated_prices, updated_quantities
    
    
