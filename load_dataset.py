
import pandas as pd
from palmerpenguins import load_penguins


def load_clean_dataset() -> pd.DataFrame:
    """Load the analysis-ready Palmer Penguins dataset (8 fields)."""

    penguins = load_penguins()

    print(f"The clean dataset has {len(penguins.index)} records.")
    print(f"It has {len(penguins.columns)} fields:", penguins.columns.tolist())

    return penguins


def load_raw_dataset() -> pd.DataFrame:
    """Load the original Palmer Penguins dataset (17 fields)."""

    gh_repo_url = (
        "https://raw.githubusercontent.com/"
        "allisonhorst/palmerpenguins/main/"
        "inst/extdata/penguins_raw.csv"
    )

    penguins = pd.read_csv(
        gh_repo_url,
        parse_dates=["Date Egg"]
    )

    print(f"The raw dataset has {len(penguins.index)} records.")
    print(f"It has {len(penguins.columns)} fields:", penguins.columns.tolist())

    return penguins