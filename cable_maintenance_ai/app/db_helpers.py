"""
Shared MySQL data loading helpers for all app pages.

Every loader is @st.cache_data decorated so multiple pages share the same in-process
cache.  Column aliases keep backward compatibility with code written against the
old CSV files.
"""

import json
import os
import sys
import requests
from datetime import datetime

import pandas as pd
import numpy as np
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import text

# Project root is three levels up: pages/ -> app/ -> cable_maintenance_ai/ -> root
_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(_ROOT_DIR, ".env"))
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from db_connection import get_db_engine as _engine_factory  # noqa: E402


@st.cache_resource
def get_engine():
    """Cached SQLAlchemy engine shared across all pages."""
    engine = _engine_factory()
    if engine is None:
        st.error(
            "❌ Database connection failed. "
            "Check your .env credentials (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)."
        )
        st.stop()
    return engine


# ── recipe_parameters ────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_recipe_parameters_df() -> pd.DataFrame:
    """
    Load all distinct parameters from MachineTagValue with calculated statistics.
    
    Returns DataFrame with columns: RecipeId, RecipeName, Machine, Parameter, Value,
    DataType, OpcNodeId, Unit, MinValue, MaxValue, SamplingMs, Min, Mean, Max
    
    Since we're now using MachineTagValue as source of truth:
    - RecipeId/RecipeName left empty (no recipe auto-detection)
    - Min/Mean/Max calculated from value statistics
    - Unit left empty (not available in MachineTagValue)
    """
    try:
        with get_engine().connect() as c:
            # Get all distinct OpcNodeIds with their statistics grouped by Machine
            df = pd.read_sql(
                text(
                    "SELECT TOP 20 "
                    "  MachineCode AS Machine, "
                    "  OpcNodeId, "
                    "  MIN(Value) as Min, "
                    "  MAX(Value) as Max, "
                    "  AVG(Value) as Mean, "
                    "  COUNT(*) as sample_count "
                    "FROM (SELECT TOP 20 MachineCode, OpcNodeId, Value FROM MachineTagValue ORDER BY SourceTimestamp DESC) AS recent "
                    "GROUP BY MachineCode, OpcNodeId "
                    "ORDER BY MachineCode, OpcNodeId"
                ),
                c,
            )
        
        if df.empty:
            return pd.DataFrame()
        
        # Convert OpcNodeId to parameter name for display (do not strip recipe markers)
        df['Parameter'] = df['OpcNodeId'].str.replace('_ACT', '', regex=False)
        
        # No recipe auto-detection
        df['RecipeId'] = ''
        df['RecipeName'] = ''
        
        # Add placeholder columns to match expected schema
        df['Value'] = df['Mean']  # Current value is mean
        df['DataType'] = 'FLOAT'  # Default data type
        df['Unit'] = ''  # Unit not available in MachineTagValue
        df['MinValue'] = df['Min']
        df['MaxValue'] = df['Max']
        df['SamplingMs'] = 20  # Default sampling interval
        
        # Return only the expected columns in the correct order
        result = df[[
            'RecipeId', 'RecipeName', 'Machine', 'Parameter', 'Value',
            'DataType', 'OpcNodeId', 'Unit', 'MinValue', 'MaxValue', 'SamplingMs',
            'Min', 'Mean', 'Max'
        ]].copy()
        
        return result.sort_values(['Machine', 'RecipeId', 'Parameter']).reset_index(drop=True)
    
    except Exception as e:
        st.warning(f"Error loading recipe parameters from database: {str(e)}")
        return pd.DataFrame()



# ── tags_mapping ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_tags_mapping_df() -> pd.DataFrame:
    """
    Load tags_mapping table.

    Aliases MachineCode → Machine and Parameter → Tag so the existing page code
    (which accesses tags_mapping['Machine'] and tags_mapping['Tag']) keeps working.
    """
    with get_engine().connect() as c:
        df = pd.read_sql(
            text(
                "SELECT MachineCode AS Machine, Parameter AS Tag, "
                "MachineCode, Parameter "
                "FROM tags_mapping "
                "ORDER BY MachineCode, Parameter"
            ),
            c,
        )
    return df


# ── productionrun ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_production_runs_df() -> pd.DataFrame:
    """
    Load the productionrun table.  Returns at minimum RunId and MachineCode columns
    so the pages that call production_runs['MachineCode'] keep working.
    """
    with get_engine().connect() as c:
        df = pd.read_sql(
            text(
                "SELECT [RunId], [MachineCode], [ScopeKey], [StartTs], [EndTs], [Status] "
                "FROM [dbo].[productionrun] "
                "ORDER BY [RunId]"
            ),
            c,
        )
    return df


# ── MachineTagValue helpers ───────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_distinct_run_ids(machine_code: str | None = None) -> list[str]:
    """Return distinct ProductionRunId values, optionally filtered by machine."""
    q = (
        "SELECT DISTINCT ProductionRunId FROM MachineTagValue "
        + ("WHERE MachineCode = :m " if machine_code else "")
        + "ORDER BY ProductionRunId"
    )
    params = {"m": machine_code} if machine_code else {}
    with get_engine().connect() as c:
        df = pd.read_sql(text(q), c, params=params)
    return df["ProductionRunId"].dropna().tolist()


@st.cache_data(ttl=60)
def load_sensor_trace(run_id: str, opc_node_id: str) -> pd.DataFrame:
    """Return time-series rows for one (ProductionRunId, OpcNodeId) pair."""
    with get_engine().connect() as c:
        df = pd.read_sql(
            text(
                "SELECT SourceTimestamp AS Timestamp, Value "
                "FROM MachineTagValue "
                "WHERE ProductionRunId = :run AND OpcNodeId = :param "
                "ORDER BY SourceTimestamp"
            ),
            c,
            params={"run": run_id, "param": opc_node_id},
        )
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    return df


@st.cache_data(ttl=300)
def load_available_parameters_for_run(run_id: str) -> list[str]:
    """Return list of OpcNodeId values that have data in the given run."""
    with get_engine().connect() as c:
        df = pd.read_sql(
            text(
                "SELECT DISTINCT OpcNodeId "
                "FROM MachineTagValue "
                "WHERE ProductionRunId = :run "
                "ORDER BY OpcNodeId"
            ),
            c,
            params={"run": run_id},
        )
    return df["OpcNodeId"].tolist() if not df.empty else []


# ── Stable-window extraction helpers ──────────────────────────────────────────
@st.cache_data(ttl=300)
def load_parameter_optimal_windows() -> pd.DataFrame:
    """Load learned startup/shutdown exclusion windows per parameter from model_schema."""
    try:
        with get_engine().connect() as c:
            df = pd.read_sql(
                text(
                    "SELECT OpcNodeId, startup_skip_sec, shutdown_skip_sec, "
                    "stable_ratio, score, n_run_samples "
                    "FROM [model_schema].[parameter_optimal_windows]"
                ),
                c,
            )
        return df
    except Exception:
        return pd.DataFrame()


def rebuild_step_signal(events_df, t0, t1, resample_sec=1):
    """Forward-fill event-based sensor data to create continuous step signal."""
    import numpy as np
    
    if events_df.empty or t0 is None or t1 is None:
        return pd.DataFrame(columns=['Timestamp', 'Value'])

    # Keep one anchor point before t0 so forward-fill has a valid starting value
    before = events_df[events_df['Timestamp'] <= t0].tail(1)
    inside = events_df[(events_df['Timestamp'] >= t0) & (events_df['Timestamp'] <= t1)]

    merged = pd.concat([before, inside], ignore_index=True).drop_duplicates('Timestamp', keep='last')
    if merged.empty:
        return pd.DataFrame(columns=['Timestamp', 'Value'])

    idx = pd.date_range(start=t0, end=t1, freq=f'{int(resample_sec)}s')
    if len(idx) < 2:
        return pd.DataFrame(columns=['Timestamp', 'Value'])

    s = merged.set_index('Timestamp')['Value'].sort_index()
    s = s.reindex(s.index.union(idx)).sort_index().ffill().reindex(idx)

    out = pd.DataFrame({'Timestamp': idx, 'Value': s.values})
    out = out.dropna(subset=['Value']).reset_index(drop=True)
    return out


def detect_stable_points(step_df, hold_sec=15, abs_eps=1e-6, rel_eps=0.002):
    """Identify stable regions where value change is within tolerance."""
    import numpy as np
    
    if step_df.empty:
        return step_df.assign(dv=np.nan, tol=np.nan, stable=False)

    df = step_df.copy()
    df['prev'] = df['Value'].shift(1)
    df['dv'] = (df['Value'] - df['prev']).abs()
    df['tol'] = np.maximum(abs_eps, rel_eps * df['Value'].abs().clip(lower=1e-9))

    window = max(2, int(hold_sec))
    rolling_max_dv = df['dv'].fillna(np.inf).rolling(window=window, min_periods=window).max()
    rolling_max_tol = df['tol'].rolling(window=window, min_periods=window).max()
    df['stable'] = (rolling_max_dv <= rolling_max_tol).fillna(False)

    return df.drop(columns=['prev'])


# ── OPC UA Real-Time Monitoring Helpers ──────────────────────────────────────
LINESPEED_FRESHNESS_SECONDS = 3


@st.cache_data(ttl=10)
def load_working_machines() -> list[str]:
    """
    Return sorted list of machines that have data in MachineTagValue.
    Machine is "working" if it appears in the table.
    """
    try:
        with get_engine().connect() as c:
            df = pd.read_sql(
                text(
                    "SELECT DISTINCT MachineCode "
                    "FROM MachineTagValue "
                    "WHERE MachineCode IS NOT NULL "
                    "ORDER BY MachineCode"
                ),
                c,
            )
        return df["MachineCode"].tolist() if not df.empty else []
    except Exception:
        return []


@st.cache_data(ttl=10)
def load_all_machines() -> list[str]:
    """Return sorted list of all machines in MachineTagValue table."""
    try:
        with get_engine().connect() as c:
            df = pd.read_sql(
                text(
                    "SELECT DISTINCT MachineCode "
                    "FROM MachineTagValue "
                    "ORDER BY MachineCode"
                ),
                c,
            )
        return df["MachineCode"].tolist() if not df.empty else []
    except Exception:
        return []


@st.cache_data(ttl=300)
def load_recipe_parameters_for_machine(machine_code: str) -> pd.DataFrame:
    """
    Deprecated: Recipe parameters are no longer auto-detected.
    Returns an empty DataFrame for backward compatibility.
    """
    return pd.DataFrame()


@st.cache_data(ttl=300)
def load_distinct_recipes_for_machine(machine_code: str) -> list[str]:
    """
    Deprecated: Recipe parameters are no longer auto-detected.
    Returns an empty list for backward compatibility.
    """
    return []


@st.cache_data(ttl=300)
def load_parameters_for_machine_recipe(machine_code: str, recipe_id: str) -> dict:
    """
    Load all parameters for a specific machine and recipe.
    Returns dict: {opc_node_id: {min, max, mean, value, unit, param_name, is_recipe}}
    
    The recipe_id is the selected recipe OpcNodeId.
    This returns all parameters for the machine (not filtered by recipe).
    """
    try:
        # Load all parameters for the machine
        all_params = load_all_parameters_for_machine_with_ranges(machine_code)
        return all_params
    except Exception:
        return {}



