
from pytrends.request import TrendReq
import pandas as pd

def fetch_trends_data(
    keyword: str, 
    country_code: str , 
    timeframe: str = "2019-01-01 2025-01-01"
) -> pd.DataFrame:

    """
    Fetch Google Trends interest over time data for a given keyword and country.

    :param keyword: Search term
    :param country_code: Country code (PE, MX, CO, CL)
    :param timeframe: Time range for analysis
    :return: Cleaned pandas DataFrame
    """
    
    pytrends = TrendReq(hl="en-US", tz=360)

    pytrends.build_payload(
        kw_list=[keyword], 
        geo=country_code,
        timeframe= timeframe
    )
    
    df = pytrends.interest_over_time() 

    if df.empty:
        return pd.DataFrame()

    df = df.reset_index()
    df = df.rename(columns={keyword: "interest_score"})
    
    df["keyword"] = keyword
    df["country_code"] = country_code

    df = df[["date", "keyword", "country_code", "interest_score"]]

    return df