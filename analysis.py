from pathlib import Path
import pandas as pd

def load_dataset(file_path: str | Path) -> pd.DataFrame:
	dataset = pd.read_csv(file_path)
	return dataset

def get_duplicate_row_count(dataset: pd.DataFrame) -> int: # returns the count of duplicate rows in the dataset.
	return dataset.duplicated().sum()

def get_missing_value_counts(dataset: pd.DataFrame) -> pd.Series: # returns counts of missing values for each column in the dataset.
	return dataset.isna().sum()

def get_value_counts(dataset: pd.DataFrame, column_name: str) -> pd.Series: # returns counts including NaN values. 
	if column_name not in dataset.columns:
		raise ValueError(f"Column '{column_name}' does not exist in the dataset.")
	return dataset[column_name].value_counts(dropna=False)

def get_string_columns(dataset: pd.DataFrame) -> pd.Index: # returns the names of columns with string data types.
	return dataset.select_dtypes(include="str").columns

def get_unique_value_counts(dataset: pd.DataFrame) -> pd.Series:   # returns the count of unique values for each column in the dataset.
	return dataset.nunique(dropna=False)

def get_column_profile(dataset: pd.DataFrame) -> pd.DataFrame: 
	profile = pd.DataFrame({
		'Data Type':    dataset.dtypes,
		'Missing Values': get_missing_value_counts(dataset),
		'Unique Values': get_unique_value_counts(dataset),
		'Missing Percentage': get_missing_value_counts(dataset) / dataset.shape[0] * 100
	})
	return profile

def get_duplicate_rows(dataset: pd.DataFrame) -> pd.DataFrame:
	return dataset[dataset.duplicated(keep=False)]

def get_numeric_columns(dataset: pd.DataFrame) -> pd.Index:
	return dataset.select_dtypes(include="number").columns