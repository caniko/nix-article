"""Verify all anx_plot modules import cleanly."""


def test_import_palette():
    import anx_plot.palette  # noqa: F401


def test_import_helpers():
    import anx_plot.helpers  # noqa: F401


def test_import_sizing():
    import anx_plot.sizing  # noqa: F401


def test_import_layout():
    import anx_plot.layout  # noqa: F401


def test_import_standard():
    import anx_plot.standard  # noqa: F401


def test_import_export():
    import anx_plot.export  # noqa: F401


def test_import_cli():
    import anx_plot.cli  # noqa: F401


def test_import_line_style():
    import anx_plot.line_style  # noqa: F401


def test_import_significance():
    import anx_plot.significance  # noqa: F401
