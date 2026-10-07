"""Real JSON-document parsing companion to Flow's json_parse benchmark.

The substring scanner is independently measured in cold/json_key_scan.
Both implementations repeat 1,000 full parses of the same fixture.
"""
import json


def main() -> int:
    payload = '{"records": [{"id": 10, "count": 250}, {"id": 20, "count": 350}, {"id": 30, "count": 450}, {"id": 40, "count": 550}]}'
    total = 0
    for _ in range(1000):
        doc = json.loads(payload)
        rows = doc["records"]
        if not isinstance(rows, list):
            return 2
        subtotal = 0
        for row in rows:
            if not isinstance(row, dict):
                return 3
            field = row["count"]
            if type(field) is not int:
                return 4
            subtotal += field
        if len(rows) != 4 or subtotal != 1600:
            return 5
        total += subtotal
    if total != 1600000:
        return 6

    try:
        json.loads('{"records":[')
    except json.JSONDecodeError:
        pass
    else:
        return 7
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