@st.cache_data(ttl=60)
def load_all_parameters_for_machine(machine_code: str) -> list[str]:
    """Return all distinct OpcNodeId values for a machine."""
    try:
        with get_engine().connect() as c:
            df = pd.read_sql(
                text(
                    "SELECT DISTINCT OpcNodeId "
                    "FROM MachineTagValue "
                    "WHERE MachineCode = :m "
                    "ORDER BY OpcNodeId"
                ),
                c,
                params={"m": machine_code},
            )
        return df["OpcNodeId"].tolist() if not df.empty else []
    except Exception:
        return []


@st.cache_data(ttl=300)
def load_all_parameters_for_machine_with_ranges(machine_code: str) -> dict:
    """
    Load ALL parameters for a machine with their min/max/mean ranges.
    Returns dict: {opc_node_id: {min, max, mean, value, unit, param_name}}
    
    This is used when user selects a recipe - they see all available parameters
    for that machine to choose from for monitoring.
    """
    try:
        with get_engine().connect() as c:
                # Get TOP 20 most recent rows per parameter for the machine
                df = pd.read_sql(
                    text(
                        "SELECT "
                        "  OpcNodeId, "
                        "  MIN(Value) as min_val, "
                        "  MAX(Value) as max_val, "
                        "  AVG(Value) as mean_val, "
                        "  COUNT(*) as count "
                        "FROM (SELECT TOP 20 OpcNodeId, Value FROM MachineTagValue "
                        "WHERE MachineCode = :m "
                        "ORDER BY SourceTimestamp DESC) AS recent "
                ),
                c,
                params={"m": machine_code},
            )
        
        if df.empty:
            return {}
        
        # Build parameter info dict
        params_dict = {}
        for _, row in df.iterrows():
            opc_node = row["OpcNodeId"]
            min_val = float(row["min_val"]) if pd.notna(row["min_val"]) else 0.0
            max_val = float(row["max_val"]) if pd.notna(row["max_val"]) else 1.0
            mean_val = float(row["mean_val"]) if pd.notna(row["mean_val"]) else (min_val + max_val) / 2
            
            # Clean parameter name for display
            param_name = opc_node.replace('_recipe', '').replace('_ACT', '').replace('_', ' ')
            
            params_dict[opc_node] = {
                'min': min_val,
                'max': max_val,
                'mean': mean_val,
                'value': mean_val,
                'unit': '',
                'opc_node': opc_node,
                'param_name': param_name,
                'is_recipe': False
            }
        
        return params_dict
    except Exception:
        return {}


