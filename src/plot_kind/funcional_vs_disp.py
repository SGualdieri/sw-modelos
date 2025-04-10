
### Aviso ###

# Este archivo del funcional es el que utiliza funciones sin refactorizar.
# La función iterate está en su versión anterior, por lo que
# se conservan su perform y solve anteriores para que puedan
# ser usadas por la iterate.

from docplex.mp.relax_linear import LinearRelaxer

from data_related_utils import get_constraint_by_name
from .plot_kind import PlotKind
from plot_kind_plotter import plot

class Funcional(PlotKind):

    def __init__(self, mdl, products, production_vars):
        super().__init__(mdl, products, production_vars)
        
        # Estos tres atributos en el futuro podrían no existir, xq podría haber un método que haga iterate and plot
        self.current_rhs_value = None
        self.rhs_values = None
        self.dual_values = None


    def get_y(self, solution):
        """AUX: WILL use this after refactoring"""
        solution.objective_value        

    def get_text_for_plot(self, constraint_name, xunit, yunit):   
        xlabel='{0}\n{1}'.format(constraint_name, xunit)
        ylabel='Funcional\n{}'.format(yunit)
        title='Funcional vs. {}'.format(constraint_name)

        return {"xlabel": xlabel, "ylabel": ylabel, "title": title}

    
    def iterate(self, constraint_name):
        self.current_rhs_value, self.rhs_values, self.objective_values = iterate_over_rhs(constraint_name, self.mdl, self.products, self.production_vars)

        return self.current_rhs_value, self.rhs_values, self.objective_values # currently returned for debugging purposes
        

    def plot(self, constraint_name, x_unit, y_unit):
        new_rhs, new_obj = sort_after_iterate(rhs_values, objective_values)

        # Graficamos
        plot_text = self.get_text_for_plot(constraint_name, x_unit, y_unit)
        plot(new_rhs, new_obj, self.current_rhs_value, plot_text, is_function_discontinuous=False)

### ANTERIOR, se deben inicializar acá por compatibilidad con
### función iterate sin refactorizar.
# Initialize lists to store the results
rhs_values = []
objective_values = []

#real_rhs_value = 0

m = 0.01

### ANTERIOR!!! Usa report en lugar de store y get_y,
### usa iterate, perform y solve anteriores.
# Report values for the chart
### Aux: misma función que VM (cambian las listas nomás)
def report(rhs_value, obj):
    rhs_values.append(rhs_value)
    objective_values.append(obj)

# # Perform sensitivity analysis of the RHS
# ### Aux: VM, Funcional, costo op
# aux: esta es la versión anterior, pero usa esto xq la iterate no es la refactorizada.
def perform_sensitivity_analysis(mdl):
    lp = LinearRelaxer.make_relaxed_model(mdl)
    lp.solve()
    cpx = lp.get_engine().get_cplex()

    return cpx.solution.sensitivity.rhs()

# Adjust RHS and solve 
### Aux: misma función que VM, funcional, costo op
  # mdl, products, production_vars
  # A la restriccción de constraint_nameX, le pone el rhs recibido.
def solve(c, rhs_value, mdl, products, production_vars):
    print("---")    
    print("- Adjusting RHS to: {0}".format(rhs_value))
    c.rhs = rhs_value
    solution = mdl.solve()
    
    if solution is not None:       
        print("* Production model solved with objective: {:g}".format(solution.objective_value))
        print("* Total benefit=%g" % solution.objective_value)
        for p in products:
            print("Production of {product}: {prod_var}".format(product=p[0], prod_var=production_vars[p[0]].solution_value))
        return solution
    else:
        print("No solution found for RHS value: {0}".format(rhs_value))
        return None  # Return None to indicate that the model is infeasible at this point


