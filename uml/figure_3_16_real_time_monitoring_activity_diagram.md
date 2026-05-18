# Figure 3.16 — Real-Time Monitoring Activity Diagram

**Location:** Chapter 3 — Conception / §3.2.4.4  
**Type:** UML Activity Diagram  

---

## Purpose

Real-time monitoring workflow. The **Analyst** selects a configuration, the system loads data, and a continuous 1-second loop monitors live values, detects violations, and triggers Mistral AI.

---

## Swimlanes

| Lane | Actions |
|------|---------|
| **Analyst** | Selects config, views data, triggers analysis |
| **System** | Auth check, data loading, monitoring loop, quality computation, chart rendering |

---

## Flow

```
[Start] → Analyst navigates to Realtime page
          ↓
    System: ensure_page_authentication('model_page')
          ↓
         [Authenticated?]
          ↓           ↓
       [Yes]       [No]
          ↓           ↓
    System loads  Redirect to
    configs       login page
          ↓           ↓
    System shows  [End]
    config dropdown
          ↓
    Analyst selects configuration
          ↓
    System loads reference datasheet
    (Min, Max, Mean, StdDev)
          ↓
    System checks machine LineSpeed status
          ↓
         [Machine status?]
          ↓                   ↓
    [Working(LineSpeed>0)]  [Standby(LineSpeed=0)]
          ↓                   ↓
    ┌──────────────────┐  Display "Standby"
    │ MONITORING LOOP   │  Keep checking
    │ (every 1 second)  │      ↓
    │                   │  [LineSpeed > 0?]
    │ Fetch values      │    ↓      ↓
    │ from MachineTag   │  [Yes]  [No]
    │     ↓             │    ↓      ↓
    │ Compare vs Min/Max│  Enter   Stay
    │     ↓             │  loop   Standby
    │ Compute quality   │    ↓
    │     ↓             │  [End]
    │ Render cards      │
    │ with status       │
    │     ↓             │
    │ [Out of range?]   │
    │  ↓        ↓       │
    │ [Yes]    [No]     │
    │  ↓        ↓       │
    │ Show      skip    │
    │ badges            │
    │  ↓                │
    │ [Quality < 50%?]  │
    │  ↓        ↓       │
    │ [Yes]    [No]     │
    │  ↓        ↓       │
    │ Trigger   skip    │
    │ Mistral AI        │
    │  ↓                │
    │ Display analysis  │
    └──────────────────┘
          ↓
    [Session expires or navigates away]
          ↓
       [End]
```

---

## Decision Nodes

| # | Decision | Branches |
|---|----------|----------|
| D1 | Authenticated? | [Yes] / [No] |
| D2 | Machine status? | [Working] / [Standby] |
| D3 | Any param out of range? | [Yes] / [No] |
| D4 | Quality < 50%? | [Yes] / [No] |

---

## Notes for Diagram Generation

- 2 swimlanes: **Analyst** (left), **System** (right).
- Monitoring loop as large rounded rectangle labeled `"Loop: every 1 second (@st.fragment)"`.
- `opt` regions inside loop for violation badges and Mistral trigger.
- Standby path as alternative with LineSpeed recheck.
- Quality formula note: `"Per param: target=(min+max)/2, spread=(max-min)/2, score=max(0, 100-|deviation|/spread*50). Final = mean(all param scores)"`.

---

## PlantUML Code

```plantuml
@startuml
|Analyst|
start
:navigate to Realtime page;

|System|
:ensure_page_authentication('model_page');
if (Authenticated?) then (yes)
  :load all configurations\nwith machine status;
  :show configuration dropdown;
  |Analyst|
  :select a configuration;
  |System|
  :load reference datasheet\n(Min, Max, Mean, StdDev);
  :check machine LineSpeed status;
  if (Machine status?) then (Working - LineSpeed > 0)
    :start 1-second monitoring loop;
    while (every 1 second)
      :fetch latest values\nfrom MachineTagValue;
      :compare each value\nagainst Min/Max;
      :compute quality probability\ntarget = (min+max)/2\nspread = (max-min)/2\nscore = max(0, 100-|deviation|/spread*50)\nfinal = mean(all param scores);
      :render parameter cards\nwith color-coded status;
      if (Any param out of range?) then (yes)
        :show violation badges;
        if (Quality < 50%?) then (yes)
          :trigger Mistral AI\nroot cause analysis;
          :display analysis results;
        else (no)
        endif
      else (no)
      endif
    endwhile
  else (Standby - LineSpeed = 0)
    :display "Standby" message;
    :keep checking LineSpeed;
    if (LineSpeed > 0?) then (yes)
      (N) --> |System|
    else (no)
      :stay in Standby;
      stop
    endif
  endif
else (no)
  :redirect to login page;
  stop
endif
@enduml
```
