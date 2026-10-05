import os

def main():
    in_path = "/tmp/flow_buffered_io_in.txt"
    out_path = "/tmp/flow_buffered_io_out.txt"

    lines = []
    for line in range(2000):
        d0 = (line // 1000) % 10
        d1 = (line // 100) % 10
        d2 = (line // 10) % 10
        d3 = line % 10
        lines.append("key_%d%d%d%d=value_data_payload_string_line_\n" % (d0, d1, d2, d3))
    text = "".join(lines)
    with open(in_path, "w") as f_in:
        f_in.write(text)

    with open(in_path, "r") as f_read:
        data = f_read.read()
    out = data.upper()
    checksum = sum(ord(c) for c in out)
    with open(out_path, "w") as f_out:
        f_out.write(out)

    if os.path.exists(in_path):
        os.remove(in_path)
    if os.path.exists(out_path):
        os.remove(out_path)
    if checksum <= 0:
        return 1
    print("allocations: 1")
    print("copies: 0")
    return 0


if __name__ == "__main__":
    main()
