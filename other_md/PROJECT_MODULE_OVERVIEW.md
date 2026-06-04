# Cable Maintenance AI - Configuration & Model Analysis Module

## Overview

This module comprises four interconnected components that work together to establish machine configurations, build parameter reference datasheets, and perform quality prediction analysis. The system enables users to:

1. **Configure** which parameters to monitor on each machine
2. **Analyze** historical parameter behavior to establish control limits
3. **Predict** product quality based on parameter trends
4. **Trace** parameter deviations and their relationship to quality outcomes

---

## Architecture

```
Configuration Layer (Database)
        ↓
machine_configuration.ipynb (Analysis)
        ↓
model_page.ipynb (Reference Building & Quality Prediction)
        ↓
configuration_page.py (UI - Create/Edit Configurations)
model_page.py (UI - Execute Analysis & View Results)
```

---

## Component 1: Machine Configuration Notebook

**File:** `notebooks/machine_configuration.ipynb`

### Purpose
Analyze and validate machine configurations stored in the database. Provides visibility into which parameters are being monitored, which are recipe parameters, and what coverage exists across machines.

### Key Functionality

#### 1.1 Database Connection & Table Initialization
- Connects to MySQL database using SQLAlchemy
- Creates/initializes three report storage tables in `model_schema`:
  - `configuration_reports`: Stores CSV exports as JSON arrays
  - `coverage_analysis_results`: Tracks parameter coverage percentages per configuration
  - `parameter_statistics`: Maintains parameter usage statistics (monitoring count, recipe count)

#### 1.2 Load Configurations
```python
Loads from model_schema.machine_configuration table:
- ConfigurationId: Unique configuration identifier
- ConfigurationName: Human-readable name (e.g., "Cable_Line_A_Standard")
- MachineCode: Target machine (e.g., "MC_00012")
- MonitoringParameters: JSON array of OPC node IDs to monitor
- RecipeParameters: JSON array of OPC node IDs that define recipes
- IsActive, CreatedAt, UpdatedAt: Status and timestamps
```

**Data Processing:**
- Parses JSON fields (MonitoringParameters, RecipeParameters) into Python lists
- Handles missing/null values gracefully

#### 1.3 Configuration Summary Statistics
Calculates and displays:
- **Total configurations** across all machines
- **Active configurations** (IsActive = 1)
- **Machines configured**: Unique machine count
- **Parameter statistics**:
  - Average monitoring parameters per configuration
  - Average recipe parameters per configuration
  - Min/max parameter counts

Example output:
```
Total Configurations: 5
Active Configurations: 4
Unique Machines: 2

Parameter Statistics:
Average monitoring parameters: 8.2
Average recipe parameters: 3.5
Max parameters: 12
Min parameters: 3
```

#### 1.4 Machine Tags Analysis
- Queries `MachineTagValue` table for all distinct machine/OPC node ID combinations
- Aggregates value statistics (min, max, mean) per tag
- Provides baseline data for coverage analysis

#### 1.5 Configuration Coverage Analysis
**Goal:** Determine what percentage of available machine parameters are being monitored.

**Calculation:**
```
Coverage % = (MonitoredTags / AvailableTags) × 100
Recipe % = (RecipeTags / MonitoredTags) × 100
```

**Output Stored in Database:**
```
ConfigurationName | MachineCode | Available | Monitored | Recipe | Coverage% | Recipe%
Cable_Line_A      | MC_00012    | 42        | 28        | 8      | 66.7%     | 28.6%
```

**Use Case:** Identify if configurations are underutilizing available sensor data.

#### 1.6 Visualization: Parameters per Configuration
- Bar chart comparing monitoring vs. recipe parameters across configurations
- Helps identify imbalanced configurations (e.g., many monitoring parameters but few recipes)

#### 1.7 Detailed Configuration Breakdown
- Lists all parameters for each configuration
- Shows which parameters appear in multiple configurations
- Identifies "critical" parameters (monitored across many machines)

### Outputs
1. Summary statistics printed to notebook
2. Coverage analysis results stored in `model_schema.coverage_analysis_results`
3. Visualizations (bar charts, distribution plots)
4. Parameter statistics stored in `model_schema.parameter_statistics`

---

## Component 2: Model & Quality Prediction Notebook

**File:** `notebooks/model_page.ipynb`

### Purpose
Build parameter reference datasheets (min/optimal/max values) for a selected configuration and correlate parameter behavior with production quality outcomes.

### Key Functionality

