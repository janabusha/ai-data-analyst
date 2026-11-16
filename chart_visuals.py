import altair as alt
import pandas as pd
import streamlit as st

def display_line_chart(
    dataset: pd.DataFrame,
    chart_choice: dict,
	) -> None:
    x_column = chart_choice["x"]
    y_column = chart_choice["y"]
    aggregation = chart_choice["aggregation"]

    chart_data = (
        dataset
        .dropna(subset=[x_column, y_column])
        .groupby(x_column)[y_column]
        .agg(aggregation)
        .reset_index()
        .sort_values(x_column)
    )

    st.line_chart(
        chart_data,
        x=x_column,
        y=y_column,
    )

def display_bar_chart(
    dataset: pd.DataFrame,
    chart_choice: dict,
    ) -> None:
    # The AI may return either "x" or "x_column".
    x_column = (
        chart_choice.get("x_column")
        or chart_choice.get("x")
    )

    # The y column can be None for count-based charts.
    y_column = (
        chart_choice.get("y_column")
        or chart_choice.get("y")
    )

    # Use "count" when the AI does not provide an aggregation.
    aggregation = (
        chart_choice.get("aggregation")
        or "count"
    ).strip().lower()

    # Provide a fallback title if the AI does not return one.
    title = chart_choice.get(
        "title",
        "Quick overview",
    )

    # We cannot create the chart without a valid x column.
    if x_column not in dataset.columns:
        st.warning(
            f"Column '{x_column}' was not found."
        )
        return

    # A numeric y column is required for sum, mean, median, etc.
    y_is_numeric = (
        y_column in dataset.columns
        and pd.api.types.is_numeric_dtype(
            dataset[y_column]
        )
    )

    # Count categories when:
    # - count was requested,
    # - y is missing,
    # - or y contains non-numeric values.
    use_count = (
        aggregation == "count"
        or not y_is_numeric
    )

    if use_count:
        # Remove rows where the category is missing.
        chart_data = dataset.dropna(
            subset=[x_column]
        )

        # Count how many rows belong to each category.
        chart_data = (
            chart_data
            .groupby(x_column)
            .size()
            .reset_index(name="count")
        )

        # Display categories from most to least common.
        chart_data = chart_data.sort_values(
            "count",
            ascending=False,
        )

        # The generated count becomes the chart's y value.
        y_column = "count"
        aggregation = "count"

    else:
        # Remove rows missing either required chart value.
        chart_data = dataset.dropna(
            subset=[x_column, y_column]
        )

        # Calculate the requested value for each category.
        chart_data = (
            chart_data
            .groupby(
                x_column,
                as_index=False,
            )[y_column]
            .agg(aggregation)
        )

        # Display the largest aggregated values first.
        chart_data = chart_data.sort_values(
            y_column,
            ascending=False,
        )

    # Avoid displaying a blank chart.
    if chart_data.empty:
        st.info(
            "There is not enough data to display this chart."
        )
        return

    # Create the bar chart using the prepared data.
    chart = (
        alt.Chart(chart_data)
        .mark_bar(
            color="#18A999",
            cornerRadiusTopLeft=4,
            cornerRadiusTopRight=4,
        )
        .encode(
            # Treat x values as categories.
            x=alt.X(
                f"{x_column}:N",
                sort="-y",
                title=x_column,
            ),

            # Treat the calculated y values as numeric.
            y=alt.Y(
                f"{y_column}:Q",
                title=(
                    "Number of rows"
                    if aggregation == "count"
                    else y_column
                ),
                scale=alt.Scale(zero=True),
            ),

            # Show both values when hovering over a bar.
            tooltip=[
                alt.Tooltip(
                    f"{x_column}:N",
                    title=x_column,
                ),
                alt.Tooltip(
                    f"{y_column}:Q",
                    title=y_column,
                ),
            ],
        )
        .properties(title=title)
    )

    # Render the chart across the available container width.
    st.altair_chart(
        chart,
        width="stretch",
    )

def display_scatter_chart(
    dataset: pd.DataFrame,
    chart_choice: dict,
	) -> None:
    x_column = chart_choice["x"]
    y_column = chart_choice["y"]

    chart_data = dataset.dropna(
        subset=[x_column, y_column]
    )

    st.scatter_chart(
        chart_data,
        x=x_column,
        y=y_column,
    )

def display_chart(
    dataset: pd.DataFrame,
    chart_choice: dict,
) -> None:
    chart_type = chart_choice["chart_type"]

    if chart_type == "line":
        display_line_chart(dataset, chart_choice)

    elif chart_type == "bar":
        display_bar_chart(dataset, chart_choice)

    elif chart_type == "scatter":
        display_scatter_chart(dataset, chart_choice)

    else:
        st.info("The recommended chart type is not supported.")