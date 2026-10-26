import streamlit as st
import pandas as pd

import analysis

def render_dataset_summary(dataset: pd.DataFrame) -> None:
	n_rows = dataset.shape[0]
	n_columns = dataset.shape[1]
	n_missing_values = analysis.get_missing_value_counts(dataset).sum()
	n_duplicated_rows = analysis.get_duplicate_row_count(dataset).sum()
	type_status = "Review" if analysis.get_mixed_type_columns(dataset) else "OK"

	column_1, column_2, column_3, column_4, column_5 = st.columns(5)
	column_1.metric("Number Of Rows", n_rows)
	column_2.metric("Number Of Columns", n_columns)
	column_3.metric("Number Of Missing Values", n_missing_values)
	column_4.metric("Number Of Duplicates", n_duplicated_rows)
	column_5.metric("Type Consistency", type_status)

def render_overview(dataset: pd.DataFrame) -> None:
	render_dataset_summary(dataset)
	st.dataframe(dataset)

def render_data_quality(dataset: pd.DataFrame) -> None:
	render_dataset_summary(dataset)
	n_duplicated_rows = analysis.get_duplicate_row_count(dataset).sum()
	
	column_profile = analysis.get_column_profile(dataset)
	with st.expander("Column Profile", expanded=True):
		st.dataframe(column_profile)

	if n_duplicated_rows > 0:
		with st.expander("Duplicated Rows"):
			st.dataframe(analysis.get_duplicate_rows(dataset))

	rows_with_missing_values = analysis.get_rows_with_missing_values(dataset)
	if not rows_with_missing_values.empty:
		with st.expander("Rows With Missing Values"):
			st.dataframe(rows_with_missing_values)

	mixed_type_columns = analysis.get_mixed_type_columns(dataset)
	if	mixed_type_columns:
		    with st.expander("Type Consistency Details"):
    		   		 st.write(
						"Columns to review:",
						", ".join(mixed_type_columns)
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
			render_overview(dataset)

		with quality_tab:
			render_data_quality(dataset)

		with exploration_tab:
			st.info("Exploration features are coming soon.")

		with advisor_tab:
			st.info("ML Model Advisor is coming soon.")

except FileNotFoundError as error:
	st.error(str(error))
except ValueError as error:
	st.error(str(error))


	


