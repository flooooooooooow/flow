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
%v1 = arith.constant 0 : i32
%v2 = llvm.mlir.constant(1 : i64) : i64
%v3 = llvm.alloca %v2 x i32 : (i64) -> !llvm.ptr
llvm.store %v1, %v3 : i32, !llvm.ptr
%v4 = arith.constant 0 : i32
%v5 = llvm.mlir.constant(1 : i64) : i64
%v6 = llvm.alloca %v5 x i32 : (i64) -> !llvm.ptr
llvm.store %v4, %v6 : i32, !llvm.ptr
cf.br ^b1
^b1:
%v7 = llvm.load %v6 : !llvm.ptr -> i32
%v8 = arith.constant 5 : i32
%v9 = arith.cmpi slt, %v7, %v8 : i32
cf.cond_br %v9, ^b2, ^b3
^b2:
%v10 = llvm.load %v3 : !llvm.ptr -> i32
%v11 = llvm.load %v6 : !llvm.ptr -> i32
%v12 = arith.extsi %v11 : i32 to i64
%v13 = llvm.getelementptr %arg0[0, %v12] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
%v14 = llvm.load %v13 : !llvm.ptr -> i32
%v15 = arith.addi %v10, %v14 : i32
llvm.store %v15, %v3 : i32, !llvm.ptr
%v16 = llvm.load %v6 : !llvm.ptr -> i32
%v17 = arith.constant 1 : i32
%v18 = arith.addi %v16, %v17 : i32
llvm.store %v18, %v6 : i32, !llvm.ptr
cf.br ^b1
^b3:
%v19 = llvm.load %v3 : !llvm.ptr -> i32
func.return %v19 : i32
}
func.func @scale(%arg0: !llvm.ptr, %arg1: i32, %arg2: f64) -> f64 {
%v20 = arith.constant 0.0 : f64
%v21 = llvm.mlir.constant(1 : i64) : i64
%v22 = llvm.alloca %v21 x f64 : (i64) -> !llvm.ptr
llvm.store %v20, %v22 : f64, !llvm.ptr
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
%v35 = llvm.load %v22 : !llvm.ptr -> f64
%v36 = arith.index_cast %v34 : index to i64
%v37 = llvm.getelementptr %arg0[%v36] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v38 = llvm.load %v37 : !llvm.ptr -> f64
%v39 = llvm.intr.fmuladd(%v38, %arg2, %v35) : (f64, f64, f64) -> f64
llvm.store %v39, %v22 : f64, !llvm.ptr
%v40 = arith.addi %v34, %v29 : index
cf.br ^b4(%v40 : index)
^b6(%v41: index):
%v42 = llvm.load %v22 : !llvm.ptr -> f64
func.return %v42 : f64
}
func.func @main() -> i32 {
%v43 = arith.constant 3 : i32
%v44 = arith.constant 1 : i32
%v45 = arith.constant 4 : i32
%v46 = arith.constant 1 : i32
%v47 = arith.constant 5 : i32
%v48 = llvm.mlir.constant(1 : i64) : i64
%v49 = llvm.alloca %v48 x !llvm.array<5 x i32> : (i64) -> !llvm.ptr
%v50 = arith.constant 20 : i64
func.call @flow_mem_note_stack(%v50) : (i64) -> ()
%v51 = llvm.mlir.zero : !llvm.array<5 x i32>
llvm.store %v51, %v49 : !llvm.array<5 x i32>, !llvm.ptr
%v52 = llvm.mlir.constant(0 : i64) : i64
%v53 = llvm.getelementptr %v49[0, %v52] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v43, %v53 : i32, !llvm.ptr
%v54 = llvm.mlir.constant(1 : i64) : i64
%v55 = llvm.getelementptr %v49[0, %v54] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v44, %v55 : i32, !llvm.ptr
%v56 = llvm.mlir.constant(2 : i64) : i64
%v57 = llvm.getelementptr %v49[0, %v56] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v45, %v57 : i32, !llvm.ptr
%v58 = llvm.mlir.constant(3 : i64) : i64
%v59 = llvm.getelementptr %v49[0, %v58] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v46, %v59 : i32, !llvm.ptr
%v60 = llvm.mlir.constant(4 : i64) : i64
%v61 = llvm.getelementptr %v49[0, %v60] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v47, %v61 : i32, !llvm.ptr
%v62 = func.call @total(%v49) : (!llvm.ptr) -> i32
%v63 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v64 = llvm.call @printf(%v63, %v62) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v65 = arith.constant 0 : i32
%v66 = arith.constant 40 : i32
%v67 = arith.constant 2 : i32
%v68 = arith.extsi %v67 : i32 to i64
%v69 = llvm.getelementptr %v49[0, %v68] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v66, %v69 : i32, !llvm.ptr
%v70 = arith.constant 4 : i32
%v71 = arith.extsi %v70 : i32 to i64
%v72 = llvm.getelementptr %v49[0, %v71] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
%v73 = llvm.load %v72 : !llvm.ptr -> i32
%v74 = arith.constant 100 : i32
%v75 = arith.addi %v73, %v74 : i32
%v76 = arith.extsi %v70 : i32 to i64
%v77 = llvm.getelementptr %v49[0, %v76] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v75, %v77 : i32, !llvm.ptr
%v78 = func.call @total(%v49) : (!llvm.ptr) -> i32
%v79 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v80 = llvm.call @printf(%v79, %v78) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v81 = arith.constant 0 : i32
%v82 = arith.constant 2 : i32
%v83 = arith.extsi %v82 : i32 to i64
%v84 = llvm.getelementptr %v49[0, %v83] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
%v85 = llvm.load %v84 : !llvm.ptr -> i32
%v86 = arith.constant 4 : i32
%v87 = arith.extsi %v86 : i32 to i64
%v88 = llvm.getelementptr %v49[0, %v87] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
%v89 = llvm.load %v88 : !llvm.ptr -> i32
%v90 = arith.addi %v85, %v89 : i32
%v91 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v92 = llvm.call @printf(%v91, %v90) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v93 = arith.constant 0 : i32
%v94 = arith.constant 1 : i32
%v95 = arith.constant 2 : i32
%v96 = arith.constant 3 : i32
%v97 = llvm.mlir.constant(1 : i64) : i64
%v98 = llvm.alloca %v97 x !llvm.array<3 x i64> : (i64) -> !llvm.ptr
%v99 = arith.constant 24 : i64
func.call @flow_mem_note_stack(%v99) : (i64) -> ()
%v100 = llvm.mlir.zero : !llvm.array<3 x i64>
llvm.store %v100, %v98 : !llvm.array<3 x i64>, !llvm.ptr
%v101 = arith.extsi %v94 : i32 to i64
%v102 = arith.extsi %v95 : i32 to i64
%v103 = arith.extsi %v96 : i32 to i64
%v104 = llvm.mlir.constant(0 : i64) : i64
%v105 = llvm.getelementptr %v98[0, %v104] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
llvm.store %v101, %v105 : i64, !llvm.ptr
%v106 = llvm.mlir.constant(1 : i64) : i64
%v107 = llvm.getelementptr %v98[0, %v106] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
llvm.store %v102, %v107 : i64, !llvm.ptr
%v108 = llvm.mlir.constant(2 : i64) : i64
%v109 = llvm.getelementptr %v98[0, %v108] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
llvm.store %v103, %v109 : i64, !llvm.ptr
%v110 = arith.constant 0 : i32
%v111 = arith.extsi %v110 : i32 to i64
%v112 = llvm.mlir.constant(1 : i64) : i64
%v113 = llvm.alloca %v112 x i64 : (i64) -> !llvm.ptr
llvm.store %v111, %v113 : i64, !llvm.ptr
%v114 = arith.constant 0 : i32
%v115 = arith.constant 3 : i32
%v116 = arith.index_cast %v114 : i32 to index
%v117 = arith.index_cast %v115 : i32 to index
%v118 = arith.constant 1 : index
%v119 = arith.constant -1 : index
%v120 = arith.cmpi sle, %v116, %v117 : index
%v121 = arith.select %v120, %v118, %v119 : index
cf.br ^b7(%v116 : index)
^b7(%v122: index):
%v123 = arith.cmpi slt, %v122, %v117 : index
%v124 = arith.cmpi sgt, %v122, %v117 : index
%v125 = arith.select %v120, %v123, %v124 : i1
cf.cond_br %v125, ^b8(%v122 : index), ^b9(%v122 : index)
^b8(%v126: index):
%v127 = llvm.load %v113 : !llvm.ptr -> i64
%v128 = arith.index_cast %v126 : index to i64
%v129 = llvm.getelementptr %v98[0, %v128] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
%v130 = llvm.load %v129 : !llvm.ptr -> i64
%v131 = arith.constant 1000000 : i32
%v132 = arith.extsi %v131 : i32 to i64
%v133 = arith.muli %v130, %v132 : i64
%v134 = arith.addi %v127, %v133 : i64
llvm.store %v134, %v113 : i64, !llvm.ptr
%v135 = arith.addi %v126, %v121 : index
cf.br ^b7(%v135 : index)
^b9(%v136: index):
%v137 = llvm.load %v113 : !llvm.ptr -> i64
%v138 = llvm.mlir.addressof @str_13 : !llvm.ptr
%v139 = llvm.call @printf(%v138, %v137) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v140 = arith.constant 0 : i32
%v141 = arith.constant 0.5 : f64
%v142 = arith.constant 1.5 : f64
%v143 = arith.constant 2.5 : f64
%v144 = arith.constant 3.5 : f64
%v145 = llvm.mlir.constant(1 : i64) : i64
%v146 = llvm.alloca %v145 x !llvm.array<4 x f64> : (i64) -> !llvm.ptr
%v147 = arith.constant 32 : i64
func.call @flow_mem_note_stack(%v147) : (i64) -> ()
%v148 = llvm.mlir.zero : !llvm.array<4 x f64>
llvm.store %v148, %v146 : !llvm.array<4 x f64>, !llvm.ptr
%v149 = llvm.mlir.constant(0 : i64) : i64
%v150 = llvm.getelementptr %v146[0, %v149] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v141, %v150 : f64, !llvm.ptr
%v151 = llvm.mlir.constant(1 : i64) : i64
%v152 = llvm.getelementptr %v146[0, %v151] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v142, %v152 : f64, !llvm.ptr
%v153 = llvm.mlir.constant(2 : i64) : i64
%v154 = llvm.getelementptr %v146[0, %v153] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v143, %v154 : f64, !llvm.ptr
%v155 = llvm.mlir.constant(3 : i64) : i64
%v156 = llvm.getelementptr %v146[0, %v155] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v144, %v156 : f64, !llvm.ptr
%v157 = arith.constant 4 : i32
%v158 = arith.constant 2.0 : f64
%v159 = func.call @scale(%v146, %v157, %v158) : (!llvm.ptr, i32, f64) -> f64
%v160 = llvm.mlir.addressof @str_14 : !llvm.ptr
%v161 = llvm.call @printf(%v160, %v159) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v162 = arith.constant 0 : i32
%v163 = arith.constant 1 : i1
%v164 = arith.constant 0 : i1
%v165 = llvm.mlir.constant(1 : i64) : i64
%v166 = llvm.alloca %v165 x !llvm.array<2 x i1> : (i64) -> !llvm.ptr
%v167 = arith.constant 2 : i64
func.call @flow_mem_note_stack(%v167) : (i64) -> ()
%v168 = llvm.mlir.zero : !llvm.array<2 x i1>
llvm.store %v168, %v166 : !llvm.array<2 x i1>, !llvm.ptr
%v169 = llvm.mlir.constant(0 : i64) : i64
%v170 = llvm.getelementptr %v166[0, %v169] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x i1>
llvm.store %v163, %v170 : i1, !llvm.ptr
%v171 = llvm.mlir.constant(1 : i64) : i64
%v172 = llvm.getelementptr %v166[0, %v171] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x i1>
llvm.store %v164, %v172 : i1, !llvm.ptr
%v173 = arith.constant 0 : i32
%v174 = arith.extsi %v173 : i32 to i64
%v175 = llvm.getelementptr %v166[0, %v174] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x i1>
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