# ── Machine Configuration Helpers ────────────────────────────────────────────
def initialize_machine_configuration_table():
    """Create model_schema schema and machine_configuration table if they don't exist."""
    try:
        with get_engine().connect() as c:
            # Step 1: Create schema if it doesn't exist
            try:
                c.execute(text("""
                    IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'model_schema')
                    BEGIN
                        EXEC('CREATE SCHEMA [model_schema]')
                    END
                """))
                c.commit()
            except Exception as schema_err:
                try:
                    c.rollback()
                except:
                    pass
                # Schema might already exist, continue
            
            # Step 2: Create table if it doesn't exist
            c.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.tables t 
                              JOIN sys.schemas s ON t.schema_id = s.schema_id 
                              WHERE t.name = 'machine_configuration' AND s.name = 'model_schema')
                CREATE TABLE [model_schema].[machine_configuration] (
                    [ConfigurationId] INT IDENTITY(1,1) PRIMARY KEY,
                    [ConfigurationName] VARCHAR(255) NOT NULL,
                    [MachineCode] VARCHAR(100) NOT NULL,
                    [MonitoringParameters] NVARCHAR(MAX) NOT NULL,
                    [RecipeParameters] NVARCHAR(MAX) NOT NULL,
                    [Description] TEXT,
                    [IsActive] BIT DEFAULT 1,
                    [CreatedAt] DATETIME DEFAULT GETDATE(),
                    [UpdatedAt] DATETIME DEFAULT GETDATE(),
                    CONSTRAINT [unique_config_name] UNIQUE ([ConfigurationName], [MachineCode]),
                    INDEX [idx_machine] ([MachineCode]),
                    INDEX [idx_active] ([IsActive])
                )
            """))
            c.commit()
    except Exception as e:
        pass  # Table likely already exists


@st.cache_data(ttl=300)
def load_machine_configurations(machine_code: str | None = None) -> pd.DataFrame:
    """Load all machine configurations, optionally filtered by machine."""
    try:
        initialize_machine_configuration_table()
        
        query = """
            SELECT 
                ConfigurationId,
                ConfigurationName,
                MachineCode,
                MonitoringParameters,
                RecipeParameters,
                Description,
                IsActive,
                CreatedAt,
                UpdatedAt
            FROM [model_schema].[machine_configuration]
        """
        
        if machine_code:
            query += " WHERE MachineCode = :m"
        
        query += " ORDER BY ConfigurationName"
        
        with get_engine().connect() as c:
            params = {"m": machine_code} if machine_code else {}
            df = pd.read_sql(text(query), c, params=params)
        
        # Parse JSON columns
        if not df.empty:
            df['MonitoringParameters'] = df['MonitoringParameters'].apply(
                lambda x: json.loads(x) if isinstance(x, str) else x if isinstance(x, list) else []
            )
            df['RecipeParameters'] = df['RecipeParameters'].apply(
                lambda x: json.loads(x) if isinstance(x, str) else x if isinstance(x, list) else []
            )
        
        return df
    except Exception as e:
        st.warning(f"Error loading machine configurations: {str(e)}")
        return pd.DataFrame()


def add_machine_configuration(config_name: str, machine_code: str, 
                             monitoring_params: list, recipe_params: list, 
                             description: str = "") -> bool:
    """Add a new machine configuration."""
    try:
        import json
        
        initialize_machine_configuration_table()
        
        with get_engine().connect() as c:
            c.execute(text("""
                INSERT INTO [model_schema].[machine_configuration]
                (ConfigurationName, MachineCode, MonitoringParameters, RecipeParameters, Description, IsActive)
                VALUES (:name, :machine, :monitoring, :recipe, :desc, 1)
            """), {
                "name": config_name,
                "machine": machine_code,
                "monitoring": json.dumps(monitoring_params),
                "recipe": json.dumps(recipe_params),
                "desc": description
            })
            c.commit()
        
        # Clear cache after insert
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error adding configuration: {str(e)}")
        return False


def update_machine_configuration(config_id: int, config_name: str, machine_code: str,
                                monitoring_params: list, recipe_params: list,
                                description: str = "", is_active: bool = True) -> bool:
    """Update an existing machine configuration."""
    try:
        import json
        
        initialize_machine_configuration_table()
        
        with get_engine().connect() as c:
            c.execute(text("""
                UPDATE [model_schema].[machine_configuration]
                SET ConfigurationName = :name,
                    MachineCode = :machine,
                    MonitoringParameters = :monitoring,
                    RecipeParameters = :recipe,
                    Description = :desc,
                    IsActive = :active
                WHERE ConfigurationId = :id
            """), {
                "id": config_id,
                "name": config_name,
                "machine": machine_code,
                "monitoring": json.dumps(monitoring_params),
                "recipe": json.dumps(recipe_params),
                "desc": description,
                "active": 1 if is_active else 0
            })
            c.commit()
        
        # Clear cache after update
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error updating configuration: {str(e)}")
        return False


def delete_machine_configuration(config_id: int) -> bool:
    """Delete a machine configuration."""
    try:
        initialize_machine_configuration_table()
        
        with get_engine().connect() as c:
            c.execute(text("""
                DELETE FROM [model_schema].[machine_configuration]
                WHERE ConfigurationId = :id
            """), {"id": int(config_id)})
            c.commit()
        
        # Clear cache after delete
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error deleting configuration: {str(e)}")
        return False


def get_machine_configuration_by_id(config_id: int) -> dict:
    """Get a specific configuration by ID."""
    try:
        import json
        
        initialize_machine_configuration_table()
        
        with get_engine().connect() as c:
            df = pd.read_sql(text("""
                SELECT *
                FROM [model_schema].[machine_configuration]
                WHERE ConfigurationId = :id
            """), c, params={"id": config_id})
        
        if df.empty:
            return None
        
        row = df.iloc[0]
        return {
            'ConfigurationId': row['ConfigurationId'],
            'ConfigurationName': row['ConfigurationName'],
            'MachineCode': row['MachineCode'],
            'MonitoringParameters': json.loads(row['MonitoringParameters']) if isinstance(row['MonitoringParameters'], str) else row['MonitoringParameters'],
            'RecipeParameters': json.loads(row['RecipeParameters']) if isinstance(row['RecipeParameters'], str) else row['RecipeParameters'],
            'Description': row['Description'],
            'IsActive': row['IsActive']
        }
    except Exception as e:
        st.error(f"Error retrieving configuration: {str(e)}")
        return None


# ── Report and Analysis Storage Helpers ──────────────────────────────────────
@st.cache_data(ttl=3600)
def load_configuration_reports(limit: int = 10) -> pd.DataFrame:
    """Load recent configuration reports from model_schema."""
    try:
        with get_engine().connect() as c:
            df = pd.read_sql(text("""
                SELECT ReportId, ReportName, ReportType, ProcessedRows, GeneratedAt, Summary
                FROM [model_schema].[configuration_reports]
                ORDER BY GeneratedAt DESC
                LIMIT :limit
            """), c, params={"limit": limit})
        
        if not df.empty:
            df['Summary'] = df['Summary'].apply(
                lambda x: json.loads(x) if isinstance(x, str) else x if isinstance(x, dict) else {}
            )
        
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_coverage_analysis_results() -> pd.DataFrame:
    """Load coverage analysis results from model_schema."""
    try:
        with get_engine().connect() as c:
            df = pd.read_sql(text("""
                SELECT ConfigurationName, MachineCode, AvailableTags, MonitoredTags,
                       RecipeTags, CoveragePct, RecipePct, AnalyzedAt
                FROM [model_schema].[coverage_analysis_results]
                ORDER BY AnalyzedAt DESC
            """), c)
        return df
    except Exception:
        return pd.DataFrame()


# ── Machine Status Helpers ───────────────────────────────────────────────────
def check_machine_active_status(machine_code: str, active_window_seconds: int | None = None) -> bool:
    """
    Check if a machine has recent data in MachineTagValue.
    Machine is considered "active" if it has linespeed data within the time window.
    
    Args:
        machine_code: Machine code to check
        active_window_seconds: Time window in seconds. If None uses LINESPEED_FRESHNESS_SECONDS.
        
    Returns:
        True if machine has recent linespeed data, False otherwise
    """
    if active_window_seconds is None:
        active_window_seconds = LINESPEED_FRESHNESS_SECONDS
    try:
        with get_engine().connect() as c:
            df = pd.read_sql(text("""
                SELECT TOP 1 Value, SourceTimestamp
                FROM MachineTagValue
                WHERE MachineCode = :m
                  AND LOWER(OpcNodeId) LIKE '%linespeed%'
                ORDER BY SourceTimestamp DESC
            """), c, params={"m": machine_code})
        
        if df.empty:
            return False
        
        ts = df.iloc[0]['SourceTimestamp']
        if ts is None:
            return False
        
        now = datetime.utcnow()
        if hasattr(ts, 'tzinfo') and ts.tzinfo is not None:
            ts = ts.replace(tzinfo=None)
        age = (now - ts).total_seconds()
        return age <= active_window_seconds
    except Exception:
        return False


def get_machine_status_by_linespeed() -> dict:
    """
    Get machine status based on LineSpeed value and data freshness.
    
    A machine is considered:
    - Working (active=True):  linespeed > 0 AND SourceTimestamp within freshness window
    - Standby (active=False): linespeed == 0 or NULL AND data is fresh
    - Inactive (active=False): no linespeed data OR data is stale
    
    Freshness window: LINESPEED_FRESHNESS_SECONDS (currently 3 seconds)
    
    Returns:
        dict: {
            machine_code: {
                'status': '🟢 Working'|'🟡 Standby'|'🔴 Inactive',
                'active': bool,
                'linespeed_value': float|None,
                'linespeed_timestamp': str|None,
                'linespeed_age_seconds': float|None
            }
        }
    """
    try:
        all_machines = load_all_machines()
        status_dict = {}
        now = datetime.utcnow()

        for machine in all_machines:
            with get_engine().connect() as c:
                df = pd.read_sql(text("""
                    SELECT TOP 1 Value, SourceTimestamp
                    FROM MachineTagValue
                    WHERE MachineCode = :machine
                      AND LOWER(OpcNodeId) LIKE '%linespeed%'
                    ORDER BY SourceTimestamp DESC
                """), c, params={"machine": machine})

            if df.empty:
                status_dict[machine] = {
                    'status': '🔴 Inactive',
                    'active': False,
                    'linespeed_value': None,
                    'linespeed_timestamp': None,
                    'linespeed_age_seconds': None
                }
            else:
                try:
                    linespeed_value = float(df.iloc[0]['Value'])
                    ts = df.iloc[0]['SourceTimestamp']

                    if ts is None:
                        status_dict[machine] = {
                            'status': '🔴 Inactive',
                            'active': False,
                            'linespeed_value': linespeed_value,
                            'linespeed_timestamp': None,
                            'linespeed_age_seconds': None
                        }
                    else:
                        if hasattr(ts, 'tzinfo') and ts.tzinfo is not None:
                            ts = ts.replace(tzinfo=None)
                        age_seconds = (now - ts).total_seconds()
                        ts_str = ts.strftime('%Y-%m-%d %H:%M:%S')
                        is_fresh = age_seconds <= LINESPEED_FRESHNESS_SECONDS

                        if not is_fresh:
                            status_dict[machine] = {
                                'status': '🔴 Inactive',
                                'active': False,
                                'linespeed_value': linespeed_value,
                                'linespeed_timestamp': ts_str,
                                'linespeed_age_seconds': round(age_seconds, 1)
                            }
                        elif linespeed_value > 0:
                            status_dict[machine] = {
                                'status': '🟢 Working',
                                'active': True,
                                'linespeed_value': linespeed_value,
                                'linespeed_timestamp': ts_str,
                                'linespeed_age_seconds': round(age_seconds, 1)
                            }
                        else:
                            status_dict[machine] = {
                                'status': '🟡 Standby',
                                'active': False,
                                'linespeed_value': linespeed_value,
                                'linespeed_timestamp': ts_str,
                                'linespeed_age_seconds': round(age_seconds, 1)
                            }
                except (ValueError, TypeError):
                    status_dict[machine] = {
                        'status': '🔴 Inactive',
                        'active': False,
                        'linespeed_value': None,
                        'linespeed_timestamp': None,
                        'linespeed_age_seconds': None
                    }

        return status_dict
    except Exception:
        return {}


def get_machine_status_for(machine_code: str) -> dict:
    """
    Get status for a single machine based on its latest linespeed data freshness.
    More efficient than calling get_machine_status_by_linespeed() when only one
    machine is needed (e.g. in live monitoring fragments).
    
    Returns the same dict structure as get_machine_status_by_linespeed() for a
    single machine_code entry:
        {
            'status': '🟢 Working'|'🟡 Standby'|'🔴 Inactive',
            'active': bool,
            'linespeed_value': float|None,
            'linespeed_timestamp': str|None,
            'linespeed_age_seconds': float|None
        }
    """
    try:
        now = datetime.utcnow()
        with get_engine().connect() as c:
            df = pd.read_sql(text("""
                SELECT TOP 1 Value, SourceTimestamp
                FROM MachineTagValue
                WHERE MachineCode = :machine
                  AND LOWER(OpcNodeId) LIKE '%linespeed%'
                ORDER BY SourceTimestamp DESC
            """), c, params={"machine": machine_code})

        if df.empty:
            return {
                'status': '🔴 Inactive',
                'active': False,
                'linespeed_value': None,
                'linespeed_timestamp': None,
                'linespeed_age_seconds': None
            }

        linespeed_value = float(df.iloc[0]['Value'])
        ts = df.iloc[0]['SourceTimestamp']

        if ts is None:
            return {
                'status': '🔴 Inactive',
                'active': False,
                'linespeed_value': linespeed_value,
                'linespeed_timestamp': None,
                'linespeed_age_seconds': None
            }

        if hasattr(ts, 'tzinfo') and ts.tzinfo is not None:
            ts = ts.replace(tzinfo=None)
        age_seconds = (now - ts).total_seconds()
        ts_str = ts.strftime('%Y-%m-%d %H:%M:%S')
        is_fresh = age_seconds <= LINESPEED_FRESHNESS_SECONDS

        if not is_fresh:
            return {
                'status': '🔴 Inactive',
                'active': False,
                'linespeed_value': linespeed_value,
                'linespeed_timestamp': ts_str,
                'linespeed_age_seconds': round(age_seconds, 1)
            }
        elif linespeed_value > 0:
            return {
                'status': '🟢 Working',
                'active': True,
                'linespeed_value': linespeed_value,
                'linespeed_timestamp': ts_str,
                'linespeed_age_seconds': round(age_seconds, 1)
            }
        else:
            return {
                'status': '🟡 Standby',
                'active': False,
                'linespeed_value': linespeed_value,
                'linespeed_timestamp': ts_str,
                'linespeed_age_seconds': round(age_seconds, 1)
            }
    except Exception:
        return {
            'status': '🔴 Inactive',
            'active': False,
            'linespeed_value': None,
            'linespeed_timestamp': None,
            'linespeed_age_seconds': None
        }


def get_machine_active_status_dict(active_window_seconds: int | None = None) -> dict:
    """
    Get active/inactive status for all machines based on linespeed data freshness.
    
    Args:
        active_window_seconds: Time window in seconds to consider machine active.
                             If None, uses LINESPEED_FRESHNESS_SECONDS.
    
    Returns:
        dict: {machine_code: {'status': 'Active'|'Standby'|'Inactive', 'active': bool}}
    """
    if active_window_seconds is None:
        active_window_seconds = LINESPEED_FRESHNESS_SECONDS
    
    try:
        all_machines = load_all_machines()
        status_dict = {}
        now = datetime.utcnow()
        
        for machine in all_machines:
            with get_engine().connect() as c:
                df = pd.read_sql(text("""
                    SELECT TOP 1 Value, SourceTimestamp
                    FROM MachineTagValue
                    WHERE MachineCode = :m
                      AND LOWER(OpcNodeId) LIKE '%linespeed%'
                    ORDER BY SourceTimestamp DESC
                """), c, params={"m": machine})
            
            if df.empty:
                status_dict[machine] = {
                    'status': '🔴 Inactive',
                    'active': False
                }
            else:
                try:
                    linespeed_value = float(df.iloc[0]['Value'])
                    ts = df.iloc[0]['SourceTimestamp']

                    if ts is None:
                        status_dict[machine] = {
                            'status': '🔴 Inactive',
                            'active': False
                        }
                    else:
                        if hasattr(ts, 'tzinfo') and ts.tzinfo is not None:
                            ts = ts.replace(tzinfo=None)
                        age = (now - ts).total_seconds()

                        if age > active_window_seconds:
                            status_dict[machine] = {
                                'status': '🔴 Inactive',
                                'active': False
                            }
                        elif linespeed_value > 0:
                            status_dict[machine] = {
                                'status': '🟢 Active',
                                'active': True
                            }
                        else:
                            status_dict[machine] = {
                                'status': '🟡 Standby',
                                'active': False
                            }
                except (ValueError, TypeError):
                    status_dict[machine] = {
                        'status': '🔴 Inactive',
                        'active': False
                    }
        
        return status_dict
    except Exception:
        return {}


# ── Mistral AI Integration ───────────────────────────────────────────────────
def call_mistral_ai(query: str, context: str = "") -> str:
    """
    Call Mistral AI API for root cause analysis and explanations.
    
    Args:
        query: The question/prompt to send to Mistral
        context: Additional context to include in the prompt
        
    Returns:
        Response from Mistral API
    """
    try:
        import requests
        
        api_key = os.getenv('MISTRAL_API_KEY')
        model = os.getenv('MISTRAL_MODEL', 'mistral-small-latest')
        
        if not api_key:
            return "⚠️ Mistral AI API key not configured in .env"
        
        # Strip whitespace from API key
        api_key = api_key.strip()
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        full_prompt = f"{context}\n\n{query}" if context else query
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                return "❌ No response from Mistral AI"
        else:
            # Try to get more details from error response
            try:
                error_details = response.json()
                error_msg = error_details.get('message', f'HTTP {response.status_code}')
                return f"❌ Mistral API error: {error_msg}"
            except:
                return f"❌ Mistral API error: {response.status_code}\n{response.text}"
    
    except Exception as e:
        return f"❌ Error calling Mistral AI: {str(e)}"


def analyze_parameter_anomaly(machine_code: str, parameter: str, current_value: float,
                             min_val: float, max_val: float, status: str) -> str:
    """
    Use Mistral AI to generate root cause analysis for parameter anomalies.
    
    Args:
        machine_code: Machine being monitored
        parameter: Parameter name
        current_value: Current parameter value
        min_val: Minimum acceptable value
        max_val: Maximum acceptable value  
        status: Current status (contains 'OK' for in-range, otherwise out-of-range)
        
    Returns:
        Root cause analysis from Mistral AI
    """
    # Check if parameter is within range (status may contain emoji or text)
    if 'OK' in status or (min_val <= current_value <= max_val):
        return "✅ Parameter within acceptable range"
    
    # Determine if value is above or below range
    if current_value < min_val:
        out_of_range_type = f"BELOW MINIMUM ({min_val})"
    elif current_value > max_val:
        out_of_range_type = f"ABOVE MAXIMUM ({max_val})"
    else:
        out_of_range_type = "OUT OF RANGE"
    
    context = f"""
    Manufacturing System Alert: Cable Maintenance AI
    Machine: {machine_code}
    Parameter: {parameter}
    Current Value: {current_value}
    
    Status: {out_of_range_type}
    Acceptable Range: {min_val} - {max_val}
    """
    
    query = f"""
    A manufacturing parameter has gone out of specification.
    
    Machine: {machine_code}
    Parameter: {parameter}
    Status: {out_of_range_type}
    Current Value: {current_value}
    Safe Range: {min_val} - {max_val}
    
    Please provide:
    1. Most likely root cause (1-2 sentences)
    2. Immediate action to take (1-2 sentences)
    3. Prevention recommendation (1-2 sentences)
    """
    
    return call_mistral_ai(query, context)


# ── Reference Datasheet Loading ──────────────────────────────────────────────
def initialize_parameter_reference_datasheet_table():
    """Create model_schema schema and parameter_reference_datasheet table if they don't exist."""
    try:
        with get_engine().connect() as c:
            # Step 1: Create schema if it doesn't exist
            try:
                c.execute(text("""
                    IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'model_schema')
                    BEGIN
                        EXEC('CREATE SCHEMA [model_schema]')
                    END
                """))
                c.commit()
            except Exception:
                try:
                    c.rollback()
                except:
                    pass
                # Schema might already exist, continue
            
            # Step 2: Create table if it doesn't exist
            c.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.tables t 
                              JOIN sys.schemas s ON t.schema_id = s.schema_id 
                              WHERE t.name = 'parameter_reference_datasheet' AND s.name = 'model_schema')
                CREATE TABLE [model_schema].[parameter_reference_datasheet] (
                    [DatasheetId] INT IDENTITY(1,1) PRIMARY KEY,
                    [MachineCode] VARCHAR(100) NOT NULL,
                    [OpcNodeId] VARCHAR(255) NOT NULL,
                    [ParameterName] VARCHAR(255),
                    [MinValue] FLOAT,
                    [OptimalValue] FLOAT,
                    [MaxValue] FLOAT,
                    [MeanValue] FLOAT,
                    [StdDev] FLOAT,
                    [SampleCount] INT,
                    [CreatedAt] DATETIME DEFAULT GETDATE(),
                    [UpdatedAt] DATETIME DEFAULT GETDATE(),
                    CONSTRAINT [unique_datasheet] UNIQUE ([MachineCode], [OpcNodeId]),
                    INDEX [idx_machine] ([MachineCode])
                )
            """))
            c.commit()
    except Exception as e:
        pass


@st.cache_data(ttl=300)
def load_parameter_reference_datasheet(machine_code: str | None = None) -> pd.DataFrame:
    """Load parameter reference datasheets from model_schema."""
    try:
        initialize_parameter_reference_datasheet_table()
        
        query = "SELECT * FROM [model_schema].[parameter_reference_datasheet]"
        if machine_code:
            query += " WHERE MachineCode = :m"
        query += " ORDER BY MachineCode, ParameterName"
        
        with get_engine().connect() as c:
            params = {"m": machine_code} if machine_code else {}
            df = pd.read_sql(text(query), c, params=params)
        
        return df if not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_parameter_statistics() -> pd.DataFrame:
    """Load parameter statistics from model_schema."""
    try:
        with get_engine().connect() as c:
            df = pd.read_sql(text("""
                SELECT Parameter, MonitoringCount, RecipeCount, AnalyzedAt
                FROM [model_schema].[parameter_statistics]
                ORDER BY AnalyzedAt DESC, MonitoringCount DESC
            """), c)
        return df
    except Exception:
        return pd.DataFrame()


def save_parameter_datasheet(machine_code: str, opc_node_id: str, 
                            min_value: float, mean_value: float, max_value: float,
                            std_dev: float = None, sample_count: int = None) -> bool:
    """
    Save or update parameter statistics to the reference datasheet.
    Called after analysis to store min/mean/max from the last 20 rows.
    """
    try:
        initialize_parameter_reference_datasheet_table()
        
        param_name = opc_node_id.replace('_recipe', '').replace('_ACT', '').replace('_', ' ')
        
        with get_engine().connect() as c:
            # Check if record exists
            existing = pd.read_sql(text("""
                SELECT DatasheetId FROM [model_schema].[parameter_reference_datasheet]
                WHERE MachineCode = :machine AND OpcNodeId = :opc_node
            """), c, params={"machine": machine_code, "opc_node": opc_node_id})
            
            if not existing.empty:
                # Update existing record
                c.execute(text("""
                    UPDATE [model_schema].[parameter_reference_datasheet]
                    SET MinValue = :min_val, MeanValue = :mean_val, MaxValue = :max_val,
                        StdDev = :std_dev, SampleCount = :sample_count, UpdatedAt = GETDATE()
                    WHERE MachineCode = :machine AND OpcNodeId = :opc_node
                """), {
                    "min_val": min_value,
                    "mean_val": mean_value,
                    "max_val": max_value,
                    "std_dev": std_dev,
                    "sample_count": sample_count or 20,
                    "machine": machine_code,
                    "opc_node": opc_node_id
                })
            else:
                # Insert new record
                c.execute(text("""
                    INSERT INTO [model_schema].[parameter_reference_datasheet]
                    (MachineCode, OpcNodeId, ParameterName, MinValue, MeanValue, MaxValue, StdDev, SampleCount)
                    VALUES (:machine, :opc_node, :param_name, :min_val, :mean_val, :max_val, :std_dev, :sample_count)
                """), {
                    "machine": machine_code,
                    "opc_node": opc_node_id,
                    "param_name": param_name,
                    "min_val": min_value,
                    "mean_val": mean_value,
                    "max_val": max_value,
                    "std_dev": std_dev,
                    "sample_count": sample_count or 20
                })
            
            c.commit()
        
        # Clear cache so new data is loaded
        st.cache_data.clear()
        return True
    except Exception as e:
        st.warning(f"Could not save parameter datasheet: {str(e)}")
        return False


# ── Analysis Results Storage (Unified Analysis Tables) ──────────────────────────────
def get_analysis_result_table_name(machine_code: str) -> str:
    """
    Get the unified analysis results table name for a machine.
    Table naming pattern: model_schema.analysis_results_[MACHINE_CODE]
    All analyses for a machine go into this single table.
    
    Args:
        machine_code: Machine code (e.g., 'MACHINE_001')
        
    Returns:
        Table name (e.g., 'analysis_results_MACHINE_001')
    """
    safe_machine = machine_code.replace('-', '_').replace(' ', '_').upper()
    return f"analysis_results_{safe_machine}"


def create_analysis_result_table(machine_code: str, timestamp: str = None) -> str:
    """
    Create or reuse a unified analysis results table for a machine.
    Table naming pattern: model_schema.analysis_results_[MACHINE_CODE]
    
    One table per machine stores all analyses sequentially with tracking metadata.
    
    Args:
        machine_code: Machine code (e.g., 'MACHINE_001')
        timestamp: Deprecated, kept for backward compatibility
        
    Returns:
        Table name created/reused (e.g., 'analysis_results_MACHINE_001')
    """
    table_name = get_analysis_result_table_name(machine_code)
    
    try:
        # Use begin() for proper transaction handling with auto-commit
        with get_engine().begin() as c:
            # Create schema if it doesn't exist
            try:
                c.execute(text("""
                    IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'model_schema')
                    BEGIN
                        EXEC('CREATE SCHEMA [model_schema]')
                    END
                """))
            except:
                pass
            
            # Create the unified analysis results table (if not exists)
            c.execute(text(f"""
                IF NOT EXISTS (SELECT * FROM sys.tables t 
                              JOIN sys.schemas s ON t.schema_id = s.schema_id 
                              WHERE t.name = '{table_name}' AND s.name = 'model_schema')
                CREATE TABLE [model_schema].[{table_name}] (
                    [ResultId] INT IDENTITY(1,1) PRIMARY KEY,
                    [RunSequence] INT NOT NULL,
                    [AnalysisTimestamp] DATETIME DEFAULT GETDATE(),
                    [ConfigurationId] INT NOT NULL,
                    [ConfigurationName] VARCHAR(255),
                    [MachineCode] VARCHAR(100) NOT NULL,
                    [OpcNodeId] VARCHAR(255) NOT NULL,
                    [ParameterName] VARCHAR(255),
                    [MinValue] FLOAT,
                    [MeanValue] FLOAT,
                    [MaxValue] FLOAT,
                    [StdDev] FLOAT,
                    [SampleCount] INT,
                    [CreatedAt] DATETIME DEFAULT GETDATE(),
                    INDEX [idx_run] ([RunSequence]),
                    INDEX [idx_config] ([ConfigurationId]),
                    INDEX [idx_machine] ([MachineCode]),
                    INDEX [idx_param] ([OpcNodeId]),
                    INDEX [idx_timestamp] ([AnalysisTimestamp])
                )
            """))
        
        return table_name
    except Exception as e:
        st.error(f"Error creating analysis result table: {str(e)}")
        return None


def get_next_analysis_sequence(machine_code: str) -> int:
    """
    Get the next RunSequence number for a machine's analysis.
    
    Args:
        machine_code: Machine code
        
    Returns:
        Next sequence number (1-indexed)
    """
    try:
        table_name = get_analysis_result_table_name(machine_code)
        with get_engine().connect() as c:
            result = c.execute(text(f"""
                SELECT MAX(RunSequence) as max_seq FROM [model_schema].[{table_name}]
            """)).fetchone()
            max_seq = result[0] if result and result[0] else 0
            return max_seq + 1
    except Exception:
        return 1


def save_analysis_results(configuration_id: int, configuration_name: str, 
                         machine_code: str, analysis_data: pd.DataFrame,
                         table_name: str = None) -> bool:
    """
    Save analysis results to the unified analysis results table.
    
    Appends new analysis rows with metadata (AnalysisId, RunSequence, AnalysisTimestamp)
    so all analyses for a machine are stored in one table sequentially.
    
    Args:
        configuration_id: ID of the configuration analyzed
        configuration_name: Name of the configuration
        machine_code: Machine code analyzed
        analysis_data: DataFrame with columns: OpcNodeId, ParameterName, MinValue, MeanValue, MaxValue, StdDev, SampleCount
        table_name: Deprecated, kept for backward compatibility. Always uses unified table.
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Always use the unified table for this machine
        table_name = create_analysis_result_table(machine_code)
        
        if table_name is None:
            print(f"❌ Failed to create analysis result table for {machine_code}")
            return False
        
        # Get the next RunSequence number for this analysis
        run_sequence = get_next_analysis_sequence(machine_code)
        
        print(f"📝 Saving {len(analysis_data)} parameters to {table_name} (Run #{run_sequence})")
        
        # Use begin() for auto-commit transactions
        insert_count = 0
        with get_engine().begin() as c:
            for idx, (_, row) in enumerate(analysis_data.iterrows()):
                try:
                    result = c.execute(text(f"""
                        INSERT INTO [model_schema].[{table_name}]
                        (RunSequence, AnalysisTimestamp, ConfigurationId, ConfigurationName, MachineCode, OpcNodeId, ParameterName, 
                         MinValue, MeanValue, MaxValue, StdDev, SampleCount)
                        VALUES (:run_seq, :analysis_time, :config_id, :config_name, :machine, :opc_node, :param_name,
                                :min_val, :mean_val, :max_val, :std_dev, :sample_count)
                    """), {
                        "run_seq": run_sequence,
                        "analysis_time": datetime.now(),
                        "config_id": configuration_id,
                        "config_name": configuration_name,
                        "machine": machine_code,
                        "opc_node": str(row.get('OpcNodeId', '')),
                        "param_name": str(row.get('ParameterName', '')),
                        "min_val": float(row.get('MinValue', 0)),
                        "mean_val": float(row.get('MeanValue', 0)),
                        "max_val": float(row.get('MaxValue', 0)),
                        "std_dev": float(row.get('StdDev', 0)) if pd.notna(row.get('StdDev')) else None,
                        "sample_count": int(row.get('SampleCount', 0)) if pd.notna(row.get('SampleCount')) else 0
                    })
                    insert_count += 1
                except Exception as insert_err:
                    print(f"⚠️ Error inserting parameter {idx}: {str(insert_err)}")
        
        print(f"✅ Inserted {insert_count}/{len(analysis_data)} parameters successfully to Run #{run_sequence}")
        return insert_count > 0
    except Exception as e:
        print(f"❌ Error saving analysis results: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def list_analysis_results_tables(machine_code: str = None) -> list:
    """
    List all analysis result tables.
    
    With unified table structure, returns the single analysis_results_[MACHINE_CODE]
    table for each machine that has analyses.
    
    Args:
        machine_code: Optional filter by machine code
        
    Returns:
        List of table names
    """
    try:
        with get_engine().connect() as c:
            # Query system tables for unified analysis_results_* tables
            query = """
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = 'model_schema' 
                  AND TABLE_NAME LIKE 'analysis_results_%'
            """
            
            if machine_code:
                safe_machine = machine_code.replace('-', '_').replace(' ', '_').upper()
                query += f" AND TABLE_NAME = 'analysis_results_{safe_machine}'"
            
            query += " ORDER BY TABLE_NAME"
            
            df = pd.read_sql(text(query), c)
        
        return df['TABLE_NAME'].tolist() if not df.empty else []
    except Exception:
        return []


def load_analysis_results(table_name: str, run_sequence: int = None) -> pd.DataFrame:
    """
    Load analysis results from a unified analysis results table.
    
    Args:
        table_name: Name of the analysis result table (e.g., 'analysis_results_MACHINE_001')
        run_sequence: Optional filter by specific RunSequence (analysis run number)
                     If None, returns all analyses from the table
        
    Returns:
        DataFrame with analysis results
    """
    try:
        with get_engine().connect() as c:
            query = f"""
                SELECT * FROM [model_schema].[{table_name}]
            """
            
            if run_sequence is not None:
                query += f" WHERE RunSequence = {run_sequence}"
            
            query += " ORDER BY AnalysisTimestamp DESC, OpcNodeId"
            
            df = pd.read_sql(text(query), c)
        
        return df if not df.empty else pd.DataFrame()
    except Exception as e:
        st.warning(f"Error loading analysis results: {str(e)}")
        return pd.DataFrame()


def get_analysis_runs(machine_code: str) -> pd.DataFrame:
    """
    Get summary of all analysis runs for a machine.
    
    Args:
        machine_code: Machine code
        
    Returns:
        DataFrame with columns: RunSequence, AnalysisTimestamp, ConfigurationId, ConfigurationName, ParameterCount
    """
    try:
        table_name = get_analysis_result_table_name(machine_code)
        with get_engine().connect() as c:
            df = pd.read_sql(text(f"""
                SELECT 
                    RunSequence,
                    AnalysisTimestamp,
                    ConfigurationId,
                    ConfigurationName,
                    COUNT(*) as ParameterCount
                FROM [model_schema].[{table_name}]
                GROUP BY RunSequence, AnalysisTimestamp, ConfigurationId, ConfigurationName
                ORDER BY RunSequence DESC
            """), c)
        
        return df if not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


# ── Production Run Quality and Parameter Analysis Helpers ────────────────────
@st.cache_data(ttl=600)
def load_production_run_quality(run_id: str = None) -> pd.DataFrame:
    """
    Load production run quality data.
    If run_id specified, return quality for that run; else return all recent runs.
    """
    try:
        query = """
            SELECT TOP 20 RunId, MachineCode, Quality, StartTime, EndTime, Duration
            FROM [dbo].[productionrunquality]
        """
        if run_id:
            query += " WHERE RunId = :run_id"
        query += " ORDER BY StartTime DESC"
        
        params = {"run_id": run_id} if run_id else {}
        with get_engine().connect() as c:
            df = pd.read_sql(text(query), c, params=params)
        
        if not df.empty:
            df['StartTime'] = pd.to_datetime(df['StartTime'])
            df['EndTime'] = pd.to_datetime(df['EndTime'])
        
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=0)
def load_current_machine_values(machine_code: str, parameters: list) -> dict:
    """
    Load latest values per parameter from MachineTagValue.
    Returns dict: {param: {value, timestamp, exists_in_db, source}}.
    No caching (ttl=0) for real-time updates every second.
    """
    # Convert list to tuple for proper caching
    if isinstance(parameters, list):
        parameters = tuple(parameters)
    
    if not parameters:
        print(f"[load_current_machine_values] No parameters provided")
        return {}
    try:
        uniq = list(dict.fromkeys(parameters))
        print(f"[load_current_machine_values] Machine: {machine_code}, Unique params: {len(uniq)}")
        
        # Simple query first - just get ANY data for this machine to verify connectivity
        test_query = "SELECT COUNT(*) as cnt FROM MachineTagValue WITH (NOLOCK) WHERE MachineCode = :machine"
        params_test = {"machine": machine_code}
        
        with get_engine().connect() as c:
            test_df = pd.read_sql(text(test_query), c, params=params_test)
            total_rows = test_df['cnt'].iloc[0]
            print(f"[load_current_machine_values] Total rows in MachineTagValue for {machine_code}: {total_rows}")
        
        # Now try a query with the IN clause
        # Use parameterized approach with explicit value list
        params = {"machine": machine_code}
        param_placeholders = []
        for i, p in enumerate(uniq):
            param_key = f"p{i}"
            params[param_key] = p
            param_placeholders.append(f":{param_key}")
        
        # Build IN clause
        in_clause = "(" + ", ".join(param_placeholders) + ")"
        
        query = f"""
            SELECT TOP 1000 OpcNodeId, Value, SourceTimestamp
            FROM MachineTagValue WITH (NOLOCK)
            WHERE MachineCode = :machine AND OpcNodeId IN {in_clause}
            ORDER BY SourceTimestamp DESC
        """
        
        print(f"[load_current_machine_values] Query template: ...WHERE MachineCode = :machine AND OpcNodeId IN {in_clause}")
        print(f"[load_current_machine_values] Parameters to pass: {params}")
        
        for i, p in enumerate(uniq):
            print(f"  Param {i}: '{p}'")

        print(f"[load_current_machine_values] Executing query with {len(uniq)} parameters")
        
        # DIAGNOSTIC: See what OpcNodeIds exist in database for this machine
        with get_engine().connect() as c:
            diag_df = pd.read_sql(
                text(f"SELECT DISTINCT TOP 10 OpcNodeId FROM MachineTagValue WITH (NOLOCK) WHERE MachineCode = :m ORDER BY OpcNodeId"),
                c,
                params={"m": machine_code}
            )
            print(f"[load_current_machine_values] DIAGNOSTIC - OpcNodeIds in DB for {machine_code}:")
            for oid in diag_df['OpcNodeId']:
                print(f"  DB has: '{oid}'")
            
            # Check for matches
            db_params = set(diag_df['OpcNodeId'].tolist())
            config_params = set(uniq)
            matching = db_params & config_params
            missing = config_params - db_params
            
            print(f"  Config has {len(config_params)} params")
            print(f"  DB has {len(db_params)} OpcNodeIds")
            print(f"  Matching: {len(matching)}")
            if missing:
                print(f"  MISSING from DB:")
                for m in list(missing)[:3]:
                    print(f"    - '{m}'")
            
            # Store missing params for later status reporting
            missing_params = missing
        
        with get_engine().connect() as c:
            df = pd.read_sql(text(query), c, params=params)

        print(f"[load_current_machine_values] Query returned {len(df)} rows")
        print(f"[load_current_machine_values] Columns: {list(df.columns)}")
        
        if df.empty:
            print(f"[load_current_machine_values] DataFrame is empty, returning {{}}")
            return {}

        # Get the latest (max SourceTimestamp) for each OpcNodeId
        print(f"[load_current_machine_values] Before grouping: {len(df)} rows")
        df_latest = df.loc[df.groupby('OpcNodeId')['SourceTimestamp'].idxmax()]
        print(f"[load_current_machine_values] After grouping (latest per param): {len(df_latest)} rows")
        
        if df_latest.empty:
            print(f"[load_current_machine_values] No latest rows found, returning {{}}")
            return {}

        result = {}
        
        # Add all queried parameters to result
        for param in uniq:
            result[param] = {
                "value": None,
                "timestamp": None,
                "exists_in_db": param in db_params,
                "source": "not_in_db" if param not in db_params else "no_data",
            }
        
        # Update with actual values from the query
        for _, row in df_latest.iterrows():
            param = row["OpcNodeId"]
            value = row["Value"]
            timestamp = row["SourceTimestamp"]
            
            print(f"[load_current_machine_values] Processing {param}: raw_value={value} (type={type(value).__name__})")
            
            # Convert value to float
            if pd.notna(value):
                try:
                    float_val = float(value)
                    print(f"  -> Converted to float: {float_val}")
                except (ValueError, TypeError) as ve:
                    print(f"  -> Failed to convert to float: {ve}")
                    float_val = None
            else:
                print(f"  -> Value is NaN/None")
                float_val = None
            
            result[param]["value"] = float_val
            result[param]["timestamp"] = timestamp
            result[param]["exists_in_db"] = True
            result[param]["source"] = "success"

        print(f"[load_current_machine_values] Returning: {len([r for r in result.values() if r['source']=='success'])} with values, {len([r for r in result.values() if r['source']=='no_data'])} existing in DB but no data, {len([r for r in result.values() if r['source']=='not_in_db'])} not in DB")
        return result
    except Exception as e:
        import traceback
        print(f"ERROR in load_current_machine_values: {e}")
        traceback.print_exc()
        return {}


