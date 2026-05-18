#!/usr/bin/env python
"""
Standalone diagnostic script to debug NO DATA issue.
Runs the same queries as load_current_machine_values without Streamlit caching.
"""
import sys
sys.path.insert(0, "cable_maintenance_ai/app")

from db_helpers import get_engine
import pandas as pd
from sqlalchemy import text

def diagnose_load_current_machine_values():
    """Test load_current_machine_values logic step by step."""
    
    machine_code = "MC_BU26"
    parameters = [
        "nsu=BN-26;s=BN-26.<Default>.dxx_com.hmi.pviFaultReason",
        "nsu=BN-26;s=BN-26.<Default>.dxx_com.hmi.lineSpeed",
    ]
    
    print("=" * 80)
    print("DIAGNOSTIC: Testing load_current_machine_values logic")
    print("=" * 80)
    print(f"\nMachine: {machine_code}")
    print(f"Parameters to load: {len(parameters)}")
    for i, p in enumerate(parameters):
        print(f"  {i}: {p}")
    
    uniq = list(dict.fromkeys(parameters))
    print(f"\nUnique parameters: {len(uniq)}")
    
    # Step 1: Verify connectivity
    print("\n" + "=" * 80)
    print("STEP 1: Verify database connectivity and data exists")
    print("=" * 80)
    
    test_query = text("SELECT COUNT(*) as cnt FROM MachineTagValue WHERE MachineCode = :machine")
    params_test = {"machine": machine_code}
    
    with get_engine().connect() as c:
        test_df = pd.read_sql(test_query, c, params=params_test)
        total_rows = test_df['cnt'].iloc[0]
        print(f"Total rows in MachineTagValue for {machine_code}: {total_rows}")
        
        if total_rows == 0:
            print("ERROR: No data found for this machine!")
            return
    
    # Step 2: Check what OpcNodeIds exist
    print("\n" + "=" * 80)
    print("STEP 2: Check what OpcNodeIds exist in database")
    print("=" * 80)
    
    with get_engine().connect() as c:
        diag_query = text("SELECT DISTINCT TOP 20 OpcNodeId FROM MachineTagValue WHERE MachineCode = :m ORDER BY OpcNodeId")
        diag_df = pd.read_sql(diag_query, c, params={"m": machine_code})
        
        print(f"Found {len(diag_df)} distinct OpcNodeIds in database:")
        db_params = set(diag_df['OpcNodeId'].tolist())
        for oid in diag_df['OpcNodeId']:
            print(f"  {oid}")
        
        # Check for matches
        config_params = set(uniq)
        matching = db_params & config_params
        missing = config_params - db_params
        
        print(f"\nParameter matching analysis:")
        print(f"  Config has: {len(config_params)} parameters")
        print(f"  DB has: {len(db_params)} OpcNodeIds")
        print(f"  Matching: {len(matching)}")
        
        if matching:
            print(f"\n  MATCHING parameters (will be queried):")
            for m in sorted(matching):
                print(f"    ✓ {m}")
        
        if missing:
            print(f"\n  MISSING from DB (will NOT be queried):")
            for m in sorted(missing):
                print(f"    ✗ {m}")
    
    # Step 3: Try the actual query
    print("\n" + "=" * 80)
    print("STEP 3: Execute the WITH IN clause query")
    print("=" * 80)
    
    params = {"machine": machine_code}
    param_placeholders = []
    for i, p in enumerate(uniq):
        param_key = f"p{i}"
        params[param_key] = p
        param_placeholders.append(f":{param_key}")
    
    in_clause = "(" + ", ".join(param_placeholders) + ")"
    query = f"""
        SELECT TOP 1000 OpcNodeId, Value, SourceTimestamp
        FROM MachineTagValue
        WHERE MachineCode = :machine AND OpcNodeId IN {in_clause}
        ORDER BY SourceTimestamp DESC
    """
    
    print(f"Query: SELECT TOP 1000 OpcNodeId, Value, SourceTimestamp FROM MachineTagValue")
    print(f"WHERE MachineCode = :machine AND OpcNodeId IN {in_clause}")
    print(f"\nParameters:")
    for key, val in params.items():
        if key != "machine":
            print(f"  {key} = {val}")
    
    with get_engine().connect() as c:
        df = pd.read_sql(text(query), c, params=params)
    
    print(f"\nQuery returned {len(df)} rows")
    if not df.empty:
        print(f"Columns: {list(df.columns)}")
        print(f"\nFirst 5 rows:")
        print(df.head(10).to_string(index=False))
    else:
        print("ERROR: Query returned no rows!")
        return
    
    # Step 4: Group by latest
    print("\n" + "=" * 80)
    print("STEP 4: Get latest value per OpcNodeId")
    print("=" * 80)
    
    df_latest = df.loc[df.groupby('OpcNodeId')['SourceTimestamp'].idxmax()]
    print(f"After grouping: {len(df_latest)} rows (should be 1 per unique OpcNodeId)")
    
    if df_latest.empty:
        print("ERROR: No rows after grouping!")
        return
    
    # Step 5: Build result
    print("\n" + "=" * 80)
    print("STEP 5: Build result dictionary")
    print("=" * 80)
    
    result = {}
    for _, row in df_latest.iterrows():
        param = row["OpcNodeId"]
        value = row["Value"]
        timestamp = row["SourceTimestamp"]
        
        print(f"\nProcessing {param}:")
        print(f"  Raw value: {value} (type={type(value).__name__})")
        print(f"  Timestamp: {timestamp}")
        
        # Convert to float
        if pd.notna(value):
            try:
                float_val = float(value)
                print(f"  -> Converted to float: {float_val}")
            except (ValueError, TypeError) as ve:
                print(f"  -> ERROR converting to float: {ve}")
                float_val = None
        else:
            print(f"  -> Value is NaN/None")
            float_val = None
        
        result[param] = {
            "value": float_val,
            "timestamp": timestamp,
        }
    
    print(f"\n" + "=" * 80)
    print(f"FINAL RESULT: {len(result)} entries")
    print("=" * 80)
    for param, data in result.items():
        print(f"{param}: {data}")

if __name__ == "__main__":
    diagnose_load_current_machine_values()
