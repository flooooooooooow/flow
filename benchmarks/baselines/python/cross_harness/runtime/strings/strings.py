def main():
    source = "The Quick Brown Fox Jumps Over The Lazy Dog 1234567890!"
    length = len(source)
    checksum = 0
    for _ in range(100000):
        chars = []
        for i in range(length):
            c = source[i]
            code = ord(c)
            if 97 <= code <= 122:
                code -= 32
                c = chr(code)
            chars.append(c)
            checksum += code
        _buf = "".join(chars)
    if checksum % 256 != 96:
        raise ValueError("Checksum mismatch")
    return 0

if __name__ == "__main__":
    main()
