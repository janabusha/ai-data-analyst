import streamlit as st
import pandas as pd
import analysis

def render_overview(dataset: pd.DataFrame) -> None:
	display_dataset = dataset.copy()
	for column_name in analysis.get_mixed_type_columns(dataset):
		display_dataset[column_name] = display_dataset[column_name].astype("string")
	
	n_rows = dataset.shape[0]
	n_columns = dataset.shape[1]
	n_missing_values = analysis.get_missing_value_counts(dataset).sum()
	n_duplicated_rows = analysis.get_duplicate_row_count(dataset).sum()
	mixed_type_columns = analysis.get_mixed_type_columns(dataset)
	suspicious_numeric_columns = analysis.get_suspicious_numeric_columns(dataset)
	n_numeric_columns = len(analysis.get_numeric_columns(dataset))
	n_string_columns = len(analysis.get_string_columns(dataset))
	n_other_columns = n_columns - n_numeric_columns - n_string_columns
	
	preview_column, information_column = st.columns([2, 1])
	if mixed_type_columns or suspicious_numeric_columns:
		type_status = "Review"
	else:
		type_status = "OK"
	
	with preview_column:
		st.subheader("Data Preview")
		st.dataframe(display_dataset)
	with information_column:
		st.subheader("Data Health")
		st.metric("Missing Values", n_missing_values)
		st.metric("Duplicate Rows", n_duplicated_rows)
		st.metric("Type Consistency", type_status)
		
		st.subheader("Data Structure")
		st.metric("Rows", n_rows)
		st.metric("Columns", n_columns)
		st.metric("Numeric Columns", n_numeric_columns)
		st.metric("Text Columns", n_string_columns)
		st.metric("Other Columns", n_other_columns)
