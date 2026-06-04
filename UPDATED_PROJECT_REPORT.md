# Cable Manufacturing AI — Full Project Report

**COFICAB — Internship Project**
**Author:** Intern, ELLOUMI Group
**Supervisors:** Mr. Malek Boudhief, Ms. Mouna Bouzazi
**Period:** January — May 2025
**Version:** 1.0 — June 2026

---

## Acknowledgments

I would like to express my sincere gratitude to the team at COFICAB for providing me with the opportunity to undertake this internship and for their unwavering support throughout the process. Their collaborative environment and resources were instrumental in the successful development of this project. Special thanks go to my supervisors, Mr. Malek Boudhief and Ms. Mouna Bouzazi, for their invaluable assistance, expert guidance, and encouragement during the internship. Their insights and feedback were pivotal in shaping the project's direction and ensuring its alignment with professional standards. Without their contributions, this work would not have been possible.

I would also like to thank the ELLOUMI Group for fostering a culture of innovation and excellence that made this project a reality.

---

## Table of Contents

1. General Introduction
2. Chapter 1: Preliminary Study
   - 1.1 Project Presentation
   - 1.2 Software Development Methodology
   - 1.3 Presentation of the Host Company
   - 1.4 Technologies and Tools
   - 1.5 Architecture
   - 1.6 Conclusion
3. Chapter 2: Requirements Analysis and Specification
   - 2.1 Introduction
   - 2.2 User Profiles
   - 2.3 Functional Requirements
   - 2.4 Non-Functional Requirements
   - 2.5 Use Case Diagrams
   - 2.6 Kanban Task Board
   - 2.7 Conclusion
4. Chapter 3: Conception
   - 3.1 Introduction
   - 3.2 UML Diagrams
   - 3.3 Conclusion
5. Chapter 4: Realization
   - 4.1 Introduction
   - 4.2 Implementation
   - 4.3 Database Tables
   - 4.4 Key Implementation Components
   - 4.5 User Interface
   - 4.6 Deployment and Monitoring
   - 4.7 Conclusion
6. General Conclusion and Future Perspectives

---

## List of Figures

- Figure 1.1 — COFICAB Key Figures 2024 infographic
- Figure 2.1 — General Use Case Diagram
- Figure 2.2 — Operator Use Case Diagram
- Figure 2.3 — Analyst Use Case Diagram
- Figure 3.1 — Configuration Management Use Case Diagram
- Figure 3.2 — Real-Time Monitoring Use Case Diagram
- Figure 3.3 — Analysis Datasheet Generation Use Case Diagram
- Figure 3.4 — Mistral AI Root Cause Analysis Use Case Diagram
- Figure 3.5 — Class Diagram — System Entities
- Figure 3.6 — Authentication Sequence Diagram
- Figure 3.7 — Machine Configuration Sequence Diagram
- Figure 3.8 — Real-Time Monitoring Sequence Diagram
- Figure 3.9 — Datasheet Analysis Sequence Diagram
- Figure 3.10 — Root Cause Analysis Sequence Diagram
- Figure 3.11 — User Login Activity Diagram
- Figure 3.12 — User Registration Activity Diagram
- Figure 3.13 — Machine Configuration Activity Diagram
- Figure 3.14 — Real-Time Monitoring Activity Diagram
- Figure 4.1 — Home Page Interface Screenshot
- Figure 4.2 — Authentication Page Interface Screenshot
- Figure 4.3 — Configuration Page Interface Screenshot
- Figure 4.4 — Real-Time Monitoring Interface Screenshot
- Figure 4.5 — Analysis Datasheet Interface Screenshot
- Figure 4.6 — Traceability Chart Interface Screenshot
- Figure 4.7 — Mistral AI Root Cause Analysis Screenshot
- Figure 4.8 — Admin Panel Interface Screenshot

---

## List of Tables

- Table 3.1 — Use Case: Configure Machine
- Table 3.2 — Use Case: Monitor Parameters
- Table 3.3 — Use Case: Generate Datasheet
- Table 3.4 — Use Case: Analyze Root Cause
- Table 3.5 — Authentication Flow
- Table 3.6 — Machine Configuration Flow
- Table 3.7 — Real-Time Monitoring Flow
- Table 3.8 — Recipe Datasheet Generation Flow
- Table 3.9 — AI-Based Root Cause Analysis Flow
- Table 3.10 — Authentication Session Flow
- Table 3.11 — User Registration Flow
- Table 3.12 — Configuration Creation Flow
- Table 3.13 — Real-Time Monitoring Flow
- Table 4.1 — Environment Variables

---

## General Introduction

This internship report presents Cable Manufacturing AI, a Streamlit-based monitoring and analysis system for cable production that unifies SQL Server-backed OPC UA trace data, machine configuration management, and Mistral AI-powered root cause analysis to deliver real-time parameter monitoring and recipe-aware datasheet generation for operator decision support. The project centers on three operational pillars — machine configuration management, real-time parameter monitoring with specification comparison, and recipe-aware production datasheet analysis — so operators can compare current values against expected ranges, track deviations across production runs, and generate statistical baselines from labeled samples.

The core problem addressed is the gap between high-frequency sensor signals and actionable quality insight on the shop floor, where raw data alone makes it difficult to detect out-of-spec behavior early or understand parameter behavior across production runs. Cable Manufacturing AI solves this by transforming event-based machine tags into structured monitoring views, applying specification-range comparison for real-time status, and presenting interpretable dashboards that highlight out-of-range parameters while providing traceable context for root-cause analysis via Mistral AI.

The result is a scalable, data-driven workflow that supports both live monitoring and historical analysis within a single, consistent Streamlit application. This report details the development of Cable Manufacturing AI, organized into four chapters:

- **Chapter 1** provides a preliminary study, presenting the project and outlining the methodology, tools, and architecture.
- **Chapter 2** specifies requirements, including user profiles, functional and non-functional requirements, and the Kanban task board.
- **Chapter 3** describes the conception phase, focusing on UML diagrams for system design.
- **Chapter 4** discusses the realization, covering implementation and user interface development.

And concludes with a summary of results, challenges encountered, and future perspectives.

---

# Chapter 1: Preliminary Study

## 1.1 Project Presentation

### 1.1.1 Introduction

This preliminary study presents Cable Manufacturing AI, a comprehensive Streamlit-based monitoring, configuration, and analysis system tailored for cable production lines at COFICAB. This chapter presents the project, analyzes the operational challenges, details the proposed solution with its interconnected components, and outlines the development methodology, technologies, and architecture.

The application is built around three core workflows — real-time OPC UA monitoring, parameter traceability, and recipe-aware datasheet analysis — while the Configuration Management Module forms the backbone of the system.

### 1.1.2 Problem Statement

In cable production, high-frequency sensor data and recipe parameters are collected via OPC UA and stored as raw time-series events in the `MachineTagValue` table. Operators and analysts lack a unified platform that connects live parameter values to expected specification ranges, integrates historical behavior analysis, and generates statistical reference datasheets from labeled production runs.

Existing setups separate configuration management, reference datasheet generation, real-time monitoring, and quality analysis, resulting in:

- Delayed detection of out-of-spec parameter deviations
- Difficulty performing root-cause analysis when quality issues arise
- Limited visibility into parameter behavior across production runs
- Fragmented workflows requiring manual data gathering across multiple tools

This separation of concerns prevents COFICAB from achieving proactive, data-driven quality management in its high-volume cable manufacturing environment.

### 1.1.3 Proposed Solution

Cable Manufacturing AI is a unified, SQL Server-backed system that seamlessly integrates machine configuration management, automated reference datasheet generation, real-time parameter monitoring, and AI-powered root cause analysis through Mistral. The system supports two primary user roles:

- **Operators** — Monitor live production, detect out-of-spec parameters, and respond to deviations; can configure machines and generate datasheets if granted access by an Analyst.
- **Analysts** — Configure machines, select monitoring and recipe parameters, build reference datasheets from labeled production runs, and manage operator accounts and page-level permissions.

The solution is structured around four interconnected components that form the Cable Manufacturing AI platform:

1. **Configuration Page (Streamlit UI)** — Full CRUD interface for creating, editing, and managing machine configurations with live machine-status indicators based on LineSpeed data. Supports two configuration types: `realtime` (for live monitoring) and `analysis` (for datasheet generation).

2. **Model Page (Streamlit UI)** — Real-time parameter monitoring with specification-violation badges, traceability charts (3-second sliding window + full timeline with overlay comparison), and AI-generated root-cause analysis via Mistral when parameters exceed safe ranges.

3. **Analysis Page (Streamlit UI)** — Recipe-aware reference datasheet generator that loads production runs, collects labeled samples (up to 1,200 per parameter per run), and computes statistical baselines (Min, Max, Mean, StdDev, SampleCount) with quality correlation using the `ProductionRunQuality.IsOk` flag. Supports both production-run-based and time-window-based analysis modes.

