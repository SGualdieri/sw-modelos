# Import libs
import sys
from docplex.mp.model import Model
from docplex.mp.relax_linear import LinearRelaxer
import matplotlib.pyplot as plt

#def load_data():
from data import load_data, LITTLE_M

# Create the model with constraints and objective
def create_model():
    name, products, resources, consumptions = load_data()
    mdl = Model(name)

    produccion_vars = mdl.continuous_var_dict(products, name='produccion')

    # --- constraints ---

    # --- resources disp equipo ---
    mdl.add_constraints((mdl.sum(produccion_vars[p] * consumptions[p[0], res[0]] for p in products) <= res[1], 'Disp_%s' % res[0]) for res in resources)

    # max demand
    mdl.add_constraints((produccion_vars[p] <= p[2], 'DemandMax_%s' % p[0]) for p in products)

    # min demand
    mdl.add_constraints((produccion_vars[p] >= p[3], 'DemandMin_%s' % p[0]) for p in products)

    # --- print information ---
    mdl.print_information()

    total_benefit = mdl.sum(produccion_vars[p] * p[1] for p in products)

    # --- set the objective ---
    mdl.maximize(total_benefit)

    return mdl, produccion_vars, products

# Solve the model
def solve_model(mdl, produccion_vars, products):
    solution = mdl.solve()

    if not solution:
        print("Model cannot be solved.")
        sys.exit(1)

    obj = mdl.objective_value

    print("* Production model solved with objective: {:g}".format(obj))
    print("* Total benefit=%g" % mdl.objective_value)
    for p in products:
        print("Production of {product}: {prod_var}".format(product=p[0], prod_var=produccion_vars[p].solution_value))

######### FUNCIONES COMUNES #########

### ANTERIOR!!!
# Perform sensitivity analysis of the RHS
### Aux: VM, Funcional, costo op
def perform_sensitivity_analysis(mdl):
    lp = LinearRelaxer.make_relaxed_model(mdl)
    lp.solve()
    cpx = lp.get_engine().get_cplex()

    return cpx.solution.sensitivity.rhs()

### NUEVO, PROBANDO, POR AHORA SOLO EN VM
# Perform sensitivity analysis of the RHS
### Aux: VM, Funcional, costo op
# Constraint es el nombre de la restricción cuyos lower y upper bounds queremos obtener,
def perform_sensitivity_analysis(mdl, constraint):
    lp = LinearRelaxer.make_relaxed_model(mdl)
    lp.solve()
    cpx = lp.get_engine().get_cplex()

    rhs=cpx.solution.sensitivity.rhs()
    names = cpx.linear_constraints.get_names()
    print("[DEBUG] NOMBRES DE LAS RESTRICCIONES:\n", names)
    idx=names.index(constraint)
    print(f"Lower y upper para restr: {constraint}: {rhs[idx]}")
    
    return rhs[idx]

# Adjust RHS and solve 
### Aux: misma función que VM, funcional, costo op
  # mdl, products, produccion_vars
def solve(c, rhs_value, mdl, products, produccion_vars):
    print("---")
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


