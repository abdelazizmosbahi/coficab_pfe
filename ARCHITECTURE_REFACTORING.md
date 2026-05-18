# Cable Maintenance AI - Architectural Refactoring Summary

## Overview
This refactoring implements a **recipe-aware, decoupled architecture** where:
- **Configuration Page**: Manages what parameters to monitor (unchanged)
- **Analysis Page**: Generates reference datasheets from historical production runs (NEW)
- **Model Page**: Real-time monitoring dashboard comparing live values to reference ranges (SIMPLIFIED)

---

## ✅ COMPLETED WORK

### 1. Enhanced Database Helpers (db_helpers.py)

**New Functions Added:**

```python
# Setup
enhance_parameter_reference_datasheet_table()

# Load Data
load_production_runs_for_recipe(machine_code, recipe_identifier)
load_distinct_recipes(machine_code)
load_recipe_datasheet(machine_code, recipe_identifier)

# Analysis
calculate_recipe_parameter_statistics(machine_code, recipe_identifier, production_runs)
save_recipe_datasheet(machine_code, recipe_identifier, parameter_statistics)
```

**Database Schema Changes:**
- Enhanced `parameter_reference_datasheet` with:
  - `RecipeIdentifier` (VARCHAR 255) - NULL for generic ranges
  - `QualityOkCount` (INT) - Samples from successful runs
  - `QualityNotOkCount` (INT) - Samples from failed runs
  - Unique constraint: (MachineCode, OpcNodeId, RecipeIdentifier)

### 2. Rewritten Analysis Page (analysis_page.py)

**Old Flow:**
- Select configuration
- Run papermill notebook execution
- Store results in `analysis_results` table

**New Flow:**
1. Select Machine → Select Recipe (from production runs)
2. View production runs for that machine + recipe
3. Click "Analyze" → System calculates stats from historical data:
   - Filters MachineTagValue by ProductionRun time windows
   - Correlates with ProductionRunQuality.IsOk
   - OptimalValue = median of values from OK runs
4. Results stored in `parameter_reference_datasheet` with recipe context
5. Optional: Load existing datasheet for comparison

**UI Features:**
- Sidebar: Machine selector → Recipe selector
- Production runs summary (count, durations)
- Generate datasheet button
- Display results with quality correlation metrics:
  - OK sample count
  - NOT OK sample count
  - OK percentage
- CSV download

---

## 🔄 REMAINING WORK: Simplify model_page.py

### Current State
Model page executes analysis via papermill and displays results. This logic should be removed.

### Required Changes

**1. Remove Analysis Execution Code:**
```python
# DELETE THESE FUNCTIONS:
- execute_analysis_notebook()
- extract_results_from_notebook()

# REMOVE analysis-related imports:
- import papermill
- import nbformat
- Any papermill-related logic
```

**2. Keep Real-Time Monitoring:**
- Configuration selection sidebar ✅
- Real-time parameter cards ✅
- Traceability buttons (3-second + full timeline) ✅
- Root cause analysis via Mistral AI ✅

**3. Update Reference Datasheet Loading:**
```python
# CHANGE FROM:
reference_df = load_parameter_reference_datasheet(machine_code=machine_code)

# CHANGE TO (recipe-aware):
if selected_recipe:
    reference_df = load_recipe_datasheet(machine_code, selected_recipe)
else:
    reference_df = load_recipe_datasheet(machine_code, None)  # Generic ranges
```

**4. Simplified Workflow:**
1. User selects configuration
2. System loads machine code + parameters from config
3. System loads reference datasheet (recipe-aware if available)
4. Display real-time values vs. reference ranges
5. Show traceability + RCA on demand

---

## Integration Points

### Data Flow
```
ProductionRun + ProductionRunQuality
        ↓
   Analysis Page (generates datasheets)
        ↓
parameter_reference_datasheet (stores ranges per machine + recipe)
        ↓
   Model Page (loads ranges, shows live values)
        ↓
   Live MachineTagValue (real-time monitoring)
```

### Key Queries

**Analysis Page:**
```sql
-- Load production runs
SELECT * FROM productionrun 
WHERE MachineCode = ? AND ScopeKey = ?

-- Get parameter values within run window
SELECT * FROM MachineTagValue
WHERE SourceTimestamp BETWEEN run.StartTs AND run.EndTs

-- Correlate with quality
SELECT IsOk FROM ProductionRunQuality WHERE RunId = ?
```

