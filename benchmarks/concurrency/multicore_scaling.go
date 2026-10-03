package main

import (
	"fmt"
	"math"
	"runtime"
	"sync"
	"time"
)

const N_ELEMENTS = 80000000

func get_time() int64 {
	return time.Now().UnixNano()
}

func prevent_optimize_away_i32(arr []int32) {
	// Prevents optimizer from dead-code eliminating the loop
	volatile_val := arr[N_ELEMENTS-1]
	_ = volatile_val
}

func prevent_optimize_away_f64(arr []float64) {
	// Prevents optimizer from dead-code eliminating the loop
	volatile_val := arr[N_ELEMENTS-1]
	_ = volatile_val
}

func run_fill_benchmark(workers int) {
	arr := make([]int32, N_ELEMENTS)

	t0 := get_time()
	var wg sync.WaitGroup
	chunk := N_ELEMENTS / workers
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func(w int) {
			start := w * chunk
			end := start + chunk
			if end > N_ELEMENTS {
				end = N_ELEMENTS
			}
			for i := start; i < end; i++ {
				arr[i] = int32(i)
			}
			wg.Done()
		}(w)
	}
	wg.Wait()
	t1 := get_time()
	ms_par := float64(t1-t0) / 1000000.0
	prevent_optimize_away_i32(arr)

	t2 := get_time()
	for i := 0; i < N_ELEMENTS; i++ {
		arr[i] = int32(i)
	}
	t3 := get_time()
	ms_single := float64(t3-t2) / 1000000.0
	prevent_optimize_away_i32(arr)

	fmt.Printf("go_multicore_scaling_fill_ms_single %.3f\n", ms_single)
	fmt.Printf("go_multicore_scaling_fill_ms_parallel %.3f\n", ms_par)
}

func run_compute_benchmark(workers int) {
	arr := make([]float64, N_ELEMENTS)

	t0 := get_time()
	var wg sync.WaitGroup
	chunk := N_ELEMENTS / workers
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func(w int) {
			start := w * chunk
			end := start + chunk
			if end > N_ELEMENTS {
				end = N_ELEMENTS
			}
			for i := start; i < end; i++ {
				sum := 0.0
				for j := 0; j < 50; j++ {
					sum += math.Sqrt(float64((i + j) % 100))
				}
				arr[i] = sum
			}
			wg.Done()
		}(w)
	}
	wg.Wait()
	t1 := get_time()
	ms_par := float64(t1-t0) / 1000000.0
	prevent_optimize_away_f64(arr)

	t2 := get_time()
	for i := 0; i < N_ELEMENTS; i++ {
		sum := 0.0
		for j := 0; j < 50; j++ {
			sum += math.Sqrt(float64((i + j) % 100))
		}
		arr[i] = sum
	}
	t3 := get_time()
	ms_single := float64(t3-t2) / 1000000.0
	prevent_optimize_away_f64(arr)

	fmt.Printf("go_multicore_scaling_compute_ms_single %.3f\n", ms_single)
	fmt.Printf("go_multicore_scaling_compute_ms_parallel %.3f\n", ms_par)
}

func run_false_sharing_benchmark(workers int) {
	count_arr := make([]int32, workers)
	padded_arr := make([]int32, workers*16)

	t0 := get_time()
	var wg1 sync.WaitGroup
	for i := 0; i < workers; i++ {
		wg1.Add(1)
		go func(idx int) {
			for c := 0; c < 100000000; c++ {
				count_arr[idx]++
			}
			wg1.Done()
		}(i)
	}
	wg1.Wait()
	t1 := get_time()
	ms_fs := float64(t1-t0) / 1000000.0

	t2 := get_time()
	var wg2 sync.WaitGroup
	for i := 0; i < workers; i++ {
		wg2.Add(1)
		go func(idx int) {
			for c := 0; c < 100000000; c++ {
				padded_arr[idx*16]++
			}
			wg2.Done()
		}(i)
	}
	wg2.Wait()
	t3 := get_time()
	ms_pad := float64(t3-t2) / 1000000.0

	fmt.Printf("go_multicore_scaling_fs_unpadded_ms %.3f\n", ms_fs)
	fmt.Printf("go_multicore_scaling_fs_padded_ms %.3f\n", ms_pad)
}

func main() {
	workers := runtime.GOMAXPROCS(0)

	run_fill_benchmark(workers)
	run_compute_benchmark(workers)
	run_false_sharing_benchmark(workers)
}
