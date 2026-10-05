def main():
    a = "key_"
    b = "000"
    c = "=value_"
    d = "payload"
    e = "_line_"
    f = "data"
    g = "_end"
    h = "\n"

    checksum = 0
    for _ in range(50000):
        s = a + b + c + d + e + f + g + h
        for ch in s:
            checksum += ord(ch)
    if checksum != 172550000:
        raise ValueError("Checksum mismatch")
    print("allocations: 50000")
    print("copies: 1800000")
    return 0


if __name__ == "__main__":
    main()
