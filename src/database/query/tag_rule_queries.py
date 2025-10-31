from sqlite3 import Connection
from typing import List
import json


class ExportTagRuleQueries:
    """Database queries for managing export tag rules"""
    
    def __init__(self, db: Connection):
        self.db = db
    
    def get_project_rules(self, project_id: int) -> List:
        """
        Get all export tag rules for a project
        
        Args:
            project_id: The project ID
            
        Returns:
            List of ExportTagRule objects
        """
        cursor = self.db.cursor()
        
        cursor.execute("""
            SELECT rule_id, project_id, rule_name, condition, tags_to_add, enabled
            FROM export_tag_rules
            WHERE project_id = ?
            ORDER BY rule_id
        """, (project_id,))
        
        # Import here to avoid circular dependency
        from src.windows.settings_pages.export_conditions_settings import ExportTagRule
        
        rules = []
        for row in cursor.fetchall():
            rule_id, proj_id, name, condition, tags_json, enabled = row
            tags_to_add = json.loads(tags_json)
            
            rule = ExportTagRule(
                rule_id=rule_id,
                project_id=proj_id,
                name=name,
                condition=condition,
                tags_to_add=tags_to_add,
                enabled=bool(enabled)
            )
            rules.append(rule)
        
        cursor.close()
        return rules
    
    def add_rule(self, rule) -> int:
        """
        Add a new export tag rule
        
        Args:
            rule: ExportTagRule object
            
        Returns:
            The ID of the newly created rule
        """
        cursor = self.db.cursor()
        
        tags_json = json.dumps(rule.tags_to_add)
        
        cursor.execute("""
            INSERT INTO export_tag_rules (project_id, rule_name, condition, tags_to_add, enabled)
            VALUES (?, ?, ?, ?, ?)
        """, (rule.project_id, rule.name, rule.condition, tags_json, int(rule.enabled)))
        
        self.db.commit()
        rule_id = cursor.lastrowid
        cursor.close()
        
        return rule_id
    
    def update_rule(self, rule):
        """
        Update an existing export tag rule
        
        Args:
            rule: ExportTagRule object with updated values
        """
        cursor = self.db.cursor()
        
        tags_json = json.dumps(rule.tags_to_add)
        
        cursor.execute("""
            UPDATE export_tag_rules
            SET rule_name = ?,
                condition = ?,
                tags_to_add = ?,
                enabled = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE rule_id = ?
        """, (rule.name, rule.condition, tags_json, int(rule.enabled), rule.id))
        
        self.db.commit()
        cursor.close()
    
    def delete_rule(self, rule_id: int):
        """
        Delete an export tag rule
        
        Args:
            rule_id: The ID of the rule to delete
        """
        cursor = self.db.cursor()
        
        cursor.execute("DELETE FROM export_tag_rules WHERE rule_id = ?", (rule_id,))
        
        self.db.commit()
        cursor.close()
    
    def toggle_rule(self, rule_id: int, enabled: bool):
        """
        Enable or disable a rule
        
        Args:
            rule_id: The ID of the rule
            enabled: Whether the rule should be enabled
        """
        cursor = self.db.cursor()
        
        cursor.execute("""
            UPDATE export_tag_rules
            SET enabled = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE rule_id = ?
        """, (int(enabled), rule_id))
        
        self.db.commit()
        cursor.close()