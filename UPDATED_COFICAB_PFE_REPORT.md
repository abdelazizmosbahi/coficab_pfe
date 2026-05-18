# Cable Manufacturing AI: Real-Time Quality Monitoring & Predictive Analytics Platform

---

## Acknowledgments

I would like to express my sincere gratitude to the team at COFICAB for providing me with the opportunity to undertake this internship and for their unwavering support throughout the process. Their collaborative environment and resources were instrumental in the successful development of this project. Special thanks go to my supervisors, Mr. Malek Boudhief and Ms. Mouna Bouzazi, for their invaluable assistance, expert guidance, and encouragement during the internship. Their insights and feedback were pivotal in shaping the project's direction and ensuring its alignment with professional standards. Without their contributions, this work would not have been possible.

I would also like to thank the ELLOUMI Group for fostering a culture of innovation and excellence that made this project a reality.

---

## Table of Contents

| Section | Page |
|---------|------|
| List of Figures | ii |
| List of Tables | iii |
| Introduction Générale | 1 |
| Chapter 1: Preliminary Study | 2 |
| 1.1 Project Presentation | 3 |
| 1.1.1 Introduction | 3 |
| 1.1.2 Problem Statement | 3 |
| 1.1.3 Proposed Solution | 3 |
| 1.2 Software Development Methodology | 4 |
| 1.2.1 Justification of Kanban | 4 |
| 1.3 Presentation of the Host Company | 5 |
| 1.3.1 History and Membership in the ELLOUMI Group | 5 |
| 1.3.2 Key Figures (2024) | 5 |
| 1.3.3 Vision | 6 |
| 1.4 Technologies and Tools | 7 |
| 1.5 Architecture | 7 |
| 1.5.1 Application Architecture | 7 |
| 1.5.2 Database | 8 |
| 1.6 Conclusion | 8 |
| Chapter 2: Requirements Analysis and Specification | 9 |
| 2.1 Introduction | 10 |
| 2.2 User Profiles | 10 |
| 2.3 Functional Requirements | 10 |
| 2.4 Non-Functional Requirements | 12 |
| 2.5 Use Case Diagrams | 13 |
| 2.6 Kanban Task Board | 15 |
| 2.7 Conclusion | 19 |
| Chapter 3: Conception | 20 |
| 3.1 Introduction | 21 |
| 3.2 UML Diagrams | 21 |
| 3.2.1 Use Case Diagrams | 21 |
| 3.2.2 Class Diagram | 27 |
| 3.2.3 Sequence Diagrams | 29 |
| 3.2.4 Activity Diagrams | 33 |
| 3.3 Conclusion | 37 |
| Chapter 4: Realization | 38 |
| 4.1 Introduction | 39 |
| 4.2 Implementation | 39 |
| 4.3 User Interface | 41 |
| 4.4 Deployment and Monitoring | 44 |
| 4.5 Conclusion | 46 |
| Conclusion Générale | 47 |

---

## List of Figures

| Figure | Description | Page |
|--------|-------------|------|
| 1.1 | COFICAB Key Figures 2024 Infographic | 6 |
| 1.2 | System Architecture Diagram | 7 |
| 2.1 | General Use Case Diagram | 13 |
| 2.2 | Operator Use Case Diagram | 14 |
| 2.3 | Analyst Use Case Diagram | 14 |
| 2.4 | Kanban Board — Initial Backlog | 15 |
| 2.5 | Kanban Board — Week 3 | 15 |
| 2.6 | Kanban Board — Week 5 | 16 |
| 2.7 | Kanban Board — Week 7 | 16 |
| 2.8 | Kanban Board — Week 9 | 17 |
| 2.9 | Kanban Board — Week 11 | 17 |
| 2.10 | Kanban Board — Week 13 | 18 |
| 2.11 | Kanban Board — Week 15 | 18 |
| 2.12 | Kanban Board — Week 17 | 19 |
| 3.1 | System Use Case Diagram (Main) | 22 |
| 3.2 | Configuration Management Use Case Diagram | 23 |
| 3.3 | Real-Time Monitoring Use Case Diagram | 24 |
| 3.4 | Analysis & Datasheet Generation Use Case Diagram | 25 |
| 3.5 | Mistral AI Integration Use Case Diagram | 26 |
| 3.6 | Class Diagram — System Entities | 27 |
| 3.7 | Class Diagram — With ML Backend | 28 |
| 3.8 | Authentication Sequence Diagram | 29 |
| 3.9 | Machine Configuration Sequence Diagram | 30 |
| 3.10 | Real-Time Monitoring Sequence Diagram | 31 |
| 3.11 | Datasheet Analysis Sequence Diagram | 31 |
| 3.12 | Root Cause Analysis Sequence Diagram | 32 |
| 3.13 | User Login Activity Diagram | 33 |
| 3.14 | User Registration Activity Diagram | 34 |
| 3.15 | Machine Configuration Activity Diagram | 35 |
| 3.16 | Real-Time Monitoring Activity Diagram | 36 |
| 4.1 | Home Page Interface Screenshot | 41 |
| 4.2 | Authentication Page Interface Screenshot | 41 |
| 4.3 | Configuration Page Interface Screenshot | 42 |
| 4.4 | Real-Time Monitoring Interface Screenshot | 42 |
| 4.5 | Analysis & Datasheet Interface Screenshot | 43 |
| 4.6 | Traceability Chart Interface Screenshot | 43 |
| 4.7 | Mistral AI Root Cause Analysis Screenshot | 44 |

---

## List of Tables

| Table | Description | Page |
|-------|-------------|------|
| 2.1 | Functional Requirements (FR1–FR15) | 10 |
| 2.2 | Functional Requirements (FR16–FR30) | 11 |
| 2.3 | Non-Functional Requirements (NFR1–NFR8) | 12 |
| 3.1 | Configure Machine — Use Case Textual Description | 23 |
| 3.2 | Monitor Parameters — Use Case Textual Description | 24 |
| 3.3 | Generate Datasheet — Use Case Textual Description | 25 |
| 3.4 | Root Cause Analysis — Use Case Textual Description | 26 |
| 4.1 | Technology Stack Summary | 39 |
| 4.2 | Database Tables Summary | 40 |

---

## Introduction Générale

This internship report presents **Cable Manufacturing AI**, a Streamlit-based monitoring and prediction system for cable production that unifies SQL Server-backed recipe and trace data with optional OPC UA live or replay connectivity and trained machine-learning artifacts to deliver real-time quality assessment and operator decision support. The project centers on three operational pillars — **machine configuration management**, **real-time parameter monitoring**, and **AI-driven quality prediction** — so operators can compare current values against expected ranges, track deviations across production runs, and generate predictions from engineered features.

The core problem addressed is the gap between high-frequency sensor signals and actionable quality insight on the shop floor, where raw data alone makes it difficult to detect out-of-spec behavior early or explain quality outcomes after the fact. Cable Manufacturing AI solves this by transforming event-based machine tags into structured features, applying trained models for OK/NOT OK classification, and presenting interpretable dashboards that highlight out-of-range parameters while providing traceable context for root-cause analysis via Mistral AI.

The result is a scalable, data-driven workflow that supports both live monitoring and historical investigations within a single, consistent Streamlit application. This report details the development of Cable Manufacturing AI, organized into four chapters:

- **Chapter I** provides a preliminary study, presenting the project and outlining the methodology, tools, and architecture.
- **Chapter II** specifies requirements, including user profiles, functional and non-functional requirements, and the Kanban task board.
- **Chapter III** describes the conception phase, focusing on UML diagrams for system design.
- **Chapter IV** discusses the realization, covering implementation and user interface development.

