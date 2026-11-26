module {
func.func private @strlen(!llvm.ptr) -> i64
func.func private @memcpy(!llvm.ptr, !llvm.ptr, i64) -> !llvm.ptr
func.func private @write(i32, !llvm.ptr, i64) -> i64
func.func private @abort() -> ()
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
%name = llvm.mlir.addressof @str_3 : !llvm.ptr
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
%hdr = llvm.mlir.addressof @str_4 : !llvm.ptr
%h = llvm.call @printf(%hdr) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%g_flow_mem_alloc_count = llvm.mlir.addressof @flow_mem_alloc_count : !llvm.ptr
%v_flow_mem_alloc_count = llvm.load %g_flow_mem_alloc_count : !llvm.ptr -> i64
%f_flow_mem_alloc_count = llvm.mlir.addressof @str_5 : !llvm.ptr
%w_flow_mem_alloc_count = llvm.call @printf(%f_flow_mem_alloc_count, %v_flow_mem_alloc_count) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_alloc_bytes = llvm.mlir.addressof @flow_mem_alloc_bytes : !llvm.ptr
%v_flow_mem_alloc_bytes = llvm.load %g_flow_mem_alloc_bytes : !llvm.ptr -> i64
%f_flow_mem_alloc_bytes = llvm.mlir.addressof @str_6 : !llvm.ptr
%w_flow_mem_alloc_bytes = llvm.call @printf(%f_flow_mem_alloc_bytes, %v_flow_mem_alloc_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_peak_live = llvm.mlir.addressof @flow_mem_peak_live : !llvm.ptr
%v_flow_mem_peak_live = llvm.load %g_flow_mem_peak_live : !llvm.ptr -> i64
%f_flow_mem_peak_live = llvm.mlir.addressof @str_7 : !llvm.ptr
%w_flow_mem_peak_live = llvm.call @printf(%f_flow_mem_peak_live, %v_flow_mem_peak_live) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_temp_bytes = llvm.mlir.addressof @flow_mem_temp_bytes : !llvm.ptr
%v_flow_mem_temp_bytes = llvm.load %g_flow_mem_temp_bytes : !llvm.ptr -> i64
%f_flow_mem_temp_bytes = llvm.mlir.addressof @str_8 : !llvm.ptr
%w_flow_mem_temp_bytes = llvm.call @printf(%f_flow_mem_temp_bytes, %v_flow_mem_temp_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_copy_bytes = llvm.mlir.addressof @flow_mem_copy_bytes : !llvm.ptr
%v_flow_mem_copy_bytes = llvm.load %g_flow_mem_copy_bytes : !llvm.ptr -> i64
%f_flow_mem_copy_bytes = llvm.mlir.addressof @str_9 : !llvm.ptr
%w_flow_mem_copy_bytes = llvm.call @printf(%f_flow_mem_copy_bytes, %v_flow_mem_copy_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_stack_bytes = llvm.mlir.addressof @flow_mem_stack_bytes : !llvm.ptr
%v_flow_mem_stack_bytes = llvm.load %g_flow_mem_stack_bytes : !llvm.ptr -> i64
%f_flow_mem_stack_bytes = llvm.mlir.addressof @str_10 : !llvm.ptr
%w_flow_mem_stack_bytes = llvm.call @printf(%f_flow_mem_stack_bytes, %v_flow_mem_stack_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_arena_bytes = llvm.mlir.addressof @flow_mem_arena_bytes : !llvm.ptr
%v_flow_mem_arena_bytes = llvm.load %g_flow_mem_arena_bytes : !llvm.ptr -> i64
%f_flow_mem_arena_bytes = llvm.mlir.addressof @str_11 : !llvm.ptr
%w_flow_mem_arena_bytes = llvm.call @printf(%f_flow_mem_arena_bytes, %v_flow_mem_arena_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%sp = llvm.mlir.addressof @flow_mem_stack_bytes : !llvm.ptr
%sv = llvm.load %sp : !llvm.ptr -> i64
%ap = llvm.mlir.addressof @flow_mem_arena_bytes : !llvm.ptr
%av = llvm.load %ap : !llvm.ptr -> i64
%promo = arith.addi %sv, %av : i64
%pf = llvm.mlir.addressof @str_12 : !llvm.ptr
%ph = llvm.call @printf(%pf, %promo) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_map_overflow = llvm.mlir.addressof @flow_mem_map_overflow : !llvm.ptr
%v_flow_mem_map_overflow = llvm.load %g_flow_mem_map_overflow : !llvm.ptr -> i64
%f_flow_mem_map_overflow = llvm.mlir.addressof @str_13 : !llvm.ptr
%w_flow_mem_map_overflow = llvm.call @printf(%f_flow_mem_map_overflow, %v_flow_mem_map_overflow) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_site_concat = llvm.mlir.addressof @flow_mem_site_concat : !llvm.ptr
%v_flow_mem_site_concat = llvm.load %g_flow_mem_site_concat : !llvm.ptr -> i64
%f_flow_mem_site_concat = llvm.mlir.addressof @str_14 : !llvm.ptr
%w_flow_mem_site_concat = llvm.call @printf(%f_flow_mem_site_concat, %v_flow_mem_site_concat) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
scf.yield
}
func.return
}
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("flow: \00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
llvm.mlir.global internal constant @str_1("\0A\00") {addr_space = 0 : i32} : !llvm.array<2 x i8>
llvm.mlir.global internal constant @str_2("span index out of bounds\00") {addr_space = 0 : i32} : !llvm.array<25 x i8>
llvm.mlir.global internal constant @str_3("FLOW_MEM_PROFILE\00") {addr_space = 0 : i32} : !llvm.array<17 x i8>
llvm.mlir.global internal constant @str_4("\0A=== Flow memory profile (#740) ===\0A\00") {addr_space = 0 : i32} : !llvm.array<37 x i8>
llvm.mlir.global internal constant @str_5("allocations: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<19 x i8>
llvm.mlir.global internal constant @str_6("heap_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<18 x i8>
llvm.mlir.global internal constant @str_7("peak_live_heap: %lld\0A\00") {addr_space = 0 : i32} : !llvm.array<22 x i8>
llvm.mlir.global internal constant @str_8("temp_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<18 x i8>
llvm.mlir.global internal constant @str_9("copies: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<14 x i8>
llvm.mlir.global internal constant @str_10("stack_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<19 x i8>
llvm.mlir.global internal constant @str_11("arena_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<19 x i8>
llvm.mlir.global internal constant @str_12("promotion_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<23 x i8>
llvm.mlir.global internal constant @str_13("live_map_overflow: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<25 x i8>
llvm.mlir.global internal constant @str_14("site_concat: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<19 x i8>
llvm.mlir.global internal constant @str_15("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_16("%lld\0A\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
llvm.mlir.global internal constant @str_17("array index out of bounds\00") {addr_space = 0 : i32} : !llvm.array<26 x i8>
llvm.mlir.global internal constant @str_18("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
func.func private @__flow_fault(%arg0: !llvm.ptr) {
%fd = arith.constant 2 : i32
%pre = llvm.mlir.addressof @str_0 : !llvm.ptr
%n6 = arith.constant 6 : i64
%w0 = func.call @write(%fd, %pre, %n6) : (i32, !llvm.ptr, i64) -> i64
%n = func.call @strlen(%arg0) : (!llvm.ptr) -> i64
%w1 = func.call @write(%fd, %arg0, %n) : (i32, !llvm.ptr, i64) -> i64
%nl = llvm.mlir.addressof @str_1 : !llvm.ptr
%n1 = arith.constant 1 : i64
%w2 = func.call @write(%fd, %nl, %n1) : (i32, !llvm.ptr, i64) -> i64
func.call @abort() : () -> ()
func.return
}
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
%v22 = llvm.extractvalue %v20[1] : !llvm.struct<(!llvm.ptr, i64)>
%v23 = arith.extsi %v21 : i32 to i64
%v24 = arith.cmpi sge, %v23, %v22 : i64
scf.if %v24 {
%v25 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v25) : (!llvm.ptr) -> ()
}
%v26 = llvm.extractvalue %v20[0] : !llvm.struct<(!llvm.ptr, i64)>
%v27 = arith.extsi %v21 : i32 to i64
%v28 = llvm.getelementptr %v26[%v27] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v29 = llvm.load %v28 : !llvm.ptr -> f64
%v30 = arith.addf %v19, %v29 : f64
llvm.store %v30, %v4 : f64, !llvm.ptr
%v31 = llvm.load %v6 : !llvm.ptr -> i32
%v32 = arith.constant 1 : i32
%v33 = arith.addi %v31, %v32 : i32
llvm.store %v33, %v6 : i32, !llvm.ptr
cf.br ^b1
^b3:
%v34 = llvm.load %v4 : !llvm.ptr -> f64
func.return %v34 : f64
}
func.func @fill(%arg0: !llvm.struct<(!llvm.ptr, i64)>, %arg1: f64) -> () {
%v35 = llvm.mlir.constant(1 : i64) : i64
%v36 = llvm.alloca %v35 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
%v37 = llvm.mlir.constant(1 : i64) : i64
%v38 = llvm.alloca %v37 x i64 : (i64) -> !llvm.ptr
%v39 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v40 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i64)>
%v41 = llvm.insertvalue %v40, %v39[0] : !llvm.struct<(!llvm.ptr, i64)>
%v42 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i64)>
%v43 = llvm.insertvalue %v42, %v41[1] : !llvm.struct<(!llvm.ptr, i64)>
llvm.store %v43, %v36 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v44 = arith.constant 0 : i32
%v45 = arith.extsi %v44 : i32 to i64
llvm.store %v45, %v38 : i64, !llvm.ptr
cf.br ^b4
^b4:
%v46 = llvm.load %v38 : !llvm.ptr -> i64
%v47 = llvm.load %v36 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v48 = llvm.extractvalue %v47[1] : !llvm.struct<(!llvm.ptr, i64)>
%v49 = arith.cmpi slt, %v46, %v48 : i64
cf.cond_br %v49, ^b5, ^b6
^b5:
%v50 = llvm.load %v36 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v51 = llvm.load %v38 : !llvm.ptr -> i64
%v52 = llvm.extractvalue %v50[0] : !llvm.struct<(!llvm.ptr, i64)>
%v53 = llvm.getelementptr %v52[%v51] : (!llvm.ptr, i64) -> !llvm.ptr, f64
llvm.store %arg1, %v53 : f64, !llvm.ptr
%v54 = llvm.load %v38 : !llvm.ptr -> i64
%v55 = arith.constant 1 : i32
%v56 = arith.extsi %v55 : i32 to i64
%v57 = arith.addi %v54, %v56 : i64
llvm.store %v57, %v38 : i64, !llvm.ptr
cf.br ^b4
^b6:
func.return
}
func.func @make(%arg0: i32) -> !llvm.struct<(!llvm.ptr, i64)> {
%v58 = llvm.mlir.constant(1 : i64) : i64
%v59 = llvm.alloca %v58 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
%v60 = arith.extsi %arg0 : i32 to i64
%v61 = arith.constant 8 : i32
%v62 = arith.extsi %v61 : i32 to i64
%v63 = arith.muli %v60, %v62 : i64
%v64 = func.call @flow_mem_malloc(%v63) : (i64) -> !llvm.ptr
%v65 = arith.constant 0 : i32
%v66 = arith.extsi %v65 : i32 to i64
%v67 = arith.extsi %arg0 : i32 to i64
%v68 = llvm.getelementptr %v64[%v66] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v69 = arith.subi %v67, %v66 : i64
%v70 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v71 = llvm.insertvalue %v68, %v70[0] : !llvm.struct<(!llvm.ptr, i64)>
%v72 = llvm.insertvalue %v69, %v71[1] : !llvm.struct<(!llvm.ptr, i64)>
%v73 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v74 = llvm.extractvalue %v72[0] : !llvm.struct<(!llvm.ptr, i64)>
%v75 = llvm.insertvalue %v74, %v73[0] : !llvm.struct<(!llvm.ptr, i64)>
%v76 = llvm.extractvalue %v72[1] : !llvm.struct<(!llvm.ptr, i64)>
%v77 = llvm.insertvalue %v76, %v75[1] : !llvm.struct<(!llvm.ptr, i64)>
llvm.store %v77, %v59 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v78 = llvm.load %v59 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
func.return %v78 : !llvm.struct<(!llvm.ptr, i64)>
}
func.func @first4(%arg0: !llvm.struct<(!llvm.ptr, i64)>) -> i32 {
%v79 = llvm.mlir.constant(1 : i64) : i64
%v80 = llvm.alloca %v79 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
%v81 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v82 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i64)>
%v83 = llvm.insertvalue %v82, %v81[0] : !llvm.struct<(!llvm.ptr, i64)>
%v84 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i64)>
%v85 = llvm.insertvalue %v84, %v83[1] : !llvm.struct<(!llvm.ptr, i64)>
llvm.store %v85, %v80 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v86 = llvm.load %v80 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v87 = arith.constant 0 : i32
%v88 = llvm.extractvalue %v86[1] : !llvm.struct<(!llvm.ptr, i64)>
%v89 = arith.extsi %v87 : i32 to i64
%v90 = arith.cmpi sge, %v89, %v88 : i64
scf.if %v90 {
%v91 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v91) : (!llvm.ptr) -> ()
}
%v92 = llvm.extractvalue %v86[0] : !llvm.struct<(!llvm.ptr, i64)>
%v93 = arith.extsi %v87 : i32 to i64
%v94 = llvm.getelementptr %v92[%v93] : (!llvm.ptr, i64) -> !llvm.ptr, i32
%v95 = llvm.load %v94 : !llvm.ptr -> i32
%v96 = llvm.load %v80 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v97 = arith.constant 3 : i32
%v98 = llvm.extractvalue %v96[1] : !llvm.struct<(!llvm.ptr, i64)>
%v99 = arith.extsi %v97 : i32 to i64
%v100 = arith.cmpi sge, %v99, %v98 : i64
scf.if %v100 {
%v101 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v101) : (!llvm.ptr) -> ()
}
%v102 = llvm.extractvalue %v96[0] : !llvm.struct<(!llvm.ptr, i64)>
%v103 = arith.extsi %v97 : i32 to i64
%v104 = llvm.getelementptr %v102[%v103] : (!llvm.ptr, i64) -> !llvm.ptr, i32
%v105 = llvm.load %v104 : !llvm.ptr -> i32
%v106 = arith.addi %v95, %v105 : i32
func.return %v106 : i32
}
func.func @scale(%arg0: memref<?xf32>, %arg1: memref<?xf32>, %arg2: i32, %arg3: f32) -> () {
// flow: vectorized elementwise f32 loop (VF=4)
%v107 = arith.constant 0 : i32
%v108 = arith.index_cast %v107 : i32 to index
%v109 = arith.index_cast %arg2 : i32 to index
%v110 = arith.constant 1 : index
%v111 = arith.constant 4 : index
%v112 = arith.subi %v109, %v108 : index
%v113 = arith.remsi %v112, %v111 : index
%v114 = arith.subi %v112, %v113 : index
%v115 = arith.addi %v108, %v114 : index
scf.for %v116 = %v108 to %v115 step %v111 {
%v117 = arith.constant 0.0 : f32
%v118 = vector.transfer_read %arg1[%v116], %v117 {in_bounds = [true]} : memref<?xf32>, vector<4xf32>
%v119 = arith.negf %v118 : vector<4xf32>
%v120 = vector.broadcast %arg3 : f32 to vector<4xf32>
%v121 = arith.mulf %v119, %v120 : vector<4xf32>
%v122 = arith.constant 2.0 : f32
%v123 = vector.broadcast %v122 : f32 to vector<4xf32>
%v124 = arith.addf %v121, %v123 : vector<4xf32>
%v125 = arith.constant 0.0 : f32
%v126 = vector.transfer_read %arg0[%v116], %v125 {in_bounds = [true]} : memref<?xf32>, vector<4xf32>
%v127 = arith.constant 4.0 : f32
%v128 = vector.broadcast %v127 : f32 to vector<4xf32>
%v129 = arith.divf %v126, %v128 : vector<4xf32>
%v130 = arith.subf %v124, %v129 : vector<4xf32>
vector.transfer_write %v130, %arg0[%v116] {in_bounds = [true]} : vector<4xf32>, memref<?xf32>
}
scf.for %v131 = %v115 to %v109 step %v110 {
%v132 = memref.load %arg1[%v131] : memref<?xf32>
%v133 = arith.negf %v132 : f32
%v134 = arith.mulf %v133, %arg3 : f32
%v135 = arith.constant 2.0 : f64
%v136 = arith.extf %v134 : f32 to f64
%v137 = arith.addf %v136, %v135 : f64
%v138 = memref.load %arg0[%v131] : memref<?xf32>
%v139 = arith.constant 4.0 : f64
%v140 = arith.extf %v138 : f32 to f64
%v141 = arith.divf %v140, %v139 : f64
%v142 = arith.subf %v137, %v141 : f64
%v143 = arith.truncf %v142 : f64 to f32
memref.store %v143, %arg0[%v131] : memref<?xf32>
}
func.return
}
func.func @dot(%arg0: memref<?xf32>, %arg1: memref<?xf32>, %arg2: i32) -> f32 {
%v144 = llvm.mlir.constant(1 : i64) : i64
%v145 = llvm.alloca %v144 x f32 : (i64) -> !llvm.ptr
%v146 = arith.constant 0.0 : f64
%v147 = arith.truncf %v146 : f64 to f32
llvm.store %v147, %v145 : f32, !llvm.ptr
%v148 = arith.constant 0 : i32
%v149 = arith.index_cast %v148 : i32 to index
%v150 = arith.index_cast %arg2 : i32 to index
%v151 = arith.constant 1 : index
%v152 = arith.constant -1 : index
%v153 = arith.cmpi sle, %v149, %v150 : index
%v154 = arith.select %v153, %v151, %v152 : index
cf.br ^b7(%v149 : index)
^b7(%v155: index):
%v156 = arith.cmpi slt, %v155, %v150 : index
%v157 = arith.cmpi sgt, %v155, %v150 : index
%v158 = arith.select %v153, %v156, %v157 : i1
cf.cond_br %v158, ^b8(%v155 : index), ^b9(%v155 : index)
^b8(%v159: index):
%v160 = llvm.load %v145 : !llvm.ptr -> f32
%v161 = memref.load %arg0[%v159] : memref<?xf32>
%v162 = memref.load %arg1[%v159] : memref<?xf32>
%v163 = llvm.intr.fmuladd(%v161, %v162, %v160) : (f32, f32, f32) -> f32
llvm.store %v163, %v145 : f32, !llvm.ptr
%v164 = arith.addi %v159, %v154 : index
cf.br ^b7(%v164 : index)
^b9(%v165: index):
%v166 = llvm.load %v145 : !llvm.ptr -> f32
func.return %v166 : f32
}
func.func @main() -> i32 {
%v167 = llvm.mlir.constant(1 : i64) : i64
%v168 = llvm.alloca %v167 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
%v169 = llvm.mlir.constant(1 : i64) : i64
%v170 = llvm.alloca %v169 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
%v171 = llvm.mlir.constant(1 : i64) : i64
%v172 = llvm.alloca %v171 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
%v173 = llvm.mlir.constant(1 : i64) : i64
%v174 = llvm.alloca %v173 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
%v175 = llvm.mlir.constant(1 : i64) : i64
%v176 = llvm.alloca %v175 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
%v177 = llvm.mlir.constant(1 : i64) : i64
%v178 = llvm.alloca %v177 x !llvm.array<4 x i32> : (i64) -> !llvm.ptr
%v179 = llvm.mlir.constant(1 : i64) : i64
%v180 = llvm.alloca %v179 x !llvm.array<3 x i32> : (i64) -> !llvm.ptr
%v181 = llvm.mlir.constant(1 : i64) : i64
%v182 = llvm.alloca %v181 x i32 : (i64) -> !llvm.ptr
%v183 = arith.constant 4 : i32
%v184 = func.call @make(%v183) : (i32) -> !llvm.struct<(!llvm.ptr, i64)>
%v185 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v186 = llvm.extractvalue %v184[0] : !llvm.struct<(!llvm.ptr, i64)>
%v187 = llvm.insertvalue %v186, %v185[0] : !llvm.struct<(!llvm.ptr, i64)>
%v188 = llvm.extractvalue %v184[1] : !llvm.struct<(!llvm.ptr, i64)>
%v189 = llvm.insertvalue %v188, %v187[1] : !llvm.struct<(!llvm.ptr, i64)>
llvm.store %v189, %v168 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v190 = llvm.load %v168 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
llvm.store %v190, %v170 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v191 = llvm.load %v170 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v192 = arith.constant 2.5 : f64
func.call @fill(%v191, %v192) : (!llvm.struct<(!llvm.ptr, i64)>, f64) -> ()
%v193 = llvm.load %v170 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v194 = llvm.extractvalue %v193[0] : !llvm.struct<(!llvm.ptr, i64)>
%v195 = arith.constant 1 : i32
%v196 = arith.constant 3 : i32
%v197 = arith.extsi %v195 : i32 to i64
%v198 = arith.extsi %v196 : i32 to i64
%v199 = llvm.getelementptr %v194[%v197] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v200 = arith.subi %v198, %v197 : i64
%v201 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v202 = llvm.insertvalue %v199, %v201[0] : !llvm.struct<(!llvm.ptr, i64)>
%v203 = llvm.insertvalue %v200, %v202[1] : !llvm.struct<(!llvm.ptr, i64)>
llvm.store %v203, %v172 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v204 = arith.constant 2 : i32
%v205 = func.call @make(%v204) : (i32) -> !llvm.struct<(!llvm.ptr, i64)>
%v206 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v207 = llvm.extractvalue %v205[0] : !llvm.struct<(!llvm.ptr, i64)>
%v208 = llvm.insertvalue %v207, %v206[0] : !llvm.struct<(!llvm.ptr, i64)>
%v209 = llvm.extractvalue %v205[1] : !llvm.struct<(!llvm.ptr, i64)>
%v210 = llvm.insertvalue %v209, %v208[1] : !llvm.struct<(!llvm.ptr, i64)>
llvm.store %v210, %v174 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v211 = llvm.load %v174 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
llvm.store %v211, %v176 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v212 = llvm.load %v170 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
llvm.store %v212, %v176 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v213 = llvm.load %v172 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v214 = func.call @total(%v213) : (!llvm.struct<(!llvm.ptr, i64)>) -> f64
%v215 = llvm.mlir.addressof @str_15 : !llvm.ptr
%v216 = llvm.call @printf(%v215, %v214) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v217 = arith.constant 0 : i32
%v218 = llvm.load %v176 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v219 = llvm.extractvalue %v218[1] : !llvm.struct<(!llvm.ptr, i64)>
%v220 = llvm.mlir.addressof @str_16 : !llvm.ptr
%v221 = llvm.call @printf(%v220, %v219) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v222 = arith.constant 0 : i32
%v223 = llvm.load %v170 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v224 = llvm.extractvalue %v223[0] : !llvm.struct<(!llvm.ptr, i64)>
%v225 = arith.constant 0 : i32
%v226 = arith.constant 2 : i32
%v227 = arith.extsi %v225 : i32 to i64
%v228 = arith.extsi %v226 : i32 to i64
%v229 = llvm.getelementptr %v224[%v227] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v230 = arith.subi %v228, %v227 : i64
%v231 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v232 = llvm.insertvalue %v229, %v231[0] : !llvm.struct<(!llvm.ptr, i64)>
%v233 = llvm.insertvalue %v230, %v232[1] : !llvm.struct<(!llvm.ptr, i64)>
%v234 = func.call @total(%v233) : (!llvm.struct<(!llvm.ptr, i64)>) -> f64
%v235 = llvm.mlir.addressof @str_15 : !llvm.ptr
%v236 = llvm.call @printf(%v235, %v234) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v237 = arith.constant 0 : i32
%v238 = arith.constant 7 : i32
%v239 = arith.constant 0 : index
%v240 = arith.constant 4 : index
%v241 = arith.constant 1 : index
%v242 = arith.constant 16 : i64
func.call @flow_mem_note_stack(%v242) : (i64) -> ()
scf.for %v243 = %v239 to %v240 step %v241 {
%v244 = arith.index_cast %v243 : index to i64
%v245 = llvm.getelementptr %v178[0, %v244] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x i32>
llvm.store %v238, %v245 : i32, !llvm.ptr
}
%v246 = arith.constant 2 : i32
%v247 = arith.constant 4 : i32
%v248 = arith.cmpi uge, %v246, %v247 : i32
scf.if %v248 {
%v249 = llvm.mlir.addressof @str_17 : !llvm.ptr
func.call @__flow_fault(%v249) : (!llvm.ptr) -> ()
}
%v250 = arith.extsi %v246 : i32 to i64
%v251 = llvm.getelementptr %v178[0, %v250] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x i32>
%v252 = llvm.load %v251 : !llvm.ptr -> i32
%v253 = arith.constant 7 : i32
%v254 = arith.constant 0 : index
%v255 = arith.constant 4 : index
%v256 = arith.constant 1 : index
%v257 = memref.alloca() : memref<4xi32>
scf.for %v258 = %v254 to %v255 step %v256 {
memref.store %v253, %v257[%v258] : memref<4xi32>
}
%v259 = memref.extract_aligned_pointer_as_index %v257 : memref<4xi32> -> index
%v260 = arith.index_cast %v259 : index to i64
%v261 = llvm.inttoptr %v260 : i64 to !llvm.ptr
%v262 = arith.constant 0 : index
%v263 = memref.dim %v257, %v262 : memref<4xi32>
%v264 = arith.index_cast %v263 : index to i64
%v265 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v266 = llvm.insertvalue %v261, %v265[0] : !llvm.struct<(!llvm.ptr, i64)>
%v267 = llvm.insertvalue %v264, %v266[1] : !llvm.struct<(!llvm.ptr, i64)>
%v268 = func.call @first4(%v267) : (!llvm.struct<(!llvm.ptr, i64)>) -> i32
%v269 = arith.addi %v252, %v268 : i32
%v270 = llvm.mlir.addressof @str_18 : !llvm.ptr
%v271 = llvm.call @printf(%v270, %v269) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v272 = arith.constant 0 : i32
%v273 = arith.constant 8 : i32
%v274 = arith.index_cast %v273 : i32 to index
%v275 = memref.alloc(%v274) : memref<?xf32>
%v276 = arith.constant 0.0 : f32
%v277 = arith.constant 0 : index
%v278 = arith.constant 1 : index
scf.for %v279 = %v277 to %v274 step %v278 {
memref.store %v276, %v275[%v279] : memref<?xf32>
}
%v280 = arith.constant 8 : i32
%v281 = arith.index_cast %v280 : i32 to index
%v282 = memref.alloc(%v281) : memref<?xf32>
%v283 = arith.constant 0.0 : f32
%v284 = arith.constant 0 : index
%v285 = arith.constant 1 : index
scf.for %v286 = %v284 to %v281 step %v285 {
memref.store %v283, %v282[%v286] : memref<?xf32>
}
%v287 = arith.constant 0 : i32
%v288 = arith.constant 8 : i32
%v289 = arith.index_cast %v287 : i32 to index
%v290 = arith.index_cast %v288 : i32 to index
%v291 = arith.constant 1 : index
%v292 = arith.constant -1 : index
%v293 = arith.cmpi sle, %v289, %v290 : index
%v294 = arith.select %v293, %v291, %v292 : index
cf.br ^b10(%v289 : index)
^b10(%v295: index):
%v296 = arith.cmpi slt, %v295, %v290 : index
%v297 = arith.cmpi sgt, %v295, %v290 : index
%v298 = arith.select %v293, %v296, %v297 : i1
cf.cond_br %v298, ^b11(%v295 : index), ^b12(%v295 : index)
^b11(%v299: index):
%v300 = arith.constant 1.5 : f64
%v301 = arith.truncf %v300 : f64 to f32
memref.store %v301, %v282[%v299] : memref<?xf32>
%v302 = arith.constant 2.0 : f64
%v303 = arith.truncf %v302 : f64 to f32
memref.store %v303, %v275[%v299] : memref<?xf32>
%v304 = arith.addi %v299, %v294 : index
cf.br ^b10(%v304 : index)
^b12(%v305: index):
%v306 = arith.constant 8 : i32
%v307 = arith.constant 0.5 : f64
%v308 = arith.truncf %v307 : f64 to f32
func.call @scale(%v275, %v282, %v306, %v308) : (memref<?xf32>, memref<?xf32>, i32, f32) -> ()
%v309 = arith.constant 3 : i32
%v310 = arith.index_cast %v309 : i32 to index
%v311 = memref.load %v275[%v310] : memref<?xf32>
%v312 = arith.extf %v311 : f32 to f64
%v313 = llvm.mlir.addressof @str_15 : !llvm.ptr
%v314 = llvm.call @printf(%v313, %v312) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v315 = arith.constant 0 : i32
%v316 = arith.constant 1.0 : f64
%v317 = arith.constant 2.0 : f64
%v318 = arith.constant 3.0 : f64
%v319 = arith.truncf %v316 : f64 to f32
%v320 = arith.truncf %v317 : f64 to f32
%v321 = arith.truncf %v318 : f64 to f32
%v322 = memref.alloca() : memref<3xf32>
%v323 = arith.constant 0 : index
memref.store %v319, %v322[%v323] : memref<3xf32>
%v324 = arith.constant 1 : index
memref.store %v320, %v322[%v324] : memref<3xf32>
%v325 = arith.constant 2 : index
memref.store %v321, %v322[%v325] : memref<3xf32>
%v326 = arith.constant 4.0 : f64
%v327 = arith.constant 5.0 : f64
%v328 = arith.constant 6.0 : f64
%v329 = arith.truncf %v326 : f64 to f32
%v330 = arith.truncf %v327 : f64 to f32
%v331 = arith.truncf %v328 : f64 to f32
%v332 = memref.alloca() : memref<3xf32>
%v333 = arith.constant 0 : index
memref.store %v329, %v332[%v333] : memref<3xf32>
%v334 = arith.constant 1 : index
memref.store %v330, %v332[%v334] : memref<3xf32>
%v335 = arith.constant 2 : index
memref.store %v331, %v332[%v335] : memref<3xf32>
%v336 = arith.constant 3 : i32
%v337 = memref.cast %v322 : memref<3xf32> to memref<?xf32>
%v338 = memref.cast %v332 : memref<3xf32> to memref<?xf32>
%v339 = func.call @dot(%v337, %v338, %v336) : (memref<?xf32>, memref<?xf32>, i32) -> f32
%v340 = arith.extf %v339 : f32 to f64
%v341 = llvm.mlir.addressof @str_15 : !llvm.ptr
%v342 = llvm.call @printf(%v341, %v340) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v343 = arith.constant 0 : i32
%v344 = arith.constant 1 : i32
%v345 = arith.constant 2 : i32
%v346 = arith.constant 3 : i32
%v347 = arith.constant 12 : i64
func.call @flow_mem_note_stack(%v347) : (i64) -> ()
%v348 = llvm.mlir.zero : !llvm.array<3 x i32>
llvm.store %v348, %v180 : !llvm.array<3 x i32>, !llvm.ptr
%v349 = llvm.mlir.constant(0 : i64) : i64
%v350 = llvm.getelementptr %v180[0, %v349] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v344, %v350 : i32, !llvm.ptr
%v351 = llvm.mlir.constant(1 : i64) : i64
%v352 = llvm.getelementptr %v180[0, %v351] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v345, %v352 : i32, !llvm.ptr
%v353 = llvm.mlir.constant(2 : i64) : i64
%v354 = llvm.getelementptr %v180[0, %v353] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v346, %v354 : i32, !llvm.ptr
%v355 = arith.constant 0 : i32
llvm.store %v355, %v182 : i32, !llvm.ptr
%v356 = arith.constant 0 : i32
%v357 = arith.constant 3 : i32
%v358 = arith.cmpi uge, %v356, %v357 : i32
scf.if %v358 {
%v359 = llvm.mlir.addressof @str_17 : !llvm.ptr
func.call @__flow_fault(%v359) : (!llvm.ptr) -> ()
}
%v360 = arith.extsi %v356 : i32 to i64
%v361 = llvm.getelementptr %v180[0, %v360] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
%v362 = llvm.load %v361 : !llvm.ptr -> i32
%v363 = arith.constant 1 : i32
%v364 = arith.cmpi eq, %v362, %v363 : i32
%v365 = arith.constant 1 : i32
%v366 = arith.constant 3 : i32
%v367 = arith.cmpi uge, %v365, %v366 : i32
scf.if %v367 {
%v368 = llvm.mlir.addressof @str_17 : !llvm.ptr
func.call @__flow_fault(%v368) : (!llvm.ptr) -> ()
}
%v369 = arith.extsi %v365 : i32 to i64
%v370 = llvm.getelementptr %v180[0, %v369] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
%v371 = llvm.load %v370 : !llvm.ptr -> i32
%v372 = arith.constant 2 : i32
%v373 = arith.constant 3 : i32
%v374 = arith.cmpi uge, %v372, %v373 : i32
scf.if %v374 {
%v375 = llvm.mlir.addressof @str_17 : !llvm.ptr
func.call @__flow_fault(%v375) : (!llvm.ptr) -> ()
}
%v376 = arith.extsi %v372 : i32 to i64
%v377 = llvm.getelementptr %v180[0, %v376] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
%v378 = llvm.load %v377 : !llvm.ptr -> i32
cf.cond_br %v364, ^b13, ^b14
^b13:
%v379 = arith.addi %v371, %v378 : i32
llvm.store %v379, %v182 : i32, !llvm.ptr
cf.br ^b15
^b14:
%v380 = arith.constant 99 : i32
llvm.store %v380, %v182 : i32, !llvm.ptr
cf.br ^b15
^b15:
%v381 = llvm.load %v182 : !llvm.ptr -> i32
%v382 = llvm.mlir.addressof @str_18 : !llvm.ptr
%v383 = llvm.call @printf(%v382, %v381) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v384 = arith.constant 0 : i32
%v385 = llvm.mlir.addressof @K : !llvm.ptr
%v386 = llvm.load %v385 : !llvm.ptr -> i32
%v387 = llvm.mlir.addressof @MASK : !llvm.ptr
%v388 = llvm.load %v387 : !llvm.ptr -> i32
%v389 = arith.addi %v386, %v388 : i32
%v390 = llvm.mlir.addressof @counter : !llvm.ptr
%v391 = llvm.load %v390 : !llvm.ptr -> i32
%v392 = arith.addi %v389, %v391 : i32
%v393 = llvm.mlir.addressof @str_18 : !llvm.ptr
%v394 = llvm.call @printf(%v393, %v392) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v395 = arith.constant 0 : i32
%v396 = llvm.mlir.addressof @NEG : !llvm.ptr
%v397 = llvm.load %v396 : !llvm.ptr -> i64
%v398 = llvm.mlir.addressof @str_16 : !llvm.ptr
%v399 = llvm.call @printf(%v398, %v397) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v400 = arith.constant 0 : i32
%v401 = arith.constant 1.5 : f64
%v402 = arith.constant 2.0 : f64
%v403 = arith.mulf %v401, %v402 : f64
%v404 = llvm.mlir.addressof @str_15 : !llvm.ptr
%v405 = llvm.call @printf(%v404, %v403) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v406 = arith.constant 0 : i32
%v407 = arith.constant 0 : i32
func.return %v407 : i32
}
}