4. **Notebook-Based Analysis Engine (optional)** — Jupyter notebooks executed via Papermill that analyze historical data per configuration and store reference datasheets in the database. Referenced by `model_page.py` for initial data analysis.

Key features include OPC UA data connectivity via `MachineTagValue` table, specification bands with visual violation badges, sliding-window real-time traceability charts, Mistral AI for natural-language root cause analysis, full audit trails through `productionrun` and `ProductionRunQuality` tables, and role-based page-level access control with operator approval workflow.

## 1.2 Software Development Methodology

### 1.2.1 Justification of Kanban

The project adopts Kanban for its flexibility, which is ideal for solo development. Tasks flow through a board with columns To Do, In Progress, and Done without fixed sprints, enabling continuous delivery and real-time adjustments as new requirements emerge during development.

As a solo developer working on the complex and evolving Cable Manufacturing AI project, Kanban is the superior choice. It eliminates Scrum's overhead of ceremonies and rigid sprints, enabling:

- Continuous progress without interruption for sprint planning
- Immediate incorporation of new insights from stakeholder feedback
- Full flexibility to adjust priorities at any time based on emerging requirements
- Visual workflow management using a simple board with clear task states

The Kanban board was maintained throughout the project lifecycle (January — May 2025) and is detailed in Chapter 2 with bi-weekly snapshots.

## 1.3 Presentation of the Host Company

### 1.3.1 History and Membership in the ELLOUMI Group

COFICAB is the leading global partner in the design, manufacturing, and sales of cables and wires. Founded in 1992 by Mr. Hichem Elloumi in Tunisia, the company is a proud member of the ELLOUMI Group, an industrial conglomerate established in 1946 by Mr. Taoufik Elloumi.

What began as a small Tunisian enterprise has grown into a major international player through exceptional organic growth and strategic expansion. The ELLOUMI Group has evolved through key milestones: SOTEE (1946), Chakira Distribution (1946), Chakira (1963), TEM (1982), COFAT (1984), and later STIFEN (1996), CHAKIRA IMMOBILIER (2000), and BTK (2021). COFICAB itself was established in 1992 and quickly became the group's flagship in automotive, energy, and appliance cables.

Mr. Hichem Elloumi, Chairman and CEO, emphasizes that COFICAB is fully committed to sustainability-driven growth and innovation, aiming to leave a better world for future generations. The company continues to expand its global footprint to be closer to customers while reducing its carbon footprint and supply-chain impact.

### 1.3.2 Key Figures (2024)

Today COFICAB operates on an impressive global scale:

- 4 billion USD turnover
- 42 million kilometers of wires and cables sold
- No. 1 worldwide with 23% market share in automotive industry cables and wires
- 20 production sites (+ 5 ongoing)
- 14 sales offices
- 4 R&D+I centers of excellence
- 9,000 employees
- Presence on 4 continents and in 16 countries

*Figure 1.1 – COFICAB Key Figures 2024 infographic.*

### 1.3.3 Vision

COFICAB's vision is to be the best-in-class partner for automotive cables and wires, committed to exceeding customer expectations through sustainable growth by:

- Expanding global presence to serve customers worldwide
- Striving for technology and operational excellence
- Sharing values and success with employees and partners

## 1.4 Technologies and Tools

The project utilizes the following technologies and tools:

| Category | Technology | Usage |
|----------|-----------|-------|
| Frontend & UI | Streamlit 1.x | Python-based web framework, multi-page navigation, caching, state management |
| Backend Logic | Python 3.11 + SQLAlchemy 2.0 | Database connectivity, connection pooling, parameterized SQL queries |
| Database | Microsoft SQL Server | Production data store (MachineTagValue, productionrun, model_schema tables) |
| Visualization | Plotly 5.x | Interactive real-time traceability charts, spec range visualization, overlay comparison |
| AI Integration | Mistral AI API (mistral-small-latest) | Natural-language root-cause analysis for parameter anomalies |
| Connectivity | pyodbc 5.0 + ODBC Driver 18 | Database driver for MSSQL connection |
| Authentication | PBKDF2-HMAC-SHA256 | Password hashing (120,000 iterations) with HMAC-signed session tokens |
| Containerization | Docker + Docker Compose | Application packaging and deployment with resource limits |
| CI/CD | GitHub Actions | Automated build and push to GitHub Container Registry (GHCR) |
| Data Processing | pandas 2.x, numpy 1.x | DataFrame manipulation, statistics, numerical operations |
| Notebook Execution | Papermill + nbformat | Optional parameterized Jupyter notebook execution for analysis runs |
| Tools | VS Code, Git/GitHub, python-dotenv | Development environment, version control, environment configuration |

**Note on scikit-learn, xgboost, joblib:** These packages are listed in `requirements.txt` but are **not actively used** by any Streamlit application page. No ML model loading, training, or inference exists in the current application codebase. These dependencies are remnants of a prior, non-functional ML pipeline and are excluded from this report's feature documentation.

## 1.5 Architecture

### 1.5.1 Application Architecture

The system follows a modular Streamlit multi-page architecture organized around three core operational pillars:

- **Configuration Layer** (`model_schema.machine_configuration` table) — Stores monitoring and recipe parameter selections per machine with CRUD support
- **Real-Time Monitoring Layer** (`model_page.py`) — Loads reference datasheets, fetches live values from `MachineTagValue`, compares against specification ranges, and renders traceability charts
- **Analysis Layer** (`analysis_page.py`) — Loads production runs, collects labeled sensor samples, computes parameter statistics, and saves reference datasheets

**System Architecture Diagram:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Streamlit Application                       │
│                                                                     │
│  ┌──────────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Authentication  │  │   Page UI    │  │    Data Layer        │  │
│  │   & Session Mgmt │  │  (5 Pages)   │  │  (db_helpers.py)     │  │
│  │ (auth_helpers.py)│  │              │  │                      │  │
│  └────────┬─────────┘  └──────┬───────┘  └──────────┬───────────┘  │
│           │                  │                      │              │
│           └──────────────────┼──────────────────────┘              │
│                              │                                     │
│                       ┌──────┴──────┐                               │
│                       │ db_helpers  │                               │
│                       │  (cached)   │                               │
│                       └──────┬──────┘                               │
└──────────────────────────────┼──────────────────────────────────────┘
                               │
                     ┌──────────┴──────────┐
                     │  SQLAlchemy + pyodbc │
                     │  (ODBC Driver 18)    │
                     └──────────┬──────────┘
                               │
                     ┌──────────┴──────────┐
                     │   Microsoft SQL     │
                     │     Server          │
                     │                     │
                     │ • MachineTagValue   │
                     │ • productionrun     │
                     │ • model_schema.*    │
                     │ • ProductionRunQuality│
                     │ • tags_mapping      │
                     └─────────────────────┘

                     ┌─────────────────────┐
                     │   Mistral AI API    │
                     │ (HTTP REST)         │
                     └─────────────────────┘
```

**Data Flow:**

1. OPC UA sensors write data to `MachineTagValue` (time-series events)
2. Configuration page saves machine setups to `model_schema.machine_configuration`
3. Analysis page loads production runs from `productionrun` table, collects samples from `MachineTagValue`, computes statistics, and stores reference datasheets in `model_schema.parameter_reference_datasheet`
4. Model page loads reference datasheets and compares live values from `MachineTagValue` in real-time with 1-second auto-refresh
5. Out-of-spec parameters trigger Mistral AI for natural-language root-cause analysis

**Backend Communication:**

- **Database**: Connection via `db_connection.py` → `get_db_engine()` → `get_engine()` (cached with `@st.cache_resource`). Connection URL built from `.env` environment variables (`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`). Uses `mssql+pyodbc` dialect with `TrustServerCertificate=yes`.
- **Mistral AI**: Direct HTTP POST to `https://api.mistral.ai/v1/chat/completions` with Bearer token auth. API key and model configurable via `.env` (`MISTRAL_API_KEY`, `MISTRAL_MODEL`). Used exclusively for parameter anomaly root cause analysis in `model_page.py`.

### 1.5.2 Database

The main SQL Server tables support structured monitoring and traceability:

| Table | Schema | Purpose |
|-------|--------|---------|
| `machine_configuration` | `model_schema` | User-saved configurations with JSON parameter lists (monitoring + recipe) |
| `MachineTagValue` | `dbo` | Time-series sensor events (core data source — OPC UA tags) |
| `productionrun` | `dbo` | Production run metadata with time ranges |
| `ProductionRunQuality` | `dbo` | Quality labels (IsOk flag) per production run |
| `parameter_reference_datasheet` | `model_schema` | Statistical reference ranges with recipe context |
| `analysis_results_[MACHINE]` | `model_schema` | Per-machine parameter-level analysis history with RunSequence tracking |
| `users` | `model_schema` | User accounts with PBKDF2 password hashing and page permissions |
| `datasheet_runs` | `model_schema` | Analysis run metadata tracking |
| `tags_mapping` | `dbo` | Machine-to-parameter mappings |
| `analysis_results` | `model_schema` | Notebook analysis output storage (JSON + optional BLOB) |
| `parameter_optimal_windows` | `model_schema` | Learned stable window parameters per sensor |

