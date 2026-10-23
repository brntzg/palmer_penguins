
import pandas as pd
from palmerpenguins import load_penguins


# This dataset is already prepared for analysis, yet it includes only 8 data fields
def load_clean_dataset():
    penguins = load_penguins()
    print("Dataset records, fields:", penguins.shape)
    print(penguins.columns.tolist())
    return penguins


# This dataset includes all 18 data fields, yet it will need to be transformed fro analysis
def load_raw_dataset():
    gh_repo = "raw.githubusercontent.com/allisonhorst/palmerpenguins/"
    csv_file = "main/inst/extdata/penguins_raw.csv"
    repo_url = "https://" + gh_repo + csv_file

    penguins = pd.read_csv(repo_url, parse_dates=["Date Egg"])
    print("Dataset records, fields:", penguins.shape)
    print(penguins.columns.tolist())
    return penguins