// Single-threaded buffered channel throughput — pair of channel_throughput.flow
package main

import (
	"fmt"
	"time"
)

const (
	N   = 200_000
	BUF = 200_000
)

func main() {
	ch := make(chan int32, BUF)
	t0 := time.Now()
	for i := int32(0); i < N; i++ {
		ch <- i
	}
	var sum int64
	for i := 0; i < N; i++ {
		sum += int64(<-ch)
	}
	ms := float64(time.Since(t0).Microseconds()) / 1000.0
	expect := int64(N-1) * int64(N) / 2
	fmt.Printf("go_channel_throughput n=%d buf=%d ms=%.3f checksum=%d expect=%d\n",
		N, BUF, ms, sum, expect)
	if sum != expect {
		panic("checksum mismatch")
	}
}
