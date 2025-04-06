from abc import ABC, abstractmethod

class PlotKind(ABC):
    @abstractmethod
    def get_y(self, constraint_nameY):
        "Subclasses must implement this method"
        pass
    
    @abstractmethod
    def get_text_for_plot(self, constraint_nameX, xunit, yunit):
        "Subclasses must implement this method"
        pass