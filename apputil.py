# apputil.py
import pandas as pd

# -----------------------
# Exercise: Recursion
# -----------------------
def fibonacci(n):
    """
    Return the n-th Fibonacci number using recursion.
    - n must be a non-negative integer (0-based: fibonacci(0)==0, fibonacci(1)==1).
    """
    n = int(n)
    if n < 0:
        raise ValueError("n must be non-negative")
    # base cases
    if n == 0:
        return 0
    if n == 1:
        return 1
    # recursive case
    return fibonacci(n - 1) + fibonacci(n - 2)


def to_binary(n):
    """
    Convert a non-negative integer n to its binary representation (string).
    Examples:
      to_binary(2)  -> '10'
      to_binary(12) -> '1100'
    """
    n = int(n)
    if n < 0:
        raise ValueError("to_binary expects a non-negative integer")
    # base cases
    if n < 2:
        return str(n)
    # recursive case
    return to_binary(n // 2) + str(n % 2)


# -----------------------
# Exercise: Bellevue dataset tasks
# -----------------------

def _get_df_bellevue():
    """
    Helper: return the df_bellevue object from globals if present,
    otherwise raise an informative error. This ensures we don't run
    anything at import time and wait until the autograder provides it.
    """
    df = globals().get("df_bellevue", None)
    if df is None:
        raise NameError(
            "df_bellevue is not defined. The autograder (or your notebook) "
            "should set df_bellevue before calling these functions."
        )
    # Ensure it's a pandas DataFrame
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df_bellevue exists but is not a pandas DataFrame")
    return df


def task_1():
    """
    Return a list of all column names sorted by increasing number of missing values:
    [column_with_fewest_NAs, ..., column_with_most_NAs]

    Also fix the gender column's messy values (only inside this function).
    """
    df = _get_df_bellevue().copy()  # copy to avoid mutating global unexpectedly

    # If gender column exists, standardize it
    if "gender" in df.columns:
        # convert to string, strip whitespace, lower-case
        df["gender"] = df["gender"].astype("string").str.strip().str.lower()
        # common mappings
        df["gender"] = df["gender"].replace(
            {
                "m": "male",
                "f": "female",
                "male.": "male",
                "female.": "female",
                "man": "male",
                "woman": "female",
                "f/m": pd.NA,
            }
        )
        # keep other values as-is; missing values remain pd.NA

    # Count missing per column and sort ascending (fewest -> most)
    missing_counts = df.isna().sum()
    sorted_cols = missing_counts.sort_values(ascending=True).index.tolist()
    return sorted_cols


def task_2():
    """
    Return a DataFrame with columns:
        year, total_admissions

    year : each year present in the data (sorted ascending),
    total_admissions : number of rows for that year.

    The function expects df_bellevue to have a 'year' column. If not present,
    it will attempt to find a date column and extract year, but if none found,
    it will raise an informative error.
    """
    df = _get_df_bellevue().copy()

    # If 'year' present and numeric, use it directly
    if "year" in df.columns:
        # try to coerce to integer year
        try:
            years = pd.to_numeric(df["year"], errors="coerce").dropna().astype(int)
            # build counts using the original index alignment
            df_valid_year = df.loc[years.index].assign(year=years.values)
        except Exception:
            # fallback: use the column as-is for grouping
            df_valid_year = df.copy()
    else:
        # try to infer a year column from typical date columns
        date_cols = [c for c in df.columns if "date" in c.lower() or "year" in c.lower()]
        extracted = False
        for col in date_cols:
            try:
                years = pd.to_datetime(df[col], errors="coerce").dt.year
                if years.notna().any():
                    df = df.assign(year=years)
                    extracted = True
                    break
            except Exception:
                continue
        if not extracted:
            raise KeyError(
                "Could not find 'year' column or a date column to extract year from. "
                "Ensure df_bellevue has a 'year' column or a date-like column."
            )
        df_valid_year = df.copy()

    # Now group by year and count rows
    # Drop rows with missing year
    df_valid_year = df_valid_year.dropna(subset=["year"])
    # ensure integer year
    df_valid_year["year"] = df_valid_year["year"].astype(int)
    counts = df_valid_year.groupby("year").size().reset_index(name="total_admissions")
    counts = counts.sort_values("year").reset_index(drop=True)
    return counts


def task_3():
    """
    Return a pandas Series indexed by gender with the average age per gender.
    Index: gender
    Values: average age (float)
    """
    df = _get_df_bellevue().copy()

    if "gender" not in df.columns:
        raise KeyError("df_bellevue has no 'gender' column — cannot compute average age by gender")
    if "age" not in df.columns:
        raise KeyError("df_bellevue has no 'age' column — cannot compute average age by gender")

    # Clean gender (same as in task_1)
    df["gender"] = df["gender"].astype("string").str.strip().str.lower()
    df["gender"] = df["gender"].replace({"m": "male", "f": "female", "man": "male", "woman": "female"})

    # Coerce age to numeric, drop invalid
    df["age"] = pd.to_numeric(df["age"], errors="coerce")

    # Group and compute mean, drop NaN genders
    series = df.dropna(subset=["gender"]).groupby("gender")["age"].mean()
    # Return series sorted by index (optional)
    return series.sort_index()


def task_4():
    """
    Return a list of the 5 most common professions (strings) in order from most to least common.
    Cleans common whitespace and lowercases for counting, but returns prettified strings.
    """
    df = _get_df_bellevue().copy()

    if "profession" not in df.columns:
        raise KeyError("df_bellevue has no 'profession' column — cannot compute top professions")

    # Clean profession strings: coerce to string, strip, lower
    prof = df["profession"].astype("string").str.strip().str.lower()
    # Drop NA and empty strings
    prof = prof.replace("", pd.NA).dropna()
    if prof.empty:
        return []

    counts = prof.value_counts()
    top5 = counts.head(5).index.tolist()

    # Return in a prettier form: capitalize common words (but keep simple)
    pretty = [s.title() for s in top5]
    return pretty


# -----------------------
# Local testing block: will not run on import in the autograder
# -----------------------
if __name__ == "__main__":
    # quick local tests (these will only run when you execute apputil.py directly)
    print("fibonacci(9) ->", fibonacci(9))    # 34
    print("to_binary(12) ->", to_binary(12))  # '1100'
