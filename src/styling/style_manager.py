from typing import Dict, Type, Tuple
from PyQt6.QtWidgets import QMainWindow, QWidget, QPushButton, QLabel, QListWidget, QProgressBar, QComboBox, QLineEdit, QSpinBox
from PyQt6.QtCore import QObject

from src.config_handler import ConfigHandler
from src.styling.style import Style

# Styles
from src.styling.push_button.decision_buttons import AcceptButtonStyle, RejectButtonStyle
from src.styling.push_button.menu_buttons import MenuButtonStyle
from src.styling.push_button.score_buttons import DiscardButtonStyle, ScoreButtonStyle
from src.styling.push_button.push_button import PushButtonAccentStyle, PushButtonStyle, PushButtonWarningStyle
from src.styling.label.default_label import LabelStyle, SubtextLabelStyle
from src.styling.widget.widget_background import WidgetBackgroundStyle
from src.styling.window.default_window import DefaultWindowStyle
from src.styling.list.list_view import ListWidgetStyle
from src.styling.progress_bar.progress_bar import ProgressBarStyle
from src.styling.label.panel_label import ImageViewerStyle, PanelLabelStyle
from src.styling.line_edit.line_edit import LineEditStyle
from src.styling.label.keybind_label import KeybindLabelAccentStyle, KeybindLabelDisabledStyle, KeybindLabelStyle
from src.styling.widget.panel_widget import PanelWidgetStyle
from src.styling.combo_box.combo_box import ComboBoxStyle
from src.styling.spin_box.spin_box import SpinBoxStyle

class StyleManager:
    def __init__(self, config: ConfigHandler):
        """
        Initializes the StyleManager with a given configuration handler.

        Args:
            config (ConfigHandler): The configuration handler used to obtain style settings.
        
        Attributes:
            config (ConfigHandler): Stores the provided configuration handler.
            _stylesheets (Dict[Tuple[Type[QObject], str | None], Style]): A mapping of UI components and their variants to style objects.
        """

        self.config = config
        self._stylesheets: Dict[Tuple[Type[QObject], str | None], Style] = {
            # Buttons
            (QPushButton, 'accept'): AcceptButtonStyle(),
            (QPushButton, 'reject'): RejectButtonStyle(),
            (QPushButton, 'menu_tab'): MenuButtonStyle(),
            (QPushButton, 'score_button'): ScoreButtonStyle(),
            (QPushButton, 'discard_button'): DiscardButtonStyle(),
            (QPushButton, 'accent'): PushButtonAccentStyle(),
            (QPushButton, 'warning'): PushButtonWarningStyle(),
            (QPushButton, None): PushButtonStyle(),

            # Labels
            (QLabel, 'image_viewer'): ImageViewerStyle(),
            (QLabel, 'panel'): PanelLabelStyle(),
            (QLabel, 'keybind'): KeybindLabelStyle(),
            (QLabel, 'keybind_accent'): KeybindLabelAccentStyle(),
            (QLabel, 'keybind_disabled'): KeybindLabelDisabledStyle(),
            (QLabel, 'bold'): LabelStyle(bold=True),
            (QLabel, 'subtext'): SubtextLabelStyle(),
            (QLabel, None): LabelStyle(),

            # Widgets
            (QWidget, 'panel'): PanelWidgetStyle(),
            (QWidget, None): WidgetBackgroundStyle(),

            # LineEdit
            (QLineEdit, None): LineEditStyle(),

            # ComboBox
            (QComboBox, None): ComboBoxStyle(),

            # SpinBox
            (QSpinBox, None): SpinBoxStyle(),

            # List
            (QListWidget, None): ListWidgetStyle(),

            # ProgressBar
            (QProgressBar, None): ProgressBarStyle(),

            # QMainWindow
            (QMainWindow, None): DefaultWindowStyle(),
        }

    def get_stylesheet(self, component_type: Type[QObject], variant: str | None = None) -> str:
        return self._get_or_default(component_type, variant)
    
    def _get_or_default(self, component_type: Type[QObject], variant: str | None = None) -> str:
        style = self._stylesheets.get((component_type, variant))
        if style is None:
            print(f"WARNING: No style found for component type: {component_type.__name__} (variant: {variant})")
        return "" if style is None else style.get_style(self.config)