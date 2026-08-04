// Two-goroutine producer/consumer — pair of chan_pingpong.flow
package main

import (
	"fmt"
	"time"
)

const (
	N   = 1_000_000
	BUF = 64
)

func main() {
	// warmup
	run(1000)
	t0 := time.Now()
	run(N)
	ms := float64(time.Since(t0).Microseconds()) / 1000.0
	fmt.Printf("go_chan_pingpong n=%d buf=%d ms=%.3f\n", N, BUF, ms)
}

func run(n int) {
	ch := make(chan int32, BUF)
	done := make(chan struct{})
	go func() {
		for i := 0; i < n; i++ {
			<-ch
		}
		close(done)
	}()
	for i := int32(0); i < int32(n); i++ {
		ch <- i
	}
	<-done
}
