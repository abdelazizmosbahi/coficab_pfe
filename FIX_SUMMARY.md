# Real-Time Parameter Cards Fix - Summary

## Issues Addressed

### Issue 1: "⚠️ NO DATA" in Parameter Cards
**Cause**: `merged_readings` dictionary was completely empty (all values None)
- Function `load_current_machine_values()` was silently catching exceptions and returning `{}`
- Impossible to debug since errors were swallowed
- No visibility into what parameters were being queried or if DB had data

**Fixes Applied**:
1. **Error logging** (db_helpers.py): Modified exception handler to print stack trace
   - Now shows actual database errors instead of silent failure
   
2. **Debug expander** (model_page.py, lines 1338-1356): Added conditional debug panel that only appears when ALL parameter values are None
   - Shows parameters being queried
   - Shows merged_readings entry count and sample entries
   - Helps identify if it's a data matching issue or database connectivity problem

---

### Issue 2: Numpy Type Comparison Error  
**Error**: `ufunc 'greater' did not contain a loop with signature matching types (<class 'numpy.dtypes.Float64DType'>, <class 'numpy.dtypes.StrDType'>)`
**Cause**: Database returns parameter values as strings, but comparison operators expect floats
- `v_min`, `v_max`, `v_mean` were strings from DB
- `hist_data["Value"]` column contained non-numeric strings
- Comparison operations like `lo <= current_val <= hi` fail with type mismatch

**Fixes Applied**:

1. **Traceability data conversion** (model_page.py, line 744):
   - Added `hist_data["Value"] = pd.to_numeric(hist_data["Value"], errors="coerce")`
   - Safely converts strings to floats, replacing unparseable values with NaN
   
2. **Overlay data conversion** (model_page.py, line 798):
   - Added same `pd.to_numeric()` for overlay_hist_data
   - Ensures both primary and overlay tracks are numeric
   
3. **Specification value conversions**:
   - Traceability: Already using safe_float(v_min, v_max, v_mean) ✓
   - Trend overview (model_page.py, line 1465-1467): Updated to use safe_float()
   - Card display (model_page.py, line 1496-1498): Already using safe_float() ✓

4. **Data aggregation fixes** (model_page.py, lines 746-747, 803-808):
   - Changed from direct `.astype(float)` to `.dropna().tolist()`
   - Prevents errors when converting lists with NaN values
   - Properly handles None and unparseable values

---

## Files Modified

### 1. `cable_maintenance_ai/app/db_helpers.py`
**Line 1265-1267**: Added exception logging (was previously silent)
```python
except Exception as e:
    import traceback
    print(f"ERROR in load_current_machine_values: {e}")
    traceback.print_exc()
    return {}
```

### 2. `cable_maintenance_ai/app/pages/model_page.py`

**Lines 1328-1356**: Added debug expander (shows when no data)
- Displays parameters being queried
- Shows merged_readings status
- Sample entries for debugging

**Line 744**: Fixed hist_data Value column type conversion
```python
hist_data["Value"] = pd.to_numeric(hist_data["Value"], errors="coerce")
```

**Lines 746-747**: Safe aggregation (handles NaN after conversion)
```python
valid_vals = hist_data["Value"].dropna().tolist()
all_vals = valid_vals + [v_min, v_max, v_mean if v_mean else 0]
```

**Line 798**: Added overlay data conversion same as above

**Lines 803-808**: Safe data value aggregation for overlay
- Using `.dropna().tolist()` instead of `.astype(float)`

**Lines 1465-1467**: Trend overview now uses safe_float()
- Was using direct `float()` conversion
- Now safe against string/None values

---

## How to Verify the Fixes

### Debug Output
1. Open the app and select a configuration
2. If all parameter cards show "NO DATA", look for the debug expander below the configuration selector
3. Expand it to see:
   - What parameters were queried
   - How many have values vs None
   - Sample data entries

### Error Messages
1. Check the terminal/console when running streamlit
2. If database errors occur, they will now be printed (previously hidden)
3. Errors will show in format: `ERROR in load_current_machine_values: [error message]`

### Traceability Charts
1. Click any parameter card's 📈 button to view traceability
2. Should display without numpy type errors
3. If values are all NaN, this indicates parameter doesn't exist in DB or has no data

---

## Remaining Gaps to Investigate

If debug panel shows NO DATA:
- Parameters queried count is 0 → Config has no parameters
- Parameters queried > 0 but merged_readings empty → load_current_machine_values() not returning anything
- Likely causes:
  1. Parameter names don't match OpcNodeIds in database
  2. Machine code is incorrect
  3. MachineTagValue table is empty for this machine

**Next diagnostic step**: Run `python diagnose.py` (in project root) to check:
- What parameters are in the config
- What OpcNodeIds exist in MachineTagValue
- Which ones match
- Available machines in database

