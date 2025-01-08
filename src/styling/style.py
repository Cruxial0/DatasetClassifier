from abc import abstractmethod, ABCMeta

from src.config_handler import ConfigHandler

class Style(metaclass=ABCMeta):
        
    @abstractmethod
    def get_style(self, config: ConfigHandler) -> str:
        pass