**Executed via:** Papermill from `model_page.py` (Streamlit page)
**Parameter Injection:** `configuration_id` (injected by Papermill)

#### 2.1 Configuration Loading
```python
Loads single configuration matching configuration_id:
SELECT ConfigurationId, ConfigurationName, MachineCode, 
       MonitoringParameters, RecipeParameters, IsActive
FROM model_schema.machine_configuration
WHERE ConfigurationId = :configuration_id
```

**Output:** Single-row DataFrame with parsed monitoring and recipe parameters

#### 2.2 Production Quality Data Loading
```python
Joins productionrun and productionrunquality tables:
- RunId: Production run identifier
- MachineCode: Machine that executed the run
- Quality: "OK" or "NOT OK" (from IsOk flag)
- StartTime, EndTime: Run duration
- Quality_ComputedAt: When quality assessment was made
```

**Handling:**
- Parses timestamps to datetime format
- Limits to last 10,000 runs (performance optimization)
- Validates table schema (handles variations in column names)

#### 2.3 Parameter Value Loading per Production Run
```python
def load_parameter_values_for_run(run_id, opc_node_ids):
    SELECT ProductionRunId, OpcNodeId, Value, SourceTimestamp
    FROM MachineTagValue
    WHERE ProductionRunId = :run_id 
      AND OpcNodeId IN (monitoring_params)
    ORDER BY SourceTimestamp
```

**Purpose:** Extract time-series data for each parameter during production runs.

#### 2.4 Build Parameter Reference Datasheet

**Goal:** For each parameter in the configuration, determine:
- Historical minimum, Q25, median (optimal), Q75, maximum values
- Mean value and standard deviation
- Sample count for confidence assessment

**Function:** `build_parameter_reference_datasheet_for_machine(machine_code, parameter_list)`

**Process:**
1. Query `MachineTagValue` for all historical values of parameter on machine
2. Convert values to numeric (drop NaNs, coerce errors)
3. Calculate statistics:
   - **MinValue**: Minimum historical value
   - **MaxValue**: Maximum historical value  
   - **OptimalValue**: Median (statistically central)
   - **MeanValue**: Average across all samples
   - **StdDev**: Standard deviation
   - **Q25, Q75**: 25th and 75th percentiles
   - **SampleCount**: Number of valid measurements

**Output DataFrame Columns:**
```
MachineCode | OpcNodeId | ParameterName | MinValue | Q25Value | OptimalValue | 
Q75Value | MaxValue | MeanValue | StdDev | SampleCount
```

**Example:**
```
MC_00012 | AN_AnnealingVoltage_ACT | Annealing Voltage | 180.5 | 210.2 | 225.3 | 
235.8 | 260.0 | 223.1 | 18.5 | 5847
```

**Storage:**
- Datasheets stored in `model_schema.parameter_reference_datasheet` table
- Schema includes UpdatedAt timestamp for traceability

#### 2.5 Quality Prediction & Correlation Analysis

**Objective:** Correlate parameter behavior with production quality outcomes

**Approach:**
1. For each parameter in configuration
2. Split historical data into OK vs. NOT OK production runs
3. Compare parameter statistics between quality groups
4. Identify parameters that differ significantly between outcomes

**Analysis Metrics:**
- **Parameter Mean by Quality**: Compare average parameter value in OK vs. NOT OK runs
- **Parameter Range by Quality**: Check if OK runs have tighter clustering
- **Anomaly Score**: Correlation strength between parameter deviation and quality issues

**Stored Results:**
- Parameter-quality correlation analysis in `model_schema` (exact table TBD based on schema)
- Links parameters to quality outcomes
- Enables predictive insights: "When AnnelingVoltage exceeds 250, quality drops by X%"

### Outputs
1. **Parameter Reference Datasheet**:
   - Min/Max/Optimal values for each parameter
   - Stored in `model_schema.parameter_reference_datasheet`
   - Used as baseline for anomaly detection

2. **Quality Correlation Report**:
   - Parameters most correlated with quality issues
   - Strength of correlation (high/medium/low)
   - Direction (high values cause failures vs. low values)

3. **Notebook Execution Results**:
   - JSON export of analysis (extracted by `model_page.py`)
   - Stored with notebook output in `notebook_outputs/` directory

---

## Component 3: Configuration Page (Streamlit UI)

**File:** `app/pages/configuration_page.py`

### Purpose
Provide user interface for full CRUD operations on machine configurations. Enables users to:
- View all machines and their data flow status
- Create new configurations
- Edit existing configurations
- Delete configurations
- Manage monitoring and recipe parameters

