module attributes {llvm.data_layout = "e-m:e-p:32:32-i64:64-n32:64-S128", llvm.target_triple = "wasm32-unknown-emscripten"} {
func.func private @memcpy(!llvm.ptr, !llvm.ptr, i32) -> !llvm.ptr
func.func private @free(!llvm.ptr) -> ()
func.func private @malloc(i32) -> !llvm.ptr
func.func private @memset(!llvm.ptr, i32, i32) -> !llvm.ptr
func.func private @strlen(!llvm.ptr) -> i32
func.func private @getenv(!llvm.ptr) -> !llvm.ptr
func.func private @atexit(!llvm.ptr) -> i32
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal @flow_mem_profile_on() {addr_space = 0 : i32} : i32 {
%z = llvm.mlir.constant(0 : i32) : i32
llvm.return %z : i32
}
llvm.mlir.global internal @flow_mem_inited() {addr_space = 0 : i32} : i32 {
%z = llvm.mlir.constant(0 : i32) : i32
llvm.return %z : i32
}
llvm.mlir.global internal @flow_mem_alloc_count() {addr_space = 0 : i32} : i64 {
%z = llvm.mlir.constant(0 : i64) : i64
llvm.return %z : i64
}
llvm.mlir.global internal @flow_mem_alloc_bytes() {addr_space = 0 : i32} : i64 {
%z = llvm.mlir.constant(0 : i64) : i64
llvm.return %z : i64
}
llvm.mlir.global internal @flow_mem_temp_bytes() {addr_space = 0 : i32} : i64 {
%z = llvm.mlir.constant(0 : i64) : i64
llvm.return %z : i64
}
llvm.mlir.global internal @flow_mem_copy_bytes() {addr_space = 0 : i32} : i64 {
%z = llvm.mlir.constant(0 : i64) : i64
llvm.return %z : i64
}
llvm.mlir.global internal @flow_mem_stack_bytes() {addr_space = 0 : i32} : i64 {
%z = llvm.mlir.constant(0 : i64) : i64
llvm.return %z : i64
}
llvm.mlir.global internal @flow_mem_arena_bytes() {addr_space = 0 : i32} : i64 {
%z = llvm.mlir.constant(0 : i64) : i64
llvm.return %z : i64
}
llvm.mlir.global internal @flow_mem_live_bytes() {addr_space = 0 : i32} : i64 {
%z = llvm.mlir.constant(0 : i64) : i64
llvm.return %z : i64
}
llvm.mlir.global internal @flow_mem_peak_live() {addr_space = 0 : i32} : i64 {
%z = llvm.mlir.constant(0 : i64) : i64
llvm.return %z : i64
}
llvm.mlir.global internal @flow_mem_site_concat() {addr_space = 0 : i32} : i64 {
%z = llvm.mlir.constant(0 : i64) : i64
llvm.return %z : i64
}
llvm.mlir.global internal @flow_mem_map_overflow() {addr_space = 0 : i32} : i64 {
%z = llvm.mlir.constant(0 : i64) : i64
llvm.return %z : i64
}
llvm.mlir.global internal @flow_mem_ptrs() {addr_space = 0 : i32} : !llvm.array<256 x ptr> {
%z = llvm.mlir.zero : !llvm.array<256 x ptr>
llvm.return %z : !llvm.array<256 x ptr>
}
llvm.mlir.global internal @flow_mem_sz() {addr_space = 0 : i32} : !llvm.array<256 x i64> {
%z = llvm.mlir.zero : !llvm.array<256 x i64>
llvm.return %z : !llvm.array<256 x i64>
}
func.func private @flow_mem_profile_init() {
%ip = llvm.mlir.addressof @flow_mem_inited : !llvm.ptr
%iv = llvm.load %ip : !llvm.ptr -> i32
%z32 = arith.constant 0 : i32
%done = arith.cmpi ne, %iv, %z32 : i32
scf.if %done {
scf.yield
} else {
%one32 = arith.constant 1 : i32
llvm.store %one32, %ip : i32, !llvm.ptr
%name = llvm.mlir.addressof @str_0 : !llvm.ptr
%e = func.call @getenv(%name) : (!llvm.ptr) -> !llvm.ptr
%null = llvm.mlir.zero : !llvm.ptr
%ok = llvm.icmp "ne" %e, %null : !llvm.ptr
%on = scf.if %ok -> (i32) {
%b = llvm.load %e : !llvm.ptr -> i8
%z8 = arith.constant 0 : i8
%nz = arith.cmpi ne, %b, %z8 : i8
%c48 = arith.constant 48 : i8
%is0 = arith.cmpi eq, %b, %c48 : i8
%e1 = llvm.getelementptr %e[1] : (!llvm.ptr) -> !llvm.ptr, i8
%b1 = llvm.load %e1 : !llvm.ptr -> i8
%term = arith.cmpi eq, %b1, %z8 : i8
%zeroish = arith.andi %is0, %term : i1
%keep = arith.andi %nz, %zeroish : i1
%not0 = arith.xori %keep, %nz : i1
%sel = arith.select %not0, %one32, %z32 : i32
scf.yield %sel : i32
} else {
scf.yield %z32 : i32
}
%op = llvm.mlir.addressof @flow_mem_profile_on : !llvm.ptr
llvm.store %on, %op : i32, !llvm.ptr
%onb = arith.cmpi ne, %on, %z32 : i32
scf.if %onb {
%rf = func.constant @flow_mem_report : () -> ()
%rp = builtin.unrealized_conversion_cast %rf : () -> () to !llvm.ptr
%ar = func.call @atexit(%rp) : (!llvm.ptr) -> i32
scf.yield
}
scf.yield
}
func.return
}
func.func private @flow_mem_note_alloc(%n: i64) {
func.call @flow_mem_profile_init() : () -> ()
%op = llvm.mlir.addressof @flow_mem_profile_on : !llvm.ptr
%on = llvm.load %op : !llvm.ptr -> i32
%z32 = arith.constant 0 : i32
%yes = arith.cmpi ne, %on, %z32 : i32
scf.if %yes {
%one = arith.constant 1 : i64
%cp = llvm.mlir.addressof @flow_mem_alloc_count : !llvm.ptr
%cv = llvm.load %cp : !llvm.ptr -> i64
%cn = arith.addi %cv, %one : i64
llvm.store %cn, %cp : i64, !llvm.ptr
%bp = llvm.mlir.addressof @flow_mem_alloc_bytes : !llvm.ptr
%bv = llvm.load %bp : !llvm.ptr -> i64
%bn = arith.addi %bv, %n : i64
llvm.store %bn, %bp : i64, !llvm.ptr
%lp = llvm.mlir.addressof @flow_mem_live_bytes : !llvm.ptr
%lv = llvm.load %lp : !llvm.ptr -> i64
%ln = arith.addi %lv, %n : i64
llvm.store %ln, %lp : i64, !llvm.ptr
%pp = llvm.mlir.addressof @flow_mem_peak_live : !llvm.ptr
%pv = llvm.load %pp : !llvm.ptr -> i64
%gt = arith.cmpi sgt, %ln, %pv : i64
%np = arith.select %gt, %ln, %pv : i64
llvm.store %np, %pp : i64, !llvm.ptr
scf.yield
}
func.return
}
func.func private @flow_mem_note_copy(%n: i64) {
func.call @flow_mem_profile_init() : () -> ()
%op = llvm.mlir.addressof @flow_mem_profile_on : !llvm.ptr
%on = llvm.load %op : !llvm.ptr -> i32
%z32 = arith.constant 0 : i32
%yes = arith.cmpi ne, %on, %z32 : i32
scf.if %yes {
%bp = llvm.mlir.addressof @flow_mem_copy_bytes : !llvm.ptr
%bv = llvm.load %bp : !llvm.ptr -> i64
%bn = arith.addi %bv, %n : i64
llvm.store %bn, %bp : i64, !llvm.ptr
scf.yield
}
func.return
}
func.func private @flow_mem_note_temp(%n: i64) {
func.call @flow_mem_profile_init() : () -> ()
%op = llvm.mlir.addressof @flow_mem_profile_on : !llvm.ptr
%on = llvm.load %op : !llvm.ptr -> i32
%z32 = arith.constant 0 : i32
%yes = arith.cmpi ne, %on, %z32 : i32
scf.if %yes {
%bp = llvm.mlir.addressof @flow_mem_temp_bytes : !llvm.ptr
%bv = llvm.load %bp : !llvm.ptr -> i64
%bn = arith.addi %bv, %n : i64
llvm.store %bn, %bp : i64, !llvm.ptr
%sp = llvm.mlir.addressof @flow_mem_site_concat : !llvm.ptr
%sv = llvm.load %sp : !llvm.ptr -> i64
%sn = arith.addi %sv, %n : i64
llvm.store %sn, %sp : i64, !llvm.ptr
scf.yield
}
func.return
}
func.func private @flow_mem_note_stack(%n: i32) {
func.call @flow_mem_profile_init() : () -> ()
%op = llvm.mlir.addressof @flow_mem_profile_on : !llvm.ptr
%on = llvm.load %op : !llvm.ptr -> i32
%z32 = arith.constant 0 : i32
%yes = arith.cmpi ne, %on, %z32 : i32
scf.if %yes {
%bp = llvm.mlir.addressof @flow_mem_stack_bytes : !llvm.ptr
%bv = llvm.load %bp : !llvm.ptr -> i64
%nw = arith.extsi %n : i32 to i64
%bn = arith.addi %bv, %nw : i64
llvm.store %bn, %bp : i64, !llvm.ptr
scf.yield
}
func.return
}
func.func private @flow_mem_note_arena(%n: i32) {
func.call @flow_mem_profile_init() : () -> ()
%op = llvm.mlir.addressof @flow_mem_profile_on : !llvm.ptr
%on = llvm.load %op : !llvm.ptr -> i32
%z32 = arith.constant 0 : i32
%yes = arith.cmpi ne, %on, %z32 : i32
scf.if %yes {
%nw = arith.extsi %n : i32 to i64
%bp = llvm.mlir.addressof @flow_mem_arena_bytes : !llvm.ptr
%bv = llvm.load %bp : !llvm.ptr -> i64
%bn = arith.addi %bv, %nw : i64
llvm.store %bn, %bp : i64, !llvm.ptr
scf.yield
}
func.return
}
func.func @flow_mem_malloc(%n: i32) -> !llvm.ptr {
%p = func.call @malloc(%n) : (i32) -> !llvm.ptr
%nw = arith.extsi %n : i32 to i64
func.call @flow_mem_note_alloc(%nw) : (i64) -> ()
func.return %p : !llvm.ptr
}
func.func private @calloc(i32, i32) -> !llvm.ptr
func.func private @realloc(!llvm.ptr, i32) -> !llvm.ptr
func.func @flow_mem_calloc(%c: i32, %s: i32) -> !llvm.ptr {
%p = func.call @calloc(%c, %s) : (i32, i32) -> !llvm.ptr
%n = arith.muli %c, %s : i32
%nw = arith.extsi %n : i32 to i64
func.call @flow_mem_note_alloc(%nw) : (i64) -> ()
func.return %p : !llvm.ptr
}
func.func @flow_mem_realloc(%p: !llvm.ptr, %n: i32) -> !llvm.ptr {
%q = func.call @realloc(%p, %n) : (!llvm.ptr, i32) -> !llvm.ptr
%nw = arith.extsi %n : i32 to i64
func.call @flow_mem_note_alloc(%nw) : (i64) -> ()
func.return %q : !llvm.ptr
}
func.func @flow_mem_free(%p: !llvm.ptr) {
func.call @free(%p) : (!llvm.ptr) -> ()
func.return
}
func.func @flow_mem_memcpy(%d: !llvm.ptr, %s: !llvm.ptr, %n: i32) -> !llvm.ptr {
%nw = arith.extsi %n : i32 to i64
func.call @flow_mem_note_copy(%nw) : (i64) -> ()
%r = func.call @memcpy(%d, %s, %n) : (!llvm.ptr, !llvm.ptr, i32) -> !llvm.ptr
func.return %r : !llvm.ptr
}
func.func @flow_mem_report() {
%op = llvm.mlir.addressof @flow_mem_profile_on : !llvm.ptr
%on = llvm.load %op : !llvm.ptr -> i32
%z32 = arith.constant 0 : i32
%yes = arith.cmpi ne, %on, %z32 : i32
scf.if %yes {
%hdr = llvm.mlir.addressof @str_1 : !llvm.ptr
%h = llvm.call @printf(%hdr) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%g_flow_mem_alloc_count = llvm.mlir.addressof @flow_mem_alloc_count : !llvm.ptr
%v_flow_mem_alloc_count = llvm.load %g_flow_mem_alloc_count : !llvm.ptr -> i64
%f_flow_mem_alloc_count = llvm.mlir.addressof @str_2 : !llvm.ptr
%w_flow_mem_alloc_count = llvm.call @printf(%f_flow_mem_alloc_count, %v_flow_mem_alloc_count) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_alloc_bytes = llvm.mlir.addressof @flow_mem_alloc_bytes : !llvm.ptr
%v_flow_mem_alloc_bytes = llvm.load %g_flow_mem_alloc_bytes : !llvm.ptr -> i64
%f_flow_mem_alloc_bytes = llvm.mlir.addressof @str_3 : !llvm.ptr
%w_flow_mem_alloc_bytes = llvm.call @printf(%f_flow_mem_alloc_bytes, %v_flow_mem_alloc_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_peak_live = llvm.mlir.addressof @flow_mem_peak_live : !llvm.ptr
%v_flow_mem_peak_live = llvm.load %g_flow_mem_peak_live : !llvm.ptr -> i64
%f_flow_mem_peak_live = llvm.mlir.addressof @str_4 : !llvm.ptr
%w_flow_mem_peak_live = llvm.call @printf(%f_flow_mem_peak_live, %v_flow_mem_peak_live) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_temp_bytes = llvm.mlir.addressof @flow_mem_temp_bytes : !llvm.ptr
%v_flow_mem_temp_bytes = llvm.load %g_flow_mem_temp_bytes : !llvm.ptr -> i64
%f_flow_mem_temp_bytes = llvm.mlir.addressof @str_5 : !llvm.ptr
%w_flow_mem_temp_bytes = llvm.call @printf(%f_flow_mem_temp_bytes, %v_flow_mem_temp_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_copy_bytes = llvm.mlir.addressof @flow_mem_copy_bytes : !llvm.ptr
%v_flow_mem_copy_bytes = llvm.load %g_flow_mem_copy_bytes : !llvm.ptr -> i64
%f_flow_mem_copy_bytes = llvm.mlir.addressof @str_6 : !llvm.ptr
%w_flow_mem_copy_bytes = llvm.call @printf(%f_flow_mem_copy_bytes, %v_flow_mem_copy_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_stack_bytes = llvm.mlir.addressof @flow_mem_stack_bytes : !llvm.ptr
%v_flow_mem_stack_bytes = llvm.load %g_flow_mem_stack_bytes : !llvm.ptr -> i64
%f_flow_mem_stack_bytes = llvm.mlir.addressof @str_7 : !llvm.ptr
%w_flow_mem_stack_bytes = llvm.call @printf(%f_flow_mem_stack_bytes, %v_flow_mem_stack_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_arena_bytes = llvm.mlir.addressof @flow_mem_arena_bytes : !llvm.ptr
%v_flow_mem_arena_bytes = llvm.load %g_flow_mem_arena_bytes : !llvm.ptr -> i64
%f_flow_mem_arena_bytes = llvm.mlir.addressof @str_8 : !llvm.ptr
%w_flow_mem_arena_bytes = llvm.call @printf(%f_flow_mem_arena_bytes, %v_flow_mem_arena_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%sp = llvm.mlir.addressof @flow_mem_stack_bytes : !llvm.ptr
%sv = llvm.load %sp : !llvm.ptr -> i64
%ap = llvm.mlir.addressof @flow_mem_arena_bytes : !llvm.ptr
%av = llvm.load %ap : !llvm.ptr -> i64
%promo = arith.addi %sv, %av : i64
%pf = llvm.mlir.addressof @str_9 : !llvm.ptr
%ph = llvm.call @printf(%pf, %promo) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_map_overflow = llvm.mlir.addressof @flow_mem_map_overflow : !llvm.ptr
%v_flow_mem_map_overflow = llvm.load %g_flow_mem_map_overflow : !llvm.ptr -> i64
%f_flow_mem_map_overflow = llvm.mlir.addressof @str_10 : !llvm.ptr
%w_flow_mem_map_overflow = llvm.call @printf(%f_flow_mem_map_overflow, %v_flow_mem_map_overflow) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_site_concat = llvm.mlir.addressof @flow_mem_site_concat : !llvm.ptr
%v_flow_mem_site_concat = llvm.load %g_flow_mem_site_concat : !llvm.ptr -> i64
%f_flow_mem_site_concat = llvm.mlir.addressof @str_11 : !llvm.ptr
%w_flow_mem_site_concat = llvm.call @printf(%f_flow_mem_site_concat, %v_flow_mem_site_concat) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
scf.yield
}
func.return
}
llvm.mlir.global internal constant @str_0("FLOW_MEM_PROFILE\00") {addr_space = 0 : i32} : !llvm.array<17 x i8>
llvm.mlir.global internal constant @str_1("\0A=== Flow memory profile (#740) ===\0A\00") {addr_space = 0 : i32} : !llvm.array<37 x i8>
llvm.mlir.global internal constant @str_2("allocations: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<19 x i8>
llvm.mlir.global internal constant @str_3("heap_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<18 x i8>
llvm.mlir.global internal constant @str_4("peak_live_heap: %lld\0A\00") {addr_space = 0 : i32} : !llvm.array<22 x i8>
llvm.mlir.global internal constant @str_5("temp_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<18 x i8>
llvm.mlir.global internal constant @str_6("copies: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<14 x i8>
llvm.mlir.global internal constant @str_7("stack_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<19 x i8>
llvm.mlir.global internal constant @str_8("arena_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<19 x i8>
llvm.mlir.global internal constant @str_9("promotion_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<23 x i8>
llvm.mlir.global internal constant @str_10("live_map_overflow: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<25 x i8>
llvm.mlir.global internal constant @str_11("site_concat: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<19 x i8>
llvm.mlir.global internal constant @str_12("hello\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
func.func private @lambda_1(%env: !llvm.ptr, %arg0: i32) -> i32 {
%v1 = llvm.getelementptr %env[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32)>
%v2 = llvm.load %v1 : !llvm.ptr -> i32
%v3 = llvm.load %v1 : !llvm.ptr -> i32
%v4 = arith.addi %arg0, %v3 : i32
func.return %v4 : i32
}
// Struct: Point
// Fields:
//   x: i32
//   y: i32
func.func @mid(%arg0: !llvm.struct<(i32, i32)>, %arg1: !llvm.struct<(i32, i32)>) -> !llvm.struct<(i32, i32)> {
%v5 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v6 = llvm.extractvalue %arg0[0] : !llvm.struct<(i32, i32)>
%v7 = llvm.insertvalue %v6, %v5[0] : !llvm.struct<(i32, i32)>
%v8 = llvm.extractvalue %arg0[1] : !llvm.struct<(i32, i32)>
%v9 = llvm.insertvalue %v8, %v7[1] : !llvm.struct<(i32, i32)>
%v10 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v11 = llvm.extractvalue %arg1[0] : !llvm.struct<(i32, i32)>
%v12 = llvm.insertvalue %v11, %v10[0] : !llvm.struct<(i32, i32)>
%v13 = llvm.extractvalue %arg1[1] : !llvm.struct<(i32, i32)>
%v14 = llvm.insertvalue %v13, %v12[1] : !llvm.struct<(i32, i32)>
%v15 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v16 = llvm.extractvalue %v9[0] : !llvm.struct<(i32, i32)>
%v17 = llvm.extractvalue %v14[0] : !llvm.struct<(i32, i32)>
%v18 = arith.addi %v16, %v17 : i32
%v19 = arith.constant 2 : i32
%v20 = arith.divsi %v18, %v19 : i32
%v21 = llvm.insertvalue %v20, %v15[0] : !llvm.struct<(i32, i32)>
%v22 = llvm.extractvalue %v9[1] : !llvm.struct<(i32, i32)>
%v23 = llvm.extractvalue %v14[1] : !llvm.struct<(i32, i32)>
%v24 = arith.addi %v22, %v23 : i32
%v25 = arith.constant 2 : i32
%v26 = arith.divsi %v24, %v25 : i32
%v27 = llvm.insertvalue %v26, %v21[1] : !llvm.struct<(i32, i32)>
%v28 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v29 = llvm.extractvalue %v27[0] : !llvm.struct<(i32, i32)>
%v30 = llvm.insertvalue %v29, %v28[0] : !llvm.struct<(i32, i32)>
%v31 = llvm.extractvalue %v27[1] : !llvm.struct<(i32, i32)>
%v32 = llvm.insertvalue %v31, %v30[1] : !llvm.struct<(i32, i32)>
func.return %v32 : !llvm.struct<(i32, i32)>
}
func.func @apply(%arg0: !llvm.struct<(!llvm.ptr, !llvm.ptr)>, %arg1: i32) -> i32 {
%v33 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v34 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v35 = llvm.insertvalue %v34, %v33[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v36 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v37 = llvm.insertvalue %v36, %v35[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v38 = llvm.extractvalue %v37[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v39 = llvm.extractvalue %v37[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v40 = llvm.call %v38(%v39, %arg1) : !llvm.ptr, (!llvm.ptr, i32) -> i32
func.return %v40 : i32
}
func.func @main() -> i32 {
%v41 = arith.constant 16 : i32
%v42 = func.call @flow_mem_malloc(%v41) : (i32) -> !llvm.ptr
%v43 = arith.constant 0 : i32
%v44 = arith.constant 16 : i32
%v45 = func.call @memset(%v42, %v43, %v44) : (!llvm.ptr, i32, i32) -> !llvm.ptr
%v46 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v47 = func.call @strlen(%v46) : (!llvm.ptr) -> i32
%v48 = arith.extsi %v47 : i32 to i64
%v49 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v50 = arith.constant 0 : i32
%v51 = llvm.insertvalue %v50, %v49[0] : !llvm.struct<(i32, i32)>
%v52 = arith.constant 0 : i32
%v53 = llvm.insertvalue %v52, %v51[1] : !llvm.struct<(i32, i32)>
%v54 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v55 = arith.constant 4 : i32
%v56 = llvm.insertvalue %v55, %v54[0] : !llvm.struct<(i32, i32)>
%v57 = arith.constant 6 : i32
%v58 = llvm.insertvalue %v57, %v56[1] : !llvm.struct<(i32, i32)>
%v59 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v60 = llvm.extractvalue %v53[0] : !llvm.struct<(i32, i32)>
%v61 = llvm.insertvalue %v60, %v59[0] : !llvm.struct<(i32, i32)>
%v62 = llvm.extractvalue %v53[1] : !llvm.struct<(i32, i32)>
%v63 = llvm.insertvalue %v62, %v61[1] : !llvm.struct<(i32, i32)>
%v64 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v65 = llvm.extractvalue %v58[0] : !llvm.struct<(i32, i32)>
%v66 = llvm.insertvalue %v65, %v64[0] : !llvm.struct<(i32, i32)>
%v67 = llvm.extractvalue %v58[1] : !llvm.struct<(i32, i32)>
%v68 = llvm.insertvalue %v67, %v66[1] : !llvm.struct<(i32, i32)>
%v69 = func.call @mid(%v63, %v68) : (!llvm.struct<(i32, i32)>, !llvm.struct<(i32, i32)>) -> !llvm.struct<(i32, i32)>
%v70 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v71 = llvm.extractvalue %v69[0] : !llvm.struct<(i32, i32)>
%v72 = llvm.insertvalue %v71, %v70[0] : !llvm.struct<(i32, i32)>
%v73 = llvm.extractvalue %v69[1] : !llvm.struct<(i32, i32)>
%v74 = llvm.insertvalue %v73, %v72[1] : !llvm.struct<(i32, i32)>
%v75 = arith.constant 5 : i32
%v76 = llvm.mlir.zero : !llvm.ptr
%v77 = llvm.getelementptr %v76[1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32)>
%v78 = llvm.ptrtoint %v77 : !llvm.ptr to i32
%v79 = func.call @flow_mem_malloc(%v78) : (i32) -> !llvm.ptr
%v80 = llvm.getelementptr %v79[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32)>
llvm.store %v75, %v80 : i32, !llvm.ptr
%v81 = func.constant @lambda_1 : (!llvm.ptr, i32) -> i32
%v82 = builtin.unrealized_conversion_cast %v81 : (!llvm.ptr, i32) -> i32 to !llvm.ptr
%v83 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v84 = llvm.insertvalue %v82, %v83[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v85 = llvm.insertvalue %v79, %v84[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v86 = arith.constant 2 : i32
%v87 = func.call @apply(%v85, %v86) : (!llvm.struct<(!llvm.ptr, !llvm.ptr)>, i32) -> i32
%v88 = arith.trunci %v48 : i64 to i32
%v89 = llvm.extractvalue %v74[0] : !llvm.struct<(i32, i32)>
%v90 = arith.addi %v88, %v89 : i32
%v91 = llvm.extractvalue %v74[1] : !llvm.struct<(i32, i32)>
%v92 = arith.addi %v90, %v91 : i32
%v93 = arith.addi %v92, %v87 : i32
func.return %v93 : i32
}
}
