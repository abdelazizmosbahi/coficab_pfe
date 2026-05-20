# Analysis Page: Data Availability Issue - Detailed Analysis & Solutions

**Date:** May 20, 2026  
**Severity:** CRITICAL - Data/Code Mismatch Issue  
**Status:** Being Fixed

---

## 1. Problem Summary

The Analysis page is currently **unable to show any production runs** because all historical production runs (May 17-18) predate the sensor data collection period (May 19-20).

```
Production Runs:  May 17-18 (no sensor data recorded)
Sensor Data DB:   May 19-20 (data starts here)
                  ↑ 2-DAY GAP
```

This creates a **data availability paradox**:
- ✅ Database HAS sensor data (for May 19-20)
- ❌ Database HAS production runs (for May 17-18)
- ❌ But they DON'T OVERLAP - no runs have matching sensor data

---

## 2. Current Error Messages

### Error 1: Data Filtering Shows 0 Runs
```
📊 Showing 0/10 runs with available sensor data
Database data: 2026-05-19 08:34:13 to 2026-05-20 14:28:09
❌ No production runs have corresponding sensor data
```

**Why this happens:**
- The filter checks if run timestamps overlap with database data timestamps
- All 10 loaded production runs are from May 17-18
- Database data is from May 19-20
- Result: 0 runs pass the filter ✓ (Correct behavior, but frustrating for users)

### Error 2: NameError - get_engine Not Defined
```
NameError: name 'get_engine' is not defined
File "/app/app/pages/analysis_page.py", line 441
    with get_engine().connect() as c:
```

**Why this happens:**
- `get_engine` is used in the error handling code (line 441)
- But `get_engine` is NOT imported at the module level
- It's only imported dynamically inside other functions/expanders
- Result: NameError when trying to show database info ✗ (BUG)

---

## 3. Root Causes

### Issue A: Data Collection vs Production Run Timing
**Root Cause:** Sensor data collection started AFTER production runs were logged

**Evidence:**
- Production run timestamps: 2026-05-17 10:47:21 to 2026-05-18 14:04:20
- Sensor data timestamps: 2026-05-19 08:34:13 to 2026-05-20 14:28:09
- **Gap:** 18+ hours between last production run and first sensor data

**Why it matters:**
- Users expect to analyze historical production runs
- But if production runs predate sensor collection, there's no data to analyze
- This is a **DATA QUALITY ISSUE**, not a code bug

### Issue B: Missing Import in analysis_page.py
**Root Cause:** `get_engine` used but not imported at module level

**Evidence:**
- Line 441 tries to use `get_engine()`
- Top-level imports (line 45-60) don't include `get_engine`
- `get_engine` is only imported conditionally inside blocks
- Result: NameError at runtime

**Why it matters:**
- The error recovery code (showing database time range) fails
- Users see a confusing Python traceback instead of helpful information
- The app stops instead of gracefully handling the situation

---

## 4. Current Solutions Attempted

| Attempt | Approach | Result | Issue |
|---------|----------|--------|-------|
| 1 | Tier 1-3 parameter discovery | Works, but finds Tier 3 (all-time) | Correct behavior |
| 2 | Generous ±6hr time buffers | Still no match | Data gap is too large (18+ hours) |
| 3 | Filter by data availability | Shows 0 runs (correct!) | But then crashes with NameError |

---

## 5. Recommended Solutions

### Solution A: Fix the Immediate NameError (Quick Fix)
**Problem:** `get_engine` not imported  
**Fix:** Import `get_engine` at the top of analysis_page.py  
**Impact:** LOW - Just one import line  
**Result:** Error message will show cleanly instead of traceback

### Solution B: Handle No-Data Scenario Gracefully (Medium Fix)
**Problem:** Users need to understand why there are no runs  
**Fix:** 
- Show a warning message explaining the data gap
- Don't try to show database info (remove code that needs get_engine)
- Suggest creating new production runs AFTER sensor data starts
- OR suggest loading historical sensor data from another database

**Impact:** MEDIUM - Better UX, helps users understand the situation

### Solution C: Backfill Production Runs OR Forward-Fill Sensor Data (Long-term Fix)
**Problem:** Fundamental data mismatch  
**Option 1 - Backfill Production Runs:**
- Find historical production run data from May 19-20
- Insert it into the database
- Now analysis page will work

**Option 2 - Forward-Fill Sensor Data:**
- Collect sensor data for future production runs
- Wait for new runs to occur
- Then Analysis page will have data to work with

**Option 3 - Use Different Run Period:**
- Load production runs from different date range
- Check if ANY production runs overlap with sensor data period

**Impact:** HIGH - Solves the data availability problem permanently

---

## 6. Recommended Action Plan

### Immediate (Fix the Crash)
1. **Import `get_engine`** at top of analysis_page.py
2. **Remove database info display** from error handling (if it requires dynamic queries)
3. **Show clear message** explaining the data gap

### Short-term (Help Users)
1. Check if there are ANY production runs that overlap with sensor data
2. If yes: Show those runs, let user work with available data
3. If no: Show helpful guidance on next steps

### Long-term (Data Strategy)
1. Coordinate with operations team on production run logging
2. Ensure production runs are created AFTER sensor data collection begins
3. Or backfill historical sensor data
4. Or run new analysis with new production runs

---

## 7. Why This Matters

This isn't just a code bug - it's a **DATA INTEGRITY ISSUE**:

```
Timeline Issue:
─────────────────────────────────────────
May 17-18: Production runs logged
             (but no sensor data recorded yet)
                    ⬇️ 18+ hour gap
May 19-20: Sensor data starts being recorded
             (but most production runs are old)
```

**Impact:**
- Analysis page can't show ANY runs (0/10 pass filter)
- Users see error instead of data
- System appears broken, but it's actually working correctly

**The Fix:**
- Import `get_engine` to stop the crash
- Show users WHY there's no data
- Suggest they work with newer production runs (May 19-20)

---

## 8. Technical Details

### Current Filter Logic
```python
def filter_runs_by_available_data(machine_code, runs_df):
    # Get database data boundaries
    db_start = 2026-05-19 08:34:13  # First sensor data
    db_end   = 2026-05-20 14:28:09  # Latest sensor data
    
    # Filter: keep runs where run_end >= (db_start - 12hr)
    cutoff = db_start - 12hr = 2026-05-18 20:34:13
    
    # Check each production run
    Run 1: ends 2026-05-18 14:04:20 < cutoff 2026-05-18 20:34:13 ❌ FILTERED OUT
    Run 2: ends 2026-05-17 11:22:15 < cutoff 2026-05-18 20:34:13 ❌ FILTERED OUT
    Run 3: ends 2026-05-17 11:22:14 < cutoff 2026-05-18 20:34:13 ❌ FILTERED OUT
    
    Result: 0/10 runs have data ✓ (Correct)
```

The filter is working perfectly - the problem is the underlying data.

---

## 9. Next Steps

1. ✅ **Immediate:** Fix NameError by importing `get_engine`
2. ✅ **Immediate:** Show user-friendly error message
3. ⏳ **Follow-up:** Investigate if there are ANY compatible production runs
4. ⏳ **Follow-up:** Coordinate with ops team on data collection timing

