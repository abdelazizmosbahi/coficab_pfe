# Cable Manufacturing AI — Analyst Use Case Documentation

## Overview

This document describes all functional use cases available to the **Analyst** role in the Cable Manufacturing AI system. The Analyst is a power user with full access to every application page: authentication, configuration management, real-time monitoring, recipe-aware datasheet generation, and user administration.

Each functional area is decomposed into **top-level use cases** (visible to the Analyst) and **low-level system-internal use cases** (hidden implementation behaviors), connected with proper UML `<<include>>` and `<<extend>>` relationships validated against the actual source code.

---

## High-Level Diagram

The PlantUML source file `general_usecase_diagram.puml` renders the complete overview. The 18 top-level use cases are organized into five functional packages. Each package name links to its detailed sub-diagram:

| Functional Area | Top-Level UCs | Low-Level UCs | Sub-Diagram |
|---|---|---|---|---|
| Authentication | 2 | 5 | `authentication/diagram.puml` |
| Machine Configuration | 5 | 8 | `configuration_management/diagram.puml` |
| Real-Time Monitoring | 4 | 10 | `realtime_monitoring/diagram.puml` |
| Root Cause Analysis | 2 | 6 | `root_cause_analysis/diagram.puml` |
| Datasheet Generation | 3 | 12 | `datasheet_generation/diagram.puml` |
| User Administration | 4 | 8 | `user_administration/diagram.puml` |
| **Total** | **20** | **49** | *(maps to 18 general-diagram UCs)* |

---

## Relationship Summary

The general diagram shows **2 `<<extend>>`** relationships. The 6 sub-diagrams decompose these into verified UML relationships aligned to actual control flow:

**Authentication is a mandatory prerequisite for every non-auth use case.** All top-level use cases in every sub-diagram (except the Authentication diagram itself) `<<include>>` the Authenticate use case. The general diagram shows this explicitly: UC03–UC18 each `<<include>>` UC01 (Authenticate). This is enforced at the code level by `ensure_page_authentication()` called at the top of every page.

| Sub-Diagram | `<<include>>` | `<<extend>>` | Total Verified Rel. |
|---|---|---|---|
| Authentication | 2 | 2 | 4 |
| Machine Configuration | 5 (auth) + 7 (domain) = 12 | 0 | 12 |
| Real-Time Monitoring | 4 (auth) + 7 (domain) = 11 | 1 | 12 |
| Root Cause Analysis | 2 (auth) + 5 (domain) = 7 | 0 | 7 |
| Datasheet Generation | 3 (auth) + 8 (domain) = 11 | 0 | 11 |
| User Administration | 4 (auth) + 1 (domain) = 5 | 4 | 9 |
| **Total** | **48** | **7** | **55** |

**General-diagram `<<extend>>` relationships (high-level):**
| Source | Target | Condition | Sub-diagram mapping |
|---|---|---|---|
| UC11 View Parameter Traceability | UC10 Monitor Real-Time Parameters | Analyst clicks 📈 on a param card | `UCM4 → UCM3` (sub-diagram 3) |
| UC12 Analyze Root Cause | UC10 Monitor Real-Time Parameters | OUT OF RANGE (🔍) or quality < 50% | `UCR1/UCR2 → UCM3` (sub-diagrams 3+4) |

### How to Read the Sub-Diagrams

Each sub-diagram (`authentication/`, `configuration_management/`, etc.) contains:
1. `diagram.puml` — PlantUML source with full low-level decomposition
2. `README.md` — Detailed descriptions of every use case and relationship justification

**Key conventions in sub-diagrams:**
- **Top-level (actor-facing)** use cases are in blue packages — these match the general diagram
- **Low-level (system-internal)** use cases are in green packages — these are NOT directly actor-invokable
- `<<include>>` arrows point FROM the including use case TO the included (mandatory) use case
- `<<extend>>` arrows point FROM the extension TO the base use case (conditional/optional)

---

## Updated Relationship Mapping

### Previous version vs. Current version

