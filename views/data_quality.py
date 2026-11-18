import streamlit as st
import pandas as pd

import analysis
from ui.components import render_subheader, create_quality_card, create_column_profile_table

from ui.icons import (
    SUCCESS_ICON,
    WARNING_ICON,
    SHIELD_ICON
)


def render_data_quality(dataset: pd.DataFrame) -> None:
    """Display the dataset quality summary and detailed results."""

    render_subheader("Data Quality", SHIELD_ICON)

    # Calculate the main quality results.
    n_duplicated_rows = analysis.get_duplicate_row_count(dataset)
    missing_counts = analysis.get_missing_value_counts(dataset)
    missing_count = int(missing_counts.sum())
    missing_column_count = int((missing_counts > 0).sum())

    # Prepare the detailed results for the tabs.
    column_profile = analysis.get_column_profile(dataset)
    rows_with_missing_values = analysis.get_rows_with_missing_values(dataset)

    # Combine both kinds of stored-type problems.
    mixed_type_columns = analysis.get_mixed_type_columns(dataset)
    suspicious_numeric_columns = (analysis.get_suspicious_numeric_columns(dataset))

    type_issue_columns = (set(mixed_type_columns) | set(suspicious_numeric_columns))

    total_type_issues = len(type_issue_columns)

    # Calculate the percentage of values that are present.
    total_values = dataset.size
    present_values = total_values - missing_count

    completeness = (
        present_values / total_values * 100
        if total_values > 0
        else 0.0
    )

    # Set the missing-values card state.
    if missing_count == 0:
        missing_status = "healthy"
        missing_icon = SUCCESS_ICON
        missing_description = "All values are present"
    else:
        missing_status = "warning"
        missing_icon = WARNING_ICON

        column_word = (
            "column"
            if missing_column_count == 1
            else "columns"
        )

        missing_description = (
            f"Across {missing_column_count} {column_word}"
        )

    # Set the duplicate-rows card state.
    if n_duplicated_rows == 0:
        duplicate_status = "healthy"
        duplicate_icon = SUCCESS_ICON
        duplicate_description = "All rows are unique"
    else:
        duplicate_status = "warning"
        duplicate_icon = WARNING_ICON
        duplicate_description = "Repeated rows detected"

    # Set the type-consistency card state.
    if total_type_issues == 0:
        type_status = "healthy"
        type_icon = SUCCESS_ICON
        type_value = "Consistent"
        type_description = "No mixed stored types"
    else:
        type_status = "warning"
        type_icon = WARNING_ICON

        issue_word = (
            "issue"
            if total_type_issues == 1
            else "issues"
        )

        type_value = (
            f"{total_type_issues} {issue_word} found"
        )

        # Name the affected column when there is only one.
        if total_type_issues == 1:
            affected_column = next(iter(type_issue_columns))
            type_description = (
                f"Review values in {affected_column}"
            )
        else:
            type_description = (
                f"Across {total_type_issues} columns"
            )
    if completeness >= 95:
        completeness_status = "healthy"
        completeness_icon = SUCCESS_ICON
    elif completeness >= 80:
        completeness_status = "warning"
        completeness_icon = WARNING_ICON
    else:
        completeness_status = "danger"
        completeness_icon = WARNING_ICON

    # Build the four summary cards.
    quality_cards = [
        create_quality_card(
            title="Completeness",
            value=f"{completeness:.2f}%",
            description="Values present",
            status=completeness_status,
            icon=completeness_icon ,
        ),
        create_quality_card(
            title="Missing values",
            value=f"{missing_count:,}",
            description=missing_description,
            status=missing_status,
            icon=missing_icon,
        ),
        create_quality_card(
            title="Duplicate rows",
            value=f"{n_duplicated_rows:,}",
            description=duplicate_description,
            status=duplicate_status,
            icon=duplicate_icon,
        ),
        create_quality_card(
            title="Type consistency",
            value=type_value,
            description=type_description,
            status=type_status,
            icon=type_icon,
        ),
    ]

    # Display the cards inside the responsive CSS grid.
    st.markdown(
        '<div class="quality-metrics">'
        + "".join(quality_cards)
        + "</div>",
        unsafe_allow_html=True,
    )

    # Create the detailed quality tabs.
    profile_tab, missing_tab, duplicates_tab = st.tabs(
        [
            "Column Profile",
            "Missing Values",
            "Duplicates",
        ]
    )

    with profile_tab:
        st.markdown(
        create_column_profile_table(column_profile),
        unsafe_allow_html=True,
    )
    with missing_tab:
        if not rows_with_missing_values.empty:
            max_preview_rows = 500

            # Keep only columns that contain missing values.
            missing_columns = dataset.columns[
                dataset.isna().any()
            ].tolist()

            missing_preview = (
                rows_with_missing_values[missing_columns]
                .head(max_preview_rows)
                .copy()
            )

            # Preserve the original dataset row index.
            missing_preview.insert(
                0,
                "Row",
                missing_preview.index,
            )

            def highlight_missing(value):
                if pd.isna(value):
                    return (
                        "background-color: #fff0cd; "
                        "color: #b66b00; "
                        "font-weight: 700;"
                    )

                return ""

            styled_missing_rows = missing_preview.style.map(
                highlight_missing
            )

            number_column_config = {}

            for column in missing_preview.select_dtypes(
                include="number"
            ).columns:
                values = missing_preview[column].dropna()

                if not values.empty and (values % 1 == 0).all():
                    number_format = "%.0f"
                else:
                    number_format = "%.2f"

                number_column_config[column] = (
                    st.column_config.NumberColumn(
                        format=number_format
                    )
                )

            # Mention truncation only when rows were actually omitted.
            if len(rows_with_missing_values) > max_preview_rows:
                st.caption(
                    f"Showing the first {max_preview_rows:,} of "
                    f"{len(rows_with_missing_values):,} affected rows."
                )

            st.dataframe(
                styled_missing_rows,
                width="stretch",
                hide_index=True,
                column_config=number_column_config,
            )

        else:
            st.success("No missing values found.")

    with duplicates_tab:
        st.caption("Showing original and repeated records for comparison.")
        if n_duplicated_rows == 0:
            st.success("No duplicates found.")
        else:
            st.dataframe(
                analysis.get_duplicate_rows(dataset),
                use_container_width=True,
            )