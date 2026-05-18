#!/usr/bin/env python
"""Debug script to trace why merged_readings is empty."""
import sys
sys.path.insert(0, r"c:\Users\stagiaire5\Desktop\coficab_agent-main")

from cable_maintenance_ai.app.db_helpers import (
    get_engine, load_configs, load_current_machine_values, 
    load_parameter_reference_datasheet
)
import pandas as pd
from sqlalchemy import text

# Load configs
configs_df = load_configs()
print(f"✅ Loaded {len(configs_df)} configurations\n")

if len(configs_df) > 0:
    cfg = configs_df.iloc[0]
    print(f"First config:")
    print(f"  ConfigurationId: {cfg['ConfigurationId']}")
    print(f"  MachineCode: {cfg['MachineCode']}")
    print(f"  ConfigurationName: {cfg['ConfigurationName']}")
    print(f"  MonitoringParameters: {type(cfg['MonitoringParameters'])} - {cfg['MonitoringParameters']}")
    print(f"  RecipeParameters: {type(cfg.get('RecipeParameters'))} - {cfg.get('RecipeParameters')}\n")
    
    machine_code = cfg["MachineCode"]
    monitoring_params = list(cfg["MonitoringParameters"] or [])
    recipe_params = list(cfg.get("RecipeParameters", []) or [])
    
    all_params = list(dict.fromkeys(list(recipe_params) + list(monitoring_params)))
    print(f"Combined parameters ({len(all_params)} unique):")
    for i, p in enumerate(all_params[:5]):  # Show first 5
        print(f"  [{i}] {p}")
    if len(all_params) > 5:
        print(f"  ... and {len(all_params) - 5} more")
    print()
    
    # Try loading current values
    print(f"Calling load_current_machine_values({machine_code}, {len(all_params)} params)...")
    latest_values = load_current_machine_values(machine_code, all_params)
    print(f"Returned: {type(latest_values)} with {len(latest_values)} entries")
    if latest_values:
        for param, data in list(latest_values.items())[:3]:
            print(f"  {param}: {data}")
        if len(latest_values) > 3:
            print(f"  ... and {len(latest_values) - 3} more")
    print()
    
    # Check raw MachineTagValue table
    print("Checking raw MachineTagValue table...")
    with get_engine().connect() as c:
        # Check total rows
        count_query = text("""
            SELECT COUNT(*) as cnt, 
                   COUNT(DISTINCT MachineCode) as machines,
                   COUNT(DISTINCT OpcNodeId) as params
            FROM MachineTagValue
        """)
        count_result = pd.read_sql(count_query, c)
        print(f"  Total rows: {count_result['cnt'].iloc[0]}")
        print(f"  Unique machines: {count_result['machines'].iloc[0]}")
        print(f"  Unique parameters: {count_result['params'].iloc[0]}\n")
        
        # Check for our specific machine
        machine_query = text("""
            SELECT TOP 10 MachineCode, OpcNodeId, Value, SourceTimestamp
            FROM MachineTagValue
            WHERE MachineCode = :machine
            ORDER BY SourceTimestamp DESC
        """)
        machine_data = pd.read_sql(machine_query, c, params={"machine": machine_code})
        print(f"  Recent rows for {machine_code}:")
        if not machine_data.empty:
            print(machine_data.to_string())
        else:
            print(f"    ❌ NO DATA for this machine!")
            
            # Check what machines DO have data
            print("\n  Machines with data:")
            machines_query = text("""
                SELECT DISTINCT MachineCode FROM MachineTagValue
            """)
            machines = pd.read_sql(machines_query, c)
            for m in machines['MachineCode'].unique()[:10]:
                print(f"    - {m}")
    print()
    
    # Check parameter reference
    print("Checking parameter_reference_datasheet...")
    ref_df = load_parameter_reference_datasheet(machine_code)
    print(f"  Loaded {len(ref_df)} reference rows")
    if len(ref_df) > 0:
        print(f"  Columns: {list(ref_df.columns)}")
        print("\n  First 3 rows:")
        print(ref_df.head(3).to_string())

