
from docplex.mp.relax_linear import LinearRelaxer

from common_iterator import Iterator

class RhsIterator(Iterator):

    ### Versión nueva, VM y costo op (que usan este iterate+perform)
    ### Aux: VM, costo op, Funcional
    # Aux: la llama la iterate
    # Perform sensitivity analysis of the RHS
    # Constraint es el nombre de la restricción cuyos lower y upper bounds queremos obtener,
    # (produccion_vars se mantiene actualmente solo por compatibilidad, refactorizable en el futuro).
    # Devuelve límites lower y upper del rango actual, solamente para la constraint especificada.
    def perform_sensitivity_analysis(self, mdl, constraint):
        lp = LinearRelaxer.make_relaxed_model(mdl)
        lp.solve()
        cpx = lp.get_engine().get_cplex()

        rhs=cpx.solution.sensitivity.rhs()
        names = cpx.linear_constraints.get_names()
        #print("[DEBUG] NOMBRES DE LAS RESTRICCIONES:\n", names)
        idx=names.index(constraint)#.name)
        #print(f"[debug] Lower y upper para restr: {constraint}: {rhs[idx]}")
        
        return rhs[idx]

    # Adjust RHS and solve 
    ### Aux: misma función que VM, funcional, costo op
    # mdl, products, produccion_vars
    # A la restriccción de constraint_nameX, le pone el rhs recibido.
    def solve(self, constraint_nameX, rhs_value, mdl, products, produccion_vars):
        print("---")
        # (Operación O(1))
        c = mdl.get_constraint_by_name(constraint_nameX)
        if c is None:
            print("Constraint with name '{0}' not found.".format(constraint_nameX))
            return
        
        print("- Adjusting RHS to: {0}".format(rhs_value))
        c.rhs = rhs_value
        solution = mdl.solve()
        
        if solution is not None:       
            print("* Production model solved with objective: {:g}".format(solution.objective_value))
            print("* Total benefit=%g" % solution.objective_value)
            for p in products:
                print("Production of {product}: {prod_var}".format(product=p[0], prod_var=produccion_vars[p].solution_value))
            return solution
        else:
            print("No solution found for RHS value: {0}".format(rhs_value))
            return None  # Return None to indicate that the model is infeasible at this point

    # aux: ver cantidad de parámetros.
    # pre: se resolvió el modelo y existe solución.
    def iterate_over_rhs(self, constraint_nameX, constraint_nameY, mdl, products, produccion_vars, get_y_function): # aux: var mdl, 'm', y funciones.

        c = mdl.get_constraint_by_name(constraint_nameX)
        if c is None:
            print("Constraint with name '{0}' not found.".format(constraint_nameX))
            return
        
        # Hago esto acá afuera, porque la obtención del punto actual depende de 'c' y el mismo
        # debe agregarse a la lista en el momento dado (entre lower y upper iniciales).

        # Obtengo lower y upper iniciales
        _initial_lower, _initial_upper = self.perform_sensitivity_analysis(mdl, constraint_nameX)
        #print("[debug] (lower, upper):", (initial_lower, initial_upper)) 
        
        # Obtengo punto actual
        current_rhs_value = c.rhs.constant
        current_dual_value = get_y_function(constraint_nameY)
        
        return super().iterate_internal(constraint_nameX, constraint_nameY, current_rhs_value, current_dual_value, mdl, products, produccion_vars, get_y_function) # Aux: Volver para revisar gran cant de parámetros.