@st.cache_data(ttl=600)
def load_parameter_historical_data(machine_code: str, opc_node_id: str, 
                                    run_id: str = None, limit_samples: int = 5000) -> pd.DataFrame:
    """
    Load historical parameter data for a specific machine and parameter.
    Optionally filter by run_id; otherwise load recent data.
    """
    try:
        query = """
            SELECT SourceTimestamp, ProductionRunId, Value
            FROM (SELECT TOP 20 SourceTimestamp, ProductionRunId, Value FROM MachineTagValue
                  WHERE MachineCode = :machine AND OpcNodeId = :param
                  ORDER BY SourceTimestamp DESC) AS recent
            ORDER BY SourceTimestamp DESC
        """
        
        params = {"machine": machine_code, "param": opc_node_id}
        
        if run_id:
            query = query.replace("WHERE MachineCode", f"WHERE ProductionRunId = '{run_id}' AND MachineCode")
        
        with get_engine().connect() as c:
            df = pd.read_sql(text(query), c, params=params)
        
        if not df.empty:
            df['SourceTimestamp'] = pd.to_datetime(df['SourceTimestamp'])
            df = df.sort_values('SourceTimestamp')
        
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300)
def get_machine_current_run_info(machine_code: str) -> dict:
    """Get current/recent production run information for a machine."""
    try:
        with get_engine().connect() as c:
            df = pd.read_sql(text("""
                SELECT RunId, MachineCode, Quality, StartTime, EndTime
                FROM [dbo].[productionrunquality]
                WHERE MachineCode = :machine
                ORDER BY StartTime DESC
            """), c, params={"machine": machine_code})
        
        if df.empty:
            return None
        
        row = df.iloc[0]
        return {
            'RunId': row['RunId'],
            'MachineCode': row['MachineCode'],
            'Quality': row['Quality'],
            'StartTime': pd.to_datetime(row['StartTime']),
            'EndTime': pd.to_datetime(row['EndTime']) if pd.notna(row['EndTime']) else None
        }
    except Exception:
        return None


