package main

import (
	"fmt"
	"io"
	"net"
	"net/http"
	"time"
)

func main() {
	ln, err := net.Listen("tcp", "127.0.0.1:18766")
	if err != nil {
		panic(err)
	}
	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Length", "2")
		w.Write([]byte("OK"))
	})
	srv := &http.Server{Handler: mux}
	go srv.Serve(ln)

	// warmup
	for i := 0; i < 20; i++ {
		resp, err := http.Get("http://127.0.0.1:18766/")
		if err == nil {
			io.Copy(io.Discard, resp.Body)
			resp.Body.Close()
		}
	}

	const n = 2000
	t0 := time.Now()
	ok := 0
	for i := 0; i < n; i++ {
		resp, err := http.Get("http://127.0.0.1:18766/")
		if err == nil {
			io.Copy(io.Discard, resp.Body)
			resp.Body.Close()
			ok++
		}
	}
	sec := time.Since(t0).Seconds()
	rps := float64(ok) / sec
	fmt.Printf("go_http_server n=%d ok=%d rps=%.1f\n", n, ok, rps)
	srv.Close()
}
