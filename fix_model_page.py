#!/usr/bin/env python
"""Fix the model_page.py datasheet display logic"""

with open('cable_maintenance_ai/app/pages/model_page.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Replace lines 1191:1216 (0-indexed)
new_section = [
    "    # ── Display datasheet from analysis results ─────\n",
    "    st.markdown('<p class=\"cofi-section-title\">📋 Analysed Configuration Datasheet</p>', unsafe_allow_html=True)\n",
    "    \n",
    "    if not analysis_results:\n",
    "        st.info(\"ℹ️ No analysis results yet. Run the analysis first to see parameter statistics.\")\n",
    "    elif not datasheet_table.empty:\n",
    "        st.caption(\"Reference ranges from analysis for this configuration (parameter, min/mean/max values, analysis date).\")\n",
    "        st.dataframe(datasheet_table, use_container_width=True, hide_index=True)\n",
    "        with st.expander(\"📊 Download datasheet\", expanded=False):\n",
    "            csv = datasheet_table.to_csv(index=False)\n",
    "            st.download_button(\n",
    "                label=\"Download CSV\",\n",
    "                data=csv,\n",
    "                file_name=f\"analysis_datasheet_{mc}_config{cid}.csv\",\n",
    "                mime=\"text/csv\",\n",
    "            )\n",
    "    else:\n",
    "        st.warning(\"⚠️ No datasheet rows for this configuration's parameters. Please refresh the page.\")\n",
    "\n",
]

# Replace lines 1191:1216 (0-indexed)
new_lines = lines[:1191] + new_section + lines[1216:]

with open('cable_maintenance_ai/app/pages/model_page.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ File updated successfully!")
print("Replaced lines 1192-1216 with new datasheet display logic")
