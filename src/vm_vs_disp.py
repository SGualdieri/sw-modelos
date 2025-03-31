# Obtener la componente 'y' a registrar.
def get_y(constraint_nameY):    
    return constraint_nameY.dual_value

def get_text_for_plot(constraint_nameX, xunit, yunit):
    xlabel='{0} {1}'.format(constraint_nameX, xunit)
    ylabel='Valor Marginal \n {0} \n{1}'.format(constraint_nameX, yunit)
    title='Valor Marginal {}'.format(constraint_nameX)
    
    return {"xlabel": xlabel, "ylabel": ylabel, "title": title}