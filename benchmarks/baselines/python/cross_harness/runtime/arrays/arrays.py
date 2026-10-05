def main():
    arr = [0] * 1000
    checksum = 0
    for _ in range(10000):
        for i in range(1000):
            arr[i] = i
            checksum += arr[i]
    if checksum != 4995000000:
        raise ValueError("checksum mismatch")
    return 0


if __name__ == "__main__":
    main()