### UI Sections

#### 3.1 Navigation & Theming
- **Coficab Theme**: Custom CSS gradient backgrounds (navy-to-orange), modern typography
- **Fixed Navigation Bar**: Links to all application pages
  - Home, Configuration, Model, Prediction, Manual Prediction, Recipe Parameters, OPC UA Live/Testing, Traceability
- **Hero Section**: Title "Machine & parameter configurations" with Coficab logo

#### 3.2 Machine Status Display
```
Section: "🤖 Machine status"
┌─────────────────────────────────────────┐
│ Machine | Status    | Receiving data    │
├─────────────────────────────────────────┤
│ MC_00012| 🟢 Active | Yes               │
│ MC_00013| 🔴 Offline| No                │
│ MC_00014| 🟢 Active | Yes               │
└─────────────────────────────────────────┘
```

**Data Source:** `get_machine_active_status_dict()` from `db_helpers.py`
- Checks `MachineTagValue` table for recent timestamps
- Indicates if machine is actively sending data
- Scrollable when many machines exist

#### 3.3 Tab 1: Add New Configuration

**Inputs:**
1. **Configuration Name** (text): Unique name for this setup (e.g., "Cable_Line_A_Standard")
2. **Select Active Machine** (dropdown):
   - Filters to only machines with active data flow
   - Shows green indicator (🟢)
   - Prevents configuration of offline machines

3. **Select Parameters to Monitor** (multi-select):
   - Populated from `load_all_parameters_for_machine(selected_machine)`
   - Queries distinct OpcNodeIds from MachineTagValue for machine
   - Formatted display: Strips "_ACT" suffix and replaces underscores with spaces
   - Example: "AN_AnnealingVoltage_ACT" → "AN Annealing Voltage"

4. **Select Recipe Parameters** (multi-select):
   - Subset of monitoring parameters
   - Only parameters already in monitoring list selectable
   - Validation: Must not contain parameters outside monitoring list

5. **Configuration Description** (text area, optional):
   - User notes about this configuration
   - Stored in database (optional field)

**Validation:**
- ✗ Configuration name is required
- ✗ At least one monitoring parameter required
- ✗ Recipe parameters must be subset of monitoring parameters

**On Save:**
- Calls `add_machine_configuration()` from `db_helpers.py`
- Inserts into `model_schema.machine_configuration` table:
  - ConfigurationName, MachineCode, MonitoringParameters (JSON), RecipeParameters (JSON)
  - CreatedAt, UpdatedAt timestamps auto-set
  - IsActive defaults to 1 (true)
- Shows success message and balloons animation
- Clears form and reruns page

#### 3.4 Tab 2: View & Edit Configurations

**Display:**
- Machine filter dropdown (All Machines or specific machine)
- Loads configurations from database
- Each configuration in expandable section showing:

**Expandable Section Layout:**
```
🔧 Configuration_Name | MC_00012 | 🟢 Active
┌─────────────────────────────────────────────┐
│ Configuration Details │ Parameters List      │
├─────────────────────────────────────────────┤
│ ID: 5                 │ MONITORING (8):      │
│ Machine: MC_00012     │ • AnnelingVoltage   │
│ Created: 2026-04-01   │ • AnnelingCurrent   │
│ Updated: 2026-04-07   │ • CoolandTemp       │
│                       │ RECIPE (3):          │
│                       │ • AnnelingVoltage   │
│                       │ • LineSpeed         │
│                       │ • CoolandTemp       │
│                       │                      │
│ [Edit] [Delete]       │                      │
└─────────────────────────────────────────────┘
```

**Edit Functionality:**
- Opens form similar to "Add Configuration" tab
- Pre-populates existing values
- Allows re-selection of parameters
- Calls `update_machine_configuration()` on save
- Validation same as Add

**Delete Link:**
- Confirms deletion with user
- Calls `delete_machine_configuration()`
- Removes from database permanently

#### 3.5 Tab 3: Delete Configuration

**Interface:**
- Lists all configurations
- Delete button for each (with confirmation dialog)
- Shows affected machine and parameter count before deletion

### Database Operations

**Helper Function Calls:**
- `load_all_machines()`: Get list of all distinct machines from database
- `load_all_parameters_for_machine(machine)`: Get OpcNodeIds from MachineTagValue
- `load_machine_configurations(machine_code=None)`: Fetch configurations (optionally filtered)
- `add_machine_configuration(config_name, machine_code, monitoring_params, recipe_params, description)`
- `update_machine_configuration(config_id, new_values)`
- `delete_machine_configuration(config_id)`
- `get_machine_active_status_dict()`: Get status for all machines
- `initialize_machine_configuration_table()`: Create table if not exists