## 1.6 Conclusion

This preliminary study establishes the foundation of Cable Manufacturing AI as a unified, production-ready monitoring and analysis system designed specifically for COFICAB's cable manufacturing environment. The platform, combining SQL Server-backed traceability, real-time specification monitoring, and Mistral AI insights in Streamlit, directly addresses the gap between raw sensor data and actionable quality insight.

The modular architecture provides scalability, interpretability, and operational value, preparing the ground for detailed requirements specification and implementation in the following chapters.

---

# Chapter 2: Requirements Analysis and Specification

## 2.1 Introduction

This chapter defines the requirements for Cable Manufacturing AI using Kanban's iterative workflow. It identifies user profiles, specifies functional and non-functional requirements, describes use case diagrams, and presents the Kanban task board, aligning with the platform's goal of unified, data-driven quality monitoring with real-time AI support.

## 2.2 User Profiles

This section identifies two primary user roles for the Cable Manufacturing AI system:

**Operator**: Shop-floor personnel responsible for monitoring live production parameters. Operators view real-time data, detect out-of-spec conditions, and respond to alerts. They can configure machines and generate datasheets only if granted explicit page-level access by an Analyst. New operator registrations require Analyst approval before the account becomes active.

**Analyst**: Quality engineers and data analysts responsible for managing the system. Analysts configure machines, select monitoring and recipe parameters, generate reference datasheets, and investigate quality correlations. Additionally, Analysts serve as system administrators: they approve or decline operator registration requests, view all registered users, manage per-operator page-level access permissions via the Admin Panel, and manage user lifecycle (activate, disable, delete). Analysts have unrestricted access to all system pages.

## 2.3 Functional Requirements

The following Functional Requirements (FR) ensure Cable Manufacturing AI meets user and system needs:

| ID | Requirement | Description |
|----|------------|-------------|
| FR1 | Authenticate | Users log in with User ID and password via PBKDF2-secured authentication |
| FR2 | Register | New users create accounts with User ID and password |
| FR3 | Logout | Authenticated users securely end their session |
| FR4 | View Home Dashboard | Users see system overview, workflow guide, and key metrics |
| FR5 | View Machine Status | Users see all machines with real-time LineSpeed-based status (Working/Standby/Inactive) |
| FR6 | Create Configuration | Analysts create new machine configurations with monitoring and recipe parameters |
| FR7 | Edit Configuration | Analysts modify existing machine configurations |
| FR8 | Delete Configuration | Analysts remove machine configurations |
| FR9 | View Configurations | Analysts browse and search saved configurations by machine |
| FR10 | Select Monitoring Parameters | Analysts choose which OPC NodeIds to track for a machine |
| FR11 | Designate Recipe Parameters | Analysts mark a subset of monitoring parameters as recipe-defining |
| FR12 | Save Configuration | System persists configurations to machine_configuration table |
| FR13 | Load Production Runs | System retrieves production runs for a selected machine |
| FR14 | Filter Runs by Quality | System filters production runs by IsOk quality flag |
| FR15 | Select Sample Runs | Analysts choose production runs for sample collection |
| FR16 | Collect Labeled Samples | System collects up to 1,200 samples per parameter per run from MachineTagValue with 12-hour time buffer |
| FR17 | Calculate Statistics | System computes Min, Max, Mean, StdDev, SampleCount per parameter |
| FR18 | Correlate Quality | System labels samples with IsOk from ProductionRunQuality table |
| FR19 | View Datasheet | Analysts view generated reference datasheets with parameter statistics and quality counts |
| FR20 | Browse Previous Datasheets | System shows previous analysis runs for comparison with metrics (sample count, OK %, timestamps) |
| FR21 | Time Window Analysis | Analysts can define custom time windows to find production runs within a date range |
| FR22 | Select Configuration for Monitoring | Operators select a saved configuration to monitor |
| FR23 | Display Reference Ranges | System shows Min/Max/Mean specification ranges from analysis results |
| FR24 | Show Real-Time Values | System displays current parameter values from MachineTagValue with 1-second auto-refresh |
| FR25 | Show Spec Violation Badges | System visually highlights out-of-range parameters with gap distance and percentage of spec span |
| FR26 | Display Parameter Cards | System shows parameter cards with color-coded status, current value, specification range, and last update time |
| FR27 | Show 3-Second Traceability | System renders real-time sliding-window charts (last 3 seconds) with spec range background |
| FR28 | Show Full Timeline | System renders complete historical traceability charts with snapshot capability |
| FR29 | Compare Parameters | Operators overlay multiple parameters on traceability charts with auto-scaling secondary Y-axis |
| FR30 | Trigger Root Cause Analysis | System sends out-of-spec parameter data to Mistral AI for analysis |
| FR31 | Display Mistral Insights | System presents AI-generated root cause analysis with corrective actions |
| FR32 | Auto-Refresh Monitoring | System refreshes parameter values every 1 second via Streamlit fragments |
| FR33 | Approve Operators | Analysts view pending operator registration requests and approve or decline them |
| FR34 | List All Users | Analysts view all registered users with their role, approval status, active flag, page permissions, creation date, and last login |
| FR35 | Manage Page Permissions | Analysts grant or revoke page-level access for each operator via checkboxes in the Admin Panel |
| FR36 | Grant Full Access | Analysts enable a "Grant Full Access" toggle to give an operator access to all available pages at once |
| FR37 | Select Individual Pages | Analysts individually check which restricted pages (Configuration, Analysis) each operator may access |
| FR38 | Restrict Page Access | Operators without explicit permission for a restricted page receive an access-denied message |
| FR39 | Role-Based Navigation | The navigation bar dynamically shows or hides links based on role and page permissions |
| FR40 | Default Page Access | All authenticated operators have default access to Home and Realtime Monitoring pages |
| FR41 | Delete User | Analysts permanently delete operator accounts from the Admin Panel |
| FR42 | Activate/Disable User | Analysts enable or disable operator accounts from the Admin Panel |

## 2.4 Non-Functional Requirements

The following Non-Functional Requirements (NFR) ensure system performance and usability:

| ID | Requirement | Description |
|----|------------|-------------|
| NFR1 | Performance | Real-time monitoring fragment refreshes within 1 second. Database queries complete within 10 seconds for typical workloads |
| NFR2 | Scalability | System handles monitoring of up to 50 parameters simultaneously across multiple machines. Database caching (TTL: 10–600 seconds) reduces query load |
| NFR3 | Availability | Core monitoring functionality remains operational even if Mistral AI API is unavailable. Graceful degradation with status-only display |
| NFR4 | Security | Passwords hashed with PBKDF2-HMAC-SHA256 (120,000 iterations). Session tokens use HMAC-signed payloads. LocalStorage-based session persistence with query-parameter fallback |
| NFR5 | Usability | Intuitive UI with clear navigation (Configuration → Realtime → Analysis). Machine status indicators (Working/Standby/Inactive) provide immediate operational awareness |
| NFR6 | Data Integrity | Analysis results stored with RunSequence tracking for auditability. Configuration changes logged with timestamps. Database transactions ensure consistency |
| NFR7 | Caching Strategy | Multi-tier caching: Streamlit @st.cache_data decorators with configurable TTLs (10s for real-time, 60s for sensor traces, 300s for configurations, 600s for analysis results) |
| NFR8 | Error Handling | Database connection testing with graceful failure. Clear user-facing error messages |

## 2.5 Use Case Diagrams

This section describes use case diagrams to model system interactions:

**General Use Case Diagram (Main System)**: Shows interactions of Operator and Analyst roles with use cases including authentication, machine configuration management, real-time monitoring, datasheet generation, and root cause analysis.

*Figure 2.1 – General Use Case Diagram*

The main system encompasses the following primary use cases:
- Authenticate (FR1–FR3): Login, register, and logout with session management
- Manage Configuration (FR6–FR12): Create, read, update, delete machine configurations
- Monitor Parameters (FR22–FR31): Real-time parameter monitoring with specification comparison
- Generate Datasheet (FR13–FR20): Production run analysis and reference datasheet generation
- Analyze Root Cause (FR30–FR31): AI-powered anomaly analysis via Mistral

**Operator Use Case Diagram**: Focuses on the Operator's limited but critical capabilities: selecting configurations, viewing real-time parameter values, detecting out-of-spec conditions, viewing traceability charts, and triggering root cause analysis.

