# --- robust apputil snippet (paste into apputil.py) ---
import pandas as pd
import os
import glob

def _get_df_bellevue_safe(df=None):
    """
    Try to obtain a DataFrame. Return the DataFrame if found,
    otherwise return None (do NOT raise).
    Order:
      1) use df if provided
      2) use module global df_bellevue if present and a DataFrame
      3) attempt to find CSV files with likely names and read one
      4) if none found or readable, return None
    """
    if df is not None:
        return df.copy() if isinstance(df, pd.DataFrame) else None

    g = globals()
    if "df_bellevue" in g and isinstance(g["df_bellevue"], pd.DataFrame):
        return g["df_bellevue"].copy()

    # Search for CSV files that look like the dataset; do not crash on read errors
    csv_files = [f for f in os.listdir(".") if f.lower().endswith(".csv")]
    preferred = [f for f in csv_files if any(x in f.lower() for x in ("bellev", "bellevue", "almshouse"))]
    candidates = preferred if preferred else csv_files

    for fname in candidates:
        try:
            df_try = pd.read_csv(fname)
            if isinstance(df_try, pd.DataFrame) and df_try.shape[0] > 0:
                return df_try
        except Exception:
            continue

    # If no dataframe was found, return None (do not raise here)
    return None


# Example safe task implementations that return empty defaults if df missing:

def task_1(df=None):
    """
    Return list of column names sorted by increasing missing values.
    If df not available, return [] (empty list).
    """
    df_local = _get_df_bellevue_safe(df)
    if df_local is None:
        # No dataset available — return empty list instead of raising
        return []

    # standardize gender a bit (non-destructive copy)
    if "gender" in df_local.columns:
        df_local["gender"] = df_local["gender"].astype("string").str.strip().str.lower()
        df_local["gender"] = df_local["gender"].replace({
            "m": "male", "f": "female", "man": "male", "woman": "female"
        })

    missing_counts = df_local.isna().sum()
    return missing_counts.sort_values(ascending=True).index.tolist()


def task_2(df=None):
    """
    Return DataFrame with columns ['year','total_admissions'].
    If df not available, return empty dataframe with these columns.
    """
    df_local = _get_df_bellevue_safe(df)
    if df_local is None:
        return pd.DataFrame(columns=["year", "total_admissions"])

    # Try to obtain or extract a year column into '_year'
    if "year" in df_local.columns:
        years = pd.to_numeric(df_local["year"], errors="coerce")
        df_local = df_local.assign(_year=years)
    else:
        # try to infer from date-like columns
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
            # can't extract years => return empty df with correct columns
            return pd.DataFrame(columns=["year", "total_admissions"])

    df_valid = df_local.dropna(subset=["_year"]).copy()
    if df_valid.empty:
        return pd.DataFrame(columns=["year", "total_admissions"])

    df_valid["_year"] = df_valid["_year"].astype(int)
    counts = df_valid.groupby("_year").size().reset_index(name="total_admissions")
    counts = counts.rename(columns={"_year": "year"}).sort_values("year").reset_index(drop=True)
    return counts


def task_3(df=None):
    """
    Return Series indexed by gender with average age. If df missing, return empty Series.
    """
    df_local = _get_df_bellevue_safe(df)
    if df_local is None:
        return pd.Series(dtype=float)

    if "gender" not in df_local.columns or "age" not in df_local.columns:
        return pd.Series(dtype=float)

    df_local["gender"] = df_local["gender"].astype("string").str.strip().str.lower()
    df_local["gender"] = df_local["gender"].replace({"m": "male", "f": "female", "man": "male", "woman": "female"})
    df_local["age"] = pd.to_numeric(df_local["age"], errors="coerce")

    result = df_local.dropna(subset=["gender"]).groupby("gender")["age"].mean()
    return result.sort_index()


def task_4(df=None):
    """
    Return list of 5 most common professions (most frequent first).
    If df missing, return empty list.
    """
    df_local = _get_df_bellevue_safe(df)
    if df_local is None:
        return []

    if "profession" not in df_local.columns:
        return []

    prof = df_local["profession"].astype("string").str.strip().str.lower().replace("", pd.NA).dropna()
    if prof.empty:
        return []
    top5 = prof.value_counts().head(5).index.tolist()
    return [s.title() for s in top5]
# --- end snippet ---
