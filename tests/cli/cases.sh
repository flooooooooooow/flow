# Cases for tests/cli/run.sh, sourced by it.
#   t NAME [cwd=root|proj|empty] [env=K=V]... [files=a,b] [stdin=FILE] -- ARGS...
# cwd=proj runs in a fresh copy of tests/cli/fixtures/proj, cwd=empty in a
# fresh empty directory; the default is the repository root.
F=tests/cli/fixtures

# Help, version, unknown commands
t help -- help
t help_noargs --
t help_unknown -- frobnicate
t version -- version
t version_flag -- --version
t version_V -- -V
t host_python_version env=FLOW_HOST=python -- version
t host_bad_version env=FLOW_HOST=weird -- version
t host_auto_version env=FLOW_HOST=auto -- version

# run
t run_hello -- run $F/hello.flow
t run_exit3 -- run $F/exit3.flow
t run_noargs -- run
t run_missing -- run $F/missing.flow
t run_notflow -- run $F/notflow.txt
t run_nomain -- run $F/nomain.flow
t run_bad_syntax -- run $F/bad_syntax.flow
t run_bad_backend -- run --backend=zzz $F/hello.flow
t run_backend_noval -- run $F/hello.flow --backend
t run_unknown_opt -- run --bogus $F/hello.flow
t run_extra_arg -- run $F/hello.flow $F/exit3.flow
t run_show_flags -- run --show-flags $F/hello.flow
t run_host_python env=FLOW_HOST=python -- run $F/hello.flow
t run_cpu_backend_bad env=FLOW_CPU_BACKEND=zzz -- run $F/hello.flow
t run_json -- run $F/hello.flow --json
t run_sanitize_bad -- run --sanitize=bogus $F/hello.flow
t run_mlir -- run --backend=mlir $F/hello.flow
t run_project cwd=proj -- run src/main.flow

# compile / show-flags
t compile_hello files=build/hello.c,build/hello -- compile $F/hello.flow
t compile_noargs -- compile
t compile_bad_syntax -- compile $F/bad_syntax.flow
t compile_show_flags -- compile --show-flags
t compile_profile_safety -- compile --profile=safety --show-flags
t show_flags -- show-flags
t show_flags_safety -- show-flags --profile=safety --sanitize=ub,asan
t show_flags_space -- show-flags --profile safety --sanitize tsan
t show_flags_env env=FLOW_UBSAN=1 env=FLOW_CFLAGS=-DX=1 env=FLOW_OPT_LEVEL=3 -- show-flags
t show_flags_bad_sanitizer -- show-flags --sanitize=bogus
t compile_isolated_root env=FLOW_BUILD_ROOT=build/cli_golden_root files=build/cli_golden_root/hello.c -- compile $F/hello.flow

# fmt
t fmt_noargs -- fmt
t fmt_check_clean -- fmt --check $F/hello.flow
t fmt_check_dirty -- fmt --check $F/badfmt.flow
t fmt_missing -- fmt $F/missing.flow
t fmt_bad_syntax -- fmt --check $F/bad_syntax.flow
t fmt_rewrite cwd=empty -- fmt ../../missing_dir/none.flow

# explain / know / doc
t explain_hello -- explain $F/hello.flow
t explain_noargs -- explain
t know_noargs -- know
t know_help -- know --help
t know_claim -- know Nat/+.zero-right
t doc_noargs -- doc
t doc_proof_missing -- doc proof $F/missing.flow
t doc_proof_noargs -- doc proof
t doc_kernel_noargs -- doc kernel

# analyze / check / lsp / tools
t analyze_noargs -- analyze
t analyze_flow -- analyze $F/hello.flow
t check_file -- check $F/hello.flow
t lsp_bad_stdin -- lsp --version

# mlir / jit / gpu / shader
t mlir_noargs -- mlir
t mlir_missing -- mlir $F/missing.flow
t mlir_hello -- mlir $F/hello.flow
t mlir_bad_opt -- mlir $F/hello.flow --frob
t mlir_gpu_retired -- mlir $F/hello.flow --gpu
t mlir_print_pipeline -- mlir $F/hello.flow --print-pass-pipeline
t mlir_run_noargs -- mlir-run
t jit_noargs -- jit
t jit_hello -- jit $F/hello.flow
t gpu_noargs -- gpu
t gpu_hello -- gpu $F/hello.flow
t shader_noargs -- shader
t shader_bad_opt -- shader $F/hello.flow --frob
t ml_bad -- ml zzz
t fir_noargs -- fir-g
t fir_bad -- fir-g notaflag

# debug / window / gfx / record / audio / dap / patch
t debug_help -- debug --help
t debug_noargs -- debug
t debug_bad_opt -- debug $F/hello.flow --frob
t debug_bad_break -- debug $F/hello.flow --break
t debug_no_launch files=build/hello.debug -- debug $F/hello.flow --no-launch
t window_noargs -- window
t gfx_noargs -- gfx
t gfx_missing -- gfx $F/missing.flow
t record_bad_flag -- record $F/hello.flow --frob
t record_frames_noval -- record $F/hello.flow --frames
t audio_noargs -- audio
t compile_audio_noargs -- compile-audio
t dap_noargs -- dap
t dap_missing -- dap $F/missing.flow
t patch_noargs -- patch

# demos
t demo_noargs -- demo
t demo_unknown -- demo nope
t demo_vulkan_bad -- demo vulkan zzz
t demo_vulkan_flow_bad -- demo vulkan-flow zzz
t transpile_retired -- transpile $F/hello.flow

# test tiers
t test_lang_one -- test-lang tests/lang/test_arithmetic.flow
t test_lang_missing -- test-lang tests/cli/fixtures/none_here
t test_runtime_one -- test-runtime tests/runtime/test_arithmetic.flow
t test_scripts_none -- test-scripts no_such_script_test
t test_project_help cwd=proj -- test --help
t test_project_list cwd=proj -- test --list

# packages and projects
t pkg_noargs -- pkg
t info_noargs -- info
t add_noargs -- add
t init_empty cwd=empty files=flow.toml,src/main.flow -- init
t init_named cwd=empty files=flow.toml,src/main.flow,demo -- init demo
t sync_proj cwd=proj files=flow.lock -- sync
t build_proj cwd=proj -- build
t clean_proj cwd=proj -- clean
t install_proj cwd=proj -- install
t search_local -- search hello
t examples_proj cwd=proj -- examples
t examples_run_proj cwd=proj -- examples run greet
t examples_run_missing cwd=proj -- examples run nope
t examples_run_noname cwd=proj -- examples run

# python / wasm / wasm32 / bpf
t python_noargs -- python
t python_source cwd=empty files=dist,dist/hello_ext.c -- python @ROOT/tests/cli/fixtures/hello.flow --source
t wasm_noargs -- wasm
t wasm_help -- wasm --help
t wasm_fs_mlir -- wasm $F/hello.flow --fs memfs --backend=mlir
t wasm_threads_mlir -- wasm $F/hello.flow --threads --backend mlir
t wasm32_noargs -- wasm32
t bpf_noargs -- bpf