# Iterate over RHS (from 0 to infinity) starting from current RHS value
def iterate_over_rhs(constraint_name, mdl, products, production_vars):
    c = get_constraint_by_name(constraint_name, mdl)
    if c is None:
        print("Constraint with name '{0}' not found.".format(constraint_name))
        return
        
    # Perform initial sensitivity analysis to get the starting lower and upper bounds
    initial_sensitivity = perform_sensitivity_analysis(mdl)
    
    # Find the sensitivity range for the specified constraint
    for c_sens, (lower, upper) in zip(mdl.iter_constraints(), initial_sensitivity):
        if c_sens.name == constraint_name:
            
            # Report the real RHS value for the chart
            real_rhs_value = c_sens.rhs.constant
            report(real_rhs_value, mdl.objective_value)
        
            # *********Store and report the initial lower and upper bounds for the chart*********
            print("---Initial lower bound: {0}".format(lower))
            rhs = lower
            solution = solve(c, rhs, mdl, products, production_vars)
            if solution is not None:
                report(rhs, mdl.objective_value)

            print("---Initial upper bound: {0}".format(upper))
            rhs = upper
            solution = solve(c, rhs, mdl, products, production_vars)
            if solution is not None and rhs < mdl.infinity:
                report(rhs, mdl.objective_value)
            # ********* End of lower and upper bounds *********
            
            
            #Decrease rhs starting from lower bound - m
            rhs = lower - m
            while True:
                if rhs < 0:
                    break ## Stop if the rhs is lower than 0                
                
                solution = solve(c, rhs, mdl, products, production_vars)#+m) # aux: no son escalones, un "m" afecta al Z # TEMP # Da Timeout
                                        # claro, siempre obtengo el mismo rango xq me quedé en el inicial si
                                        # le vuevo a sumar el m que le resté, #ja.
                if solution is None:
                    break  # Stop if the model is infeasible
                
                #report(c_sens.rhs.constant+m, mdl.objective_value) ### AUX PROBANDO
                # Perform sensitivity analysis to get the new lower bound
                new_sensitivity = perform_sensitivity_analysis(mdl)                
                for c_new_sens, (new_lower, _) in zip(mdl.iter_constraints(), new_sensitivity):
                    if c_new_sens.name == constraint_name: 
                        rhs = new_lower
                        if rhs < 0:
                            break ## Stop if the rhs is lower than 0                
                            
                        solution = solve(c, rhs, mdl, products, production_vars)
                        if solution is None:
                            break  # Stop if the model is infeasible
                        report(c_new_sens.rhs.constant, mdl.objective_value)
                        
                        rhs = new_lower - m

                        break


            # Increase rhs starting from upper bound + m
            rhs = upper + m
            
            while True:
                if rhs >= mdl.infinity:
                    break ## Stop if the rhs reaches or exceeds infinity

                solution = solve(c, rhs, mdl, products, production_vars)#-m) # aux: no son escalones, un "m" afecta al Z # TEMP
                if solution is None:
                    break  # Stop if the model is infeasible

                #report(c_sens.rhs.constant-m, mdl.objective_value) ### AUX PROBANDO
                # Perform sensitivity analysis to get the new upper bound
                new_sensitivity = perform_sensitivity_analysis(mdl)
                for c_new_sens, (_, new_upper) in zip(mdl.iter_constraints(), new_sensitivity):
                    if c_new_sens.name == constraint_name:                        
                        rhs = new_upper
                        if rhs >= mdl.infinity:
                            break ## Stop if the rhs reaches or exceeds infinity

                        solution = solve(c, rhs, mdl, products, production_vars)
                        if solution is None:
                            break  # Stop if the model is infeasible
                        report(c_new_sens.rhs.constant, mdl.objective_value)
                        
                        rhs = new_upper + m

                        break
                    
    return real_rhs_value, rhs_values, objective_values

# Llamar a esta función es necesario, dsp de llamar a iterate
# y antes de llamar a plot, porque estamos usando la versión anterior
# de iterate (si se unificaran, esta función se podría eliminar).
def sort_after_iterate(rhs_values, objective_values):
    ### Mejora1
    # Armo pares y los ordeno según 'x'
    pairs = []
    for i in range(len(rhs_values)):
        pairs.append((rhs_values[i], objective_values[i]))

    print("[debug] pairs", pairs)

    #pairs.sort()
    # Ordeno ascendentemente por la primera componente y Asc por la segunda si hay empates
    pairs.sort(key=lambda x: (x[0], x[1]))

    print("[debug] pairs", pairs)

    # Los vuelvo a separar en listas, para no cambiar la función plot
    new_rhs, new_obj = [], []
    for elem in pairs:
        new_rhs.append(elem[0])
        new_obj.append(elem[1])
    print("[debug] new_rhs", new_rhs)
    print("[debug] new_dual", new_obj)
    return new_rhs, new_obj

#####################################
### FIN tema funciones anteriores ###
#####################################

