from typing import Dict, Type, Tuple
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QObject

from src.config_handler import ConfigHandler
from src.styling.style import Style
from src.styling.push_button.decision_buttons import AcceptButtonStyle, RejectButtonStyle
from src.styling.push_button.menu_buttons import MenuButtonStyle
from src.styling.push_button.score_buttons import DiscardButtonStyle, ScoreButtonStyle

class StyleManager:
    def __init__(self, config: ConfigHandler):
        self.config = config
        self._stylesheets: Dict[Tuple[Type[QObject], str | None], Style] = {
            (QPushButton, 'accept'): AcceptButtonStyle(),
            (QPushButton, 'reject'): RejectButtonStyle(),
            (QPushButton, 'menu_tab'): MenuButtonStyle(),
            (QPushButton, 'score_button'): ScoreButtonStyle(),
            (QPushButton, 'discard_button'): DiscardButtonStyle(),
        }

    def get_stylesheet(self, component_type: Type[QObject], variant: str | None = None) -> str:
        return self._get_or_default(component_type, variant)
    
    def _get_or_default(self, component_type: Type[QObject], variant: str | None = None) -> str:
        style = self._stylesheets.get((component_type, variant))
        return "" if style is None else style.get_style(self.config)