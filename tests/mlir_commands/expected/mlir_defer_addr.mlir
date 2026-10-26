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
%name = llvm.mlir.addressof @str_2 : !llvm.ptr
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
%hdr = llvm.mlir.addressof @str_3 : !llvm.ptr
%h = llvm.call @printf(%hdr) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%g_flow_mem_alloc_count = llvm.mlir.addressof @flow_mem_alloc_count : !llvm.ptr
%v_flow_mem_alloc_count = llvm.load %g_flow_mem_alloc_count : !llvm.ptr -> i64
%f_flow_mem_alloc_count = llvm.mlir.addressof @str_4 : !llvm.ptr
%w_flow_mem_alloc_count = llvm.call @printf(%f_flow_mem_alloc_count, %v_flow_mem_alloc_count) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_alloc_bytes = llvm.mlir.addressof @flow_mem_alloc_bytes : !llvm.ptr
%v_flow_mem_alloc_bytes = llvm.load %g_flow_mem_alloc_bytes : !llvm.ptr -> i64
%f_flow_mem_alloc_bytes = llvm.mlir.addressof @str_5 : !llvm.ptr
%w_flow_mem_alloc_bytes = llvm.call @printf(%f_flow_mem_alloc_bytes, %v_flow_mem_alloc_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_peak_live = llvm.mlir.addressof @flow_mem_peak_live : !llvm.ptr
%v_flow_mem_peak_live = llvm.load %g_flow_mem_peak_live : !llvm.ptr -> i64
%f_flow_mem_peak_live = llvm.mlir.addressof @str_6 : !llvm.ptr
%w_flow_mem_peak_live = llvm.call @printf(%f_flow_mem_peak_live, %v_flow_mem_peak_live) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_temp_bytes = llvm.mlir.addressof @flow_mem_temp_bytes : !llvm.ptr
%v_flow_mem_temp_bytes = llvm.load %g_flow_mem_temp_bytes : !llvm.ptr -> i64
%f_flow_mem_temp_bytes = llvm.mlir.addressof @str_7 : !llvm.ptr
%w_flow_mem_temp_bytes = llvm.call @printf(%f_flow_mem_temp_bytes, %v_flow_mem_temp_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_copy_bytes = llvm.mlir.addressof @flow_mem_copy_bytes : !llvm.ptr
%v_flow_mem_copy_bytes = llvm.load %g_flow_mem_copy_bytes : !llvm.ptr -> i64
%f_flow_mem_copy_bytes = llvm.mlir.addressof @str_8 : !llvm.ptr
%w_flow_mem_copy_bytes = llvm.call @printf(%f_flow_mem_copy_bytes, %v_flow_mem_copy_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_stack_bytes = llvm.mlir.addressof @flow_mem_stack_bytes : !llvm.ptr
%v_flow_mem_stack_bytes = llvm.load %g_flow_mem_stack_bytes : !llvm.ptr -> i64
%f_flow_mem_stack_bytes = llvm.mlir.addressof @str_9 : !llvm.ptr
%w_flow_mem_stack_bytes = llvm.call @printf(%f_flow_mem_stack_bytes, %v_flow_mem_stack_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_arena_bytes = llvm.mlir.addressof @flow_mem_arena_bytes : !llvm.ptr
%v_flow_mem_arena_bytes = llvm.load %g_flow_mem_arena_bytes : !llvm.ptr -> i64
%f_flow_mem_arena_bytes = llvm.mlir.addressof @str_10 : !llvm.ptr
%w_flow_mem_arena_bytes = llvm.call @printf(%f_flow_mem_arena_bytes, %v_flow_mem_arena_bytes) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%sp = llvm.mlir.addressof @flow_mem_stack_bytes : !llvm.ptr
%sv = llvm.load %sp : !llvm.ptr -> i64
%ap = llvm.mlir.addressof @flow_mem_arena_bytes : !llvm.ptr
%av = llvm.load %ap : !llvm.ptr -> i64
%promo = arith.addi %sv, %av : i64
%pf = llvm.mlir.addressof @str_11 : !llvm.ptr
%ph = llvm.call @printf(%pf, %promo) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_map_overflow = llvm.mlir.addressof @flow_mem_map_overflow : !llvm.ptr
%v_flow_mem_map_overflow = llvm.load %g_flow_mem_map_overflow : !llvm.ptr -> i64
%f_flow_mem_map_overflow = llvm.mlir.addressof @str_12 : !llvm.ptr
%w_flow_mem_map_overflow = llvm.call @printf(%f_flow_mem_map_overflow, %v_flow_mem_map_overflow) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%g_flow_mem_site_concat = llvm.mlir.addressof @flow_mem_site_concat : !llvm.ptr
%v_flow_mem_site_concat = llvm.load %g_flow_mem_site_concat : !llvm.ptr -> i64
%f_flow_mem_site_concat = llvm.mlir.addressof @str_13 : !llvm.ptr
%w_flow_mem_site_concat = llvm.call @printf(%f_flow_mem_site_concat, %v_flow_mem_site_concat) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
scf.yield
}
func.return
}
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("defer %d\0A\00") {addr_space = 0 : i32} : !llvm.array<10 x i8>
llvm.mlir.global internal constant @str_1("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_2("FLOW_MEM_PROFILE\00") {addr_space = 0 : i32} : !llvm.array<17 x i8>
llvm.mlir.global internal constant @str_3("\0A=== Flow memory profile (#740) ===\0A\00") {addr_space = 0 : i32} : !llvm.array<37 x i8>
llvm.mlir.global internal constant @str_4("allocations: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<19 x i8>
llvm.mlir.global internal constant @str_5("heap_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<18 x i8>
llvm.mlir.global internal constant @str_6("peak_live_heap: %lld\0A\00") {addr_space = 0 : i32} : !llvm.array<22 x i8>
llvm.mlir.global internal constant @str_7("temp_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<18 x i8>
llvm.mlir.global internal constant @str_8("copies: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<14 x i8>
llvm.mlir.global internal constant @str_9("stack_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<19 x i8>
llvm.mlir.global internal constant @str_10("arena_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<19 x i8>
llvm.mlir.global internal constant @str_11("promotion_bytes: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<23 x i8>
llvm.mlir.global internal constant @str_12("live_map_overflow: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<25 x i8>
llvm.mlir.global internal constant @str_13("site_concat: %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<19 x i8>
llvm.mlir.global internal constant @str_14("flow: \00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
llvm.mlir.global internal constant @str_15("\0A\00") {addr_space = 0 : i32} : !llvm.array<2 x i8>
llvm.mlir.global internal constant @str_16("array index out of bounds\00") {addr_space = 0 : i32} : !llvm.array<26 x i8>
func.func private @__flow_fault(%arg0: !llvm.ptr) {
%fd = arith.constant 2 : i32
%pre = llvm.mlir.addressof @str_14 : !llvm.ptr
%n6 = arith.constant 6 : i64
%w0 = func.call @write(%fd, %pre, %n6) : (i32, !llvm.ptr, i64) -> i64
%n = func.call @strlen(%arg0) : (!llvm.ptr) -> i64
%w1 = func.call @write(%fd, %arg0, %n) : (i32, !llvm.ptr, i64) -> i64
%nl = llvm.mlir.addressof @str_15 : !llvm.ptr
%n1 = arith.constant 1 : i64
%w2 = func.call @write(%fd, %nl, %n1) : (i32, !llvm.ptr, i64) -> i64
func.call @abort() : () -> ()
func.return
}
// Struct: Counter
// Fields:
//   hits: i32
//   last: i32
func.func @note(%arg0: i32) -> () {
%v1 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v2 = llvm.call @printf(%v1, %arg0) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
func.return
}
func.func @bump(%arg0: !llvm.ptr) -> () {
%v3 = arith.constant 0 : i32
%v4 = arith.extsi %v3 : i32 to i64
%v5 = llvm.getelementptr %arg0[%v4] : (!llvm.ptr, i64) -> !llvm.ptr, i32
%v6 = llvm.load %v5 : !llvm.ptr -> i32
%v7 = arith.constant 1 : i32
%v8 = arith.addi %v6, %v7 : i32
%v9 = arith.constant 0 : i32
%v10 = arith.extsi %v9 : i32 to i64
%v11 = llvm.getelementptr %arg0[%v10] : (!llvm.ptr, i64) -> !llvm.ptr, i32
llvm.store %v8, %v11 : i32, !llvm.ptr
func.return
}
func.func @deferred(%arg0: i32) -> i32 {
%v12 = arith.constant 0 : i32
%v13 = llvm.mlir.constant(1 : i64) : i64
%v14 = llvm.alloca %v13 x i32 : (i64) -> !llvm.ptr
llvm.store %v12, %v14 : i32, !llvm.ptr
cf.br ^b1
^b1:
%v15 = llvm.load %v14 : !llvm.ptr -> i32
%v16 = arith.cmpi slt, %v15, %arg0 : i32
cf.cond_br %v16, ^b2, ^b3
^b2:
%v17 = llvm.load %v14 : !llvm.ptr -> i32
%v18 = arith.constant 2 : i32
%v19 = arith.cmpi eq, %v17, %v18 : i32
cf.cond_br %v19, ^b4, ^b5
^b4:
%v20 = arith.constant 2 : i32
func.call @note(%v20) : (i32) -> ()
cf.br ^b3
^b5:
cf.br ^b6
^b6:
%v21 = llvm.load %v14 : !llvm.ptr -> i32
%v22 = arith.constant 1 : i32
%v23 = arith.addi %v21, %v22 : i32
llvm.store %v23, %v14 : i32, !llvm.ptr
%v24 = arith.constant 2 : i32
func.call @note(%v24) : (i32) -> ()
cf.br ^b1
^b3:
%v25 = llvm.load %v14 : !llvm.ptr -> i32
%v26 = arith.constant 10 : i32
%v27 = arith.muli %v25, %v26 : i32
%v28 = arith.constant 3 : i32
func.call @note(%v28) : (i32) -> ()
%v29 = arith.constant 1 : i32
func.call @note(%v29) : (i32) -> ()
func.return %v27 : i32
}
func.func @main() -> i32 {
%v30 = arith.constant 5 : i32
%v31 = func.call @deferred(%v30) : (i32) -> i32
%v32 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v33 = llvm.call @printf(%v32, %v31) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v34 = arith.constant 0 : i32
%v35 = arith.constant 41 : i32
%v36 = llvm.mlir.constant(1 : i64) : i64
%v37 = llvm.alloca %v36 x i32 : (i64) -> !llvm.ptr
llvm.store %v35, %v37 : i32, !llvm.ptr
func.call @bump(%v37) : (!llvm.ptr) -> ()
%v38 = llvm.load %v37 : !llvm.ptr -> i32
%v39 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v40 = llvm.call @printf(%v39, %v38) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v41 = arith.constant 0 : i32
%v42 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v43 = arith.constant 0 : i32
%v44 = llvm.insertvalue %v43, %v42[0] : !llvm.struct<(i32, i32)>
%v45 = arith.constant 0 : i32
%v46 = llvm.insertvalue %v45, %v44[1] : !llvm.struct<(i32, i32)>
%v47 = llvm.mlir.constant(1 : i64) : i64
%v48 = llvm.alloca %v47 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v46, %v48 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v49 = llvm.getelementptr %v48[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
func.call @bump(%v49) : (!llvm.ptr) -> ()
%v50 = llvm.getelementptr %v48[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
func.call @bump(%v50) : (!llvm.ptr) -> ()
%v51 = llvm.load %v48 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v52 = llvm.getelementptr %v48[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v53 = llvm.load %v52 : !llvm.ptr -> i32
%v54 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v55 = llvm.call @printf(%v54, %v53) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v56 = arith.constant 0 : i32
%v57 = arith.constant 1 : i32
%v58 = arith.constant 2 : i32
%v59 = arith.constant 3 : i32
%v60 = llvm.mlir.constant(1 : i64) : i64
%v61 = llvm.alloca %v60 x !llvm.array<3 x i32> : (i64) -> !llvm.ptr
%v62 = arith.constant 12 : i64
func.call @flow_mem_note_stack(%v62) : (i64) -> ()
%v63 = llvm.mlir.zero : !llvm.array<3 x i32>
llvm.store %v63, %v61 : !llvm.array<3 x i32>, !llvm.ptr
%v64 = llvm.mlir.constant(0 : i64) : i64
%v65 = llvm.getelementptr %v61[0, %v64] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v57, %v65 : i32, !llvm.ptr
%v66 = llvm.mlir.constant(1 : i64) : i64
%v67 = llvm.getelementptr %v61[0, %v66] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v58, %v67 : i32, !llvm.ptr
%v68 = llvm.mlir.constant(2 : i64) : i64
%v69 = llvm.getelementptr %v61[0, %v68] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v59, %v69 : i32, !llvm.ptr
%v70 = arith.constant 1 : i32
%v71 = arith.extsi %v70 : i32 to i64
%v72 = llvm.getelementptr %v61[0, %v71] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
func.call @bump(%v72) : (!llvm.ptr) -> ()
%v73 = arith.constant 1 : i32
%v74 = arith.constant 3 : i32
%v75 = arith.cmpi uge, %v73, %v74 : i32
scf.if %v75 {
%v76 = llvm.mlir.addressof @str_16 : !llvm.ptr
func.call @__flow_fault(%v76) : (!llvm.ptr) -> ()
}
%v77 = arith.extsi %v73 : i32 to i64
%v78 = llvm.getelementptr %v61[0, %v77] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
%v79 = llvm.load %v78 : !llvm.ptr -> i32
%v80 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v81 = llvm.call @printf(%v80, %v79) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v82 = arith.constant 0 : i32
%v83 = arith.constant 5 : i32
%v84 = llvm.mlir.constant(1 : i64) : i64
%v85 = llvm.alloca %v84 x i32 : (i64) -> !llvm.ptr
llvm.store %v83, %v85 : i32, !llvm.ptr
// flowc.noalias py
%v86 = arith.constant 0 : i32
%v87 = arith.extsi %v86 : i32 to i64
%v88 = llvm.getelementptr %v85[%v87] : (!llvm.ptr, i64) -> !llvm.ptr, i32
%v89 = llvm.load %v88 : !llvm.ptr -> i32
%v90 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v91 = llvm.call @printf(%v90, %v89) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v92 = arith.constant 0 : i32
%v93 = arith.constant 0 : i32
func.return %v93 : i32
}
}
