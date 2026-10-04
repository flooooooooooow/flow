import os

def main():
    in_path = "/tmp/flow_file_transform_in.txt"
    out_path = "/tmp/flow_file_transform_out.txt"

    with open(in_path, "w") as f_in:
        for line in range(200):
            d1 = (line // 100) % 10
            d2 = (line // 10) % 10
            d3 = line % 10
            f_in.write(f"key_{d1}{d2}{d3}=value_data_payload_string_line_\n")

    total_bytes = 0
    with open(in_path, "r") as f_read, open(out_path, "w") as f_out:
        for line in f_read:
            transformed = line.upper()
            f_out.write(transformed)
            total_bytes += len(transformed)

    if os.path.exists(in_path):
        os.remove(in_path)
    if os.path.exists(out_path):
        os.remove(out_path)

    if total_bytes <= 0:
        return 1
    return 0

if __name__ == "__main__":
    main()
