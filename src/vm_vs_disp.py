
# Obtener la componente 'y' a registrar.
def get_y(constraint_nameY):    
    return constraint_nameY.dual_value

def get_text_for_plot(constraint_nameX, xunit, yunit):
    xlabel='{0} {1}'.format(constraint_nameX, xunit)
    ylabel='Valor Marginal \n {0} \n{1}'.format(constraint_nameX, yunit)
    title='Valor Marginal {}'.format(constraint_nameX)
    
    return {"xlabel": xlabel, "ylabel": ylabel, "title": title}


# Comentarios de debug, entre iterate y plot
# print("rhs_values:",rhs_values)
# print("current_rhs_value:",current_rhs_value) # es el actual, el bi
# print("dual_values:", dual_values)
# print("")
# print("constraint_nameX:", constraint_nameX)
# print("constraint_nameY:", constraint_nameY)
# print("")
# print("mdl:", mdl)
# print("mdl:", mdl.solution)
# # if 0 not in rhs_values, significa que antes de su mín es incompatible