import argparse
import pandas as pd

def inspect_dataset(dataset: pd.DataFrame) -> None:
    print(dataset.shape)
    print(dataset.dtypes)
    print(dataset.columns)
    print(dataset.isna().sum())
    print(dataset.duplicated().sum())
    print(dataset.describe())
    print(dataset.describe(include='str'))
    print(dataset.head())

def load_dataset(file_path: str) -> pd.DataFrame:
    dataset = pd.read_csv(file_path)
    return dataset

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