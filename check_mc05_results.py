import os, sys, pandas as pd
from dotenv import load_dotenv
from sqlalchemy import text

_ROOT_DIR = os.getcwd()
load_dotenv(os.path.join(_ROOT_DIR, '.env'))
sys.path.insert(0, _ROOT_DIR)
from db_connection import get_db_engine

engine = get_db_engine()

# Find MC_05 tables
query = """SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'model_schema' AND TABLE_NAME LIKE 'datasheet_MC_05%'
ORDER BY TABLE_NAME DESC"""
df = pd.read_sql(text(query), engine)

print('\n📊 MC_05 Analysis Tables:')
for table_name in df['TABLE_NAME']:
    print(f'  {table_name}')
    
    # Get row count and sample
    count_query = f"SELECT COUNT(*) as cnt FROM [model_schema].[{table_name}]"
    count_df = pd.read_sql(text(count_query), engine)
    row_count = count_df['cnt'].iloc[0]
    print(f'    → {row_count} rows', end='')
    
    if row_count > 0:
        sample_query = f"""
        SELECT TOP 3 ParameterName, MinValue, MeanValue, MaxValue, SampleCount
        FROM [model_schema].[{table_name}]"""
        sample_df = pd.read_sql(text(sample_query), engine)
        print()
        for _, row in sample_df.iterrows():
            print(f"      ✓ {row['ParameterName'][:50]}: min={row['MinValue']:.2f}, mean={row['MeanValue']:.2f}, max={row['MaxValue']:.2f}")
    else:
        print(' (empty)')
