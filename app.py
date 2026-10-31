import streamlit as st
import pandas as pd

import analysis
from views import overview
from views import data_quality
from views import exploration
from views import ml_advisor

st.set_page_config(
    page_title="Intelligent Data Analysis Assistant",
    page_icon="📊",
    layout="wide",
)
st.title("Intelligent Data Analysis Assistant")
st.write("Upload a CSV or Excel file to inspect and analyze your data.")

with st.sidebar:
	st.header("Dataset")
	uploaded_file = st.file_uploader(
		"Upload a CSV or Excel file",
		 type=["csv", "xlsx"],
)
overview_tab, quality_tab, exploration_tab, advisor_tab = st.tabs([
	"Overview",
	"Data Quality",
	"Exploration",
	"ML Advisor",
])

try:
	if uploaded_file is not None:
		dataset = analysis.load_dataset(uploaded_file)
		st.write("Uploaded file:", uploaded_file.name)

		with overview_tab:
			overview.render_overview(dataset)

		with quality_tab:
			data_quality.render_data_quality(dataset)

		with exploration_tab:
			exploration.render_exploration(dataset)

		with advisor_tab:
			st.info("ML Model Advisor is coming soon.")

except FileNotFoundError as error:
	st.error(str(error))
except ValueError as error:
	st.error(str(error))


	