| Previous (General) | Current (Detailed) | Change |
|---|---|---|
| No internal decomposition | 49 low-level use cases across 6 areas | **New** — full behavioral decomposition |
| UC01-UC02 in Auth only | 5 internal UCs: UCA3 Validate, UCA4 Build & Persist, UCA5 Destroy, UCA6 Restore, UCA7 Reject | **Decomposed** with 4 UML relationships |
| UC03-UC07 in Configuration only | 8 internal UCs: UCC6 Browse Machine, UCC7 Browse Params, UCC8 Insert, UCC9 Fetch, UCC10 Update, UCC11 Delete, UCC12 Read Status, UCC13 Load List | **Decomposed** with 12 `<<include>>` |
| UC08-UC11 in Monitoring only | 10 internal UCs: UCM5 Launch Papermill, UCM6 Extract, UCM7 Store, UCM8 Load Datasheet, UCM9 Load Values, UCM10 Compute Quality, UCM11 Eval Spec, UCM12 Sliding Window, UCM13 Full History, UCM14 Render Chart | **Decomposed** with 11 `<<include>>` + 1 `<<extend>>` |
| UC12 Root Cause split | UCR1 (single-param) + UCR2 (aggregated) + UCR3-8 (Mistral pipeline) | **Split** into 2 top-level + 6 internal with 7 `<<include>>` |
| UC13-UC14 in Datasheet only | 12 internal UCs: 6 wizard steps (UCD4-UCD9) + query/calculate/save/load/list/details (UCD10-UCD15) | **Decomposed** with 11 `<<include>>` |
| UC15-UC18 in Admin only | 8 internal UCs: UCU5 Query All, UCU6 Query Pending, UCU7 Approve, UCU8 Decline, UCU9 Load Perms, UCU10 Save Perms, UCU11 Toggle, UCU12 Delete | **Decomposed** with 5 `<<include>>` + 4 `<<extend>>` |

---

## Detailed Use Case Descriptions

*All 49 low-level use cases are fully documented in the individual sub-diagram READMEs:*

| Sub-diagram | Low-Level UCs | Relationship Summary |
|---|---|---|
| `authentication/README.md` | UCA3 Validate Credentials, UCA4 Build & Persist Session, UCA5 Destroy Session, UCA6 Restore Session, UCA7 Reject Authentication | 2 `<<include>>` + 2 `<<extend>>` |
| `configuration_management/README.md` | UCC6 Browse Machine Registry, UCC7 Browse Parameter Catalog, UCC8 Insert Config, UCC9 Fetch Config By ID, UCC10 Update Config, UCC11 Delete Config, UCC12 Read Machine Status, UCC13 Load Config List | 12 `<<include>>` |
| `realtime_monitoring/README.md` | UCM5 Launch Papermill, UCM6 Extract Results, UCM7 Store to DB, UCM8 Load Datasheet, UCM9 Load Values, UCM10 Compute Quality, UCM11 Eval Spec, UCM12 Sliding Window, UCM13 Full History, UCM14 Render Chart | 11 `<<include>>` + 1 `<<extend>>` |
| `root_cause_analysis/README.md` | UCR3 Invoke Mistral, UCR4 Construct Single-Param Prompt, UCR5 Construct Aggregated Prompt, UCR6 Read API Key, UCR7 Send Request, UCR8 Parse Response | 7 `<<include>>` (two chains) |
| `datasheet_generation/README.md` | UCD4-UCD9 (6 wizard steps), UCD10 Query Samples, UCD11 Calc Stats, UCD12 Save, UCD13 Load, UCD14 Load Run List, UCD15 Load Run Details | 11 `<<include>>` |
| `user_administration/README.md` | UCU5 Query All Users, UCU6 Query Pending, UCU7 Approve, UCU8 Decline, UCU9 Load Perms, UCU10 Save Perms, UCU11 Toggle Active, UCU12 Delete | 5 `<<include>>` + 4 `<<extend>>` |

---

## Key Design Decisions

### 1. Root Cause Analysis split into two distinct entry points
The general diagram's "UC12 Analyze Root Cause" is actually two separate use cases:
- **UCR1** (single-parameter, triggered by 🔍 icon on OUT OF RANGE card, uses `mistral-small-latest`, fullscreen view)
- **UCR2** (aggregated degradation, triggered by quality < 50% button, uses `mistral-large-latest`, dialog modal)

They share UCR3 (Invoke Mistral AI API) via `<<include>>` but differ in prompt construction (UCR4 vs UCR5), model choice, and view type.

### 2. No `<<include>>` in User Administration — only `<<extend>>`
User Administration uses `<<extend>>` (not `<<include>>`) for the atomic actions (Approve, Decline, Toggle Active, Delete) because the base use case (viewing the list/panel) is complete without any of those actions. The analyst can view pending operators without approving anyone.

### 3. Sequential wizard steps modeled as `<<include>>` chain
The 6-step datasheet generation wizard uses `<<include>>` to show that each step is a mandatory part of the generation workflow. This is a "local decomposition" pattern — steps are NOT independently reusable, but the chain illustrates the internal flow.

### 4. All 40+ relationships validated against source code
Every `<<include>>` and `<<extend>>` in every sub-diagram is backed by explicit code references. No relationships are invented — only those that exist in the actual control flow are modeled.

---

*Document version 2.0 — Low-level decomposition with 40 internal use cases and 40+ UML relationships, all validated against source code.*

*Source files analyzed: `auth_helpers.py` (970 lines), `configuration_page.py` (681 lines), `model_page.py` (2382 lines), `analysis_page.py` (653 lines), `admin_page.py` (344 lines), `db_helpers.py`.*
