module {
func.func private @memcpy(!llvm.ptr, !llvm.ptr, i64) -> !llvm.ptr
func.func private @free(!llvm.ptr) -> ()
func.func private @malloc(i64) -> !llvm.ptr
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
llvm.func @printf(!llvm.ptr, ...) -> i32
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
llvm.mlir.global internal constant @str_12("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_13("%lld\0A\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
llvm.mlir.global internal constant @str_14("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
// Constant: K
llvm.mlir.global internal constant @K(3 : i32) : i32
// Constant: MASK
llvm.mlir.global internal constant @MASK(16 : i32) : i32
// Constant: NEG
llvm.mlir.global internal constant @NEG(-5 : i64) : i64
// Constant: ZERO_F
// Module static: counter
llvm.mlir.global internal @counter(42 : i32) : i32
func.func @total(%arg0: !llvm.struct<(!llvm.ptr, i64)>) -> f64 {
%v1 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v2 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i64)>
%v3 = llvm.insertvalue %v2, %v1[0] : !llvm.struct<(!llvm.ptr, i64)>
%v4 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i64)>
%v5 = llvm.insertvalue %v4, %v3[1] : !llvm.struct<(!llvm.ptr, i64)>
%v6 = llvm.mlir.constant(1 : i64) : i64
%v7 = llvm.alloca %v6 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v5, %v7 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v8 = arith.constant 0.0 : f64
%v9 = llvm.mlir.constant(1 : i64) : i64
%v10 = llvm.alloca %v9 x f64 : (i64) -> !llvm.ptr
llvm.store %v8, %v10 : f64, !llvm.ptr
%v11 = arith.constant 0 : i32
%v12 = llvm.mlir.constant(1 : i64) : i64
%v13 = llvm.alloca %v12 x i32 : (i64) -> !llvm.ptr
llvm.store %v11, %v13 : i32, !llvm.ptr
cf.br ^b1
^b1:
%v14 = llvm.load %v13 : !llvm.ptr -> i32
%v15 = llvm.load %v7 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v16 = llvm.extractvalue %v15[1] : !llvm.struct<(!llvm.ptr, i64)>
%v17 = arith.extsi %v14 : i32 to i64
%v18 = arith.cmpi slt, %v17, %v16 : i64
cf.cond_br %v18, ^b2, ^b3
^b2:
%v19 = llvm.load %v10 : !llvm.ptr -> f64
%v20 = llvm.load %v7 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v21 = llvm.load %v13 : !llvm.ptr -> i32
%v22 = llvm.extractvalue %v20[0] : !llvm.struct<(!llvm.ptr, i64)>
%v23 = arith.extsi %v21 : i32 to i64
%v24 = llvm.getelementptr %v22[%v23] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v25 = llvm.load %v24 : !llvm.ptr -> f64
%v26 = arith.addf %v19, %v25 : f64
llvm.store %v26, %v10 : f64, !llvm.ptr
%v27 = llvm.load %v13 : !llvm.ptr -> i32
%v28 = arith.constant 1 : i32
%v29 = arith.addi %v27, %v28 : i32
llvm.store %v29, %v13 : i32, !llvm.ptr
cf.br ^b1
^b3:
%v30 = llvm.load %v10 : !llvm.ptr -> f64
func.return %v30 : f64
}
func.func @fill(%arg0: !llvm.struct<(!llvm.ptr, i64)>, %arg1: f64) -> () {
%v31 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v32 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i64)>
%v33 = llvm.insertvalue %v32, %v31[0] : !llvm.struct<(!llvm.ptr, i64)>
%v34 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i64)>
%v35 = llvm.insertvalue %v34, %v33[1] : !llvm.struct<(!llvm.ptr, i64)>
%v36 = llvm.mlir.constant(1 : i64) : i64
%v37 = llvm.alloca %v36 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v35, %v37 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v38 = arith.constant 0 : i32
%v39 = arith.extsi %v38 : i32 to i64
%v40 = llvm.mlir.constant(1 : i64) : i64
%v41 = llvm.alloca %v40 x i64 : (i64) -> !llvm.ptr
llvm.store %v39, %v41 : i64, !llvm.ptr
cf.br ^b4
^b4:
%v42 = llvm.load %v41 : !llvm.ptr -> i64
%v43 = llvm.load %v37 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v44 = llvm.extractvalue %v43[1] : !llvm.struct<(!llvm.ptr, i64)>
%v45 = arith.cmpi slt, %v42, %v44 : i64
cf.cond_br %v45, ^b5, ^b6
^b5:
%v46 = llvm.load %v37 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v47 = llvm.load %v41 : !llvm.ptr -> i64
%v48 = llvm.extractvalue %v46[0] : !llvm.struct<(!llvm.ptr, i64)>
%v49 = llvm.getelementptr %v48[%v47] : (!llvm.ptr, i64) -> !llvm.ptr, f64
llvm.store %arg1, %v49 : f64, !llvm.ptr
%v50 = llvm.load %v41 : !llvm.ptr -> i64
%v51 = arith.constant 1 : i32
%v52 = arith.extsi %v51 : i32 to i64
%v53 = arith.addi %v50, %v52 : i64
llvm.store %v53, %v41 : i64, !llvm.ptr
cf.br ^b4
^b6:
func.return
}
func.func @make(%arg0: i32) -> !llvm.struct<(!llvm.ptr, i64)> {
%v54 = arith.extsi %arg0 : i32 to i64
%v55 = arith.constant 8 : i32
%v56 = arith.extsi %v55 : i32 to i64
%v57 = arith.muli %v54, %v56 : i64
%v58 = func.call @flow_mem_malloc(%v57) : (i64) -> !llvm.ptr
%v59 = arith.constant 0 : i32
%v60 = arith.extsi %v59 : i32 to i64
%v61 = arith.extsi %arg0 : i32 to i64
%v62 = llvm.getelementptr %v58[%v60] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v63 = arith.subi %v61, %v60 : i64
%v64 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v65 = llvm.insertvalue %v62, %v64[0] : !llvm.struct<(!llvm.ptr, i64)>
%v66 = llvm.insertvalue %v63, %v65[1] : !llvm.struct<(!llvm.ptr, i64)>
%v67 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v68 = llvm.extractvalue %v66[0] : !llvm.struct<(!llvm.ptr, i64)>
%v69 = llvm.insertvalue %v68, %v67[0] : !llvm.struct<(!llvm.ptr, i64)>
%v70 = llvm.extractvalue %v66[1] : !llvm.struct<(!llvm.ptr, i64)>
%v71 = llvm.insertvalue %v70, %v69[1] : !llvm.struct<(!llvm.ptr, i64)>
%v72 = llvm.mlir.constant(1 : i64) : i64
%v73 = llvm.alloca %v72 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v71, %v73 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v74 = llvm.load %v73 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
func.return %v74 : !llvm.struct<(!llvm.ptr, i64)>
}
func.func @first4(%arg0: !llvm.struct<(!llvm.ptr, i64)>) -> i32 {
%v75 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v76 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i64)>
%v77 = llvm.insertvalue %v76, %v75[0] : !llvm.struct<(!llvm.ptr, i64)>
%v78 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i64)>
%v79 = llvm.insertvalue %v78, %v77[1] : !llvm.struct<(!llvm.ptr, i64)>
%v80 = llvm.mlir.constant(1 : i64) : i64
%v81 = llvm.alloca %v80 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v79, %v81 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v82 = llvm.load %v81 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v83 = arith.constant 0 : i32
%v84 = llvm.extractvalue %v82[0] : !llvm.struct<(!llvm.ptr, i64)>
%v85 = arith.extsi %v83 : i32 to i64
%v86 = llvm.getelementptr %v84[%v85] : (!llvm.ptr, i64) -> !llvm.ptr, i32
%v87 = llvm.load %v86 : !llvm.ptr -> i32
%v88 = llvm.load %v81 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v89 = arith.constant 3 : i32
%v90 = llvm.extractvalue %v88[0] : !llvm.struct<(!llvm.ptr, i64)>
%v91 = arith.extsi %v89 : i32 to i64
%v92 = llvm.getelementptr %v90[%v91] : (!llvm.ptr, i64) -> !llvm.ptr, i32
%v93 = llvm.load %v92 : !llvm.ptr -> i32
%v94 = arith.addi %v87, %v93 : i32
func.return %v94 : i32
}
func.func @scale(%arg0: memref<?xf32>, %arg1: memref<?xf32>, %arg2: i32, %arg3: f32) -> () {
// flow: vectorized elementwise f32 loop (VF=4)
%v95 = arith.constant 0 : i32
%v96 = arith.index_cast %v95 : i32 to index
%v97 = arith.index_cast %arg2 : i32 to index
%v98 = arith.constant 1 : index
%v99 = arith.constant 4 : index
%v100 = arith.subi %v97, %v96 : index
%v101 = arith.remsi %v100, %v99 : index
%v102 = arith.subi %v100, %v101 : index
%v103 = arith.addi %v96, %v102 : index
scf.for %v104 = %v96 to %v103 step %v99 {
%v105 = arith.constant 0.0 : f32
%v106 = vector.transfer_read %arg1[%v104], %v105 {in_bounds = [true]} : memref<?xf32>, vector<4xf32>
%v107 = arith.negf %v106 : vector<4xf32>
%v108 = vector.broadcast %arg3 : f32 to vector<4xf32>
%v109 = arith.mulf %v107, %v108 : vector<4xf32>
%v110 = arith.constant 2.0 : f32
%v111 = vector.broadcast %v110 : f32 to vector<4xf32>
%v112 = arith.addf %v109, %v111 : vector<4xf32>
%v113 = arith.constant 0.0 : f32
%v114 = vector.transfer_read %arg0[%v104], %v113 {in_bounds = [true]} : memref<?xf32>, vector<4xf32>
%v115 = arith.constant 4.0 : f32
%v116 = vector.broadcast %v115 : f32 to vector<4xf32>
%v117 = arith.divf %v114, %v116 : vector<4xf32>
%v118 = arith.subf %v112, %v117 : vector<4xf32>
vector.transfer_write %v118, %arg0[%v104] {in_bounds = [true]} : vector<4xf32>, memref<?xf32>
}
scf.for %v119 = %v103 to %v97 step %v98 {
%v120 = memref.load %arg1[%v119] : memref<?xf32>
%v121 = arith.negf %v120 : f32
%v122 = arith.mulf %v121, %arg3 : f32
%v123 = arith.constant 2.0 : f64
%v124 = arith.extf %v122 : f32 to f64
%v125 = arith.addf %v124, %v123 : f64
%v126 = memref.load %arg0[%v119] : memref<?xf32>
%v127 = arith.constant 4.0 : f64
%v128 = arith.extf %v126 : f32 to f64
%v129 = arith.divf %v128, %v127 : f64
%v130 = arith.subf %v125, %v129 : f64
%v131 = arith.truncf %v130 : f64 to f32
memref.store %v131, %arg0[%v119] : memref<?xf32>
}
func.return
}
func.func @dot(%arg0: memref<?xf32>, %arg1: memref<?xf32>, %arg2: i32) -> f32 {
%v132 = arith.constant 0.0 : f64
%v133 = arith.truncf %v132 : f64 to f32
%v134 = llvm.mlir.constant(1 : i64) : i64
%v135 = llvm.alloca %v134 x f32 : (i64) -> !llvm.ptr
llvm.store %v133, %v135 : f32, !llvm.ptr
%v136 = arith.constant 0 : i32
%v137 = arith.index_cast %v136 : i32 to index
%v138 = arith.index_cast %arg2 : i32 to index
%v139 = arith.constant 1 : index
%v140 = arith.constant -1 : index
%v141 = arith.cmpi sle, %v137, %v138 : index
%v142 = arith.select %v141, %v139, %v140 : index
cf.br ^b7(%v137 : index)
^b7(%v143: index):
%v144 = arith.cmpi slt, %v143, %v138 : index
%v145 = arith.cmpi sgt, %v143, %v138 : index
%v146 = arith.select %v141, %v144, %v145 : i1
cf.cond_br %v146, ^b8(%v143 : index), ^b9(%v143 : index)
^b8(%v147: index):
%v148 = llvm.load %v135 : !llvm.ptr -> f32
%v149 = memref.load %arg0[%v147] : memref<?xf32>
%v150 = memref.load %arg1[%v147] : memref<?xf32>
%v151 = llvm.intr.fmuladd(%v149, %v150, %v148) : (f32, f32, f32) -> f32
llvm.store %v151, %v135 : f32, !llvm.ptr
%v152 = arith.addi %v147, %v142 : index
cf.br ^b7(%v152 : index)
^b9(%v153: index):
%v154 = llvm.load %v135 : !llvm.ptr -> f32
func.return %v154 : f32
}
func.func @main() -> i32 {
%v155 = arith.constant 4 : i32
%v156 = func.call @make(%v155) : (i32) -> !llvm.struct<(!llvm.ptr, i64)>
%v157 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v158 = llvm.extractvalue %v156[0] : !llvm.struct<(!llvm.ptr, i64)>
%v159 = llvm.insertvalue %v158, %v157[0] : !llvm.struct<(!llvm.ptr, i64)>
%v160 = llvm.extractvalue %v156[1] : !llvm.struct<(!llvm.ptr, i64)>
%v161 = llvm.insertvalue %v160, %v159[1] : !llvm.struct<(!llvm.ptr, i64)>
%v162 = llvm.mlir.constant(1 : i64) : i64
%v163 = llvm.alloca %v162 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v161, %v163 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v164 = llvm.load %v163 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v165 = llvm.mlir.constant(1 : i64) : i64
%v166 = llvm.alloca %v165 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v164, %v166 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v167 = llvm.load %v166 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v168 = arith.constant 2.5 : f64
func.call @fill(%v167, %v168) : (!llvm.struct<(!llvm.ptr, i64)>, f64) -> ()
%v169 = llvm.load %v166 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v170 = llvm.extractvalue %v169[0] : !llvm.struct<(!llvm.ptr, i64)>
%v171 = arith.constant 1 : i32
%v172 = arith.constant 3 : i32
%v173 = arith.extsi %v171 : i32 to i64
%v174 = arith.extsi %v172 : i32 to i64
%v175 = llvm.getelementptr %v170[%v173] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v176 = arith.subi %v174, %v173 : i64
%v177 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v178 = llvm.insertvalue %v175, %v177[0] : !llvm.struct<(!llvm.ptr, i64)>
%v179 = llvm.insertvalue %v176, %v178[1] : !llvm.struct<(!llvm.ptr, i64)>
%v180 = llvm.mlir.constant(1 : i64) : i64
%v181 = llvm.alloca %v180 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v179, %v181 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v182 = arith.constant 2 : i32
%v183 = func.call @make(%v182) : (i32) -> !llvm.struct<(!llvm.ptr, i64)>
%v184 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v185 = llvm.extractvalue %v183[0] : !llvm.struct<(!llvm.ptr, i64)>
%v186 = llvm.insertvalue %v185, %v184[0] : !llvm.struct<(!llvm.ptr, i64)>
%v187 = llvm.extractvalue %v183[1] : !llvm.struct<(!llvm.ptr, i64)>
%v188 = llvm.insertvalue %v187, %v186[1] : !llvm.struct<(!llvm.ptr, i64)>
%v189 = llvm.mlir.constant(1 : i64) : i64
%v190 = llvm.alloca %v189 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v188, %v190 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v191 = llvm.load %v190 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v192 = llvm.mlir.constant(1 : i64) : i64
%v193 = llvm.alloca %v192 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v191, %v193 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v194 = llvm.load %v166 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
llvm.store %v194, %v193 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v195 = llvm.load %v181 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v196 = func.call @total(%v195) : (!llvm.struct<(!llvm.ptr, i64)>) -> f64
%v197 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v198 = llvm.call @printf(%v197, %v196) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v199 = arith.constant 0 : i32
%v200 = llvm.load %v193 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v201 = llvm.extractvalue %v200[1] : !llvm.struct<(!llvm.ptr, i64)>
%v202 = llvm.mlir.addressof @str_13 : !llvm.ptr
%v203 = llvm.call @printf(%v202, %v201) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v204 = arith.constant 0 : i32
%v205 = llvm.load %v166 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v206 = llvm.extractvalue %v205[0] : !llvm.struct<(!llvm.ptr, i64)>
%v207 = arith.constant 0 : i32
%v208 = arith.constant 2 : i32
%v209 = arith.extsi %v207 : i32 to i64
%v210 = arith.extsi %v208 : i32 to i64
%v211 = llvm.getelementptr %v206[%v209] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v212 = arith.subi %v210, %v209 : i64
%v213 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v214 = llvm.insertvalue %v211, %v213[0] : !llvm.struct<(!llvm.ptr, i64)>
%v215 = llvm.insertvalue %v212, %v214[1] : !llvm.struct<(!llvm.ptr, i64)>
%v216 = func.call @total(%v215) : (!llvm.struct<(!llvm.ptr, i64)>) -> f64
%v217 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v218 = llvm.call @printf(%v217, %v216) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v219 = arith.constant 0 : i32
%v220 = arith.constant 7 : i32
%v221 = arith.constant 0 : index
%v222 = arith.constant 4 : index
%v223 = arith.constant 1 : index
%v224 = llvm.mlir.constant(1 : i64) : i64
%v225 = llvm.alloca %v224 x !llvm.array<4 x i32> : (i64) -> !llvm.ptr
%v226 = arith.constant 16 : i64
func.call @flow_mem_note_stack(%v226) : (i64) -> ()
scf.for %v227 = %v221 to %v222 step %v223 {
%v228 = arith.index_cast %v227 : index to i64
%v229 = llvm.getelementptr %v225[0, %v228] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x i32>
llvm.store %v220, %v229 : i32, !llvm.ptr
}
%v230 = arith.constant 2 : i32
%v231 = arith.extsi %v230 : i32 to i64
%v232 = llvm.getelementptr %v225[0, %v231] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x i32>
%v233 = llvm.load %v232 : !llvm.ptr -> i32
%v234 = arith.constant 7 : i32
%v235 = arith.constant 0 : index
%v236 = arith.constant 4 : index
%v237 = arith.constant 1 : index
%v238 = memref.alloca() : memref<4xi32>
scf.for %v239 = %v235 to %v236 step %v237 {
memref.store %v234, %v238[%v239] : memref<4xi32>
}
%v240 = memref.extract_aligned_pointer_as_index %v238 : memref<4xi32> -> index
%v241 = arith.index_cast %v240 : index to i64
%v242 = llvm.inttoptr %v241 : i64 to !llvm.ptr
%v243 = arith.constant 0 : index
%v244 = memref.dim %v238, %v243 : memref<4xi32>
%v245 = arith.index_cast %v244 : index to i64
%v246 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v247 = llvm.insertvalue %v242, %v246[0] : !llvm.struct<(!llvm.ptr, i64)>
%v248 = llvm.insertvalue %v245, %v247[1] : !llvm.struct<(!llvm.ptr, i64)>
%v249 = func.call @first4(%v248) : (!llvm.struct<(!llvm.ptr, i64)>) -> i32
%v250 = arith.addi %v233, %v249 : i32
%v251 = llvm.mlir.addressof @str_14 : !llvm.ptr
%v252 = llvm.call @printf(%v251, %v250) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v253 = arith.constant 0 : i32
%v254 = arith.constant 8 : i32
%v255 = arith.index_cast %v254 : i32 to index
%v256 = memref.alloc(%v255) : memref<?xf32>
%v257 = arith.constant 0.0 : f32
%v258 = arith.constant 0 : index
%v259 = arith.constant 1 : index
scf.for %v260 = %v258 to %v255 step %v259 {
memref.store %v257, %v256[%v260] : memref<?xf32>
}
%v261 = arith.constant 8 : i32
%v262 = arith.index_cast %v261 : i32 to index
%v263 = memref.alloc(%v262) : memref<?xf32>
%v264 = arith.constant 0.0 : f32
%v265 = arith.constant 0 : index
%v266 = arith.constant 1 : index
scf.for %v267 = %v265 to %v262 step %v266 {
memref.store %v264, %v263[%v267] : memref<?xf32>
}
%v268 = arith.constant 0 : i32
%v269 = arith.constant 8 : i32
%v270 = arith.index_cast %v268 : i32 to index
%v271 = arith.index_cast %v269 : i32 to index
%v272 = arith.constant 1 : index
%v273 = arith.constant -1 : index
%v274 = arith.cmpi sle, %v270, %v271 : index
%v275 = arith.select %v274, %v272, %v273 : index
cf.br ^b10(%v270 : index)
^b10(%v276: index):
%v277 = arith.cmpi slt, %v276, %v271 : index
%v278 = arith.cmpi sgt, %v276, %v271 : index
%v279 = arith.select %v274, %v277, %v278 : i1
cf.cond_br %v279, ^b11(%v276 : index), ^b12(%v276 : index)
^b11(%v280: index):
%v281 = arith.constant 1.5 : f64
%v282 = arith.truncf %v281 : f64 to f32
memref.store %v282, %v263[%v280] : memref<?xf32>
%v283 = arith.constant 2.0 : f64
%v284 = arith.truncf %v283 : f64 to f32
memref.store %v284, %v256[%v280] : memref<?xf32>
%v285 = arith.addi %v280, %v275 : index
cf.br ^b10(%v285 : index)
^b12(%v286: index):
%v287 = arith.constant 8 : i32
%v288 = arith.constant 0.5 : f64
%v289 = arith.truncf %v288 : f64 to f32
func.call @scale(%v256, %v263, %v287, %v289) : (memref<?xf32>, memref<?xf32>, i32, f32) -> ()
%v290 = arith.constant 3 : i32
%v291 = arith.index_cast %v290 : i32 to index
%v292 = memref.load %v256[%v291] : memref<?xf32>
%v293 = arith.extf %v292 : f32 to f64
%v294 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v295 = llvm.call @printf(%v294, %v293) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v296 = arith.constant 0 : i32
%v297 = arith.constant 1.0 : f64
%v298 = arith.constant 2.0 : f64
%v299 = arith.constant 3.0 : f64
%v300 = arith.truncf %v297 : f64 to f32
%v301 = arith.truncf %v298 : f64 to f32
%v302 = arith.truncf %v299 : f64 to f32
%v303 = memref.alloca() : memref<3xf32>
%v304 = arith.constant 0 : index
memref.store %v300, %v303[%v304] : memref<3xf32>
%v305 = arith.constant 1 : index
memref.store %v301, %v303[%v305] : memref<3xf32>
%v306 = arith.constant 2 : index
memref.store %v302, %v303[%v306] : memref<3xf32>
%v307 = arith.constant 4.0 : f64
%v308 = arith.constant 5.0 : f64
%v309 = arith.constant 6.0 : f64
%v310 = arith.truncf %v307 : f64 to f32
%v311 = arith.truncf %v308 : f64 to f32
%v312 = arith.truncf %v309 : f64 to f32
%v313 = memref.alloca() : memref<3xf32>
%v314 = arith.constant 0 : index
memref.store %v310, %v313[%v314] : memref<3xf32>
%v315 = arith.constant 1 : index
memref.store %v311, %v313[%v315] : memref<3xf32>
%v316 = arith.constant 2 : index
memref.store %v312, %v313[%v316] : memref<3xf32>
%v317 = arith.constant 3 : i32
%v318 = memref.cast %v303 : memref<3xf32> to memref<?xf32>
%v319 = memref.cast %v313 : memref<3xf32> to memref<?xf32>
%v320 = func.call @dot(%v318, %v319, %v317) : (memref<?xf32>, memref<?xf32>, i32) -> f32
%v321 = arith.extf %v320 : f32 to f64
%v322 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v323 = llvm.call @printf(%v322, %v321) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v324 = arith.constant 0 : i32
%v325 = arith.constant 1 : i32
%v326 = arith.constant 2 : i32
%v327 = arith.constant 3 : i32
%v328 = llvm.mlir.constant(1 : i64) : i64
%v329 = llvm.alloca %v328 x !llvm.array<3 x i32> : (i64) -> !llvm.ptr
%v330 = arith.constant 12 : i64
func.call @flow_mem_note_stack(%v330) : (i64) -> ()
%v331 = llvm.mlir.zero : !llvm.array<3 x i32>
llvm.store %v331, %v329 : !llvm.array<3 x i32>, !llvm.ptr
%v332 = llvm.mlir.constant(0 : i64) : i64
%v333 = llvm.getelementptr %v329[0, %v332] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v325, %v333 : i32, !llvm.ptr
%v334 = llvm.mlir.constant(1 : i64) : i64
%v335 = llvm.getelementptr %v329[0, %v334] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v326, %v335 : i32, !llvm.ptr
%v336 = llvm.mlir.constant(2 : i64) : i64
%v337 = llvm.getelementptr %v329[0, %v336] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v327, %v337 : i32, !llvm.ptr
%v338 = arith.constant 0 : i32
%v339 = llvm.mlir.constant(1 : i64) : i64
%v340 = llvm.alloca %v339 x i32 : (i64) -> !llvm.ptr
llvm.store %v338, %v340 : i32, !llvm.ptr
%v341 = arith.constant 0 : i32
%v342 = arith.extsi %v341 : i32 to i64
%v343 = llvm.getelementptr %v329[0, %v342] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
%v344 = llvm.load %v343 : !llvm.ptr -> i32
%v345 = arith.constant 1 : i32
%v346 = arith.cmpi eq, %v344, %v345 : i32
%v347 = arith.constant 1 : i32
%v348 = arith.extsi %v347 : i32 to i64
%v349 = llvm.getelementptr %v329[0, %v348] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
%v350 = llvm.load %v349 : !llvm.ptr -> i32
%v351 = arith.constant 2 : i32
%v352 = arith.extsi %v351 : i32 to i64
%v353 = llvm.getelementptr %v329[0, %v352] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
%v354 = llvm.load %v353 : !llvm.ptr -> i32
cf.cond_br %v346, ^b13, ^b14
^b13:
%v355 = arith.addi %v350, %v354 : i32
llvm.store %v355, %v340 : i32, !llvm.ptr
cf.br ^b15
^b14:
%v356 = arith.constant 99 : i32
llvm.store %v356, %v340 : i32, !llvm.ptr
cf.br ^b15
^b15:
%v357 = llvm.load %v340 : !llvm.ptr -> i32
%v358 = llvm.mlir.addressof @str_14 : !llvm.ptr
%v359 = llvm.call @printf(%v358, %v357) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v360 = arith.constant 0 : i32
%v361 = llvm.mlir.addressof @K : !llvm.ptr
%v362 = llvm.load %v361 : !llvm.ptr -> i32
%v363 = llvm.mlir.addressof @MASK : !llvm.ptr
%v364 = llvm.load %v363 : !llvm.ptr -> i32
%v365 = arith.addi %v362, %v364 : i32
%v366 = llvm.mlir.addressof @counter : !llvm.ptr
%v367 = llvm.load %v366 : !llvm.ptr -> i32
%v368 = arith.addi %v365, %v367 : i32
%v369 = llvm.mlir.addressof @str_14 : !llvm.ptr
%v370 = llvm.call @printf(%v369, %v368) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v371 = arith.constant 0 : i32
%v372 = llvm.mlir.addressof @NEG : !llvm.ptr
%v373 = llvm.load %v372 : !llvm.ptr -> i64
%v374 = llvm.mlir.addressof @str_13 : !llvm.ptr
%v375 = llvm.call @printf(%v374, %v373) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v376 = arith.constant 0 : i32
%v377 = arith.constant 1.5 : f64
%v378 = arith.constant 2.0 : f64
%v379 = arith.mulf %v377, %v378 : f64
%v380 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v381 = llvm.call @printf(%v380, %v379) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v382 = arith.constant 0 : i32
%v383 = arith.constant 0 : i32
func.return %v383 : i32
}
}
