import argparse
import pandas as pd

def load_dataset(file_path: str) -> pd.DataFrame:
    dataset = pd.read_csv(file_path)
    return dataset

def get_duplicate_row_count(dataset: pd.DataFrame) -> int:
    return dataset.duplicated().sum()

def get_missing_value_counts(dataset: pd.DataFrame) -> pd.Series:
    return dataset.isna().sum()

def inspect_dataset(dataset: pd.DataFrame) -> None:
    print("Dataset Shape:", dataset.shape)
    print("\nDataset Dtypes:")
    print(dataset.dtypes)
    print("\nDataset Columns:")
    print(dataset.columns)
    print("\nMissing Values:")
    print(get_missing_value_counts(dataset))
    print("\nDuplicate Rows:", get_duplicate_row_count(dataset))
    print("\nDataset Description:")
    print(dataset.describe())
    print("\nDataset Description (String Columns):")
    print(dataset.describe(include='str'))
    print("\nFirst Few Rows:")
    print(dataset.head())

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", type=str, help="Path to the dataset file")
    args = parser.parse_args()
    try:
        dataset = load_dataset(args.file_path)
        inspect_dataset(dataset)
    except FileNotFoundError as error:
        print(error)
    except pd.errors.EmptyDataError as error:
        print(error)
    except pd.errors.ParserError as error:
        print(error)

if __name__ == "__main__":
    main()