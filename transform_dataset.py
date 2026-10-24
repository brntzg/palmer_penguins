
import pandas as pd


def transform_raw_dataset(penguins: pd.DataFrame) -> pd.DataFrame:
    """Transform the raw Palmer Penguins data into a standardized DataFrame."""

    # Avoid modifying the original dataset:
    penguins = penguins.copy()

    # Rename the columns to snake_case and relabel some for comprehsibility:
    penguins = penguins.rename(columns={
        "studyName": "study_name",
        "Sample Number": "sample_number",
        "Species": "species",
        "Region": "region",
        "Island": "island",
        "Stage": "stage",
        "Individual ID": "id",
        "Clutch Completion": "clutch_completion",
        "Date Egg": "date_egg",
        "Culmen Length (mm)": "bill_length_mm",
        "Culmen Depth (mm)": "bill_depth_mm",
        "Flipper Length (mm)": "flipper_length_mm",
        "Body Mass (g)": "body_mass_g",
        "Sex": "sex",
        "Delta 15 N (o/oo)": "nitrogen15",
        "Delta 13 C (o/oo)": "carbon13",
        "Comments": "comments"
    })

    # Standardize species name values to common name identifier:
    penguins["species"] = penguins["species"].str.split().str[0]

    # Standardize sex values' case:
    penguins["sex"] = penguins["sex"].str.lower()
    
    # Remove unecessary columns from the DataFrame:
    penguins = penguins.drop(columns=[
        "study_name", # Redundant as year field is used
        "sample_number", # Superfluous and values are not unique
        "region", # All the same value: "Anvers"
        "stage", # All the same value: "Adult, 1 egg stage"
        "id", # Superflous data 
        "clutch_completion", # Superflous data
        "comments", # Superflous data
    ])

    # Reformat the datetime stamp field to year:
    penguins["year"] = penguins.pop("date_egg").dt.year.astype("category")

    # Recast str fields to category for memory efficiency:
    penguins = penguins.astype({
        "species": "category",
        "island": "category",
        "sex": "category",
    })

    return penguins