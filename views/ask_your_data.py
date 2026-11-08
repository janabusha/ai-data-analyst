import pandas as pd
import streamlit as st

import analysis
from ollama import chat


MODEL_NAME = "qwen3.5:4b"


# Create tools that can use the uploaded dataset.
def create_advisor_tools(dataset: pd.DataFrame) -> dict:

    def get_missing_values() -> str:
        """Return the missing-value count for every dataset column."""

        missing_counts = analysis.get_missing_value_counts(dataset)

        if missing_counts.sum() == 0:
            return "No missing values were found in the dataset."

        return (
            "Missing-value counts for every column:\n"
            + missing_counts.to_string()
        )
    
    def get_duplicate_row_count() -> str:
        """Return the number of duplicated rows in the dataset."""
        duplicate_row_count = analysis.get_duplicate_row_count(dataset)

        if duplicate_row_count == 0:
            return "No duplicates found in dataset."

        return(
            f"The dataset contains {duplicate_row_count} "
             "duplicate rows."
        )
    
    def get_column_profile() -> str:
         """Return data type, missing-value, and unique-value details for each column."""
         return analysis.get_column_profile(dataset).to_string()
    
    def get_mixed_type_columns() -> str:
        """Return columns containing more than one stored Python type."""
        mixed_columns = analysis.get_mixed_type_columns(dataset)

        if not mixed_columns:
            return "No columns with mixed stored types were found."

        return (
            "Columns with mixed stored types: "
            + ", ".join(mixed_columns)
        )

    def get_likely_identifier_columns() -> str:
        """Return columns that can be likely un identifier."""
        id_columns = analysis.get_likely_identifier_columns(dataset)

        if not id_columns:
            return(
                "No likely identifier columns were found. "
                "The detection rule checks column names such as "
                "'id', names ending in '_id', and 'Unnamed' columns."
            )
        
        return (
            "Columns that could likely be identifiers: "
            + ", ".join(id_columns)
        )

    def get_correlation_matrix() -> str:
        """Return correlations between numeric columns."""
        correlations = analysis.get_correlation_matrix(dataset)

        if correlations.shape[1] < 2:
            return "At least two numeric columns are required."

        return (
            "Pearson correlation matrix, ranging from -1 to +1:\n"
            + correlations.round(3).to_string()
            + "\n\nInterpretation rules:"
            "\n- Ignore diagonal values of 1.0."
            "\n- Weakest correlation means closest to zero."
            "\n- Strongest correlation means the largest absolute value."
            "\n- Most negative correlation means the smallest signed value."
            "\nCorrelation does not prove causation."
            "\nThe heatmap is available in the Exploration tab."
        )
    def get_numeric_summary() -> str:
        """
        Return count, mean, standard deviation, minimum, quartiles,
        median, and maximum for every numeric column.
        """
        summary = analysis.get_numeric_summary(dataset)

        if summary.empty:
            return "No numeric columns were found."

        return (
            "Numeric summary statistics:\n"
            + summary.round(2).to_string()
        )
    def get_key_findings() -> str:
        """Return evidence used to identify the most valuable dataset findings."""

        findings = [
            f"Dataset size: {dataset.shape[0]} rows and "
            f"{dataset.shape[1]} columns.",
            get_missing_values(),
            get_duplicate_row_count(),
            get_mixed_type_columns(),
            get_likely_identifier_columns(),
            get_numeric_summary(),
            get_correlation_matrix(),
        ]
        return "\n\n".join(findings)        
    
    # Connect each tool name to its function.
    return {
        "get_missing_values": get_missing_values,
        "get_duplicate_row_count": get_duplicate_row_count,
        "get_column_profile": get_column_profile,
        "get_mixed_type_columns": get_mixed_type_columns,
        "get_likely_identifier_columns": get_likely_identifier_columns,
        "get_correlation_matrix": get_correlation_matrix,
        "get_numeric_summary": get_numeric_summary,
        "get_key_findings": get_key_findings,
    }