# AUX: VM, Costo op, Curva de oferta, Funcional
# Grafica.
# Recibe
#  - x_values, y_values, a graficar;
#  - current_x_value al que le dibuja una línea punteada;
#  - text es un diccionario que se obtiene con get_text_for_plot(..)
#  - is_function_discontinuous (por defecto vale True) indica si la función es o no escalonada.
def plot(x_values, y_values, current_x_value, text, is_function_discontinuous=True):

    # Set default font size for all text elements
    plt.rcParams.update({'font.size': 18})
    WIDTH=6
    
    if is_function_discontinuous:
        # Dibujar líneas horizontales entre x y x+1, con valor y
        for i in range(len(x_values) - 1):
            plt.hlines(y_values[i], x_values[i], x_values[i + 1], linewidth=WIDTH, color='C0')
            print("plt.hline dual_values[i], rhs_values[i], rhs_values[i + 1]:", y_values[i], x_values[i], x_values[i + 1]) # debug
            
    else:
        WIDTH=3 # más fino, para que se aprecien los límites
        plt.plot(x_values, y_values, marker='o', linewidth=WIDTH)
          
    # Set the x-axis and y-axis ticks to the values we are printing
    aux_locs, aux_labels = plt.xticks(x_values)
    #print("[debug], returned ticks:", aux_locs)
    #plt.yticks(dual_values)
    # Agregar el 0 a los yticks, por claridad
    y_values_and_scale=[0]+y_values
    plt.yticks(y_values_and_scale) 
    
    #Print current value
    print("[debug] current_x_value:", current_x_value)
    plt.axvline(x=current_x_value, color='g', linestyle='--', label='Valor actual')

    plt.xlabel(text["xlabel"], labelpad=20, color='#DC143C')
    plt.ylabel(text["ylabel"], rotation=0, labelpad=90, color='#DC143C')
    plt.title(text["title"], pad=30)
    plt.grid(True, which='both', linestyle='--', linewidth=0.2, color='gray', alpha=0.7)    
    
    # Extender el último rango un poco hacia la derecha
    x_start = x_values[-1] # Punto donde comienza la línea
              # aux: ^ max(eso, current_x_value), si estuvieran separados
    x_offset = 20
    y_value = y_values[-1]
    plt.hlines(y=y_value, xmin=x_start, xmax=x_start + x_offset, color='C0', linewidth=WIDTH)
    
    # Dibujar un vector con origen al final del último punto (extendido) y dirección hacia el infinito horizontalmente
    plt.annotate('', xy=(plt.xlim()[1], y_values[-1]), xytext=(x_start + x_offset, y_values[-1]),
             arrowprops=dict(arrowstyle="->", lw=2, color='C0', linewidth=30))
    
    # Se puede ajustar la rotación y tamaño, si los números están muy cerca y se enciman
    plt.xticks(rotation=0, ha='center') # rotation=45, fontsize 18

    # Mostrar yticks desde el 0, por claridad
    plt.ylim(bottom=-1)         

    plt.figure(figsize=(20, 10))
    plt.show()

###################
##### ITERATE #####
###################

# aux: mdl, products, produccion_vars, constraint_nameX, constraint_nameY, report_function
       # aux: cant parámetros...
def iterate_left(c, lower, mdl, products, produccion_vars, constraint_nameX, constraint_nameY, report):
    x_list = []
    y_list = []
    rhs = lower - LITTLE_M
    while True:
        print("[debug] Viendo para rhs:", rhs)
        if rhs < 0:
            break ## Stop if the rhs is lower than 0                
    
        solution = solve(c, rhs, mdl, products, produccion_vars)
        if solution is None:
            break  # Stop if the model is infeasible
        else:
            #report(rhs, constraint_nameY.dual_value) #Diferencia con grafico funcional vs disp
            #report(c_sens.rhs.constant, constraint_nameY.dual_value) ### Aux, veamos si así queda 126 y no 125.99
            print("[debug al append] rhs:", rhs)
            print("[debug al append] c_sens.rhs.constant:", c.rhs.constant)
            report(x_list, y_list, rhs + LITTLE_M, constraint_nameY)
            
        # Perform sensitivity analysis to get the new lower bound
        new_sensitivity = perform_sensitivity_analysis(mdl, constraint_nameX)
        print("[debug] sensitivity", new_sensitivity)            
        # for c_new_sens, (new_lower, _) in zip(mdl.iter_constraints(), new_sensitivity):
        #     if c_new_sens.name == constraint_nameX: 

        (new_lower, _) = new_sensitivity
        rhs = new_lower
        if rhs < 0:
            break ## Stop if the rhs is lower than 0                
            
        solution = solve(c, rhs, mdl, products, produccion_vars)
        if solution is None:
            break  # Stop if the model is infeasible
        #report(c.rhs.constant, constraint_nameY.dual_value)
        report(x_list, y_list, rhs, constraint_nameY)
        
        rhs = new_lower - LITTLE_M #### aux: es para la sgte vuelta del while
    
    return x_list, y_list
    

# aux: mdl, products, produccion_vars, constraint_nameX, constraint_nameY, report_function
       # aux: cant parámetros...
