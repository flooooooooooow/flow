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
%v1 = llvm.mlir.constant(1 : i64) : i64
%v2 = llvm.alloca %v1 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
%v3 = llvm.mlir.constant(1 : i64) : i64
%v4 = llvm.alloca %v3 x f64 : (i64) -> !llvm.ptr
%v5 = llvm.mlir.constant(1 : i64) : i64
%v6 = llvm.alloca %v5 x i32 : (i64) -> !llvm.ptr
%v7 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v8 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i64)>
%v9 = llvm.insertvalue %v8, %v7[0] : !llvm.struct<(!llvm.ptr, i64)>
%v10 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i64)>
%v11 = llvm.insertvalue %v10, %v9[1] : !llvm.struct<(!llvm.ptr, i64)>
llvm.store %v11, %v2 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v12 = arith.constant 0.0 : f64
llvm.store %v12, %v4 : f64, !llvm.ptr
%v13 = arith.constant 0 : i32
llvm.store %v13, %v6 : i32, !llvm.ptr
cf.br ^b1
^b1:
%v14 = llvm.load %v6 : !llvm.ptr -> i32
%v15 = llvm.load %v2 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v16 = llvm.extractvalue %v15[1] : !llvm.struct<(!llvm.ptr, i64)>
%v17 = arith.extsi %v14 : i32 to i64
%v18 = arith.cmpi slt, %v17, %v16 : i64
cf.cond_br %v18, ^b2, ^b3
^b2:
%v19 = llvm.load %v4 : !llvm.ptr -> f64
%v20 = llvm.load %v2 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v21 = llvm.load %v6 : !llvm.ptr -> i32
%v22 = llvm.extractvalue %v20[0] : !llvm.struct<(!llvm.ptr, i64)>
%v23 = arith.extsi %v21 : i32 to i64
%v24 = llvm.getelementptr %v22[%v23] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v25 = llvm.load %v24 : !llvm.ptr -> f64
%v26 = arith.addf %v19, %v25 : f64
llvm.store %v26, %v4 : f64, !llvm.ptr
%v27 = llvm.load %v6 : !llvm.ptr -> i32
%v28 = arith.constant 1 : i32
%v29 = arith.addi %v27, %v28 : i32
llvm.store %v29, %v6 : i32, !llvm.ptr
cf.br ^b1
^b3:
%v30 = llvm.load %v4 : !llvm.ptr -> f64
func.return %v30 : f64
}
func.func @fill(%arg0: !llvm.struct<(!llvm.ptr, i64)>, %arg1: f64) -> () {
%v31 = llvm.mlir.constant(1 : i64) : i64
%v32 = llvm.alloca %v31 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
%v33 = llvm.mlir.constant(1 : i64) : i64
%v34 = llvm.alloca %v33 x i64 : (i64) -> !llvm.ptr
%v35 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v36 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i64)>
%v37 = llvm.insertvalue %v36, %v35[0] : !llvm.struct<(!llvm.ptr, i64)>
%v38 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i64)>
%v39 = llvm.insertvalue %v38, %v37[1] : !llvm.struct<(!llvm.ptr, i64)>
llvm.store %v39, %v32 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v40 = arith.constant 0 : i32
%v41 = arith.extsi %v40 : i32 to i64
llvm.store %v41, %v34 : i64, !llvm.ptr
cf.br ^b4
^b4:
%v42 = llvm.load %v34 : !llvm.ptr -> i64
%v43 = llvm.load %v32 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v44 = llvm.extractvalue %v43[1] : !llvm.struct<(!llvm.ptr, i64)>
%v45 = arith.cmpi slt, %v42, %v44 : i64
cf.cond_br %v45, ^b5, ^b6
^b5:
%v46 = llvm.load %v32 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v47 = llvm.load %v34 : !llvm.ptr -> i64
%v48 = llvm.extractvalue %v46[0] : !llvm.struct<(!llvm.ptr, i64)>
%v49 = llvm.getelementptr %v48[%v47] : (!llvm.ptr, i64) -> !llvm.ptr, f64
llvm.store %arg1, %v49 : f64, !llvm.ptr
%v50 = llvm.load %v34 : !llvm.ptr -> i64
%v51 = arith.constant 1 : i32
%v52 = arith.extsi %v51 : i32 to i64
%v53 = arith.addi %v50, %v52 : i64
llvm.store %v53, %v34 : i64, !llvm.ptr
cf.br ^b4
^b6:
func.return
}
func.func @make(%arg0: i32) -> !llvm.struct<(!llvm.ptr, i64)> {
%v54 = llvm.mlir.constant(1 : i64) : i64
%v55 = llvm.alloca %v54 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
%v56 = arith.extsi %arg0 : i32 to i64
%v57 = arith.constant 8 : i32
%v58 = arith.extsi %v57 : i32 to i64
%v59 = arith.muli %v56, %v58 : i64
%v60 = func.call @flow_mem_malloc(%v59) : (i64) -> !llvm.ptr
%v61 = arith.constant 0 : i32
%v62 = arith.extsi %v61 : i32 to i64
%v63 = arith.extsi %arg0 : i32 to i64
%v64 = llvm.getelementptr %v60[%v62] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v65 = arith.subi %v63, %v62 : i64
%v66 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v67 = llvm.insertvalue %v64, %v66[0] : !llvm.struct<(!llvm.ptr, i64)>
%v68 = llvm.insertvalue %v65, %v67[1] : !llvm.struct<(!llvm.ptr, i64)>
%v69 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v70 = llvm.extractvalue %v68[0] : !llvm.struct<(!llvm.ptr, i64)>
%v71 = llvm.insertvalue %v70, %v69[0] : !llvm.struct<(!llvm.ptr, i64)>
%v72 = llvm.extractvalue %v68[1] : !llvm.struct<(!llvm.ptr, i64)>
%v73 = llvm.insertvalue %v72, %v71[1] : !llvm.struct<(!llvm.ptr, i64)>
llvm.store %v73, %v55 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v74 = llvm.load %v55 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
func.return %v74 : !llvm.struct<(!llvm.ptr, i64)>
}
func.func @first4(%arg0: !llvm.struct<(!llvm.ptr, i64)>) -> i32 {
%v75 = llvm.mlir.constant(1 : i64) : i64
%v76 = llvm.alloca %v75 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
%v77 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v78 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i64)>
%v79 = llvm.insertvalue %v78, %v77[0] : !llvm.struct<(!llvm.ptr, i64)>
%v80 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i64)>
%v81 = llvm.insertvalue %v80, %v79[1] : !llvm.struct<(!llvm.ptr, i64)>
llvm.store %v81, %v76 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v82 = llvm.load %v76 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v83 = arith.constant 0 : i32
%v84 = llvm.extractvalue %v82[0] : !llvm.struct<(!llvm.ptr, i64)>
%v85 = arith.extsi %v83 : i32 to i64
%v86 = llvm.getelementptr %v84[%v85] : (!llvm.ptr, i64) -> !llvm.ptr, i32
%v87 = llvm.load %v86 : !llvm.ptr -> i32
%v88 = llvm.load %v76 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
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
%v132 = llvm.mlir.constant(1 : i64) : i64
%v133 = llvm.alloca %v132 x f32 : (i64) -> !llvm.ptr
%v134 = arith.constant 0.0 : f64
%v135 = arith.truncf %v134 : f64 to f32
llvm.store %v135, %v133 : f32, !llvm.ptr
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
%v148 = llvm.load %v133 : !llvm.ptr -> f32
%v149 = memref.load %arg0[%v147] : memref<?xf32>
%v150 = memref.load %arg1[%v147] : memref<?xf32>
%v151 = llvm.intr.fmuladd(%v149, %v150, %v148) : (f32, f32, f32) -> f32
llvm.store %v151, %v133 : f32, !llvm.ptr
%v152 = arith.addi %v147, %v142 : index
cf.br ^b7(%v152 : index)
^b9(%v153: index):
%v154 = llvm.load %v133 : !llvm.ptr -> f32
func.return %v154 : f32
}
func.func @main() -> i32 {
%v155 = llvm.mlir.constant(1 : i64) : i64
%v156 = llvm.alloca %v155 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
%v157 = llvm.mlir.constant(1 : i64) : i64
%v158 = llvm.alloca %v157 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
%v159 = llvm.mlir.constant(1 : i64) : i64
%v160 = llvm.alloca %v159 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
%v161 = llvm.mlir.constant(1 : i64) : i64
%v162 = llvm.alloca %v161 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
%v163 = llvm.mlir.constant(1 : i64) : i64
%v164 = llvm.alloca %v163 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
%v165 = llvm.mlir.constant(1 : i64) : i64
%v166 = llvm.alloca %v165 x !llvm.array<4 x i32> : (i64) -> !llvm.ptr
%v167 = llvm.mlir.constant(1 : i64) : i64
%v168 = llvm.alloca %v167 x !llvm.array<3 x i32> : (i64) -> !llvm.ptr
%v169 = llvm.mlir.constant(1 : i64) : i64
%v170 = llvm.alloca %v169 x i32 : (i64) -> !llvm.ptr
%v171 = arith.constant 4 : i32
%v172 = func.call @make(%v171) : (i32) -> !llvm.struct<(!llvm.ptr, i64)>
%v173 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v174 = llvm.extractvalue %v172[0] : !llvm.struct<(!llvm.ptr, i64)>
%v175 = llvm.insertvalue %v174, %v173[0] : !llvm.struct<(!llvm.ptr, i64)>
%v176 = llvm.extractvalue %v172[1] : !llvm.struct<(!llvm.ptr, i64)>
%v177 = llvm.insertvalue %v176, %v175[1] : !llvm.struct<(!llvm.ptr, i64)>
llvm.store %v177, %v156 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v178 = llvm.load %v156 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
llvm.store %v178, %v158 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v179 = llvm.load %v158 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v180 = arith.constant 2.5 : f64
func.call @fill(%v179, %v180) : (!llvm.struct<(!llvm.ptr, i64)>, f64) -> ()
%v181 = llvm.load %v158 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v182 = llvm.extractvalue %v181[0] : !llvm.struct<(!llvm.ptr, i64)>
%v183 = arith.constant 1 : i32
%v184 = arith.constant 3 : i32
%v185 = arith.extsi %v183 : i32 to i64
%v186 = arith.extsi %v184 : i32 to i64
%v187 = llvm.getelementptr %v182[%v185] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v188 = arith.subi %v186, %v185 : i64
%v189 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v190 = llvm.insertvalue %v187, %v189[0] : !llvm.struct<(!llvm.ptr, i64)>
%v191 = llvm.insertvalue %v188, %v190[1] : !llvm.struct<(!llvm.ptr, i64)>
llvm.store %v191, %v160 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v192 = arith.constant 2 : i32
%v193 = func.call @make(%v192) : (i32) -> !llvm.struct<(!llvm.ptr, i64)>
%v194 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v195 = llvm.extractvalue %v193[0] : !llvm.struct<(!llvm.ptr, i64)>
%v196 = llvm.insertvalue %v195, %v194[0] : !llvm.struct<(!llvm.ptr, i64)>
%v197 = llvm.extractvalue %v193[1] : !llvm.struct<(!llvm.ptr, i64)>
%v198 = llvm.insertvalue %v197, %v196[1] : !llvm.struct<(!llvm.ptr, i64)>
llvm.store %v198, %v162 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v199 = llvm.load %v162 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
llvm.store %v199, %v164 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v200 = llvm.load %v158 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
llvm.store %v200, %v164 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v201 = llvm.load %v160 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v202 = func.call @total(%v201) : (!llvm.struct<(!llvm.ptr, i64)>) -> f64
%v203 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v204 = llvm.call @printf(%v203, %v202) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v205 = arith.constant 0 : i32
%v206 = llvm.load %v164 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v207 = llvm.extractvalue %v206[1] : !llvm.struct<(!llvm.ptr, i64)>
%v208 = llvm.mlir.addressof @str_13 : !llvm.ptr
%v209 = llvm.call @printf(%v208, %v207) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v210 = arith.constant 0 : i32
%v211 = llvm.load %v158 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v212 = llvm.extractvalue %v211[0] : !llvm.struct<(!llvm.ptr, i64)>
%v213 = arith.constant 0 : i32
%v214 = arith.constant 2 : i32
%v215 = arith.extsi %v213 : i32 to i64
%v216 = arith.extsi %v214 : i32 to i64
%v217 = llvm.getelementptr %v212[%v215] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v218 = arith.subi %v216, %v215 : i64
%v219 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v220 = llvm.insertvalue %v217, %v219[0] : !llvm.struct<(!llvm.ptr, i64)>
%v221 = llvm.insertvalue %v218, %v220[1] : !llvm.struct<(!llvm.ptr, i64)>
%v222 = func.call @total(%v221) : (!llvm.struct<(!llvm.ptr, i64)>) -> f64
%v223 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v224 = llvm.call @printf(%v223, %v222) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v225 = arith.constant 0 : i32
%v226 = arith.constant 7 : i32
%v227 = arith.constant 0 : index
%v228 = arith.constant 4 : index
%v229 = arith.constant 1 : index
%v230 = arith.constant 16 : i64
func.call @flow_mem_note_stack(%v230) : (i64) -> ()
scf.for %v231 = %v227 to %v228 step %v229 {
%v232 = arith.index_cast %v231 : index to i64
%v233 = llvm.getelementptr %v166[0, %v232] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x i32>
llvm.store %v226, %v233 : i32, !llvm.ptr
}
%v234 = arith.constant 2 : i32
%v235 = arith.extsi %v234 : i32 to i64
%v236 = llvm.getelementptr %v166[0, %v235] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x i32>
%v237 = llvm.load %v236 : !llvm.ptr -> i32
%v238 = arith.constant 7 : i32
%v239 = arith.constant 0 : index
%v240 = arith.constant 4 : index
%v241 = arith.constant 1 : index
%v242 = memref.alloca() : memref<4xi32>
scf.for %v243 = %v239 to %v240 step %v241 {
memref.store %v238, %v242[%v243] : memref<4xi32>
}
%v244 = memref.extract_aligned_pointer_as_index %v242 : memref<4xi32> -> index
%v245 = arith.index_cast %v244 : index to i64
%v246 = llvm.inttoptr %v245 : i64 to !llvm.ptr
%v247 = arith.constant 0 : index
%v248 = memref.dim %v242, %v247 : memref<4xi32>
%v249 = arith.index_cast %v248 : index to i64
%v250 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v251 = llvm.insertvalue %v246, %v250[0] : !llvm.struct<(!llvm.ptr, i64)>
%v252 = llvm.insertvalue %v249, %v251[1] : !llvm.struct<(!llvm.ptr, i64)>
%v253 = func.call @first4(%v252) : (!llvm.struct<(!llvm.ptr, i64)>) -> i32
%v254 = arith.addi %v237, %v253 : i32
%v255 = llvm.mlir.addressof @str_14 : !llvm.ptr
%v256 = llvm.call @printf(%v255, %v254) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v257 = arith.constant 0 : i32
%v258 = arith.constant 8 : i32
%v259 = arith.index_cast %v258 : i32 to index
%v260 = memref.alloc(%v259) : memref<?xf32>
%v261 = arith.constant 0.0 : f32
%v262 = arith.constant 0 : index
%v263 = arith.constant 1 : index
scf.for %v264 = %v262 to %v259 step %v263 {
memref.store %v261, %v260[%v264] : memref<?xf32>
}
%v265 = arith.constant 8 : i32
%v266 = arith.index_cast %v265 : i32 to index
%v267 = memref.alloc(%v266) : memref<?xf32>
%v268 = arith.constant 0.0 : f32
%v269 = arith.constant 0 : index
%v270 = arith.constant 1 : index
scf.for %v271 = %v269 to %v266 step %v270 {
memref.store %v268, %v267[%v271] : memref<?xf32>
}
%v272 = arith.constant 0 : i32
%v273 = arith.constant 8 : i32
%v274 = arith.index_cast %v272 : i32 to index
%v275 = arith.index_cast %v273 : i32 to index
%v276 = arith.constant 1 : index
%v277 = arith.constant -1 : index
%v278 = arith.cmpi sle, %v274, %v275 : index
%v279 = arith.select %v278, %v276, %v277 : index
cf.br ^b10(%v274 : index)
^b10(%v280: index):
%v281 = arith.cmpi slt, %v280, %v275 : index
%v282 = arith.cmpi sgt, %v280, %v275 : index
%v283 = arith.select %v278, %v281, %v282 : i1
cf.cond_br %v283, ^b11(%v280 : index), ^b12(%v280 : index)
^b11(%v284: index):
%v285 = arith.constant 1.5 : f64
%v286 = arith.truncf %v285 : f64 to f32
memref.store %v286, %v267[%v284] : memref<?xf32>
%v287 = arith.constant 2.0 : f64
%v288 = arith.truncf %v287 : f64 to f32
memref.store %v288, %v260[%v284] : memref<?xf32>
%v289 = arith.addi %v284, %v279 : index
cf.br ^b10(%v289 : index)
^b12(%v290: index):
%v291 = arith.constant 8 : i32
%v292 = arith.constant 0.5 : f64
%v293 = arith.truncf %v292 : f64 to f32
func.call @scale(%v260, %v267, %v291, %v293) : (memref<?xf32>, memref<?xf32>, i32, f32) -> ()
%v294 = arith.constant 3 : i32
%v295 = arith.index_cast %v294 : i32 to index
%v296 = memref.load %v260[%v295] : memref<?xf32>
%v297 = arith.extf %v296 : f32 to f64
%v298 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v299 = llvm.call @printf(%v298, %v297) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v300 = arith.constant 0 : i32
%v301 = arith.constant 1.0 : f64
%v302 = arith.constant 2.0 : f64
%v303 = arith.constant 3.0 : f64
%v304 = arith.truncf %v301 : f64 to f32
%v305 = arith.truncf %v302 : f64 to f32
%v306 = arith.truncf %v303 : f64 to f32
%v307 = memref.alloca() : memref<3xf32>
%v308 = arith.constant 0 : index
memref.store %v304, %v307[%v308] : memref<3xf32>
%v309 = arith.constant 1 : index
memref.store %v305, %v307[%v309] : memref<3xf32>
%v310 = arith.constant 2 : index
memref.store %v306, %v307[%v310] : memref<3xf32>
%v311 = arith.constant 4.0 : f64
%v312 = arith.constant 5.0 : f64
%v313 = arith.constant 6.0 : f64
%v314 = arith.truncf %v311 : f64 to f32
%v315 = arith.truncf %v312 : f64 to f32
%v316 = arith.truncf %v313 : f64 to f32
%v317 = memref.alloca() : memref<3xf32>
%v318 = arith.constant 0 : index
memref.store %v314, %v317[%v318] : memref<3xf32>
%v319 = arith.constant 1 : index
memref.store %v315, %v317[%v319] : memref<3xf32>
%v320 = arith.constant 2 : index
memref.store %v316, %v317[%v320] : memref<3xf32>
%v321 = arith.constant 3 : i32
%v322 = memref.cast %v307 : memref<3xf32> to memref<?xf32>
%v323 = memref.cast %v317 : memref<3xf32> to memref<?xf32>
%v324 = func.call @dot(%v322, %v323, %v321) : (memref<?xf32>, memref<?xf32>, i32) -> f32
%v325 = arith.extf %v324 : f32 to f64
%v326 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v327 = llvm.call @printf(%v326, %v325) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v328 = arith.constant 0 : i32
%v329 = arith.constant 1 : i32
%v330 = arith.constant 2 : i32
%v331 = arith.constant 3 : i32
%v332 = arith.constant 12 : i64
func.call @flow_mem_note_stack(%v332) : (i64) -> ()
%v333 = llvm.mlir.zero : !llvm.array<3 x i32>
llvm.store %v333, %v168 : !llvm.array<3 x i32>, !llvm.ptr
%v334 = llvm.mlir.constant(0 : i64) : i64
%v335 = llvm.getelementptr %v168[0, %v334] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v329, %v335 : i32, !llvm.ptr
%v336 = llvm.mlir.constant(1 : i64) : i64
%v337 = llvm.getelementptr %v168[0, %v336] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v330, %v337 : i32, !llvm.ptr
%v338 = llvm.mlir.constant(2 : i64) : i64
%v339 = llvm.getelementptr %v168[0, %v338] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v331, %v339 : i32, !llvm.ptr
%v340 = arith.constant 0 : i32
llvm.store %v340, %v170 : i32, !llvm.ptr
%v341 = arith.constant 0 : i32
%v342 = arith.extsi %v341 : i32 to i64
%v343 = llvm.getelementptr %v168[0, %v342] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
%v344 = llvm.load %v343 : !llvm.ptr -> i32
%v345 = arith.constant 1 : i32
%v346 = arith.cmpi eq, %v344, %v345 : i32
%v347 = arith.constant 1 : i32
%v348 = arith.extsi %v347 : i32 to i64
%v349 = llvm.getelementptr %v168[0, %v348] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
%v350 = llvm.load %v349 : !llvm.ptr -> i32
%v351 = arith.constant 2 : i32
%v352 = arith.extsi %v351 : i32 to i64
%v353 = llvm.getelementptr %v168[0, %v352] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
%v354 = llvm.load %v353 : !llvm.ptr -> i32
cf.cond_br %v346, ^b13, ^b14
^b13:
%v355 = arith.addi %v350, %v354 : i32
llvm.store %v355, %v170 : i32, !llvm.ptr
cf.br ^b15
^b14:
%v356 = arith.constant 99 : i32
llvm.store %v356, %v170 : i32, !llvm.ptr
cf.br ^b15
^b15:
%v357 = llvm.load %v170 : !llvm.ptr -> i32
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
