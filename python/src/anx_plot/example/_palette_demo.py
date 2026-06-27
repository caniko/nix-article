"""Example custom palette for a downstream article project.

Shows how to extend the base anx_plot palette with project-specific colors.
"""

from anx_plot.palette import BLUE, GREEN, ORANGE, RED, TEAL, YELLOW

MY_COLORS: dict[str, str] = {
    "primary": BLUE,
    "secondary": GREEN,
    "accent": ORANGE,
    "highlight": YELLOW,
    "error": RED,
    "info": TEAL,
}
