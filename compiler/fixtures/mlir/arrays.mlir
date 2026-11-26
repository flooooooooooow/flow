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
llvm.mlir.global internal constant @str_12("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_13("%lld\0A\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
llvm.mlir.global internal constant @str_14("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_15("first\0A\00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
func.func @total(%arg0: !llvm.ptr) -> i32 {
%v1 = llvm.mlir.constant(1 : i64) : i64
%v2 = llvm.alloca %v1 x i32 : (i64) -> !llvm.ptr
%v3 = llvm.mlir.constant(1 : i64) : i64
%v4 = llvm.alloca %v3 x i32 : (i64) -> !llvm.ptr
%v5 = arith.constant 0 : i32
llvm.store %v5, %v2 : i32, !llvm.ptr
%v6 = arith.constant 0 : i32
llvm.store %v6, %v4 : i32, !llvm.ptr
cf.br ^b1
^b1:
%v7 = llvm.load %v4 : !llvm.ptr -> i32
%v8 = arith.constant 5 : i32
%v9 = arith.cmpi slt, %v7, %v8 : i32
cf.cond_br %v9, ^b2, ^b3
^b2:
%v10 = llvm.load %v2 : !llvm.ptr -> i32
%v11 = llvm.load %v4 : !llvm.ptr -> i32
%v12 = arith.extsi %v11 : i32 to i64
%v13 = llvm.getelementptr %arg0[0, %v12] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
%v14 = llvm.load %v13 : !llvm.ptr -> i32
%v15 = arith.addi %v10, %v14 : i32
llvm.store %v15, %v2 : i32, !llvm.ptr
%v16 = llvm.load %v4 : !llvm.ptr -> i32
%v17 = arith.constant 1 : i32
%v18 = arith.addi %v16, %v17 : i32
llvm.store %v18, %v4 : i32, !llvm.ptr
cf.br ^b1
^b3:
%v19 = llvm.load %v2 : !llvm.ptr -> i32
func.return %v19 : i32
}
func.func @scale(%arg0: !llvm.ptr, %arg1: i32, %arg2: f64) -> f64 {
%v20 = llvm.mlir.constant(1 : i64) : i64
%v21 = llvm.alloca %v20 x f64 : (i64) -> !llvm.ptr
%v22 = arith.constant 0.0 : f64
llvm.store %v22, %v21 : f64, !llvm.ptr
%v23 = arith.constant 0 : i32
%v24 = arith.index_cast %v23 : i32 to index
%v25 = arith.index_cast %arg1 : i32 to index
%v26 = arith.constant 1 : index
%v27 = arith.constant -1 : index
%v28 = arith.cmpi sle, %v24, %v25 : index
%v29 = arith.select %v28, %v26, %v27 : index
cf.br ^b4(%v24 : index)
^b4(%v30: index):
%v31 = arith.cmpi slt, %v30, %v25 : index
%v32 = arith.cmpi sgt, %v30, %v25 : index
%v33 = arith.select %v28, %v31, %v32 : i1
cf.cond_br %v33, ^b5(%v30 : index), ^b6(%v30 : index)
^b5(%v34: index):
%v35 = llvm.load %v21 : !llvm.ptr -> f64
%v36 = arith.index_cast %v34 : index to i64
%v37 = llvm.getelementptr %arg0[%v36] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v38 = llvm.load %v37 : !llvm.ptr -> f64
%v39 = llvm.intr.fmuladd(%v38, %arg2, %v35) : (f64, f64, f64) -> f64
llvm.store %v39, %v21 : f64, !llvm.ptr
%v40 = arith.addi %v34, %v29 : index
cf.br ^b4(%v40 : index)
^b6(%v41: index):
%v42 = llvm.load %v21 : !llvm.ptr -> f64
func.return %v42 : f64
}
func.func @main() -> i32 {
%v43 = llvm.mlir.constant(1 : i64) : i64
%v44 = llvm.alloca %v43 x !llvm.array<5 x i32> : (i64) -> !llvm.ptr
%v45 = llvm.mlir.constant(1 : i64) : i64
%v46 = llvm.alloca %v45 x !llvm.array<3 x i64> : (i64) -> !llvm.ptr
%v47 = llvm.mlir.constant(1 : i64) : i64
%v48 = llvm.alloca %v47 x i64 : (i64) -> !llvm.ptr
%v49 = llvm.mlir.constant(1 : i64) : i64
%v50 = llvm.alloca %v49 x !llvm.array<4 x f64> : (i64) -> !llvm.ptr
%v51 = llvm.mlir.constant(1 : i64) : i64
%v52 = llvm.alloca %v51 x !llvm.array<2 x i1> : (i64) -> !llvm.ptr
%v53 = arith.constant 3 : i32
%v54 = arith.constant 1 : i32
%v55 = arith.constant 4 : i32
%v56 = arith.constant 1 : i32
%v57 = arith.constant 5 : i32
%v58 = arith.constant 20 : i64
func.call @flow_mem_note_stack(%v58) : (i64) -> ()
%v59 = llvm.mlir.zero : !llvm.array<5 x i32>
llvm.store %v59, %v44 : !llvm.array<5 x i32>, !llvm.ptr
%v60 = llvm.mlir.constant(0 : i64) : i64
%v61 = llvm.getelementptr %v44[0, %v60] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v53, %v61 : i32, !llvm.ptr
%v62 = llvm.mlir.constant(1 : i64) : i64
%v63 = llvm.getelementptr %v44[0, %v62] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v54, %v63 : i32, !llvm.ptr
%v64 = llvm.mlir.constant(2 : i64) : i64
%v65 = llvm.getelementptr %v44[0, %v64] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v55, %v65 : i32, !llvm.ptr
%v66 = llvm.mlir.constant(3 : i64) : i64
%v67 = llvm.getelementptr %v44[0, %v66] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v56, %v67 : i32, !llvm.ptr
%v68 = llvm.mlir.constant(4 : i64) : i64
%v69 = llvm.getelementptr %v44[0, %v68] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v57, %v69 : i32, !llvm.ptr
%v70 = func.call @total(%v44) : (!llvm.ptr) -> i32
%v71 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v72 = llvm.call @printf(%v71, %v70) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v73 = arith.constant 0 : i32
%v74 = arith.constant 40 : i32
%v75 = arith.constant 2 : i32
%v76 = arith.extsi %v75 : i32 to i64
%v77 = llvm.getelementptr %v44[0, %v76] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v74, %v77 : i32, !llvm.ptr
%v78 = arith.constant 4 : i32
%v79 = arith.extsi %v78 : i32 to i64
%v80 = llvm.getelementptr %v44[0, %v79] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
%v81 = llvm.load %v80 : !llvm.ptr -> i32
%v82 = arith.constant 100 : i32
%v83 = arith.addi %v81, %v82 : i32
%v84 = arith.extsi %v78 : i32 to i64
%v85 = llvm.getelementptr %v44[0, %v84] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v83, %v85 : i32, !llvm.ptr
%v86 = func.call @total(%v44) : (!llvm.ptr) -> i32
%v87 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v88 = llvm.call @printf(%v87, %v86) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v89 = arith.constant 0 : i32
%v90 = arith.constant 2 : i32
%v91 = arith.extsi %v90 : i32 to i64
%v92 = llvm.getelementptr %v44[0, %v91] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
%v93 = llvm.load %v92 : !llvm.ptr -> i32
%v94 = arith.constant 4 : i32
%v95 = arith.extsi %v94 : i32 to i64
%v96 = llvm.getelementptr %v44[0, %v95] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
%v97 = llvm.load %v96 : !llvm.ptr -> i32
%v98 = arith.addi %v93, %v97 : i32
%v99 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v100 = llvm.call @printf(%v99, %v98) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v101 = arith.constant 0 : i32
%v102 = arith.constant 1 : i32
%v103 = arith.constant 2 : i32
%v104 = arith.constant 3 : i32
%v105 = arith.constant 24 : i64
func.call @flow_mem_note_stack(%v105) : (i64) -> ()
%v106 = llvm.mlir.zero : !llvm.array<3 x i64>
llvm.store %v106, %v46 : !llvm.array<3 x i64>, !llvm.ptr
%v107 = arith.extsi %v102 : i32 to i64
%v108 = arith.extsi %v103 : i32 to i64
%v109 = arith.extsi %v104 : i32 to i64
%v110 = llvm.mlir.constant(0 : i64) : i64
%v111 = llvm.getelementptr %v46[0, %v110] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
llvm.store %v107, %v111 : i64, !llvm.ptr
%v112 = llvm.mlir.constant(1 : i64) : i64
%v113 = llvm.getelementptr %v46[0, %v112] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
llvm.store %v108, %v113 : i64, !llvm.ptr
%v114 = llvm.mlir.constant(2 : i64) : i64
%v115 = llvm.getelementptr %v46[0, %v114] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
llvm.store %v109, %v115 : i64, !llvm.ptr
%v116 = arith.constant 0 : i32
%v117 = arith.extsi %v116 : i32 to i64
llvm.store %v117, %v48 : i64, !llvm.ptr
%v118 = arith.constant 0 : i32
%v119 = arith.constant 3 : i32
%v120 = arith.index_cast %v118 : i32 to index
%v121 = arith.index_cast %v119 : i32 to index
%v122 = arith.constant 1 : index
%v123 = arith.constant -1 : index
%v124 = arith.cmpi sle, %v120, %v121 : index
%v125 = arith.select %v124, %v122, %v123 : index
cf.br ^b7(%v120 : index)
^b7(%v126: index):
%v127 = arith.cmpi slt, %v126, %v121 : index
%v128 = arith.cmpi sgt, %v126, %v121 : index
%v129 = arith.select %v124, %v127, %v128 : i1
cf.cond_br %v129, ^b8(%v126 : index), ^b9(%v126 : index)
^b8(%v130: index):
%v131 = llvm.load %v48 : !llvm.ptr -> i64
%v132 = arith.index_cast %v130 : index to i64
%v133 = llvm.getelementptr %v46[0, %v132] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
%v134 = llvm.load %v133 : !llvm.ptr -> i64
%v135 = arith.constant 1000000 : i32
%v136 = arith.extsi %v135 : i32 to i64
%v137 = arith.muli %v134, %v136 : i64
%v138 = arith.addi %v131, %v137 : i64
llvm.store %v138, %v48 : i64, !llvm.ptr
%v139 = arith.addi %v130, %v125 : index
cf.br ^b7(%v139 : index)
^b9(%v140: index):
%v141 = llvm.load %v48 : !llvm.ptr -> i64
%v142 = llvm.mlir.addressof @str_13 : !llvm.ptr
%v143 = llvm.call @printf(%v142, %v141) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v144 = arith.constant 0 : i32
%v145 = arith.constant 0.5 : f64
%v146 = arith.constant 1.5 : f64
%v147 = arith.constant 2.5 : f64
%v148 = arith.constant 3.5 : f64
%v149 = arith.constant 32 : i64
func.call @flow_mem_note_stack(%v149) : (i64) -> ()
%v150 = llvm.mlir.zero : !llvm.array<4 x f64>
llvm.store %v150, %v50 : !llvm.array<4 x f64>, !llvm.ptr
%v151 = llvm.mlir.constant(0 : i64) : i64
%v152 = llvm.getelementptr %v50[0, %v151] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v145, %v152 : f64, !llvm.ptr
%v153 = llvm.mlir.constant(1 : i64) : i64
%v154 = llvm.getelementptr %v50[0, %v153] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v146, %v154 : f64, !llvm.ptr
%v155 = llvm.mlir.constant(2 : i64) : i64
%v156 = llvm.getelementptr %v50[0, %v155] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v147, %v156 : f64, !llvm.ptr
%v157 = llvm.mlir.constant(3 : i64) : i64
%v158 = llvm.getelementptr %v50[0, %v157] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v148, %v158 : f64, !llvm.ptr
%v159 = arith.constant 4 : i32
%v160 = arith.constant 2.0 : f64
%v161 = func.call @scale(%v50, %v159, %v160) : (!llvm.ptr, i32, f64) -> f64
%v162 = llvm.mlir.addressof @str_14 : !llvm.ptr
%v163 = llvm.call @printf(%v162, %v161) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v164 = arith.constant 0 : i32
%v165 = arith.constant 1 : i1
%v166 = arith.constant 0 : i1
%v167 = arith.constant 2 : i64
func.call @flow_mem_note_stack(%v167) : (i64) -> ()
%v168 = llvm.mlir.zero : !llvm.array<2 x i1>
llvm.store %v168, %v52 : !llvm.array<2 x i1>, !llvm.ptr
%v169 = llvm.mlir.constant(0 : i64) : i64
%v170 = llvm.getelementptr %v52[0, %v169] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x i1>
llvm.store %v165, %v170 : i1, !llvm.ptr
%v171 = llvm.mlir.constant(1 : i64) : i64
%v172 = llvm.getelementptr %v52[0, %v171] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x i1>
llvm.store %v166, %v172 : i1, !llvm.ptr
%v173 = arith.constant 0 : i32
%v174 = arith.extsi %v173 : i32 to i64
%v175 = llvm.getelementptr %v52[0, %v174] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x i1>
%v176 = llvm.load %v175 : !llvm.ptr -> i1
cf.cond_br %v176, ^b10, ^b11
^b10:
%v177 = llvm.mlir.addressof @str_15 : !llvm.ptr
%v178 = llvm.call @printf(%v177) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v179 = arith.constant 0 : i32
cf.br ^b12
^b11:
cf.br ^b12
^b12:
%v180 = arith.constant 0 : i32
func.return %v180 : i32
}
}
