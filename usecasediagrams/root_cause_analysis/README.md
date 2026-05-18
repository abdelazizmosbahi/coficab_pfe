# Root Cause Analysis — Low-Level Use Case Decomposition

## Scope

This diagram decomposes the **Root Cause Analysis** functional area, powered by Mistral AI. Two entry points (single-parameter anomaly and aggregated quality degradation) share the same AI invocation pipeline, factored out as an `<<include>>` chain. Source: `model_page.py:1606-1687` (fullscreen) + `model_page.py:2301-2349` (dialog) + `db_helpers.py:982-1103`.

## Mapping to General Diagram

| General UC | Title | Sub-Diagram UC |
|---|---|---|
| UC12 | Analyze Root Cause | UCR1 Analyze Parameter Root Cause + UCR2 Analyze Quality Degradation |

*Note: The general diagram's "UC12 Analyze Root Cause" is actually two distinct entry points with different triggers, prompts, models, and views. They share only the Mistral AI invocation (UCR3).*

## Low-Level Use Cases

### UCR3 — Invoke Mistral AI API
*`<<include>>` by UCR1 and UCR2 (mandatory for both)*

| | |
|---|---|
| **Goal** | Send a diagnostic prompt to Mistral AI Chat Completions and retrieve the analysis |
| **Sub-use cases executed in sequence** | UCR6 → UCR7 → UCR8 |
| **Models Used** | `mistral-small-latest` when called from UCR1 (single-parameter), `mistral-large-latest` when called from UCR2 (aggregated degradation) |

### UCR4 — Construct Single-Parameter Prompt
*`<<include>>` by UCR1 (mandatory)*

| | |
|---|---|
| **Goal** | Build a diagnostic prompt focused on a single out-of-range parameter |
| **Implementation** | Hardcoded template at `model_page.py:1633-1678`: includes machine code, parameter name, current value, acceptable range `[min, max]`, deviation type (below min / above max), and deviation magnitude |
| **Example Prompt** | *"Machine [MC]: Parameter [NAME] = [VALUE]. Acceptable range: [MIN]-[MAX]. Current value is [above/below] the acceptable range by [DELTA]. Provide likely root causes, immediate corrective actions, and preventive measures."* |
| **View** | Fullscreen dedicated view (`st.session_state["fullscreen_rca_param"]` set by 🔍 button click) |

### UCR5 — Construct Aggregated Prompt
*`<<include>>` by UCR2 (mandatory)*

| | |
|---|---|
| **Goal** | Build a multi-parameter diagnostic prompt with ALL out-of-range parameters for holistic analysis |
| **Implementation** | Hardcoded template at `model_page.py:2301-2349`: includes machine code, overall quality probability (%), list of ALL out-of-range parameters with current values and spec ranges |
| **Example Prompt** | *"Machine [MC]: Quality probability is [Q]%. The following parameters are out of range: [param1]=[val1] (range [min1]-[max1]), [param2]=[val2] (range [min2]-[max2]), ... Provide likely root causes, corrective actions, and preventive measures."* |
| **View** | Dialog modal (`@st.dialog("🤖 Mistral Root Cause Analysis")`) |

### UCR6 — Read API Key & Init Mistral SDK
*`<<include>>` by UCR3 (mandatory)*

| | |
|---|---|
| **Goal** | Read `MISTRAL_API_KEY` from environment and initialize the Mistral AI client |
| **Implementation** | `api_key = os.getenv("MISTRAL_API_KEY")` → `client = Mistral(api_key=api_key)` (`model_page.py:1634-1668` or `model_page.py:2318-2333` depending on entry point) |
| **Fallback** | If `mistralai` SDK is not installed, falls back to direct HTTP POST to `https://api.mistral.ai/v1/chat/completions` |
| **Error** | If API key is missing → `st.error("Mistral API key not found")` and use case terminates |

### UCR7 — Send Chat Completion Request
*`<<include>>` by UCR3 (mandatory)*

| | |
|---|---|
| **Goal** | Send the constructed prompt to the Mistral AI Chat Completions API |
| **Implementation** | `chat_response = client.chat.complete(model=model, messages=[{"role": "user", "content": prompt}])` |
| **Timeout** | Standard HTTP timeout (no explicit timeout set — uses SDK default) |
| **Error** | API failure → `st.error(f"Mistral API error: {e}")` |

