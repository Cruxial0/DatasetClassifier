from typing import List, Optional
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                            QListWidget, QListWidgetItem, QMessageBox, QWidget)
from PyQt6.QtCore import Qt

from src.windows.settings_pages.settings_widget import SettingsWidget
from src.tagging.tag_group import TagGroup
from src.parser import parse_condition, validate_references
from src.styling.styling_utils import styled_information_box, styled_warning_box

class ExportTagRule:
    """Represents a rule for adding tags during export based on conditions"""
    def __init__(self, rule_id: int = -1, project_id: int = -1, name: str = "", 
                 condition: str = "", tags_to_add: List[str] = None, enabled: bool = True):
        self.id = rule_id
        self.project_id = project_id
        self.name = name
        self.condition = condition  # Uses the same syntax as activation conditions
        self.tags_to_add = tags_to_add or []
        self.enabled = enabled
    
    def __repr__(self):
        return f"ExportTagRule(id={self.id}, name='{self.name}', condition='{self.condition}', tags={self.tags_to_add}, enabled={self.enabled})"


class ExportTagRuleWidget(QWidget):
    """Widget for displaying a single export tag rule in the list"""
    def __init__(self, rule: ExportTagRule, style_manager, parent=None):
        super().__init__(parent)
        self.rule = rule
        self.style_manager = style_manager
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Rule name and info
        info_layout = QVBoxLayout()
        
        name_label = QLabel(self.rule.name or "Unnamed Rule")
        name_label.setStyleSheet(self.style_manager.get_stylesheet(QLabel, 'bold'))
        
        condition_label = QLabel(f"Condition: {self.rule.condition or 'None'}")
        condition_label.setStyleSheet(self.style_manager.get_stylesheet(QLabel, 'subtext'))
        
        tags_label = QLabel(f"Adds: {', '.join(self.rule.tags_to_add) if self.rule.tags_to_add else 'None'}")
        tags_label.setStyleSheet(self.style_manager.get_stylesheet(QLabel, 'subtext'))
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(condition_label)
        info_layout.addWidget(tags_label)
        
        layout.addLayout(info_layout, 1)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        edit_btn = QPushButton("Edit")
        edit_btn.setStyleSheet(self.style_manager.get_stylesheet(QPushButton, 'accent'))
        edit_btn.clicked.connect(lambda: self.parent().parent().parent().edit_rule(self.rule))
        
        delete_btn = QPushButton("Delete")
        delete_btn.setStyleSheet(self.style_manager.get_stylesheet(QPushButton, 'warning'))
        delete_btn.clicked.connect(lambda: self.parent().parent().parent().delete_rule(self.rule))
        
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)


