
from pytrends.request import TrendReq
import pandas as pd
import time 
import random

def fetch_trends_data(
    keyword: str, 
    country_code: str , 
    timeframe: str = "2019-01-01 2025-01-01",
    retries: int = 3
) -> pd.DataFrame: 

    """Fetch Google Trends interest over time data for a given keyword and country.
        :param keyword: Search term
        :param country_code: Country code (PE, MX, CO, CL)
        :param timeframe: Time range for analysis
        :return: Cleaned pandas DataFrame """
    for attempt in range(retries):
        try: 
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
        
        except Exception as e:
            if "429" in str(e):
                sleep_time = random.uniform(20, 40)
                print(f"Rate limit hit. Waiting for {sleep_time:.1f} seconds before retrying...")
                time.sleep(sleep_time)
            else:
                raise e
            
    return pd.DataFrame()
