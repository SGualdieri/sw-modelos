import matplotlib.pyplot as plt

################
##### PLOT #####
################

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
    #plt.figure(figsize=(20, 10)) # si se desea usar, debe ir acá arriba, antes de que plt.otras_cosas dibujen sobre la figura
    
    if is_function_discontinuous:
        # Dibujar líneas horizontales entre x y x+1, con valor y
        for i in range(len(x_values) - 1):
            plt.hlines(y_values[i], x_values[i], x_values[i + 1], linewidth=WIDTH, color='C0')
            #print("[debug] plt.hline y_values[i], x_values[i], x_values[i + 1]:", y_values[i], x_values[i], x_values[i + 1]) # debug
            
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

    plt.show()
