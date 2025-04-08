from abc import ABC, abstractmethod

class PlotKind(ABC):

    def __init__(self, mdl, products, production_vars):
        self.mdl = mdl
        self.products = products
        self.production_vars = production_vars


    @abstractmethod
    def get_y(self, constraint_nameY):
        "Subclasses must implement this method"
        pass
    
    @abstractmethod
    def get_text_for_plot(self, constraint_nameX, xunit, yunit):
        "Subclasses must implement this method"
        pass