*Figure 2.2 – Operator Use Case Diagram*

**Analyst Use Case Diagram**: In addition to all Operator use cases, Analysts have exclusive access to the Admin Panel for user management: reviewing pending operator registrations, approving or declining new accounts, listing all registered users, managing per-operator page-level permissions, activating/disabling users, and permanently deleting accounts.

*Figure 2.3 – Analyst Use Case Diagram*

## 2.6 Kanban Task Board

Tasks were organized using a Kanban board reflecting the iterative workflow updated through the project lifecycle (February — May 2025):

| Period | To Do | In Progress | Done |
|--------|-------|-------------|------|
| Feb W1–W2 | Project setup, repo initialization, Streamlit base | Requirements gathering | — |
| Feb W3–W4 | Authentication system, database schema | Machine configuration CRUD | Project scaffold |
| Mar W1–W2 | Real-time monitoring page, OPC UA data queries | Analysis page design | Auth system + config CRUD |
| Mar W3–W4 | Mistral AI integration, traceability charts | Full parameter monitoring | Real-time MVP |
| Apr W1–W2 | Admin panel, page permissions, approval workflow | Deployment pipeline | Analysis + Mistral RCA |
| Apr W3–W4 | Docker Compose, GitHub Actions CI/CD | Documentation | Admin panel |
| May W1–W2 | Testing, report writing | Final bug fixes | Docker + CI/CD complete |

Kanban board snapshots show task flow through To Do → In Progress → Done columns with bi-weekly updates, enabling continuous delivery and real-time priority adjustments.

## 2.7 Conclusion

This chapter defines Cable Manufacturing AI's requirements and task organization, ensuring alignment with user needs and system goals including AI-powered root cause analysis. The Kanban approach facilitated flexible development, while use case diagrams clarified interactions between Operators and Analysts. The next chapter details the system's design through UML diagrams.

---

# Chapter 3: Conception

## 3.1 Introduction

This chapter presents the design of Cable Manufacturing AI, focusing on UML diagrams to model the system's structure and behavior. The UML content guides development and ensures clarity across the Streamlit frontend, database layer, and Mistral AI integration.

## 3.2 UML Diagrams

Cable Manufacturing AI uses UML to ensure alignment across Streamlit pages, SQL Server database, and Mistral AI. The diagrams include use case, class, sequence, and activity diagrams, detailed below.

### 3.2.1 Use Case Diagrams

#### 3.2.1.1 Configuration Management — Use Case Diagram

*Figure 3.1 – Configuration Management Use Case Diagram*

**Table 3.1 – Use Case: Configure Machine**

| Element | Description |
|---------|-------------|
| Use Case Name | Configure Machine |
| Actor | Analyst |
| Description | Analyst creates or modifies a machine configuration by selecting monitoring parameters and designating recipe parameters |
| Precondition | Analyst is authenticated. Machine exists in MachineTagValue |
| Postcondition | Configuration is saved to model_schema.machine_configuration |
| Main Flow | 1. Analyst navigates to Configuration page. 2. System displays machine status table. 3. Analyst fills configuration form (name, machine, monitoring params, recipe params, description). 4. System validates inputs. 5. System saves configuration. 6. System confirms success |
| Alternative Flow | If configuration name already exists for the machine, system displays an error. If recipe parameters are not a subset of monitoring parameters, system displays a validation error |

#### 3.2.1.2 Real-Time Monitoring — Use Case Diagram

*Figure 3.2 – Real-Time Monitoring Use Case Diagram*

**Table 3.2 – Use Case: Monitor Parameters**

| Element | Description |
|---------|-------------|
| Use Case Name | Monitor Parameters |
| Actor | Operator (and Analyst) |
| Description | Operator views real-time parameter values compared against specification ranges |
| Precondition | Configuration has been analyzed. Reference datasheet exists. Machine is active |
| Postcondition | Operator sees live parameter values with status indicators |
| Main Flow | 1. Operator selects configuration from dropdown. 2. System loads reference datasheet from latest analysis. 3. System fetches live values from MachineTagValue. 4. System compares each value against Min/Max specs. 5. System displays parameter cards with color-coded status. 6. Cards auto-refresh every 1 second |
| Alternative Flow | If machine is in Standby (LineSpeed = 0), system displays Standby status. If parameters have no data, system shows "Waiting for value..." state. If parameters are out of range, system displays violation badges |

#### 3.2.1.3 Analysis Datasheet Generation — Use Case Diagram

*Figure 3.3 – Analysis Datasheet Generation Use Case Diagram*

**Table 3.3 – Use Case: Generate Datasheet**

| Element | Description |
|---------|-------------|
| Use Case Name | Generate Datasheet |
| Actor | Analyst |
| Description | Analyst selects a machine, picks an analysis configuration, chooses production runs, and generates a statistical reference datasheet |
| Precondition | Analyst is authenticated. Machine has production runs with data |
| Postcondition | Reference datasheet is saved to parameter_reference_datasheet table. Analysis history is tracked in datasheet_runs |
| Main Flow | 1. Analyst navigates to Analysis page. 2. System displays step-by-step workflow. 3. Analyst selects an analysis configuration. 4. System pre-fills machine and parameters. 5. Analyst selects analysis mode (Production Run or Time Window). 6. System loads production runs. 7. Analyst selects runs with IsOk = 1 for sample collection. 8. System collects up to 1,200 samples per parameter per run. 9. System computes statistics (Min, Max, Mean, StdDev). 10. System correlates with quality labels. 11. System saves datasheet |
| Alternative Flow | If ProductionRunQuality table has no matching records, samples are labeled IsOk = 0. If no OK runs exist, system prevents datasheet generation |

#### 3.2.1.4 Mistral AI Root Cause Analysis — Use Case Diagram

*Figure 3.4 – Mistral AI Root Cause Analysis Use Case Diagram*

**Table 3.4 – Use Case: Analyze Root Cause**

| Element | Description |
|---------|-------------|
| Use Case Name | Analyze Root Cause |
| Actor | Operator (triggered manually) |
| Description | System sends out-of-spec parameter data to Mistral AI and receives natural-language root cause analysis with corrective actions |
| Precondition | MISTRAL_API_KEY is configured. Parameter is out of specification range |
| Postcondition | Operator views AI-generated analysis with root cause, immediate actions, and preventive measures |
| Main Flow | 1. System detects parameter out of spec OR operator clicks "Mistral RCA" button. 2. System collects out-of-range parameter with value, min, max, and deviation info. 3. System constructs prompt with machine context. 4. System calls Mistral AI API. 5. System displays generated analysis with root cause, corrective actions, and preventive recommendations |
| Alternative Flow | If Mistral API is unavailable, system displays an error message. If no parameters are out of range, system notifies the operator |

### 3.2.2 Class Diagram

*Figure 3.5 – Class Diagram — System Entities*

The class diagram models the following system entities:

| Entity | Attributes | Relationships |
|--------|------------|---------------|
| User | UserId, PasswordHash, PasswordSalt, Role, ApprovalStatus, IsActive, PagePermissions, CreatedAt, LastLoginAt | 1 → * AnalysisRun, 1 → * Configuration |
| MachineConfiguration | ConfigurationId, ConfigurationName, MachineCode, MonitoringParameters (JSON), RecipeParameters (JSON), ConfigurationType, Description, IsActive, CreatedAt, UpdatedAt | * → 1 User |
| ParameterReferenceDatasheet | DatasheetId, RunId, MachineCode, ParameterName, MinValue, MaxValue, MeanValue, StdDev, SampleCount, QualityOkCount, QualityNotOkCount, RecipeIdentifier | * → 1 DatasheetRun |
| DatasheetRun | RunId, ConfigurationId, MachineCode, ExecutionTimestamp, TotalSamples, ParameterCount, AnalysisMode | 1 → * ParameterReferenceDatasheet |
| AnalysisResult | ResultId, RunId, MachineCode, ParameterName, CurrentValue, MinSpec, MaxSpec, Status, Timestamp, MistralAnalysis | * → 1 Configuration |
| ProductionRun | RunId, MachineCode, StartTime, EndTime | 1 → * ProductionRunQuality |
| ProductionRunQuality | QualityId, RunId, IsOk | * → 1 ProductionRun |
| MachineTagValue | TagId, OpcNodeId, MachineCode, Value, Timestamp | Independent time-series entity |

### 3.2.3 Sequence Diagrams

Sequence diagrams demonstrate chronological interactions between system components, precisely tracking how objects exchange messages during operations.

#### 3.2.3.1 Authentication — Sequence Diagram

*Figure 3.6 – Authentication Sequence Diagram*

**Table 3.5 – Authentication Flow**

