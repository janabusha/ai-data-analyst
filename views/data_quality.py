import streamlit as st
import pandas as pd

import analysis


def render_data_quality(dataset: pd.DataFrame) -> None:

    n_duplicated_rows = analysis.get_duplicate_row_count(dataset)
    column_profile = analysis.get_column_profile(dataset)
    rows_with_missing_values = analysis.get_rows_with_missing_values(dataset)
    mixed_type_columns = analysis.get_mixed_type_columns(dataset)
    suspicious_numeric_columns = analysis.get_suspicious_numeric_columns(dataset)
    missing_col, duplicates_col, typeis_col = st.columns(3)
    type_issue_columns = set(mixed_type_columns) | set(suspicious_numeric_columns)
    total_type_issues = len(type_issue_columns)

    missing_col.metric("Missing Values", analysis.get_missing_value_counts(dataset).sum())
    duplicates_col.metric("Duplicate Rows", n_duplicated_rows)
    typeis_col.metric("Type Issues", total_type_issues)

    profile_tab, missing_tab, duplicates_tab, types_tab = st.tabs([
        "Column Profile",
        "Missing Values",
        "Duplicates",
        "Type Issues",
    ])

    with profile_tab:
        st.dataframe(column_profile)

    with duplicates_tab:
        if n_duplicated_rows > 0:
            st.dataframe(analysis.get_duplicate_rows(dataset))
        else:
            st.success("No duplicates found.")

    with missing_tab:
        if not rows_with_missing_values.empty:
            st.dataframe(rows_with_missing_values)
        else:
            st.success("No missing values found.")
    
    with types_tab:
        if mixed_type_columns or suspicious_numeric_columns:
            st.write(
                "Mixed stored types:",
                ", ".join(mixed_type_columns)
            )
            st.write(
                "Numeric-looking columns containing invalid values:",
                ", ".join(suspicious_numeric_columns)
            )
        else:
            st.success("No type consistency issues found.")
        