class ExportTagRulesSettings(SettingsWidget):
    """Settings page for managing export tag rules"""
    
    def __init__(self, parent=None):
        self._pages = {}
        self._page_creators = {
            "rules_list": self.create_rules_list_page,
            "rule_editor": lambda **kwargs: self.create_rule_editor_page(**kwargs)
        }
        
        super().__init__(parent)
        
        self.rules: List[ExportTagRule] = []
        self.current_rule: Optional[ExportTagRule] = None
        self.tag_groups: List[TagGroup] = []
        
        self.load_data()
        self.switch_page("rules_list")
    
    def navigate_path(self, path: str):
        """Navigate to a specific path in the settings"""
        pass  # Can be extended later
    
    def init_ui(self):
        """Initialize the main UI with a stacked widget"""
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
    
    def load_data(self):
        """Load export tag rules and tag groups from database"""
        # Load tag groups for validation
        self.tag_groups = self.db.tags.get_project_tags(self.active_project.id)
        
        # Load export tag rules
        self.rules = self.db.export_rules.get_project_rules(self.active_project.id)
    
    def create_rules_list_page(self) -> QWidget:
        """Create the main page showing all export tag rules"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addLayout(self._create_header("Export Tag Rules", font_size=14))
        header_layout.addStretch(1)
        
        new_btn = self._create_button("New Rule", "Create a new export tag rule")
        new_btn.clicked.connect(self.create_new_rule)
        header_layout.addWidget(new_btn)
        
        layout.addLayout(header_layout)
        
        # Info label
        info_label = QLabel(
            "Define rules to automatically add tags during export based on conditions.\n"
            "Example: If an image has 'from above' AND 'from side', add 'mixed perspectives'"
        )
        info_label.setStyleSheet(self.style_manager.get_stylesheet(QLabel, 'subtext'))
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Rules list
        self.rules_list = QListWidget()
        self.rules_list.setStyleSheet(self.style_manager.get_stylesheet(QListWidget))
        layout.addWidget(self.rules_list)
        
        # Populate rules
        self.refresh_rules_list()
        
        return widget
    
    def create_rule_editor_page(self, rule: Optional[ExportTagRule] = None) -> QWidget:
        """Create the page for editing/creating a rule"""
        from PyQt6.QtWidgets import QLineEdit, QTextEdit, QCheckBox
        
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Header
        title = "Edit Rule" if rule else "New Rule"
        layout.addLayout(self._create_header(title, font_size=14))
        
        # Rule name
        name_layout = QHBoxLayout()
        name_label = QLabel("Rule Name:")
        name_label.setStyleSheet(self.style_manager.get_stylesheet(QLabel))
        self.rule_name_input = QLineEdit()
        self.rule_name_input.setStyleSheet(self.style_manager.get_stylesheet(QLineEdit))
        self.rule_name_input.setPlaceholderText("e.g., 'Add mixed perspectives tag'")
        if rule:
            self.rule_name_input.setText(rule.name)
        
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.rule_name_input, 1)
        layout.addLayout(name_layout)
        
        # Condition
        condition_label = QLabel("Condition (using tag group syntax):")
        condition_label.setStyleSheet(self.style_manager.get_stylesheet(QLabel))
        layout.addWidget(condition_label)
        
        self.condition_input = QTextEdit()
        self.condition_input.setStyleSheet(self.style_manager.get_stylesheet(QTextEdit))
        self.condition_input.setPlaceholderText(
            "Examples:\n"
            "  Composition[has:from above] AND BodyFeatures[has:long ears]\n"
            "  Composition[completed]\n"
            "  BodyFeatures[count>=3]"
        )
        self.condition_input.setMaximumHeight(100)
        if rule:
            self.condition_input.setPlainText(rule.condition)
        
        layout.addWidget(self.condition_input)
        
        # Validation button
        validate_btn = QPushButton("Validate Condition")
        validate_btn.setStyleSheet(self.style_manager.get_stylesheet(QPushButton))
        validate_btn.clicked.connect(self.validate_condition)
        layout.addWidget(validate_btn)
        
        # Tags to add
        tags_label = QLabel("Tags to Add (comma-separated):")
        tags_label.setStyleSheet(self.style_manager.get_stylesheet(QLabel))
        layout.addWidget(tags_label)
        
        self.tags_input = QLineEdit()
        self.tags_input.setStyleSheet(self.style_manager.get_stylesheet(QLineEdit))
        self.tags_input.setPlaceholderText("e.g., 'mixed perspectives, full body'")
        if rule and rule.tags_to_add:
            self.tags_input.setText(", ".join(rule.tags_to_add))
        
        layout.addWidget(self.tags_input)
        
        # Enabled checkbox
        self.enabled_checkbox = QCheckBox("Rule Enabled")
        self.enabled_checkbox.setStyleSheet(self.style_manager.get_stylesheet(QCheckBox))
        self.enabled_checkbox.setChecked(rule.enabled if rule else True)
        layout.addWidget(self.enabled_checkbox)
        
        layout.addStretch(1)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(self.style_manager.get_stylesheet(QPushButton, 'accept'))
        save_btn.clicked.connect(lambda: self.save_rule(rule))
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(self.style_manager.get_stylesheet(QPushButton))
        cancel_btn.clicked.connect(lambda: self.switch_page("rules_list"))
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        return widget
    
    def refresh_rules_list(self):
        """Refresh the list of rules displayed"""
        self.rules_list.clear()
        
        for rule in self.rules:
            item = QListWidgetItem()
            widget = ExportTagRuleWidget(rule, self.style_manager, self.rules_list)
            
            self.rules_list.addItem(item)
            self.rules_list.setItemWidget(item, widget)
            item.setSizeHint(widget.sizeHint())
    
    def create_new_rule(self):
        """Create a new export tag rule"""
        self.current_rule = None
        self.switch_page("rule_editor")
    
    def edit_rule(self, rule: ExportTagRule):
        """Edit an existing rule"""
        self.current_rule = rule
        self.switch_page("rule_editor", rule=rule)
    
    def validate_condition(self):
        """Validate the condition syntax"""
        condition_text = self.condition_input.toPlainText().strip()
        
        if not condition_text:
            styled_information_box(self, "Validation", "Condition is empty", self.style_manager)
            return
        
        try:
            # Parse the condition
            parsed = parse_condition(condition_text)
            
            if parsed is None:
                styled_information_box(self, "Validation", "Condition is empty", self.style_manager)
                return
            
            # Create a dummy tag group for validation
            from src.tagging.tag_group import TagGroup
            dummy_group = TagGroup(
                id=-1,
                project_id=self.active_project.id,
                name="__validation__",
                order=len(self.tag_groups),
                condition=condition_text
            )
            
            # Validate references
            validate_references(parsed, dummy_group, self.tag_groups)
            
            styled_information_box(
                self, 
                "Validation Successful", 
                "The condition syntax is valid and all referenced groups/tags exist!",
                self.style_manager
            )
        except ValueError as e:
            styled_warning_box(
                self,
                "Validation Error",
                f"Invalid condition:\n{str(e)}",
                self.style_manager
            )
        except Exception as e:
            styled_warning_box(
                self,
                "Validation Error",
                f"Error validating condition:\n{str(e)}",
                self.style_manager
            )
    
    def save_rule(self, existing_rule: Optional[ExportTagRule]):
        """Save the current rule"""
        name = self.rule_name_input.text().strip()
        condition = self.condition_input.toPlainText().strip()
        tags_text = self.tags_input.text().strip()
        enabled = self.enabled_checkbox.isChecked()
        
        # Validate inputs
        if not name:
            styled_warning_box(self, "Validation Error", "Please enter a rule name", self.style_manager)
            return
        
        if not condition:
            styled_warning_box(self, "Validation Error", "Please enter a condition", self.style_manager)
            return
        
        if not tags_text:
            styled_warning_box(self, "Validation Error", "Please enter at least one tag to add", self.style_manager)
            return
        
        # Parse tags
        tags_to_add = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
        
        if not tags_to_add:
            styled_warning_box(self, "Validation Error", "Please enter at least one tag to add", self.style_manager)
            return
        
        # Validate condition syntax
        try:
            parsed = parse_condition(condition)
            if parsed is None:
                styled_warning_box(self, "Validation Error", "Condition cannot be empty", self.style_manager)
                return
            
            # Create a dummy tag group for validation
            from src.tagging.tag_group import TagGroup
            dummy_group = TagGroup(
                id=-1,
                project_id=self.active_project.id,
                name="__validation__",
                order=len(self.tag_groups),
                condition=condition
            )
            
            validate_references(parsed, dummy_group, self.tag_groups)
        except ValueError as e:
            styled_warning_box(
                self,
                "Validation Error",
                f"Invalid condition:\n{str(e)}",
                self.style_manager
            )
            return
        
        # Create or update rule
        if existing_rule:
            existing_rule.name = name
            existing_rule.condition = condition
            existing_rule.tags_to_add = tags_to_add
            existing_rule.enabled = enabled
            
            # Update in database
            self.db.export_rules.update_rule(existing_rule)
        else:
            new_rule = ExportTagRule(
                project_id=self.active_project.id,
                name=name,
                condition=condition,
                tags_to_add=tags_to_add,
                enabled=enabled
            )
            
            # Save to database
            rule_id = self.db.export_rules.add_rule(new_rule)
            new_rule.id = rule_id
            
            self.rules.append(new_rule)
        
        self.refresh_rules_list()
        self.switch_page("rules_list")
    
    def delete_rule(self, rule: ExportTagRule):
        """Delete a rule"""
        reply = QMessageBox.question(
            self,
            "Delete Rule",
            f"Are you sure you want to delete the rule '{rule.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Delete from database
            self.db.export_rules.delete_rule(rule.id)
            
            self.rules.remove(rule)
            self.refresh_rules_list()
    
    def get_page(self, page_name: str, **kwargs):
        """Get or create a page"""
        # For rule_editor, always create fresh to avoid stale state
        if page_name == "rule_editor":
            return self._page_creators[page_name](**kwargs)
        
        if page_name not in self._pages:
            creator = self._page_creators.get(page_name)
            if creator:
                page = creator(**kwargs)
                self._pages[page_name] = page
                self.main_layout.addWidget(page)
        
        return self._pages.get(page_name)
    
    def switch_page(self, page_name: str, **kwargs):
        """Switch to a different page"""
        # Remove all widgets from layout
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # Get and display the requested page
        page = self.get_page(page_name, **kwargs)
        if page:
            self.main_layout.addWidget(page)