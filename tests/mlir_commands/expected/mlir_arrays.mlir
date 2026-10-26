module {
func.func private @strlen(!llvm.ptr) -> i64
func.func private @malloc(i64) -> !llvm.ptr
func.func private @memcpy(!llvm.ptr, !llvm.ptr, i64) -> !llvm.ptr
func.func private @write(i32, !llvm.ptr, i64) -> i64
func.func private @abort() -> ()
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
llvm.mlir.global internal constant @str_2("array index out of bounds\00") {addr_space = 0 : i32} : !llvm.array<26 x i8>
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
llvm.mlir.global internal constant @str_15("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_16("%lld\0A\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
llvm.mlir.global internal constant @str_17("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_18("first\0A\00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
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
%v12 = arith.constant 5 : i32
%v13 = arith.cmpi uge, %v11, %v12 : i32
scf.if %v13 {
%v14 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v14) : (!llvm.ptr) -> ()
}
%v15 = arith.extsi %v11 : i32 to i64
%v16 = llvm.getelementptr %arg0[0, %v15] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
%v17 = llvm.load %v16 : !llvm.ptr -> i32
%v18 = arith.addi %v10, %v17 : i32
llvm.store %v18, %v3 : i32, !llvm.ptr
%v19 = llvm.load %v6 : !llvm.ptr -> i32
%v20 = arith.constant 1 : i32
%v21 = arith.addi %v19, %v20 : i32
llvm.store %v21, %v6 : i32, !llvm.ptr
cf.br ^b1
^b3:
%v22 = llvm.load %v3 : !llvm.ptr -> i32
func.return %v22 : i32
}
func.func @scale(%arg0: !llvm.ptr, %arg1: i32, %arg2: f64) -> f64 {
%v23 = arith.constant 0.0 : f64
%v24 = llvm.mlir.constant(1 : i64) : i64
%v25 = llvm.alloca %v24 x f64 : (i64) -> !llvm.ptr
llvm.store %v23, %v25 : f64, !llvm.ptr
%v26 = arith.constant 0 : i32
%v27 = arith.index_cast %v26 : i32 to index
%v28 = arith.index_cast %arg1 : i32 to index
%v29 = arith.constant 1 : index
%v30 = arith.constant -1 : index
%v31 = arith.cmpi sle, %v27, %v28 : index
%v32 = arith.select %v31, %v29, %v30 : index
cf.br ^b4(%v27 : index)
^b4(%v33: index):
%v34 = arith.cmpi slt, %v33, %v28 : index
%v35 = arith.cmpi sgt, %v33, %v28 : index
%v36 = arith.select %v31, %v34, %v35 : i1
cf.cond_br %v36, ^b5(%v33 : index), ^b6(%v33 : index)
^b5(%v37: index):
%v38 = llvm.load %v25 : !llvm.ptr -> f64
%v39 = arith.index_cast %v37 : index to i64
%v40 = llvm.getelementptr %arg0[%v39] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v41 = llvm.load %v40 : !llvm.ptr -> f64
%v42 = llvm.intr.fmuladd(%v41, %arg2, %v38) : (f64, f64, f64) -> f64
llvm.store %v42, %v25 : f64, !llvm.ptr
%v43 = arith.addi %v37, %v32 : index
cf.br ^b4(%v43 : index)
^b6(%v44: index):
%v45 = llvm.load %v25 : !llvm.ptr -> f64
func.return %v45 : f64
}
func.func @main() -> i32 {
%v46 = arith.constant 3 : i32
%v47 = arith.constant 1 : i32
%v48 = arith.constant 4 : i32
%v49 = arith.constant 1 : i32
%v50 = arith.constant 5 : i32
%v51 = llvm.mlir.constant(1 : i64) : i64
%v52 = llvm.alloca %v51 x !llvm.array<5 x i32> : (i64) -> !llvm.ptr
%v53 = arith.constant 20 : i64
func.call @flow_mem_note_stack(%v53) : (i64) -> ()
%v54 = llvm.mlir.zero : !llvm.array<5 x i32>
llvm.store %v54, %v52 : !llvm.array<5 x i32>, !llvm.ptr
%v55 = llvm.mlir.constant(0 : i64) : i64
%v56 = llvm.getelementptr %v52[0, %v55] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v46, %v56 : i32, !llvm.ptr
%v57 = llvm.mlir.constant(1 : i64) : i64
%v58 = llvm.getelementptr %v52[0, %v57] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v47, %v58 : i32, !llvm.ptr
%v59 = llvm.mlir.constant(2 : i64) : i64
%v60 = llvm.getelementptr %v52[0, %v59] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v48, %v60 : i32, !llvm.ptr
%v61 = llvm.mlir.constant(3 : i64) : i64
%v62 = llvm.getelementptr %v52[0, %v61] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v49, %v62 : i32, !llvm.ptr
%v63 = llvm.mlir.constant(4 : i64) : i64
%v64 = llvm.getelementptr %v52[0, %v63] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v50, %v64 : i32, !llvm.ptr
%v65 = func.call @total(%v52) : (!llvm.ptr) -> i32
%v66 = llvm.mlir.addressof @str_15 : !llvm.ptr
%v67 = llvm.call @printf(%v66, %v65) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v68 = arith.constant 0 : i32
%v69 = arith.constant 40 : i32
%v70 = arith.constant 2 : i32
%v71 = arith.extsi %v70 : i32 to i64
%v72 = llvm.getelementptr %v52[0, %v71] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v69, %v72 : i32, !llvm.ptr
%v73 = arith.constant 4 : i32
%v74 = arith.constant 5 : i32
%v75 = arith.cmpi uge, %v73, %v74 : i32
scf.if %v75 {
%v76 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v76) : (!llvm.ptr) -> ()
}
%v77 = arith.extsi %v73 : i32 to i64
%v78 = llvm.getelementptr %v52[0, %v77] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
%v79 = llvm.load %v78 : !llvm.ptr -> i32
%v80 = arith.constant 100 : i32
%v81 = arith.addi %v79, %v80 : i32
%v82 = arith.extsi %v73 : i32 to i64
%v83 = llvm.getelementptr %v52[0, %v82] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v81, %v83 : i32, !llvm.ptr
%v84 = func.call @total(%v52) : (!llvm.ptr) -> i32
%v85 = llvm.mlir.addressof @str_15 : !llvm.ptr
%v86 = llvm.call @printf(%v85, %v84) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v87 = arith.constant 0 : i32
%v88 = arith.constant 2 : i32
%v89 = arith.constant 5 : i32
%v90 = arith.cmpi uge, %v88, %v89 : i32
scf.if %v90 {
%v91 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v91) : (!llvm.ptr) -> ()
}
%v92 = arith.extsi %v88 : i32 to i64
%v93 = llvm.getelementptr %v52[0, %v92] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
%v94 = llvm.load %v93 : !llvm.ptr -> i32
%v95 = arith.constant 4 : i32
%v96 = arith.constant 5 : i32
%v97 = arith.cmpi uge, %v95, %v96 : i32
scf.if %v97 {
%v98 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v98) : (!llvm.ptr) -> ()
}
%v99 = arith.extsi %v95 : i32 to i64
%v100 = llvm.getelementptr %v52[0, %v99] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
%v101 = llvm.load %v100 : !llvm.ptr -> i32
%v102 = arith.addi %v94, %v101 : i32
%v103 = llvm.mlir.addressof @str_15 : !llvm.ptr
%v104 = llvm.call @printf(%v103, %v102) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v105 = arith.constant 0 : i32
%v106 = arith.constant 1 : i32
%v107 = arith.constant 2 : i32
%v108 = arith.constant 3 : i32
%v109 = llvm.mlir.constant(1 : i64) : i64
%v110 = llvm.alloca %v109 x !llvm.array<3 x i64> : (i64) -> !llvm.ptr
%v111 = arith.constant 24 : i64
func.call @flow_mem_note_stack(%v111) : (i64) -> ()
%v112 = llvm.mlir.zero : !llvm.array<3 x i64>
llvm.store %v112, %v110 : !llvm.array<3 x i64>, !llvm.ptr
%v113 = arith.extsi %v106 : i32 to i64
%v114 = arith.extsi %v107 : i32 to i64
%v115 = arith.extsi %v108 : i32 to i64
%v116 = llvm.mlir.constant(0 : i64) : i64
%v117 = llvm.getelementptr %v110[0, %v116] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
llvm.store %v113, %v117 : i64, !llvm.ptr
%v118 = llvm.mlir.constant(1 : i64) : i64
%v119 = llvm.getelementptr %v110[0, %v118] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
llvm.store %v114, %v119 : i64, !llvm.ptr
%v120 = llvm.mlir.constant(2 : i64) : i64
%v121 = llvm.getelementptr %v110[0, %v120] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
llvm.store %v115, %v121 : i64, !llvm.ptr
%v122 = arith.constant 0 : i32
%v123 = arith.extsi %v122 : i32 to i64
%v124 = llvm.mlir.constant(1 : i64) : i64
%v125 = llvm.alloca %v124 x i64 : (i64) -> !llvm.ptr
llvm.store %v123, %v125 : i64, !llvm.ptr
%v126 = arith.constant 0 : i32
%v127 = arith.constant 3 : i32
%v128 = arith.index_cast %v126 : i32 to index
%v129 = arith.index_cast %v127 : i32 to index
%v130 = arith.constant 1 : index
%v131 = arith.constant -1 : index
%v132 = arith.cmpi sle, %v128, %v129 : index
%v133 = arith.select %v132, %v130, %v131 : index
cf.br ^b7(%v128 : index)
^b7(%v134: index):
%v135 = arith.cmpi slt, %v134, %v129 : index
%v136 = arith.cmpi sgt, %v134, %v129 : index
%v137 = arith.select %v132, %v135, %v136 : i1
cf.cond_br %v137, ^b8(%v134 : index), ^b9(%v134 : index)
^b8(%v138: index):
%v139 = llvm.load %v125 : !llvm.ptr -> i64
%v140 = arith.index_cast %v138 : index to i32
%v141 = arith.constant 3 : i32
%v142 = arith.cmpi uge, %v140, %v141 : i32
scf.if %v142 {
%v143 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v143) : (!llvm.ptr) -> ()
}
%v144 = arith.index_cast %v138 : index to i64
%v145 = llvm.getelementptr %v110[0, %v144] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
%v146 = llvm.load %v145 : !llvm.ptr -> i64
%v147 = arith.constant 1000000 : i32
%v148 = arith.extsi %v147 : i32 to i64
%v149 = arith.muli %v146, %v148 : i64
%v150 = arith.addi %v139, %v149 : i64
llvm.store %v150, %v125 : i64, !llvm.ptr
%v151 = arith.addi %v138, %v133 : index
cf.br ^b7(%v151 : index)
^b9(%v152: index):
%v153 = llvm.load %v125 : !llvm.ptr -> i64
%v154 = llvm.mlir.addressof @str_16 : !llvm.ptr
%v155 = llvm.call @printf(%v154, %v153) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v156 = arith.constant 0 : i32
%v157 = arith.constant 0.5 : f64
%v158 = arith.constant 1.5 : f64
%v159 = arith.constant 2.5 : f64
%v160 = arith.constant 3.5 : f64
%v161 = llvm.mlir.constant(1 : i64) : i64
%v162 = llvm.alloca %v161 x !llvm.array<4 x f64> : (i64) -> !llvm.ptr
%v163 = arith.constant 32 : i64
func.call @flow_mem_note_stack(%v163) : (i64) -> ()
%v164 = llvm.mlir.zero : !llvm.array<4 x f64>
llvm.store %v164, %v162 : !llvm.array<4 x f64>, !llvm.ptr
%v165 = llvm.mlir.constant(0 : i64) : i64
%v166 = llvm.getelementptr %v162[0, %v165] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v157, %v166 : f64, !llvm.ptr
%v167 = llvm.mlir.constant(1 : i64) : i64
%v168 = llvm.getelementptr %v162[0, %v167] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v158, %v168 : f64, !llvm.ptr
%v169 = llvm.mlir.constant(2 : i64) : i64
%v170 = llvm.getelementptr %v162[0, %v169] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v159, %v170 : f64, !llvm.ptr
%v171 = llvm.mlir.constant(3 : i64) : i64
%v172 = llvm.getelementptr %v162[0, %v171] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v160, %v172 : f64, !llvm.ptr
%v173 = arith.constant 4 : i32
%v174 = arith.constant 2.0 : f64
%v175 = func.call @scale(%v162, %v173, %v174) : (!llvm.ptr, i32, f64) -> f64
%v176 = llvm.mlir.addressof @str_17 : !llvm.ptr
%v177 = llvm.call @printf(%v176, %v175) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v178 = arith.constant 0 : i32
%v179 = arith.constant 1 : i1
%v180 = arith.constant 0 : i1
%v181 = llvm.mlir.constant(1 : i64) : i64
%v182 = llvm.alloca %v181 x !llvm.array<2 x i1> : (i64) -> !llvm.ptr
%v183 = arith.constant 2 : i64
func.call @flow_mem_note_stack(%v183) : (i64) -> ()
%v184 = llvm.mlir.zero : !llvm.array<2 x i1>
llvm.store %v184, %v182 : !llvm.array<2 x i1>, !llvm.ptr
%v185 = llvm.mlir.constant(0 : i64) : i64
%v186 = llvm.getelementptr %v182[0, %v185] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x i1>
llvm.store %v179, %v186 : i1, !llvm.ptr
%v187 = llvm.mlir.constant(1 : i64) : i64
%v188 = llvm.getelementptr %v182[0, %v187] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x i1>
llvm.store %v180, %v188 : i1, !llvm.ptr
%v189 = arith.constant 0 : i32
%v190 = arith.constant 2 : i32
%v191 = arith.cmpi uge, %v189, %v190 : i32
scf.if %v191 {
%v192 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v192) : (!llvm.ptr) -> ()
}
%v193 = arith.extsi %v189 : i32 to i64
%v194 = llvm.getelementptr %v182[0, %v193] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x i1>
%v195 = llvm.load %v194 : !llvm.ptr -> i1
cf.cond_br %v195, ^b10, ^b11
^b10:
%v196 = llvm.mlir.addressof @str_18 : !llvm.ptr
%v197 = llvm.call @printf(%v196) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v198 = arith.constant 0 : i32
cf.br ^b12
^b11:
cf.br ^b12
^b12:
%v199 = arith.constant 0 : i32
func.return %v199 : i32
}
}
