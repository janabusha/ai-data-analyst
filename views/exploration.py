import pandas as pd
import streamlit as st
import altair as alt

import analysis
from ui.components import render_subheader, create_at_a_glance_card, create_relationship_list

from ui.icons import (
    EXPLORE_ICON,
    CALCULATE_ICON,
    MATRIX_ICON,
    RELATIONSHIP_ICON,
    ARROW_ICON
)

def render_exploration(dataset: pd.DataFrame) -> None:
    render_subheader("Exploration", EXPLORE_ICON)
    st.caption("Explore distributions, patterns, and relationships in the dataset.")

    numeric_tab, categorical_tab, relationships_tab = st.tabs([
        "Numeric",
        "Categorical",
        "Relationships",
    ])
    
    with numeric_tab:
        numeric_columns = [
            column
            for column in analysis.get_numeric_columns(dataset)
            if dataset[column].notna().any()
        ]

        if not numeric_columns:
            st.info("This dataset does not contain any numeric columns.")

        else:
            with st.container(key="numeric-selector"):
                selected_numeric = st.selectbox(
                    "Choose a numeric column",
                    numeric_columns,
                    key="numeric_column_selector",
                )
            visual_col, statistic_col = st.columns(
                [2, 1],
                border=True,
            )

            with visual_col:
                chart_data = (
                    dataset[[selected_numeric]]
                    .dropna()
                    .rename(columns={selected_numeric: "value"})
                )

                histogram = (
                    alt.Chart(chart_data)
                    .mark_bar(
                        color="#18a999",
                        cornerRadiusTopLeft=4,
                        cornerRadiusTopRight=4,
                    )
                    .encode(
                        x=alt.X(
                            "value:Q",
                            bin=alt.Bin(maxbins=20),
                            title=selected_numeric,
                            axis=alt.Axis(
                                labelColor="#667085",
                                titleColor="#667085",
                                grid=False,
                            ),
                        ),
                        y=alt.Y(
                            "count():Q",
                            title="Number of rows",
                            axis=alt.Axis(
                                labelColor="#667085",
                                titleColor="#667085",
                                grid=True,
                                gridColor="#e8eeec",
                                gridOpacity=1,
                            ),
                        ),
                        tooltip=[
                            alt.Tooltip("value:Q", bin=True, title="Range"),
                            alt.Tooltip("count():Q", title="Rows", format=","),
                        ],
                    )
                    .properties(height=390)
                    .configure_view(stroke=None)
                    .configure_axis(
                        domain=False,
                        tickColor="#d8e1df",
                        labelFontSize=12,
                        titleFontSize=13,
                        titleFontWeight=500,
                        labelPadding=8,
                        titlePadding=12,
                    )
                )

                st.altair_chart(histogram, width="stretch")

            with statistic_col:
                render_subheader(
                    "At a glance",
                    CALCULATE_ICON,
                )

                selected_data = dataset[selected_numeric]

                missing_count = selected_data.isna().sum()
                mean = selected_data.mean()
                median = selected_data.median()
                std = selected_data.std()
                minimum = selected_data.min()
                maximum = selected_data.max()

                numeric_statistics = [
                    ("Missing", f"{missing_count:,}"),
                    ("Mean", f"{mean:,.2f}"),
                    ("Median", f"{median:,.2f}"),
                    ("Std. deviation", f"{std:,.2f}"),
                    ("Minimum", f"{minimum:,.2f}"),
                    ("Maximum", f"{maximum:,.2f}"),
                ]

                st.markdown(
                    create_at_a_glance_card(numeric_statistics),
                    unsafe_allow_html=True,
                ) 
    with categorical_tab:
        cat_columns = analysis.get_string_columns(dataset)

        if cat_columns.empty:
            st.info("This dataset does not contain any categorical columns.")
        else:
            with st.container(key="categorical-selector"):
                selected_category = st.selectbox(
                    "Choose a categorical column",
                    cat_columns,
                    key="categorical_column_selector",
                )
        visual_col, statistic_col = st.columns([2, 1], border=True)
    with visual_col:
        st.subheader(f"{selected_category} distribution")

        category_counts = (
            dataset[selected_category]
            .dropna()
            .astype(str)
            .value_counts()
        )

        valid_count = int(category_counts.sum())
        category_count = len(category_counts)

        if valid_count == 0:
            st.info("This column does not contain any values.")

        else:
            top_categories = (
                category_counts
                .head(10)
                .rename_axis("category")
                .reset_index(name="count")
            )

            top_categories["percentage"] = (
                top_categories["count"] / valid_count * 100
            )

            top_categories["full_width"] = 100

            top_categories["percentage_label"] = (
                top_categories["percentage"]
                .map(lambda value: f"{value:.1f}%")
            )

            category_order = top_categories["category"].tolist()

            base = alt.Chart(top_categories).encode(
                y=alt.Y(
                    "category:N",
                    sort=category_order,
                    title=None,
                    axis=alt.Axis(
                        domain=False,
                        ticks=False,
                        labelColor="#20242c",
                        labelFontSize=13,
                        labelLimit=155,

                        # Keep every label left-aligned.
                        labelAlign="left",

                        # Reserve space between labels and bars.
                        labelPadding=170,
                    ),
                )
            )

            background_bars = base.mark_bar(
                color="#edf3f2",
                cornerRadius=6,
                size=10,
            ).encode(
                x=alt.X(
                    "full_width:Q",
                    scale=alt.Scale(domain=[0, 100]),
                    axis=None,
                )
            )

            value_bars = base.mark_bar(
                color="#18a999",
                cornerRadius=6,
                size=10,
            ).encode(
                x=alt.X(
                    "percentage:Q",
                    scale=alt.Scale(domain=[0, 100]),
                    axis=None,
                ),
                tooltip=[
                    alt.Tooltip(
                        "category:N",
                        title="Category",
                    ),
                    alt.Tooltip(
                        "count:Q",
                        title="Rows",
                        format=",",
                    ),
                    alt.Tooltip(
                        "percentage:Q",
                        title="Share",
                        format=".1f",
                    ),
                ],
            )

            percentage_labels = base.mark_text(
                align="right",
                baseline="middle",
                dx=-5,
                color="#20242c",
                fontSize=12,
                fontWeight=600,
            ).encode(
                x=alt.X(
                    "full_width:Q",
                    scale=alt.Scale(domain=[0, 100]),
                ),
                text=alt.Text("percentage_label:N"),
            )

            category_chart = (
                background_bars
                + value_bars
                + percentage_labels
            ).properties(
                height=max(300, len(top_categories) * 42)
            ).configure_view(
                stroke=None
            )

            st.altair_chart(
                category_chart,
                width="stretch",
            )

            if category_count > 10:
                st.caption(
                    f"Showing the top 10 of "
                    f"{category_count:,} categories."
                )
            
        with statistic_col:
            render_subheader("At a glance", CALCULATE_ICON)
            missing_count = dataset[selected_category].isna().sum()
            unique_value_count = dataset[selected_category].nunique(dropna=False)
            most_common = dataset[selected_category].value_counts(dropna=False).idxmax()
            top_share = analysis.get_top_value_share(dataset[selected_category])

            if top_share is None:
                top_share_text = "N/A"
            else:
                top_share_text = f"{top_share:.1%}"

            categorical_statistics = [
                ("Missing", f"{missing_count:,}"),
                ("Unique Values", f"{unique_value_count}"),
                ("Most common", f"{most_common}"),
                ("Topshare", top_share_text),
                ]
            st.markdown(
                create_at_a_glance_card(categorical_statistics),
                unsafe_allow_html=True,
                ) 
    with relationships_tab:
        identifier_columns = analysis.get_likely_identifier_columns(
            dataset
        )

        numeric_columns = analysis.get_numeric_columns(dataset)

        numeric_identifier_columns = [
            identifier
            for identifier in identifier_columns
            if identifier in numeric_columns
        ]

        matrix_column, insights_column = st.columns([2, 1])

        with insights_column:
            with st.container(border=True):
                render_subheader(
                    "Analysis controls",
                    ARROW_ICON,
                )

                if numeric_identifier_columns:
                    included_identifiers = st.multiselect(
                        "Include identifier columns",
                        options=numeric_identifier_columns,
                        help=(
                            "Identifiers are excluded by default because "
                            "their numeric values may create misleading "
                            "correlations."
                        ),
                    )
                else:
                    included_identifiers = []

                    st.caption(
                        "No likely numeric identifier columns detected."
                    )

                if included_identifiers:
                    st.warning(
                        "Interpret correlations involving identifier "
                        "columns carefully."
                    )

                correlation_matrix = analysis.get_correlation_matrix(
                    dataset,
                    included_identifiers=included_identifiers,
                )

                strongest_relationships = (
                    analysis.get_strongest_relationships(
                        correlation_matrix
                    )
                )

                excluded_identifiers = [
                    identifier
                    for identifier in numeric_identifier_columns
                    if identifier not in included_identifiers
                ]

                st.divider()

                render_subheader(
                    "Strongest relationships",
                    RELATIONSHIP_ICON,
                )

                st.markdown(
                    create_relationship_list(
                        strongest_relationships,
                        identifiers_excluded=bool(
                            excluded_identifiers
                        ),
                    ),
                    unsafe_allow_html=True,
                )
            with matrix_column:
                render_subheader("Correlation matrix", MATRIX_ICON)

                column_order = correlation_matrix.columns.tolist()

                heatmap_data = (
                    correlation_matrix
                    .rename_axis("row")
                    .reset_index()
                    .melt(
                        id_vars="row",
                        var_name="column",
                        value_name="correlation",
                    )
                )

                base = alt.Chart(heatmap_data).encode(
                    x=alt.X(
                        "column:N",
                        sort=column_order,
                        title=None,
                        axis=alt.Axis(
                            domain=False,
                            ticks=False,
                            labelAngle=0,
                            labelColor="#667085",
                            labelFontSize=11,
                            labelPadding=10,
                            labelLimit=100,
                        ),
                    ),
                    y=alt.Y(
                        "row:N",
                        sort=column_order,
                        title=None,
                        axis=alt.Axis(
                            domain=False,
                            ticks=False,
                            labelColor="#667085",
                            labelFontSize=11,
                            labelPadding=10,
                            labelLimit=160,
                        ),
                    ),
                )

                cells = base.mark_rect(
                    stroke="#ffffff",
                    strokeWidth=1.5,
                ).encode(
                    color=alt.Color(
                        "correlation:Q",
                        scale=alt.Scale(
                            domain=[-1, 0, 1],
                            range=[
                                "#ff8f80",
                                "#f3f0e8",
                                "#0c9f8e",
                            ],
                        ),
                        legend=alt.Legend(
                            title=None,
                            orient="right",
                            values=[-1, 0, 1],
                            labelExpr=(
                                "datum.value === 1 ? 'Positive' : "
                                "datum.value === 0 ? '0' : 'Negative'"
                            ),
                            labelColor="#667085",
                            labelFontSize=12,
                            labelPadding=8,
                            gradientLength=150,
                            gradientThickness=18,
                            offset=20,
                        ),
                    ),
                    tooltip=[
                        alt.Tooltip("row:N", title="Column 1"),
                        alt.Tooltip("column:N", title="Column 2"),
                        alt.Tooltip(
                            "correlation:Q",
                            title="Correlation",
                            format=".2f",
                        ),
                    ],
                )

                values = base.mark_text(
                    fontSize=12,
                    fontWeight=600,
                    baseline="middle",
                ).encode(
                    text=alt.Text(
                        "correlation:Q",
                        format=".2f",
                    ),
                    color=alt.condition(
                        "abs(datum.correlation) >= 0.65",
                        alt.value("#ffffff"),
                        alt.value("#20242c"),
                    ),
                )

                correlation_chart = (
                    cells + values
                ).properties(
                    width=alt.Step(70),
                    height=alt.Step(52),
                ).configure_view(
                    stroke=None,
                )

                st.altair_chart(
                    correlation_chart,
                    width="stretch",
                )