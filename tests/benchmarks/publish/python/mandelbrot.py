# Mandelbrot set membership count on a 400x400 grid, 100 max iterations.
# Same algorithm and size as mandelbrot.flow. Plain CPython.
import time

W = 400
H = 400
MAXI = 100


def mandel_count():
    count = 0
    for py in range(H):
        cy = 2.5 * py / H - 1.25
        for px in range(W):
            cx = 2.5 * px / W - 2.0
            zx = 0.0
            zy = 0.0
            it = 0
            while zx * zx + zy * zy <= 4.0 and it < MAXI:
                tmp = zx * zx - zy * zy + cx
                zy = 2.0 * zx * zy + cy
                zx = tmp
                it = it + 1
            if it == MAXI:
                count = count + 1
    return count


def main():
    t0 = time.perf_counter()
    count = mandel_count()
    secs = time.perf_counter() - t0
    print("result %d" % count)
    print("seconds %.9f" % secs)


if __name__ == "__main__":
    main()