def initialize_analysis_results_table():
    """Create model_schema schema and analysis_results table if they don't exist."""
    try:
        with get_engine().connect() as c:
            # Create schema if it doesn't exist
            c.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'model_schema')
                BEGIN
                    EXEC('CREATE SCHEMA [model_schema]')
                END
            """))
            
            # Create table if it doesn't exist
            c.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.tables t 
                              JOIN sys.schemas s ON t.schema_id = s.schema_id 
                              WHERE t.name = 'analysis_results' AND s.name = 'model_schema')
                CREATE TABLE [model_schema].[analysis_results] (
                    [ResultId] INT IDENTITY(1,1) PRIMARY KEY,
                    [ConfigurationId] INT NOT NULL,
                    [ConfigurationName] VARCHAR(255),
                    [MachineCode] VARCHAR(100) NOT NULL,
                    [MonitoringParameters] NVARCHAR(MAX),
                    [ReferenceDatasheets] NVARCHAR(MAX),
                    [CorrelationAnalysis] NVARCHAR(MAX),
                    [Summary] NVARCHAR(MAX),
                    [NotebookContent] VARBINARY(MAX),
                    [CreatedAt] DATETIME DEFAULT GETDATE(),
                    INDEX [idx_config] ([ConfigurationId]),
                    INDEX [idx_machine] ([MachineCode]),
                    INDEX [idx_created] ([CreatedAt])
                )
            """))
            c.commit()
    except Exception:
        pass  # Table likely already exists


