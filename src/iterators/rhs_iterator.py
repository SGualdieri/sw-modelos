
from docplex.mp.relax_linear import LinearRelaxer

from .common_iterator import Iterator
from data_related_utils import get_constraint_by_name



class RhsIterator(Iterator):

    def __init__(self, products, production_vars, constraint_nameX, prod_var_or_min_dem_constraint):
        super().__init__(products, production_vars)
        self.constraint_nameX = constraint_nameX
        self.constraint_nameY = prod_var_or_min_dem_constraint


    #... def __init__(self, mdl, products, production_vars, constraint_nameX, prod_var=None):    
        
    # Perform sensitivity analysis of the RHS
    # Constraint es el nombre de la restricción cuyos lower y upper bounds queremos obtener,
    # (production_vars se mantiene actualmente solo por compatibilidad, refactorizable en el futuro).
    # Devuelve límites lower y upper del rango actual, solamente para la constraint especificada.
    def perform_sensitivity_analysis(self, mdl):
        lp = LinearRelaxer.make_relaxed_model(mdl)
        lp.solve()
        cpx = lp.get_engine().get_cplex()

        rhs=cpx.solution.sensitivity.rhs()
        names = cpx.linear_constraints.get_names()
        #print("[DEBUG] NOMBRES DE LAS RESTRICCIONES:\n", names)
        idx=names.index(self.constraint_nameX)#.name)
        #print(f"[debug] Lower y upper para restr: {constraint}: {rhs[idx]}")
        
        return rhs[idx]

    # Adjust RHS and solve 
    # A la restriccción de constraint_nameX, le pone el rhs recibido, y resuelve.
    def solve(self, rhs_value, mdl):
        print("---")
        c = get_constraint_by_name(self.constraint_nameX, mdl)
        
        print("- Adjusting RHS to: {0}".format(rhs_value))
        # aux: para reemplazar esta línea con "c" por "self.constraint_nameY.rhs = rhs_value" hay que tener cuidado [].
        c.rhs = rhs_value
        solution = mdl.solve()

        if solution is not None:       
            print("* Production model solved with objective: {:g}".format(solution.objective_value))
            print("* Total benefit=%g" % solution.objective_value)
            for p in self.products:
                print("Production of {product}: {prod_var}".format(product=p[0], prod_var=self.production_vars[p[0]].solution_value))
            return solution
        else:
            print("No solution found for RHS value: {0}".format(rhs_value))
            return None  # Return None to indicate that the model is infeasible at this point

    # Deja el mdl como estaba antes de ser modificado por el proceso de iteración.
    def reestablish_initial_value(self, current_rhs_value, mdl):
        self.solve(current_rhs_value, mdl)

    # Pre: se resolvió el modelo y existe solución.
    # Itera sobre el rhs de la restricción constraint_nameX.
    def iterate_over_rhs(self, mdl, get_y_function):

        c = get_constraint_by_name(self.constraint_nameX, mdl)        
        
        # Hago esto acá afuera, porque la obtención del punto actual depende de 'c' y el mismo
        # debe agregarse a la lista en el momento dado (entre lower y upper iniciales).

        # Obtengo lower y upper iniciales
        _initial_lower, _initial_upper = self.perform_sensitivity_analysis(mdl)
        #print("[debug] (lower, upper):", (initial_lower, initial_upper)) 
        
        # Obtengo punto actual
        current_rhs_value = c.rhs.constant
        current_dual_value = get_y_function(self.constraint_nameY)

        iteration_results = super().iterate_internal(self.constraint_nameX, self.constraint_nameY, current_rhs_value, current_dual_value, mdl, get_y_function)

        # Restablezco el valor original, que fue modificado por solve durante la iteración
        self.reestablish_initial_value(current_rhs_value, mdl)
        
        return iteration_results