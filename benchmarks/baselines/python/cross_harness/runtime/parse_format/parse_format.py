def main():
    text = "10,20,30,40,50,60,70,80,90,100,250,350,450,550,999,-1,-42,0,7,2147483647"
    checksum = 0
    for _ in range(20000):
        pos = 0
        n = len(text)
        while pos < n:
            end = pos
            while end < n and text[end] != ",":
                end += 1
            token = text[pos:end]
            value = int(token)
            checksum += value
            checksum += len(str(value))
            pos = end + 1 if end < n and text[end] == "," else end
    if checksum != 42949736260000:
        raise ValueError("Checksum mismatch: %s" % checksum)
    return 0


if __name__ == "__main__":
    main()
