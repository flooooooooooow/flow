def sift_down(xs, start, n):
    root = start
    while True:
        left = root * 2 + 1
        if left >= n:
            return
        cand = root
        if xs[cand] < xs[left]:
            cand = left
        right = left + 1
        if right < n and xs[cand] < xs[right]:
            cand = right
        if cand == root:
            return
        xs[root], xs[cand] = xs[cand], xs[root]
        root = cand


def heap_sort(xs):
    n = len(xs)
    start = n // 2 - 1
    while start >= 0:
        sift_down(xs, start, n)
        start -= 1
    end = n - 1
    while end > 0:
        xs[0], xs[end] = xs[end], xs[0]
        sift_down(xs, 0, end)
        end -= 1


def binary_search(xs, key):
    lo = 0
    hi = len(xs)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        v = xs[mid]
        if v == key:
            return mid
        if v < key:
            lo = mid + 1
        else:
            hi = mid
    return -1


def main():
    n = 4096
    xs = [((i * 1103515245 + 12345) % 100000) for i in range(n)]
    k0 = xs[0]
    k1 = xs[n // 2]
    k2 = xs[n - 1]
    heap_sort(xs)
    checksum = sum(xs)
    if binary_search(xs, k0) < 0:
        raise ValueError("missing k0")
    if binary_search(xs, k1) < 0:
        raise ValueError("missing k1")
    if binary_search(xs, k2) < 0:
        raise ValueError("missing k2")
    for i in range(1, n):
        if xs[i - 1] > xs[i]:
            raise ValueError("not sorted")
    if checksum != 204872320:
        raise ValueError("checksum mismatch: %s" % checksum)
    return 0


if __name__ == "__main__":
    main()
