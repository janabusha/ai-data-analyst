from pathlib import Path

import pandas as pd
import streamlit as st

import analysis
from views import ask_your_data
from views import data_quality
from views import exploration
from views import overview


# Configure the page before displaying any Streamlit elements.
st.set_page_config(
    page_title="Intelligent Data Analysis Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def load_css() -> None:
    """Load the application styles."""

    css_path = Path(__file__).parent / "styles.css"
    css = css_path.read_text(encoding="utf-8")

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )


# Apply the application styling.
load_css()


# Create the header layout.
brand_column, upload_column = st.columns(
    [1, 2],
    gap = "large",
    vertical_alignment="center",
)


# Display the temporary application name and logo.
with brand_column:
    brand_html = (
        '<div class="app-brand">'
        '<div class="app-logo">✦</div>'
        '<div class="app-brand-content">'
        '<div class="app-name">'
        "Intelligent Data Analysis Assistant"
        "</div>"
        '<div class="app-description">'
        "Explore your data with Python-powered analysis"
        "</div>"
        "</div>"
        "</div>"
    )

    st.markdown(
        brand_html,
        unsafe_allow_html=True,
    )


# Display the file uploader in the header.
with upload_column:
    uploaded_file = st.file_uploader(
        "Upload dataset",
        type=["csv", "xlsx"],
        label_visibility="collapsed",
    )


# Show an introduction before a file is uploaded.
if uploaded_file is None:
    empty_state_html = (
        '<div class="upload-empty-state">'
        "<h2>Upload a dataset to begin</h2>"
        "<p>"
        "Choose a CSV or Excel file above to generate an overview, "
        "check data quality, explore patterns, and ask questions "
        "about your data."
        "</p>"
        "</div>"
    )

    st.markdown(
        empty_state_html,
        unsafe_allow_html=True,
    )

    # Do not create the tabs until a dataset is available.
    st.stop()


# Load and validate the uploaded dataset.
try:
    dataset = analysis.load_dataset(uploaded_file)

except FileNotFoundError as error:
    st.error(str(error))
    st.stop()

except pd.errors.EmptyDataError:
    st.error("The uploaded file is empty.")
    st.stop()

except pd.errors.ParserError:
    st.error("The uploaded file could not be parsed.")
    st.stop()

except ValueError as error:
    st.error(str(error))
    st.stop()

except Exception as error:
    st.error(f"Could not load the dataset: {error}")
    st.stop()


# Create the navigation only after the dataset loads successfully.
overview_tab, quality_tab, exploration_tab, ask_tab = st.tabs(
    [
        "Overview",
        "Data Quality",
        "Exploration",
        "Ask Your Data",
    ]
)


# Render the selected application section.
with overview_tab:
    overview.render_overview(dataset)

with quality_tab:
    data_quality.render_data_quality(dataset)

with exploration_tab:
    exploration.render_exploration(dataset)

with ask_tab:
    ask_your_data.render_ask_your_data(dataset)