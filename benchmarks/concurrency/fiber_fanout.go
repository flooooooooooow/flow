package main

import (
	"fmt"
	"runtime"
	"sync"
	"time"
)

const (
	N      = 50_000_000
	FIBERS = 256
)

func main() {
	partials := make([]int64, FIBERS)
	chunk := (N + FIBERS - 1) / FIBERS
	t0 := time.Now()
	var wg sync.WaitGroup
	for i := 0; i < FIBERS; i++ {
		s := i * chunk
		e := s + chunk
		if s >= N {
			break
		}
		if e > N {
			e = N
		}
		wg.Add(1)
		go func(idx, start, end int) {
			defer wg.Done()
			var sum int64
			for j := start; j < end; j++ {
				sum += int64(j)
			}
			partials[idx] = sum
		}(i, s, e)
	}
	wg.Wait()
	var total int64
	for _, p := range partials {
		total += p
	}
	ms := float64(time.Since(t0).Microseconds()) / 1000.0
	want := int64(N-1) * int64(N) / 2
	fmt.Printf("go_fiber_fanout n=%d fibers=%d maxprocs=%d ms=%.3f checksum=%d want=%d\n",
		N, FIBERS, runtime.GOMAXPROCS(0), ms, total, want)
	if total != want {
		panic("checksum")
	}
}