def iterate_right(c, upper, mdl, products, produccion_vars, constraint_nameX, constraint_nameY, report):
    x_list = []
    y_list = []
    rhs = upper + LITTLE_M
    
    while True:
        print("[debug] Viendo para rhs:", rhs)
        if rhs >= mdl.infinity:
            break ## Stop if the rhs reaches or exceeds infinity

        solution = solve(c, rhs, mdl, products, produccion_vars)
        if solution is None:
            break  # Stop if the model is infeasible
        else:
            report(x_list, y_list, rhs-LITTLE_M, constraint_nameY) #Diferencia con grafico funcional vs disp

        # Perform sensitivity analysis to get the new upper bound
        new_sensitivity = perform_sensitivity_analysis(mdl, constraint_nameX)
        # for c_new_sens, (_, new_upper) in zip(mdl.iter_constraints(), new_sensitivity):
        #     if c_new_sens.name == constraint_nameX:
        (_, new_upper) = new_sensitivity
        rhs = new_upper
        if rhs >= mdl.infinity:
            break ## Stop if the rhs reaches or exceeds infinity

        solution = solve(c, rhs, mdl, products, produccion_vars)
        if solution is None:
            break  # Stop if the model is infeasible
        #report(c.rhs.constant, constraint_nameY.dual_value)
        report(x_list, y_list, rhs, constraint_nameY)
        
        rhs = new_upper + LITTLE_M
        
    return x_list, y_list

# aux: ver cantidad de parámetros.
# pre: se resolvió el modelo y existe solución.
def iterate_over_rhs(constraint_nameX, constraint_nameY, mdl, products, produccion_vars, report): # aux: var mdl, 'm', y funciones.
    # Inicializo listas para acumular los resultados
    rhs_values = []
    dual_values = []

    c = mdl.get_constraint_by_name(constraint_nameX)
    if c is None:
        print("Constraint with name '{0}' not found.".format(constraint_nameX))
        return
    # Obtengo lower y upper iniciales
    initial_lower, initial_upper = perform_sensitivity_analysis(mdl, constraint_nameX)
    print("[debug] (lower, upper):", (initial_lower, initial_upper)) 

    # Obtengo punto actual
    current_rhs_value = c.rhs.constant
    current_dual_value = constraint_nameY.dual_value
    print(f"[DEBUG] DUAL DE CURRENT_RHS: {constraint_nameY.dual_value}")


    # Guardo puntos hacia atrás
    #Decrease rhs starting from lower bound - m
    left_x_list, left_y_list = iterate_left(c, initial_lower, mdl, products, produccion_vars, constraint_nameX, constraint_nameY, report)
    rhs_values.extend(reversed(left_x_list))
    dual_values.extend(reversed(left_y_list))

    # Guardo lower inicial y upper inicial
    store(rhs_values, dual_values, initial_lower, current_dual_value) #aux: puede ser none xq sol infeaseable, pero recién en la sgte vuelta de lower-m (y no aća)
    store(rhs_values, dual_values, current_rhs_value, current_dual_value)
    rhs = initial_upper
    if rhs < mdl.infinity:
        store(rhs_values, dual_values, rhs, current_dual_value)
    
    # Guardo puntos hacia adelante
    # Increase rhs starting from upper bound + m
    right_x_list, right_y_list = iterate_right(c, initial_upper, mdl, products, produccion_vars, constraint_nameX, constraint_nameY, report)
    rhs_values.extend(right_x_list)
    dual_values.extend(right_y_list)
    
    # Devuelvo el current
    current_rhs_value=current_rhs_value
    
    return current_rhs_value, rhs_values, dual_values

#################################
### SOLO PARA CURVA DE OFERTA ###
#################################
### SOLO PARA VM
def report(x_list, y_list, rhs_value, constraint_nameY):
    x_list.append(rhs_value)
    y_list.append(constraint_nameY.dual_value) 

# Igual que report, pero el 'y' recibido ya es el literal a guardar.
def store(x_list, y_list, rhs_value, dual_value):
    x_list.append(rhs_value)
    y_list.append(dual_value) 

### SOLO PARA CURVA DE OFERTA
# Report values for the chart
def report_with_min_dem(x_list, y_list, rhs_value, min_dem_constraint):
    #internal_sortable_rhs_values.append(internal_value)
    x_list.append(rhs_value)
    y_list.append(-1 * min_dem_constraint.dual_value) #Diferencia con grafico funcional vs disp
    
def report_without_min_dem(x_list, y_list, rhs_value, prod_var):
    #internal_sortable_rhs_values.append(internal_value)
    x_list.append(rhs_value)    
    y_list.append(-1 * prod_var.reduced_cost)