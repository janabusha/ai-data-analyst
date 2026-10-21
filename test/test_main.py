import csv
import pytest
import pandas as pd

from main import load_dataset
def test_load_dataset(tmp_path):  # Test loading a valid dataset
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