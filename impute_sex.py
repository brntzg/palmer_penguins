from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


def impute_sex(penguins):
    """Return a copy with unknown sex predicted and recorded values preserved."""
    penguins = penguins.copy()
    penguins["sex_recorded"] = penguins["sex"].copy()
    sex = penguins["sex"].astype("string").str.strip().str.lower()
    penguins["sex"] = sex.map({"female": "Female", "male": "Male"}).fillna("Unknown")
    known = penguins["sex"].ne("Unknown")
    penguins["sex_source"] = known.map({True: "Recorded", False: "Unknown"})

    categorical = ["species", "island"]
    numeric = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
    # Avoid assigning sex from location/species alone when all measurements are missing.
    unknown = ~known & penguins[numeric].notna().any(axis=1)
    if not unknown.any() or penguins.loc[known, "sex"].nunique() < 2:
        return penguins

    preprocess = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ("num", SimpleImputer(strategy="median"), numeric),
    ])
    model = Pipeline([
        ("prep", preprocess),
        ("rf", RandomForestClassifier(n_estimators=300, random_state=13)),
    ])
    features = categorical + numeric
    model.fit(penguins.loc[known, features], penguins.loc[known, "sex"])
    penguins.loc[unknown, "sex"] = model.predict(penguins.loc[unknown, features])
    penguins.loc[unknown, "sex_source"] = "Estimated (random forest)"
    return penguins
