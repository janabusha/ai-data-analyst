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

def create_at_a_glance_card(
    statistics: list[tuple[str, str]],
    insight: str | None = None,
) -> str:
    """Create the content of an at-a-glance statistics card."""

    statistic_items = []

    for label, value in statistics:
        safe_label = escape(str(label))
        safe_value = escape(str(value))

        statistic_items.append(
            f'<div class="glance-stat">'
            f'<div class="glance-stat-label">{safe_label}</div>'
            f'<div class="glance-stat-value">{safe_value}</div>'
            f'</div>'
        )

    statistics_html = "".join(statistic_items)

    insight_html = ""

    if insight:
        safe_insight = escape(str(insight))

        insight_html = (
            f'<div class="glance-insight">'
            f'<span class="glance-insight-icon">i</span>'
            f'<span>{safe_insight}</span>'
            f'</div>'
        )

    return (
        f'<div class="glance-card">'
        f'<div class="glance-stat-grid">{statistics_html}</div>'
        f'{insight_html}'
        f'</div>'
    )

def create_relationship_list(
    relationships: pd.DataFrame,
    identifiers_excluded: bool,
) -> str:
    """Create a styled list of the strongest relationships."""

    relationship_rows = []

    for rank, (_, relationship) in enumerate(
        relationships.head(3).iterrows(),
        start=1,
    ):
        column_1 = escape(str(relationship["Column 1"]))
        column_2 = escape(str(relationship["Column 2"]))
        correlation = float(relationship["Correlation"])

        value_color = (
            "#087f70"
            if correlation >= 0
            else "#c5544d"
        )

        relationship_rows.append(
            '<div style="'
            'display:grid;'
            'grid-template-columns:34px minmax(0,1fr) auto;'
            'align-items:center;'
            'gap:0.7rem;'
            'min-height:56px;'
            'padding:0.55rem 0;'
            'border-bottom:1px solid #dde4e2;'
            '">'
            
            f'<div style="'
            'display:flex;'
            'align-items:center;'
            'justify-content:center;'
            'width:32px;'
            'height:32px;'
            'border-radius:50%;'
            'background:#d9f3ef;'
            'color:#087f70;'
            'font-size:0.85rem;'
            'font-weight:750;'
            f'">{rank}</div>'

            '<div style="'
            'display:flex;'
            'align-items:center;'
            'gap:0.4rem;'
            'min-width:0;'
            'color:#20242c;'
            'font-size:0.82rem;'
            'font-weight:600;'
            '">'

            f'<span title="{column_1}" style="'
            'min-width:0;'
            'overflow:hidden;'
            'text-overflow:ellipsis;'
            'white-space:nowrap;'
            f'">{column_1}</span>'

            '<span style="'
            'flex-shrink:0;'
            'color:#0c9586;'
            'font-size:1.1rem;'
            'font-weight:700;'
            '">&#8596;</span>'

            f'<span title="{column_2}" style="'
            'min-width:0;'
            'overflow:hidden;'
            'text-overflow:ellipsis;'
            'white-space:nowrap;'
            f'">{column_2}</span>'

            '</div>'

            f'<div style="'
            f'color:{value_color};'
            'font-size:0.95rem;'
            'font-weight:800;'
            'text-align:right;'
            'white-space:nowrap;'
            f'">{correlation:.2f}</div>'

            '</div>'
        )

    identifier_notice = ""

    if identifiers_excluded:
        identifier_notice = (
            '<div style="'
            'display:flex;'
            'align-items:flex-start;'
            'gap:0.7rem;'
            'margin-top:1rem;'
            'padding:0.85rem;'
            'border-radius:12px;'
            'background:#dff5f1;'
            'color:#20242c;'
            'font-size:0.8rem;'
            'line-height:1.4;'
            '">'

            '<div style="'
            'display:flex;'
            'align-items:center;'
            'justify-content:center;'
            'flex:0 0 auto;'
            'width:22px;'
            'height:22px;'
            'border:2px solid #0c9586;'
            'border-radius:50%;'
            'color:#0c9586;'
            'font-size:0.75rem;'
            'font-weight:800;'
            '">i</div>'

            '<div>'
            'Identifier-like columns are excluded automatically.'
            '</div>'

            '</div>'
        )

    return (
        '<div style="width:100%;margin-top:0.65rem;">'

        '<div style="'
        'width:100%;'
        'border-top:1px solid #dde4e2;'
        '">'
        f'{"".join(relationship_rows)}'
        '</div>'

        f'{identifier_notice}'

        '<div style="'
        'margin-top:0.8rem;'
        'color:#8490a3;'
        'font-size:0.78rem;'
        'line-height:1.4;'
        '">'
        'Correlation shows association, not causation.'
        '</div>'

        '</div>'
    )