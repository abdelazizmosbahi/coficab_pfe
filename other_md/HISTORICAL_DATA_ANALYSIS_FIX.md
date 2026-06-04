# Historical Data Analysis - Parameter Discovery & Sample Collection Fixes

## Overview
Fixed the Recipe-Aware Analysis page to work reliably with **historical production data**, not real-time data.

**Key Principle**: The Analysis page analyzes past production runs of any age. Parameter discovery and sample collection must work even for runs from 1+ weeks ago, without assuming "latest data" availability.

---

## Problem Summary

### Before (Real-Time Bias)
- `get_all_params_in_time_window()` would fallback to "last 7 days" when run window had no data
- `get_labeled_samples_from_runs()` error messages recommended "more recent runs" and mentioned real-time OPC
- Always showed same ~188 parameters regardless of selected run
- No samples collected from historical runs

### Root Cause
Functions were designed for **real-time monitoring**, not **historical analysis**. They assumed:
- Recent data exists (last 24 hours)
- Fallback to "latest parameters" is acceptable
- Users should select recent runs

---

## Solution: Historical Data First

### 1. `get_all_params_in_time_window()` - 3-Tier Historical Strategy

**Instead of**: Try run window → fallback to "last 7 days" → give up

**Now**: Try run window → try exact times → fall back to all-time history

```python
# Strategy 1: Run window with ±2 hour buffer (PREFERRED)
# "Found X parameters in run window"
SELECT DISTINCT OpcNodeId FROM MachineTagValue
WHERE SourceTimestamp BETWEEN [start-2hr] AND [end+2hr]

# Strategy 2: Exact run times (if Strategy 1 is empty)
# "Found X parameters in exact run window"
SELECT DISTINCT OpcNodeId FROM MachineTagValue
WHERE SourceTimestamp BETWEEN [start] AND [end]

# Strategy 3: All historical (if Strategies 1-2 are empty)
# "Using X all-time parameters for this machine"
SELECT DISTINCT OpcNodeId FROM MachineTagValue
WHERE MachineCode = :machine
```

**Key Differences from Real-Time Version:**
- ❌ No "last 7 days" fallback
- ❌ No "recent parameters" suggestion
- ✅ Respects specific run window selected
- ✅ Can work with runs from any time period

**User Experience:**
```
Step 1: User selects MC_05 run from Dec 1, 2025
Step 4: "Strategy 1 (Exact Window ±2hrs): Found 187 parameters"
  → Parameters used during that run
  → All discovery tied to that specific run
```

---

### 2. `get_labeled_samples_from_runs()` - Works with Historical Runs

**Key Changes:**

#### Time Buffers (±2 hours)
```python
# EXACT run times are sacred - use them as base
start_ts = pd.to_datetime(run['StartTs']).tz_localize(None)
end_ts = pd.to_datetime(run['EndTs']).tz_localize(None)

# Add buffers only to catch nearby data
start_buffered = start_ts - pd.Timedelta(hours=2)
end_buffered = end_ts + pd.Timedelta(hours=2)

# Query uses buffered times, but centered on run window
SELECT TOP (:limit) OpcNodeId, Value, SourceTimestamp
FROM MachineTagValue
WHERE SourceTimestamp BETWEEN start_buffered AND end_buffered
```

#### ProductionRunQuality Graceful Handling
```python
# Old: Crash if ProductionRunQuality is empty
# New: Handle gracefully
try:
    quality_map = {RunId: IsOk} or {}
except:
    st.debug("ProductionRunQuality unavailable")
    quality_map = {}  # Continue with IsOk=0 for all
```

#### Sample Ordering
```python
# Changed from DESC to ASC (chronological)
ORDER BY SourceTimestamp ASC
# Reason: Chronological order better for statistical analysis
```

#### Error Messages (No Real-Time References)
```python
# Old (Real-Time Bias)
"Database may not be receiving real-time data from OPC UA currently"
"Try selecting more recent production runs (last 24 hours)"

# New (Historical Focus)
"If runs are very old (> 1 month), historical data may have been archived"
"Try expanding the time window by selecting different runs"
```

---

## File Changes

### `db_helpers.py`

#### Function 1: `get_all_params_in_time_window()`
- Lines: ~2180-2250
- Changes:
  - Removed "last 7 days" fallback
  - Added "exact run times" (no buffer) as Tier 2
  - All historical as Tier 3
  - Clear messaging showing which strategy succeeded
  - Proper SQL Server syntax (no DISTINCT + ORDER BY issues)

