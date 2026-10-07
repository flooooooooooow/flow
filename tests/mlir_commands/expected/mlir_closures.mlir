module {
func.func private @malloc(i64) -> !llvm.ptr
func.func private @memcpy(!llvm.ptr, !llvm.ptr, i64) -> !llvm.ptr
func.func private @free(!llvm.ptr) -> ()
func.func private @getenv(!llvm.ptr) -> !llvm.ptr
func.func private @atexit(!llvm.ptr) -> i32
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
%name = llvm.mlir.addressof @str_1 : !llvm.ptr
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
func.func private @flow_mem_note_stack(%n: i64) {
func.call @flow_mem_profile_init() : () -> ()
%op = llvm.mlir.addressof @flow_mem_profile_on : !llvm.ptr
%on = llvm.load %op : !llvm.ptr -> i32
%z32 = arith.constant 0 : i32
%yes = arith.cmpi ne, %on, %z32 : i32
scf.if %yes {
%bp = llvm.mlir.addressof @flow_mem_stack_bytes : !llvm.ptr
%bv = llvm.load %bp : !llvm.ptr -> i64
%bn = arith.addi %bv, %n : i64
llvm.store %bn, %bp : i64, !llvm.ptr
scf.yield
}
func.return
}
func.func private @flow_mem_note_arena(%n: i64) {
func.call @flow_mem_profile_init() : () -> ()
%op = llvm.mlir.addressof @flow_mem_profile_on : !llvm.ptr
%on = llvm.load %op : !llvm.ptr -> i32
%z32 = arith.constant 0 : i32
%yes = arith.cmpi ne, %on, %z32 : i32
scf.if %yes {
%bp = llvm.mlir.addressof @flow_mem_arena_bytes : !llvm.ptr
%bv = llvm.load %bp : !llvm.ptr -> i64
%bn = arith.addi %bv, %n : i64
llvm.store %bn, %bp : i64, !llvm.ptr
scf.yield
}
func.return
}
func.func @flow_mem_malloc(%n: i64) -> !llvm.ptr {
%p = func.call @malloc(%n) : (i64) -> !llvm.ptr
func.call @flow_mem_note_alloc(%n) : (i64) -> ()
func.return %p : !llvm.ptr
}
func.func private @calloc(i64, i64) -> !llvm.ptr
func.func private @realloc(!llvm.ptr, i64) -> !llvm.ptr
func.func @flow_mem_calloc(%c: i64, %s: i64) -> !llvm.ptr {
%p = func.call @calloc(%c, %s) : (i64, i64) -> !llvm.ptr
%n = arith.muli %c, %s : i64
func.call @flow_mem_note_alloc(%n) : (i64) -> ()
func.return %p : !llvm.ptr
}
func.func @flow_mem_realloc(%p: !llvm.ptr, %n: i64) -> !llvm.ptr {
%q = func.call @realloc(%p, %n) : (!llvm.ptr, i64) -> !llvm.ptr
func.call @flow_mem_note_alloc(%n) : (i64) -> ()
func.return %q : !llvm.ptr
}
func.func @flow_mem_free(%p: !llvm.ptr) {
func.call @free(%p) : (!llvm.ptr) -> ()
func.return
}
func.func @flow_mem_memcpy(%d: !llvm.ptr, %s: !llvm.ptr, %n: i64) -> !llvm.ptr {
func.call @flow_mem_note_copy(%n) : (i64) -> ()
%r = func.call @memcpy(%d, %s, %n) : (!llvm.ptr, !llvm.ptr, i64) -> !llvm.ptr
func.return %r : !llvm.ptr
}
func.func @flow_mem_report() {
%op = llvm.mlir.addressof @flow_mem_profile_on : !llvm.ptr
%on = llvm.load %op : !llvm.ptr -> i32
%z32 = arith.constant 0 : i32
%yes = arith.cmpi ne, %on, %z32 : i32
scf.if %yes {
%hdr = llvm.mlir.addressof @str_2 : !llvm.ptr
%h = llvm.call @printf(%hdr) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%g_flow_mem_alloc_count = llvm.mlir.addressof @flow_mem_alloc_count : !llvm.ptr
%v_flow_mem_alloc_count = llvm.load %g_flow_mem_alloc_count : !llvm.ptr -> i64
%f_flow_mem_alloc_count = llvm.mlir.addressof @str_3 : !llvm.ptr
%w_flow_mem_alloc_count = llvm.call @printf(%f_flow_mem_alloc_count, %v_flow_mem_alloc_count) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_alloc_bytes = llvm.mlir.addressof @flow_mem_alloc_bytes : !llvm.ptr
%v_flow_mem_alloc_bytes = llvm.load %g_flow_mem_alloc_bytes : !llvm.ptr -> i64
%f_flow_mem_alloc_bytes = llvm.mlir.addressof @str_4 : !llvm.ptr
%w_flow_mem_alloc_bytes = llvm.call @printf(%f_flow_mem_alloc_bytes, %v_flow_mem_alloc_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_peak_live = llvm.mlir.addressof @flow_mem_peak_live : !llvm.ptr
%v_flow_mem_peak_live = llvm.load %g_flow_mem_peak_live : !llvm.ptr -> i64
%f_flow_mem_peak_live = llvm.mlir.addressof @str_5 : !llvm.ptr
%w_flow_mem_peak_live = llvm.call @printf(%f_flow_mem_peak_live, %v_flow_mem_peak_live) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_temp_bytes = llvm.mlir.addressof @flow_mem_temp_bytes : !llvm.ptr
%v_flow_mem_temp_bytes = llvm.load %g_flow_mem_temp_bytes : !llvm.ptr -> i64
%f_flow_mem_temp_bytes = llvm.mlir.addressof @str_6 : !llvm.ptr
%w_flow_mem_temp_bytes = llvm.call @printf(%f_flow_mem_temp_bytes, %v_flow_mem_temp_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_copy_bytes = llvm.mlir.addressof @flow_mem_copy_bytes : !llvm.ptr
%v_flow_mem_copy_bytes = llvm.load %g_flow_mem_copy_bytes : !llvm.ptr -> i64
%f_flow_mem_copy_bytes = llvm.mlir.addressof @str_7 : !llvm.ptr
%w_flow_mem_copy_bytes = llvm.call @printf(%f_flow_mem_copy_bytes, %v_flow_mem_copy_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_stack_bytes = llvm.mlir.addressof @flow_mem_stack_bytes : !llvm.ptr
%v_flow_mem_stack_bytes = llvm.load %g_flow_mem_stack_bytes : !llvm.ptr -> i64
%f_flow_mem_stack_bytes = llvm.mlir.addressof @str_8 : !llvm.ptr
%w_flow_mem_stack_bytes = llvm.call @printf(%f_flow_mem_stack_bytes, %v_flow_mem_stack_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_arena_bytes = llvm.mlir.addressof @flow_mem_arena_bytes : !llvm.ptr
%v_flow_mem_arena_bytes = llvm.load %g_flow_mem_arena_bytes : !llvm.ptr -> i64
%f_flow_mem_arena_bytes = llvm.mlir.addressof @str_9 : !llvm.ptr
%w_flow_mem_arena_bytes = llvm.call @printf(%f_flow_mem_arena_bytes, %v_flow_mem_arena_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%sp = llvm.mlir.addressof @flow_mem_stack_bytes : !llvm.ptr
%sv = llvm.load %sp : !llvm.ptr -> i64
%ap = llvm.mlir.addressof @flow_mem_arena_bytes : !llvm.ptr
%av = llvm.load %ap : !llvm.ptr -> i64
%promo = arith.addi %sv, %av : i64
%pf = llvm.mlir.addressof @str_10 : !llvm.ptr
%ph = llvm.call @printf(%pf, %promo) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_map_overflow = llvm.mlir.addressof @flow_mem_map_overflow : !llvm.ptr
%v_flow_mem_map_overflow = llvm.load %g_flow_mem_map_overflow : !llvm.ptr -> i64
%f_flow_mem_map_overflow = llvm.mlir.addressof @str_11 : !llvm.ptr
%w_flow_mem_map_overflow = llvm.call @printf(%f_flow_mem_map_overflow, %v_flow_mem_map_overflow) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_site_concat = llvm.mlir.addressof @flow_mem_site_concat : !llvm.ptr
%v_flow_mem_site_concat = llvm.load %g_flow_mem_site_concat : !llvm.ptr -> i64
%f_flow_mem_site_concat = llvm.mlir.addressof @str_12 : !llvm.ptr
%w_flow_mem_site_concat = llvm.call @printf(%f_flow_mem_site_concat, %v_flow_mem_site_concat) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
scf.yield
}
func.return
}
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("note %d\0A\00") {addr_space = 0 : i32} : !llvm.array<9 x i8>
llvm.mlir.global internal constant @str_1("FLOW_MEM_PROFILE\00") {addr_space = 0 : i32} : !llvm.array<17 x i8>
llvm.mlir.global internal constant @str_2("\0A=== Flow memory profile (#740) ===\0A\00") {addr_space = 0 : i32} : !llvm.array<37 x i8>
llvm.mlir.global internal constant @str_3("allocations: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<19 x i8>
llvm.mlir.global internal constant @str_4("heap_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<18 x i8>
llvm.mlir.global internal constant @str_5("peak_live_heap: %lld\0A\00") {addr_space = 0 : i32} : !llvm.array<22 x i8>
llvm.mlir.global internal constant @str_6("temp_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<18 x i8>
llvm.mlir.global internal constant @str_7("copies: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<14 x i8>
llvm.mlir.global internal constant @str_8("stack_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<19 x i8>
llvm.mlir.global internal constant @str_9("arena_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<19 x i8>
llvm.mlir.global internal constant @str_10("promotion_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<23 x i8>
llvm.mlir.global internal constant @str_11("live_map_overflow: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<25 x i8>
llvm.mlir.global internal constant @str_12("site_concat: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<19 x i8>
llvm.mlir.global internal constant @str_13("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_14("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
func.func @__flow_callback_square(%env: !llvm.ptr, %arg1: i32) -> i32 {
%result = func.call @square(%arg1) : (i32) -> i32
func.return %result : i32
}
func.func private @lambda_1(%env: !llvm.ptr, %arg0: i32) -> i32 {
%v1 = arith.constant 2 : i32
%v2 = arith.muli %arg0, %v1 : i32
func.return %v2 : i32
}
func.func private @lambda_2(%env: !llvm.ptr, %arg0: i32) -> i32 {
%v3 = llvm.getelementptr %env[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32)>
%v4 = llvm.load %v3 : !llvm.ptr -> i32
%v5 = llvm.load %v3 : !llvm.ptr -> i32
%v6 = arith.addi %arg0, %v5 : i32
%v7 = llvm.mlir.addressof @BIAS : !llvm.ptr
%v8 = llvm.load %v7 : !llvm.ptr -> i32
%v9 = arith.addi %v6, %v8 : i32
func.return %v9 : i32
}
func.func private @lambda_3(%env: !llvm.ptr, %arg0: i32) -> i32 {
%v10 = llvm.getelementptr %env[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.struct<(!llvm.ptr, !llvm.ptr)>)>
%v11 = llvm.load %v10 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v12 = llvm.getelementptr %env[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.struct<(!llvm.ptr, !llvm.ptr)>)>
%v13 = llvm.load %v12 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v14 = llvm.load %v12 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v15 = llvm.extractvalue %v14[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v16 = llvm.extractvalue %v14[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v17 = llvm.call %v15(%v16, %arg0) : !llvm.ptr, (!llvm.ptr, i32) -> i32
%v18 = llvm.load %v10 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v19 = llvm.extractvalue %v18[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v20 = llvm.extractvalue %v18[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v21 = llvm.call %v19(%v20, %v17) : !llvm.ptr, (!llvm.ptr, i32) -> i32
func.return %v21 : i32
}
func.func private @lambda_4(%env: !llvm.ptr, %arg0: f64, %arg1: f64) -> f64 {
%v22 = arith.constant 0.5 : f64
%v23 = llvm.intr.fmuladd(%arg1, %v22, %arg0) : (f64, f64, f64) -> f64
func.return %v23 : f64
}
// Constant: BIAS
llvm.mlir.global internal constant @BIAS(1 : i32) : i32
func.func @apply(%arg0: !llvm.struct<(!llvm.ptr, !llvm.ptr)>, %arg1: i32) -> i32 {
%v24 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v25 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v26 = llvm.insertvalue %v25, %v24[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v27 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v28 = llvm.insertvalue %v27, %v26[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v29 = llvm.mlir.constant(1 : i64) : i64
%v30 = llvm.alloca %v29 x !llvm.struct<(!llvm.ptr, !llvm.ptr)> : (i64) -> !llvm.ptr
llvm.store %v28, %v30 : !llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.ptr
%v31 = llvm.load %v30 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v32 = llvm.extractvalue %v31[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v33 = llvm.extractvalue %v31[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v34 = llvm.call %v32(%v33, %arg1) : !llvm.ptr, (!llvm.ptr, i32) -> i32
func.return %v34 : i32
}
func.func @twice(%arg0: !llvm.struct<(!llvm.ptr, !llvm.ptr)>, %arg1: i32) -> i32 {
%v35 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v36 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v37 = llvm.insertvalue %v36, %v35[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v38 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v39 = llvm.insertvalue %v38, %v37[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v40 = llvm.mlir.constant(1 : i64) : i64
%v41 = llvm.alloca %v40 x !llvm.struct<(!llvm.ptr, !llvm.ptr)> : (i64) -> !llvm.ptr
llvm.store %v39, %v41 : !llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.ptr
%v42 = llvm.load %v41 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v43 = llvm.mlir.constant(1 : i64) : i64
%v44 = llvm.alloca %v43 x !llvm.struct<(!llvm.ptr, !llvm.ptr)> : (i64) -> !llvm.ptr
llvm.store %v42, %v44 : !llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.ptr
%v45 = llvm.load %v44 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v46 = llvm.extractvalue %v45[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v47 = llvm.extractvalue %v45[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v48 = llvm.load %v44 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v49 = llvm.extractvalue %v48[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v50 = llvm.extractvalue %v48[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v51 = llvm.call %v49(%v50, %arg1) : !llvm.ptr, (!llvm.ptr, i32) -> i32
%v52 = llvm.call %v46(%v47, %v51) : !llvm.ptr, (!llvm.ptr, i32) -> i32
func.return %v52 : i32
}
func.func @square(%arg0: i32) -> i32 {
%v53 = arith.muli %arg0, %arg0 : i32
func.return %v53 : i32
}
func.func @fold(%arg0: !llvm.struct<(!llvm.ptr, !llvm.ptr)>, %arg1: i32) -> f64 {
%v54 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v55 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v56 = llvm.insertvalue %v55, %v54[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v57 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v58 = llvm.insertvalue %v57, %v56[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v59 = llvm.mlir.constant(1 : i64) : i64
%v60 = llvm.alloca %v59 x !llvm.struct<(!llvm.ptr, !llvm.ptr)> : (i64) -> !llvm.ptr
llvm.store %v58, %v60 : !llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.ptr
%v61 = arith.constant 0.0 : f64
%v62 = llvm.mlir.constant(1 : i64) : i64
%v63 = llvm.alloca %v62 x f64 : (i64) -> !llvm.ptr
llvm.store %v61, %v63 : f64, !llvm.ptr
%v64 = arith.constant 0 : i32
%v65 = arith.index_cast %v64 : i32 to index
%v66 = arith.index_cast %arg1 : i32 to index
%v67 = arith.constant 1 : index
%v68 = arith.constant -1 : index
%v69 = arith.cmpi sle, %v65, %v66 : index
%v70 = arith.select %v69, %v67, %v68 : index
cf.br ^b1(%v65 : index)
^b1(%v71: index):
%v72 = arith.cmpi slt, %v71, %v66 : index
%v73 = arith.cmpi sgt, %v71, %v66 : index
%v74 = arith.select %v69, %v72, %v73 : i1
cf.cond_br %v74, ^b2(%v71 : index), ^b3(%v71 : index)
^b2(%v75: index):
%v76 = llvm.load %v60 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v77 = llvm.extractvalue %v76[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v78 = llvm.extractvalue %v76[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v79 = llvm.load %v63 : !llvm.ptr -> f64
%v80 = arith.index_cast %v75 : index to i64
%v81 = arith.sitofp %v80 : i64 to f64
%v82 = llvm.call %v77(%v78, %v79, %v81) : !llvm.ptr, (!llvm.ptr, f64, f64) -> f64
llvm.store %v82, %v63 : f64, !llvm.ptr
%v83 = arith.addi %v75, %v70 : index
cf.br ^b1(%v83 : index)
^b3(%v84: index):
%v85 = llvm.load %v63 : !llvm.ptr -> f64
func.return %v85 : f64
}
func.func @note(%arg0: i32) -> () {
%v86 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v87 = llvm.call @printf(%v86, %arg0) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
func.return
}
func.func @main() -> i32 {
%v88 = llvm.mlir.zero : !llvm.ptr
%v89 = func.constant @lambda_1 : (!llvm.ptr, i32) -> i32
%v90 = builtin.unrealized_conversion_cast %v89 : (!llvm.ptr, i32) -> i32 to !llvm.ptr
%v91 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v92 = llvm.insertvalue %v90, %v91[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v93 = llvm.insertvalue %v88, %v92[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v94 = arith.constant 10 : i32
%v95 = llvm.mlir.constant(1 : i64) : i64
%v96 = llvm.alloca %v95 x i32 : (i64) -> !llvm.ptr
llvm.store %v94, %v96 : i32, !llvm.ptr
%v97 = llvm.mlir.zero : !llvm.ptr
%v98 = llvm.getelementptr %v97[1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32)>
%v99 = llvm.ptrtoint %v98 : !llvm.ptr to i64
%v100 = func.call @flow_mem_malloc(%v99) : (i64) -> !llvm.ptr
%v101 = llvm.load %v96 : !llvm.ptr -> i32
%v102 = llvm.getelementptr %v100[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32)>
llvm.store %v101, %v102 : i32, !llvm.ptr
%v103 = func.constant @lambda_2 : (!llvm.ptr, i32) -> i32
%v104 = builtin.unrealized_conversion_cast %v103 : (!llvm.ptr, i32) -> i32 to !llvm.ptr
%v105 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v106 = llvm.insertvalue %v104, %v105[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v107 = llvm.insertvalue %v100, %v106[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v108 = arith.constant 100 : i32
llvm.store %v108, %v96 : i32, !llvm.ptr
%v109 = llvm.mlir.zero : !llvm.ptr
%v110 = llvm.getelementptr %v109[1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.struct<(!llvm.ptr, !llvm.ptr)>)>
%v111 = llvm.ptrtoint %v110 : !llvm.ptr to i64
%v112 = func.call @flow_mem_malloc(%v111) : (i64) -> !llvm.ptr
%v113 = llvm.getelementptr %v112[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.struct<(!llvm.ptr, !llvm.ptr)>)>
llvm.store %v107, %v113 : !llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.ptr
%v114 = llvm.getelementptr %v112[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.struct<(!llvm.ptr, !llvm.ptr)>)>
llvm.store %v93, %v114 : !llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.ptr
%v115 = func.constant @lambda_3 : (!llvm.ptr, i32) -> i32
%v116 = builtin.unrealized_conversion_cast %v115 : (!llvm.ptr, i32) -> i32 to !llvm.ptr
%v117 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v118 = llvm.insertvalue %v116, %v117[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v119 = llvm.insertvalue %v112, %v118[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v120 = llvm.mlir.zero : !llvm.ptr
%v121 = func.constant @lambda_4 : (!llvm.ptr, f64, f64) -> f64
%v122 = builtin.unrealized_conversion_cast %v121 : (!llvm.ptr, f64, f64) -> f64 to !llvm.ptr
%v123 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v124 = llvm.insertvalue %v122, %v123[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v125 = llvm.insertvalue %v120, %v124[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v126 = llvm.mlir.addressof @str_13 : !llvm.ptr
%v127 = arith.constant 21 : i32
%v128 = func.call @apply(%v93, %v127) : (!llvm.struct<(!llvm.ptr, !llvm.ptr)>, i32) -> i32
%v129 = llvm.call @printf(%v126, %v128) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v130 = llvm.mlir.addressof @str_13 : !llvm.ptr
%v131 = arith.constant 5 : i32
%v132 = func.call @apply(%v107, %v131) : (!llvm.struct<(!llvm.ptr, !llvm.ptr)>, i32) -> i32
%v133 = llvm.call @printf(%v130, %v132) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v134 = llvm.mlir.addressof @str_13 : !llvm.ptr
%v135 = llvm.extractvalue %v119[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v136 = llvm.extractvalue %v119[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v137 = arith.constant 4 : i32
%v138 = llvm.call %v135(%v136, %v137) : !llvm.ptr, (!llvm.ptr, i32) -> i32
%v139 = llvm.call @printf(%v134, %v138) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v140 = llvm.mlir.addressof @str_13 : !llvm.ptr
%v141 = arith.constant 3 : i32
%v142 = func.call @twice(%v93, %v141) : (!llvm.struct<(!llvm.ptr, !llvm.ptr)>, i32) -> i32
%v143 = llvm.call @printf(%v140, %v142) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v144 = llvm.mlir.addressof @str_13 : !llvm.ptr
%v145 = func.constant @__flow_callback_square : (!llvm.ptr, i32) -> i32
%v146 = builtin.unrealized_conversion_cast %v145 : (!llvm.ptr, i32) -> i32 to !llvm.ptr
%v147 = llvm.mlir.zero : !llvm.ptr
%v148 = llvm.mlir.zero : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v149 = llvm.insertvalue %v146, %v148[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v150 = llvm.insertvalue %v147, %v149[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v151 = arith.constant 7 : i32
%v152 = func.call @apply(%v150, %v151) : (!llvm.struct<(!llvm.ptr, !llvm.ptr)>, i32) -> i32
%v153 = llvm.call @printf(%v144, %v152) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v154 = llvm.mlir.addressof @str_14 : !llvm.ptr
%v155 = arith.constant 5 : i32
%v156 = func.call @fold(%v125, %v155) : (!llvm.struct<(!llvm.ptr, !llvm.ptr)>, i32) -> f64
%v157 = llvm.call @printf(%v154, %v156) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v158 = arith.constant 3 : i32
func.call @note(%v158) : (i32) -> ()
%v159 = arith.constant 0 : i32
func.return %v159 : i32
}
}
