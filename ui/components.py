"""Reusable interface components."""

import html
from html import escape
import pandas as pd
import streamlit as st

from ui.icons import (
    SUCCESS_ICON,
    WARNING_ICON,
)


def render_subheader(title: str, icon: str) -> None:
    """Display a subheader with an SVG icon."""

    safe_title = html.escape(title)

    # Keep the HTML on one line so Markdown does not treat it as code.
    subheader_html = (
        f'<div class="section-heading">'
        f'<div class="section-heading-icon">{icon}</div>'
        f'<h2>{safe_title}</h2>'
        f'</div>'
    )

    st.markdown(
        subheader_html,
        unsafe_allow_html=True,
    )

def create_quality_card(
    title: str,
    value: str,
    description: str,
    status: str,
    icon: str,
) -> str:
    """Create one reusable data-quality summary card."""

    # Escape dataset-derived text before placing it inside HTML.
    safe_title = escape(str(title))
    safe_value = escape(str(value))
    safe_description = escape(str(description))

    return (
        f'<div class="quality-card quality-card-{status}">'
        f'    <div class="quality-card-content">'
        f'        <div class="quality-card-title">{safe_title}</div>'
        f'        <div class="quality-card-value">{safe_value}</div>'
        f'        <div class="quality-card-description">{safe_description}</div>'
        f"    </div>"
        f'    <div class="quality-card-icon">{icon}</div>'
        f"</div>"
    )

def create_column_profile_table(
    profile: pd.DataFrame,
) -> str:
    """Create the styled column-profile table."""

    # Handle a dataset without columns.
    if profile.empty:
        return (
            '<div class="profile-empty">'
            "No column information is available."
            "</div>"
        )

    table_rows = []

    # Create one table row for every dataset column.
    for column, values in profile.iterrows():
        data_type = str(values["Data Type"])
        completeness = float(values["Complete"])
        unique_values = int(values["Unique Values"])
        status = str(values["Status"])

        # Replace an unavailable percentage with zero.
        if pd.isna(completeness):
            completeness = 0.0

        has_issue = status != "OK"

        # Choose the row and badge appearance.
        if has_issue:
            row_class = "profile-row-warning"
            status_class = "profile-status-warning"
            status_icon = WARNING_ICON
        else:
            row_class = "profile-row-healthy"
            status_class = "profile-status-healthy"
            status_icon = SUCCESS_ICON

        # Protect text originating from the uploaded dataset.
        safe_column = escape(str(column))
        safe_type = escape(data_type)
        safe_status = escape(status)

        table_rows.append(
            f'<tr class="{row_class}">'
            f'    <td class="profile-column-name">'
            f"        {safe_column}"
            f"    </td>"
            f'    <td class="profile-data-type">'
            f"        {safe_type}"
            f"    </td>"
            f'    <td class="profile-complete">'
            f"        {completeness:.1f}%"
            f"    </td>"
            f'    <td class="profile-unique-values">'
            f"        {unique_values:,}"
            f"    </td>"
            f'    <td class="profile-status-cell">'
            f'        <span class="profile-status {status_class}">'
            f'            <span class="profile-status-icon">'
            f"                {status_icon}"
            f"            </span>"
            f"            {safe_status}"
            f"        </span>"
            f"    </td>"
            f"</tr>"
        )

    # Combine all rows into one complete HTML table.
    return (
        '<div class="column-profile-table-wrapper">'
        '    <table class="column-profile-table">'
        "        <thead>"
        "            <tr>"
        '                <th scope="col">Column</th>'
        '                <th scope="col">Detected type</th>'
        '                <th scope="col">Complete</th>'
        '                <th scope="col">Unique values</th>'
        '                <th scope="col">Status</th>'
        "            </tr>"
        "        </thead>"
        "        <tbody>"
        + "".join(table_rows)
        + "        </tbody>"
        "    </table>"
        "</div>"
    )