#### Function 2: `get_labeled_samples_from_runs()`
- Lines: ~2300-2480
- Changes:
  - Defaults `samples_per_run` from 1500 to 1200
  - Graceful ProductionRunQuality handling
  - ±2 hour buffers around exact run times
  - Per-task error isolation (one failure doesn't stop all)
  - Detailed collection statistics
  - Better error messages for historical context
  - Added `collection_stats` dict with params_queried/params_found/total_samples

#### Added Import
- `import traceback` (line 8) for better error logging

### `pages/analysis_page.py`

#### Step 4: Discover Parameters
- Updated caption from "with automatic fallback to recent data" → "that were recorded during the selected production run"
- Simplified spinner message
- Removed manual double-call fallback (now internal to function)

#### Step 6: Collect Samples
- Updated spinner message to be neutral (not mentioning "real-time")
- Completely redesigned diagnostics display:
  - Shows strategy used in function (function now emits messages)
  - 4-column metrics for clarity
  - Better ProductionRunQuality diagnostics
  - Collection statistics breakdown
- Removed error messages recommending "recent runs"
- Added historical troubleshooting guidance

---

## Usage Example: Historical Analysis Workflow

### Scenario: Analyze December 1, 2025 Production Run for MC_05

**Step 1: Load Runs**
```
User selects: Machine = MC_05
Click: "Load Last 10 Runs"
Result: Shows runs from Dec 1-10, 2025
```

**Step 2: Select Run**
```
User selects: Run from Dec 1, 14:00-16:30 (old but valid)
```

**Step 3: Discover Parameters**
```
Function: get_all_params_in_time_window('MC_05', Dec1-14:00, Dec1-16:30)

Strategy 1: Tries Dec1 12:00 to Dec1 18:30 (±2hr buffer)
  → Find 165 parameters
  ✅ Return these 165 parameters

(If empty would try exact times, then all-time historical)
```

**Step 4: Select Runs for Sample Collection**
```
User multi-selects: 3 runs from Dec 1-3 (for more data)
```

**Step 5: Collect Samples**
```
Function: get_labeled_samples_from_runs(
    'MC_05',
    3_runs_dataframe,
    165_parameters,
    samples_per_run=1200
)

For each parameter in 165:
  For each run in 3_runs:
    Query MachineTagValue 
    WHERE (start_ts - 2hr) <= SourceTimestamp <= (end_ts + 2hr)
    Get up to 1200 samples
    
Result: 150,000+ samples from 3 × 165 param/run combinations
```

**Step 6: Generate Datasheet**
```
Statistics calculated from 150k samples
Datasheet saved with:
  - Recipe: custom_param1_param2_param3
  - 165 parameters
  - 150,000 samples
  - Quality info (IsOk breakdown)
```

---

## Key Technical Details

### SQL Server Compatibility

**Fixed Issues:**
| Issue | Solution |
|-------|----------|
| `DISTINCT TOP ... ORDER BY` | Removed TOP, moved ORDER BY after DISTINCT |
| ORDER BY non-selected columns | ORDER BY only selected columns in SELECT |
| Parameter binding for TOP | Use WHERE limit or TOP with named parameters |

### Time Window Logic

```
Run Window: [StartTs=14:00, EndTs=16:30]
±2hr Buffer: [12:00, 18:30]

Query Range: 12:00 to 18:30
Why Buffer?
  - Sometimes data is recorded slightly before run starts
  - OPC synchronization might lag
  - Buffers provide reasonable coverage

Strategy 2 (if buffer fails):
  Query Range: 14:00 to 16:30 (exact)
  For old runs where data is definitely in that window

Strategy 3 (if exact fails):
  All-time for machine
  Ensures we always have SOME parameters
```

### Sample Collection Loop

```python
Total Queries = len(parameters) × len(runs)
Example: 165 params × 3 runs = 495 queries

Each Query:
  1. Get buffered timestamps (±2 hours)
  2. Query MachineTagValue with TOP 1200
  3. Order chronologically (ASC)
  4. Drop null values
  5. Add RunId + IsOk metadata
  6. Collect into results

Failure Handling:
  - Single param/run failure doesn't stop others
  - Errors only logged for first few (avoids spam)
  - Missing quality data defaults IsOk=0
```

---

## Testing Checklist

### Test 1: Recent Run (Last 48 Hours)
```
- Machine: MC_05
- Run: Dec 15, 2025
- Expected: Strategy 1 succeeds with ~200+ parameters
- Expected: Collect 50k+ samples
```

### Test 2: Old Run (1+ Weeks)
```
- Machine: MC_05
- Run: Nov 20, 2025 (25+ days old)
- Expected: Strategy 1 or 2 succeeds
- Expected: Still collects samples (if data exists)
```

### Test 3: No Run-Specific Data
```
- Run: Very old run with no data in buffer
- Expected: Falls back to Strategy 3 (all-time params)
- Expected: Shows clear messaging about strategy used
```

### Test 4: Missing Quality Data
```
- Runs not in ProductionRunQuality table
- Expected: Collects samples with IsOk=0 defaulted
- Expected: Shows diagnostic "No quality data found"
```

---

## Troubleshooting Guide

### "No samples collected"
1. Check run dates are correct
2. Verify MachineTagValue has data for selected period
3. If run > 1 month old, data may be archived
4. Try different run dates to confirm DB connectivity

### "Only X parameters discovered (much less than expected)"
1. Check run window has actual data
2. View parameter list - are they meaningful?
3. Try adjacent runs to compare parameter counts

### "Strategy 3 (All-Time) shown"
1. Normal for old runs outside ±2 buffer
2. Indicates run window had no data but parameters exist overall
3. Sample collection will use full run times (not buffer)

### "All samples have IsOk=0"
1. ProductionRunQuality has no matching runs (expected for old data)
2. Database shows no quality label for these runs
3. Samples are still valid for analysis - just unlabeled

---

## Performance Considerations

- **samples_per_run**: 1200 (changed from 1500)
  - Balances data coverage with query performance
  - Each query limited to avoid memory spike
  - Total samples = params × runs × 1200

- **Query Strategy**: 3-tier with early exit
  - Minimizes queries (stops after first success)
  - Tier 1 (buffer): ~1 second
  - Tier 2 (exact): ~1 second
  - Tier 3 (all-time): ~1 second

- **Progress Tracking**: Shows live progress
  - Updates every query completion
  - Shows param/run count for transparency

---

## Future Improvements

1. **Caching**: Cache parameter discovery for same run
2. **Batch Queries**: Combine multiple param queries
3. **Archive Handling**: Auto-detect and handle archived data
4. **Compression**: Optional sample downsampling for very old large datasets
5. **Run Comparison**: Compare parameters across multiple selected runs
