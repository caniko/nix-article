"""Centralised colour palette for manuscript figures.

Based on Paul Tol's *Bright* qualitative scheme — colorblind-safe and
widely used in science communication.

    Source: https://personal.sron.nl/~pault/

All matplotlib composite figures and TikZ diagrams should draw from these
definitions to ensure consistent colour identity across the manuscript.
"""

from __future__ import annotations

# ── Tol Bright base palette ───────────────────────────────────────────
BLUE = "#4477AA"
CYAN = "#66CCEE"
GREEN = "#228833"
YELLOW = "#CCBB44"
RED = "#EE6677"
PURPLE = "#AA3377"
GREY = "#BBBBBB"

# ── Extended (Tol Vibrant additions) ──────────────────────────────────
ORANGE = "#EE7733"
TEAL = "#009988"

# ── Utility ───────────────────────────────────────────────────────────
DARK = "#2c3e50"
GREY_DARK = "#555555"
GREY_MID = "#888888"
GREY_LIGHT = "#CCCCCC"

# ── Common palette collections ────────────────────────────────────────
FOREST_COLORS: list[str] = [BLUE, GREEN, ORANGE, YELLOW, TEAL, PURPLE]
MOTIF_COLORS: list[str] = [GREEN, BLUE, YELLOW, PURPLE, RED]