| Step | Description |
|------|-------------|
| 1 | User enters User ID and password on Authentication page |
| 2 | Authentication page calls authenticate_user() from auth_helpers.py |
| 3 | auth_helpers.py queries model_schema.users table via SQLAlchemy |
| 4 | System verifies password using PBKDF2-HMAC-SHA256 with stored salt |
| 5 | On success, sign_in_user() creates HMAC-signed session token |
| 6 | Session token stored in st.session_state and synced to window.localStorage |
| 7 | User is redirected to the requested page (or home page) |

#### 3.2.3.2 Machine Configuration — Sequence Diagram

*Figure 3.7 – Machine Configuration Sequence Diagram*

**Table 3.6 – Machine Configuration Flow**

| Step | Description |
|------|-------------|
| 1 | Analyst selects machine from dropdown |
| 2 | Configuration page calls load_all_parameters_for_machine from db_helpers.py |
| 3 | db_helpers.py queries MachineTagValue for distinct OpcNodeIds |
| 4 | System displays available parameters |
| 5 | Analyst selects monitoring parameters and designates recipe parameters |
| 6 | Analyst clicks "Save Configuration" |
| 7 | System calls add_machine_configuration() with JSON-serialized parameter lists |
| 8 | System inserts into model_schema.machine_configuration |
| 9 | System clears cache and confirms success |

#### 3.2.3.3 Real-Time Monitoring — Sequence Diagram

*Figure 3.8 – Real-Time Monitoring Sequence Diagram*

**Table 3.7 – Real-Time Monitoring Flow**

| Step | Description |
|------|-------------|
| 1 | Operator selects a saved configuration |
| 2 | Model page loads config from machine_configuration table |
| 3 | System calls load_latest_analysis_results() to retrieve reference datasheet |
| 4 | System calls get_machine_status_by_linespeed() to check LineSpeed-based status |
| 5 | System starts 1-second auto-refresh |
| 6 | Each second: load_current_machine_values() fetches latest values from MachineTagValue |
| 7 | System compares each value against Min/Max from reference datasheet |
| 8 | System renders parameter cards with color-coded status indicators |
| 9 | Operator views real-time data with spec violation badges |

#### 3.2.3.4 Datasheet Analysis — Sequence Diagram

*Figure 3.9 – Datasheet Analysis Sequence Diagram*

**Table 3.8 – Recipe Datasheet Generation Flow**

| Step | Description |
|------|-------------|
| 1 | Analyst selects machine and analysis configuration |
| 2 | System pre-fills machine and parameters |
| 3 | Analyst selects analysis mode |
| 4 | System loads production runs from productionrun table |
| 5 | Analyst selects runs with IsOk = 1 for sample collection |
| 6 | Analyst clicks "Collect Samples & Generate Datasheet" |
| 7 | System calls get_labeled_samples_from_runs() — up to 1,200 samples per parameter per run |
| 8 | System labels samples using ProductionRunQuality.IsOk |
| 9 | System calls calculate_recipe_parameter_statistics_from_samples() |
| 10 | System saves results via save_recipe_datasheet() to parameter_reference_datasheet |
| 11 | System displays generated datasheet with sample counts and quality correlation |

#### 3.2.3.5 Root Cause Analysis — Sequence Diagram

*Figure 3.10 – Root Cause Analysis Sequence Diagram*

**Table 3.9 – AI-Based Root Cause Analysis Flow**

| Step | Description |
|------|-------------|
| 1 | System detects parameter out of spec OR Operator clicks "Mistral RCA" button |
| 2 | System collects out-of-range parameter with current values and specification ranges |
| 3 | System constructs a detailed prompt with machine context and parameter deviation data |
| 4 | System calls Mistral AI API (via requests REST API) |
| 5 | Mistral AI processes the prompt and returns natural-language analysis |
| 6 | System displays: (a) Most likely root cause, (b) Immediate corrective actions, (c) Preventive measures |
| 7 | Operator reviews the analysis and takes appropriate action |

### 3.2.4 Activity Diagrams

Activity diagrams model system workflows through actions, decisions, and parallel processes.

#### 3.2.4.1 User Login — Activity Diagram

*Figure 3.11 – User Login Activity Diagram*

**Table 3.10 – Authentication Session Flow**

| Step | Description |
|------|-------------|
| 1 | User navigates to Authentication page |
| 2 | System checks for existing session (query params, LocalStorage, session state) |
| 3 | [Session exists] → User is redirected to target page |
| 4 | [No session] → User sees Login form |
| 5 | User enters User ID and password |
| 6 | System validates credentials against database |
| 7 | [Valid] → System creates session token and redirects to home page |
| 8 | [Invalid] → System displays error message and user retries |

#### 3.2.4.2 User Registration — Activity Diagram

*Figure 3.12 – User Registration Activity Diagram*

**Table 3.11 – User Registration Flow**

| Step | Description |
|------|-------------|
| 1 | User navigates to Register tab |
| 2 | User enters User ID and password |
| 3 | System checks if User ID already exists |
| 4 | [Exists with approved status] → System displays "User ID already exists" error |
| 5 | [Exists with pending status] → System displays "pending registration" message |
| 6 | [Exists with declined status] → System updates record with new password and resets to pending |
| 7 | [New] → System generates random 16-byte salt |
| 8 | System hashes password with PBKDF2-HMAC-SHA256 (120,000 iterations) |
| 9 | System inserts new user record into model_schema.users with role='operator' and ApprovalStatus='pending' |
| 10 | User is informed that account is pending Analyst approval |

#### 3.2.4.3 Machine Configuration — Activity Diagram

*Figure 3.13 – Machine Configuration Activity Diagram*

**Table 3.12 – Configuration Creation Flow**

| Step | Description |
|------|-------------|
| 1 | Analyst navigates to Configuration page |
| 2 | System loads all machines and their LineSpeed-based status |
| 3 | Analyst selects a machine from the dropdown |
| 4 | System loads all available parameters for that machine |
| 5 | Analyst enters configuration name |
| 6 | Analyst selects config type (realtime or analysis) |
| 7 | Analyst selects monitoring parameters from the list |
| 8 | Analyst selects recipe parameters (subset of monitoring parameters) |
| 9 | System validates: recipe parameters subset of monitoring parameters |
| 10 | [Invalid] → System displays error and analyst corrects input |
| 11 | [Valid] → System saves configuration to database |
| 12 | System clears cache and confirms success |

#### 3.2.4.4 Real-Time Monitoring — Activity Diagram

*Figure 3.14 – Real-Time Monitoring Activity Diagram*

**Table 3.13 – Real-Time Monitoring Flow**

| Step | Description |
|------|-------------|
| 1 | Operator selects a configuration from dropdown |
| 2 | System loads reference datasheet from latest analysis results |
| 3 | System checks machine LineSpeed-based status |
| 4 | [Machine Standby] → Display standby message and keep checking status |
| 5 | [Machine Inactive] → Display inactive status |
| 6 | [Machine Active] → Start 1-second monitoring loop: fetch latest parameter values from MachineTagValue, compare against Min/Max specifications, render parameter cards with color-coded status, trigger violation badges and optional Mistral root cause analysis for out-of-spec parameters |
| 7 | Wait 1 second and repeat monitoring loop |

## 3.3 Conclusion

The UML diagrams provide a comprehensive design for Cable Manufacturing AI, clarifying interactions and structure with focus on real-time monitoring and AI integration. These models guide the implementation phase, detailed in the next chapter.

---

# Chapter 4: Realization

## 4.1 Introduction

This chapter details the implementation of Cable Manufacturing AI, including code realization, UI design, and the integration with Mistral AI for root cause analysis.

## 4.2 Implementation

The project implements Cable Manufacturing AI using Streamlit for the multi-page frontend, SQL Server for the database, and Python for the backend logic. Key implementation details follow:

| Component | Technology | Details |
|-----------|-----------|---------|
| Frontend | Streamlit 1.x | Multi-page app with custom CSS theming and hidden sidebar |
| Backend | Python 3.11 | Modular package structure with auth_helpers.py and db_helpers.py |
| Database | SQL Server | dbo schema + model_schema for application tables |
| ORM | SQLAlchemy | Database connectivity with connection pooling and parameterized queries |
| AI | Mistral AI API | Root cause analysis via mistral-small-latest model |
| Automation | Papermill | Optional Jupyter notebook execution for analysis |
| Charts | Plotly | Interactive time-series visualizations with spec range overlays |
| Auth | PBKDF2-HMAC-SHA256 | Password hashing with 120,000 iterations and HMAC-signed session tokens |
| Caching | Streamlit @st.cache_data | Multi-tier TTL-based caching (10s–600s) |
| Containerization | Docker | Deployment via docker-compose with Microsoft ODBC Driver 18 |
| CI/CD | GitHub Actions | Automated build and push to GHCR |

