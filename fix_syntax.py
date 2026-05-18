import re

path = 'cable_maintenance_ai/app/db_helpers.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix missing commas in return statements
# Pattern: {"active": False "status": -> {"active": False, "status":
content = re.sub(r'\{"active": (False|True)\s+"status":', r'{"active": \1, "status":', content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed missing commas in return statements')
