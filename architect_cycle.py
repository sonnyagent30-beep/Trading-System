import json

with open('/root/workspace/forex/journal/manager_reports/2026-06-09.jsonl') as f:
    lines = f.readlines()

print(f"Total records: {len(lines)}")
for line in lines:
    r = json.loads(line)
    if r['type'] not in ('MANAGER_START',):
        print(json.dumps(r, indent=2))
