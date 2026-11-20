from pathlib import Path
from typing import BinaryIO
import pandas as pd
import streamlit as st

def load_dataset(file_source: str | Path | BinaryIO) -> pd.DataFrame:
	if hasattr(file_source, "name"): #	 Check if the file_source has a 'name' attribute (e.g., file-like object)
		source_name = file_source.name
	else:
		source_name = str(file_source)

	suffix = Path(source_name).suffix.lower()

	if suffix == '.xlsx':
		dataset = pd.read_excel(file_source)
	elif suffix == ".csv":
		dataset = pd.read_csv(file_source)
	else:
		raise ValueError(f"'{suffix}' is unsupported")
	
	if dataset.empty:
		raise ValueError("The dataset is empty.")
	
	return dataset

def get_duplicate_row_count(dataset: pd.DataFrame) -> int: # returns the count of duplicate rows in the dataset.
	return dataset.duplicated().sum()

def get_missing_value_counts(dataset: pd.DataFrame) -> pd.Series: # returns counts of missing values for each column in the dataset.
	return dataset.isna().sum()

def get_value_counts(dataset: pd.DataFrame,
                     column_name: str,
					 normalize: bool = False,
					 dropna: bool = False,) -> pd.Series: # returns counts including NaN values. 
	if column_name not in dataset.columns:
		raise ValueError(f"Column '{column_name}' does not exist in the dataset.")
	return dataset[column_name].value_counts(normalize=normalize, dropna=dropna)

def get_string_columns(dataset: pd.DataFrame) -> pd.Index: # returns the names of columns with string data types.
	return dataset.select_dtypes(include="str").columns

def get_unique_value_counts(dataset: pd.DataFrame) -> pd.Series:   # returns the count of unique values for each column in the dataset.
	return dataset.nunique(dropna=False)

def get_column_profile(dataset: pd.DataFrame) -> pd.DataFrame:
    # Calculate reusable column statistics.
    missing_counts = get_missing_value_counts(dataset)
    unique_counts = get_unique_value_counts(dataset)
    row_count = len(dataset)

    # Combine all columns with detected type problems.
    type_issue_columns = (
        set(get_mixed_type_columns(dataset))
        | set(get_suspicious_numeric_columns(dataset))
    )

    # Calculate the percentage of missing values per column.
    missing_percentages = (
        missing_counts / row_count * 100
        if row_count > 0
        else pd.Series(0.0, index=dataset.columns)
    )

    detected_types = []
    completeness_values = []
    statuses = []

    for column in dataset.columns:
        dtype = dataset[column].dtype
        missing_count = int(missing_counts[column])
        has_missing_values = missing_count > 0
        has_type_issue = column in type_issue_columns

        # Convert pandas types into readable names.
        if has_type_issue:
            detected_type = "Mixed"
        elif pd.api.types.is_bool_dtype(dtype):
            detected_type = "Boolean"
        elif pd.api.types.is_integer_dtype(dtype):
            detected_type = "Integer"
        elif pd.api.types.is_float_dtype(dtype):
            detected_type = "Decimal"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            detected_type = "Date / Time"
        elif pd.api.types.is_string_dtype(dtype):
            detected_type = "String"
        else:
            detected_type = str(dtype)

        detected_types.append(detected_type)
        if has_missing_values and has_type_issue:
            status = "2 issues"
        elif has_missing_values:
            status = f"{missing_count:,} missing"
        elif has_type_issue:
            status = "Mixed type"
        else:
            status = "OK"
        statuses.append(status)

    profile = pd.DataFrame({
        "Data Type": detected_types,
        "Complete": 100 - missing_percentages,
        "Missing Values": missing_counts,
        "Unique Values": unique_counts,
        "Status": statuses,
    })
    return profile

def get_duplicate_rows(dataset: pd.DataFrame) -> pd.DataFrame:
	return dataset[dataset.duplicated(keep=False)]

def get_numeric_columns(dataset: pd.DataFrame) -> pd.Index:
	return dataset.select_dtypes(include="number").columns

def get_rows_with_missing_values(dataset: pd.DataFrame) -> pd.DataFrame:
	return dataset[dataset.isna().any(axis=1)] #axis=1 checks across the columns of each row in any()