def store_analysis_results(results_export: dict, notebook_content: bytes = None) -> bool:
    """
    Store analysis results in the database - SIMPLE AND DIRECT like configuration save.
    
    Args:
        results_export: Dictionary with configuration_id, configuration_name, machine_code,
                       monitoring_parameters, reference_datasheets, correlation_analysis, summary
        notebook_content: Optional notebook file content (bytes) to store as BLOB
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        initialize_analysis_results_table()
        
        # Simple and direct - exactly like add_machine_configuration
        with get_engine().connect() as c:
            c.execute(text("""
                INSERT INTO [model_schema].[analysis_results] 
                ([ConfigurationId], [ConfigurationName], [MachineCode], [MonitoringParameters], 
                 [ReferenceDatasheets], [CorrelationAnalysis], [Summary], [NotebookContent])
                VALUES (:config_id, :config_name, :machine_code, :params, :datasheets, :correlation, :summary, :notebook)
            """), {
                'config_id': results_export.get('configuration_id'),
                'config_name': results_export.get('configuration_name'),
                'machine_code': results_export.get('machine_code'),
                'params': json.dumps(results_export.get('monitoring_parameters', [])),
                'datasheets': json.dumps(results_export.get('reference_datasheets', {})),
                'correlation': json.dumps(results_export.get('correlation_analysis', {})),
                'summary': json.dumps(results_export.get('summary', {})),
                'notebook': notebook_content
            })
            c.commit()
        
        return True
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return False


@st.cache_data(ttl=5)
def load_latest_analysis_results(machine_code: str = None, config_id: int = None, include_notebook: bool = False) -> dict:
    """
    Load the latest analysis results from the unified analysis results table.
    Loads all parameters from the most recent RunSequence for a machine.
    
    Args:
        machine_code: Machine code to load results for
        config_id: Optional filter by configuration ID (not used in new structure)
        include_notebook: Deprecated parameter, kept for compatibility
    
    Returns:
        dict: Latest analysis results with reference_datasheets structure, or empty dict if none found
    """
    try:
        if not machine_code:
            print(f"⚠️ load_latest_analysis_results: No machine_code provided")
            return {}
        
        # Get the unified table name for this machine
        table_name = get_analysis_result_table_name(machine_code)
        print(f"📊 load_latest_analysis_results: Looking for table [{table_name}] for machine [{machine_code}]")
        
        with get_engine().connect() as c:
            # Get the latest RunSequence
            latest_run_query = f"""
                SELECT MAX(RunSequence) as max_run FROM [model_schema].[{table_name}]
            """
            latest_run_result = pd.read_sql(text(latest_run_query), c)
            max_run = latest_run_result['max_run'].iloc[0] if not latest_run_result.empty else None
            
            print(f"   Latest RunSequence: {max_run}")
            
            if max_run is None:
                print(f"   ❌ No runs found in table")
                return {}  # No analysis found
            
            # Load all parameters from the latest run
            results_query = f"""
                SELECT 
                    ResultId,
                    RunSequence,
                    AnalysisTimestamp,
                    ConfigurationId,
                    ConfigurationName,
                    MachineCode,
                    OpcNodeId,
                    ParameterName,
                    MinValue,
                    MeanValue,
                    MaxValue,
                    StdDev,
                    SampleCount,
                    CreatedAt
                FROM [model_schema].[{table_name}]
                WHERE RunSequence = :run_seq
                ORDER BY OpcNodeId
            """
            
            results_df = pd.read_sql(text(results_query), c, params={'run_seq': int(max_run)})
            print(f"   ✅ Loaded {len(results_df)} parameters from RunSequence #{max_run}")
        
        if results_df.empty:
            print(f"   ❌ No data returned from query")
            return {}
        
        # Get metadata from first row
        first_row = results_df.iloc[0]
        created_at = first_row['CreatedAt']
        configuration_id = first_row['ConfigurationId']
        configuration_name = first_row['ConfigurationName']
        
        # Build reference_datasheets structure like model_page expects
        parameters_list = []
        for _, row in results_df.iterrows():
            parameters_list.append({
                'OpcNodeId': row['OpcNodeId'],
                'ParameterName': row['ParameterName'],
                'MinValue': float(row['MinValue']) if pd.notna(row['MinValue']) else None,
                'MeanValue': float(row['MeanValue']) if pd.notna(row['MeanValue']) else None,
                'MaxValue': float(row['MaxValue']) if pd.notna(row['MaxValue']) else None,
                'StdDev': float(row['StdDev']) if pd.notna(row['StdDev']) else None,
                'SampleCount': int(row['SampleCount']) if pd.notna(row['SampleCount']) else 0
            })
        
        # Build results_export structure expected by model_page
        results_export = {
            'configuration_id': int(configuration_id),
            'configuration_name': str(configuration_name),
            'machine_code': str(machine_code),
            'monitoring_parameters': [p['OpcNodeId'] for p in parameters_list],
            'reference_datasheets': {
                machine_code: {
                    'parameter_count': len(parameters_list),
                    'parameters': parameters_list
                }
            },
            'summary': {
                'total_machines': 1,
                'total_parameters': len(parameters_list)
            }
        }
        
        # Build full result dict with metadata
        result = {
            'result_id': int(first_row['ResultId']),
            'results_export': results_export,
            'correlations': [],
            'created_at': created_at,
            'run_sequence': int(max_run)
        }
        
        print(f"   ✅ Successfully loaded analysis results with {len(parameters_list)} parameters")
        return result
    except Exception as e:
        print(f"❌ Error in load_latest_analysis_results: {str(e)}")
        import traceback
        traceback.print_exc()
        return {}


# ── Recipe-Aware Analysis Helpers ────────────────────────────────────────────
def enhance_parameter_reference_datasheet_table():
    """Create or enhance parameter_reference_datasheet with recipe-aware columns."""
    try:
        with get_engine().connect() as c:
            # First ensure schema exists
            try:
                c.execute(text("""
                    IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'model_schema')
                    BEGIN
                        EXEC('CREATE SCHEMA [model_schema]')
                    END
                """))
                c.commit()
            except:
                try:
                    c.rollback()
                except:
                    pass
            
            # Create or enhance table with recipe-aware columns
            c.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.tables t 
                              JOIN sys.schemas s ON t.schema_id = s.schema_id 
                              WHERE t.name = 'parameter_reference_datasheet' AND s.name = 'model_schema')
                CREATE TABLE [model_schema].[parameter_reference_datasheet] (
                    [DatasheetId] INT IDENTITY(1,1) PRIMARY KEY,
                    [MachineCode] VARCHAR(100) NOT NULL,
                    [RecipeIdentifier] VARCHAR(255),
                    [OpcNodeId] VARCHAR(255) NOT NULL,
                    [ParameterName] VARCHAR(255),
                    [MinValue] FLOAT,
                    [OptimalValue] FLOAT,
                    [MaxValue] FLOAT,
                    [MeanValue] FLOAT,
                    [StdDev] FLOAT,
                    [SampleCount] INT,
                    [QualityOkCount] INT,
                    [QualityNotOkCount] INT,
                    [CreatedAt] DATETIME DEFAULT GETDATE(),
                    [UpdatedAt] DATETIME DEFAULT GETDATE(),
                    CONSTRAINT [unique_recipe_datasheet] UNIQUE ([MachineCode], [OpcNodeId], [RecipeIdentifier]),
                    INDEX [idx_machine] ([MachineCode]),
                    INDEX [idx_recipe] ([RecipeIdentifier]),
                    INDEX [idx_machine_recipe] ([MachineCode], [RecipeIdentifier])
                )
                ELSE
                BEGIN
                    -- Add recipe-aware columns if they don't exist
                    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                                   WHERE TABLE_SCHEMA = 'model_schema' 
                                   AND TABLE_NAME = 'parameter_reference_datasheet' 
                                   AND COLUMN_NAME = 'RecipeIdentifier')
                    BEGIN
                        ALTER TABLE [model_schema].[parameter_reference_datasheet]
                        ADD [RecipeIdentifier] VARCHAR(255) NULL
                    END
                    
                    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                                   WHERE TABLE_SCHEMA = 'model_schema' 
                                   AND TABLE_NAME = 'parameter_reference_datasheet' 
                                   AND COLUMN_NAME = 'QualityOkCount')
                    BEGIN
                        ALTER TABLE [model_schema].[parameter_reference_datasheet]
                        ADD [QualityOkCount] INT,
                            [QualityNotOkCount] INT
                    END
                END
            """))
            c.commit()
    except Exception as e:
        print(f"⚠️ Error enhancing parameter_reference_datasheet: {str(e)}")


@st.cache_data(ttl=600)
def get_last_10_runs_for_machine(machine_code: str) -> pd.DataFrame:
    """
    Get the 10 most recent production runs for a machine (no recipe filter).
    Queries productionrun table directly.
    """
    try:
        query = """
            SELECT TOP 10
                [RunId],
                [MachineCode],
                [StartTs],
                [EndTs],
                [Status],
                [ScopeKey] AS RecipeIdentifier
            FROM [dbo].[productionrun]
            WHERE [MachineCode] = :machine
              AND [StartTs] IS NOT NULL
              AND [EndTs] IS NOT NULL
            ORDER BY [StartTs] DESC
        """

        with get_engine().connect() as c:
            df = pd.read_sql(text(query), c, params={"machine": machine_code})

        if not df.empty:
            df['StartTs'] = pd.to_datetime(df['StartTs'])
            df['EndTs'] = pd.to_datetime(df['EndTs'])

        return df
    except Exception as e:
        st.warning(f"Error getting last 10 runs: {str(e)}")
        return pd.DataFrame()


def get_last_10_runs_for_recipe(machine_code: str, recipe_identifier: str) -> pd.DataFrame:
    """
    Get the 10 most recent production runs for a machine + recipe combination.
    Queries productionrun table directly (no MachineTagValue join needed).
    """
    try:
        query = """
            SELECT TOP 10
                [RunId],
                [MachineCode],
                [StartTs],
                [EndTs],
                [Status],
                [ScopeKey] AS RecipeIdentifier
            FROM [dbo].[productionrun]
            WHERE [MachineCode] = :machine
              AND [ScopeKey] = :recipe
              AND [StartTs] IS NOT NULL
              AND [EndTs] IS NOT NULL
            ORDER BY [StartTs] DESC
        """

        with get_engine().connect() as c:
            df = pd.read_sql(text(query), c, params={
                "machine": machine_code,
                "recipe": recipe_identifier
            })

        if not df.empty:
            df['StartTs'] = pd.to_datetime(df['StartTs'])
            df['EndTs'] = pd.to_datetime(df['EndTs'])

        return df
    except Exception as e:
        st.warning(f"Error getting last 10 runs: {str(e)}")
        return pd.DataFrame()


