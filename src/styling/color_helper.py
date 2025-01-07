class ColorHelper:
    def __init__(self, primary_color: str):
        """
        Initialize ColorHelper with a primary color in hex format (e.g., '#5a9bd8')
        """
        if not primary_color.startswith('#') or len(primary_color) != 7:
            raise ValueError("Color must be in hex format (e.g., '#5a9bd8')")
        self.primary_color = primary_color.upper()
        self.rgb = self._hex_to_rgb(primary_color)

    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, rgb: tuple) -> str:
        """Convert RGB tuple to hex color."""
        return '#{:02x}{:02x}{:02x}'.format(*[min(255, max(0, int(x))) for x in rgb]).upper()

    def _calculate_luminance(self) -> float:
        """Calculate relative luminance of the color."""
        r, g, b = self.rgb
        return (max(r, g, b) + min(r, g, b)) / (2 * 255)

    def _adjust_color(self, rgb: tuple, factor: float) -> tuple:
        """Adjust RGB values by a factor."""
        return tuple(min(255, max(0, x * factor)) for x in rgb)

    def get_variants(self, hover_adjust: float = 0.25, active_adjust: float = 0.35) -> dict:
        """
        Generate hover and active color variants.
        
        Args:
            hover_adjust: Amount to adjust for hover state (default 0.15 = 15%)
            active_adjust: Amount to adjust for active state (default 0.25 = 25%)
        
        Returns:
            dict: Dictionary containing primary, hover, and active colors in hex format
        """
        # Determine if we should lighten or darken based on luminance
        luminance = self._calculate_luminance()
        hover_factor = 1 - hover_adjust if luminance > 0.5 else 1 + hover_adjust
        active_factor = 1 - active_adjust if luminance > 0.5 else 1 + active_adjust
        
        # Calculate hover color
        hover_rgb = self._adjust_color(self.rgb, hover_factor)
        hover_color = self._rgb_to_hex(hover_rgb)
        
        # Calculate active color (more pronounced adjustment)
        active_rgb = self._adjust_color(self.rgb, active_factor)
        active_color = self._rgb_to_hex(active_rgb)
        
        return {
            'primary': self.primary_color,
            'hover': hover_color,
            'active': active_color
        }

    def get_complementary(self) -> str:
        """Generate complementary color (180° on the color wheel)."""
        r, g, b = self.rgb
        return self._rgb_to_hex((255 - r, 255 - g, 255 - b))

    def get_analogous(self) -> tuple:
        """
        Generate analogous colors (30° on either side on the color wheel).
        Basic implementation - for true analogous colors, conversion to HSL would be more accurate.
        """
        r, g, b = self.rgb
        return (
            self._rgb_to_hex((int(r * 0.9), int(g * 1.1), int(b * 0.9))),
            self._rgb_to_hex((int(r * 1.1), int(g * 0.9), int(b * 1.1)))
        )