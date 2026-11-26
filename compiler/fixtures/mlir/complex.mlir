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
%v1 = llvm.mlir.constant(1 : i64) : i64
%v2 = llvm.alloca %v1 x !llvm.struct<(!llvm.struct<(f64, f64)>, i32)> : (i64) -> !llvm.ptr
%v3 = llvm.mlir.constant(1 : i64) : i64
%v4 = llvm.alloca %v3 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
%v5 = llvm.mlir.constant(1 : i64) : i64
%v6 = llvm.alloca %v5 x !llvm.struct<(!llvm.struct<(f64, f64)>, i32)> : (i64) -> !llvm.ptr
%v7 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v8 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v9 = llvm.insertvalue %v8, %v7[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v10 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v11 = llvm.insertvalue %v10, %v9[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
llvm.store %v11, %v2 : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>, !llvm.ptr
%v12 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v13 = llvm.extractvalue %arg1[0] : !llvm.struct<(f64, f64)>
%v14 = llvm.insertvalue %v13, %v12[0] : !llvm.struct<(f64, f64)>
%v15 = llvm.extractvalue %arg1[1] : !llvm.struct<(f64, f64)>
%v16 = llvm.insertvalue %v15, %v14[1] : !llvm.struct<(f64, f64)>
llvm.store %v16, %v4 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v17 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v18 = llvm.load %v2 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v19 = llvm.getelementptr %v2[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v20 = llvm.load %v19 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v21 = llvm.load %v4 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v22 = llvm.extractvalue %v20[0] : !llvm.struct<(f64, f64)>
%v23 = llvm.extractvalue %v20[1] : !llvm.struct<(f64, f64)>
%v24 = llvm.extractvalue %v21[0] : !llvm.struct<(f64, f64)>
%v25 = llvm.extractvalue %v21[1] : !llvm.struct<(f64, f64)>
%v26 = arith.mulf %v22, %v24 : f64
%v27 = arith.mulf %v23, %v25 : f64
%v28 = arith.mulf %v22, %v25 : f64
%v29 = arith.mulf %v23, %v24 : f64
%v30 = arith.subf %v26, %v27 : f64
%v31 = arith.addf %v28, %v29 : f64
%v32 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v33 = llvm.insertvalue %v30, %v32[0] : !llvm.struct<(f64, f64)>
%v34 = llvm.insertvalue %v31, %v33[1] : !llvm.struct<(f64, f64)>
%v35 = llvm.insertvalue %v34, %v17[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v36 = llvm.load %v2 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v37 = llvm.getelementptr %v2[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v38 = llvm.load %v37 : !llvm.ptr -> i32
%v39 = arith.constant 1 : i32
%v40 = arith.addi %v38, %v39 : i32
%v41 = llvm.insertvalue %v40, %v35[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v42 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v43 = llvm.extractvalue %v41[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v44 = llvm.insertvalue %v43, %v42[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v45 = llvm.extractvalue %v41[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v46 = llvm.insertvalue %v45, %v44[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
llvm.store %v46, %v6 : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>, !llvm.ptr
%v47 = llvm.load %v6 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
func.return %v47 : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
}
func.func @sum(%arg0: !llvm.ptr, %arg1: i32) -> !llvm.struct<(f32, f32)> {
%v48 = llvm.mlir.constant(1 : i64) : i64
%v49 = llvm.alloca %v48 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
%v50 = llvm.mlir.constant(1 : i64) : i64
%v51 = llvm.alloca %v50 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
%v52 = arith.constant 0.0 : f64
%v53 = arith.constant 0.0 : f64
%v54 = arith.truncf %v52 : f64 to f32
%v55 = arith.truncf %v53 : f64 to f32
%v56 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v57 = llvm.insertvalue %v54, %v56[0] : !llvm.struct<(f32, f32)>
%v58 = llvm.insertvalue %v55, %v57[1] : !llvm.struct<(f32, f32)>
llvm.store %v58, %v49 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v59 = arith.constant 0 : i32
%v60 = arith.index_cast %v59 : i32 to index
%v61 = arith.index_cast %arg1 : i32 to index
%v62 = arith.constant 1 : index
%v63 = arith.constant -1 : index
%v64 = arith.cmpi sle, %v60, %v61 : index
%v65 = arith.select %v64, %v62, %v63 : index
cf.br ^b1(%v60 : index)
^b1(%v66: index):
%v67 = arith.cmpi slt, %v66, %v61 : index
%v68 = arith.cmpi sgt, %v66, %v61 : index
%v69 = arith.select %v64, %v67, %v68 : i1
cf.cond_br %v69, ^b2(%v66 : index), ^b3(%v66 : index)
^b2(%v70: index):
%v71 = llvm.load %v49 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v72 = arith.index_cast %v70 : index to i64
%v73 = llvm.getelementptr %arg0[%v72] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(f32, f32)>
%v74 = llvm.load %v73 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v75 = llvm.extractvalue %v71[0] : !llvm.struct<(f32, f32)>
%v76 = llvm.extractvalue %v71[1] : !llvm.struct<(f32, f32)>
%v77 = llvm.extractvalue %v74[0] : !llvm.struct<(f32, f32)>
%v78 = llvm.extractvalue %v74[1] : !llvm.struct<(f32, f32)>
%v79 = arith.addf %v75, %v77 : f32
%v80 = arith.addf %v76, %v78 : f32
%v81 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v82 = llvm.insertvalue %v79, %v81[0] : !llvm.struct<(f32, f32)>
%v83 = llvm.insertvalue %v80, %v82[1] : !llvm.struct<(f32, f32)>
llvm.store %v83, %v49 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v84 = arith.addi %v70, %v65 : index
cf.br ^b1(%v84 : index)
^b3(%v85: index):
%v86 = llvm.load %v49 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v87 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v88 = llvm.extractvalue %v86[0] : !llvm.struct<(f32, f32)>
%v89 = llvm.insertvalue %v88, %v87[0] : !llvm.struct<(f32, f32)>
%v90 = llvm.extractvalue %v86[1] : !llvm.struct<(f32, f32)>
%v91 = llvm.insertvalue %v90, %v89[1] : !llvm.struct<(f32, f32)>
llvm.store %v91, %v51 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v92 = llvm.load %v51 : !llvm.ptr -> !llvm.struct<(f32, f32)>
func.return %v92 : !llvm.struct<(f32, f32)>
}
func.func @main() -> i32 {
%v93 = llvm.mlir.constant(1 : i64) : i64
%v94 = llvm.alloca %v93 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
%v95 = llvm.mlir.constant(1 : i64) : i64
%v96 = llvm.alloca %v95 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
%v97 = llvm.mlir.constant(1 : i64) : i64
%v98 = llvm.alloca %v97 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
%v99 = llvm.mlir.constant(1 : i64) : i64
%v100 = llvm.alloca %v99 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
%v101 = llvm.mlir.constant(1 : i64) : i64
%v102 = llvm.alloca %v101 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
%v103 = llvm.mlir.constant(1 : i64) : i64
%v104 = llvm.alloca %v103 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
%v105 = llvm.mlir.constant(1 : i64) : i64
%v106 = llvm.alloca %v105 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
%v107 = llvm.mlir.constant(1 : i64) : i64
%v108 = llvm.alloca %v107 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
%v109 = llvm.mlir.constant(1 : i64) : i64
%v110 = llvm.alloca %v109 x !llvm.struct<(!llvm.struct<(f64, f64)>, i32)> : (i64) -> !llvm.ptr
%v111 = llvm.mlir.constant(1 : i64) : i64
%v112 = llvm.alloca %v111 x !llvm.struct<(!llvm.struct<(f64, f64)>, i32)> : (i64) -> !llvm.ptr
%v113 = llvm.mlir.constant(1 : i64) : i64
%v114 = llvm.alloca %v113 x !llvm.array<3 x !llvm.struct<(f32, f32)>> : (i64) -> !llvm.ptr
%v115 = llvm.mlir.constant(1 : i64) : i64
%v116 = llvm.alloca %v115 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
%v117 = llvm.mlir.constant(1 : i64) : i64
%v118 = llvm.alloca %v117 x !llvm.array<2 x !llvm.struct<(f32, f32)>> : (i64) -> !llvm.ptr
%v119 = llvm.mlir.constant(1 : i64) : i64
%v120 = llvm.alloca %v119 x !llvm.ptr : (i64) -> !llvm.ptr
%v121 = arith.constant 3.0 : f64
%v122 = arith.constant 4.0 : f64
%v123 = arith.truncf %v121 : f64 to f32
%v124 = arith.truncf %v122 : f64 to f32
%v125 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v126 = llvm.insertvalue %v123, %v125[0] : !llvm.struct<(f32, f32)>
%v127 = llvm.insertvalue %v124, %v126[1] : !llvm.struct<(f32, f32)>
llvm.store %v127, %v94 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v128 = arith.constant 1.0 : f64
%v129 = arith.constant 2.0 : f64
%v130 = arith.truncf %v128 : f64 to f32
%v131 = arith.truncf %v129 : f64 to f32
%v132 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v133 = llvm.insertvalue %v130, %v132[0] : !llvm.struct<(f32, f32)>
%v134 = llvm.insertvalue %v131, %v133[1] : !llvm.struct<(f32, f32)>
llvm.store %v134, %v96 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v135 = llvm.load %v94 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v136 = llvm.load %v96 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v137 = llvm.extractvalue %v135[0] : !llvm.struct<(f32, f32)>
%v138 = llvm.extractvalue %v135[1] : !llvm.struct<(f32, f32)>
%v139 = llvm.extractvalue %v136[0] : !llvm.struct<(f32, f32)>
%v140 = llvm.extractvalue %v136[1] : !llvm.struct<(f32, f32)>
%v141 = arith.addf %v137, %v139 : f32
%v142 = arith.addf %v138, %v140 : f32
%v143 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v144 = llvm.insertvalue %v141, %v143[0] : !llvm.struct<(f32, f32)>
%v145 = llvm.insertvalue %v142, %v144[1] : !llvm.struct<(f32, f32)>
%v146 = llvm.extractvalue %v145[0] : !llvm.struct<(f32, f32)>
%v147 = arith.extf %v146 : f32 to f64
%v148 = llvm.extractvalue %v145[1] : !llvm.struct<(f32, f32)>
%v149 = arith.extf %v148 : f32 to f64
%v150 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v151 = llvm.call @printf(%v150, %v147, %v149) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v152 = arith.constant 0 : i32
%v153 = llvm.load %v94 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v154 = llvm.load %v96 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v155 = llvm.extractvalue %v153[0] : !llvm.struct<(f32, f32)>
%v156 = llvm.extractvalue %v153[1] : !llvm.struct<(f32, f32)>
%v157 = llvm.extractvalue %v154[0] : !llvm.struct<(f32, f32)>
%v158 = llvm.extractvalue %v154[1] : !llvm.struct<(f32, f32)>
%v159 = arith.subf %v155, %v157 : f32
%v160 = arith.subf %v156, %v158 : f32
%v161 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v162 = llvm.insertvalue %v159, %v161[0] : !llvm.struct<(f32, f32)>
%v163 = llvm.insertvalue %v160, %v162[1] : !llvm.struct<(f32, f32)>
%v164 = llvm.extractvalue %v163[0] : !llvm.struct<(f32, f32)>
%v165 = arith.extf %v164 : f32 to f64
%v166 = llvm.extractvalue %v163[1] : !llvm.struct<(f32, f32)>
%v167 = arith.extf %v166 : f32 to f64
%v168 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v169 = llvm.call @printf(%v168, %v165, %v167) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v170 = arith.constant 0 : i32
%v171 = llvm.load %v94 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v172 = llvm.load %v96 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v173 = llvm.extractvalue %v171[0] : !llvm.struct<(f32, f32)>
%v174 = llvm.extractvalue %v171[1] : !llvm.struct<(f32, f32)>
%v175 = llvm.extractvalue %v172[0] : !llvm.struct<(f32, f32)>
%v176 = llvm.extractvalue %v172[1] : !llvm.struct<(f32, f32)>
%v177 = arith.mulf %v173, %v175 : f32
%v178 = arith.mulf %v174, %v176 : f32
%v179 = arith.mulf %v173, %v176 : f32
%v180 = arith.mulf %v174, %v175 : f32
%v181 = arith.subf %v177, %v178 : f32
%v182 = arith.addf %v179, %v180 : f32
%v183 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v184 = llvm.insertvalue %v181, %v183[0] : !llvm.struct<(f32, f32)>
%v185 = llvm.insertvalue %v182, %v184[1] : !llvm.struct<(f32, f32)>
%v186 = llvm.extractvalue %v185[0] : !llvm.struct<(f32, f32)>
%v187 = arith.extf %v186 : f32 to f64
%v188 = llvm.extractvalue %v185[1] : !llvm.struct<(f32, f32)>
%v189 = arith.extf %v188 : f32 to f64
%v190 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v191 = llvm.call @printf(%v190, %v187, %v189) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v192 = arith.constant 0 : i32
%v193 = llvm.load %v94 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v194 = llvm.load %v96 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v195 = llvm.extractvalue %v193[0] : !llvm.struct<(f32, f32)>
%v196 = llvm.extractvalue %v193[1] : !llvm.struct<(f32, f32)>
%v197 = llvm.extractvalue %v194[0] : !llvm.struct<(f32, f32)>
%v198 = llvm.extractvalue %v194[1] : !llvm.struct<(f32, f32)>
%v199 = arith.mulf %v197, %v197 : f32
%v200 = arith.mulf %v198, %v198 : f32
%v201 = arith.addf %v199, %v200 : f32
%v202 = arith.mulf %v195, %v197 : f32
%v203 = arith.mulf %v196, %v198 : f32
%v204 = arith.mulf %v196, %v197 : f32
%v205 = arith.mulf %v195, %v198 : f32
%v206 = arith.addf %v202, %v203 : f32
%v207 = arith.subf %v204, %v205 : f32
%v208 = arith.divf %v206, %v201 : f32
%v209 = arith.divf %v207, %v201 : f32
%v210 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v211 = llvm.insertvalue %v208, %v210[0] : !llvm.struct<(f32, f32)>
%v212 = llvm.insertvalue %v209, %v211[1] : !llvm.struct<(f32, f32)>
%v213 = llvm.extractvalue %v212[0] : !llvm.struct<(f32, f32)>
%v214 = arith.extf %v213 : f32 to f64
%v215 = llvm.extractvalue %v212[1] : !llvm.struct<(f32, f32)>
%v216 = arith.extf %v215 : f32 to f64
%v217 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v218 = llvm.call @printf(%v217, %v214, %v216) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v219 = arith.constant 0 : i32
%v220 = llvm.load %v94 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v221 = llvm.extractvalue %v220[0] : !llvm.struct<(f32, f32)>
%v222 = arith.negf %v221 : f32
%v223 = llvm.extractvalue %v220[1] : !llvm.struct<(f32, f32)>
%v224 = arith.negf %v223 : f32
%v225 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v226 = llvm.insertvalue %v222, %v225[0] : !llvm.struct<(f32, f32)>
%v227 = llvm.insertvalue %v224, %v226[1] : !llvm.struct<(f32, f32)>
%v228 = llvm.extractvalue %v227[0] : !llvm.struct<(f32, f32)>
%v229 = arith.extf %v228 : f32 to f64
%v230 = llvm.extractvalue %v227[1] : !llvm.struct<(f32, f32)>
%v231 = arith.extf %v230 : f32 to f64
%v232 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v233 = llvm.call @printf(%v232, %v229, %v231) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v234 = arith.constant 0 : i32
%v235 = arith.constant 2.0 : f64
%v236 = arith.truncf %v235 : f64 to f32
%v237 = llvm.load %v94 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v238 = llvm.extractvalue %v237[0] : !llvm.struct<(f32, f32)>
%v239 = llvm.extractvalue %v237[1] : !llvm.struct<(f32, f32)>
%v240 = arith.mulf %v238, %v236 : f32
%v241 = arith.mulf %v239, %v236 : f32
%v242 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v243 = llvm.insertvalue %v240, %v242[0] : !llvm.struct<(f32, f32)>
%v244 = llvm.insertvalue %v241, %v243[1] : !llvm.struct<(f32, f32)>
llvm.store %v244, %v98 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v245 = llvm.load %v94 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v246 = llvm.extractvalue %v245[0] : !llvm.struct<(f32, f32)>
%v247 = llvm.extractvalue %v245[1] : !llvm.struct<(f32, f32)>
%v248 = arith.divf %v246, %v236 : f32
%v249 = arith.divf %v247, %v236 : f32
%v250 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v251 = llvm.insertvalue %v248, %v250[0] : !llvm.struct<(f32, f32)>
%v252 = llvm.insertvalue %v249, %v251[1] : !llvm.struct<(f32, f32)>
llvm.store %v252, %v100 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v253 = arith.constant 0.0 : f32
%v254 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v255 = llvm.insertvalue %v236, %v254[0] : !llvm.struct<(f32, f32)>
%v256 = llvm.insertvalue %v253, %v255[1] : !llvm.struct<(f32, f32)>
%v257 = llvm.load %v94 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v258 = llvm.extractvalue %v256[0] : !llvm.struct<(f32, f32)>
%v259 = llvm.extractvalue %v256[1] : !llvm.struct<(f32, f32)>
%v260 = llvm.extractvalue %v257[0] : !llvm.struct<(f32, f32)>
%v261 = llvm.extractvalue %v257[1] : !llvm.struct<(f32, f32)>
%v262 = arith.mulf %v258, %v260 : f32
%v263 = arith.mulf %v259, %v261 : f32
%v264 = arith.mulf %v258, %v261 : f32
%v265 = arith.mulf %v259, %v260 : f32
%v266 = arith.subf %v262, %v263 : f32
%v267 = arith.addf %v264, %v265 : f32
%v268 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v269 = llvm.insertvalue %v266, %v268[0] : !llvm.struct<(f32, f32)>
%v270 = llvm.insertvalue %v267, %v269[1] : !llvm.struct<(f32, f32)>
llvm.store %v270, %v102 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v271 = llvm.load %v98 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v272 = llvm.extractvalue %v271[0] : !llvm.struct<(f32, f32)>
%v273 = arith.extf %v272 : f32 to f64
%v274 = llvm.extractvalue %v271[1] : !llvm.struct<(f32, f32)>
%v275 = arith.extf %v274 : f32 to f64
%v276 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v277 = llvm.call @printf(%v276, %v273, %v275) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v278 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v279 = llvm.call @printf(%v278) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v280 = llvm.load %v100 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v281 = llvm.extractvalue %v280[0] : !llvm.struct<(f32, f32)>
%v282 = arith.extf %v281 : f32 to f64
%v283 = llvm.extractvalue %v280[1] : !llvm.struct<(f32, f32)>
%v284 = arith.extf %v283 : f32 to f64
%v285 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v286 = llvm.call @printf(%v285, %v282, %v284) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v287 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v288 = llvm.call @printf(%v287) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v289 = llvm.load %v102 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v290 = llvm.extractvalue %v289[0] : !llvm.struct<(f32, f32)>
%v291 = arith.extf %v290 : f32 to f64
%v292 = llvm.extractvalue %v289[1] : !llvm.struct<(f32, f32)>
%v293 = arith.extf %v292 : f32 to f64
%v294 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v295 = llvm.call @printf(%v294, %v291, %v293) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v296 = arith.constant 0 : i32
%v297 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v298 = llvm.load %v94 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v299 = llvm.extractvalue %v298[0] : !llvm.struct<(f32, f32)>
%v300 = llvm.extractvalue %v298[1] : !llvm.struct<(f32, f32)>
%v301 = arith.extf %v299 : f32 to f64
%v302 = llvm.load %v94 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v303 = llvm.extractvalue %v302[0] : !llvm.struct<(f32, f32)>
%v304 = llvm.extractvalue %v302[1] : !llvm.struct<(f32, f32)>
%v305 = arith.extf %v304 : f32 to f64
%v306 = llvm.load %v94 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v307 = llvm.extractvalue %v306[0] : !llvm.struct<(f32, f32)>
%v308 = llvm.extractvalue %v306[1] : !llvm.struct<(f32, f32)>
%v309 = arith.extf %v307 : f32 to f64
%v310 = arith.extf %v308 : f32 to f64
%v311 = arith.mulf %v309, %v309 : f64
%v312 = arith.mulf %v310, %v310 : f64
%v313 = arith.addf %v311, %v312 : f64
%v314 = math.sqrt %v313 : f64
%v315 = arith.truncf %v314 : f64 to f32
%v316 = arith.extf %v315 : f32 to f64
%v317 = llvm.call @printf(%v297, %v301, %v305, %v316) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64, f64) -> i32
%v318 = llvm.load %v96 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v319 = llvm.extractvalue %v318[0] : !llvm.struct<(f32, f32)>
%v320 = llvm.extractvalue %v318[1] : !llvm.struct<(f32, f32)>
%v321 = arith.negf %v320 : f32
%v322 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v323 = llvm.insertvalue %v319, %v322[0] : !llvm.struct<(f32, f32)>
%v324 = llvm.insertvalue %v321, %v323[1] : !llvm.struct<(f32, f32)>
%v325 = llvm.extractvalue %v324[0] : !llvm.struct<(f32, f32)>
%v326 = arith.extf %v325 : f32 to f64
%v327 = llvm.extractvalue %v324[1] : !llvm.struct<(f32, f32)>
%v328 = arith.extf %v327 : f32 to f64
%v329 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v330 = llvm.call @printf(%v329, %v326, %v328) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v331 = arith.constant 0 : i32
%v332 = llvm.load %v94 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v333 = arith.constant 3.0 : f64
%v334 = arith.constant 4.0 : f64
%v335 = arith.truncf %v333 : f64 to f32
%v336 = arith.truncf %v334 : f64 to f32
%v337 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v338 = llvm.insertvalue %v335, %v337[0] : !llvm.struct<(f32, f32)>
%v339 = llvm.insertvalue %v336, %v338[1] : !llvm.struct<(f32, f32)>
%v340 = llvm.extractvalue %v332[0] : !llvm.struct<(f32, f32)>
%v341 = llvm.extractvalue %v332[1] : !llvm.struct<(f32, f32)>
%v342 = llvm.extractvalue %v339[0] : !llvm.struct<(f32, f32)>
%v343 = llvm.extractvalue %v339[1] : !llvm.struct<(f32, f32)>
%v344 = arith.cmpf oeq, %v340, %v342 : f32
%v345 = arith.cmpf oeq, %v341, %v343 : f32
%v346 = arith.andi %v344, %v345 : i1
%v347 = scf.if %v346 -> (i1) {
%v348 = llvm.load %v94 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v349 = llvm.load %v96 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v350 = llvm.extractvalue %v348[0] : !llvm.struct<(f32, f32)>
%v351 = llvm.extractvalue %v348[1] : !llvm.struct<(f32, f32)>
%v352 = llvm.extractvalue %v349[0] : !llvm.struct<(f32, f32)>
%v353 = llvm.extractvalue %v349[1] : !llvm.struct<(f32, f32)>
%v354 = arith.cmpf une, %v350, %v352 : f32
%v355 = arith.cmpf une, %v351, %v353 : f32
%v356 = arith.ori %v354, %v355 : i1
scf.yield %v356 : i1
} else {
%v357 = arith.constant false
scf.yield %v357 : i1
}
cf.cond_br %v347, ^b4, ^b5
^b4:
%v358 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v359 = llvm.call @printf(%v358) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
cf.br ^b6
^b5:
cf.br ^b6
^b6:
%v360 = llvm.load %v94 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v361 = llvm.extractvalue %v360[0] : !llvm.struct<(f32, f32)>
%v362 = llvm.extractvalue %v360[1] : !llvm.struct<(f32, f32)>
%v363 = arith.extf %v361 : f32 to f64
%v364 = llvm.load %v94 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v365 = llvm.extractvalue %v364[0] : !llvm.struct<(f32, f32)>
%v366 = llvm.extractvalue %v364[1] : !llvm.struct<(f32, f32)>
%v367 = arith.extf %v366 : f32 to f64
%v368 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v369 = llvm.insertvalue %v363, %v368[0] : !llvm.struct<(f64, f64)>
%v370 = llvm.insertvalue %v367, %v369[1] : !llvm.struct<(f64, f64)>
llvm.store %v370, %v104 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v371 = arith.constant 0.0 : f64
%v372 = arith.constant 0.0 : f64
%v373 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v374 = llvm.insertvalue %v371, %v373[0] : !llvm.struct<(f64, f64)>
%v375 = llvm.insertvalue %v372, %v374[1] : !llvm.struct<(f64, f64)>
%v376 = llvm.extractvalue %v375[0] : !llvm.struct<(f64, f64)>
%v377 = llvm.extractvalue %v375[1] : !llvm.struct<(f64, f64)>
%v378 = math.exp %v376 : f64
%v379 = math.cos %v377 : f64
%v380 = math.sin %v377 : f64
%v381 = arith.mulf %v378, %v379 : f64
%v382 = arith.mulf %v378, %v380 : f64
%v383 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v384 = llvm.insertvalue %v381, %v383[0] : !llvm.struct<(f64, f64)>
%v385 = llvm.insertvalue %v382, %v384[1] : !llvm.struct<(f64, f64)>
llvm.store %v385, %v106 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v386 = llvm.load %v104 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v387 = llvm.load %v106 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v388 = llvm.extractvalue %v386[0] : !llvm.struct<(f64, f64)>
%v389 = llvm.extractvalue %v386[1] : !llvm.struct<(f64, f64)>
%v390 = llvm.extractvalue %v387[0] : !llvm.struct<(f64, f64)>
%v391 = llvm.extractvalue %v387[1] : !llvm.struct<(f64, f64)>
%v392 = arith.mulf %v388, %v390 : f64
%v393 = arith.mulf %v389, %v391 : f64
%v394 = arith.mulf %v388, %v391 : f64
%v395 = arith.mulf %v389, %v390 : f64
%v396 = arith.subf %v392, %v393 : f64
%v397 = arith.addf %v394, %v395 : f64
%v398 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v399 = llvm.insertvalue %v396, %v398[0] : !llvm.struct<(f64, f64)>
%v400 = llvm.insertvalue %v397, %v399[1] : !llvm.struct<(f64, f64)>
%v401 = llvm.extractvalue %v400[0] : !llvm.struct<(f64, f64)>
%v402 = llvm.extractvalue %v400[1] : !llvm.struct<(f64, f64)>
%v403 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v404 = llvm.call @printf(%v403, %v401, %v402) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v405 = arith.constant 0 : i32
%v406 = llvm.load %v94 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v407 = llvm.extractvalue %v406[0] : !llvm.struct<(f32, f32)>
%v408 = arith.extf %v407 : f32 to f64
%v409 = llvm.extractvalue %v406[1] : !llvm.struct<(f32, f32)>
%v410 = arith.extf %v409 : f32 to f64
%v411 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v412 = llvm.insertvalue %v408, %v411[0] : !llvm.struct<(f64, f64)>
%v413 = llvm.insertvalue %v410, %v412[1] : !llvm.struct<(f64, f64)>
llvm.store %v413, %v108 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v414 = llvm.load %v108 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v415 = llvm.extractvalue %v414[0] : !llvm.struct<(f64, f64)>
%v416 = llvm.extractvalue %v414[1] : !llvm.struct<(f64, f64)>
%v417 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v418 = llvm.call @printf(%v417, %v415, %v416) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v419 = arith.constant 0 : i32
%v420 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v421 = arith.constant 1.0 : f64
%v422 = arith.constant 0.0 : f64
%v423 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v424 = llvm.insertvalue %v421, %v423[0] : !llvm.struct<(f64, f64)>
%v425 = llvm.insertvalue %v422, %v424[1] : !llvm.struct<(f64, f64)>
%v426 = llvm.insertvalue %v425, %v420[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v427 = arith.constant 0 : i32
%v428 = llvm.insertvalue %v427, %v426[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v429 = arith.constant 0.0 : f64
%v430 = arith.constant 1.0 : f64
%v431 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v432 = llvm.insertvalue %v429, %v431[0] : !llvm.struct<(f64, f64)>
%v433 = llvm.insertvalue %v430, %v432[1] : !llvm.struct<(f64, f64)>
%v434 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v435 = llvm.extractvalue %v428[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v436 = llvm.insertvalue %v435, %v434[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v437 = llvm.extractvalue %v428[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v438 = llvm.insertvalue %v437, %v436[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v439 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v440 = llvm.extractvalue %v433[0] : !llvm.struct<(f64, f64)>
%v441 = llvm.insertvalue %v440, %v439[0] : !llvm.struct<(f64, f64)>
%v442 = llvm.extractvalue %v433[1] : !llvm.struct<(f64, f64)>
%v443 = llvm.insertvalue %v442, %v441[1] : !llvm.struct<(f64, f64)>
%v444 = func.call @rotate(%v438, %v443) : (!llvm.struct<(!llvm.struct<(f64, f64)>, i32)>, !llvm.struct<(f64, f64)>) -> !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v445 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v446 = llvm.extractvalue %v444[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v447 = llvm.insertvalue %v446, %v445[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v448 = llvm.extractvalue %v444[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v449 = llvm.insertvalue %v448, %v447[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
llvm.store %v449, %v110 : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>, !llvm.ptr
%v450 = llvm.load %v110 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
llvm.store %v450, %v112 : !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>, !llvm.ptr
%v451 = llvm.mlir.addressof @str_5 : !llvm.ptr
%v452 = llvm.load %v112 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v453 = llvm.getelementptr %v112[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v454 = llvm.load %v453 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v455 = llvm.extractvalue %v454[0] : !llvm.struct<(f64, f64)>
%v456 = llvm.extractvalue %v454[1] : !llvm.struct<(f64, f64)>
%v457 = llvm.load %v112 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v458 = llvm.getelementptr %v112[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v459 = llvm.load %v458 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v460 = llvm.extractvalue %v459[0] : !llvm.struct<(f64, f64)>
%v461 = llvm.extractvalue %v459[1] : !llvm.struct<(f64, f64)>
%v462 = llvm.load %v112 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v463 = llvm.getelementptr %v112[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, i32)>
%v464 = llvm.load %v463 : !llvm.ptr -> i32
%v465 = llvm.call @printf(%v451, %v455, %v461, %v464) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64, i32) -> i32
%v466 = arith.constant 1.0 : f64
%v467 = arith.constant 1.0 : f64
%v468 = arith.truncf %v466 : f64 to f32
%v469 = arith.truncf %v467 : f64 to f32
%v470 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v471 = llvm.insertvalue %v468, %v470[0] : !llvm.struct<(f32, f32)>
%v472 = llvm.insertvalue %v469, %v471[1] : !llvm.struct<(f32, f32)>
%v473 = arith.constant 2.0 : f64
%v474 = arith.constant 1.0 : f64
%v475 = arith.negf %v474 : f64
%v476 = arith.truncf %v473 : f64 to f32
%v477 = arith.truncf %v475 : f64 to f32
%v478 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v479 = llvm.insertvalue %v476, %v478[0] : !llvm.struct<(f32, f32)>
%v480 = llvm.insertvalue %v477, %v479[1] : !llvm.struct<(f32, f32)>
%v481 = arith.constant 0.5 : f64
%v482 = arith.constant 0.25 : f64
%v483 = arith.truncf %v481 : f64 to f32
%v484 = arith.truncf %v482 : f64 to f32
%v485 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v486 = llvm.insertvalue %v483, %v485[0] : !llvm.struct<(f32, f32)>
%v487 = llvm.insertvalue %v484, %v486[1] : !llvm.struct<(f32, f32)>
%v488 = arith.constant 24 : i64
func.call @flow_mem_note_stack(%v488) : (i64) -> ()
%v489 = llvm.mlir.zero : !llvm.array<3 x !llvm.struct<(f32, f32)>>
llvm.store %v489, %v114 : !llvm.array<3 x !llvm.struct<(f32, f32)>>, !llvm.ptr
%v490 = llvm.mlir.constant(0 : i64) : i64
%v491 = llvm.getelementptr %v114[0, %v490] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(f32, f32)>>
llvm.store %v472, %v491 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v492 = llvm.mlir.constant(1 : i64) : i64
%v493 = llvm.getelementptr %v114[0, %v492] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(f32, f32)>>
llvm.store %v480, %v493 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v494 = llvm.mlir.constant(2 : i64) : i64
%v495 = llvm.getelementptr %v114[0, %v494] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(f32, f32)>>
llvm.store %v487, %v495 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v496 = arith.constant 3 : i32
%v497 = func.call @sum(%v114, %v496) : (!llvm.ptr, i32) -> !llvm.struct<(f32, f32)>
%v498 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v499 = llvm.extractvalue %v497[0] : !llvm.struct<(f32, f32)>
%v500 = llvm.insertvalue %v499, %v498[0] : !llvm.struct<(f32, f32)>
%v501 = llvm.extractvalue %v497[1] : !llvm.struct<(f32, f32)>
%v502 = llvm.insertvalue %v501, %v500[1] : !llvm.struct<(f32, f32)>
llvm.store %v502, %v116 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v503 = llvm.load %v116 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v504 = llvm.extractvalue %v503[0] : !llvm.struct<(f32, f32)>
%v505 = arith.extf %v504 : f32 to f64
%v506 = llvm.extractvalue %v503[1] : !llvm.struct<(f32, f32)>
%v507 = arith.extf %v506 : f32 to f64
%v508 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v509 = llvm.call @printf(%v508, %v505, %v507) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v510 = arith.constant 0 : i32
%v511 = llvm.load %v94 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v512 = llvm.load %v96 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v513 = arith.constant 16 : i64
func.call @flow_mem_note_stack(%v513) : (i64) -> ()
%v514 = llvm.mlir.zero : !llvm.array<2 x !llvm.struct<(f32, f32)>>
llvm.store %v514, %v118 : !llvm.array<2 x !llvm.struct<(f32, f32)>>, !llvm.ptr
%v515 = llvm.mlir.constant(0 : i64) : i64
%v516 = llvm.getelementptr %v118[0, %v515] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x !llvm.struct<(f32, f32)>>
llvm.store %v511, %v516 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v517 = llvm.mlir.constant(1 : i64) : i64
%v518 = llvm.getelementptr %v118[0, %v517] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x !llvm.struct<(f32, f32)>>
llvm.store %v512, %v518 : !llvm.struct<(f32, f32)>, !llvm.ptr
llvm.store %v118, %v120 : !llvm.ptr, !llvm.ptr
%v519 = llvm.load %v96 : !llvm.ptr -> !llvm.struct<(f32, f32)>
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
%v540 = llvm.load %v120 : !llvm.ptr -> !llvm.ptr
%v541 = arith.constant 1 : i32
%v542 = arith.extsi %v541 : i32 to i64
%v543 = llvm.getelementptr %v540[0, %v542] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x !llvm.struct<(f32, f32)>>
llvm.store %v539, %v543 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v544 = llvm.load %v120 : !llvm.ptr -> !llvm.ptr
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
%v557 = llvm.load %v120 : !llvm.ptr -> !llvm.ptr
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