def get_last_10_runs_for_machine_with_recipe(machine_code: str, opcnodeids: list) -> pd.DataFrame:
    """
    Get the 10 most recent production runs for a machine that contain data for 
    the specified recipe parameters (opcnodeids).
    
    Filters runs to only those where at least one of the selected opcnodeids 
    has data recorded within the run's time window.
    
    Args:
        machine_code: The machine code to filter by
        opcnodeids: List of OPC NodeIds that define the recipe (e.g., ["param1", "param2"])
                   If empty or None, returns empty DataFrame.
    
    Returns:
        DataFrame with last 10 matching runs with columns: RunId, MachineCode, 
        StartTs, EndTs, Status, RecipeIdentifier
    """
    if not opcnodeids or len(opcnodeids) == 0:
        return pd.DataFrame()
    
    try:
        # Build the IN clause for OPC NodeIds
        opcnodeid_placeholders = ','.join([f':opcnodeid_{i}' for i in range(len(opcnodeids))])
        params = {"machine": machine_code}
        for i, nodeid in enumerate(opcnodeids):
            params[f"opcnodeid_{i}"] = nodeid
        
        query = f"""
            SELECT TOP 10
                pr.[RunId],
                pr.[MachineCode],
                pr.[StartTs],
                pr.[EndTs],
                pr.[Status],
                pr.[ScopeKey] AS RecipeIdentifier
            FROM [dbo].[productionrun] pr
            WHERE pr.[MachineCode] = :machine
              AND pr.[StartTs] IS NOT NULL
              AND pr.[EndTs] IS NOT NULL
              AND EXISTS (
                SELECT 1
                FROM [dbo].[MachineTagValue] mtv WITH (NOLOCK)
                WHERE mtv.[MachineCode] = pr.[MachineCode]
                  AND mtv.[OpcNodeId] IN ({opcnodeid_placeholders})
                  AND mtv.[SourceTimestamp] BETWEEN pr.[StartTs] AND pr.[EndTs]
              )
            ORDER BY pr.[StartTs] DESC
        """

        with get_engine().connect() as c:
            df = pd.read_sql(text(query), c, params=params)

        if not df.empty:
            df['StartTs'] = pd.to_datetime(df['StartTs'])
            df['EndTs'] = pd.to_datetime(df['EndTs'])

        return df
    except Exception as e:
        st.warning(f"Error getting last 10 runs for recipe: {str(e)}")
        return pd.DataFrame()


def get_all_params_in_time_window(machine_code: str, start_ts, end_ts) -> list:
    """
    Discover all distinct OpcNodeIds recorded during a time window.
    Uses SourceTimestamp only — does NOT require ProductionRunId to be non-NULL.
    Includes retry logic for SQL Server deadlock (Error 1205).
    """
    import time
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            query = """
                SELECT DISTINCT OpcNodeId
                FROM MachineTagValue WITH (NOLOCK)
                WHERE MachineCode = :machine
                  AND SourceTimestamp BETWEEN :start_ts AND :end_ts
                ORDER BY OpcNodeId
            """

            with get_engine().connect() as c:
                df = pd.read_sql(text(query), c, params={
                    "machine": machine_code,
                    "start_ts": start_ts,
                    "end_ts": end_ts
                })

            return df['OpcNodeId'].tolist() if not df.empty else []
        except Exception as e:
            error_str = str(e)
            # Check if it's a deadlock error (1205)
            if '1205' in error_str or 'deadlock' in error_str.lower():
                retry_count += 1
                if retry_count < max_retries:
                    # Exponential backoff: 0.5s, 1s, 1.5s
                    wait_time = 0.5 * retry_count
                    time.sleep(wait_time)
                    continue
                else:
                    st.error(f"⚠️ Database deadlock detected. Please try again in a moment.")
                    return []
            else:
                st.warning(f"Error discovering parameters: {str(e)}")
                return []


def get_recent_runs_for_sample_collection(machine_code: str, limit: int = 10) -> pd.DataFrame:
    """
    Get the most recent production runs for a machine.

    The caller can decide how many runs to surface for sample collection.
    """
    try:
        query = """
            SELECT TOP (:limit)
                [RunId],
                [MachineCode],
                [StartTs],
                [EndTs],
                [ScopeKey] AS RecipeIdentifier
            FROM [dbo].[productionrun]
            WHERE [MachineCode] = :machine
              AND [StartTs] IS NOT NULL
              AND [EndTs] IS NOT NULL
            ORDER BY [StartTs] DESC
        """

        with get_engine().connect() as c:
            df = pd.read_sql(text(query), c, params={"machine": machine_code, "limit": limit})

        if not df.empty:
            df['StartTs'] = pd.to_datetime(df['StartTs'])
            df['EndTs'] = pd.to_datetime(df['EndTs'])

        return df
    except Exception as e:
        st.warning(f"Error getting recent runs: {str(e)}")
        return pd.DataFrame()


def get_labeled_samples_from_runs(machine_code: str, runs: pd.DataFrame,
                                   param_list: list, samples_per_run: int = 5000) -> tuple:
    """
    For each parameter, collect up to samples_per_run from each run window using timestamps.
    Tags each sample with IsOk from ProductionRunQuality.

    Returns (labeled_df, quality_info) where quality_info is a dict with diagnostics:
        - quality_map: {RunId: IsOk}
        - matched_runs: list of RunIds found in ProductionRunQuality
        - missing_runs: list of RunIds NOT found
        - all_zero: True if all found IsOk values are 0
    """
    if runs.empty or not param_list:
        return pd.DataFrame(), {"quality_map": {}, "matched_runs": [], "missing_runs": [], "all_zero": True}

    all_samples = []
    run_ids = runs['RunId'].tolist()

    try:
        with get_engine().connect() as c:
            run_ids_str = ','.join([f"'{r}'" for r in run_ids])
            quality_df = pd.read_sql(
                text(f"""
                    SELECT RunId, IsOk
                    FROM [dbo].[ProductionRunQuality] WITH (NOLOCK)
                    WHERE RunId IN ({run_ids_str})
                """),
                c
            )

            quality_map = {}
            matched_runs = []
            if not quality_df.empty:
                quality_map = dict(zip(quality_df['RunId'], quality_df['IsOk']))
                matched_runs = quality_df['RunId'].tolist()

            missing_runs = [r for r in run_ids if r not in quality_map]
            all_zero = all(v == 0 for v in quality_map.values()) if quality_map else True

            for param in param_list:
                for _, run in runs.iterrows():
                    end_ts = run['EndTs'] if pd.notna(run['EndTs']) else datetime.now()

                    samples_df = pd.read_sql(
                        text("""
                            SELECT TOP (:limit) OpcNodeId, Value, SourceTimestamp
                            FROM MachineTagValue WITH (NOLOCK)
                            WHERE MachineCode = :machine
                              AND OpcNodeId = :param
                              AND SourceTimestamp BETWEEN :start_ts AND :end_ts
                            ORDER BY SourceTimestamp DESC
                        """),
                        c,
                        params={
                            "machine": machine_code,
                            "param": param,
                            "start_ts": run['StartTs'],
                            "end_ts": end_ts,
                            "limit": samples_per_run
                        }
                    )

                    if not samples_df.empty:
                        samples_df['Value'] = pd.to_numeric(samples_df['Value'], errors='coerce')
                        samples_df = samples_df.dropna(subset=['Value'])
                        samples_df['RunId'] = run['RunId']
                        samples_df['IsOk'] = quality_map.get(run['RunId'], 0)
                        all_samples.append(samples_df)

        quality_info = {
            "quality_map": quality_map,
            "matched_runs": matched_runs,
            "missing_runs": missing_runs,
            "all_zero": all_zero,
        }

        if all_samples:
            return pd.concat(all_samples, ignore_index=True), quality_info
        return pd.DataFrame(), quality_info
    except Exception as e:
        error_str = str(e)
        if '1205' in error_str or 'deadlock' in error_str.lower():
            st.error("⚠️ Database deadlock detected. The system is experiencing high contention. Please try again in a moment.")
        else:
            st.error(f"Error collecting samples: {str(e)}")
        return pd.DataFrame(), {"quality_map": {}, "matched_runs": [], "missing_runs": [], "all_zero": True}


