// Chunked parallel fill + serial checksum — pair of parallel_sum.flow
package main

import (
	"fmt"
	"runtime"
	"sync"
	"time"
)

const N = 8_000_000

func main() {
	arr := make([]int32, N)
	workers := runtime.NumCPU()
	t0 := time.Now()
	var wg sync.WaitGroup
	chunk := (N + workers - 1) / workers
	for w := 0; w < workers; w++ {
		start := w * chunk
		end := start + chunk
		if start >= N {
			break
		}
		if end > N {
			end = N
		}
		wg.Add(1)
		go func(s, e int) {
			defer wg.Done()
			for i := s; i < e; i++ {
				arr[i] = int32(i)
			}
		}(start, end)
	}
	wg.Wait()
	var total int64
	for i := 0; i < N; i++ {
		total += int64(arr[i])
	}
	ms := float64(time.Since(t0).Microseconds()) / 1000.0
	expect := int64(N-1) * int64(N) / 2
	fmt.Printf("go_parallel_sum n=%d ms=%.3f checksum=%d expect=%d workers=%d\n",
		N, ms, total, expect, workers)
	if total != expect {
		panic("checksum mismatch")
	}
}
