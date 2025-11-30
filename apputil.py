# apputil.py
import pandas as pd
import os
import glob

# -----------------------
# Recursion exercises (unchanged behavior)
# -----------------------
def fibonacci(n):
    n = int(n)
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)


def to_binary(n):
    n = int(n)
    if n < 0:
        raise ValueError("to_binary expects non-negative integer")
    if n < 2:
        return str(n)
    return to_binary(n // 2) + str(n % 2)


# -----------------------
# Helper to obtain df_bellevue robustly
# -----------------------
def _get_df_bellevue(df=None):
    """
    Attempts to return a pandas DataFrame representing the Bellevue dataset.

    Order of attempts:
      1. Use df if provided (preferred).
      2. If a global variable df_bellevue exists in this module, use it.
      3. Search current directory for a CSV filename containing likely substrings
         like 'bellev', 'bellevue', or 'almshouse' and try to read it.
      4. As a last resort, read the first .csv file in cwd (if any).
      5. If none succeed, raise NameError (clear message).
    """
    # 1) Use provided df
    if df is not None:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Provided df argument is not a pandas DataFrame")
        return df.copy()

    # 2) Check module global
    g = globals()
    if "df_bellevue" in g and isinstance(g["df_bellevue"], pd.DataFrame):
        return g["df_bellevue"].copy()

    # 3) Search for likely file names in cwd
    cwd_files = os.listdir(".")
    csv_candidates = [f for f in cwd_files if f.lower().endswith(".csv")]
    # prefer names containing likely substrings
    preferred = [f for f in csv_candidates if any(x in f.lower() for x in ("bellev", "bellevue", "almshouse"))]
    candidates = preferred if preferred else csv_candidates

    for fname in candidates:
        try:
            df_try = pd.read_csv(fname)
            # basic sanity check: must be a DataFrame with >0 rows and >0 columns
            if isinstance(df_try, pd.DataFrame) and df_try.shape[0] > 0 and df_try.shape[1] > 0:
                return df_try
        except Exception:
            continue

    # 5) Nothing found — raise clear error
    raise NameError(
        "df_bellevue is not defined and no suitable CSV found in the working directory. "
        "Call the function with df=your_dataframe, or set df_bellevue in this module before calling."
    )


# -----------------------
# Bellevue tasks (now accept optional df param)
# -----------------------

def task_1(df=None):
    """
    Return a LIST of all column names sorted by increasing number of missing values.
    """
    df_local = _get_df_bellevue(df)

    # Clean gender if present (do not mutate original)
    if "gender" in df_local.columns:
        df_local["gender"] = df_local["gender"].astype("string").str.strip().str.lower()
        df_local["gender"] = df_local["gender"].replace({
            "m": "male", "f": "female", "male.": "male", "female.": "female",
            "man": "male", "woman": "female", "f/m": pd.NA
        })

    missing_counts = df_local.isna().sum()
    sorted_cols = missing_counts.sort_values(ascending=True).index.tolist()
    return sorted_cols


def task_2(df=None):
    """
    Return a DataFrame with columns ['year', 'total_admissions'] with counts per year.
    """
    df_local = _get_df_bellevue(df)

    if "year" in df_local.columns:
        # try numeric coercion
        years = pd.to_numeric(df_local["year"], errors="coerce")
        df_local = df_local.assign(_year=years)
    else:
        # try to detect a date-like column to extract year
        date_cols = [c for c in df_local.columns if "date" in c.lower() or "year" in c.lower()]
        extracted = False
        for c in date_cols:
            try:
                years = pd.to_datetime(df_local[c], errors="coerce").dt.year
                if years.notna().any():
                    df_local = df_local.assign(_year=years)
                    extracted = True
                    break
            except Exception:
                continue
        if not extracted:
            raise KeyError("Could not find a 'year' column or a date-like column to extract year from.")

    df_valid = df_local.dropna(subset=["_year"]).copy()
    df_valid["_year"] = df_valid["_year"].astype(int)
    counts = df_valid.groupby("_year").size().reset_index(name="total_admissions")
    counts = counts.rename(columns={"_year": "year"}).sort_values("year").reset_index(drop=True)
    return counts


def task_3(df=None):
    """
    Return a Series indexed by gender with average age for each gender.
    """
    df_local = _get_df_bellevue(df)

    if "gender" not in df_local.columns:
        raise KeyError("df_bellevue has no 'gender' column — cannot compute average age by gender")
    if "age" not in df_local.columns:
        raise KeyError("df_bellevue has no 'age' column — cannot compute average age by gender")

    df_local["gender"] = df_local["gender"].astype("string").str.strip().str.lower()
    df_local["gender"] = df_local["gender"].replace({"m": "male", "f": "female", "man": "male", "woman": "female"})

    df_local["age"] = pd.to_numeric(df_local["age"], errors="coerce")
    result = df_local.dropna(subset=["gender"]).groupby("gender")["age"].mean()
    return result.sort_index()


def task_4(df=None):
    """
    Return a list of 5 most common professions (strings), most common first.
    """
    df_local = _get_df_bellevue(df)

    if "profession" not in df_local.columns:
        raise KeyError("df_bellevue has no 'profession' column — cannot compute top professions")

    prof = df_local["profession"].astype("string").str.strip().str.lower().replace("", pd.NA).dropna()
    if prof.empty:
        return []
    top5 = prof.value_counts().head(5).index.tolist()
    return [s.title() for s in top5]


# Local testing block (won't run on import by autograder)
if __name__ == "__main__":
    print("fibonacci(9) ->", fibonacci(9))
    print("to_binary(12) ->", to_binary(12))