def calculate_recipe_parameter_statistics_from_samples(labeled_samples: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate parameter statistics from labeled samples (OpcNodeId, Value, RunId, IsOk).

    Returns DataFrame with columns: OpcNodeId, ParameterName, MinValue, OptimalValue, MaxValue,
                                    MeanValue, StdDev, SampleCount, QualityOkCount, QualityNotOkCount
    """
    try:
        if labeled_samples.empty:
            return pd.DataFrame()

        results_list = []
        for param in labeled_samples['OpcNodeId'].unique():
            param_data = labeled_samples[labeled_samples['OpcNodeId'] == param].copy()
            param_data['Value'] = pd.to_numeric(param_data['Value'], errors='coerce')
            param_data = param_data.dropna(subset=['Value'])

            if param_data.empty:
                continue

            all_values = param_data['Value'].tolist()
            ok_values = param_data[param_data['IsOk'] == 1]['Value'].tolist()

            min_val = float(min(all_values))
            max_val = float(max(all_values))
            mean_val = float(param_data['Value'].mean())
            optimal_val = float(np.median(ok_values)) if ok_values else mean_val
            std_dev = float(param_data['Value'].std()) if len(all_values) > 1 else 0.0
            sample_count = len(all_values)
            ok_count = len(ok_values)
            not_ok_count = len(all_values) - ok_count

            param_name = param.replace('_recipe', '').replace('_ACT', '').replace('_', ' ')

            results_list.append({
                'OpcNodeId': param,
                'ParameterName': param_name,
                'MinValue': min_val,
                'OptimalValue': optimal_val,
                'MaxValue': max_val,
                'MeanValue': mean_val,
                'StdDev': std_dev,
                'SampleCount': sample_count,
                'QualityOkCount': ok_count,
                'QualityNotOkCount': not_ok_count
            })

        return pd.DataFrame(results_list) if results_list else pd.DataFrame()

    except Exception as e:
        st.error(f"Error calculating statistics: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return pd.DataFrame()


def load_production_runs_for_recipe(machine_code: str, recipe_identifier: str = None) -> pd.DataFrame:
    """
    Load historical ProductionRun records for a machine, optionally filtered by recipe.
    
    Args:
        machine_code: Machine code to analyze
        recipe_identifier: Optional recipe ID/name to filter by
        
    Returns:
        DataFrame with columns: RunId, MachineCode, StartTs, EndTs, Status, RecipeIdentifier
    """
    try:
        query = """
            SELECT DISTINCT
                [RunId],
                [MachineCode],
                [StartTs],
                [EndTs],
                [Status],
                [ScopeKey] AS RecipeIdentifier
            FROM [dbo].[productionrun]
            WHERE [MachineCode] = :machine
        """
        
        params = {"machine": machine_code}
        
        if recipe_identifier:
            query += " AND [ScopeKey] = :recipe"
            params["recipe"] = recipe_identifier
        
        query += " ORDER BY [StartTs] DESC"
        
        with get_engine().connect() as c:
            df = pd.read_sql(text(query), c, params=params)
        
        if not df.empty:
            df['StartTs'] = pd.to_datetime(df['StartTs'])
            df['EndTs'] = pd.to_datetime(df['EndTs'])
        
        return df
    except Exception as e:
        st.warning(f"Error loading production runs: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=600)
def load_distinct_recipes(machine_code: str) -> list:
    """Load distinct recipe identifiers for a machine."""
    try:
        with get_engine().connect() as c:
            df = pd.read_sql(
                text("""
                    SELECT DISTINCT [ScopeKey] AS RecipeIdentifier
                    FROM [dbo].[productionrun]
                    WHERE [MachineCode] = :machine AND [ScopeKey] IS NOT NULL
                    ORDER BY [ScopeKey]
                """),
                c,
                params={"machine": machine_code}
            )
        return df['RecipeIdentifier'].tolist() if not df.empty else []
    except Exception:
        return []


def save_recipe_datasheet(machine_code: str, recipe_identifier: str, 
                         parameter_statistics: pd.DataFrame) -> bool:
    """
    Save recipe-aware parameter datasheet to database.
    
    Args:
        machine_code: Machine code
        recipe_identifier: Recipe identifier
        parameter_statistics: DataFrame with calculated statistics
        
    Returns:
        True if successful, False otherwise
    """
    try:
        enhance_parameter_reference_datasheet_table()
        
        with get_engine().begin() as c:
            for _, row in parameter_statistics.iterrows():
                param_name = row.get('ParameterName', '')
                
                # Check if record exists
                existing = pd.read_sql(
                    text("""
                        SELECT DatasheetId FROM [model_schema].[parameter_reference_datasheet]
                        WHERE MachineCode = :machine AND OpcNodeId = :opc_node AND RecipeIdentifier = :recipe
                    """),
                    c,
                    params={
                        "machine": machine_code,
                        "opc_node": row['OpcNodeId'],
                        "recipe": recipe_identifier
                    }
                )
                
                if not existing.empty:
                    # Update existing
                    c.execute(text("""
                        UPDATE [model_schema].[parameter_reference_datasheet]
                        SET MinValue = :min_val, 
                            OptimalValue = :optimal_val, 
                            MaxValue = :max_val,
                            MeanValue = :mean_val,
                            StdDev = :std_dev,
                            SampleCount = :sample_count,
                            QualityOkCount = :ok_count,
                            QualityNotOkCount = :not_ok_count,
                            UpdatedAt = GETDATE()
                        WHERE MachineCode = :machine AND OpcNodeId = :opc_node AND RecipeIdentifier = :recipe
                    """), {
                        "machine": machine_code,
                        "opc_node": row['OpcNodeId'],
                        "recipe": recipe_identifier,
                        "min_val": float(row['MinValue']) if pd.notna(row['MinValue']) else None,
                        "optimal_val": float(row['OptimalValue']) if pd.notna(row['OptimalValue']) else None,
                        "max_val": float(row['MaxValue']) if pd.notna(row['MaxValue']) else None,
                        "mean_val": float(row['MeanValue']) if pd.notna(row['MeanValue']) else None,
                        "std_dev": float(row['StdDev']) if pd.notna(row['StdDev']) else None,
                        "sample_count": int(row['SampleCount']) if pd.notna(row['SampleCount']) else 0,
                        "ok_count": int(row['QualityOkCount']) if pd.notna(row['QualityOkCount']) else 0,
                        "not_ok_count": int(row['QualityNotOkCount']) if pd.notna(row['QualityNotOkCount']) else 0
                    })
                else:
                    # Insert new
                    c.execute(text("""
                        INSERT INTO [model_schema].[parameter_reference_datasheet]
                        (MachineCode, RecipeIdentifier, OpcNodeId, ParameterName, 
                         MinValue, OptimalValue, MaxValue, MeanValue, StdDev, SampleCount,
                         QualityOkCount, QualityNotOkCount)
                        VALUES (:machine, :recipe, :opc_node, :param_name,
                                :min_val, :optimal_val, :max_val, :mean_val, :std_dev, :sample_count,
                                :ok_count, :not_ok_count)
                    """), {
                        "machine": machine_code,
                        "recipe": recipe_identifier,
                        "opc_node": row['OpcNodeId'],
                        "param_name": param_name,
                        "min_val": float(row['MinValue']) if pd.notna(row['MinValue']) else None,
                        "optimal_val": float(row['OptimalValue']) if pd.notna(row['OptimalValue']) else None,
                        "max_val": float(row['MaxValue']) if pd.notna(row['MaxValue']) else None,
                        "mean_val": float(row['MeanValue']) if pd.notna(row['MeanValue']) else None,
                        "std_dev": float(row['StdDev']) if pd.notna(row['StdDev']) else None,
                        "sample_count": int(row['SampleCount']) if pd.notna(row['SampleCount']) else 0,
                        "ok_count": int(row['QualityOkCount']) if pd.notna(row['QualityOkCount']) else 0,
                        "not_ok_count": int(row['QualityNotOkCount']) if pd.notna(row['QualityNotOkCount']) else 0
                    })
        
        # Clear cache
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error saving recipe datasheet: {str(e)}")
        return False


@st.cache_data(ttl=300)
def initialize_datasheet_runs_table():
    """Create datasheet_runs table if it doesn't exist."""
    try:
        with get_engine().connect() as c:
            # First ensure schema exists
            try:
                c.execute(text("""
                    IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'model_schema')
                    BEGIN
                        EXEC('CREATE SCHEMA [model_schema]')
                    END
                """))
                c.commit()
            except:
                try:
                    c.rollback()
                except:
                    pass
            
            # Create table if it doesn't exist
            c.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.tables t 
                              JOIN sys.schemas s ON t.schema_id = s.schema_id 
                              WHERE t.name = 'datasheet_runs' AND s.name = 'model_schema')
                CREATE TABLE [model_schema].[datasheet_runs] (
                    [DatasheetRunId] INT IDENTITY(1,1) PRIMARY KEY,
                    [MachineCode] VARCHAR(100) NOT NULL,
                    [RecipeIdentifier] VARCHAR(255),
                    [ExecutionTimestamp] DATETIME DEFAULT GETDATE(),
                    [ParameterCount] INT,
                    [SampleCount] INT,
                    [OkCount] INT,
                    [NotOkCount] INT,
                    [CreatedAt] DATETIME DEFAULT GETDATE(),
                    INDEX [idx_machine] ([MachineCode]),
                    INDEX [idx_machine_timestamp] ([MachineCode], [ExecutionTimestamp]),
                    INDEX [idx_recipe] ([RecipeIdentifier])
                )
            """))
            c.commit()
    except Exception as e:
        print(f"⚠️ Error initializing datasheet_runs table: {str(e)}")


def enhance_parameter_reference_datasheet_with_run_id():
    """Add DatasheetRunId column to parameter_reference_datasheet if it doesn't exist."""
    try:
        with get_engine().connect() as c:
            # Check if column exists
            result = c.execute(text("""
                SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'model_schema' 
                AND TABLE_NAME = 'parameter_reference_datasheet' 
                AND COLUMN_NAME = 'DatasheetRunId'
            """))
            
            if not result.fetchone():
                # Add the column
                c.execute(text("""
                    ALTER TABLE [model_schema].[parameter_reference_datasheet]
                    ADD [DatasheetRunId] INT NULL
                """))
                c.commit()
    except Exception as e:
        print(f"⚠️ Error enhancing parameter_reference_datasheet with RunId: {str(e)}")


def save_datasheet_run(machine_code: str, recipe_identifier: str, 
                      parameter_count: int, sample_count: int, 
                      ok_count: int, not_ok_count: int) -> int | None:
    """
    Save a datasheet run entry with execution timestamp.
    
    Args:
        machine_code: Machine code
        recipe_identifier: Recipe identifier
        parameter_count: Number of parameters in the datasheet
        sample_count: Total samples collected
        ok_count: OK samples count
        not_ok_count: NOT OK samples count
        
    Returns:
        DatasheetRunId if successful, None otherwise
    """
    try:
        initialize_datasheet_runs_table()
        
        with get_engine().begin() as c:
            # Insert and get ID using OUTPUT clause (SQL Server syntax)
            result = c.execute(text("""
                INSERT INTO [model_schema].[datasheet_runs]
                (MachineCode, RecipeIdentifier, ParameterCount, SampleCount, OkCount, NotOkCount)
                OUTPUT INSERTED.[DatasheetRunId]
                VALUES (:machine, :recipe, :param_count, :sample_count, :ok_count, :not_ok_count)
            """), {
                "machine": machine_code,
                "recipe": recipe_identifier,
                "param_count": parameter_count,
                "sample_count": sample_count,
                "ok_count": ok_count,
                "not_ok_count": not_ok_count
            })
            
            row = result.fetchone()
            datasheet_run_id = row[0] if row else None
            
        if datasheet_run_id:
            st.cache_data.clear()
            return datasheet_run_id
        return None
    except Exception as e:
        import traceback
        st.error(f"Error saving datasheet run: {str(e)}")
        st.error(traceback.format_exc())
        return None


@st.cache_data(ttl=300)
def get_datasheet_runs_for_machine(machine_code: str) -> pd.DataFrame:
    """
    Get all datasheet runs for a machine, sorted by execution timestamp (most recent first).
    
    Args:
        machine_code: Machine code
        
    Returns:
        DataFrame with columns: DatasheetRunId, RecipeIdentifier, ExecutionTimestamp, ParameterCount, SampleCount, OkCount, NotOkCount
    """
    try:
        initialize_datasheet_runs_table()
        
        with get_engine().connect() as c:
            df = pd.read_sql(
                text("""
                    SELECT 
                        DatasheetRunId,
                        RecipeIdentifier,
                        ExecutionTimestamp,
                        ParameterCount,
                        SampleCount,
                        OkCount,
                        NotOkCount
                    FROM [model_schema].[datasheet_runs]
                    WHERE MachineCode = :machine
                    ORDER BY ExecutionTimestamp DESC
                """),
                c,
                params={"machine": machine_code}
            )
        
        if not df.empty:
            df['ExecutionTimestamp'] = pd.to_datetime(df['ExecutionTimestamp'])
        
        return df if not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def load_datasheet_by_run_id(machine_code: str, datasheet_run_id: int) -> pd.DataFrame:
    """
    Load datasheet parameters for a specific run.
    
    Args:
        machine_code: Machine code
        datasheet_run_id: DatasheetRunId from datasheet_runs table
        
    Returns:
        DataFrame with parameter statistics for the specified run
    """
    try:
        with get_engine().connect() as c:
            df = pd.read_sql(
                text("""
                    SELECT 
                        prd.OpcNodeId,
                        prd.ParameterName,
                        prd.MinValue,
                        prd.OptimalValue,
                        prd.MaxValue,
                        prd.MeanValue,
                        prd.StdDev,
                        prd.SampleCount,
                        prd.QualityOkCount,
                        prd.QualityNotOkCount
                    FROM [model_schema].[datasheet_runs] dr
                    LEFT JOIN [model_schema].[parameter_reference_datasheet] prd 
                        ON dr.MachineCode = prd.MachineCode 
                        AND dr.RecipeIdentifier = prd.RecipeIdentifier
                    WHERE dr.DatasheetRunId = :run_id 
                    AND dr.MachineCode = :machine
                    ORDER BY prd.OpcNodeId
                """),
                c,
                params={"run_id": datasheet_run_id, "machine": machine_code}
            )
        
        return df if not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def load_recipe_datasheet(machine_code: str, recipe_identifier: str) -> pd.DataFrame:
    """Load reference datasheet for a specific machine + recipe combination."""
    try:
        enhance_parameter_reference_datasheet_table()
        
        with get_engine().connect() as c:
            df = pd.read_sql(
                text("""
                    SELECT * FROM [model_schema].[parameter_reference_datasheet]
                    WHERE MachineCode = :machine AND RecipeIdentifier = :recipe
                    ORDER BY OpcNodeId
                """),
                c,
                params={"machine": machine_code, "recipe": recipe_identifier}
            )
        
        return df if not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()