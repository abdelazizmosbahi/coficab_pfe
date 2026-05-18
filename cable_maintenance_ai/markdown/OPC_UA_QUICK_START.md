# OPC UA Quick Start

This guide covers connecting the app to a live OPC UA server.

## Prerequisites

- Python dependencies installed from `requirements.txt`
- Valid MySQL connection in `.env`
- Optional Mistral configuration if you want AI explanations in the app

## Required `.env` values

```env
DB_HOST=...
DB_PORT=3306
DB_USER=...
DB_PASSWORD=...
DB_NAME=...

OPC_SERVER_URL=opc.tcp://0.0.0.0:4840/freeopcua/server/
OPC_NAMESPACE_URI=http://examples.freeopcua.github.io
```

## Start the OPC UA server

Ensure your OPC UA server is running and reachable from the machine running Streamlit.

## Start the Streamlit app

```bash
cd app
streamlit run app.py
```

## Recommended pages

- `OPC UA Real-Time Production Monitoring - Live Demo`
- `OPC UA Parameter Testing & Model Validation`
- `Parameter Traceability`

## Expected behavior

- OPC UA pages can read live values from the OPC UA server
- recipe reference data comes from MySQL
- traceability remains available from historical MySQL data

## Troubleshooting

### Streamlit page cannot connect to OPC UA

- verify `OPC_SERVER_URL`
- ensure the OPC UA server is running
- confirm local firewall rules allow the endpoint port

### Data appears missing in traceability

- verify the selected run exists in `MachineTagValue`
- verify the `OpcNodeId` in `recipe_parameters` matches the trace rows

## Notes

- Older documentation that referenced `data/opc_test/MachineTagValue.csv` is obsolete.