def get_invalid_numeric_values(column : pd.Series) -> pd.Series:
	is_non_numeric = pd.to_numeric(column, errors='coerce').isna()
	return column[is_non_numeric & column.notna()]

def get_value_type_counts(column: pd.Series) -> pd.Series:
	return column.dropna().map(type).value_counts()

def get_mixed_type_columns(dataset: pd.DataFrame) -> list[str]:
	column_names = []

	for name in dataset:
		column_series = dataset[name]
		if get_value_type_counts(column_series).count() > 1:
			column_names.append(name)

	return column_names

def get_numeric_conversion_ratio(column: pd.Series) -> float:
    non_missing_values = column.dropna()
    converted_values = pd.to_numeric(non_missing_values, errors="coerce")
    is_numeric = converted_values.notna()

    return is_numeric.mean()

def get_suspicious_numeric_columns( dataset: pd.DataFrame, threshold: float = 0.8) -> list[str]:
	column_names = []
	
	for name in dataset:
		column_series = dataset[name]
		if get_numeric_conversion_ratio(column_series) >= threshold and get_numeric_conversion_ratio(column_series) < 1:
			column_names.append(name)

	return column_names

def get_top_value_share(column: pd.Series) -> float | None:
	non_missing_values = column.dropna()

	if non_missing_values.empty:
		return None
	return float(non_missing_values.value_counts(normalize=True).iloc[0])

def get_correlation_matrix(
    dataset: pd.DataFrame,
    included_identifiers: list[str] | None = None,
	) -> pd.DataFrame:
	identifiers_to_exclude = []
	identifiers = get_likely_identifier_columns(dataset)
	
	if included_identifiers is None:
		included_identifiers = []

	for identifier in identifiers:
		if identifier not in included_identifiers:
			identifiers_to_exclude.append(identifier)

	analysis_columns = get_numeric_columns(dataset).difference(identifiers_to_exclude, sort=False)
	return dataset[analysis_columns].corr()

def get_likely_identifier_columns(dataset: pd.DataFrame,) -> list[str]:
	possible_id = []

	for name in dataset.columns:
		if ("id" == name.lower() 
		    or name.lower().endswith("_id") 
		    or name.lower().endswith(" id") 
		    or name.lower().endswith("id") 
			or name.lower().startswith("unnamed")
			or name.lower() in ("id", "index", "ranks")
		):
			possible_id.append(name)
	return possible_id

def get_strongest_relationships(correlation_matrix: pd.DataFrame) -> pd.DataFrame:
    relationships = []
    columns = correlation_matrix.columns

    for first_index in range(len(columns)):
        for second_index in range(first_index + 1, len(columns)):
            first_column = columns[first_index]
            second_column = columns[second_index]

            correlation = correlation_matrix.loc[
                first_column,
                second_column,
            ]

            if pd.isna(correlation):
                continue

            relationships.append({
                "Column 1": first_column,
                "Column 2": second_column,
                "Correlation": correlation,
                "Strength": abs(correlation),
            })

    relationships_dataframe = pd.DataFrame(relationships)

    if relationships_dataframe.empty:
        return pd.DataFrame(
            columns=["Column 1", "Column 2", "Correlation"]
        )

    strongest_relationships = (
        relationships_dataframe
        .sort_values("Strength", ascending=False)
        .head(3)
        .drop(columns="Strength")
        .reset_index(drop=True)
    )

    return strongest_relationships

def get_numeric_summary(dataset: pd.DataFrame) -> pd.DataFrame:
    numeric_columns = get_numeric_columns(dataset)
    identifiers = get_likely_identifier_columns(dataset)

    analysis_columns = numeric_columns.drop(
        identifiers,
        errors="ignore",
    )

    return dataset[analysis_columns].describe().transpose()


def get_visualization_profile(
    dataset: pd.DataFrame,
	) -> list[dict]:
    profile = []

    for column in dataset.columns:
        usable_values = dataset[column].dropna()

        # Cannot create a useful chart from these columns.
        if usable_values.empty:
            continue

        if usable_values.nunique() <= 1:
            continue

        unique_values = usable_values.nunique()

        profile.append(
            {
                "name": column,
                "dtype": str(dataset[column].dtype),
                "unique_values": unique_values,
                "unique_percentage": round(
                    unique_values / len(dataset) * 100,
                    2,
                ),
                "missing_values": dataset[column].isna().sum(),
            }
        )

    return profile
