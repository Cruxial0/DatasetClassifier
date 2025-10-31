"""
Tag Conditionals Page - UI for editing TagGroup activation conditions
"""

from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QPushButton, QLabel, QWidget, QMessageBox,
                            QScrollArea, QFrame)
from PyQt6.QtCore import pyqtSignal, Qt
from src.windows.settings_pages.settings_widget import SettingsWidget
from src.tagging.tag_group import TagGroup
from src.parser import parse_condition, validate_references, condition_to_string
from src.styling.styling_utils import inline_emoji

class TagConditionalsPage(SettingsWidget):
    """
    UI page for editing activation conditions for a tag group.
    
    Allows users to define when a TagGroup should become active during
    the tagging workflow based on the state of previous TagGroups.
    """
    conditionSaved = pyqtSignal(TagGroup)
    cancelClicked = pyqtSignal()
    
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.parent_widget = parent
        self.selected_group: TagGroup = kwargs.get('tag_group', None)
        
    def init_ui(self):
        """Initialize the user interface"""
        # Main scroll area to handle overflow
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        content_widget = QWidget()
        content_widget.setStyleSheet(self.style_manager.get_stylesheet(QWidget))
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        header = self._create_header("Activation Condition", font_size=16)
        header_layout.addLayout(header)
        layout.addLayout(header_layout)
        
        # Group info
        self.group_info_label = QLabel()
        self.group_info_label.setStyleSheet(self.style_manager.get_stylesheet(QLabel, 'subtext'))
        layout.addWidget(self.group_info_label)
        
        # Help section
        help_section = self._create_help_section()
        layout.addWidget(help_section)
        
        # Condition input section
        input_label = QLabel("Condition Expression:")
        input_label.setStyleSheet(self.style_manager.get_stylesheet(QLabel, 'bold'))
        layout.addWidget(input_label)
        
        self.condition_input = QTextEdit()
        self.condition_input.setPlaceholderText(self._get_placeholder_text())
        self.condition_input.setMaximumHeight(120)
        self.condition_input.setStyleSheet(self.style_manager.get_stylesheet(QTextEdit))
        self.condition_input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.condition_input)
        
        # Validation feedback
        self.validation_label = QLabel()
        self.validation_label.setWordWrap(True)
        self.validation_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(self.validation_label)
        
        # Examples section
        examples_section = self._create_examples_section()
        layout.addWidget(examples_section)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        validate_btn = self._create_button("Validate", "Check if the condition is valid")
        validate_btn.clicked.connect(self.validate_condition)
        
        clear_btn = self._create_button("Clear", "Remove the condition")
        clear_btn.clicked.connect(self.clear_condition)
        
        cancel_btn = self._create_button("Cancel", "Cancel without saving")
        cancel_btn.clicked.connect(self.cancelClicked)
        
        save_btn = QPushButton("Save")
        save_btn.setToolTip("Save the condition")
        save_btn.setStyleSheet(self.style_manager.get_stylesheet(QPushButton, 'accept'))
        save_btn.clicked.connect(self.save_condition)
        
        button_layout.addWidget(validate_btn)
        button_layout.addWidget(clear_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        # Set the scroll area content
        scroll.setWidget(content_widget)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
    
    def set_group(self, group: TagGroup):
        """
        Load the group and its existing condition
        
        Args:
            group: The TagGroup to edit
        """
        self.selected_group = group
        
        # Update group info label
        self.group_info_label.setText(
            f"Editing condition for: <b>{group.name}</b> "
            f"(Position: {group.order + 1})"
        )
        
        # Load existing condition if present
        if group.condition:
            self.condition_input.setPlainText(group.condition)
        else:
            self.condition_input.clear()
            self._set_validation_message(
                f"{inline_emoji("ℹ️")} No condition set - group is always active",
                "info"
            )
    
    def _on_text_changed(self):
        """Clear validation message when user starts typing"""
        self.validation_label.clear()
        self.validation_label.setStyleSheet("")
    
    def _set_validation_message(self, message: str, status: str):
        """
        Set validation message with appropriate styling
        
        Args:
            message: The message to display
            status: One of 'success', 'error', 'info'
        """
        self.validation_label.setText(message)
        
        if status == "success":
            success_color = self.config_handler.get_value('colors.accent_color')
            bg_color = self._adjust_color_alpha(success_color, 0.2)
            self.validation_label.setStyleSheet(
                f"QLabel {{"
                f"  color: {success_color};"
                f"  background-color: {bg_color};"
                f"  padding: 8px;"
                f"  border-radius: 4px;"
                f"  border: 1px solid {success_color};"
                f"}}"
            )
        elif status == "error":
            error_color = self.config_handler.get_value('colors.warning_color')
            bg_color = self._adjust_color_alpha(error_color, 0.2)
            self.validation_label.setStyleSheet(
                f"QLabel {{"
                f"  color: {error_color};"
                f"  background-color: {bg_color};"
                f"  padding: 8px;"
                f"  border-radius: 4px;"
                f"  border: 1px solid {error_color};"
                f"  font-weight: bold;"
                f"}}"
            )
        elif status == "info":
            text_color = self.config_handler.get_value('colors.text_color_overlay')
            panel_color = self.config_handler.get_value('colors.panel_color')
            self.validation_label.setStyleSheet(
                f"QLabel {{"
                f"  color: {text_color};"
                f"  background-color: {panel_color};"
                f"  padding: 8px;"
                f"  border-radius: 4px;"
                f"}}"
            )
    
    def _adjust_color_alpha(self, hex_color: str, alpha: float) -> str:
        """Convert hex color to rgba with given alpha"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"
    
    def validate_condition(self) -> bool:
        """
        Validate the condition syntax and references
        
        Returns:
            True if valid, False otherwise
        """

        condition_text = self.condition_input.toPlainText().strip()
        
        if not condition_text:
            self._set_validation_message(
                f"{inline_emoji("✓")} No condition set (group always active)",
                "success"
            )
            return True
        
        try:
            # Parse the condition
            parsed = parse_condition(condition_text)
            
            if parsed is None:
                self._set_validation_message(
                    f"{inline_emoji("✓")} No condition set (group always active)",
                    "success"
                )
                return True
            
            # Validate references
            # Get tag_groups from parent - handle both direct attribute and property
            all_groups = []
            parent_widget = None
            if hasattr(self, 'parent_widget'):
                parent_widget = self.parent_widget

            if parent_widget and hasattr(parent_widget, 'tag_groups'):
                all_groups = parent_widget.tag_groups
            
            if not all_groups:
                # Can't validate references without groups, but allow saving
                self._set_validation_message(
                    f"{inline_emoji("⚠️")} Cannot validate references (no groups loaded), but syntax is correct",
                    "info"
                )
                return True
            
            validate_references(parsed, self.selected_group, all_groups)
            
            # Show success with parsed representation
            parsed_str = condition_to_string(parsed)
            self._set_validation_message(
                f"{inline_emoji("✓")} Condition is valid!\nParsed as: {parsed_str}",
                "success"
            )
            return True
            
        except ValueError as e:
            self._set_validation_message(
                f"{inline_emoji("✗")} Error: {str(e)}",
                "error"
            )
            return False
        except Exception as e:
            self._set_validation_message(
                f"{inline_emoji("✗")} Unexpected error: {str(e)}",
                "error"
            )
            return False
    
    def clear_condition(self):
        """Clear the condition input and validation message"""
        reply = QMessageBox.question(
            self,
            "Clear Condition",
            "Are you sure you want to clear the condition? "
            "The group will become always active.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.condition_input.clear()
            self._set_validation_message(
                f"{inline_emoji("ℹ️")} Condition cleared - group is now always active",
                "info"
            )
    
    def save_condition(self):
        """Save the condition to the tag group"""
        # Validate first
        if not self.validate_condition():
            reply = QMessageBox.question(
                self,
                "Invalid Condition",
                "The condition has errors. Do you want to save it anyway?\n\n"
                "Warning: Invalid conditions will cause the group to be always inactive!",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # Save the condition
        condition_text = self.condition_input.toPlainText().strip()
        self.selected_group.condition = condition_text if condition_text else None
        
        # Emit signal to save the group
        self.conditionSaved.emit(self.selected_group)
        
        # Show confirmation
        QMessageBox.information(
            self,
            "Condition Saved",
            f"Activation condition for '{self.selected_group.name}' has been saved."
        )
    
    def _create_help_section(self) -> QWidget:
        """Create the help section with styled widgets"""
        help_frame = QWidget()
        help_frame.setStyleSheet(self.style_manager.get_stylesheet(QWidget, 'panel'))
        
        help_layout = QVBoxLayout(help_frame)
        help_layout.setContentsMargins(10, 10, 10, 10)
        
        help_title = QLabel("📖 Syntax Guide")
        help_title.setStyleSheet(self.style_manager.get_stylesheet(QLabel, 'bold'))
        help_layout.addWidget(help_title)
        
        help_text = QLabel(self._get_help_text())
        help_text.setWordWrap(True)
        help_text.setStyleSheet(self.style_manager.get_stylesheet(QLabel))
        help_layout.addWidget(help_text)
        
        return help_frame
    
    def _create_examples_section(self) -> QWidget:
        """Create the examples section with styled widgets"""
        examples_frame = QWidget()
        examples_frame.setStyleSheet(self.style_manager.get_stylesheet(QWidget, 'panel'))
        
        examples_layout = QVBoxLayout(examples_frame)
        examples_layout.setContentsMargins(10, 10, 10, 10)
        
        examples_title = QLabel("💡 Quick Examples")
        examples_title.setStyleSheet(self.style_manager.get_stylesheet(QLabel, 'bold'))
        examples_layout.addWidget(examples_title)
        
        examples = [
            ("Simple completion", "Composition[completed]"),
            ("Specific tag", "Composition[has:from above]"),
            ("Multiple conditions", "Composition[completed] AND Style[completed]"),
            ("Tag count", "BodyFeatures[count>=2]"),
            ("Complex logic", "(Composition[completed] OR Style[completed]) AND BodyFeatures[count>=1]"),
        ]
        
        text_color = self.config_handler.get_value('colors.text_color')
        button_color = self.config_handler.get_value('colors.button_color')
        
        for description, example in examples:
            example_layout = QHBoxLayout()
            
            desc_label = QLabel(f"<b>{description}:</b>")
            desc_label.setMinimumWidth(150)
            desc_label.setStyleSheet(self.style_manager.get_stylesheet(QLabel))
            example_layout.addWidget(desc_label)
            
            example_text = QLabel(f"<code>{example}</code>")
            example_text.setStyleSheet(
                f"QLabel {{"
                f"  background-color: {button_color};"
                f"  color: {text_color};"
                f"  padding: 4px 8px;"
                f"  border-radius: 3px;"
                f"  font-family: monospace;"
                f"}}"
            )
            example_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            example_layout.addWidget(example_text, 1)
            
            examples_layout.addLayout(example_layout)
        
        return examples_frame
    
    def _get_help_text(self) -> str:
        """Get the help text explaining the syntax"""
        return """
<b>Condition Types:</b><br>
• <code>GROUP[completed]</code> - Group has minimum required tags<br>
• <code>GROUP[has:tag1,tag2]</code> - Has ANY of these tags<br>
• <code>GROUP[has_all:tag1,tag2]</code> - Has ALL these tags<br>
• <code>GROUP[count>=N]</code> - Has at least N tags (supports =, >, >=, <, <=)<br>
<br>
<b>Operators:</b><br>
• <code>AND</code> / <code>&&</code> - Both conditions must be true<br>
• <code>OR</code> / <code>||</code> - At least one condition must be true<br>
• <code>NOT</code> / <code>!</code> - Negates a condition<br>
• <code>( )</code> - Parentheses for grouping<br>
<br>
<b>Important:</b> You can only reference groups that appear <u>before</u> this one in the order.
        """.strip()
    
    def _get_placeholder_text(self) -> str:
        """Get placeholder text for the condition input"""
        return (
            "Examples:\n"
            "  Torso[completed]\n"
            "  Torso[completed] AND Legs[has:fur-covered shins]\n"
            "  (Torso[completed] OR Legs[completed]) AND Features[count>=2]\n\n"
            "Leave empty for no condition (always active)"
        )
    
    def navigate_path(self, path: str):
        """Handle navigation path (required by SettingsWidget)"""
        pass