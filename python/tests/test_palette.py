"""Tests for anx_plot.palette."""

from anx_plot import palette


class TestTolBright:
    def test_blue_is_correct(self):
        assert palette.BLUE == "#4477AA"

    def test_red_is_correct(self):
        assert palette.RED == "#EE6677"

    def test_green_is_correct(self):
        assert palette.GREEN == "#228833"

    def test_yellow_is_correct(self):
        assert palette.YELLOW == "#CCBB44"

    def test_purple_is_correct(self):
        assert palette.PURPLE == "#AA3377"

    def test_cyan_is_correct(self):
        assert palette.CYAN == "#66CCEE"

    def test_grey_is_correct(self):
        assert palette.GREY == "#BBBBBB"

    def test_orange_is_correct(self):
        assert palette.ORANGE == "#EE7733"

    def test_teal_is_correct(self):
        assert palette.TEAL == "#009988"


class TestUtilColors:
    def test_dark(self):
        assert palette.DARK == "#2c3e50"

    def test_grey_dark(self):
        assert palette.GREY_DARK == "#555555"

    def test_grey_mid(self):
        assert palette.GREY_MID == "#888888"

    def test_grey_light(self):
        assert palette.GREY_LIGHT == "#CCCCCC"


class TestCollections:
    def test_forest_colors_length(self):
        assert len(palette.FOREST_COLORS) == 6

    def test_motif_colors_length(self):
        assert len(palette.MOTIF_COLORS) == 5

    def test_forest_contains_blue(self):
        assert palette.BLUE in palette.FOREST_COLORS
