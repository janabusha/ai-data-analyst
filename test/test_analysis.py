import csv
import pytest
import pandas as pd

import analysis

def test_load_csv_dataset(tmp_path):  # Test loading a valid dataset
    csv_path = tmp_path / "names.csv"
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['first_name', 'last_name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'first_name': 'Baked', 'last_name': 'Beans'})
        writer.writerow({'first_name': 'Lovely', 'last_name': 'Spam'})
        writer.writerow({'first_name': 'Wonderful', 'last_name': 'Spam'})

    dataset = analysis.load_dataset(csv_path)
    assert dataset.shape == (3, 2)  
    assert dataset.columns.tolist() == ["first_name", "last_name"]

def test_empty_xslx_file(tmp_path):
    xlsx_path = tmp_path / "empty_file.xlsx"
    empty = pd.DataFrame({
    })

    empty.to_excel(xlsx_path, index=False)
    with pytest.raises(ValueError):
        analysis.load_dataset(xlsx_path)

def test_load_xlsx_dataset(tmp_path):  # Test loading a valid dataset
    xlsx_path = tmp_path / "names.xlsx"
    expected = pd.DataFrame({
    "name": ["Alice", "Bob"],
    "age": [30, 25],
    })

    expected.to_excel(xlsx_path, index=False)
    dataset = analysis.load_dataset(xlsx_path)
    assert dataset.shape == (2,2)
    assert dataset.columns.tolist() == ["name", "age"]


def test_load_dataset_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        analysis.load_dataset(tmp_path / "this_file_does_not_exist.csv")

def test_load_dataset_empty_file(tmp_path):
    csv_path = tmp_path / "empty.csv"
    with open(csv_path, 'w') as csvfile:
        pass  # Create an empty file
    with pytest.raises(pd.errors.EmptyDataError):
        analysis.load_dataset(csv_path)

def test_load_dataset_invalid_format(tmp_path):
    csv_path = tmp_path / "invalid.csv"
    with open(csv_path, 'w') as csvfile:
        csvfile.write("name,age\nAda,30\nGrace,31,extra\n")
    with pytest.raises(pd.errors.ParserError):
        analysis.load_dataset(csv_path)

def test_load_dataset_value_error(tmp_path):
    txt_path = tmp_path / "sample.txt"
    txt_path.write_text("some text")
    with pytest.raises(ValueError):
        analysis.load_dataset(txt_path)

def test_get_missing_value_counts(tmp_path):
    csv_path = tmp_path / "missing_values.csv"
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['A', 'B', 'C']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'A': 1, 'B': 2, 'C': 3})
        writer.writerow({'A': 4, 'B': None, 'C': 6})
        writer.writerow({'A': None, 'B': 8, 'C': None})

    dataset = analysis.load_dataset(csv_path)
    missing_counts = analysis.get_missing_value_counts(dataset)
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

    dataset = analysis.load_dataset(csv_path)
    duplicate_count = analysis.get_duplicate_row_count(dataset)
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

    dataset = analysis.load_dataset(csv_path)
    value_counts = analysis.get_value_counts(dataset, 'gender')
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

    dataset = analysis.load_dataset(csv_path)
    with pytest.raises(ValueError):
        analysis.get_value_counts(dataset, 'nonexistent_column')

def test_get_string_columns(tmp_path):
    csv_path = tmp_path / "string_columns.csv"
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['name', 'age', 'city']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'name': 'Alice', 'age': 30, 'city': 'New York'})
        writer.writerow({'name': 'Bob', 'age': 25, 'city': 'Los Angeles'})

    dataset = analysis.load_dataset(csv_path)
    string_columns = analysis.get_string_columns(dataset)
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

    dataset = analysis.load_dataset(csv_path)
    unique_counts = analysis.get_unique_value_counts(dataset)
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

    dataset = analysis.load_dataset(csv_path)
    profile = analysis.get_column_profile(dataset)
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

    dataset = analysis.load_dataset(csv_path)
    duplicates = analysis.get_duplicate_rows(dataset)
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

    dataset = analysis.load_dataset(csv_path)
    numeric_columns = analysis.get_numeric_columns(dataset)
    assert numeric_columns.tolist() == ["age", "height"]

def test_get_rows_with_missing_values(tmp_path):
    csv_path = tmp_path / "missing_values.csv"
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['name', 'age', 'height']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'name': 'Alice', 'age': 30, 'height': 165 })
        writer.writerow({'name': 'Bob', 'age': 25, 'height': 183 })
        writer.writerow({'name': 'Anna', 'age': None, 'height': 183 })
        writer.writerow({'name': None, 'age': 25, 'height': 12 })

    dataset = analysis.load_dataset(csv_path)
    missing_values = analysis.get_rows_with_missing_values(dataset)
    assert missing_values.shape == (2,3)

