import csv
import pytest
import pandas as pd

from analysis import load_dataset, get_missing_value_counts, get_duplicate_row_count, get_value_counts, get_string_columns
from analysis import get_unique_value_counts, get_column_profile, get_duplicate_rows, get_numeric_columns

def test_load_csv_dataset(tmp_path):  # Test loading a valid dataset
    csv_path = tmp_path / "names.csv"
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['first_name', 'last_name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'first_name': 'Baked', 'last_name': 'Beans'})
        writer.writerow({'first_name': 'Lovely', 'last_name': 'Spam'})
        writer.writerow({'first_name': 'Wonderful', 'last_name': 'Spam'})

    dataset = load_dataset(csv_path)
    assert dataset.shape == (3, 2)  
    assert dataset.columns.tolist() == ["first_name", "last_name"]

def test_empty_xslx_file(tmp_path):
    xlsx_path = tmp_path / "empty_file.xlsx"
    empty = pd.DataFrame({
    })

    empty.to_excel(xlsx_path, index=False)
    with pytest.raises(ValueError):
        load_dataset(xlsx_path)

def test_load_xlsx_dataset(tmp_path):  # Test loading a valid dataset
    xlsx_path = tmp_path / "names.xlsx"
    expected = pd.DataFrame({
    "name": ["Alice", "Bob"],
    "age": [30, 25],
    })

    expected.to_excel(xlsx_path, index=False)
    dataset = load_dataset(xlsx_path)
    assert dataset.shape == (2,2)
    assert dataset.columns.tolist() == ["name", "age"]


def test_load_dataset_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_dataset(tmp_path / "this_file_does_not_exist.csv")

def test_load_dataset_empty_file(tmp_path):
    csv_path = tmp_path / "empty.csv"
    with open(csv_path, 'w') as csvfile:
        pass  # Create an empty file
    with pytest.raises(pd.errors.EmptyDataError):
        load_dataset(csv_path)

def test_load_dataset_invalid_format(tmp_path):
    csv_path = tmp_path / "invalid.csv"
    with open(csv_path, 'w') as csvfile:
        csvfile.write("name,age\nAda,30\nGrace,31,extra\n")
    with pytest.raises(pd.errors.ParserError):
        load_dataset(csv_path)

def test_load_dataset_value_error(tmp_path):
    txt_path = tmp_path / "sample.txt"
    txt_path.write_text("some text")
    with pytest.raises(ValueError):
        load_dataset(txt_path)

def test_get_missing_value_counts(tmp_path):
    csv_path = tmp_path / "missing_values.csv"
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['A', 'B', 'C']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'A': 1, 'B': 2, 'C': 3})
        writer.writerow({'A': 4, 'B': None, 'C': 6})
        writer.writerow({'A': None, 'B': 8, 'C': None})

    dataset = load_dataset(csv_path)
    missing_counts = get_missing_value_counts(dataset)
    assert missing_counts['A'] == 1
    assert missing_counts['B'] == 1
    assert missing_counts['C'] == 1

def test_get_duplicate_row_count(tmp_path):
    csv_path = tmp_path / "duplicates.csv"
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['X', 'Y']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'X': 1, 'Y': 2})
        writer.writerow({'X': 3, 'Y': 4})
        writer.writerow({'X': 1, 'Y': 2})  # Duplicate row

    dataset = load_dataset(csv_path)
    duplicate_count = get_duplicate_row_count(dataset)
    assert duplicate_count == 1

def test_get_value_counts_existent_column(tmp_path):
    csv_path = tmp_path / "value_counts.csv"
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['gender']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'gender': 'Male'})
        writer.writerow({'gender': 'Female'})
        writer.writerow({'gender': 'Male'})
        writer.writerow({'gender': None})  # Missing value

    dataset = load_dataset(csv_path)
    value_counts = get_value_counts(dataset, 'gender')
    assert value_counts['Male'] == 2
    assert value_counts['Female'] == 1
    assert value_counts.loc[value_counts.index.isna()].iloc[0] == 1 

def test_get_value_counts_nonexistent_column(tmp_path):
    csv_path = tmp_path / "value_counts.csv"
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['gender']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'gender': 'Male'})
        writer.writerow({'gender': 'Female'})

    dataset = load_dataset(csv_path)
    with pytest.raises(ValueError):
        get_value_counts(dataset, 'nonexistent_column')

def test_get_string_columns(tmp_path):
    csv_path = tmp_path / "string_columns.csv"
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['name', 'age', 'city']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'name': 'Alice', 'age': 30, 'city': 'New York'})
        writer.writerow({'name': 'Bob', 'age': 25, 'city': 'Los Angeles'})

    dataset = load_dataset(csv_path)
    string_columns = get_string_columns(dataset)
    assert string_columns.tolist() == ["name", "city"]

def test_get_unique_value_counts(tmp_path):
    csv_path = tmp_path / "unique_values.csv"
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['A', 'B']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'A': 1, 'B': 'X'})
        writer.writerow({'A': 2, 'B': 'Y'})
        writer.writerow({'A': 1, 'B': 'X'})  # Duplicate row
        writer.writerow({'A': None, 'B': 'Z'})  # Missing value

    dataset = load_dataset(csv_path)
    unique_counts = get_unique_value_counts(dataset)
    assert unique_counts['A'] == 3  # Unique values: 1, 2, NaN
    assert unique_counts['B'] == 3  # Unique values: X, Y, Z

def test_get_column_profile(tmp_path):
    csv_path = tmp_path / "profile.csv"
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['age', 'Sex']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'age': 23, 'Sex': 'F' })
        writer.writerow({'age': 34, 'Sex': 'M' })
        writer.writerow({'age': None,'Sex': 'F' })

    dataset = load_dataset(csv_path)
    profile = get_column_profile(dataset)
    assert profile.shape == (2,4)
    assert profile.loc["age", "Missing Values"] == 1
    assert profile.loc["Sex", "Unique Values"] == 2
    assert profile.loc["age", "Unique Values"] == 3
    assert profile.loc["Sex", "Data Type"] == 'str'
    assert profile.loc["age", "Missing Percentage"] == 1 / 3 * 100

def test_get_duplicate_rows(tmp_path):
    csv_path = tmp_path / "duplicated.csv"
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['age', 'Sex']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'age': 23, 'Sex': 'F' })
        writer.writerow({'age': 34, 'Sex': 'M' })
        writer.writerow({'age': 34, 'Sex': 'M' })
        writer.writerow({'age': None,'Sex': 'F' })

    dataset = load_dataset(csv_path)
    duplicates = get_duplicate_rows(dataset)
    expected = pd.DataFrame(
        {"age": [34.0, 34.0], "Sex": ["M", "M"]},
        index=[1, 2],
    )
    pd.testing.assert_frame_equal(duplicates, expected)

def test_get_numeric_columns(tmp_path):
    csv_path = tmp_path / "numeric_columns.csv"
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['name', 'age', 'height']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'name': 'Alice', 'age': 30, 'height': 165 })
        writer.writerow({'name': 'Bob', 'age': 25, 'height': 183 })

    dataset = load_dataset(csv_path)
    numeric_columns = get_numeric_columns(dataset)
    assert numeric_columns.tolist() == ["age", "height"]