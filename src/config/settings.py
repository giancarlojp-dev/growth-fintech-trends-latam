import os 

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Paths
RAW_PATH = os.path.join(BASE_DIR, "data/raw/google_trends_master.csv")
PROCESSED_PATH = os.path.join(BASE_DIR, "data/processed/google_trends_clean.csv")

