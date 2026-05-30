import json

with open('agent_rlm', 'r') as f:
    data = json.load(f)

with open('agent_utils.py', 'w') as f:
    for cell in data.get('cells', []):
        if cell.get('cell_type') == 'code':
            source = cell.get('source', [])
            if isinstance(source, list):
                source = "".join(source)
            f.write(source + "\n\n")
