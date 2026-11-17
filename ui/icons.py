"""Load reusable SVG icons from the assets directory."""

from pathlib import Path


# Find the main project directory.
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Find the folder containing the downloaded icons.
ICONS_DIR = PROJECT_DIR / "assets" / "icons"


def load_icon(filename: str) -> str:
    """Read and return an SVG icon as HTML."""

    icon_path = ICONS_DIR / filename

    return icon_path.read_text(encoding="utf-8")


# Section icons
DATABASE_ICON = load_icon("dataset.svg")
FINDINGS_ICON = load_icon("clipboard_check.svg")
CHART_ICON = load_icon("chart.svg")
SHIELD_ICON = load_icon("shield.svg")

# Finding icons
WARNING_ICON = load_icon("warning.svg")
SUCCESS_ICON = load_icon("check.svg")
RELATIONSHIP_ICON = load_icon("correlation.svg")

# Inforamtion icons
MISSING_ICON = load_icon("missing.svg")
ROWS_ICON = load_icon("rows.svg")
COLUMNS_ICON = load_icon("columns.svg")