def test_get_invalid_numeric_values():
    invalid_numeric_series = pd.Series(["10", "20", "O", None, "31.5"])

    invalid_numeric = analysis.get_invalid_numeric_values(invalid_numeric_series)
    assert invalid_numeric[2] == 'O'
    assert invalid_numeric.index.tolist() == [2]

def test_get_value_type_counts():
    value_series = pd.Series(["active", "inactive", 0, "active", None], dtype="object")

    values = analysis.get_value_type_counts(value_series)
    assert values.at[str] == 3
    assert values.at[int] == 1

def test_get_mixed_type_columns():
    data = pd.DataFrame({
    "name": ["Alice", "Bob", 0, "Rihards"],
    "age": [30, 25, 15, 28],
    })

    result = analysis.get_mixed_type_columns(data)
    assert result == ["name"]

def test_get_numeric_conversion_ratio():
    column = pd.Series(["10", "oops", None])

    assert analysis.get_numeric_conversion_ratio(column) == 0.5

def test_get_suspicious_numeric_columns():
    data = pd.DataFrame({
    "name": ["Alice", "Bob", "Jana", "Rihards", "Anna"],
    "age": ["12", "j", "15", "28", "14"],
    })
    result = analysis.get_suspicious_numeric_columns(data)
    assert result == ["age"]

def test_get_top_value_share():
    column = pd.Series(["Female", "Female", "Male", None])

    result = analysis.get_top_value_share(column)
    assert result == pytest.approx(2 / 3)

def test_get_correlation_matrix():
    data = pd.DataFrame({
    "Height": [150, 160, 170, 180],
    "Weight": [50, 65, 68, 80],
    "Name": ["A", "B", "C", "D"],
    })

    result = analysis.get_correlation_matrix(data)
    assert result.loc["Height", "Height"] == 1.00
    assert result.loc["Weight", "Height"] == 0.973035471890234
    assert "Name" not in result.columns

def test_get_likely_identifier_columns():
    data = pd.DataFrame({
    "customer_id": [1, 2, 3, 4],
    "Product_Id": [50, 65, 68, 80],
    "Name": ["A", "B", "C", "D"],
    "id": [1, 2, 3, 4],
    "Unnamed: 0": [0, 1, 2, 3],
    "middle_name": ["A", "B", "C", "D"],
    "paid_amount": [10, 20, 30, 40],    
    })

    list_of_ids = analysis.get_likely_identifier_columns(data)
    assert list_of_ids[0] == 'customer_id'
    assert list_of_ids[1] == 'Product_Id'
    assert list_of_ids[2] == 'id'
    assert list_of_ids[3] == 'Unnamed: 0'
    assert list_of_ids == ['customer_id', 'Product_Id', 'id', 'Unnamed: 0']

def test_correlation_matrix_excludes_identifiers():
    data = pd.DataFrame({
        "id": [1, 2, 3, 4],
        "Age": [20, 30, 40, 50],
        "Income": [2000, 3000, 4000, 5000],
    })

    result = analysis.get_correlation_matrix(data)

    assert result.columns.tolist() == ["Age", "Income"]
    assert result.index.tolist() == ["Age", "Income"]

def test_correlation_matrix_can_include_selected_identifier():
    data = pd.DataFrame({
        "customer_id": [1, 2, 3, 4],
        "product_id": [10, 20, 30, 40],
        "Revenue": [100, 120, 90, 150],
    })

    result = analysis.get_correlation_matrix(
        data,
        included_identifiers=["customer_id"],
    )

    assert result.columns.tolist() == [
        "customer_id",
        "Revenue",
    ]

def test_get_strongest_relationships():
    correlation_matrix = pd.DataFrame(
        {
            "A": [1.0, -0.95, 0.20],
            "B": [-0.95, 1.0, 0.70],
            "C": [0.20, 0.70, 1.0],
        },
        index=["A", "B", "C"],
    )

    result = analysis.get_strongest_relationships(correlation_matrix)

    assert result.iloc[0]["Column 1"] == "A"
    assert result.iloc[0]["Column 2"] == "B"
    assert result.iloc[0]["Correlation"] == pytest.approx(-0.95)

def test_get_numeric_summary():
    data = pd.DataFrame({
        "customer_id": [1, 2, 3, 4],
        "age": [45, 20, 23, 36],
        "Revenue": [100, 120, 90, 150],
    })

    result = analysis.get_numeric_summary(data)

    assert "customer_id" not in result.index
    assert result.loc["age", "max"]  == 45
    assert result.loc["Revenue", "min"] == 90