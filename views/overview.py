import streamlit as st
import pandas as pd
import analysis
import chart_visuals
import json
import html
from ui.components import render_subheader
from model_client import create_model_client

from ui.icons import (
    CHART_ICON,
    DATABASE_ICON,
    FINDINGS_ICON,
    RELATIONSHIP_ICON,
    SUCCESS_ICON,
    WARNING_ICON,
    MISSING_ICON,
    ROWS_ICON,
    COLUMNS_ICON
)

def render_findings(dataset: pd.DataFrame) -> None:
    # Calculate basic quality results.
    missing_count = int(dataset.isna().sum().sum())
    missing_columns = analysis.get_missing_value_counts(dataset)
    correlation_matrix = analysis.get_correlation_matrix(dataset)
    stongest_relationship = analysis.get_strongest_relationships(correlation_matrix)

    missing_columns = (
        missing_columns[missing_columns > 0]
        .sort_values(ascending=False)
        .head(3)
    )
    # Create one formatted entry for every affected column.
    missing_parts = [
        (
            f"<strong>{html.escape(str(column))}</strong> "
            f"- <strong>{count:,}</strong>"
        )
        for column, count in missing_columns.items()
    ]
    duplicate_count = int(dataset.duplicated().sum())

    # Find columns containing different stored Python types.
    mixed_type_columns = []

    for column in dataset.columns:
        stored_types = dataset[column].dropna().map(type).nunique()

        if stored_types > 1:
            mixed_type_columns.append(str(column))

    # Choose the correct status and message for missing data.
    if missing_count > 0:
        missing_status = "warning"
        missing_icon = WARNING_ICON
        missing_title = "Missing data"
        # Join the column names using natural English.
        if len(missing_parts) == 1:
            missing_columns_text = missing_parts[0]

        elif len(missing_parts) == 2:
            missing_columns_text = " and ".join(missing_parts)

        else:
            missing_columns_text = (
                ", ".join(missing_parts[:-1])
                + f", and {missing_parts[-1]}"
            )

        # Use the correct singular or plural wording.
        if missing_count == 1:
            missing_text = (
                f"<strong>1 value</strong> is missing. "
                f"It is in {missing_columns_text}."
            )
 
        else:
            missing_text = (
                f"<strong>{missing_count:,} values</strong> are missing. "
                f"Most are in {missing_columns_text}."
            )
    else:
        missing_status = "healthy"
        missing_icon = SUCCESS_ICON
        missing_title = "No missing data"
        missing_text = "All values are present."
    # Choose the correct status and message for correlations.
    if not stongest_relationship.empty:
        corr_status = "healthy"
        corr_icon = RELATIONSHIP_ICON
        corr_title = "Strongest relationship found"
        corr_text = (
            "Strongest relationship is between columns "
            f"<strong>{stongest_relationship.iloc[0]['Column 1']}</strong> and "
            f"<strong>{stongest_relationship.iloc[0]['Column 2']}</strong>."
            f" With correlation of <strong>{round(stongest_relationship.iloc[0]['Correlation'],2)}</strong>."
        )
    else:
        corr_status = "warning"
        corr_icon = RELATIONSHIP_ICON
        corr_title = "No correlations found."
        corr_text = "At least two numeric columns are required to calculate relationships."

    # Choose the correct status and message for stored types.
    if mixed_type_columns:
        type_status = "warning"
        type_icon = WARNING_ICON
        type_title = "Mixed stored types"

        # Escape column names before inserting them into HTML.
        column_names = ", ".join(
            html.escape(column) for column in mixed_type_columns
        )

        type_text = f"Mixed types detected in:<strong> {column_names}<strong>."
    else:
        type_status = "healthy"
        type_icon = SUCCESS_ICON
        type_title = "Types are consistent"
        type_text = "No mixed stored types were detected."
        
        # Choose the correct status and message for duplicate rows.
    if duplicate_count > 0:
        duplicate_status = "warning"
        duplicate_icon = WARNING_ICON
        duplicate_title = "Duplicate rows"
        duplicate_text = f"{duplicate_count:,} duplicate rows detected."
    else:
        duplicate_status = "healthy"
        duplicate_icon = SUCCESS_ICON
        duplicate_title = "No duplicate rows"
        duplicate_text = "All records are unique."

    # Build all findings as one HTML block.
    findings_html = f"""
    <div class="findings-list">
    <div class="finding-item">
    <div class="finding-icon {missing_status}">{missing_icon}</div>
    <div>
    <div class="finding-title">{missing_title}</div>
    <div class="finding-text">{missing_text}</div>
    </div>
    </div>
    <div class="finding-item">
    <div class="finding-icon {duplicate_status}">{duplicate_icon}</div>
    <div>
    <div class="finding-title">{duplicate_title}</div>
    <div class="finding-text">{duplicate_text}</div>
    </div>
    </div>
    <div class="finding-item">
    <div class="finding-icon {type_status}">{type_icon}</div>
    <div>
    <div class="finding-title">{type_title}</div>
    <div class="finding-text">{type_text}</div>
    </div>
    </div>
	<div class="finding-item">
	<div class="finding-icon {corr_status}">{corr_icon}</div>
	<div>
	<div class="finding-title">{corr_title}</div>
	<div class="finding-text">{corr_text}</div>
	</div>
	</div>
    </div>
    """

    st.markdown(findings_html, unsafe_allow_html=True)

