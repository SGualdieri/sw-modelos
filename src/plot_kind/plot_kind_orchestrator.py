from plot_kind.costo_op_vs_disp import CostoOportunidad
from plot_kind.curva_of_cant_vs_precio import CurvaDeOferta
from plot_kind.funcional_vs_disp import Funcional
from plot_kind.vm_vs_disp import VM

class PlotKindOrchestrator:
    # Recibe: mdl, el modelo creado y resuelto; products y production_vars, variables creadas con los datos del modelo.
    def __init__(self, mdl, products, production_vars):
        self.mdl = mdl
        self.products = products
        self.production_vars = production_vars
    
    def vm(self, constraint_nameX, x_unit, y_unit):
        vm = VM(self.mdl, self.products, self.production_vars)
        current_rhs_value, rhs_values, dual_values = vm.iterate(constraint_nameX) # Aux returned for debugging purposes only
        vm.plot(constraint_nameX, x_unit, y_unit)
        return current_rhs_value, rhs_values, dual_values #
    
    def costo_oportunidad(self, constraint_nameX, product_name, x_unit, y_unit):
        costo_op = CostoOportunidad(self.mdl, self.products, self.production_vars)
        current_rhs_value, rhs_values, dual_values = costo_op.iterate(constraint_nameX, product_name)
        costo_op.plot(constraint_nameX, product_name, x_unit, y_unit)
        return current_rhs_value, rhs_values, dual_values 
    
    def funcional(self,constraint_nameX, x_unit, y_unit):
        funcional = Funcional(self.mdl, self.products, self.production_vars)
        real_rhs_value, rhs_values, objective_values = funcional.iterate(constraint_nameX)
        funcional.plot(constraint_nameX, x_unit, y_unit) #"[hs/mes]", "[$/mes]")
        return real_rhs_value, rhs_values, objective_values
    
    def curva_de_oferta(self, product_name, x_unit, y_unit):
        curva_of = CurvaDeOferta(self.mdl, self.products, self.production_vars)
        current_price_value, prices, quantities = curva_of.iterate(product_name)
        curva_of.plot(product_name, x_unit, y_unit)
        return current_price_value, prices, quantities 

