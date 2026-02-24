import pandas as pd

def clean_trends_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """ Clean and transform Google Trends data """
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"])
    df["interest_score"] = df["interest_score"].astype(int)

    # Eliminar duplicados
    df = df.drop_duplicates()
    # Remover datos nengativos
    df = df[df["interest_score"] > 0]
    # Ensure interest_score within 0-100 
    df = df[df["interest_score"] <= 100]
    return df


def filter_incomplete_combinations(df: pd.DataFrame, min_obs: int = 12) -> pd.DataFrame:
    """
    Remove country-keyword combinations with insufficient observations.
    """
    counts = (
        df.groupby(["country_code", "keyword"])
          .size()
          .reset_index(name="count")
    )

    valid = counts[counts["count"] >= min_obs]

    df = df.merge(valid[["country_code", "keyword"]], 
                  on=["country_code", "keyword"], 
                  how="inner")

    return df


def add_zscore(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add z-score per country-keyword combination.
    """
    df["z_score"] = (
        df.groupby(["country_code", "keyword"])["interest_score"]
          .transform(lambda x: (x - x.mean()) / x.std())
    )
    return df


def transform_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full transformation pipeline.
    """
    df = clean_trends_dataframe(df)
    df = filter_incomplete_combinations(df)
    df = add_zscore(df)

    return df