def choose_visualization_with_ai(
    profile: list[dict],
) -> dict:
    client, model_name = create_model_client()
    prompt = f"""
    Choose one useful visualization for this dataset.

    Dataset columns:
    {profile}

    You may choose only:
    - line
    - bar
    - scatter

    Return JSON only in this format:
    {{
        "chart_type": "line",
        "x": "column name",
        "y": "column name",
        "aggregation": "sum",
        "title": "chart title"
    }}

        Important rules:

        - Do not use likely identifiers as chart axes or measurements.
        - Columns with names such as id, index, rank, code, or number
            may be identifiers.
        - A column with nearly 100% unique values may be an identifier.
        - Use a line chart only when the x-axis represents time,
            such as a date, year, month, or timestamp.
        - Use a bar chart for a categorical column with a manageable
            number of categories.
        - Use a scatter chart only for two meaningful numeric measurements.
        - Do not select a chart simply because two columns are numeric.
        - Prefer a chart that gives a useful high-level overview.
    """

    response = client.chat(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        format="json",
        think=False,
    )
    return json.loads(response.message.content)


def render_overview(dataset: pd.DataFrame) -> None:
    with st.spinner(
    "Analyzing your data...",
    show_time=True,
    width="stretch",
    ):
        visualization_profile = analysis.get_visualization_profile(dataset)
        chart_choice = choose_visualization_with_ai(visualization_profile)

    preview_column, findings_column = st.columns(
        [2.2, 1],
        gap="medium",
        border=True,
    )

    with preview_column:
        render_subheader("Data preview", DATABASE_ICON)
        row_count = dataset.shape[0]
        column_count = dataset.shape[1]
        missing_count = int(dataset.isna().sum().sum())
        # Choose the missing-data badge appearance.
        if missing_count == 0:
            badge_class = "dataset-badge-success"
            missing_badge_icon = SUCCESS_ICON
        else:
            badge_class = "dataset-badge-warning"
            missing_badge_icon = MISSING_ICON

        badges_html = (
            f'<div class="dataset-badges">'
            f'<div class="dataset-badge">'
            f'<span class="dataset-badge-icon">{ROWS_ICON}</span>'
            f'<strong>{row_count:,}</strong> rows'
            f'</div>'
            f'<div class="dataset-badge">'
            f'<span class="dataset-badge-icon">{COLUMNS_ICON}</span>'
            f'<strong>{column_count:,}</strong> columns'
            f'</div>'
            f'<div class="dataset-badge {badge_class}">'
            f'<span class="dataset-badge-icon">{missing_badge_icon}</span>'
            f'<strong>{missing_count:,}</strong> missing'
            f'</div>'
            f'</div>'
        )

        st.markdown(
            badges_html,
            unsafe_allow_html=True,
        )
        preview_data = dataset.head(10)
        column_config = {
            column: st.column_config.Column(width=150)
            for column in preview_data.columns
        }
        st.dataframe(
            preview_data,
            width="stretch",
            height=420,
            hide_index=True,
            column_config=column_config,
        )
        st.caption("Showing the first 10 rows of the dataset.")
        
    with findings_column:
        render_subheader("Findings", FINDINGS_ICON)
        st.caption(
            "Summary based on Python-computed results. "
            "Review the Data Quality and Exploration tabs for details."
        )
        render_findings(dataset)

    with st.container(border=True):
        render_subheader("Quick overview", CHART_ICON)
        
        chart_visuals.display_chart(
        	dataset,
            chart_choice,
        )
        st.markdown(
			"""
			<div class="chart-disclaimer">
				<strong>AI-assisted chart.</strong>
				AI selected the chart type and columns using dataset metadata and
				summary statistics. The full dataset was not sent to the model.
				Chart values are calculated with Python. Automated suggestions may
				not always show the most meaningful relationship.
			</div>
			""",
			unsafe_allow_html=True,
			)
