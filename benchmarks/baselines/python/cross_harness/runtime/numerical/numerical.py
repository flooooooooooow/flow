def main():
    n = 4096
    xs = [i * 17 + 3 for i in range(n)]
    total = 0
    sumsq = 0
    mn = xs[0]
    mx = xs[0]
    for v in xs:
        total += v
        sumsq += v * v
        if v < mn:
            mn = v
        if v > mx:
            mx = v
    if total != 142583808:
        raise ValueError("sum mismatch")
    if mn != 3 or mx != 69618:
        raise ValueError("min/max mismatch")
    if sumsq != 6618407614464:
        raise ValueError("sumsq mismatch")
    return 0


if __name__ == "__main__":
    main()