## 4.3 Database Tables

The following database tables support the application:

| Table | Schema | Purpose |
|-------|--------|---------|
| `MachineTagValue` | `dbo` | Time-series sensor events (core data source — OPC UA tags) |
| `productionrun` | `dbo` | Production run metadata with time ranges |
| `ProductionRunQuality` | `dbo` | Quality labels (IsOk = 1 or 0) per production run |
| `tags_mapping` | `dbo` | Machine-to-parameter mappings |
| `machine_configuration` | `model_schema` | User-saved configurations with JSON parameter lists |
| `parameter_reference_datasheet` | `model_schema` | Statistical reference ranges with recipe context |
| `analysis_results_[MACHINE]` | `model_schema` | Per-machine parameter-level analysis history with RunSequence |
| `datasheet_runs` | `model_schema` | Analysis run metadata tracking |
| `users` | `model_schema` | Authentication data with page permissions |
| `analysis_results` | `model_schema` | Notebook analysis output storage (JSON + optional BLOB) |
| `parameter_optimal_windows` | `model_schema` | Learned stable window parameters per sensor |

## 4.4 Key Implementation Components

### 4.4.1 Authentication System (auth_helpers.py — 970 lines)

The authentication system (`cable_maintenance_ai/app/auth_helpers.py`) implements a secure, stateless session management approach:

- **Password Hashing**: PBKDF2-HMAC-SHA256 with 120,000 iterations and random 16-byte salt
- **Session Tokens**: HMAC-SHA256 signed JSON payloads with expiration (7-day TTL) and nonce
- **Session Persistence**: Three-layer recovery — `st.session_state` → URL query parameters → `window.localStorage`
- **Automatic Login Flow**: `bootstrap_auth_page()` automatically redirects authenticated users
- **Logout**: Clears all session state, query params, and localStorage
- New operator registrations require Analyst approval (`ApprovalStatus = 'pending'`)
- Default analyst account (`admin` / `Coficab2025!`) seeded on first run via `initialize_users_table()`

**Database Schema — model_schema.users:**

```sql
CREATE TABLE [model_schema].[users] (
    [UserId] NVARCHAR(100) NOT NULL PRIMARY KEY,
    [PasswordHash] NVARCHAR(255) NOT NULL,
    [PasswordSalt] NVARCHAR(255) NOT NULL,
    [Role] NVARCHAR(20) NOT NULL DEFAULT 'operator',
    [ApprovalStatus] NVARCHAR(20) NOT NULL DEFAULT 'approved',
    [CreatedAt] DATETIME NOT NULL DEFAULT GETDATE(),
    [LastLoginAt] DATETIME NULL,
    [IsActive] BIT NOT NULL DEFAULT 1,
    [PagePermissions] NVARCHAR(MAX) NULL
);
```

**User Roles:**

| Role | Default Access | Granting |
|------|---------------|----------|
| **Operator** | Home + Realtime only; Configuration & Analysis require explicit permission | Registered and approved by Analyst |
| **Analyst** | All pages | Pre-seeded during `initialize_users_table()` — default account `admin` / `Coficab2025!` |
| **Pending** | Cannot log in | Newly registered operators awaiting Analyst approval |

**Session Token Flow:**

1. User submits credentials → `authenticate_user()` validates
2. `sign_in_user()` → `_build_session_token()` creates payload: `{ user_id, role, expires_at, nonce }`
3. Payload is JSON-serialized, base64url-encoded, signed with HMAC-SHA256
4. Token stored in `st.session_state`, query params, and browser `localStorage`
5. Each page load → `ensure_page_authentication()` → `_is_authenticated()` verifies token
6. On logout → `sign_out_user()` clears all storage

**Page Access Management System:**

The authentication module implements page-level access control:
- **Page Registry (`PAGE_REGISTRY`)**: A dictionary mapping internal page identifiers to human-readable labels. Tracks `configuration_page` (Configuration) and `analysis_page` (Analysis) as restrictable pages. Pages not in this registry (`app.py` Home, `model_page` Realtime) are default-accessible to all authenticated operators.
- `get_user_page_permissions(user_id)`: Retrieves an operator's explicitly granted pages from the `PagePermissions` column. Returns `None` if no explicit permissions exist (default access only), or a list of allowed page identifiers.
- `set_user_page_permissions(user_id, permissions)`: Persists page permissions. Setting permissions to `None` grants only default pages; setting a list of page identifiers grants explicit access. Returns success status and a descriptive message.
- `check_page_access(page_id)`: Enforces page-level authorization. Rules: (1) Analysts always have access; (2) Default pages (`app.py`, `model_page`) are always accessible; (3) Restricted pages require explicit permission; (4) NULL `PagePermissions` means only default pages are accessible.
- `ensure_page_authentication(current_page_path)`: Extended to perform page-level access checks after authentication using `_PAGE_PATH_MAP` to resolve page paths to identifiers. Blocked users see an access denied message.
- `render_nav_bar()`: Dynamically filters navigation links based on page permissions.

### 4.4.2 Database Helpers (db_helpers.py — ~2,700 lines)

The database layer (`cable_maintenance_ai/app/db_helpers.py`) provides comprehensive data access with caching:

- **Caching Strategy**: `@st.cache_data` decorators with configurable TTLs (10s for real-time, 60s for sensor traces, 300s for configurations, 600s for analysis)
- **Machine Configuration CRUD**: Full create, read, update, delete operations with JSON-serialized parameter lists
- **Analysis Results Storage**: Per-machine tables (`analysis_results_[MACHINE]`) with RunSequence tracking for versioned analysis history
- **Production Run Queries**: Time-window based parameter discovery, sample collection (up to 1,200 per run), quality-labeled sample extraction
- **Mistral AI Integration**: `call_mistral_ai()` and `analyze_parameter_anomaly()` functions for AI-powered root cause analysis
- **Machine Status**: Dual-mode status detection — LineSpeed-based Working/Standby/Inactive with 3-second freshness window
- **Sliding Window Sensor Traces**: `rebuild_step_signal()` and `detect_stable_points()` for event-based to continuous signal conversion
- **Robust Path Detection**: `get_project_root()` works both locally and in Docker

**Database Connection Layer (`db_connection.py`):**

Singleton engine factory with connection pooling:
- Engine created via SQLAlchemy with `mssql+pyodbc` dialect
- Connection URL format: `mssql+pyodbc://user:password@host,port/dbname?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes`
- Pool settings: `pool_pre_ping=True`, `pool_recycle=3600`, `pool_size=5`, `max_overflow=10`
- Startup verification with `SELECT 1` query
- The `get_engine()` function is cached with `@st.cache_resource` and provides the SQLAlchemy engine to all pages

### 4.4.3 Machine Configuration Page (configuration_page.py — 720 lines)

The configuration page (`cable_maintenance_ai/app/pages/configuration_page.py`) provides a complete CRUD interface:

- **Machine Status Display**: Real-time LineSpeed-based Working/Standby/Inactive indicators derived from data freshness:
  - 🟢 **Working**: linespeed > 0 and timestamp within 3-second window
  - 🟡 **Standby**: linespeed = 0 and timestamp within 3-second window
  - 🔴 **Inactive**: no data or stale (>3 seconds)
  - Manual refresh button; status cached in session state to prevent reactivity issues
- **Add Configuration**: Step-by-step form with machine selection (status icons), parameter browsing, monitoring/recipe designation, config type selection (realtime/analysis), and description
- **View & Edit**: Searchable configuration list with expandable details, in-place editing with parameter validation
- **Delete**: Confirmation workflow with visual safety check (checkbox required)
- **Validation**: Recipe parameters must be a subset of monitoring parameters; configuration names must be unique per machine
- **Summary metrics**: Total/Active configurations, unique machines, realtime/analysis breakdown at page bottom

**Database table:** `model_schema.machine_configuration` with columns for `ConfigurationName`, `MachineCode`, `MonitoringParameters` (JSON), `RecipeParameters` (JSON), `ConfigurationType`, `Description`, `IsActive`, timestamps. Has unique constraint on `(ConfigurationName, MachineCode)`.

### 4.4.4 Real-Time Monitoring Page (model_page.py — ~2,000 lines)

The most complex page (`cable_maintenance_ai/app/pages/model_page.py`) handles real-time monitoring with Mistral AI root cause analysis:

