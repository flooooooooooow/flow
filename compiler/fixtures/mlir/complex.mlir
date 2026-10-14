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
%name = llvm.mlir.addressof @str_6 : !llvm.ptr
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
%hdr = llvm.mlir.addressof @str_7 : !llvm.ptr
%h = llvm.call @printf(%hdr) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%g_flow_mem_alloc_count = llvm.mlir.addressof @flow_mem_alloc_count : !llvm.ptr
%v_flow_mem_alloc_count = llvm.load %g_flow_mem_alloc_count : !llvm.ptr -> i64
%f_flow_mem_alloc_count = llvm.mlir.addressof @str_8 : !llvm.ptr
%w_flow_mem_alloc_count = llvm.call @printf(%f_flow_mem_alloc_count, %v_flow_mem_alloc_count) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_alloc_bytes = llvm.mlir.addressof @flow_mem_alloc_bytes : !llvm.ptr
%v_flow_mem_alloc_bytes = llvm.load %g_flow_mem_alloc_bytes : !llvm.ptr -> i64
%f_flow_mem_alloc_bytes = llvm.mlir.addressof @str_9 : !llvm.ptr
%w_flow_mem_alloc_bytes = llvm.call @printf(%f_flow_mem_alloc_bytes, %v_flow_mem_alloc_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_peak_live = llvm.mlir.addressof @flow_mem_peak_live : !llvm.ptr
%v_flow_mem_peak_live = llvm.load %g_flow_mem_peak_live : !llvm.ptr -> i64
%f_flow_mem_peak_live = llvm.mlir.addressof @str_10 : !llvm.ptr
%w_flow_mem_peak_live = llvm.call @printf(%f_flow_mem_peak_live, %v_flow_mem_peak_live) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_temp_bytes = llvm.mlir.addressof @flow_mem_temp_bytes : !llvm.ptr
%v_flow_mem_temp_bytes = llvm.load %g_flow_mem_temp_bytes : !llvm.ptr -> i64
%f_flow_mem_temp_bytes = llvm.mlir.addressof @str_11 : !llvm.ptr
%w_flow_mem_temp_bytes = llvm.call @printf(%f_flow_mem_temp_bytes, %v_flow_mem_temp_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_copy_bytes = llvm.mlir.addressof @flow_mem_copy_bytes : !llvm.ptr
%v_flow_mem_copy_bytes = llvm.load %g_flow_mem_copy_bytes : !llvm.ptr -> i64
%f_flow_mem_copy_bytes = llvm.mlir.addressof @str_12 : !llvm.ptr
%w_flow_mem_copy_bytes = llvm.call @printf(%f_flow_mem_copy_bytes, %v_flow_mem_copy_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_stack_bytes = llvm.mlir.addressof @flow_mem_stack_bytes : !llvm.ptr
%v_flow_mem_stack_bytes = llvm.load %g_flow_mem_stack_bytes : !llvm.ptr -> i64
%f_flow_mem_stack_bytes = llvm.mlir.addressof @str_13 : !llvm.ptr
%w_flow_mem_stack_bytes = llvm.call @printf(%f_flow_mem_stack_bytes, %v_flow_mem_stack_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_arena_bytes = llvm.mlir.addressof @flow_mem_arena_bytes : !llvm.ptr
%v_flow_mem_arena_bytes = llvm.load %g_flow_mem_arena_bytes : !llvm.ptr -> i64
%f_flow_mem_arena_bytes = llvm.mlir.addressof @str_14 : !llvm.ptr
%w_flow_mem_arena_bytes = llvm.call @printf(%f_flow_mem_arena_bytes, %v_flow_mem_arena_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%sp = llvm.mlir.addressof @flow_mem_stack_bytes : !llvm.ptr
%sv = llvm.load %sp : !llvm.ptr -> i64
%ap = llvm.mlir.addressof @flow_mem_arena_bytes : !llvm.ptr
%av = llvm.load %ap : !llvm.ptr -> i64
%promo = arith.addi %sv, %av : i64
%pf = llvm.mlir.addressof @str_15 : !llvm.ptr
%ph = llvm.call @printf(%pf, %promo) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_map_overflow = llvm.mlir.addressof @flow_mem_map_overflow : !llvm.ptr
%v_flow_mem_map_overflow = llvm.load %g_flow_mem_map_overflow : !llvm.ptr -> i64
%f_flow_mem_map_overflow = llvm.mlir.addressof @str_16 : !llvm.ptr
%w_flow_mem_map_overflow = llvm.call @printf(%f_flow_mem_map_overflow, %v_flow_mem_map_overflow) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_site_concat = llvm.mlir.addressof @flow_mem_site_concat : !llvm.ptr
%v_flow_mem_site_concat = llvm.load %g_flow_mem_site_concat : !llvm.ptr -> i64
%f_flow_mem_site_concat = llvm.mlir.addressof @str_17 : !llvm.ptr
%w_flow_mem_site_concat = llvm.call @printf(%f_flow_mem_site_concat, %v_flow_mem_site_concat) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
scf.yield
}
func.return
}
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("(%f + %f j)\0A\00") {addr_space = 0 : i32} : !llvm.array<13 x i8>
llvm.mlir.global internal constant @str_1("(%f + %f j)\00") {addr_space = 0 : i32} : !llvm.array<12 x i8>
llvm.mlir.global internal constant @str_2(" \00") {addr_space = 0 : i32} : !llvm.array<2 x i8>
llvm.mlir.global internal constant @str_3("parts %f %f abs %f\0A\00") {addr_space = 0 : i32} : !llvm.array<20 x i8>
llvm.mlir.global internal constant @str_4("compare ok\0A\00") {addr_space = 0 : i32} : !llvm.array<12 x i8>
llvm.mlir.global internal constant @str_5("phasor %f %f tag %d\0A\00") {addr_space = 0 : i32} : !llvm.array<21 x i8>
llvm.mlir.global internal constant @str_6("FLOW_MEM_PROFILE\00") {addr_space = 0 : i32} : !llvm.array<17 x i8>
llvm.mlir.global internal constant @str_7("\0A=== Flow memory profile (#740) ===\0A\00") {addr_space = 0 : i32} : !llvm.array<37 x i8>
llvm.mlir.global internal constant @str_8("allocations: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<19 x i8>
llvm.mlir.global internal constant @str_9("heap_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<18 x i8>
llvm.mlir.global internal constant @str_10("peak_live_heap: %lld\0A\00") {addr_space = 0 : i32} : !llvm.array<22 x i8>
llvm.mlir.global internal constant @str_11("temp_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<18 x i8>
llvm.mlir.global internal constant @str_12("copies: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<14 x i8>
llvm.mlir.global internal constant @str_13("stack_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<19 x i8>
llvm.mlir.global internal constant @str_14("arena_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<19 x i8>
llvm.mlir.global internal constant @str_15("promotion_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<23 x i8>
llvm.mlir.global internal constant @str_16("live_map_overflow: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<25 x i8>
llvm.mlir.global internal constant @str_17("site_concat: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<19 x i8>
// Struct: Phasor
// Fields:
//   z: !llvm.struct<(f64, f64)>
//   tag: i32
func.func @rotate(%arg0: !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>, %arg1: !llvm.struct<(f64, f64)>) -> !llvm.struct<(!llvm.struct<(f64, f64)>, i32)> {
%v1 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v2 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v3 = llvm.insertvalue %v2, %v1[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v4 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v5 = llvm.insertvalue %v4, %v3[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v6 = llvm.mlir.constant(1 : i64) : i64
%v7 = llvm.alloca %v6 x !llvm.struct<(!llvm.struct<(f64, f64)>, i32)> : (i64) -> !llvm.ptr
llvm.store %v5, %v7 : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>, !llvm.ptr
%v8 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v9 = llvm.extractvalue %arg1[0] : !llvm.struct<(f64, f64)>
%v10 = llvm.insertvalue %v9, %v8[0] : !llvm.struct<(f64, f64)>
%v11 = llvm.extractvalue %arg1[1] : !llvm.struct<(f64, f64)>
%v12 = llvm.insertvalue %v11, %v10[1] : !llvm.struct<(f64, f64)>
%v13 = llvm.mlir.constant(1 : i64) : i64
%v14 = llvm.alloca %v13 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v12, %v14 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v15 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v16 = llvm.load %v7 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v17 = llvm.getelementptr %v7[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v18 = llvm.load %v17 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v19 = llvm.load %v14 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v20 = llvm.extractvalue %v18[0] : !llvm.struct<(f64, f64)>
%v21 = llvm.extractvalue %v18[1] : !llvm.struct<(f64, f64)>
%v22 = llvm.extractvalue %v19[0] : !llvm.struct<(f64, f64)>
%v23 = llvm.extractvalue %v19[1] : !llvm.struct<(f64, f64)>
%v24 = arith.mulf %v20, %v22 : f64
%v25 = arith.mulf %v21, %v23 : f64
%v26 = arith.mulf %v20, %v23 : f64
%v27 = arith.mulf %v21, %v22 : f64
%v28 = arith.subf %v24, %v25 : f64
%v29 = arith.addf %v26, %v27 : f64
%v30 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v31 = llvm.insertvalue %v28, %v30[0] : !llvm.struct<(f64, f64)>
%v32 = llvm.insertvalue %v29, %v31[1] : !llvm.struct<(f64, f64)>
%v33 = llvm.insertvalue %v32, %v15[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v34 = llvm.load %v7 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v35 = llvm.getelementptr %v7[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v36 = llvm.load %v35 : !llvm.ptr -> i32
%v37 = arith.constant 1 : i32
%v38 = arith.addi %v36, %v37 : i32
%v39 = llvm.insertvalue %v38, %v33[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v40 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v41 = llvm.extractvalue %v39[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v42 = llvm.insertvalue %v41, %v40[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v43 = llvm.extractvalue %v39[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v44 = llvm.insertvalue %v43, %v42[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v45 = llvm.mlir.constant(1 : i64) : i64
%v46 = llvm.alloca %v45 x !llvm.struct<(!llvm.struct<(f64, f64)>, i32)> : (i64) -> !llvm.ptr
llvm.store %v44, %v46 : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>, !llvm.ptr
%v47 = llvm.load %v46 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
func.return %v47 : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
}
func.func @sum(%arg0: !llvm.ptr, %arg1: i32) -> !llvm.struct<(f32, f32)> {
%v48 = arith.constant 0.0 : f64
%v49 = arith.constant 0.0 : f64
%v50 = arith.truncf %v48 : f64 to f32
%v51 = arith.truncf %v49 : f64 to f32
%v52 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v53 = llvm.insertvalue %v50, %v52[0] : !llvm.struct<(f32, f32)>
%v54 = llvm.insertvalue %v51, %v53[1] : !llvm.struct<(f32, f32)>
%v55 = llvm.mlir.constant(1 : i64) : i64
%v56 = llvm.alloca %v55 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
llvm.store %v54, %v56 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v57 = arith.constant 0 : i32
%v58 = arith.index_cast %v57 : i32 to index
%v59 = arith.index_cast %arg1 : i32 to index
%v60 = arith.constant 1 : index
%v61 = arith.constant -1 : index
%v62 = arith.cmpi sle, %v58, %v59 : index
%v63 = arith.select %v62, %v60, %v61 : index
cf.br ^b1(%v58 : index)
^b1(%v64: index):
%v65 = arith.cmpi slt, %v64, %v59 : index
%v66 = arith.cmpi sgt, %v64, %v59 : index
%v67 = arith.select %v62, %v65, %v66 : i1
cf.cond_br %v67, ^b2(%v64 : index), ^b3(%v64 : index)
^b2(%v68: index):
%v69 = llvm.load %v56 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v70 = arith.index_cast %v68 : index to i64
%v71 = llvm.getelementptr %arg0[%v70] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(f32, f32)>
%v72 = llvm.load %v71 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v73 = llvm.extractvalue %v69[0] : !llvm.struct<(f32, f32)>
%v74 = llvm.extractvalue %v69[1] : !llvm.struct<(f32, f32)>
%v75 = llvm.extractvalue %v72[0] : !llvm.struct<(f32, f32)>
%v76 = llvm.extractvalue %v72[1] : !llvm.struct<(f32, f32)>
%v77 = arith.addf %v73, %v75 : f32
%v78 = arith.addf %v74, %v76 : f32
%v79 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v80 = llvm.insertvalue %v77, %v79[0] : !llvm.struct<(f32, f32)>
%v81 = llvm.insertvalue %v78, %v80[1] : !llvm.struct<(f32, f32)>
llvm.store %v81, %v56 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v82 = arith.addi %v68, %v63 : index
cf.br ^b1(%v82 : index)
^b3(%v83: index):
%v84 = llvm.load %v56 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v85 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v86 = llvm.extractvalue %v84[0] : !llvm.struct<(f32, f32)>
%v87 = llvm.insertvalue %v86, %v85[0] : !llvm.struct<(f32, f32)>
%v88 = llvm.extractvalue %v84[1] : !llvm.struct<(f32, f32)>
%v89 = llvm.insertvalue %v88, %v87[1] : !llvm.struct<(f32, f32)>
%v90 = llvm.mlir.constant(1 : i64) : i64
%v91 = llvm.alloca %v90 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
llvm.store %v89, %v91 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v92 = llvm.load %v91 : !llvm.ptr -> !llvm.struct<(f32, f32)>
func.return %v92 : !llvm.struct<(f32, f32)>
}
func.func @main() -> i32 {
%v93 = arith.constant 3.0 : f64
%v94 = arith.constant 4.0 : f64
%v95 = arith.truncf %v93 : f64 to f32
%v96 = arith.truncf %v94 : f64 to f32
%v97 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v98 = llvm.insertvalue %v95, %v97[0] : !llvm.struct<(f32, f32)>
%v99 = llvm.insertvalue %v96, %v98[1] : !llvm.struct<(f32, f32)>
%v100 = llvm.mlir.constant(1 : i64) : i64
%v101 = llvm.alloca %v100 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
llvm.store %v99, %v101 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v102 = arith.constant 1.0 : f64
%v103 = arith.constant 2.0 : f64
%v104 = arith.truncf %v102 : f64 to f32
%v105 = arith.truncf %v103 : f64 to f32
%v106 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v107 = llvm.insertvalue %v104, %v106[0] : !llvm.struct<(f32, f32)>
%v108 = llvm.insertvalue %v105, %v107[1] : !llvm.struct<(f32, f32)>
%v109 = llvm.mlir.constant(1 : i64) : i64
%v110 = llvm.alloca %v109 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
llvm.store %v108, %v110 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v111 = llvm.load %v101 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v112 = llvm.load %v110 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v113 = llvm.extractvalue %v111[0] : !llvm.struct<(f32, f32)>
%v114 = llvm.extractvalue %v111[1] : !llvm.struct<(f32, f32)>
%v115 = llvm.extractvalue %v112[0] : !llvm.struct<(f32, f32)>
%v116 = llvm.extractvalue %v112[1] : !llvm.struct<(f32, f32)>
%v117 = arith.addf %v113, %v115 : f32
%v118 = arith.addf %v114, %v116 : f32
%v119 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v120 = llvm.insertvalue %v117, %v119[0] : !llvm.struct<(f32, f32)>
%v121 = llvm.insertvalue %v118, %v120[1] : !llvm.struct<(f32, f32)>
%v122 = llvm.extractvalue %v121[0] : !llvm.struct<(f32, f32)>
%v123 = arith.extf %v122 : f32 to f64
%v124 = llvm.extractvalue %v121[1] : !llvm.struct<(f32, f32)>
%v125 = arith.extf %v124 : f32 to f64
%v126 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v127 = llvm.call @printf(%v126, %v123, %v125) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v128 = arith.constant 0 : i32
%v129 = llvm.load %v101 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v130 = llvm.load %v110 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v131 = llvm.extractvalue %v129[0] : !llvm.struct<(f32, f32)>
%v132 = llvm.extractvalue %v129[1] : !llvm.struct<(f32, f32)>
%v133 = llvm.extractvalue %v130[0] : !llvm.struct<(f32, f32)>
%v134 = llvm.extractvalue %v130[1] : !llvm.struct<(f32, f32)>
%v135 = arith.subf %v131, %v133 : f32
%v136 = arith.subf %v132, %v134 : f32
%v137 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v138 = llvm.insertvalue %v135, %v137[0] : !llvm.struct<(f32, f32)>
%v139 = llvm.insertvalue %v136, %v138[1] : !llvm.struct<(f32, f32)>
%v140 = llvm.extractvalue %v139[0] : !llvm.struct<(f32, f32)>
%v141 = arith.extf %v140 : f32 to f64
%v142 = llvm.extractvalue %v139[1] : !llvm.struct<(f32, f32)>
%v143 = arith.extf %v142 : f32 to f64
%v144 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v145 = llvm.call @printf(%v144, %v141, %v143) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v146 = arith.constant 0 : i32
%v147 = llvm.load %v101 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v148 = llvm.load %v110 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v149 = llvm.extractvalue %v147[0] : !llvm.struct<(f32, f32)>
%v150 = llvm.extractvalue %v147[1] : !llvm.struct<(f32, f32)>
%v151 = llvm.extractvalue %v148[0] : !llvm.struct<(f32, f32)>
%v152 = llvm.extractvalue %v148[1] : !llvm.struct<(f32, f32)>
%v153 = arith.mulf %v149, %v151 : f32
%v154 = arith.mulf %v150, %v152 : f32
%v155 = arith.mulf %v149, %v152 : f32
%v156 = arith.mulf %v150, %v151 : f32
%v157 = arith.subf %v153, %v154 : f32
%v158 = arith.addf %v155, %v156 : f32
%v159 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v160 = llvm.insertvalue %v157, %v159[0] : !llvm.struct<(f32, f32)>
%v161 = llvm.insertvalue %v158, %v160[1] : !llvm.struct<(f32, f32)>
%v162 = llvm.extractvalue %v161[0] : !llvm.struct<(f32, f32)>
%v163 = arith.extf %v162 : f32 to f64
%v164 = llvm.extractvalue %v161[1] : !llvm.struct<(f32, f32)>
%v165 = arith.extf %v164 : f32 to f64
%v166 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v167 = llvm.call @printf(%v166, %v163, %v165) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v168 = arith.constant 0 : i32
%v169 = llvm.load %v101 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v170 = llvm.load %v110 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v171 = llvm.extractvalue %v169[0] : !llvm.struct<(f32, f32)>
%v172 = llvm.extractvalue %v169[1] : !llvm.struct<(f32, f32)>
%v173 = llvm.extractvalue %v170[0] : !llvm.struct<(f32, f32)>
%v174 = llvm.extractvalue %v170[1] : !llvm.struct<(f32, f32)>
%v175 = arith.mulf %v173, %v173 : f32
%v176 = arith.mulf %v174, %v174 : f32
%v177 = arith.addf %v175, %v176 : f32
%v178 = arith.mulf %v171, %v173 : f32
%v179 = arith.mulf %v172, %v174 : f32
%v180 = arith.mulf %v172, %v173 : f32
%v181 = arith.mulf %v171, %v174 : f32
%v182 = arith.addf %v178, %v179 : f32
%v183 = arith.subf %v180, %v181 : f32
%v184 = arith.divf %v182, %v177 : f32
%v185 = arith.divf %v183, %v177 : f32
%v186 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v187 = llvm.insertvalue %v184, %v186[0] : !llvm.struct<(f32, f32)>
%v188 = llvm.insertvalue %v185, %v187[1] : !llvm.struct<(f32, f32)>
%v189 = llvm.extractvalue %v188[0] : !llvm.struct<(f32, f32)>
%v190 = arith.extf %v189 : f32 to f64
%v191 = llvm.extractvalue %v188[1] : !llvm.struct<(f32, f32)>
%v192 = arith.extf %v191 : f32 to f64
%v193 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v194 = llvm.call @printf(%v193, %v190, %v192) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v195 = arith.constant 0 : i32
%v196 = llvm.load %v101 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v197 = llvm.extractvalue %v196[0] : !llvm.struct<(f32, f32)>
%v198 = arith.negf %v197 : f32
%v199 = llvm.extractvalue %v196[1] : !llvm.struct<(f32, f32)>
%v200 = arith.negf %v199 : f32
%v201 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v202 = llvm.insertvalue %v198, %v201[0] : !llvm.struct<(f32, f32)>
%v203 = llvm.insertvalue %v200, %v202[1] : !llvm.struct<(f32, f32)>
%v204 = llvm.extractvalue %v203[0] : !llvm.struct<(f32, f32)>
%v205 = arith.extf %v204 : f32 to f64
%v206 = llvm.extractvalue %v203[1] : !llvm.struct<(f32, f32)>
%v207 = arith.extf %v206 : f32 to f64
%v208 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v209 = llvm.call @printf(%v208, %v205, %v207) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v210 = arith.constant 0 : i32
%v211 = arith.constant 2.0 : f64
%v212 = arith.truncf %v211 : f64 to f32
%v213 = llvm.load %v101 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v214 = llvm.extractvalue %v213[0] : !llvm.struct<(f32, f32)>
%v215 = llvm.extractvalue %v213[1] : !llvm.struct<(f32, f32)>
%v216 = arith.mulf %v214, %v212 : f32
%v217 = arith.mulf %v215, %v212 : f32
%v218 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v219 = llvm.insertvalue %v216, %v218[0] : !llvm.struct<(f32, f32)>
%v220 = llvm.insertvalue %v217, %v219[1] : !llvm.struct<(f32, f32)>
%v221 = llvm.mlir.constant(1 : i64) : i64
%v222 = llvm.alloca %v221 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
llvm.store %v220, %v222 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v223 = llvm.load %v101 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v224 = llvm.extractvalue %v223[0] : !llvm.struct<(f32, f32)>
%v225 = llvm.extractvalue %v223[1] : !llvm.struct<(f32, f32)>
%v226 = arith.divf %v224, %v212 : f32
%v227 = arith.divf %v225, %v212 : f32
%v228 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v229 = llvm.insertvalue %v226, %v228[0] : !llvm.struct<(f32, f32)>
%v230 = llvm.insertvalue %v227, %v229[1] : !llvm.struct<(f32, f32)>
%v231 = llvm.mlir.constant(1 : i64) : i64
%v232 = llvm.alloca %v231 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
llvm.store %v230, %v232 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v233 = arith.constant 0.0 : f32
%v234 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v235 = llvm.insertvalue %v212, %v234[0] : !llvm.struct<(f32, f32)>
%v236 = llvm.insertvalue %v233, %v235[1] : !llvm.struct<(f32, f32)>
%v237 = llvm.load %v101 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v238 = llvm.extractvalue %v236[0] : !llvm.struct<(f32, f32)>
%v239 = llvm.extractvalue %v236[1] : !llvm.struct<(f32, f32)>
%v240 = llvm.extractvalue %v237[0] : !llvm.struct<(f32, f32)>
%v241 = llvm.extractvalue %v237[1] : !llvm.struct<(f32, f32)>
%v242 = arith.mulf %v238, %v240 : f32
%v243 = arith.mulf %v239, %v241 : f32
%v244 = arith.mulf %v238, %v241 : f32
%v245 = arith.mulf %v239, %v240 : f32
%v246 = arith.subf %v242, %v243 : f32
%v247 = arith.addf %v244, %v245 : f32
%v248 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v249 = llvm.insertvalue %v246, %v248[0] : !llvm.struct<(f32, f32)>
%v250 = llvm.insertvalue %v247, %v249[1] : !llvm.struct<(f32, f32)>
%v251 = llvm.mlir.constant(1 : i64) : i64
%v252 = llvm.alloca %v251 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
llvm.store %v250, %v252 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v253 = llvm.load %v222 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v254 = llvm.extractvalue %v253[0] : !llvm.struct<(f32, f32)>
%v255 = arith.extf %v254 : f32 to f64
%v256 = llvm.extractvalue %v253[1] : !llvm.struct<(f32, f32)>
%v257 = arith.extf %v256 : f32 to f64
%v258 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v259 = llvm.call @printf(%v258, %v255, %v257) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v260 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v261 = llvm.call @printf(%v260) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v262 = llvm.load %v232 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v263 = llvm.extractvalue %v262[0] : !llvm.struct<(f32, f32)>
%v264 = arith.extf %v263 : f32 to f64
%v265 = llvm.extractvalue %v262[1] : !llvm.struct<(f32, f32)>
%v266 = arith.extf %v265 : f32 to f64
%v267 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v268 = llvm.call @printf(%v267, %v264, %v266) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v269 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v270 = llvm.call @printf(%v269) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v271 = llvm.load %v252 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v272 = llvm.extractvalue %v271[0] : !llvm.struct<(f32, f32)>
%v273 = arith.extf %v272 : f32 to f64
%v274 = llvm.extractvalue %v271[1] : !llvm.struct<(f32, f32)>
%v275 = arith.extf %v274 : f32 to f64
%v276 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v277 = llvm.call @printf(%v276, %v273, %v275) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v278 = arith.constant 0 : i32
%v279 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v280 = llvm.load %v101 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v281 = llvm.extractvalue %v280[0] : !llvm.struct<(f32, f32)>
%v282 = llvm.extractvalue %v280[1] : !llvm.struct<(f32, f32)>
%v283 = arith.extf %v281 : f32 to f64
%v284 = llvm.load %v101 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v285 = llvm.extractvalue %v284[0] : !llvm.struct<(f32, f32)>
%v286 = llvm.extractvalue %v284[1] : !llvm.struct<(f32, f32)>
%v287 = arith.extf %v286 : f32 to f64
%v288 = llvm.load %v101 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v289 = llvm.extractvalue %v288[0] : !llvm.struct<(f32, f32)>
%v290 = llvm.extractvalue %v288[1] : !llvm.struct<(f32, f32)>
%v291 = arith.extf %v289 : f32 to f64
%v292 = arith.extf %v290 : f32 to f64
%v293 = arith.mulf %v291, %v291 : f64
%v294 = arith.mulf %v292, %v292 : f64
%v295 = arith.addf %v293, %v294 : f64
%v296 = math.sqrt %v295 : f64
%v297 = arith.truncf %v296 : f64 to f32
%v298 = arith.extf %v297 : f32 to f64
%v299 = llvm.call @printf(%v279, %v283, %v287, %v298) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64, f64) -> i32
%v300 = llvm.load %v110 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v301 = llvm.extractvalue %v300[0] : !llvm.struct<(f32, f32)>
%v302 = llvm.extractvalue %v300[1] : !llvm.struct<(f32, f32)>
%v303 = arith.negf %v302 : f32
%v304 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v305 = llvm.insertvalue %v301, %v304[0] : !llvm.struct<(f32, f32)>
%v306 = llvm.insertvalue %v303, %v305[1] : !llvm.struct<(f32, f32)>
%v307 = llvm.extractvalue %v306[0] : !llvm.struct<(f32, f32)>
%v308 = arith.extf %v307 : f32 to f64
%v309 = llvm.extractvalue %v306[1] : !llvm.struct<(f32, f32)>
%v310 = arith.extf %v309 : f32 to f64
%v311 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v312 = llvm.call @printf(%v311, %v308, %v310) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v313 = arith.constant 0 : i32
%v314 = llvm.load %v101 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v315 = arith.constant 3.0 : f64
%v316 = arith.constant 4.0 : f64
%v317 = arith.truncf %v315 : f64 to f32
%v318 = arith.truncf %v316 : f64 to f32
%v319 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v320 = llvm.insertvalue %v317, %v319[0] : !llvm.struct<(f32, f32)>
%v321 = llvm.insertvalue %v318, %v320[1] : !llvm.struct<(f32, f32)>
%v322 = llvm.extractvalue %v314[0] : !llvm.struct<(f32, f32)>
%v323 = llvm.extractvalue %v314[1] : !llvm.struct<(f32, f32)>
%v324 = llvm.extractvalue %v321[0] : !llvm.struct<(f32, f32)>
%v325 = llvm.extractvalue %v321[1] : !llvm.struct<(f32, f32)>
%v326 = arith.cmpf oeq, %v322, %v324 : f32
%v327 = arith.cmpf oeq, %v323, %v325 : f32
%v328 = arith.andi %v326, %v327 : i1
%v329 = scf.if %v328 -> (i1) {
%v330 = llvm.load %v101 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v331 = llvm.load %v110 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v332 = llvm.extractvalue %v330[0] : !llvm.struct<(f32, f32)>
%v333 = llvm.extractvalue %v330[1] : !llvm.struct<(f32, f32)>
%v334 = llvm.extractvalue %v331[0] : !llvm.struct<(f32, f32)>
%v335 = llvm.extractvalue %v331[1] : !llvm.struct<(f32, f32)>
%v336 = arith.cmpf une, %v332, %v334 : f32
%v337 = arith.cmpf une, %v333, %v335 : f32
%v338 = arith.ori %v336, %v337 : i1
scf.yield %v338 : i1
} else {
%v339 = arith.constant false
scf.yield %v339 : i1
}
cf.cond_br %v329, ^b4, ^b5
^b4:
%v340 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v341 = llvm.call @printf(%v340) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
cf.br ^b6
^b5:
cf.br ^b6
^b6:
%v342 = llvm.load %v101 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v343 = llvm.extractvalue %v342[0] : !llvm.struct<(f32, f32)>
%v344 = llvm.extractvalue %v342[1] : !llvm.struct<(f32, f32)>
%v345 = arith.extf %v343 : f32 to f64
%v346 = llvm.load %v101 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v347 = llvm.extractvalue %v346[0] : !llvm.struct<(f32, f32)>
%v348 = llvm.extractvalue %v346[1] : !llvm.struct<(f32, f32)>
%v349 = arith.extf %v348 : f32 to f64
%v350 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v351 = llvm.insertvalue %v345, %v350[0] : !llvm.struct<(f64, f64)>
%v352 = llvm.insertvalue %v349, %v351[1] : !llvm.struct<(f64, f64)>
%v353 = llvm.mlir.constant(1 : i64) : i64
%v354 = llvm.alloca %v353 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v352, %v354 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v355 = arith.constant 0.0 : f64
%v356 = arith.constant 0.0 : f64
%v357 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v358 = llvm.insertvalue %v355, %v357[0] : !llvm.struct<(f64, f64)>
%v359 = llvm.insertvalue %v356, %v358[1] : !llvm.struct<(f64, f64)>
%v360 = llvm.extractvalue %v359[0] : !llvm.struct<(f64, f64)>
%v361 = llvm.extractvalue %v359[1] : !llvm.struct<(f64, f64)>
%v362 = math.exp %v360 : f64
%v363 = math.cos %v361 : f64
%v364 = math.sin %v361 : f64
%v365 = arith.mulf %v362, %v363 : f64
%v366 = arith.mulf %v362, %v364 : f64
%v367 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v368 = llvm.insertvalue %v365, %v367[0] : !llvm.struct<(f64, f64)>
%v369 = llvm.insertvalue %v366, %v368[1] : !llvm.struct<(f64, f64)>
%v370 = llvm.mlir.constant(1 : i64) : i64
%v371 = llvm.alloca %v370 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v369, %v371 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v372 = llvm.load %v354 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v373 = llvm.load %v371 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v374 = llvm.extractvalue %v372[0] : !llvm.struct<(f64, f64)>
%v375 = llvm.extractvalue %v372[1] : !llvm.struct<(f64, f64)>
%v376 = llvm.extractvalue %v373[0] : !llvm.struct<(f64, f64)>
%v377 = llvm.extractvalue %v373[1] : !llvm.struct<(f64, f64)>
%v378 = arith.mulf %v374, %v376 : f64
%v379 = arith.mulf %v375, %v377 : f64
%v380 = arith.mulf %v374, %v377 : f64
%v381 = arith.mulf %v375, %v376 : f64
%v382 = arith.subf %v378, %v379 : f64
%v383 = arith.addf %v380, %v381 : f64
%v384 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v385 = llvm.insertvalue %v382, %v384[0] : !llvm.struct<(f64, f64)>
%v386 = llvm.insertvalue %v383, %v385[1] : !llvm.struct<(f64, f64)>
%v387 = llvm.extractvalue %v386[0] : !llvm.struct<(f64, f64)>
%v388 = llvm.extractvalue %v386[1] : !llvm.struct<(f64, f64)>
%v389 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v390 = llvm.call @printf(%v389, %v387, %v388) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v391 = arith.constant 0 : i32
%v392 = llvm.load %v101 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v393 = llvm.extractvalue %v392[0] : !llvm.struct<(f32, f32)>
%v394 = arith.extf %v393 : f32 to f64
%v395 = llvm.extractvalue %v392[1] : !llvm.struct<(f32, f32)>
%v396 = arith.extf %v395 : f32 to f64
%v397 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v398 = llvm.insertvalue %v394, %v397[0] : !llvm.struct<(f64, f64)>
%v399 = llvm.insertvalue %v396, %v398[1] : !llvm.struct<(f64, f64)>
%v400 = llvm.mlir.constant(1 : i64) : i64
%v401 = llvm.alloca %v400 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v399, %v401 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v402 = llvm.load %v401 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v403 = llvm.extractvalue %v402[0] : !llvm.struct<(f64, f64)>
%v404 = llvm.extractvalue %v402[1] : !llvm.struct<(f64, f64)>
%v405 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v406 = llvm.call @printf(%v405, %v403, %v404) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v407 = arith.constant 0 : i32
%v408 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v409 = arith.constant 1.0 : f64
%v410 = arith.constant 0.0 : f64
%v411 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v412 = llvm.insertvalue %v409, %v411[0] : !llvm.struct<(f64, f64)>
%v413 = llvm.insertvalue %v410, %v412[1] : !llvm.struct<(f64, f64)>
%v414 = llvm.insertvalue %v413, %v408[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v415 = arith.constant 0 : i32
%v416 = llvm.insertvalue %v415, %v414[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v417 = arith.constant 0.0 : f64
%v418 = arith.constant 1.0 : f64
%v419 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v420 = llvm.insertvalue %v417, %v419[0] : !llvm.struct<(f64, f64)>
%v421 = llvm.insertvalue %v418, %v420[1] : !llvm.struct<(f64, f64)>
%v422 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v423 = llvm.extractvalue %v416[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v424 = llvm.insertvalue %v423, %v422[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v425 = llvm.extractvalue %v416[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v426 = llvm.insertvalue %v425, %v424[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v427 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v428 = llvm.extractvalue %v421[0] : !llvm.struct<(f64, f64)>
%v429 = llvm.insertvalue %v428, %v427[0] : !llvm.struct<(f64, f64)>
%v430 = llvm.extractvalue %v421[1] : !llvm.struct<(f64, f64)>
%v431 = llvm.insertvalue %v430, %v429[1] : !llvm.struct<(f64, f64)>
%v432 = func.call @rotate(%v426, %v431) : (!llvm.struct<(!llvm.struct<(f64, f64)>, i32)>, !llvm.struct<(f64, f64)>) -> !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v433 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v434 = llvm.extractvalue %v432[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v435 = llvm.insertvalue %v434, %v433[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v436 = llvm.extractvalue %v432[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v437 = llvm.insertvalue %v436, %v435[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v438 = llvm.mlir.constant(1 : i64) : i64
%v439 = llvm.alloca %v438 x !llvm.struct<(!llvm.struct<(f64, f64)>, i32)> : (i64) -> !llvm.ptr
llvm.store %v437, %v439 : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>, !llvm.ptr
%v440 = llvm.load %v439 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v441 = llvm.mlir.constant(1 : i64) : i64
%v442 = llvm.alloca %v441 x !llvm.struct<(!llvm.struct<(f64, f64)>, i32)> : (i64) -> !llvm.ptr
llvm.store %v440, %v442 : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>, !llvm.ptr
%v443 = llvm.mlir.addressof @str_5 : !llvm.ptr
%v444 = llvm.load %v442 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v445 = llvm.getelementptr %v442[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v446 = llvm.load %v445 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v447 = llvm.extractvalue %v446[0] : !llvm.struct<(f64, f64)>
%v448 = llvm.extractvalue %v446[1] : !llvm.struct<(f64, f64)>
%v449 = llvm.load %v442 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v450 = llvm.getelementptr %v442[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v451 = llvm.load %v450 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v452 = llvm.extractvalue %v451[0] : !llvm.struct<(f64, f64)>
%v453 = llvm.extractvalue %v451[1] : !llvm.struct<(f64, f64)>
%v454 = llvm.load %v442 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v455 = llvm.getelementptr %v442[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v456 = llvm.load %v455 : !llvm.ptr -> i32
%v457 = llvm.call @printf(%v443, %v447, %v453, %v456) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64, i32) -> i32
%v458 = arith.constant 1.0 : f64
%v459 = arith.constant 1.0 : f64
%v460 = arith.truncf %v458 : f64 to f32
%v461 = arith.truncf %v459 : f64 to f32
%v462 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v463 = llvm.insertvalue %v460, %v462[0] : !llvm.struct<(f32, f32)>
%v464 = llvm.insertvalue %v461, %v463[1] : !llvm.struct<(f32, f32)>
%v465 = arith.constant 2.0 : f64
%v466 = arith.constant 1.0 : f64
%v467 = arith.negf %v466 : f64
%v468 = arith.truncf %v465 : f64 to f32
%v469 = arith.truncf %v467 : f64 to f32
%v470 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v471 = llvm.insertvalue %v468, %v470[0] : !llvm.struct<(f32, f32)>
%v472 = llvm.insertvalue %v469, %v471[1] : !llvm.struct<(f32, f32)>
%v473 = arith.constant 0.5 : f64
%v474 = arith.constant 0.25 : f64
%v475 = arith.truncf %v473 : f64 to f32
%v476 = arith.truncf %v474 : f64 to f32
%v477 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v478 = llvm.insertvalue %v475, %v477[0] : !llvm.struct<(f32, f32)>
%v479 = llvm.insertvalue %v476, %v478[1] : !llvm.struct<(f32, f32)>
%v480 = llvm.mlir.constant(1 : i64) : i64
%v481 = llvm.alloca %v480 x !llvm.array<3 x !llvm.struct<(f32, f32)>> : (i64) -> !llvm.ptr
%v482 = arith.constant 24 : i64
func.call @flow_mem_note_stack(%v482) : (i64) -> ()
%v483 = llvm.mlir.zero : !llvm.array<3 x !llvm.struct<(f32, f32)>>
llvm.store %v483, %v481 : !llvm.array<3 x !llvm.struct<(f32, f32)>>, !llvm.ptr
%v484 = llvm.mlir.constant(0 : i64) : i64
%v485 = llvm.getelementptr %v481[0, %v484] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(f32, f32)>>
llvm.store %v464, %v485 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v486 = llvm.mlir.constant(1 : i64) : i64
%v487 = llvm.getelementptr %v481[0, %v486] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(f32, f32)>>
llvm.store %v472, %v487 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v488 = llvm.mlir.constant(2 : i64) : i64
%v489 = llvm.getelementptr %v481[0, %v488] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(f32, f32)>>
llvm.store %v479, %v489 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v490 = arith.constant 3 : i32
%v491 = func.call @sum(%v481, %v490) : (!llvm.ptr, i32) -> !llvm.struct<(f32, f32)>
%v492 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v493 = llvm.extractvalue %v491[0] : !llvm.struct<(f32, f32)>
%v494 = llvm.insertvalue %v493, %v492[0] : !llvm.struct<(f32, f32)>
%v495 = llvm.extractvalue %v491[1] : !llvm.struct<(f32, f32)>
%v496 = llvm.insertvalue %v495, %v494[1] : !llvm.struct<(f32, f32)>
%v497 = llvm.mlir.constant(1 : i64) : i64
%v498 = llvm.alloca %v497 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
llvm.store %v496, %v498 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v499 = llvm.load %v498 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v500 = llvm.extractvalue %v499[0] : !llvm.struct<(f32, f32)>
%v501 = arith.extf %v500 : f32 to f64
%v502 = llvm.extractvalue %v499[1] : !llvm.struct<(f32, f32)>
%v503 = arith.extf %v502 : f32 to f64
%v504 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v505 = llvm.call @printf(%v504, %v501, %v503) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v506 = arith.constant 0 : i32
%v507 = llvm.load %v101 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v508 = llvm.load %v110 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v509 = llvm.mlir.constant(1 : i64) : i64
%v510 = llvm.alloca %v509 x !llvm.array<2 x !llvm.struct<(f32, f32)>> : (i64) -> !llvm.ptr
%v511 = arith.constant 16 : i64
func.call @flow_mem_note_stack(%v511) : (i64) -> ()
%v512 = llvm.mlir.zero : !llvm.array<2 x !llvm.struct<(f32, f32)>>
llvm.store %v512, %v510 : !llvm.array<2 x !llvm.struct<(f32, f32)>>, !llvm.ptr
%v513 = llvm.mlir.constant(0 : i64) : i64
%v514 = llvm.getelementptr %v510[0, %v513] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x !llvm.struct<(f32, f32)>>
llvm.store %v507, %v514 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v515 = llvm.mlir.constant(1 : i64) : i64
%v516 = llvm.getelementptr %v510[0, %v515] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x !llvm.struct<(f32, f32)>>
llvm.store %v508, %v516 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v517 = llvm.mlir.constant(1 : i64) : i64
%v518 = llvm.alloca %v517 x !llvm.ptr : (i64) -> !llvm.ptr
llvm.store %v510, %v518 : !llvm.ptr, !llvm.ptr
%v519 = llvm.load %v110 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v520 = arith.constant 0.0 : f64
%v521 = arith.constant 1.0 : f64
%v522 = arith.truncf %v520 : f64 to f32
%v523 = arith.truncf %v521 : f64 to f32
%v524 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v525 = llvm.insertvalue %v522, %v524[0] : !llvm.struct<(f32, f32)>
%v526 = llvm.insertvalue %v523, %v525[1] : !llvm.struct<(f32, f32)>
%v527 = llvm.extractvalue %v519[0] : !llvm.struct<(f32, f32)>
%v528 = llvm.extractvalue %v519[1] : !llvm.struct<(f32, f32)>
%v529 = llvm.extractvalue %v526[0] : !llvm.struct<(f32, f32)>
%v530 = llvm.extractvalue %v526[1] : !llvm.struct<(f32, f32)>
%v531 = arith.mulf %v527, %v529 : f32
%v532 = arith.mulf %v528, %v530 : f32
%v533 = arith.mulf %v527, %v530 : f32
%v534 = arith.mulf %v528, %v529 : f32
%v535 = arith.subf %v531, %v532 : f32
%v536 = arith.addf %v533, %v534 : f32
%v537 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v538 = llvm.insertvalue %v535, %v537[0] : !llvm.struct<(f32, f32)>
%v539 = llvm.insertvalue %v536, %v538[1] : !llvm.struct<(f32, f32)>
%v540 = llvm.load %v518 : !llvm.ptr -> !llvm.ptr
%v541 = arith.constant 1 : i32
%v542 = arith.extsi %v541 : i32 to i64
%v543 = llvm.getelementptr %v540[0, %v542] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x !llvm.struct<(f32, f32)>>
llvm.store %v539, %v543 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v544 = llvm.load %v518 : !llvm.ptr -> !llvm.ptr
%v545 = arith.constant 0 : i32
%v546 = arith.extsi %v545 : i32 to i64
%v547 = llvm.getelementptr %v544[0, %v546] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x !llvm.struct<(f32, f32)>>
%v548 = llvm.load %v547 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v549 = llvm.extractvalue %v548[0] : !llvm.struct<(f32, f32)>
%v550 = arith.extf %v549 : f32 to f64
%v551 = llvm.extractvalue %v548[1] : !llvm.struct<(f32, f32)>
%v552 = arith.extf %v551 : f32 to f64
%v553 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v554 = llvm.call @printf(%v553, %v550, %v552) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v555 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v556 = llvm.call @printf(%v555) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v557 = llvm.load %v518 : !llvm.ptr -> !llvm.ptr
%v558 = arith.constant 1 : i32
%v559 = arith.extsi %v558 : i32 to i64
%v560 = llvm.getelementptr %v557[0, %v559] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x !llvm.struct<(f32, f32)>>
%v561 = llvm.load %v560 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v562 = llvm.extractvalue %v561[0] : !llvm.struct<(f32, f32)>
%v563 = arith.extf %v562 : f32 to f64
%v564 = llvm.extractvalue %v561[1] : !llvm.struct<(f32, f32)>
%v565 = arith.extf %v564 : f32 to f64
%v566 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v567 = llvm.call @printf(%v566, %v563, %v565) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v568 = arith.constant 0 : i32
%v569 = arith.constant 0 : i32
func.return %v569 : i32
}
}
