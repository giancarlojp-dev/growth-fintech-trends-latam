"""Upload google_trends_missing_clean.csv to Supabase"""
import pandas as pd
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.load.supabase_loader import upload_dataframe

df = pd.read_csv(project_root / "data" / "processed" / "google_trends_missing_clean.csv")
df['date'] = pd.to_datetime(df['date'])

print(f"📤 Uploading {len(df)} records...")
upload_dataframe(df)
print("✅ Listo")