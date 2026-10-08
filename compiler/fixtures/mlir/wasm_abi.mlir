module {
func.func private @memcpy(!llvm.ptr, !llvm.ptr, i64) -> !llvm.ptr
func.func private @free(!llvm.ptr) -> ()
func.func private @malloc(i64) -> !llvm.ptr
func.func private @memset(!llvm.ptr, i32, i64) -> !llvm.ptr
func.func private @strlen(!llvm.ptr) -> i64
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
%v10 = llvm.mlir.constant(1 : i64) : i64
%v11 = llvm.alloca %v10 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v9, %v11 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v12 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v13 = llvm.extractvalue %arg1[0] : !llvm.struct<(i32, i32)>
%v14 = llvm.insertvalue %v13, %v12[0] : !llvm.struct<(i32, i32)>
%v15 = llvm.extractvalue %arg1[1] : !llvm.struct<(i32, i32)>
%v16 = llvm.insertvalue %v15, %v14[1] : !llvm.struct<(i32, i32)>
%v17 = llvm.mlir.constant(1 : i64) : i64
%v18 = llvm.alloca %v17 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v16, %v18 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v19 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v20 = llvm.load %v11 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v21 = llvm.getelementptr %v11[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v22 = llvm.load %v21 : !llvm.ptr -> i32
%v23 = llvm.load %v18 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v24 = llvm.getelementptr %v18[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v25 = llvm.load %v24 : !llvm.ptr -> i32
%v26 = arith.addi %v22, %v25 : i32
%v27 = arith.constant 2 : i32
%v28 = arith.divsi %v26, %v27 : i32
%v29 = llvm.insertvalue %v28, %v19[0] : !llvm.struct<(i32, i32)>
%v30 = llvm.load %v11 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v31 = llvm.getelementptr %v11[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v32 = llvm.load %v31 : !llvm.ptr -> i32
%v33 = llvm.load %v18 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v34 = llvm.getelementptr %v18[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v35 = llvm.load %v34 : !llvm.ptr -> i32
%v36 = arith.addi %v32, %v35 : i32
%v37 = arith.constant 2 : i32
%v38 = arith.divsi %v36, %v37 : i32
%v39 = llvm.insertvalue %v38, %v29[1] : !llvm.struct<(i32, i32)>
%v40 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v41 = llvm.extractvalue %v39[0] : !llvm.struct<(i32, i32)>
%v42 = llvm.insertvalue %v41, %v40[0] : !llvm.struct<(i32, i32)>
%v43 = llvm.extractvalue %v39[1] : !llvm.struct<(i32, i32)>
%v44 = llvm.insertvalue %v43, %v42[1] : !llvm.struct<(i32, i32)>
%v45 = llvm.mlir.constant(1 : i64) : i64
%v46 = llvm.alloca %v45 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v44, %v46 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v47 = llvm.load %v46 : !llvm.ptr -> !llvm.struct<(i32, i32)>
func.return %v47 : !llvm.struct<(i32, i32)>
}
func.func @apply(%arg0: !llvm.struct<(!llvm.ptr, !llvm.ptr)>, %arg1: i32) -> i32 {
%v48 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v49 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v50 = llvm.insertvalue %v49, %v48[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v51 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v52 = llvm.insertvalue %v51, %v50[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v53 = llvm.mlir.constant(1 : i64) : i64
%v54 = llvm.alloca %v53 x !llvm.struct<(!llvm.ptr, !llvm.ptr)> : (i64) -> !llvm.ptr
llvm.store %v52, %v54 : !llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.ptr
%v55 = llvm.load %v54 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v56 = llvm.extractvalue %v55[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v57 = llvm.extractvalue %v55[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v58 = llvm.call %v56(%v57, %arg1) : !llvm.ptr, (!llvm.ptr, i32) -> i32
func.return %v58 : i32
}
func.func @main() -> i32 {
%v59 = arith.constant 16 : i32
%v60 = arith.extsi %v59 : i32 to i64
%v61 = func.call @flow_mem_malloc(%v60) : (i64) -> !llvm.ptr
%v62 = arith.constant 0 : i32
%v63 = arith.constant 16 : i32
%v64 = arith.extsi %v63 : i32 to i64
%v65 = func.call @memset(%v61, %v62, %v64) : (!llvm.ptr, i32, i64) -> !llvm.ptr
%v66 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v67 = func.call @strlen(%v66) : (!llvm.ptr) -> i64
%v68 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v69 = arith.constant 0 : i32
%v70 = llvm.insertvalue %v69, %v68[0] : !llvm.struct<(i32, i32)>
%v71 = arith.constant 0 : i32
%v72 = llvm.insertvalue %v71, %v70[1] : !llvm.struct<(i32, i32)>
%v73 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v74 = arith.constant 4 : i32
%v75 = llvm.insertvalue %v74, %v73[0] : !llvm.struct<(i32, i32)>
%v76 = arith.constant 6 : i32
%v77 = llvm.insertvalue %v76, %v75[1] : !llvm.struct<(i32, i32)>
%v78 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v79 = llvm.extractvalue %v72[0] : !llvm.struct<(i32, i32)>
%v80 = llvm.insertvalue %v79, %v78[0] : !llvm.struct<(i32, i32)>
%v81 = llvm.extractvalue %v72[1] : !llvm.struct<(i32, i32)>
%v82 = llvm.insertvalue %v81, %v80[1] : !llvm.struct<(i32, i32)>
%v83 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v84 = llvm.extractvalue %v77[0] : !llvm.struct<(i32, i32)>
%v85 = llvm.insertvalue %v84, %v83[0] : !llvm.struct<(i32, i32)>
%v86 = llvm.extractvalue %v77[1] : !llvm.struct<(i32, i32)>
%v87 = llvm.insertvalue %v86, %v85[1] : !llvm.struct<(i32, i32)>
%v88 = func.call @mid(%v82, %v87) : (!llvm.struct<(i32, i32)>, !llvm.struct<(i32, i32)>) -> !llvm.struct<(i32, i32)>
%v89 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v90 = llvm.extractvalue %v88[0] : !llvm.struct<(i32, i32)>
%v91 = llvm.insertvalue %v90, %v89[0] : !llvm.struct<(i32, i32)>
%v92 = llvm.extractvalue %v88[1] : !llvm.struct<(i32, i32)>
%v93 = llvm.insertvalue %v92, %v91[1] : !llvm.struct<(i32, i32)>
%v94 = llvm.mlir.constant(1 : i64) : i64
%v95 = llvm.alloca %v94 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v93, %v95 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v96 = llvm.load %v95 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v97 = llvm.mlir.constant(1 : i64) : i64
%v98 = llvm.alloca %v97 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v96, %v98 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v99 = arith.constant 5 : i32
%v100 = llvm.mlir.zero : !llvm.ptr
%v101 = llvm.getelementptr %v100[1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32)>
%v102 = llvm.ptrtoint %v101 : !llvm.ptr to i64
%v103 = func.call @flow_mem_malloc(%v102) : (i64) -> !llvm.ptr
%v104 = llvm.getelementptr %v103[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32)>
llvm.store %v99, %v104 : i32, !llvm.ptr
%v105 = func.constant @lambda_1 : (!llvm.ptr, i32) -> i32
%v106 = builtin.unrealized_conversion_cast %v105 : (!llvm.ptr, i32) -> i32 to !llvm.ptr
%v107 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v108 = llvm.insertvalue %v106, %v107[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v109 = llvm.insertvalue %v103, %v108[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v110 = arith.constant 2 : i32
%v111 = func.call @apply(%v109, %v110) : (!llvm.struct<(!llvm.ptr, !llvm.ptr)>, i32) -> i32
%v112 = arith.trunci %v67 : i64 to i32
%v113 = llvm.load %v98 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v114 = llvm.getelementptr %v98[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v115 = llvm.load %v114 : !llvm.ptr -> i32
%v116 = arith.addi %v112, %v115 : i32
%v117 = llvm.load %v98 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v118 = llvm.getelementptr %v98[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v119 = llvm.load %v118 : !llvm.ptr -> i32
%v120 = arith.addi %v116, %v119 : i32
%v121 = arith.addi %v120, %v111 : i32
func.return %v121 : i32
}
}
