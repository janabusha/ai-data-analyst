import pandas as pd
import streamlit as st

import analysis
from ui.components import render_subheader
from model_client import create_model_client

from ui.icons import (
    CHAT_ICON,
)

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
    """Render the dataset chat interface."""

    available_tools = create_advisor_tools(dataset)
    client, model_name = create_model_client()

    if "advisor_messages" not in st.session_state:
        st.session_state.advisor_messages = []

    if "advisor_pending_question" not in st.session_state:
        st.session_state.advisor_pending_question = None

    def queue_question(question: str) -> None:
        """Add a question to history and queue it for analysis."""
        st.session_state.advisor_messages.append({
            "role": "user",
            "content": question,
        })
        st.session_state.advisor_pending_question = question

    def get_assistant_answer(user_question: str) -> str:
        """Run the advisor model and return its answer."""
        messages_for_model = [
            {
                "role": "system",
                "content": (
                    "You are a data-analysis assistant. "
                    "A dataset is available only through the provided tools. "
                    "Answer only with facts directly supported by tool results. "
                    "Use the recent conversation history to understand follow-up "
                    "questions and references such as 'that', 'it', or 'what else'. "
                    "Keep answers concise and use no more than three sentences. "
                    "Do not offer to perform unavailable actions. "
                    "Do not offer to modify, clean, or delete data. "
                    "If the user's question remains ambiguous after considering "
                    "the conversation history, ask for clarification. "
                    "If a question requires a column name and none is provided, "
                    "ask the user to specify a column. "
                    "Never choose a column yourself. "
                    "Treat duplicates and other anomalies as findings that require "
                    "review, not as confirmed errors."
                ),
            },
            *st.session_state.advisor_messages[-10:],
        ]

        try:
            first_response = client.chat(
                model=model_name,
                messages=messages_for_model,
                tools=list(available_tools.values()),
                think=False,
                keep_alive="1m",
            )

            messages_for_model.append(first_response.message)

            if first_response.message.tool_calls:
                for tool_call in first_response.message.tool_calls:
                    tool_name = tool_call.function.name
                    selected_tool = available_tools.get(tool_name)

                    if selected_tool is None:
                        tool_result = f"Unknown tool: {tool_name}"
                    else:
                        tool_result = selected_tool()

                    messages_for_model.append({
                        "role": "tool",
                        "tool_name": tool_name,
                        "content": str(tool_result),
                    })

                final_response = client.chat(
                    model=model_name,
                    messages=messages_for_model,
                    think=False,
                )

                return final_response.message.content

            # Allow Ollama to answer supported general questions directly.
            direct_answer = first_response.message.content.strip()

            if direct_answer:
                return direct_answer

            return (
                "I cannot answer that question with the available "
                "analysis tools yet."
            )

        except Exception:
            return (
                "I could not complete the analysis. "
                "Please try again with a more specific question."
            )

    # Page heading.
    heading_column, action_column = st.columns([5, 1])

    with heading_column:
        render_subheader("Ask your Data", CHAT_ICON )
        st.caption("Ask questions about your dataset and receive answers grounded in Python computations.")
    with action_column:
        if st.button(
            "Clear chat",
            key="clear-advisor-chat",
            use_container_width=True,
            disabled=not st.session_state.advisor_messages,
        ):
            st.session_state.advisor_messages = []
            st.session_state.advisor_pending_question = None
            st.rerun()

    # Suggested questions.
    st.markdown(
        '<div class="advisor-suggestion-label">Try asking</div>',
        unsafe_allow_html=True,
    )

    suggestions = [
        (
            "Summarize dataset",
            "Summarize the key findings in this dataset.",
        ),
        (
            "Check missing values",
            "Which columns contain missing values?",
        ),
        (
            "Find relationships",
            "What are the strongest relationships in this dataset?",
        ),
        (
            "Check duplicates",
            "Does this dataset contain duplicate rows?",
        ),
    ]

    with st.container(key="advisor-suggestions"):
        suggestion_columns = st.columns(4)

        for index, (label, question) in enumerate(suggestions):
            with suggestion_columns[index]:
                if st.button(
                    label,
                    key=f"advisor-suggestion-{index}",
                    use_container_width=True,
                ):
                    queue_question(question)
                    st.rerun()

    # Conversation workspace.
    with st.container(border=True, key="advisor-chat-shell"):
        if not st.session_state.advisor_messages:
            st.markdown(
                """
                <div class="advisor-empty-state">
                    <div class="advisor-empty-icon">✦</div>
                    <h3>What would you like to learn?</h3>
                    <p>
                        Choose one of the suggestions above or ask your own
                        question about the uploaded dataset.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Display complete conversation history above the input.
        for message in st.session_state.advisor_messages:
            avatar = (
                ":material/person:"
                if message["role"] == "user"
                else ":material/auto_awesome:"
            )

            with st.chat_message(
                message["role"],
                avatar=avatar,
            ):
                st.markdown(message["content"])

        # Process a queued question after its user message has been rendered.
        pending_question = st.session_state.advisor_pending_question

        if pending_question:
            with st.chat_message(
                "assistant",
                avatar=":material/auto_awesome:",
            ):
                with st.spinner("Analyzing your dataset..."):
                    assistant_answer = get_assistant_answer(
                        pending_question
                    )

            st.session_state.advisor_messages.append({
                "role": "assistant",
                "content": assistant_answer,
            })

            st.session_state.advisor_pending_question = None
            st.rerun()

        user_question = st.chat_input(
            "Ask a question about your dataset",
            key="advisor-chat-input",
        )

        if user_question:
            queue_question(user_question)
            st.rerun()