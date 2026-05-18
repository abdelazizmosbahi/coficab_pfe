"""
Diagnostic utility to help debug the no-data issue in model_page.
"""
import sys
sys.path.insert(0, "cable_maintenance_ai/app")

from db_helpers import get_engine, load_machine_configurations
import pandas as pd
from sqlalchemy import text

def diagnose_machine_parameters():
    """Check what's in the database vs what's in the config."""
    
    # Load configs
    configs = load_machine_configurations()
    if len(configs) == 0:
        print("ERROR: No configurations found!")
        return
    
    cfg = configs.iloc[0]
    machine_code = cfg["MachineCode"]
    monitoring_params = list(cfg["MonitoringParameters"] or [])
    recipe_params = list(cfg.get("RecipeParameters", []) or [])
    
    print("\n" + "=" * 80)
    print(f"CONFIGURATION: {cfg['ConfigurationName']}")
    print(f"MACHINE: {machine_code}")
    print("=" * 80)
    
    print(f"\nConfigured parameters ({len(monitoring_params) + len(recipe_params)} total):")
    print("  Monitoring:", len(monitoring_params))
    print("  Recipe:", len(recipe_params))
    
    # Show first few
    all_params = list(dict.fromkeys(list(recipe_params) + list(monitoring_params)))
    print("\nFirst 5 parameters from config:")
    for p in all_params[:5]:
        print(f"  - {p}")
    
    # Query database
    print(f"\nQuerying MachineTagValue for {machine_code}...")
    
    with get_engine().connect() as conn:
        # Check if machine has any data
        machine_check = text("""
            SELECT COUNT(*) as cnt
            FROM MachineTagValue
            WHERE MachineCode = :mc
        """)
        total = pd.read_sql(machine_check, conn, params={"mc": machine_code})
        total_rows = total['cnt'].iloc[0]
        
        print(f"  Total rows for {machine_code}: {total_rows}")
        
        if total_rows > 0:
            # Get unique parameters
            params_query = text("""
                SELECT DISTINCT OpcNodeId
                FROM MachineTagValue
                WHERE MachineCode = :mc
            """)
            params_in_db = pd.read_sql(params_query, conn, params={"mc": machine_code})
            print(f"  Unique OpcNodeIds in DB: {len(params_in_db)}")
            
            print("\n  First 5 OpcNodeIds in database:")
            for param in params_in_db['OpcNodeId'].head(5):
                print(f"    - {param}")
            
            # Check for matches
            config_set = set(all_params)
            db_set = set(params_in_db['OpcNodeId'].tolist())
            matching = config_set & db_set
            
            print(f"\nParameter matching:")
            print(f"  Config params: {len(config_set)}")
            print(f"  DB params: {len(db_set)}")
            print(f"  Matching: {len(matching)}")
            
            if matching:
                print(f"\n  First few matches:")
                for p in list(matching)[:3]:
                    print(f"    - {p}")
            
            if len(config_set) > len(matching):
                missing = config_set - db_set
                print(f"\n  Missing from DB ({len(missing)}):")
                for p in list(missing)[:3]:
                    print(f"    - {p}")
                if len(missing) > 3:
                    print(f"    ... and {len(missing) - 3} more")
            
            # Sample recent data
            print(f"\nSample recent data:")
            sample = text("""
                SELECT TOP 5 OpcNodeId, Value, SourceTimestamp
                FROM MachineTagValue
                WHERE MachineCode = :mc
                ORDER BY SourceTimestamp DESC
            """)
            data = pd.read_sql(sample, conn, params={"mc": machine_code})
            print(data.to_string(index=False))
        
        else:
            print(f"  ERROR: No data for machine {machine_code}!")
            
            # Try to find what machines DO have data
            all_machines = text("SELECT DISTINCT MachineCode FROM MachineTagValue LIMIT 10")
            machines = pd.read_sql(all_machines, conn)
            print("\n  Machines with data in MachineTagValue:")
            for m in machines['MachineCode']:
                print(f"    - {m}")

if __name__ == "__main__":
    diagnose_machine_parameters()
