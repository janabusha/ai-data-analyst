import pandas as pd
import streamlit as st
import altair as alt

import analysis

def render_exploration(dataset: pd.DataFrame) -> None:
    st.subheader("Exploration")
    st.write("Explore distributions, patterns, and relationships in the dataset.")

    numeric_tab, categorical_tab, relationships_tab = st.tabs([
        "Numeric",
        "Categorical",
        "Relationships",
    ])

    with numeric_tab:
        numeric_columns = analysis.get_numeric_columns(dataset)

        if numeric_columns.empty:
            st.info("This dataset does not contain any numeric columns.")
        else:
            selected = st.selectbox(
                "Select Numeric Column",
                numeric_columns,
            )
        
        visual_col, statistic_col = st.columns([2, 1], border=True)
        with visual_col:
                st.subheader(f'{selected} distribution')
                chart_data = (
                    dataset[[selected]]
                    .dropna()
                    .rename(columns={selected: "value"}))
                histogram = alt.Chart(chart_data).mark_bar().encode(
                        x=alt.X(
                    "value:Q", # value is quantitative—numeric data.
                    bin=True, # group nearby values into ranges.
                    title=selected,
                    ),
                    y=alt.Y(
                            "count():Q", # count how many rows belong to each range.
                            title="Number of Rows",
                            ),
                            )
                st.altair_chart(histogram, width="stretch")

        with statistic_col:
            st.subheader("Statistics")
            row_1_col_1, row_1_col_2 = st.columns(2)
            row_2_col_1, row_2_col_2 = st.columns(2)
            row_3_col_1, row_3_col_2 = st.columns(2)

            row_1_col_1.metric("Missing Values", dataset[selected].isna().sum())
            row_1_col_2.metric("Mean", dataset[selected].mean().round(1))
            row_2_col_1.metric("Median", dataset[selected].median().round(1))
            row_2_col_2.metric("Standard Deviation", dataset[selected].std().round(1))
            row_3_col_1.metric("Minimum", dataset[selected].min())
            row_3_col_2.metric("Maximum", dataset[selected].max())
    

    with categorical_tab:
        cat_columns = analysis.get_string_columns(dataset)

        if cat_columns.empty:
            st.info("This dataset does not contain any categorical columns.")
        else:
            selected = st.selectbox(
                "Select Categorical Column",
                cat_columns,
            )
        visual_col, statistic_col = st.columns([2, 1], border=True)
        with visual_col:
            st.subheader(f'{selected} distribution')
            value_proportions = analysis.get_value_counts(
                    dataset,
                    selected,
                    normalize=True,
                    dropna=True,
                    )
            top_values = value_proportions.head(10)

            for category, proportion in top_values.items():
                label_col, bar_col, percentage_col = st.columns(
                    [2, 6, 1],
                    vertical_alignment="center",
                )

                label_col.write(str(category))
                bar_col.progress(float(proportion))
                percentage_col.write(f"**{proportion:.1%}**")

            st.caption(
                f"Showing the top {len(top_values)} "
                f"of {len(value_proportions)} categories."
            )
            
        with statistic_col:
            st.subheader("Statistics")
            row_1_col_1, row_1_col_2 = st.columns(2)
            row_2_col_1, row_2_col_2 = st.columns(2)

            top_share = analysis.get_top_value_share(dataset[selected])

            if top_share is None:
                top_share_text = "N/A"
            else:
                top_share_text = f"{top_share:.1%}"

            row_1_col_1.metric("Missing Values", dataset[selected].isna().sum())
            row_1_col_2.metric("Unique Values", dataset[selected].nunique(dropna=False))
            row_2_col_1.metric("Most common", dataset[selected].value_counts(dropna=False).idxmax())
            row_2_col_2.metric("Topshare", top_share_text)

    with relationships_tab:
        correlation_matrix = analysis.get_correlation_matrix(dataset)
        
        if correlation_matrix.shape[1] < 2:
            st.info(
            "At least two numeric columns are required "
            "to calculate relationships."
            )
        else:
            correlation_data = (
                correlation_matrix
                .rename_axis("variable_1")
                .reset_index()
                .melt(
                    id_vars="variable_1",
                    var_name="variable_2",
                    value_name="correlation",
                    )
                )
            column_order = correlation_matrix.columns.tolist()

            chart_size = min(
                max(len(column_order) * 100, 280),
                700,
            )

            base_chart = alt.Chart(correlation_data).encode(
                x=alt.X(
                    "variable_2:N",
                    title=None,
                    sort=column_order,
                    axis=alt.Axis(labelAngle=0),
                ),
                y=alt.Y(
                    "variable_1:N",
                    title=None,
                    sort=column_order,
                ),
                tooltip=[
                    alt.Tooltip("variable_1:N", title="Variable 1"),
                    alt.Tooltip("variable_2:N", title="Variable 2"),
                    alt.Tooltip(
                        "correlation:Q",
                        title="Correlation",
                        format=".2f",
                    ),
                ],
            )

            colored_cells = base_chart.mark_rect(
                cornerRadius=5,
                stroke="#0E1117",
                strokeWidth=4,
            ).encode(
                color=alt.Color(
                    "correlation:Q",
                    scale=alt.Scale(
                        domain=[-1, 0, 1],
                        range=["#806544", "#303A59", "#7183C7"],
                    ),
                    legend=None,
                )
            )

            cell_values = base_chart.mark_text(
                color="white",
                fontSize=16,
            ).encode(
                text=alt.Text(
                    "correlation:Q",
                    format=".2f",
                )
            )

            heatmap = (
                (colored_cells + cell_values)
                .properties(
                    width=chart_size,
                    height=chart_size,
                )
                .configure_view(strokeWidth=0)
            )

            with st.container(border=True):
                title_column, range_column = st.columns(
                    [4, 1],
                    vertical_alignment="center",
                )

                title_column.subheader("Correlation matrix")
                range_column.markdown("−1 to +1")

                st.altair_chart(
                    heatmap,
                    use_container_width=False,
                )