### Styling & UX Features
- **Color Scheme**: Navy (#0b1b2b), Orange (#f57c00), Light gray backgrounds
- **Hover Effects**: Cards lift, borders highlight in orange
- **Responsive**: Adapts to different screen sizes
- **Accessibility**: Proper labels, help text for all inputs
- **Feedback**: Success/error messages, balloons on success

---

## Component 4: Model Page (Streamlit UI)

**File:** `app/pages/model_page.py`

### Purpose
Execute parameter reference datasheet analysis and display results. Provides:
- Interactive configuration selection
- Automated notebook execution via Papermill
- Parameter reference datasheets with spec bands
- Real-time parameter monitoring with synthetic data fallback
- Current value display with spec violation indicators
- Parameter traceability with historical trends
- AI-powered analysis insights

### UI Sections

#### 4.1 Navigation & Theming
- **Coficab Theme**: Same as configuration_page.py (navy/orange gradient)
- **Fixed Navigation Bar**: Full page navigation
- **Hero Section**: "Cable Manufacturing - Model Analysis & Real-Time Monitoring"

#### 4.2 Configuration Selector & Analysis Trigger

**Inputs:**
1. **Configuration Selection** (selectbox):
   - Lists all active configurations
   - Format: "Configuration Name (Machine: MC_00012)"
   - Loads from `load_machine_configurations()`

2. **Execute Analysis Button**:
   - Calls `execute_analysis_notebook()`
   - Passes `configuration_id` to Papermill
   - Shows progress stages:
     - Loading configuration (15%)
     - Loading production data (30%)
     - Building reference datasheets (50%)
     - Analyzing correlations (70%)
     - Storing results (85%)
     - Generating reports (100%)

#### 4.3 Notebook Execution Process

**Function:** `execute_analysis_notebook(configuration_id, machine_code, config_name, progress_callback)`

**Steps:**
1. **Preparation**:
   - Create outputs directory: `notebook_outputs/`
   - Generate timestamped notebook name: `analysis_{config_name}_{machine}_{timestamp}.ipynb`
   - Verify source notebook exists: `notebooks/model_page.ipynb`

2. **Execution**:
   ```python
   pm.execute_notebook(
       source_notebook="notebooks/model_page.ipynb",
       output_notebook=temp_path,
       parameters={"configuration_id": configuration_id},
       progress_bar=False
   )
   ```
   - Papermill injects `configuration_id` parameter at notebook top
   - Notebook executes in isolated kernel
   - Outputs saved to timestamped notebook file

3. **Result Extraction**:
   - Searches executed notebook for cell output containing "ANALYSIS RESULTS EXPORTED FOR STREAMLIT"
   - Parses JSON from output
   - Returns dictionary with:
     - `success`: Boolean
     - `results_export`: JSON dict with analysis results
     - `error`: Error message if failed

4. **Storage**:
   - Calls `store_analysis_results(results_export, notebook_content)`
   - Saves results to database (location TBD)
   - Stores full notebook for audit trail

5. **Cleanup**:
   - Removes temporary notebook file after execution
   - Preserves error notebooks for debugging

**Error Handling:**
- If Papermill not installed: Returns error message "Papermill not installed. Run: pip install papermill"
- If notebook file not found: Returns error with file path
- Catches all exceptions and reports to UI

#### 4.4 Parameter Reference Datasheet Display

**Function:** `build_filtered_datasheet(reference_df, machine_code, opc_ids)`

**Output Format:**
```
┌───────────────────────────────────────────────────────────────┐
│ Machine | Parameter | Min    | Mean   | Max    | Date_Analysed│
├───────────────────────────────────────────────────────────────┤
│ MC_00012| Annealing | 180.50 | 223.10 | 260.00 | 2026-04-07  │
│ MC_00012| Coolant   | 15.20  | 25.30  | 35.50  | 2026-04-07  │
│ MC_00012| LineSpeed | 850.00 | 1150.0| 1450.0 | 2026-04-07  │
└───────────────────────────────────────────────────────────────┘
```

**Sorting:**
- Maintains parameter order from configuration (recipe params first, then monitoring)
- Uses order map to preserve original sequence

**Data Sources:**
- Pulled from `model_schema.parameter_reference_datasheet` (populated by model_page.ipynb)
- Rows filtered by:
  - OpcNodeId in configuration's monitoring/recipe parameters
  - MachineCode matches selected configuration

#### 4.5 Production State Detection & Synthetic Value Generation

**Function:** `detect_production_state(elapsed_seconds, total_duration_estimate=600)`

**State Classification:**
```
Elapsed % | Phase      | Description       | Multiplier
0-10%     | startup    | Ramp phase       | 1.2x nominal
10-90%    | steady     | Main production  | 1.0x nominal
90-100%   | shutdown   | Cool-down        | 1.1x nominal
```

**Purpose:** Generate realistic synthetic parameter values when MachineTagValue data unavailable

**Approach:**
1. Calculate elapsed time since session start
2. Determine production phase
3. For each parameter:
   - Try to load latest value from `MachineTagValue` (preferred)
   - If unavailable, generate synthetic value:
     - Use historical mean as baseline
     - Apply state-specific range constraints
     - Add realistic noise (±8% variation + ±2% random)
     - Mark as `synthetic=True` in output

**State-Specific Ranges** (within STATE_SPECIFIC_RANGES dict):
```python
"startup": {
    "AN_AnnealingVoltage_ACT": {"min": 150, "max": 270},
    "AN_AnnealingCurrent_ACT": {"min": 100, "max": 170},
    ...
}
"steady": {
    "AN_AnnealingVoltage_ACT": {"min": 200, "max": 260},
    "AN_AnnealingCurrent_ACT": {"min": 130, "max": 160},
    ...
}
"shutdown": {
    # Broader ranges for shutdown phase
    ...
}
```

**Output Structure:**
```python
{
    "AN_AnnealingVoltage_ACT": {
        "value": 223.45,
        "timestamp": datetime.now(),
        "synthetic": False,  # or True if generated
        "opc_state_range": {...}
    },
    ...
}
```

#### 4.6 Current Parameter Metrics Display

**Layout:** Grid of metric cards showing current values

**Card Format:**
```
┌──────────────────────────────┐
│   ANNEALING VOLTAGE          │
│        223.5 V               │
│  Status: ✓ OK (within spec)  │
│  Range: 200-260 V            │
│  Target: 225 V               │
└──────────────────────────────┘
```

**Styling (CSS):**
- Gradient background: white → light gray
- Border: 2px solid #e4e8ec, radius 14px
- Hover: Border-color changes to orange (#f57c00), shadow increases
- Min-height: 160px for uniformity

**Data Fields:**
- Parameter name
- Current value (from real-time feed)
- Status indicator:
  - ✓ Green: Within specification
  - ⚠ Orange: Warning (approaching limit)
  - ✗ Red: Exceeds specification
- Min/Max range from reference datasheet
- Target/Optimal value from reference datasheet

#### 4.7 Specification Violation Badge

**Function:** `spec_violation_badge_html(current, lo, hi)`

**Output (if violation exists):**
```
↓ 12.45 below min · 25.3% of spec span
  [pill with red background, white text]

OR

↑ 18.20 above max · 41.2% of spec span
  [pill with orange background]
```

**Calculation:**
```
spec_span = high_limit - low_limit
if current < low_limit:
    gap = low_limit - current
    pct_of_span = (gap / span) * 100
    color: red gradient, text "↓ {gap:.2f} below min · {pct:.1f}% of spec span"
    
if current > high_limit:
    gap = current - high_limit
    pct_of_span = (gap / span) * 100
    color: orange gradient, text "↑ {gap:.2f} above max · {pct:.1f}% of spec span"
```

**CSS Styling:**
- Inline pill shape (border-radius: 999px)
- Gradient backgrounds (red for below, orange for above)
- Box shadow for depth
- Font: 12px, weight 700, letter-spacing 0.02em

**Use Case:** Quickly see magnitude and percentage of specification deviation

#### 4.8 Parameter Traceability Chart

**Function:** `_render_param_trace(machine_code, param, v_min, v_max, v_mean, fullscreen=False)`

**Features:**

**1. Historical Time-Series Plot:**
- Line + markers showing parameter values over time
- X-axis: Timestamp (formatted as YYYY-MM-DD HH:MM:SS)
- Y-axis: Parameter value
- Hover: Shows exact timestamp and value(s)

**2. Specification Bands:**
- Background shading between v_min and v_max (green, 10% opacity)
- Red shading below v_min (labeled "Below Min")
- Red shading above v_max (labeled "Above Max")
- Automatically scaled with 20% padding above/below data range

**3. Target Line:**
- Dashed green line at v_mean (optimal value)
- Labeled "Target"
- Helps identify drift from intended operation

**4. Overlay Parameter Selection:**
- Dropdown: "Select parameter to overlay"
- Excludes current parameter from options
- Queries distinct OpcNodeIds for machine
- Second trace added with different color if selected
- Enables visual comparison of related parameters

**Data Loading:**
```python
# Get earliest timestamp for time reference
SELECT MIN(SourceTimestamp) FROM MachineTagValue 
WHERE MachineCode = {machine} AND OpcNodeId = {param}

# Load full history
SELECT SourceTimestamp, Value FROM MachineTagValue
WHERE MachineCode = {machine} AND OpcNodeId = {param}
ORDER BY SourceTimestamp
```

**Filters:**
- Machine: Selected configuration's machine
- Parameter: Current parameter being traced
- Time: All historical data available

**Display:**
- Interactive Plotly chart (zoom, pan, hover)
- Legend showing parameter name and target
- Responsive width (full container)

#### 4.9 AI-Powered Analysis (Mistral Integration)

**Integration:** Mistral AI client for natural language insights

**Purpose:** Generate human-readable interpretation of analysis results

**Potential Use Cases:**
- "Parameter X is consistently below target during startup phase"
- "Coolant temperature shows 15% correlation with quality failures"
- "Recommend increasing annealing voltage by 5% to reduce variance"

**Implementation Details:** (Based on model_page.py imports)
- Uses `from mistralai import Mistral`
- Initialized with API key from `.env`
- Processes reference datasheet and quality correlation results
- Returns formatted analysis text/recommendations

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Database Tables                              │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐ ┌──────────────────┐│
│  │machine_configuration
│  │ • ConfigId       │  │MachineTagValue   │ │productionrun     ││
│  │ • ConfigName     │  │ • MachineCode    │ │ • RunId          ││
│  │ • MachineCode    │  │ • OpcNodeId      │ │ • MachineCode    ││
│  │ • Monitoring[]   │  │ • Value          │ │ • StartTs        ││
│  │ • Recipe[]       │  │ • SourceTimestamp│ │ • EndTs          ││
│  │ • IsActive       │  │                  │ │                  ││
│  └──────────────────┘  └──────────────────┘ └──────────────────┘
└─────────────────────────────────────────────────────────────────┘
              ↓                    ↓                    ↓
┌─────────────────────────────────────────────────────────────────┐
│              machine_configuration.ipynb                          │
│                                                                   │
│  • Load configurations by machine                                │
│  • Load available parameters (from MachineTagValue)              │
│  • Calculate coverage % (monitored/available)                    │
│  • Store coverage_analysis_results                               │
└─────────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────────┐
│            configuration_page.py (Streamlit UI)                   │
│                                                                   │
│  User Actions:                                                   │
│  • Create new configuration (select machine + parameters)        │
│  • Edit configuration (adjust parameters)                        │
│  • Delete configuration                                          │
│  • View machine status (active/inactive)                         │
└─────────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────────┐
│              model_page.py (Streamlit UI)                         │
│                                                                   │
│  1. User selects configuration                                   │
│  2. Click "Execute Analysis"                                     │
│  3. Executes model_page.ipynb via Papermill                      │
└─────────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   model_page.ipynb                                │
│                                                                   │
│  • Load configuration (configuration_id from Papermill)          │
│  • Load production quality data (productionrun + quality)        │
│  • Load parameter values per run (MachineTagValue)               │
│  • Build reference datasheet (min/optimal/max per parameter)    │
│  • Analyze quality correlations (OK vs. NOT OK runs)             │
│  • Store parameter_reference_datasheet results                   │
│  • Export JSON results for Streamlit                             │
└─────────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────────┐
│         Stored Results (model_schema tables)                      │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │parameter_reference_datasheet                             │   │
│  │ • OpcNodeId, MachineCode                                 │   │
│  │ • MinValue, Q25Value, OptimalValue, Q75Value, MaxValue  │   │
│  │ • MeanValue, StdDev, SampleCount                         │   │
│  │ • UpdatedAt (timestamp)                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │quality_correlation_results (if stored)                   │   │
│  │ • Parameter <-> Quality correlation metrics              │   │
│  │ • Strength (high/medium/low)                             │   │
│  │ • Direction (high values cause failures?)                │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────────┐
│              model_page.py (Results Display)                      │
│                                                                   │
│  Display to User:                                                │
│  • Parameter reference datasheet (table view)                    │
│  • Current values with spec violation badges                     │
│  • Parameter traceability charts (with overlays)                 │
│  • AI-generated insights (Mistral)                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Database Schema Interactions

### Tables Used

| Table | Schema | Purpose | Read/Write |
|-------|--------|---------|-----------|
| `machine_configuration` | model_schema | Store configuration definitions | Both |
| `MachineTagValue` | production | Store sensor readings per machine/parameter | Read |
| `productionrun` | opc_schema | Store production run metadata | Read |
| `productionrunquality` | opc_schema | Store quality assessment per run | Read |
| `parameter_reference_datasheet` | model_schema | Store min/max/optimal per parameter | Write |
| `coverage_analysis_results` | model_schema | Store parameter coverage statistics | Write |
| `parameter_statistics` | model_schema | Store parameter usage counts | Write |
| `configuration_reports` | model_schema | Store CSV exports as JSON | Write |

### Key Relationships

```
machine_configuration
    ├─ FK: implicit reference to machines via MachineCode
    └─ References MonitoringParameters/RecipeParameters as OpcNodeId strings

MachineTagValue
    ├─ FK: MachineCode → machines table
    ├─ FK: ProductionRunId → productionrun table
    └─ OpcNodeId matches parameters in configurations

productionrun
    ├─ FK: MachineCode → machines table
    └─ Has one ProductionRunQuality record (1:1)

parameter_reference_datasheet
    ├─ FK: MachineCode
    ├─ OpcNodeId (matches configuration parameters)
    └─ Derived from historical MachineTagValue
```

---

## Workflows

### Workflow 1: Create & Configure a New Machine

**Actors:** Operations Engineer, System Administrator

**Steps:**
1. Machine is physically connected and data flows into MachineTagValue table
2. Navigate to Configuration Page
3. In "Machine Status" section, verify 🟢 green indicator (data flowing)
4. Click "Add Configuration" tab
5. Fill in Configuration Name (e.g., "Cable_Line_B_Tuned")
6. Select Machine from dropdown (only active machines shown)
7. Select monitoring parameters (core OPC nodes to track)
8. Select recipe parameters (subset involved in recipe formulation)
9. Add optional description
10. Click "Save Configuration"
11. Configuration stored in database with IsActive=1

**Outcome:** Configuration ready for analysis

---

### Workflow 2: Analyze Configuration & Build Reference Datasheets

**Actors:** Data Analyst, Quality Engineer

**Steps:**
1. Navigate to Model Page
2. Select configuration from dropdown (e.g., "Cable_Line_B_Tuned | MC_00013")
3. Click "Execute Analysis"
4. System executes model_page.ipynb via Papermill with configuration_id parameter
5. Notebook:
   - Loads 10,000 most recent production runs
   - Queries all MachineTagValue records for configuration parameters
   - Builds reference datasheet (min/max/optimal statistics per parameter)
   - Analyzes OK vs. NOT OK runs for quality correlations
   - Stores results in parameter_reference_datasheet table
6. Page displays:
   - Parameter reference table (Min/Mean/Max statistics)
   - Current values with spec violation indicators
   - Parameter traceability charts
7. Optional: Select overlay parameter to compare trends

**Outcome:** Reference datasheets established, visual analysis available

---

### Workflow 3: Monitor & Trace Parameter Deviations

**Actors:** Machine Operator, Quality Control

**Steps:**
1. Real-time monitoring shows current parameter values on Model Page
2. User notices orange/red spec violation badge on parameter
3. Click parameter name or "Trace" button
4. System displays parameter traceability chart:
   - Green band: normal spec range (min-max)
   - Blue line: actual parameter values over time
   - Green dashed: target/optimal value
5. User can select overlay parameter to:
   - Compare with related parameters
   - Identify root cause (electrical vs. mechanical factor)
6. Chart shows timestamp when deviation started
7. User can correlate with production quality data
8. Document findings and notify maintenance if needed

**Outcome:** Visual evidence of when/how parameters deviated

---

### Workflow 4: Edit Configuration (Add/Remove Parameters)

**Actors:** Configuration Manager

**Steps:**
1. Navigate to Configuration Page, "View & Edit" tab
2. Optionally filter by machine
3. Find configuration in expandable list
4. Click expander to open details
5. In right panel, review current parameters
6. Click "Edit" button
7. Form opens with pre-populated values:
   - Configuration name (editable)
   - Machine (usually not changed)
   - Monitoring parameters (update multi-select)
   - Recipe parameters (update multi-select)
   - Description (update notes)
8. Make changes (e.g., add new monitoring parameter)
9. Validate: Recipe params must be subset of monitoring
10. Click "Update Configuration"
11. Database updated
12. Previous reference datasheets remain; next analysis will generate new ones

**Outcome:** Configuration modified, ready for re-analysis

---

## Error Handling & Robustness

### Common Issues & Mitigations

| Issue | Cause | Solution |
|-------|-------|----------|
| No active machines shown | Data not flowing into MachineTagValue | Check OPC UA server, firewall rules |
| "No parameters found" | MachineTagValue empty for machine | Wait for initial data, retry |
| Papermill execution fails | Notebook file missing | Verify `notebooks/model_page.ipynb` exists |
| Analysis timeout | Large dataset in MachineTagValue | Query optimization, data pruning |
| Synthetic values shown | Real-time data unavailable | Expected; system falls back gracefully |
| Coverage % = 0% | Monitoring parameters not in MachineTagValue | Re-configure with available parameters |

### Logging & Debugging

- All database errors printed to notebook/page console
- Papermill execution creates timestamped notebook in `notebook_outputs/`
- Executed notebook contains full cell outputs for debugging
- JSON results exported with "ANALYSIS RESULTS EXPORTED FOR STREAMLIT" marker
- Session state tracked (st.session_state) for UI state persistence

---

## Performance Considerations

### Query Optimization

1. **MachineTagValue Lookups**:
   - Limited to 100,000 rows per parameter (balance detail vs. speed)
   - Indexed on MachineCode, OpcNodeId, SourceTimestamp
   - Recommend database partitioning by date after 1 year of data

2. **Production Quality Analysis**:
   - Limited to 10,000 recent runs (covers 2-4 weeks typically)
   - Avoid full table scan; filter by MachineCode first

3. **Reference Datasheet**:
   - Cached per configuration (re-queried only on Execute Analysis)
   - Min/Max/Optimal recalculated, not incremental (fresh perspective)

### Scaling Strategies

- **Multiple Machines**: Configuration can specify only relevant parameters (reduces compute)
- **Batch Processing**: machine_configuration.ipynb designed for nightly summary runs
- **Incremental Updates**: parameter_reference_datasheet can be updated periodically vs. on-demand
- **Archive**: Move old MachineTagValue records to archive table after coverage analysis

---

## Security & Governance

### Data Access Control

- Database credentials in `.env` file (not in code)
- SQLAlchemy ORM prevents SQL injection
- Streamlit session state doesn't expose sensitive records
- Notebook execution sandboxed (temporary output only)

### Audit Trail

- All configurations timestamped (CreatedAt, UpdatedAt)
- Parameter reference datasheets include UpdatedAt
- Notebooks stored with timestamp for version tracking
- Database stores who executed analysis (can be enhanced)

### Data Quality

- Numeric coercion with error handling (invalid values → NaN → dropped)
- Null handling: configs with empty parameter lists filtered
- Timestamp parsing explicit (errors='coerce')
- JSON parsing defensive (checks for strings vs. already-parsed)

---

## Future Enhancements

### Potential Features

1. **Threshold Learning**: Automatically suggest spec limits based on statistical distribution
2. **Anomaly Detection**: Flag unusual parameter behavior during production runs
3. **Root Cause Analysis**: Link parameter deviations to specific quality failures
4. **Predictive Maintenance**: Identify parameters that precede failures
5. **Batch Optimization**: Suggest recipe parameter values for optimal quality
6. **A/B Testing**: Compare two configurations on same machine
7. **Parameter Dependency**: Identify correlated parameters and reduce redundancy
8. **Mobile Interface**: View reference datasheets and current values on mobile
9. **Export to PDF**: Generate configuration reports for archives
10. **Version Control**: Track configuration changes over time

### Code Extensibility

- `build_parameter_reference_datasheet_for_machine()` can be extended with statistical tests
- `detect_production_state()` can incorporate actual status tags (instead of elapsed time)
- `spec_violation_badge_html()` can include predictive severity scores
- Quality correlation logic can use advanced techniques (regression, random forest)

---

## Conclusion

This module provides a comprehensive platform for:
- **Defining** which parameters matter for each machine
- **Analyzing** historical behavior to establish control limits
- **Monitoring** real-time values against those limits
- **Tracing** deviations and their relationship to quality

The separation of concerns (configuration management, analysis notebook, streamlit UI) allows operators, analysts, and engineers to work independently while maintaining data integrity and audit trails.
