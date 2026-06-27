"""Tests for anx_plot.helpers."""

from anx_plot import helpers


class TestLabelAbbreviations:
    def test_default_is_empty(self):
        assert helpers._LABEL_ABBREVIATIONS == {}

    def test_can_extend(self):
        helpers._LABEL_ABBREVIATIONS["test_key"] = "TK"
        assert helpers._LABEL_ABBREVIATIONS["test_key"] == "TK"