### UCR8 — Parse & Display Response
*`<<include>>` by UCR3 (mandatory)*

| | |
|---|---|
| **Goal** | Extract the AI-generated analysis text and render it in the Streamlit UI |
| **Implementation** | `analysis_text = chat_response.choices[0].message.content` → `st.markdown(analysis_text)` |
| **Format** | The response is markdown-formatted (Mistral returns structured text with sections: Root Cause, Corrective Actions, Preventive Measures) |

## Relationship Justification

| Source | Target | Type | Rationale |
|---|---|---|---|
| UCR1 | UCR3 | `<<include>>` | Single-parameter RCA CANNOT complete without invoking Mistral AI. The entire purpose is to get AI-generated diagnostics. |
| UCR1 | UCR4 | `<<include>>` | The prompt must be constructed before sending — this is a mandatory preparatory step. |
| UCR2 | UCR3 | `<<include>>` | Quality degradation analysis also REQUIRES Mistral AI invocation. Without it, only raw data would be shown (no analysis). |
| UCR2 | UCR5 | `<<include>>` | The aggregated prompt must be constructed before sending — mandatory step. |
| UCR3 | UCR6 | `<<include>>` | API key is required before any API call can be made. Without it, the pipeline stops. |
| UCR3 | UCR7 | `<<include>>` | The API request is the core behavior of UCR3. |
| UCR3 | UCR8 | `<<include>>` | The raw API response must be parsed and displayed to be useful. |

### Why Two `<<include>>` Chains Instead of One?

UCR4 and UCR5 are separate because their prompt structures differ significantly (single-parameter context vs. aggregated multi-parameter context). They are NOT shared behavior — each is exclusive to its entry point. Only UCR3 (the API invocation mechanics) is shared.

### Why No `<<extend>>`?

There is no conditional/optional behavior in this area. Both entry points always construct a prompt and always call Mistral AI. The only variation (model choice) is a parameter passed to UCR7, not a separate behavioral extension.

## Entry Point Comparison

| Aspect | UCR1 — Single Parameter | UCR2 — Quality Degradation |
|---|---|---|
| **Trigger** | 🔍 icon on OUT OF RANGE parameter card | "Analyze Root Cause" button when quality < 50% |
| **Scope** | 1 parameter | All out-of-range parameters |
| **Mistral Model** | `mistral-small-latest` | `mistral-large-latest` |
| **View** | Fullscreen page | Dialog modal |
| **Code Location** | `model_page.py:1606-1687` | `model_page.py:2301-2349` |

## Authentication Prerequisite

All top-level use cases in this diagram `<<include>>` the **Authenticate** use case (UCAUTH) as a mandatory prerequisite. The Analyst must be authenticated before invoking any root cause analysis. Both entry points (UCR1 and UCR2) are triggered from the Realtime page, which requires authentication via `ensure_page_authentication()` in `model_page.py:1680`. Without a valid session, the Analyst cannot access the monitoring dashboard and thus cannot trigger either RCA flow.

### Relationship Detail

| Source | Target | Type | Rationale |
|---|---|---|---|
| UCR1, UCR2 | UCAUTH | `<<include>>` | Both root cause analysis entry points require authentication. They are triggered from the Realtime monitoring page (UC10 → UCM3), which itself requires authentication. The `<<include>>` from UCR1 and UCR2 to Authenticate makes this dependency explicit even in the standalone diagram. |

## Key Implementation Details

| Aspect | Detail |
|---|---|
| **AI Provider** | Mistral AI — Chat Completions API |
| **SDK** | `mistralai` Python package with HTTP fallback |
| **Environment** | `MISTRAL_API_KEY` + `MISTRAL_MODEL` in `.env` |
| **Fullscreen RCA** | `model_page.py:1606-1687` — inline at module scope |
| **Dialog RCA** | `model_page.py:2300-2349` — `@st.dialog` decorator |
| **DB Helpers** | `db_helpers.py:982-1048` (`call_mistral_ai`) and `1050-1103` (`analyze_parameter_anomaly`) |
