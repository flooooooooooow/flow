# Naive recursive Fibonacci. Same algorithm and size as fib.flow.
import time


def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def main():
    t0 = time.perf_counter()
    result = fib(35)
    secs = time.perf_counter() - t0
    print("result %d" % result)
    print("seconds %.9f" % secs)


if __name__ == "__main__":
    main()