**Model Page:**
```sql
-- Load reference ranges for machine + recipe
SELECT * FROM parameter_reference_datasheet
WHERE MachineCode = ? AND RecipeIdentifier = ?

-- Load live values
SELECT Value FROM MachineTagValue
WHERE MachineCode = ? AND OpcNodeId = ?
ORDER BY SourceTimestamp DESC
```

---

## Testing Strategy

### 1. Data Setup
```sql
-- Create test production runs
INSERT INTO productionrun (RunId, MachineCode, ScopeKey, StartTs, EndTs, Status)
VALUES ('RUN001', 'MACHINE_001', 'RECIPE_A', '2024-01-01 10:00', '2024-01-01 11:00', 'Complete');

-- Create quality records
INSERT INTO ProductionRunQuality (RunId, IsOk) VALUES ('RUN001', 1);  -- Success
INSERT INTO ProductionRunQuality (RunId, IsOk) VALUES ('RUN002', 0);  -- Failure

-- Add machine tag values within run window
INSERT INTO MachineTagValue (MachineCode, OpcNodeId, SourceTimestamp, ProductionRunId, Value)
VALUES ('MACHINE_001', 'TEMP_ACT', '2024-01-01 10:30', 'RUN001', 75.5);
```

### 2. Analysis Page Testing
- [ ] Open analysis page
- [ ] Select machine with recipes → recipes appear
- [ ] Click analyze → progress shown
- [ ] Results display with OK/NOT OK counts
- [ ] CSV downloads correctly
- [ ] Load existing → shows previous results

### 3. Model Page Testing
- [ ] Configuration loads → parameter cards appear
- [ ] Real-time values update every second
- [ ] Reference ranges display correctly (recipe-aware)
- [ ] Traceability buttons work (3-sec + full timeline)
- [ ] RCA button works (Mistral API call)

---

## Configuration Example

**Setup in Configuration Page:**
```
Config Name: "Cable Assembly - Recipe A"
Machine: MACHINE_001
Monitoring Parameters: [TEMP_ACT, HUMIDITY_ACT, SPEED_ACT]
Recipe Parameters: [RECIPE_ID]
```

**Analysis Process (Analysis Page):**
```
1. Select: MACHINE_001 → RECIPE_A
2. System finds: 47 production runs
3. Analyze: Calculates stats from those 47 runs
4. Result: Reference datasheet specific to MACHINE_001 + RECIPE_A
```

**Real-Time Monitoring (Model Page):**
```
1. Select: "Cable Assembly - Recipe A"
2. Load ranges: From parameter_reference_datasheet (RECIPE_A specific)
3. Show live values: Compare to RECIPE_A ranges
4. Alert if out-of-spec for this recipe
```

---

## Benefits of This Architecture

✅ **Separation of Concerns**: Analysis ≠ Monitoring
✅ **Recipe Awareness**: Different recipes can have different specs
✅ **Quality Correlation**: Reference ranges based on successful runs
✅ **Reduced Model Page Complexity**: No notebook execution needed
✅ **Faster Monitoring**: Pre-calculated ranges, instant display
✅ **Better UX**: Clear workflow (configure → analyze → monitor)

---

## Checklist for Completion

- [x] Enhanced db_helpers with recipe-aware functions
- [x] Updated parameter_reference_datasheet schema
- [x] Rewrote analysis_page.py
- [ ] Remove analysis code from model_page.py
- [ ] Update model_page to use recipe-aware datasheets
- [ ] Test end-to-end with sample data
- [ ] Update navigation/documentation
- [ ] Deploy to production

---

## Notes for Next Steps

1. **Model Page Refactoring**: Start by removing the `execute_analysis_notebook()` function and all related code. This is ~400 lines that are no longer needed.

2. **Backward Compatibility**: The new schema supports `RecipeIdentifier = NULL` for machines without recipe context. Existing code will work with generic ranges.

3. **Performance**: Analysis runs are now instant (no notebook execution). Reference datasheets are pre-computed and cached.

4. **Future Enhancement**: Could add quality prediction ML models using the OK vs NOT OK correlation data.
