import pandas as pd
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Connect to Supabase using Render Environment Variables
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")
supabase = create_client(url, key)

def run_seed():
    try:
        # 1. Load the BPR&D data
        csv_path = os.path.join(os.getcwd(), 'backend', 'laws.csv')
        print(f"Reading file from: {csv_path}")
        
        df = pd.read_csv(csv_path)
        df = df.fillna("Details in summary") # Handle empty cells
        
        # 2. Convert to dictionary
        data = df.to_dict(orient='records')
        print(f"Found {len(data)} rows. Starting upload...")

        # 3. Batch upload (Render/Supabase limit precaution)
        batch_size = 100
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            supabase.table("laws_mapping").insert(batch).execute()
            print(f"✅ Uploaded {i + len(batch)} rows...")

        print("🚀 DATABASE SEEDED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_seed()