def render_ask_your_data(dataset: pd.DataFrame) -> None:
# Create tools for the current dataset.
    available_tools = create_advisor_tools(dataset)

    st.header("Ask Your Data")
    st.write(

        "Ask questions about the uploaded dataset. "
        "Answers will be grounded in Python computations."
    )

    st.caption(
        f"Dataset loaded: {dataset.shape[0]} rows "
        f"and {dataset.shape[1]} columns."
    )
    chat_column, insights_column = st.columns([2, 1])

    with insights_column:
        st.subheader("✨ Findings")

        st.caption(
            "AI-generated summary based on Python-computed results. "
            "Review the Data Quality and Exploration tabs for full details."
        )
        if "key_findings_text" not in st.session_state:
            evidence = available_tools["get_key_findings"]()
            prompt = f"""
            Using only the computed evidence below, write exactly 3 concise,
            non-overlapping findings for a narrow sidebar.

            Formatting:
            - Give each finding a specific bold heading that describes the insight.
            - Never use generic headings such as "Data Quality Issue",
            -"Numeric Pattern", or "Column Relationship".
            - Wrap every exact dataset column name in Markdown bold using
            double asterisks, for example: **Global_Sales**.
            - Use one or two short sentences per finding.
            - Keep each finding under 35 words.

            Selection:
            - Include a data-quality issue only when it affects interpretation.
            - Choose a genuinely useful numeric pattern, such as an unusual
            range, skew, concentration, or potential outlier. Do not report
            a mean by itself.
            - Choose a meaningful non-trivial relationship.
            - Avoid correlations between a total column and one of its
            component columns when another useful relationship exists.

            Accuracy:
            - Do not claim causation, prediction, dominance, business strategy,
            customer behaviour, or historical preference.
            - Do not infer information that is absent from the evidence.
            - Treat correlations involving totals and their component columns
            cautiously because the relationship may be mechanical.
            - If a finding is uncertain or uninformative, omit it.

            Computed evidence:
            {evidence}
            """

            with st.spinner("Finding what stands out..."):
                response = chat(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                            
                        }
                    ],
                    think=False,
                    keep_alive="1m",
                )

            st.session_state.key_findings_text = response.message.content

        st.markdown(st.session_state.key_findings_text)
    with chat_column:
    # Create conversation history.
        if "advisor_messages" not in st.session_state:
            st.session_state.advisor_messages = []

        if st.button("Clear conversation"):
            st.session_state.advisor_messages = []
            st.rerun()

        # Display previous messages.
        for message in st.session_state.advisor_messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        user_question = st.chat_input(
            "Ask a question about your dataset"
        )

        if user_question:
            user_message = {
                "role": "user",
                "content": user_question,
            }

            st.session_state.advisor_messages.append(user_message)

            with st.chat_message("user"):
                st.write(user_question)

            messages_for_model = [
                {
                    "role": "system",
                    "content": (
                        "You are a data-analysis assistant. "
                        "A dataset is available only through the provided tools. "
                        "Answer only with facts directly supported by tool results. "
                        "Keep answers concise and use no more than three sentences. "
                        "Do not offer to perform unavailable actions. "
                        "Do not offer to modify, clean, or delete data. "
                        "If the user's question is ambiguous, do not guess. "
                        "Ask them to provide a complete and specific question."
                        "If a question requires a column name and none is provided, "
                        "ask the user to specify a column. Never choose a column yourself. "
                        "Treat duplicates and other anomalies as findings that require "
                        "review, not as confirmed errors. "
                        "For data-quality findings, mention that details are available "
                        "in the Data Quality tab or Exploration tab."
                    ),
                },
                {
                "role": "user",
                "content": user_question,
                }
            ]

            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    try:
                        # First call: Ollama chooses whether to use a tool.
                        first_response = chat(
                            model=MODEL_NAME,
                            messages=messages_for_model,
                            tools=list(available_tools.values()),
                            think=False,
                            keep_alive="1m",
                        )

                        messages_for_model.append(
                            first_response.message
                        )

                        if first_response.message.tool_calls:
                            for tool_call in (
                                first_response.message.tool_calls
                            ):
                                tool_name = tool_call.function.name

                                # Find the selected tool.
                                selected_tool = available_tools.get(
                                    tool_name
                                )

                                if selected_tool is None:
                                    tool_result = (
                                        f"Unknown tool: {tool_name}"
                                    )
                                else:
                                    # Run the selected Python function.
                                    tool_result = selected_tool()

                                messages_for_model.append({
                                    "role": "tool",
                                    "tool_name": tool_name,
                                    "content": tool_result,
                                })

                            # Second call: Ollama explains the tool result.
                            final_response = chat(
                                model=MODEL_NAME,
                                messages=messages_for_model,
                                think=False,
                            )

                            assistant_answer = (
                                final_response.message.content
                            )
                        else:
                            assistant_answer = (
                                "I cannot answer that question with the available "
                                "analysis tools yet."
                            )
                    except Exception as error:
                        assistant_answer = (
                            "I could not complete the analysis. "
                            f"Details: {error}"
                        )

                st.write(assistant_answer)

            # Save the answer in conversation history.
            st.session_state.advisor_messages.append({
                "role": "assistant",
                "content": assistant_answer,
            })