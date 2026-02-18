import pandas as pd

def clean_trends_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    """
    Clean and transform Google Trends data """
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

