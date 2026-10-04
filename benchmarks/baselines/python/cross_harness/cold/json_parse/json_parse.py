def parse_nth_int_after_key(json_str: str, key: str, target_occ: int) -> int:
    occ = 0
    idx = 0
    key_len = len(key)
    while True:
        pos = json_str.find(key, idx)
        if pos == -1:
            return 0
        occ += 1
        if occ == target_occ:
            j = pos + key_len
            while j < len(json_str) and not json_str[j].isdigit():
                j += 1
            val = 0
            while j < len(json_str) and json_str[j].isdigit():
                val = val * 10 + int(json_str[j])
                j += 1
            return val
        idx = pos + 1

def main():
    json_data = "{\"records\": [{\"id\": 10, \"count\": 250}, {\"id\": 20, \"count\": 350}, {\"id\": 30, \"count\": 450}, {\"id\": 40, \"count\": 550}]}"
    key = "\"count\":"

    total_count = 0
    for _ in range(10000):
        c1 = parse_nth_int_after_key(json_data, key, 1)
        c2 = parse_nth_int_after_key(json_data, key, 2)
        c3 = parse_nth_int_after_key(json_data, key, 3)
        c4 = parse_nth_int_after_key(json_data, key, 4)
        total_count += c1 + c2 + c3 + c4

    if total_count != 16000000:
        raise ValueError("Sum mismatch")
    return 0

if __name__ == "__main__":
    main()
