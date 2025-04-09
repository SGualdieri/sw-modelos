from docplex.mp.relax_linear import LinearRelaxer
from common_iterator import Iterator
from data_related_utils import get_prod_var_for

class PriceIterator(Iterator):

    def __init__(self, prod_name, products, production_vars):
        super().__init__(products, production_vars)

        self.prod_name = prod_name
        self.prod_var = get_prod_var_for(prod_name, production_vars)
    

    # Aux: específica de Curva de oferta
    # Perform sensitivity analysis of the objective
    # Devuelve el lower y upper del rango actual para el coeficiente del funcional
    # de la variable prod_var.
    def perform_sensitivity_analysis(self, mdl, prod_name):
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
    # Al prod_name le pone el price, y resuelve.
    def solve(self, prod_name, price, mdl):

        # Función objetivo
        # Toma los coeficientes de los datos excepto por el de la variable prod_name para la cual considera el coeficiente 'price'
        total_benefit = mdl.sum(self.production_vars[p] * (p[1] if p[0] != self.prod_name else price) for p in self.products)
        mdl.maximize(total_benefit)

        solution = mdl.solve()
        if solution is not None:
            print("* Production model solved with objective: {:g}".format(solution.objective_value))
            print("* Total benefit=%g" % solution.objective_value)
            for p in self.products:
                print("Production of {product}: {prod_var}".format(product=p[0], prod_var=self.production_vars[p].solution_value))

            return solution
        else:
            print("No solution found for price value: {0}".format(price))
            return None  # Return None to indicate that the model is infeasible at this point
        
    # Pre: se resolvió el modelo y existe solución.
    def iterate_over_price(self, prod_name, prod_var, mdl, get_y_function):
        PRICE_POSITION_IN_PRODUCTS = 1 # price position in products vector (0=name, 1=benefit, 2=max demand, 3=min demand)

        # Obtengo punto actual
        # Obs: Esto, a diferencia la iteración para otros gráficos (rhs) No requiere llamar a perform_sensitivity_analysis.
        # Buscamos el product_name en el array "products" para consultar en su primera posición su precio
        # (aux: products tiene tuplas, esto obtiene la tupla que tiene 'product_name' como primer valor)
        idx = next((i for i, prod in enumerate(self.products) if prod[0] == self.prod_name), None)
        current_price_value = self.products[idx][PRICE_POSITION_IN_PRODUCTS]
        current_quantity_value = get_y_function(self.prod_var)

        return super().iterate_internal(self.prod_name, self.prod_var, current_price_value, current_quantity_value, mdl, get_y_function)