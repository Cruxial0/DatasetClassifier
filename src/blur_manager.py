from PyQt6.QtWidgets import QGraphicsBlurEffect
from PyQt6.QtCore import Qt

class BlurManager:
    def __init__(self, widget, blur_radius=10):
        self.widget = widget
        self.blur_radius = blur_radius
        self.blur_effect = None
        self.is_blurred = False
    
    def toggle_blur(self):
        if self.is_blurred:
            # Remove blur
            self.widget.setGraphicsEffect(None)
            self.blur_effect = None
        else:
            # Apply blur
            self.blur_effect = QGraphicsBlurEffect()
            self.blur_effect.setBlurRadius(self.blur_radius)
            self.blur_effect.setBlurHints(QGraphicsBlurEffect.BlurHint.PerformanceHint)
            self.widget.setGraphicsEffect(self.blur_effect)
        
        self.is_blurred = not self.is_blurred
        
    def set_blur_radius(self, radius):
        self.blur_radius = radius
        if self.blur_effect:
            self.blur_effect.setBlurRadius(radius)