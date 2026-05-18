# Figure 3.16 — Real-Time Monitoring Activity Diagram

> Continuous monitoring loop: load configuration, check machine status, fetch and compare live values, render cards, and trigger root cause analysis on anomaly.

```mermaid
flowchart TD
    START(["Operator selects
        a configuration"])
    LOAD_DS["Load reference datasheet
        from latest analysis results"]
    CHECK_STATUS{"Check machine
        LineSpeed status?"}
    STANDBY["Display standby message
        Machine is not running"]
    ACTIVE["Machine is Working
        Start 1-second monitoring loop"]
    FETCH_VALS["Fetch latest values
        from MachineTagValue"]
    COMPARE["Compare each value
        against Min/Max spec"]
    COMPUTE_SCORE["Compute quality
        probability score"]
    RENDER_CARDS["Render parameter cards:
        • STABLE (green)
        • NEAR MIN / NEAR MAX (yellow)
        • OUT OF RANGE (red)
        • NO DATA (gray)
        • STALE (orange)"]
    UPDATE_GAUGE["Update quality prediction
        probability gauge"]
    CHECK_RANGE{"Any parameter
        out of range?"}
    SHOW_BADGE["Show violation
        badges on cards"]
    CHECK_PROB{"Quality probability
        < 50%?"}
    TRIGGER_MISTRAL["Auto-trigger Mistral AI
        root cause analysis"]
    WAIT["Wait 1 second"]

    START --> LOAD_DS
    LOAD_DS --> CHECK_STATUS
    CHECK_STATUS -->|Standby| STANDBY
    STANDBY --> CHECK_STATUS
    CHECK_STATUS -->|Active| ACTIVE
    ACTIVE --> FETCH_VALS
    FETCH_VALS --> COMPARE
    COMPARE --> COMPUTE_SCORE
    COMPUTE_SCORE --> RENDER_CARDS
    RENDER_CARDS --> UPDATE_GAUGE
    UPDATE_GAUGE --> CHECK_RANGE
    CHECK_RANGE -->|Yes| SHOW_BADGE
    CHECK_RANGE -->|No| CHECK_PROB
    SHOW_BADGE --> CHECK_PROB
    CHECK_PROB -->|Yes| TRIGGER_MISTRAL
    TRIGGER_MISTRAL --> WAIT
    CHECK_PROB -->|No| WAIT
    WAIT --> FETCH_VALS

    classDef start fill:#e8f0fe,stroke:#1a73e8,stroke-width:2px;
    classDef decision fill:#fef7e0,stroke:#f9ab00,stroke-width:1px;
    classDef process fill:#e6f4ea,stroke:#34a853,stroke-width:1px;
    classDef alert fill:#fce8e6,stroke:#ea4335,stroke-width:1px;
    class START start;
    class CHECK_STATUS,CHECK_RANGE,CHECK_PROB decision;
    class LOAD_DS,STANDBY,ACTIVE,FETCH_VALS,COMPARE,COMPUTE_SCORE,RENDER_CARDS,UPDATE_GAUGE,WAIT process;
    class SHOW_BADGE,TRIGGER_MISTRAL alert;
```
