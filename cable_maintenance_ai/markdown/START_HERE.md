# Start Here

This is the shortest path to running the current system.

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Configure `.env`

At minimum, set the MySQL connection used by the Streamlit pages:

```env
DB_HOST=...
DB_PORT=3306
DB_USER=...
DB_PASSWORD=...
DB_NAME=...
```

Optional but recommended:

```env
MISTRAL_API_KEY=...
MISTRAL_MODEL=mistral-small-latest
OPC_SERVER_URL=opc.tcp://0.0.0.0:4840/freeopcua/server/
OPC_NAMESPACE_URI=http://examples.freeopcua.github.io
```

## 3. Start the app

```bash
cd app
streamlit run app.py
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## 4. Optional: verify OPC UA connectivity

If you use the OPC UA pages, make sure your OPC UA server is running and reachable.

## What to use first

- For live monitoring: open the OPC UA Real-Time page
- For parameter health checks: open the OPC UA Parameter Testing page
- For historical traceability: open the Parameter Traceability page
- For offline prediction workflows: use the Prediction or Manual Prediction pages

## If models are missing

Run the notebook workflow described in `QUICK_START_NOTEBOOK.md`.

## Canonical docs

- `README.md`
- `MANIFEST.md`
- `PROJECT_SUMMARY.md`
- `SYSTEM_ARCHITECTURE.md`
- `OPC_UA_QUICK_START.md`
- `docs/OPCUA_PARAMETER_TESTING_GUIDE.md`
- `QUICK_START_NOTEBOOK.md`
