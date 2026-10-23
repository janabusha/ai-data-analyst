import argparse
import pandas as pd
import analysis

def inspect_dataset(dataset: pd.DataFrame) -> None:
	print("Dataset Shape:", dataset.shape)
	print("\nDataset Dtypes:")
	print(dataset.dtypes)
	print("\nDataset Columns:")
	print(dataset.columns)
	print("\nMissing Values:")
	print(analysis.get_missing_value_counts(dataset))
	print("\nDuplicate Rows:", analysis.get_duplicate_row_count(dataset))
	print("\nString Columns:")
	print(analysis.get_string_columns(dataset))
	print("\nDataset Description:")
	print(dataset.describe())
	print("\nDataset Description (String Columns):")
	print(dataset.describe(include='str'))
	print("\nFirst Few Rows:")
	print(dataset.head())
	print("\nUnique Value Counts:")
	print(analysis.get_unique_value_counts(dataset))
	print("here:")
	print(dataset.select_dtypes(include="number")) #returns only numeric columns Dataframe
	print(dataset.select_dtypes(exclude="number").columns) 
	print(dataset["gender"].value_counts()) #returns counts excluding NaN values
	print(dataset["gender"].value_counts(dropna=False)) # returns counts including NaN values
	print(dataset["gender"].value_counts(normalize=True, dropna=False)) # returns counts as proportions including NaN values
	print(analysis.get_value_counts(dataset, "gender")) # returns counts including NaN values
	print(dataset.select_dtypes(include="str").columns) #returns only string columns Dataframe
	print(analysis.get_column_profile(dataset)) # returns a DataFrame with data type, missing values, and unique values for each column
	print(dataset["id"].duplicated().sum())
	print(analysis.get_duplicate_rows(dataset))

def main() -> None: 
	parser = argparse.ArgumentParser()
	parser.add_argument("file_path", type=str, help="Path to the dataset file")
	args = parser.parse_args()
	try:
		dataset = analysis.load_dataset(args.file_path)
		inspect_dataset(dataset)
	except FileNotFoundError as error:
		print(error)
	except ValueError as error:
		print(error)
	except pd.errors.EmptyDataError as error:
		print(error)
	except pd.errors.ParserError as error:
		print(error)

if __name__ == "__main__":
	main()