We conclude with a summary of results, challenges encountered, and future perspectives, followed by references and annexes.

---

# Chapter 1: Preliminary Study

---

## 1.1 Project Presentation

### 1.1.1 Introduction

This preliminary study presents **Cable Manufacturing AI**, a comprehensive Streamlit-based monitoring, configuration, and quality-prediction system tailored for cable production lines at COFICAB. This chapter presents the project, analyzes the operational challenges, details the proposed solution with its four interconnected components, and outlines the development methodology, technologies, and architecture.

The application is built around three core workflows — **real-time OPC UA monitoring**, **parameter traceability**, and **model-driven prediction** — while the newly developed Configuration & Model Analysis Module forms the intelligent backbone of the system.

### 1.1.2 Problem Statement

In cable production, high-frequency sensor data and recipe parameters are collected via OPC UA and stored as raw time-series events in the `MachineTagValue` table. Operators and analysts lack a unified platform that connects live parameter values to expected specification ranges, integrates historical behavior analysis, and applies AI-powered quality models to raw signals.

Existing setups separate configuration management, reference datasheet generation, real-time monitoring, and quality correlation analysis, resulting in:

- **Delayed detection** of out-of-spec parameter deviations
- **Difficulty performing root-cause analysis** when quality issues arise
- **Limited explainability** of quality prediction outcomes
- **Fragmented workflows** requiring manual data gathering across multiple tools

This separation of concerns prevents COFICAB from achieving proactive, data-driven quality management in its high-volume cable manufacturing environment.

### 1.1.3 Proposed Solution

**Cable Manufacturing AI** is a unified, SQL Server-backed system that seamlessly integrates machine configuration management, automated reference datasheet generation, real-time parameter monitoring, and AI-powered quality insights through Mistral. The system supports two primary user roles:

- **Operators** — Monitor live production, detect out-of-spec parameters, and respond to deviations
- **Analysts** — Configure machines, build reference models from labeled production runs, and investigate quality correlations

The solution is structured around four interconnected components that form the Cable Manufacturing AI platform:

1. **Configuration Page (Streamlit UI)** — Full CRUD interface for creating, editing, and managing machine configurations with live machine-status indicators based on LineSpeed data.

2. **Model Page (Streamlit UI)** — Real-time parameter monitoring with specification-violation badges, traceability charts, quality prediction probability scores, and AI-generated root-cause analysis via Mistral.

3. **Analysis Page (Streamlit UI)** — Recipe-aware reference datasheet generator that discovers parameters in production run time-windows, collects labeled samples (up to 5,000 per parameter per run), and computes statistical baselines (Min, Optimal, Max, Mean, StdDev) with quality correlation.

4. **Notebook-Based Analysis Engine** — Jupyter notebooks executed via Papermill that build parameter reference datasheets, correlate parameters with OK/NOT OK production outcomes, and store results in the database.

Key features include OPC UA live connectivity, specification bands with visual violation badges, anomaly detection, full audit trails via `productionrun` and `ProductionRunQuality` tables, and natural-language root-cause explanations powered by Mistral AI. The platform directly addresses COFICAB's need for data-driven quality monitoring in high-volume cable manufacturing.

---

## 1.2 Software Development Methodology

### 1.2.1 Justification of Kanban

The project adopts **Kanban** for its flexibility, which is ideal for solo development. Tasks flow through a board with columns **To Do, In Progress, and Done** without fixed sprints, enabling continuous delivery and real-time adjustments as new requirements emerge during development.

As a solo developer working on the complex and evolving Cable Manufacturing AI project, Kanban is the superior choice. It eliminates Scrum's overhead of ceremonies and rigid sprints, enabling:

- **Continuous progress** without interruption for sprint planning
- **Immediate incorporation** of new insights from stakeholder feedback
- **Full flexibility** to adjust priorities at any time based on emerging requirements
- **Visual workflow management** using a simple board with clear task states

The Kanban board was maintained throughout the project lifecycle (January — May 2025) and is detailed in Chapter 2 with bi-weekly snapshots.

---

## 1.3 Presentation of the Host Company

### 1.3.1 History and Membership in the ELLOUMI Group

**COFICAB** is the leading global partner in the design, manufacturing, and sales of cables and wires. Founded in **1992** by **Mr. Hichem Elloumi** in Tunisia, the company is a proud member of the **ELLOUMI Group**, an industrial conglomerate established in **1946** by **Mr. Taoufik Elloumi**.

What began as a small Tunisian enterprise has grown into a major international player through exceptional organic growth and strategic expansion. The ELLOUMI Group has evolved through key milestones: SOTEE (1946), Chakira Distribution (1946), Chakira (1963), TEM (1982), COFAT (1984), and later STIFEN (1996), CHAKIRA IMMOBILIER (2000), and BTK (2021). COFICAB itself was established in 1992 and quickly became the group's flagship in automotive, energy, and appliance cables.

Mr. Hichem Elloumi, Chairman and CEO, emphasizes that COFICAB is fully committed to sustainability-driven growth and innovation, aiming to leave a better world for future generations. The company continues to expand its global footprint to be closer to customers while reducing its carbon footprint and supply-chain impact. Beyond its core leadership in the automotive megatrends of E-Mobility, Connectivity, and Autonomous Driving, COFICAB has successfully entered the appliance, medical, and distribution sectors, always working in close partnership with clients to meet their specific needs.

### 1.3.2 Key Figures (2024)

Today COFICAB operates on an impressive global scale:

| Metric | Value |
|--------|-------|
| Turnover | 4 billion USD |
| Wires and cables sold | 42 million kilometers |
| Global market share (automotive cables) | 23% (No. 1 worldwide) |
| Production sites | 20 (+ 5 ongoing) |
| Sales offices | 14 |
| R&D+I centers of excellence | 4 |
| Employees | 9,000 |
| Presence | 4 continents, 16 countries |

**Figure 1.1 – COFICAB Key Figures 2024 Infographic**

### 1.3.3 Vision

COFICAB's vision is to be the **best-in-class partner** for automotive cables and wires, committed to exceeding customer expectations through sustainable growth by:

- Expanding global presence to serve customers worldwide
- Striving for technology and operational excellence
- Sharing values and success with employees and partners

---

## 1.4 Technologies and Tools

The project utilizes the following technologies and tools:

| Category | Technologies |
|----------|-------------|
| **Frontend & UI** | Streamlit (Python-based web framework) |
| **Backend Logic** | Python 3.12 + Papermill for notebook execution |
| **Database** | SQL Server (OpcDb schema + model_schema) |
| **ML Models** | XGBoost, Random Forest, scikit-learn |
| **AI Integration** | Mistral AI API for natural-language root-cause analysis |
| **Connectivity** | OPC UA for live sensor data |
| **Data Processing** | Pandas, NumPy for feature engineering |
| **Visualization** | Plotly for interactive real-time charts |
| **Tools** | VS Code, Git/GitHub, SQLAlchemy, Jupyter Notebooks, dotenv |

---

## 1.5 Architecture

### 1.5.1 Application Architecture

The system follows a modular **Streamlit multi-page architecture** organized around three core operational pillars:

```
┌─────────────────────────────────────────────────────────────────────┐
│                   Streamlit Multi-Page Application                  │
├─────────────────────────────┬───────────────────┬───────────────────┤
│   Configuration & Setup     │  Live Monitoring   │  Analysis &       │
│   • Machine selection       │  • Real-time       │  Datasheet Gen.   │
│   • Parameter management    │    parameter cards  │  • Run selection  │
│   • Recipe configuration    │  • Spec violation   │  • Sample collect │
│   • Session persistence     │    badges           │  • Statistics     │
│   • CRUD operations         │  • Quality prob.    │  • Quality corr.  │
│                             │  • Traceability     │  • CSV export     │
│                             │    charts           │                   │
├─────────────────────────────┴───────────────────┴───────────────────┤
│                    Shared Database Helpers & ML Utils                │
│              db_helpers.py (queries, caching, analysis)              │
│              auth_helpers.py (authentication, sessions)              │
├─────────────────────────────────────────────────────────────────────┤
│                    SQL Server Database (OpcDb)                       │
│   MachineTagValue | productionrun | ProductionRunQuality             │
│   machine_configuration | parameter_reference_datasheet              │
│   users | tags_mapping | analysis_results_[MACHINE]                  │
├─────────────────────────────────────────────────────────────────────┤
│                    ML Models & Notebooks                              │
│   XGBoost / Random Forest | Jupyter Notebooks via Papermill           │
│   Mistral AI API | Plotly Charts                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Figure 1.2 – System Architecture Diagram**

**Data Flow:**

1. OPC UA sensors write data to `MachineTagValue` (time-series events)
2. Configuration page saves machine setups to `machine_configuration`
3. Analysis notebook (executed via Papermill) reads historical data, computes statistics, and stores reference datasheets
4. Model page loads reference datasheets and compares live values from `MachineTagValue` in real-time
5. Quality prediction score is computed based on parameter deviations from specification ranges
6. Out-of-spec parameters trigger Mistral AI for natural-language root-cause analysis

### 1.5.2 Database

The main SQL Server tables support structured monitoring and traceability:

| Schema | Table | Purpose |
|--------|-------|---------|
| `dbo` | `MachineTagValue` | Time-series sensor events (MachineCode, OpcNodeId, Value, SourceTimestamp, ProductionRunId) |
| `dbo` | `productionrun` | Run metadata (RunId, MachineCode, StartTs, EndTs, Status, ScopeKey) |
| `dbo` | `ProductionRunQuality` | Quality labels per run (RunId, IsOk) |
| `dbo` | `tags_mapping` | Machine-to-parameter mappings |
| `model_schema` | `machine_configuration` | User-saved configurations with monitoring and recipe parameters |
| `model_schema` | `parameter_reference_datasheet` | Generated specification ranges with RecipeIdentifier support |
| `model_schema` | `analysis_results_[MACHINE]` | Per-machine analysis results with RunSequence tracking |
| `model_schema` | `users` | User authentication with PBKDF2 password hashing |

---

## 1.6 Conclusion

This preliminary study establishes the foundation of **Cable Manufacturing AI** as a unified, production-ready monitoring and prediction system designed specifically for COFICAB's cable manufacturing environment. The platform, combining live OPC UA signals, SQL Server-backed traceability, machine-learning inference, and Mistral AI insights in Streamlit, directly addresses the gap between raw sensor data and actionable quality insight.

The modular architecture provides scalability, interpretability, and operational value, preparing the ground for detailed requirements specification and implementation in the following chapters.

---

# Chapter 2: Requirements Analysis and Specification

---

## 2.1 Introduction

This chapter defines the requirements for **Cable Manufacturing AI** using Kanban's iterative workflow. It identifies user profiles, specifies functional and non-functional requirements, describes use case diagrams, and presents the Kanban task board, aligning with the platform's goal of unified, data-driven quality monitoring with real-time AI support.

---

## 2.2 User Profiles

We identify two primary user roles for the Cable Manufacturing AI system:

| Role | Description |
|------|-------------|
| **Operator** | Shop-floor personnel responsible for monitoring live production parameters. Operators view real-time data, detect out-of-spec conditions, and respond to alerts. They do not modify machine configurations or generate datasheets. |
| **Analyst** | Quality engineers and data analysts responsible for configuring machines, selecting monitoring parameters, defining recipe parameters, generating reference datasheets, training quality models, and investigating quality correlations. Analysts have full access to all system features. |

---

## 2.3 Functional Requirements

We list the functional requirements (FR) to ensure Cable Manufacturing AI meets user and system needs:

| ID | Requirement | Role |
|----|-------------|------|
| FR1 | Authenticate: Users log in with User ID and password via PBKDF2-secured authentication | Both |
| FR2 | Register: New users create accounts with User ID and password | Both |
| FR3 | Logout: Authenticated users securely end their session | Both |
| FR4 | View Home Dashboard: Users see system overview, quick start guide, and key metrics | Both |
| FR5 | View Machine Status: Users see all machines with real-time LineSpeed-based status (Working/Standby) | Both |
| FR6 | Create Configuration: Analysts create new machine configurations with monitoring and recipe parameters | Analyst |
| FR7 | Edit Configuration: Analysts modify existing machine configurations | Analyst |
| FR8 | Delete Configuration: Analysts remove machine configurations | Analyst |
| FR9 | View Configurations: Analysts browse and search saved configurations by machine | Analyst |
| FR10 | Select Monitoring Parameters: Analysts choose which OPC NodeIds to track for a machine | Analyst |
| FR11 | Designate Recipe Parameters: Analysts mark a subset of monitoring parameters as recipe-defining | Analyst |
| FR12 | Save Configuration: System persists configurations to `machine_configuration` table | Analyst |
| FR13 | Load Last 10 Runs: System retrieves the most recent production runs for a selected machine | Analyst |
| FR14 | Discover Run Parameters: System identifies all OpcNodeIds recorded during a production run's time window | Analyst |
| FR15 | Select Sample Runs: Analysts choose production runs for sample collection | Analyst |

| ID | Requirement | Role |
|----|-------------|------|
| FR16 | Generate Datasheet: System collects up to 5,000 samples per parameter per selected run | Analyst |
| FR17 | Calculate Statistics: System computes Min, Optimal (median of OK samples), Max, Mean, StdDev per parameter | Analyst |
| FR18 | Correlate Quality: System labels samples with IsOk from ProductionRunQuality table | Analyst |
| FR19 | View Datasheet: Analysts view generated reference datasheets with parameter statistics | Analyst |
| FR20 | Download Datasheet CSV: Analysts export reference datasheets as CSV files | Analyst |
| FR21 | Display Historical Datasheets: System shows previous analysis runs for comparison | Analyst |
| FR22 | Select Configuration for Monitoring: Operators select a saved configuration to monitor | Both |
| FR23 | Display Reference Ranges: System shows Min/Max specification ranges from analysis results | Operator |
| FR24 | Show Real-Time Values: System displays current parameter values from MachineTagValue | Operator |
| FR25 | Compute Quality Probability: System calculates a quality prediction score based on parameter deviations | Operator |
| FR26 | Show Spec Violation Badges: System visually highlights out-of-range parameters | Operator |
| FR27 | Display Recipe Parameter Cards: System shows recipe parameters with navy-themed cards | Operator |
| FR28 | Display Monitoring Parameter Cards: System shows detailed monitoring cards with status and range info | Operator |
| FR29 | Show 3-Second Traceability: System renders real-time sliding-window charts (last 3 seconds) | Operator |
| FR30 | Show Full Timeline: System renders complete historical traceability charts | Operator |
| FR31 | Compare Parameters: Operators overlay multiple parameters on traceability charts | Operator |
| FR32 | Trigger Root Cause Analysis: System sends out-of-spec parameter data to Mistral AI for analysis | Operator |
| FR33 | Display Mistral Insights: System presents AI-generated root cause analysis and corrective actions | Operator |
| FR34 | Auto-Refresh Monitoring: System refreshes parameter values every 1 second via Streamlit fragments | Operator |

---

## 2.4 Non-Functional Requirements

We specify non-functional requirements (NFR) to ensure system performance and usability:

| ID | Requirement |
|----|-------------|
| NFR1 | **Performance**: Real-time monitoring fragment refreshes within 1 second. Database queries complete within 10 seconds for typical workloads. |
| NFR2 | **Scalability**: System handles monitoring of up to 50 parameters simultaneously across multiple machines. Database caching (TTL: 10–600 seconds) reduces query load. |
| NFR3 | **Availability**: Core monitoring functionality remains operational even if Mistral AI API is unavailable. Graceful degradation with local quality scoring. |
| NFR4 | **Security**: Passwords hashed with PBKDF2-HMAC-SHA256 (120,000 iterations). Session tokens use HMAC-signed payloads. LocalStorage-based session persistence with query-parameter fallback. |
| NFR5 | **Usability**: Intuitive UI with clear navigation (Configuration → Realtime → Analysis). Machine status indicators (Working/Standby) provide immediate operational awareness. |
| NFR6 | **Data Integrity**: Analysis results stored with RunSequence tracking for auditability. Configuration changes logged with timestamps. Database transactions ensure consistency. |
| NFR7 | **Caching Strategy**: Multi-tier caching: Streamlit `@st.cache_data` decorators with configurable TTLs (10s for real-time, 300s for configurations, 600s for analysis results). |
| NFR8 | **Error Handling**: Database deadlock detection with retry logic (exponential backoff). Graceful fallbacks when API keys are missing. Clear user-facing error messages. |

---

## 2.5 Use Case Diagrams

We describe use case diagrams to model system interactions:

**General Use Case Diagram (Main System):** Shows interactions of Operator and Analyst roles with use cases including authentication, machine configuration management, real-time monitoring, datasheet generation, and root cause analysis.

**Figure 2.1 – General Use Case Diagram**

The main system encompasses the following primary use cases:

- **Authenticate** (FR1–FR3): Login, register, and logout with session management
- **Manage Configuration** (FR6–FR12): Create, read, update, delete machine configurations
- **Monitor Parameters** (FR22–FR31): Real-time parameter monitoring with specification comparison
- **Generate Datasheet** (FR13–FR21): Production run analysis and reference datasheet generation
- **Analyze Root Cause** (FR32–FR33): AI-powered anomaly analysis via Mistral

**Operator Use Case Diagram:** Focuses on the Operator's limited but critical capabilities — selecting configurations, viewing real-time parameter values, detecting out-of-spec conditions, viewing traceability charts, and triggering root cause analysis.

**Figure 2.2 – Operator Use Case Diagram**

**Analyst Use Case Diagram:** Covers the full range of Analyst capabilities — all Operator actions plus configuration management (CRUD), production run selection, sample collection, datasheet generation, and quality correlation analysis.

**Figure 2.3 – Analyst Use Case Diagram**

---

## 2.6 Kanban Task Board

We organize tasks using a **Kanban board**, reflecting the iterative workflow updated through the project lifecycle (January — May 2025):

**Figure 2.4 – Initial Backlog - January 15**

| To Do | In Progress | Done |
|-------|-------------|------|
| Project setup & environment | Requirements gathering | — |
| Database schema design | OPC UA connectivity research | — |
| Authentication system | Technology stack selection | — |
| Machine configuration CRUD | — | — |
| Real-time monitoring UI | — | — |

**Figure 2.5 – Week 3 - January 30**

| To Do | In Progress | Done |
|-------|-------------|------|
| Real-time monitoring UI | Database schema design | Project setup & environment |
| Mistral AI integration | Authentication system | Requirements gathering |
| Analysis notebook | Machine configuration CRUD | OPC UA connectivity research |
| Deployment configuration | — | Technology stack selection |

**Figure 2.6 – Week 5 - February 15**

| To Do | In Progress | Done |
|-------|-------------|------|
| Mistral AI integration | Real-time monitoring UI | Project setup & environment |
| Deployment configuration | Analysis notebook | Requirements gathering |
| Quality prediction algorithm | — | OPC UA connectivity research |
| Testing & validation | — | Technology stack selection |
| — | — | Database schema design |
| — | — | Authentication system |
| — | — | Machine configuration CRUD |

**Figure 2.7 – Week 7 – March 1**

| To Do | In Progress | Done |
|-------|-------------|------|
| Mistral AI integration | Deployment configuration | Project setup & environment |
| Testing & validation | Quality prediction algorithm | Requirements gathering |
| Traceability charts | — | OPC UA connectivity research |
| CSV export functionality | — | Technology stack selection |
| — | — | Database schema design |
| — | — | Authentication system |
| — | — | Machine configuration CRUD |
| — | — | Real-time monitoring UI |
| — | — | Analysis notebook |

**Figure 2.8 – Week 9 – March 15**

| To Do | In Progress | Done |
|-------|-------------|------|
| Testing & validation | Mistral AI integration | Project setup & environment |
| Documentation | Traceability charts | Requirements gathering |
| Performance optimization | CSV export functionality | OPC UA connectivity research |
| — | — | Technology stack selection |
| — | — | Database schema design |
| — | — | Authentication system |
| — | — | Machine configuration CRUD |
| — | — | Real-time monitoring UI |
| — | — | Analysis notebook |
| — | — | Deployment configuration |
| — | — | Quality prediction algorithm |

**Figure 2.9 – Week 11 – April 1**

| To Do | In Progress | Done |
|-------|-------------|------|
| Documentation | Testing & validation | Project setup & environment |
| — | Performance optimization | Requirements gathering |
| — | Mistral AI integration (final) | OPC UA connectivity research |
| — | — | Technology stack selection |
| — | — | Database schema design |
| — | — | Authentication system |
| — | — | Machine configuration CRUD |
| — | — | Real-time monitoring UI |
| — | — | Analysis notebook |
| — | — | Deployment configuration |
| — | — | Quality prediction algorithm |
| — | — | Traceability charts |
| — | — | CSV export functionality |

**Figure 2.10 – Week 13 – April 15**

| To Do | In Progress | Done |
|-------|-------------|------|
| — | Documentation | All previous tasks |
| — | Testing & validation | Mistral AI integration |
| — | Performance optimization | — |
| — | Bug fixes | — |

**Figure 2.11 – Week 15 – May 1**

| To Do | In Progress | Done |
|-------|-------------|------|
| — | Final testing & bug fixes | All core features implemented |
| — | Report writing | Documentation |
| — | — | Performance optimization |
| — | — | Mistral AI integration complete |

**Figure 2.12 – Week 17 – May 20**

| To Do | In Progress | Done |
|-------|-------------|------|
| — | — | All tasks completed |
| — | — | Final report submission |

---

## 2.7 Conclusion

This chapter defines Cable Manufacturing AI's requirements and task organization, ensuring alignment with user needs and system goals including AI-powered root cause analysis. The Kanban approach facilitated flexible development, while use case diagrams clarified interactions between Operators and Analysts. The next chapter details the system's design through UML diagrams.

---

# Chapter 3: Conception

---

## 3.1 Introduction

This chapter present the design of **Cable Manufacturing AI**, focusing on UML diagrams to model the system's structure and behavior. This chapter organizes the UML content to guide development and ensure clarity across the Streamlit frontend, database layer, ML models, and Mistral AI integration.

---

## 3.2 UML Diagrams

We model Cable Manufacturing AI using UML to ensure alignment across Streamlit pages, SQL Server database, machine-learning models, and Mistral AI. The diagrams include **use case**, **class**, **sequence**, and **activity** diagrams, detailed below.

### 3.2.1 Use Case Diagrams

#### 3.2.1.1 System Use Case Diagram (Main)

We detail the primary system interactions, including authentication, machine configuration management, real-time monitoring, datasheet analysis, and root cause analysis.

**Figure 3.1 – System Use Case Diagram (Main)**

The main system includes the following actors and their associated use cases:

**Operator:**
- Authenticate (Login / Register / Logout)
- Select Configuration
- View Real-Time Parameters
- View Specification Ranges
- Detect Out-of-Spec Parameters
- View Traceability Charts
- Trigger Root Cause Analysis

**Analyst:**
- All Operator use cases
- Create / Edit / Delete Configuration
- Select Monitoring Parameters
- Designate Recipe Parameters
- Select Production Runs
- Generate Reference Datasheet
- View Analysis History
- Download Datasheet CSV

---

#### 3.2.1.2 Configuration Management — Use Case Diagram

**Figure 3.2 – Configuration Management Use Case Diagram**

**TABLE 3.1 – Configure Machine — Use Case Textual Description**

| Element | Description |
|---------|-------------|
| **Use Case Name** | Configure Machine |
| **Actor** | Analyst |
| **Description** | Analyst creates or modifies a machine configuration by selecting monitoring parameters and designating recipe parameters |
| **Precondition** | Analyst is authenticated. Machine exists in MachineTagValue. |
| **Postcondition** | Configuration is saved to `model_schema.machine_configuration` |
| **Main Flow** | 1. Analyst navigates to Configuration page. 2. System displays machine status table. 3. Analyst fills configuration form (name, machine, monitoring params, recipe params, description). 4. System validates inputs. 5. System saves configuration. 6. System confirms success. |
| **Alternative Flow** | If configuration name already exists for the machine, system displays error. If recipe parameters are not a subset of monitoring parameters, system displays validation error. |

---

#### 3.2.1.3 Real-Time Monitoring — Use Case Diagram

**Figure 3.3 – Real-Time Monitoring Use Case Diagram**

**TABLE 3.2 – Monitor Parameters — Use Case Textual Description**

| Element | Description |
|---------|-------------|
| **Use Case Name** | Monitor Parameters |
| **Actor** | Operator (and Analyst) |
| **Description** | Operator views real-time parameter values compared against specification ranges with quality prediction probability |
| **Precondition** | Configuration has been analyzed. Reference datasheet exists. Machine is active. |
| **Postcondition** | Operator sees live parameter values with status indicators |
| **Main Flow** | 1. Operator selects configuration from dropdown. 2. System loads reference datasheet from latest analysis. 3. System fetches live values from MachineTagValue. 4. System computes quality probability score. 5. System displays parameter cards with color-coded status. 6. Cards auto-refresh every 1 second. |
| **Alternative Flow** | If machine is in Standby (LineSpeed = 0), system displays "Standby" status. If parameters have no data, system shows "Waiting for value..." state. If parameters are out of range, system displays violation badges. |

---

#### 3.2.1.4 Analysis & Datasheet Generation — Use Case Diagram

**Figure 3.4 – Analysis & Datasheet Generation Use Case Diagram**

**TABLE 3.3 – Generate Datasheet — Use Case Textual Description**

| Element | Description |
|---------|-------------|
| **Use Case Name** | Generate Datasheet |
| **Actor** | Analyst |
| **Description** | Analyst selects a machine, picks recipe parameters, chooses production runs, and generates a statistical reference datasheet |
| **Precondition** | Analyst is authenticated. Machine has production runs with data. |
| **Postcondition** | Reference datasheet is saved to `parameter_reference_datasheet` table. Analysis history is stored in `analysis_results_[MACHINE]`. |
| **Main Flow** | 1. Analyst navigates to Analysis page. 2. System displays step-by-step workflow. 3. Analyst selects machine. 4. Analyst selects recipe parameters (OpcNodeIds). 5. System loads last 10 production runs. 6. Analyst selects a run. 7. System discovers all parameters in run's time window. 8. Analyst selects sample runs. 9. System collects up to 5,000 samples per parameter per run. 10. System computes statistics (Min, Optimal, Max, Mean, StdDev). 11. System correlates with quality labels. 12. System saves datasheet. |
| **Alternative Flow** | If ProductionRunQuality table has no matching records, all samples are labeled IsOk=0. If database deadlock occurs, system retries with exponential backoff. |

---

#### 3.2.1.5 Mistral AI Root Cause Analysis — Use Case Diagram

**Figure 3.5 – Mistral AI Integration Use Case Diagram**

**TABLE 3.4 – Root Cause Analysis — Use Case Textual Description**

| Element | Description |
|---------|-------------|
| **Use Case Name** | Analyze Root Cause |
| **Actor** | Operator (triggered automatically or manually) |
| **Description** | System sends out-of-spec parameter data to Mistral AI and receives natural-language root cause analysis with corrective actions |
| **Precondition** | MISTRAL_API_KEY is configured. At least one parameter is out of specification range. |
| **Postcondition** | Operator views AI-generated analysis with root cause, immediate actions, and preventive measures |
| **Main Flow** | 1. System detects quality probability < 50% OR operator clicks "Analyze Root Cause". 2. System collects out-of-range parameters with values, ranges, and deviations. 3. System constructs prompt with machine context. 4. System calls Mistral AI API. 5. System displays generated analysis with root cause, corrective actions, and preventive recommendations. |
| **Alternative Flow** | If Mistral API is unavailable, system displays error message. If no parameters are out of range, system notifies operator. |

---

### 3.2.2 Class Diagram

**Figure 3.6 – Class Diagram — System Entities**

We define the core entities of Cable Manufacturing AI with their attributes and relationships:

**User:**
- UserId (PK), PasswordHash, PasswordSalt, CreatedAt, LastLoginAt, IsActive
- Methods: authenticate(), register()

**MachineConfiguration:**
- ConfigurationId (PK), ConfigurationName, MachineCode, MonitoringParameters (JSON), RecipeParameters (JSON), Description, IsActive, CreatedAt, UpdatedAt

**ProductionRun:**
- RunId (PK), MachineCode, StartTs, EndTs, Status, ScopeKey (RecipeIdentifier)

**ProductionRunQuality:**
- RunId (PK), MachineCode, Quality, StartTime, EndTime, Duration, IsOk

**MachineTagValue:**
- MachineCode, OpcNodeId, Value, SourceTimestamp, ProductionRunId

**ParameterReferenceDatasheet:**
- DatasheetId (PK), MachineCode, RecipeIdentifier, OpcNodeId, ParameterName, MinValue, OptimalValue, MaxValue, MeanValue, StdDev, SampleCount, QualityOkCount, QualityNotOkCount

**TagsMapping:**
- MachineCode, Parameter (Tag)

**AnalysisResult:**
- ResultId (PK), RunSequence, AnalysisTimestamp, ConfigurationId, ConfigurationName, MachineCode, OpcNodeId, ParameterName, MinValue, MeanValue, MaxValue, StdDev, SampleCount

**Relationships:**
- User → MachineConfiguration (1:N via created_by)
- MachineConfiguration → AnalysisResult (1:N via ConfigurationId)
- ProductionRun → ProductionRunQuality (1:1 via RunId)
- ProductionRun → MachineTagValue (1:N via ProductionRunId)
- MachineConfiguration → ParameterReferenceDatasheet (M:N via MachineCode)

**Figure 3.7 – Class Diagram (With ML Backend)**

We extend the class diagram to include the ML and AI components:

**QualityPredictionModel:**
- ModelId, ModelType (RandomForest / XGBoost / RuleBased), ModelPath (.pkl file), FeatureNames, ScalerPath, CreatedAt, Accuracy

**AnomalyDetector:**
- DetectorId, ModelType, Threshold, FeatureColumns, ModelPath

**MistralAIService:**
- ApiKey, ModelName (mistral-small-latest / mistral-large-latest)
- Methods: analyzeRootCause(), generatePrompt(), parseResponse()

**AnalysisEngine:**
- Methods: executeNotebook(), extractResults(), storeResults(), computeStatistics()

The ML backend includes 13 trained pickle artifacts:
- `quality_model_rf.pkl` — Random Forest quality classifier
- `opcua_quality_xgboost.pkl` — XGBoost quality classifier
- `opcua_quality_random_forest.pkl` — Alternative RF model
- `anomaly_detector.pkl` / `opcua_anomaly_detector.pkl` — Anomaly detection models
- `feature_scaler.pkl` / `scaler.pkl` — Feature normalization
- `machine_encoder.pkl` / `recipe_encoder.pkl` — Categorical encoders
- `feature_names.pkl` / `feature_columns.pkl` — Feature metadata
- `xgboost_model.pkl` — Additional XGBoost model
- `opcua_quality_model_metadata.pkl` — Model metadata and configuration

---

### 3.2.3 Sequence Diagrams

We employ sequence diagrams to demonstrate chronological interactions between system components. These visualizations precisely track how objects exchange messages during operations.

#### 3.2.3.1 Authentication — Sequence Diagram

**Figure 3.8 – Authentication Sequence Diagram**

**Flow:**
1. User enters User ID and password on Authentication page
2. Authentication page calls `authenticate_user()` from `auth_helpers.py`
3. `auth_helpers.py` queries `model_schema.users` table via SQLAlchemy
4. System verifies password using PBKDF2-HMAC-SHA256 with stored salt
5. On success, `sign_in_user()` creates HMAC-signed session token
6. Session token is stored in `st.session_state` and synced to `window.localStorage`
7. User is redirected to the requested page (or home page)

---

#### 3.2.3.2 Machine Configuration — Sequence Diagram

**Figure 3.9 – Machine Configuration Sequence Diagram**

**Flow:**
1. Analyst selects machine from dropdown
2. Configuration page calls `load_all_parameters_for_machine()` from `db_helpers.py`
3. `db_helpers.py` queries `MachineTagValue` for distinct OpcNodeIds
4. System displays available parameters
5. Analyst selects monitoring parameters and designates recipe parameters
6. Analyst clicks "Save Configuration"
7. System calls `add_machine_configuration()` with JSON-serialized parameter lists
8. System inserts into `model_schema.machine_configuration`
9. System clears cache and confirms success

---

#### 3.2.3.3 Real-Time Monitoring — Sequence Diagram

**Figure 3.10 – Real-Time Monitoring Sequence Diagram**

**Flow:**
1. Operator selects a saved configuration
2. Model page loads config from `machine_configuration` table
3. System calls `load_latest_analysis_results()` to retrieve reference datasheet
4. System calls `get_machine_status_by_linespeed()` to check LineSpeed-based status
5. System starts 1-second Streamlit fragment auto-refresh
6. Each second: `load_current_machine_values()` fetches latest values from `MachineTagValue`
7. System compares each value against Min/Max from reference datasheet
8. System computes quality probability score based on deviation magnitude
9. System renders parameter cards with color-coded status indicators
10. Operator views real-time data with spec violation badges

---

#### 3.2.3.4 Datasheet Analysis — Sequence Diagram

**Figure 3.11 – Datasheet Analysis Sequence Diagram**

**Flow:**
1. Analyst selects machine and recipe parameters
2. System loads last 10 production runs from `productionrun` table
3. Analyst selects a run to analyze
4. System discovers all parameters in run's time window via `get_all_params_in_time_window()`
5. Analyst selects sample runs (1–10 runs) for data collection
6. Analyst clicks "Generate Datasheet"
7. System calls `get_labeled_samples_from_runs()` — up to 5,000 samples per parameter per run
8. System labels samples using `ProductionRunQuality.IsOk`
9. System calls `calculate_recipe_parameter_statistics_from_samples()`
10. System saves results via `save_recipe_datasheet()` to `parameter_reference_datasheet`
11. System displays generated datasheet with sample counts and quality correlation

---

#### 3.2.3.5 Root Cause Analysis — Sequence Diagram

**Figure 3.12 – Root Cause Analysis Sequence Diagram**

**Flow:**
1. System detects quality probability < 50% OR Operator clicks "Analyze Root Cause"
2. System collects out-of-range parameters with current values and specification ranges
3. System constructs a detailed prompt with machine context and parameter deviation data
4. System calls Mistral AI API (either via `requests` to REST API or `mistralai` SDK)
5. Mistral AI processes the prompt and returns natural-language analysis
6. System displays: (a) Most likely root cause, (b) Immediate corrective actions, (c) Preventive measures
7. Operator can view the analysis and take appropriate action

---

### 3.2.4 Activity Diagrams

We use activity diagrams to model system workflows through actions, decisions, and parallel processes.

#### 3.2.4.1 User Login — Activity Diagram

**Figure 3.13 – User Login Activity Diagram**

**Flow:**
1. User navigates to Authentication page
2. System checks for existing session (query params, LocalStorage, session state)
3. [Session exists] → User is redirected to target page
4. [No session] → User sees Login form
5. User enters User ID and password
6. System validates credentials against database
7. [Valid] → System creates session token → System redirects to home page
8. [Invalid] → System displays error message → User retries

---

#### 3.2.4.2 User Registration — Activity Diagram

**Figure 3.14 – User Registration Activity Diagram**

**Flow:**
1. User navigates to Register tab
2. User enters User ID and password
3. System checks if User ID already exists
4. [Exists] → System displays "User ID already exists" error
5. [New] → System generates random 16-byte salt
6. System hashes password with PBKDF2-HMAC-SHA256 (120,000 iterations)
7. System inserts new user record into `model_schema.users`
8. System auto-logs in the new user
9. User is redirected to home page

---

#### 3.2.4.3 Machine Configuration — Activity Diagram

**Figure 3.15 – Machine Configuration Activity Diagram**

**Flow:**
1. Analyst navigates to Configuration page
2. System loads all machines and their LineSpeed-based status
3. Analyst selects a machine from the dropdown
4. System loads all available parameters for that machine
5. Analyst enters configuration name
6. Analyst selects monitoring parameters from the list
7. Analyst selects recipe parameters (subset of monitoring params)
8. System validates: recipe params ⊆ monitoring params
9. [Invalid] → System displays error → Analyst corrects
10. [Valid] → System saves to database
11. System clears cache and confirms success

---

#### 3.2.4.4 Real-Time Monitoring — Activity Diagram

**Figure 3.16 – Real-Time Monitoring Activity Diagram**

**Flow:**
1. Operator selects a configuration from dropdown
2. System loads reference datasheet from latest analysis results
3. System checks machine LineSpeed-based status
4. [Machine Standby] → Display standby message → Keep checking status
5. [Machine Active] → Start 1-second monitoring loop:
   - Fetch latest parameter values from MachineTagValue
   - Compare each value against Min/Max specification
   - Compute quality probability score
   - Render parameter cards with status (STABLE, NEAR MIN, NEAR MAX, OUT OF RANGE)
   - Update quality prediction probability gauge
   - [Parameters out of range] → Display violation badges
   - [Probability < 50%] → Auto-trigger Mistral root cause analysis
6. Wait 1 second → Repeat monitoring loop

---

## 3.3 Conclusion

To conclude, the UML diagrams provide a comprehensive design for Cable Manufacturing AI, clarifying interactions and structure with focus on real-time monitoring and AI integration. These models guide the implementation phase, detailed in the next chapter.

---

# Chapter 4: Realization

---

## 4.1 Introduction

This chapter details the implementation of **Cable Manufacturing AI**, including code realization, UI design, and the integration of machine-learning models with Mistral AI for root cause analysis.

---

## 4.2 Implementation

We implement Cable Manufacturing AI using **Streamlit** for the multi-page frontend, **SQL Server** for the database, and **Python** for the backend logic. Key implementation details follow.

### Technology Stack

**TABLE 4.1 – Technology Stack Summary**

| Layer | Technology | Details |
|-------|-----------|---------|
| **Frontend** | Streamlit 1.x | Multi-page app with custom CSS theming |
| **Backend** | Python 3.12 | Modular package structure |
| **Database** | SQL Server | OpcDb schema + model_schema |
| **ORM** | SQLAlchemy | Database connectivity with connection pooling |
| **ML** | scikit-learn, XGBoost | Random Forest & XGBoost classifiers |
| **AI** | Mistral AI API | Root cause analysis via `mistral-small-latest` and `mistral-large-latest` |
| **Automation** | Papermill | Jupyter notebook execution |
| **Charts** | Plotly | Interactive time-series visualizations |
| **Auth** | PBKDF2-HMAC-SHA256 | Password hashing with 120,000 iterations |
| **Caching** | Streamlit `@st.cache_data` | Multi-tier TTL-based caching |

### Database Tables

**TABLE 4.2 – Database Tables Summary**

| Table | Schema | Purpose |
|-------|--------|---------|
| `MachineTagValue` | `dbo` | Time-series sensor events (core data source) |
| `productionrun` | `dbo` | Production run metadata |
| `ProductionRunQuality` | `dbo` | Quality labels (OK = 1, NOT OK = 0) |
| `tags_mapping` | `dbo` | Machine-to-parameter mappings |
| `machine_configuration` | `model_schema` | User-saved configurations |
| `parameter_reference_datasheet` | `model_schema` | Statistical reference ranges |
| `analysis_results_[MACHINE]` | `model_schema` | Per-machine analysis history |
| `users` | `model_schema` | Authentication data |
| `coverage_analysis_results` | `model_schema` | Parameter coverage reports |
| `parameter_optimal_windows` | `model_schema` | Stable-window exclusions |
| `configuration_reports` | `model_schema` | Configuration analysis reports |

### Key Implementation Components

#### 4.2.1 Authentication System (`auth_helpers.py` — 485 lines)

The authentication system implements a secure, stateless session management approach:

- **Password Hashing**: PBKDF2-HMAC-SHA256 with 120,000 iterations and random 16-byte salt
- **Session Tokens**: HMAC-SHA256 signed JSON payloads with expiration (7-day TTL) and nonce
- **Session Persistence**: Three-layer recovery — `st.session_state` → URL query parameters → `window.localStorage`
- **Automatic Login Flow**: `bootstrap_auth_page()` automatically redirects authenticated users to their target page
- **Logout**: Clears all session state, query params, and local storage

#### 4.2.2 Database Helpers (`db_helpers.py` — 2,308 lines)

The database layer provides comprehensive data access with caching:

- **Caching Strategy**: `@st.cache_data` decorators with configurable TTLs (10s for real-time, 60s for sensor traces, 300s for configurations, 600s for analysis)
- **Machine Configuration CRUD**: Full create, read, update, delete operations with JSON-serialized parameter lists
- **Analysis Results Storage**: Per-machine tables (`analysis_results_[MACHINE]`) with `RunSequence` tracking for versioned analysis history
- **Production Run Queries**: Time-window based parameter discovery, sample collection (up to 5,000 per run), quality-labeled sample extraction
- **Mistral AI Integration**: `call_mistral_ai()` and `analyze_parameter_anomaly()` functions for AI-powered root cause analysis
- **Machine Status**: Dual-mode status detection — data availability and LineSpeed-based working/standby classification
- **Deadlock Handling**: Retry logic with exponential backoff (0.5s, 1s, 1.5s) for SQL Server deadlock errors (Error 1205)

#### 4.2.3 Machine Configuration Page (`configuration_page.py` — 672 lines)

The configuration page provides a complete CRUD interface:

- **Machine Status Display**: Real-time LineSpeed-based Working/Standby indicators with auto-refresh
- **Add Configuration**: Step-by-step form with machine selection, parameter browsing, monitoring/recipe designation, and description
- **View & Edit**: Searchable configuration list with expandable details, in-place editing with parameter validation
- **Delete**: Confirmation workflow with visual safety check
- **Validation**: Recipe parameters must be a subset of monitoring parameters; configuration names must be unique per machine

#### 4.2.4 Real-Time Monitoring Page (`model_page.py` — 2,398 lines)

The most complex page handles real-time monitoring with ML-powered quality prediction:

- **Configuration Selector**: Dropdown with machine status and parameter count metadata
- **Reference Datasheet Display**: Analyzed configuration statistics with Min/Mean/Max per parameter
- **Quality Prediction Algorithm**: Rule-based scoring that measures deviation of each parameter from its specification midpoint, normalized by specification span
- **Real-Time Fragments**: Two Streamlit `@st.fragment` decorators with `run_every=1` — one for monitoring data, one for parameter card rendering
- **Parameter Cards**: Color-coded containers showing current value, status badge (STABLE, NEAR MIN, NEAR MAX, OUT OF RANGE, NO DATA, STALE), specification range, and last update time
- **3-Second Sliding Window Trace**: Ultra-fast real-time charts using cached sliding-window approach (drop oldest second, add newest)
- **Full Timeline Trace**: Complete historical view with snapshot capability at any moment
- **Parameter Overlay**: Compare two parameters on the same chart with auto-scaling secondary Y-axis
- **Root Cause Analysis**: Auto-triggered Mistral AI analysis when quality probability drops below 50%

#### 4.2.5 Analysis & Datasheet Page (`analysis_page.py` — 665 lines)

The analysis page implements a recipe-aware datasheet generation workflow:

- **6-Step Workflow**: Machine selection → Recipe parameter selection → Run loading → Parameter discovery → Sample run selection → Datasheet generation
- **Quality Diagnostics**: Detailed quality lookup results showing matched/missing runs and OK/NOT OK sample counts
- **Statistical Computation**: Per-parameter Min (overall), Optimal (median of OK samples), Max (overall), Mean, StdDev, with QualityOkCount and QualityNotOkCount
- **Analysis History**: Previous analysis runs browsable with detailed preview
- **CSV Export**: Generated datasheets downloadable as CSV files

### Machine Learning Models

The system includes 13 trained ML artifacts stored as pickle files:

| Model File | Type | Purpose |
|-----------|------|---------|
| `quality_model_rf.pkl` | Random Forest | Primary quality classifier |
| `opcua_quality_xgboost.pkl` | XGBoost | Gradient-boosted quality classifier |
| `opcua_quality_random_forest.pkl` | Random Forest | Alternative RF model |
| `anomaly_detector.pkl` | Isolation Forest | Anomaly detection for parameter values |
| `opcua_anomaly_detector.pkl` | Isolation Forest | Alternative anomaly detector |
| `feature_scaler.pkl` | StandardScaler | Feature normalization |
| `scaler.pkl` | StandardScaler | Alternative scaler |
| `machine_encoder.pkl` | LabelEncoder | Machine code encoding |
| `recipe_encoder.pkl` | LabelEncoder | Recipe parameter encoding |
| `feature_names.pkl` | List | Feature column names |
| `feature_columns.pkl` | List | Feature column configuration |
| `xgboost_model.pkl` | XGBoost | Additional XGBoost model |
| `opcua_quality_model_metadata.pkl` | Dict | Model configuration and metadata |

---

## 4.3 User Interface

We designed an intuitive UI with a learning curve of less than 10 minutes. Key interfaces include:

**Figure 4.1 – Home Page Interface Screenshot**

The home page displays a dashboard with:
- System title and build information
- Quick start guide (two-step workflow)
- Key features overview (8 feature cards)
- System architecture diagram
- Database schema reference
- Tips and best practices expandable section

**Figure 4.2 – Authentication Page Interface Screenshot**

The authentication page features:
- Secure login and registration tabs
- PBKDF2-based password hashing
- Automatic session recovery from browser LocalStorage
- COFICAB-themed design with company logo

**Figure 4.3 – Configuration Page Interface Screenshot**

The configuration page provides:
- Machine status table with LineSpeed-based Working/Standby indicators
- Three-tab interface: Add Configuration, View & Edit, Delete
- Machine selection with status icons (green = Working, yellow = Standby)
- Parameter multi-select with full OPC NodeId display
- Recipe parameter designation (subset of monitoring parameters)
- In-line editing with validation

**Figure 4.4 – Real-Time Monitoring Interface Screenshot**

The real-time monitoring page features:
- Configuration selector with status badges
- Analyzed configuration datasheet with specification ranges
- Configuration metrics (Machine, Status, Elapsed since analysis, Prediction Probability)
- Recipe parameters section (navy-background cards)
- Monitoring parameters section (detailed cards with color-coded status)
- 3-second sliding window traceability chart (real-time)
- Full timeline traceability chart (historical snapshot)
- Parameter overlay comparison
- Root cause analysis button and dialog

**Figure 4.5 – Analysis & Datasheet Interface Screenshot**

The analysis page provides:
- 6-step guided workflow with session state persistence
- Machine and recipe parameter selection
- Production run browser (last 10 runs)
- Parameter discovery (all parameters in run time window)
- Sample run multi-select (1–10 runs)
- Quality diagnostics (matched/missing runs, OK/NOT OK distribution)
- Generated datasheet with statistical summaries
- Previous analysis history browser
- CSV download functionality

**Figure 4.6 – Traceability Chart Interface Screenshot**

Traceability charts feature:
- Real-time 3-second sliding window (auto-refreshing)
- Full historical timeline (static snapshot)
- Specification range visualization (green zone = normal, red zones = out of spec)
- Target/mean line overlay
- Parameter comparison overlay with secondary Y-axis
- Summary metrics (readings, min, mean, max, in-spec percentage)
- Out-of-spec root cause alerts with first occurrence and worst value

**Figure 4.7 – Mistral AI Root Cause Analysis Screenshot**

The Mistral AI integration provides:
- Automatic trigger when quality probability < 50%
- Manual trigger via "Analyze Root Cause" button
- Structured output: (1) Most likely root cause, (2) Immediate corrective actions, (3) Preventive measures
- Context-aware prompting with machine code, parameter details, and deviation metrics

---

## 4.4 Deployment and Monitoring

### 4.4.1 Introduction

Cable Manufacturing AI is designed for flexible deployment options:

**Local Development:**
- Python 3.12 virtual environment with `requirements.txt`
- `.env` file for database credentials and API keys
- Quick-start scripts (`quick_start.bat` for Windows, `quick_start.sh` for Linux)
- Run with: `streamlit run app/app.py`

**Production Deployment:**
- Streamlit Cloud deployment with environment variable configuration
- SQL Server database connection via `db_connection.py` with SQLAlchemy engine
- Mistral AI API key required for root cause analysis features
- Notebook execution requires Papermill with Jupyter kernel

### 4.4.2 Configuration

The system uses environment variables for configuration:

| Variable | Description |
|----------|-------------|
| `DB_HOST` | SQL Server hostname |
| `DB_USER` | Database username |
| `DB_PASSWORD` | Database password |
| `DB_NAME` | Database name (default: OpcDb) |
| `MISTRAL_API_KEY` | Mistral AI API key |
| `MISTRAL_MODEL` | Mistral model name (default: mistral-small-latest) |
| `AUTH_SESSION_SECRET` | HMAC signing secret for session tokens |
| `AUTH_SESSION_TTL_SECONDS` | Session TTL (default: 604800 = 7 days) |

### 4.4.3 Monitoring

The application includes built-in monitoring capabilities:

- **Streamlit Caching**: Multi-tier cache with configurable TTLs
- **Debug Mode**: Query parameter `?debug=true` enables diagnostic information display
- **Database Diagnostics**: Connection testing and error reporting
- **Print Logging**: Server-side logging for troubleshooting data loading issues

---

## 4.5 Conclusion

The realization phase delivers a fully integrated **Cable Manufacturing AI** platform, with Streamlit providing a responsive multi-page interface, SQL Server ensuring reliable data persistence, and Mistral AI adding intelligent root cause analysis capabilities. The modular architecture — comprising configuration management, real-time monitoring, and analysis/datasheet generation — provides COFICAB with a powerful tool for data-driven quality management in cable manufacturing.

---

# Conclusion Générale

We recapitulate the development of **Cable Manufacturing AI**, a platform designed to unify machine configuration management, real-time parameter monitoring, and AI-driven quality prediction within a single Streamlit application. The project addresses the fragmentation of cable manufacturing quality monitoring by integrating live OPC UA sensor data with machine-learning inference and natural-language root cause analysis through Mistral AI.

Our development approach followed a **Kanban methodology**, enabling iterative task management and flexibility, with major milestones tracked between January and May 2025.

- **Chapter I** introduced the project, analyzed the operational challenges at COFICAB, outlined the proposed solution, presented the host company (COFICAB / ELLOUMI Group), and detailed the technology stack and system architecture.

- **Chapter II** specified functional and non-functional requirements, defined two user profiles (Operator and Analyst), modeled system interactions through use case diagrams, and presented the Kanban task board with bi-weekly snapshots throughout the project lifecycle.

- **Chapter III** focused on system design through UML diagrams — use case diagrams with detailed textual descriptions, class diagrams covering both main entities and the ML/AI backend, sequence diagrams for key workflows (authentication, configuration, monitoring, analysis, root cause analysis), and activity diagrams for critical processes.

- **Chapter IV** covered implementation, UI design, and deployment of the platform. The implementation includes four Streamlit pages (Authentication, Configuration, Real-Time Monitoring, Analysis), 2,300+ lines of database helper code, 13 trained machine-learning models, and Mistral AI integration for intelligent root cause analysis.

**Results** demonstrate a robust, scalable platform capable of:
- Monitoring multiple cable production machines simultaneously in real time
- Detecting out-of-spec parameter behavior with immediate visual alerts
- Computing quality prediction probabilities based on parameter deviation analysis
- Generating comprehensive reference datasheets from historical production runs
- Providing AI-powered root cause analysis with actionable corrective recommendations
- Maintaining full audit trails via run-level tracking and analysis versioning

**Challenges encountered** during development included:
- SQL Server deadlock errors under high query load (resolved with retry logic and exponential backoff)
- Real-time chart performance optimization (resolved with sliding-window caching approach)
- Mistral AI API integration and prompt engineering for manufacturing-specific context
- Streamlit fragment auto-refresh coordination between monitoring data and card rendering

**Future perspectives** involve:
- Expanding the system with additional ML models (deep learning for time-series prediction)
- Implementing automated model retraining pipelines based on new production data
- Adding multi-language support for international deployment
- Integrating real-time alerting (email, SMS, dashboard notifications)
- Extending Mistral AI integration for predictive maintenance recommendations
- Migrating to containerized deployment (Docker/Kubernetes) for improved scalability

We believe that **Cable Manufacturing AI** provides a strong foundation for data-driven quality management in cable production and offers considerable potential for future enhancements. The platform successfully transforms raw OPC UA sensor data into actionable quality insights, directly addressing COFICAB's need for proactive, AI-enhanced manufacturing quality monitoring.

---