- **Configuration Selector**: Dropdown with machine status and configuration metadata
- **Reference Datasheet Display**: Analyzed configuration statistics with Min/Max/Mean per parameter from the latest analysis results
- **Machine Status Card**: Live status indicator with elapsed time counter (auto-updating)
- **Real-Time Fragments**: Streamlit fragments with `run_every=1` for monitoring data refresh
- **Parameter Cards**: Color-coded containers showing current value, specification range, status badge, and last update time
- **Spec Violation Badges**: Out-of-range parameters display a colored pill showing the gap distance and percentage of spec span
- **3-Second Sliding Window Trace**: Ultra-fast real-time charts using cached sliding-window approach (drop oldest second, add newest on each refresh)
  - Plotly chart with spec range background (green for normal, red for out-of-spec)
  - Target mean line, overlay comparison with another parameter (auto-detects scale mismatch and uses secondary Y-axis)
  - Metrics row: readings count, min, mean, max for the window
  - Out-of-spec percentage warning
- **Full Timeline Trace**: Complete historical view with snapshot capability
  - Loads all historical data on first access (cached in session state)
  - Static snapshot frozen at button-click moment while 3-second window updates live
  - "Take Snapshot" button captures current state for comparison
  - Long-term metrics (total readings, min, max, mean, % in spec)
- **Parameter Overlay**: Compare two parameters on the same chart with auto-scaling secondary Y-axis
- **Root Cause Analysis**: Triggered manually via "Mistral RCA" button for out-of-spec parameters. Sends structured prompt to Mistral AI and displays root cause, immediate actions, and preventive recommendations
- Parameters within range show "✅ Parameter within acceptable range"

**Data flow:**
- `load_current_machine_values()` → queries `MachineTagValue` for latest readings (TTL=0 for real-time)
- `load_parameter_reference_datasheet()` → loads Min/Max/Mean specs from stored datasheet
- `analyze_parameter_anomaly()` → calls Mistral AI API when value is out of spec
- `_get_cached_3second_data()` → sliding window cache for live trace chart

### 4.4.5 Analysis Datasheet Page (analysis_page.py — 827 lines)

The analysis page (`cable_maintenance_ai/app/pages/analysis_page.py`) implements a recipe-aware datasheet generation workflow:

- **5-Step Workflow**: Select analysis configuration → Choose analysis mode → Load production runs → Select runs for sample collection (IsOk = 1 only) → Generate datasheet
- **Two Analysis Modes**:
  - **Production Run-based**: Loads runs from `productionrun` table joined with `ProductionRunQuality` for quality labels
  - **Time Window-based**: User defines custom time range, production runs within that window are loaded
- **Quality Filtering**: Only runs with `IsOk = 1` are available for sample collection
- **Statistical Computation**: Per-parameter Min, Max, Mean, StdDev, SampleCount, with QualityOkCount and QualityNotOkCount
- **Recipe Parameter Exclusion**: Recipe parameters are automatically excluded from the datasheet
- **Analysis History**: Previous datasheet runs browsable with detailed preview showing metrics (total samples, OK %, parameter count)
- **Sample Collection**: Up to 1,200 samples per parameter per run from MachineTagValue with 12-hour buffer around run time range. Limited to 150 parameters max

**Key database tables:**
- `model_schema.parameter_reference_datasheet` — stores per-parameter statistics with `RecipeIdentifier`, `QualityOkCount`, `QualityNotOkCount`
- `model_schema.datasheet_runs` — tracks analysis run metadata (execution timestamp, sample counts, parameter counts)
- `productionrun` and `ProductionRunQuality` — source of production run data and quality labels
- `MachineTagValue` — source of sensor parameter time-series data

### 4.4.6 Admin Panel (admin_page.py — 354 lines)

The Admin Panel (`cable_maintenance_ai/app/pages/admin_page.py`) provides Analysts with user management and page-level permission control:

- **Pending Approvals Section**: Lists all operator registrations with `ApprovalStatus = 'pending'`. Each entry shows User ID, registration timestamp, and Approve/Decline buttons. Approved operators gain login ability; declined operators are automatically deactivated.
- **All Users Table**: Displays a dataframe of all registered users with columns: User ID, Role, Approval Status, Active flag, Page Access summary, Created date, and Last Login date. The Page Access column shows a human-readable summary (e.g., "All pages (analyst)", "Default (Realtime only)", or "Configuration, Analysis").
- **Manage Page Access Section**: For each operator, an expandable section provides:
  - A "Grant Full Access" checkbox — when checked, operator can access all restricted pages
  - Individual checkboxes for each restricted page from `PAGE_REGISTRY` (`configuration_page` and `analysis_page`)
  - Checkboxes automatically disabled when "Grant Full Access" is enabled
  - A "Save Permissions" button that persists changes via `set_user_page_permissions()`
  - Activate/Disable and Delete buttons for user lifecycle management
- **Access Control**: Page calls `ensure_page_authentication()` and `is_current_user_analyst()` — non-Analyst users see "Access denied" error and execution is stopped.

### 4.4.7 Entry Point (app.py)

The main entry point (`cable_maintenance_ai/app/app.py`) configures the Python path for both local and Docker environments, initializes the database schema on startup (`users` table + `machine_configuration` table), enforces authentication, and renders the home page.

**Home page features:**
- Animated gradient background with floating Coficab logo watermark
- Hero section displaying the user's role and current month/year
- Interactive "How it works" workflow section with three expandable steps:
  1. **Configure** — Define machines, OPC parameters, and recipe subsets
  2. **Analyze** — Generate datasheets from production run samples with quality filtering
  3. **Monitor** — Track live values against reference specs with Mistral AI root cause analysis
- Footer with technology credits (Streamlit + Mistral AI)
- A shared custom navigation bar (`render_nav_bar`) renders links to Configuration, Realtime, Analysis, and Admin (Analyst-only) pages. The sidebar is hidden entirely via CSS + MutationObserver JS injection.

## 4.5 User Interface

The UI is designed with an intuitive workflow — Configure → Analyze → Monitor — with a learning curve of less than 10 minutes.

### 4.5.1 Home Page Interface

The home page displays a dashboard with:
- Animated gradient background with floating Coficab logo watermark
- Hero section with "Cable Manufacturing AI" title and role badge
- Interactive three-step workflow (Configure → Analyze → Monitor) with expandable details
- Technology credits in footer

*Figure 4.2 – Home Page Interface Screenshot*

### 4.5.2 Authentication Page Interface

The authentication page features:
- Secure login and registration tabs
- PBKDF2-based password hashing
- Automatic session recovery from browser LocalStorage
- COFICAB-themed design with company logo
- User registration with pending-approval workflow

*Figure 4.3 – Authentication Page Interface Screenshot*

### 4.5.3 Configuration Page Interface

The configuration page provides:
- Machine status table with LineSpeed-based Working/Standby/Inactive indicators
- Three-tab interface: Add Configuration, View & Edit, Delete
- Machine selection with status icons (green = Working, yellow = Standby, red = Inactive)
- Parameter multi-select with full OPC NodeId display
- Recipe parameter designation (subset of monitoring parameters)
- Config type selection (realtime vs analysis)
- In-line editing with validation
- Summary metrics at page bottom

*Figure 4.4 – Configuration Page Interface Screenshot*

### 4.5.4 Real-Time Monitoring Interface

The real-time monitoring page features:
- Configuration selector with metadata display
- Machine status card with elapsed time counter
- Reference datasheet with specification ranges
- Monitoring parameter cards with color-coded status (value, range, last update)
- Spec violation badges for out-of-range parameters
- 3-second sliding window traceability chart (real-time)
- Full timeline traceability chart (historical snapshot)
- Parameter overlay comparison with secondary Y-axis
- Mistral RCA button and analysis dialog

*Figure 4.5 – Real-Time Monitoring Interface Screenshot*

### 4.5.5 Analysis Datasheet Interface

The analysis page provides:
- Step-by-step guided workflow with session state persistence
- Configuration pre-selection with machine and parameter summary
- Production run browser with quality filtering (IsOk = 1 only)
- Time window analysis mode with date range picker
- Sample run multi-select with "Select All" option
- Generated datasheet with statistical summaries and quality counts
- Previous analysis history browser with run metrics

*Figure 4.6 – Analysis Datasheet Interface Screenshot*

### 4.5.6 Traceability Chart Interface

Traceability charts feature:
- Real-time 3-second sliding window (auto-refreshing)
- Full historical timeline (static snapshot with snapshot button)
- Specification range visualization (green zone = normal, red zones = out of spec)
- Target/mean line overlay
- Parameter comparison overlay with secondary Y-axis for different scales
- Summary metrics (readings, min, mean, max, in-spec percentage)

*Figure 4.7 – Traceability Chart Interface Screenshot*

### 4.5.7 Mistral AI Root Cause Analysis Interface

The Mistral AI integration provides:
- Manual trigger via "Mistral RCA" button when parameter is out of spec
- Parameters within range show "✅ Parameter within acceptable range"
- Structured output: (1) Most likely root cause, (2) Immediate corrective actions, (3) Preventive measures
- Context-aware prompting with machine code, parameter details, and deviation metrics

*Figure 4.8 – Mistral AI Root Cause Analysis Screenshot*

### 4.5.8 Admin Panel Interface

The Admin Panel interface features:
- Navy gradient hero section with "ADMIN PANEL" eyebrow label and "User Management" title
- Pending Approvals Section: Lists operator registrations awaiting approval with User ID, registration timestamp, and Approve/Decline action buttons
- All Users Table: Full-width dataframe displaying all registered users with columns for User ID, Role, Approval Status, Active flag, Page Access summary, Creation date, and Last Login
- Manage Page Access Section: Expandable panels for each operator containing:
  - User metadata (User ID, Status, Active flag)
  - "Grant Full Access" checkbox — enables all pages
  - Individual page checkboxes for Configuration and Analysis pages (disabled when full access granted)
  - "Save Permissions" button with success/error feedback
  - Activate/Disable and Delete buttons per user
- Navigation: Top navigation bar dynamically shows "Admin" link only for Analyst users

*Figure 4.9 – Admin Panel Interface Screenshot*

## 4.6 Deployment and Monitoring

### 4.6.1 Introduction

Cable Manufacturing AI is deployed using Docker containerization with automated CI/CD pipeline via GitHub Actions to GitHub Container Registry (GHCR).

### 4.6.2 Docker Containerization

**Dockerfile (`cable_maintenance_ai/Dockerfile`):**
- Base image: `python:3.11-slim`
- System dependencies: `unixodbc`, `unixodbc-dev`, `curl`, `gnupg`
- Microsoft ODBC Driver 18 for SQL Server installed from Microsoft's Debian 12 repository
- Python dependencies installed from `requirements.txt`
- Application code copied at `/app`
- Healthcheck: `python -c "import sqlalchemy; print('OK')"` every 30 seconds
- Port 8501 exposed with Streamlit binding to `0.0.0.0`

**Docker Compose (`docker-compose.yml`):**
- Single service `cable-ai` with build context `./cable_maintenance_ai`
- `.env` file for database credentials and Mistral API key
- Streamlit server configuration: headless, no sidebar, CORS disabled, XSRF enabled
- Volume mount: `./cable_maintenance_ai:/app` (development hot-reload)
- Resource limits: 2 CPU cores, 2GB memory (reserve: 1 CPU, 1GB)
- Healthcheck: 30s interval, 10s timeout, 3 retries, 40s start period
- Custom bridge network `cable-ai-network`
- Restart policy: `unless-stopped`

### 4.6.3 CI/CD Pipeline

**File:** `.github/workflows/docker-build-push.yml`

**Trigger conditions:**
- Push to `main` branch (when `cable_maintenance_ai/**`, workflow file, `requirements.txt`, or `Dockerfile` change)
- Pull request to `main`
- Manual `workflow_dispatch`

**Build Job** (runs on `ubuntu-latest`):
1. Checkout code (`actions/checkout@v4`)
2. Set up Docker Buildx (`docker/setup-buildx-action@v4`)
3. Login to GHCR (`docker/login-action@v4`) — push events only
4. Extract Docker metadata (`docker/metadata-action@v6`): tags `latest`, SHA-based, and branch-based
5. Build and push to `ghcr.io/abdelazizmosbahi/cable-maintenance-ai` with GitHub Actions cache
6. Publish build summary to workflow run page

**Test Job** (conditional — runs only on non-main-push events):
1. Build test image (load into Docker, not pushed)
2. Run Python import verification for all critical dependencies (streamlit, pandas, numpy, sqlalchemy, pyodbc, plotly, requests, papermill, nbformat, mistralai)

**Image Registry:**
- **Registry:** `ghcr.io` (GitHub Container Registry)
- **Image:** `ghcr.io/abdelazizmosbahi/cable-maintenance-ai`
- **Tags:** `latest` (default branch), `{branch}-{sha}` (SHA-based), `{branch}` (branch-based)

### 4.6.4 Configuration

The system uses environment variables for configuration:

**Table 4.1 – Environment Variables**

| Variable | Description |
|----------|-------------|
| `DB_HOST` | SQL Server hostname |
| `DB_PORT` | SQL Server port (default: 1433) |
| `DB_USER` | Database username |
| `DB_PASSWORD` | Database password |
| `DB_NAME` | Database name |
| `MISTRAL_API_KEY` | Mistral AI API key |
| `MISTRAL_MODEL` | Mistral model name (default: mistral-small-latest) |
| `AUTH_SESSION_SECRET` | HMAC signing secret for session tokens |
| `AUTH_SESSION_TTL_SECONDS` | Session TTL (default: 604800 = 7 days) |

### 4.6.5 Monitoring

The application includes built-in monitoring capabilities:
- **Streamlit Caching**: Multi-tier cache with configurable TTLs (10s–600s)
- **Database Diagnostics**: Connection testing and error reporting with graceful degradation
- **Print Logging**: Server-side logging for troubleshooting data loading issues
- **Healthcheck**: Docker-level health monitoring every 30 seconds with 3 retries
- **Machine Status**: Built-in LineSpeed-based status monitoring with 3-second freshness window

### 4.6.6 Conclusion

The realization phase delivers a fully integrated Cable Manufacturing AI platform, with Streamlit providing a responsive multi-page interface, SQL Server ensuring reliable data persistence, and Mistral AI adding intelligent root cause analysis capabilities. The modular architecture — comprising configuration management, real-time monitoring, and analysis/datasheet generation — provides COFICAB with a powerful tool for data-driven quality management in cable manufacturing.

---

## General Conclusion and Future Perspectives

To recapitulate the development of Cable Manufacturing AI, a platform designed to unify machine configuration management, real-time parameter monitoring, and recipe-aware datasheet analysis within a single Streamlit application. The project addresses the fragmentation of cable manufacturing quality monitoring by integrating live OPC UA sensor data with natural-language root cause analysis through Mistral AI.

Our development approach followed a Kanban methodology, enabling iterative task management and flexibility, with major milestones tracked between January and May 2025.

- **Chapter I** introduced the project, analyzed the operational challenges at COFICAB, outlined the proposed solution, presented the host company (COFICAB / ELLOUMI Group), and detailed the technology stack and system architecture.
- **Chapter II** specified functional and non-functional requirements, defined two user profiles (Operator and Analyst), modeled system interactions through use case diagrams, and presented the Kanban task board with bi-weekly snapshots throughout the project lifecycle.
- **Chapter III** focused on system design through UML diagrams — use case diagrams with detailed textual descriptions, class diagrams covering system entities, sequence diagrams for key workflows (authentication, configuration, monitoring, analysis, root cause analysis), and activity diagrams for critical processes.
- **Chapter IV** covered implementation, UI design, and deployment of the platform. The implementation includes five Streamlit pages (Authentication, Home, Configuration, Real-Time Monitoring, Analysis, and Admin Panel), ~2,700 lines of database helper code, a 970-line authentication and authorization module with role-based page-level access control, Docker containerization with GitHub Actions CI/CD, and Mistral AI integration for intelligent root cause analysis.

**Results** demonstrate a robust, scalable platform capable of:
- Monitoring multiple cable production machines simultaneously in real time with 1-second refresh
- Detecting out-of-spec parameter behavior with immediate visual violation badges
- Generating comprehensive reference datasheets from historical production runs with quality correlation
- Providing AI-powered root cause analysis with actionable corrective recommendations
- Maintaining full audit trails via run-level tracking and analysis versioning
- Enforcing role-based page-level access control with default and restricted pages
- Managing operator registrations through an approval workflow
- Configuring per-operator page permissions via a checkbox-based Admin Panel interface
- Deploying via Docker with automated CI/CD to GitHub Container Registry

**Challenges** encountered during development included:
- Real-time chart performance optimization (resolved with sliding-window caching approach)
- Mistral AI API integration and prompt engineering for manufacturing-specific context
- Streamlit fragment auto-refresh coordination between monitoring data and card rendering
- Cross-page session persistence across Streamlit's single-page navigation model
- Robust path detection working both locally and in Docker

**Future perspectives** involve:
- Expanding the system with ML models for time-series prediction and predictive maintenance
- Implementing automated retraining pipelines based on new production data
- Adding multi-language support for international deployment
- Integrating real-time alerting (email, SMS, dashboard notifications)
- Extending Mistral AI integration for predictive maintenance recommendations
- Migrating to Kubernetes for improved scalability
- Extending the permission system with granular feature-level (rather than page-level) access control
- Implementing role-based audit logging for all admin actions
- Adding self-service password reset and account recovery workflows

We believe that Cable Manufacturing AI provides a strong foundation for data-driven quality management in cable production and offers considerable potential for future enhancements. The platform successfully transforms raw OPC UA sensor data into actionable quality insights, directly addressing COFICAB's need for proactive, AI-enhanced manufacturing quality monitoring.

---

*Report generated from source code audit on 2026-06-03.*
