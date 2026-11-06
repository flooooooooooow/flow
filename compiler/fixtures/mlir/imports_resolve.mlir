module {
func.func private @memcpy(!llvm.ptr, !llvm.ptr, i64) -> !llvm.ptr
func.func private @malloc(i64) -> !llvm.ptr
func.func private @free(!llvm.ptr) -> ()
func.func private @realloc(!llvm.ptr, i64) -> !llvm.ptr
func.func private @strlen(!llvm.ptr) -> i64
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
llvm.mlir.global internal constant @str_13("resolved\00") {addr_space = 0 : i32} : !llvm.array<9 x i8>
// Module static: dep_calls
llvm.mlir.global internal @dep_calls(0 : i32) : i32
func.func @dep_scale(%arg0: i32) -> i32 {
%v1 = llvm.mlir.addressof @dep_calls : !llvm.ptr
%v2 = llvm.load %v1 : !llvm.ptr -> i32
%v3 = arith.constant 1 : i32
%v4 = arith.addi %v2, %v3 : i32
%v5 = llvm.mlir.addressof @dep_calls : !llvm.ptr
llvm.store %v4, %v5 : i32, !llvm.ptr
%v6 = arith.constant 3 : i32
%v7 = arith.muli %arg0, %v6 : i32
func.return %v7 : i32
}
func.func @dep_total() -> i32 {
%v8 = llvm.mlir.addressof @dep_calls : !llvm.ptr
%v9 = llvm.load %v8 : !llvm.ptr -> i32
func.return %v9 : i32
}
// Struct: ByteBuf
// Fields:
//   p: !llvm.ptr
//   len: i32
//   cap: i32
//   err: i32
func.func @bb_new(%arg0: i32) -> !llvm.ptr {
%v10 = arith.constant 24 : i32
%v11 = arith.extsi %v10 : i32 to i64
%v12 = func.call @flow_mem_malloc(%v11) : (i64) -> !llvm.ptr
%v13 = llvm.mlir.constant(1 : i64) : i64
%v14 = llvm.alloca %v13 x i32 : (i64) -> !llvm.ptr
llvm.store %arg0, %v14 : i32, !llvm.ptr
%v15 = llvm.load %v14 : !llvm.ptr -> i32
%v16 = arith.constant 16 : i32
%v17 = arith.cmpi slt, %v15, %v16 : i32
cf.cond_br %v17, ^b1, ^b2
^b1:
%v18 = arith.constant 16 : i32
llvm.store %v18, %v14 : i32, !llvm.ptr
cf.br ^b3
^b2:
cf.br ^b3
^b3:
%v19 = llvm.load %v14 : !llvm.ptr -> i32
%v20 = arith.constant 1 : i32
%v21 = arith.addi %v19, %v20 : i32
%v22 = arith.extsi %v21 : i32 to i64
%v23 = func.call @flow_mem_malloc(%v22) : (i64) -> !llvm.ptr
%v24 = arith.constant 0 : i32
%v25 = arith.extsi %v24 : i32 to i64
%v26 = llvm.getelementptr %v12[%v25] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v27 = llvm.getelementptr %v26[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
llvm.store %v23, %v27 : !llvm.ptr, !llvm.ptr
%v28 = arith.constant 0 : i32
%v29 = arith.constant 0 : i32
%v30 = arith.extsi %v29 : i32 to i64
%v31 = llvm.getelementptr %v12[%v30] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v32 = llvm.getelementptr %v31[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
llvm.store %v28, %v32 : i32, !llvm.ptr
%v33 = llvm.load %v14 : !llvm.ptr -> i32
%v34 = arith.constant 0 : i32
%v35 = arith.extsi %v34 : i32 to i64
%v36 = llvm.getelementptr %v12[%v35] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v37 = llvm.getelementptr %v36[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
llvm.store %v33, %v37 : i32, !llvm.ptr
%v38 = arith.constant 0 : i32
%v39 = arith.constant 0 : i32
%v40 = arith.extsi %v39 : i32 to i64
%v41 = llvm.getelementptr %v12[%v40] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v42 = llvm.getelementptr %v41[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
llvm.store %v38, %v42 : i32, !llvm.ptr
%v43 = arith.constant 0 : i32
%v44 = arith.extsi %v43 : i32 to i64
%v45 = llvm.getelementptr %v12[%v44] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v46 = llvm.load %v45 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v47 = arith.constant 0 : i32
%v48 = arith.extsi %v47 : i32 to i64
%v49 = llvm.getelementptr %v12[%v48] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v50 = llvm.getelementptr %v49[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v51 = llvm.load %v50 : !llvm.ptr -> !llvm.ptr
%v52 = llvm.mlir.zero : !llvm.ptr
%v53 = llvm.icmp "eq" %v51, %v52 : !llvm.ptr
cf.cond_br %v53, ^b4, ^b5
^b4:
%v54 = arith.constant 0 : i32
%v55 = arith.constant 0 : i32
%v56 = arith.extsi %v55 : i32 to i64
%v57 = llvm.getelementptr %v12[%v56] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v58 = llvm.getelementptr %v57[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
llvm.store %v54, %v58 : i32, !llvm.ptr
%v59 = arith.constant 1 : i32
%v60 = arith.constant 0 : i32
%v61 = arith.extsi %v60 : i32 to i64
%v62 = llvm.getelementptr %v12[%v61] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v63 = llvm.getelementptr %v62[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
llvm.store %v59, %v63 : i32, !llvm.ptr
func.return %v12 : !llvm.ptr
^b5:
cf.br ^b6
^b6:
%v64 = arith.constant 0 : i32
%v65 = arith.constant 0 : i32
%v66 = arith.extsi %v65 : i32 to i64
%v67 = llvm.getelementptr %v12[%v66] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v68 = llvm.load %v67 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v69 = arith.constant 0 : i32
%v70 = arith.extsi %v69 : i32 to i64
%v71 = llvm.getelementptr %v12[%v70] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v72 = llvm.getelementptr %v71[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v73 = llvm.load %v72 : !llvm.ptr -> !llvm.ptr
%v74 = arith.constant 0 : i32
%v75 = arith.trunci %v64 : i32 to i8
%v76 = arith.extsi %v74 : i32 to i64
%v77 = llvm.getelementptr %v73[%v76] : (!llvm.ptr, i64) -> !llvm.ptr, i8
llvm.store %v75, %v77 : i8, !llvm.ptr
func.return %v12 : !llvm.ptr
}
func.func @bb_free(%arg0: !llvm.ptr) -> () {
%v78 = llvm.mlir.zero : !llvm.ptr
%v79 = llvm.icmp "eq" %arg0, %v78 : !llvm.ptr
cf.cond_br %v79, ^b7, ^b8
^b7:
func.return
^b8:
cf.br ^b9
^b9:
%v80 = arith.constant 0 : i32
%v81 = arith.extsi %v80 : i32 to i64
%v82 = llvm.getelementptr %arg0[%v81] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v83 = llvm.load %v82 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v84 = arith.constant 0 : i32
%v85 = arith.extsi %v84 : i32 to i64
%v86 = llvm.getelementptr %arg0[%v85] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v87 = llvm.getelementptr %v86[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v88 = llvm.load %v87 : !llvm.ptr -> !llvm.ptr
%v89 = llvm.mlir.zero : !llvm.ptr
%v90 = llvm.icmp "ne" %v88, %v89 : !llvm.ptr
cf.cond_br %v90, ^b10, ^b11
^b10:
%v91 = arith.constant 0 : i32
%v92 = arith.extsi %v91 : i32 to i64
%v93 = llvm.getelementptr %arg0[%v92] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v94 = llvm.load %v93 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v95 = arith.constant 0 : i32
%v96 = arith.extsi %v95 : i32 to i64
%v97 = llvm.getelementptr %arg0[%v96] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v98 = llvm.getelementptr %v97[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v99 = llvm.load %v98 : !llvm.ptr -> !llvm.ptr
func.call @flow_mem_free(%v99) : (!llvm.ptr) -> ()
cf.br ^b12
^b11:
cf.br ^b12
^b12:
func.call @flow_mem_free(%arg0) : (!llvm.ptr) -> ()
func.return
}
func.func @bb_reserve(%arg0: !llvm.ptr, %arg1: i32) -> i1 {
%v100 = arith.constant 0 : i32
%v101 = arith.extsi %v100 : i32 to i64
%v102 = llvm.getelementptr %arg0[%v101] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v103 = llvm.load %v102 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v104 = arith.constant 0 : i32
%v105 = arith.extsi %v104 : i32 to i64
%v106 = llvm.getelementptr %arg0[%v105] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v107 = llvm.getelementptr %v106[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v108 = llvm.load %v107 : !llvm.ptr -> i32
%v109 = arith.addi %v108, %arg1 : i32
%v110 = arith.constant 0 : i32
%v111 = arith.extsi %v110 : i32 to i64
%v112 = llvm.getelementptr %arg0[%v111] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v113 = llvm.load %v112 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v114 = arith.constant 0 : i32
%v115 = arith.extsi %v114 : i32 to i64
%v116 = llvm.getelementptr %arg0[%v115] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v117 = llvm.getelementptr %v116[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v118 = llvm.load %v117 : !llvm.ptr -> i32
%v119 = arith.cmpi sle, %v109, %v118 : i32
cf.cond_br %v119, ^b13, ^b14
^b13:
%v120 = arith.constant 1 : i1
func.return %v120 : i1
^b14:
cf.br ^b15
^b15:
%v121 = arith.constant 0 : i32
%v122 = arith.extsi %v121 : i32 to i64
%v123 = llvm.getelementptr %arg0[%v122] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v124 = llvm.load %v123 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v125 = arith.constant 0 : i32
%v126 = arith.extsi %v125 : i32 to i64
%v127 = llvm.getelementptr %arg0[%v126] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v128 = llvm.getelementptr %v127[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v129 = llvm.load %v128 : !llvm.ptr -> i32
%v130 = arith.constant 2 : i32
%v131 = arith.muli %v129, %v130 : i32
%v132 = arith.constant 64 : i32
%v133 = arith.addi %v131, %v132 : i32
%v134 = llvm.mlir.constant(1 : i64) : i64
%v135 = llvm.alloca %v134 x i32 : (i64) -> !llvm.ptr
llvm.store %v133, %v135 : i32, !llvm.ptr
%v136 = llvm.load %v135 : !llvm.ptr -> i32
%v137 = arith.cmpi slt, %v136, %v109 : i32
cf.cond_br %v137, ^b16, ^b17
^b16:
llvm.store %v109, %v135 : i32, !llvm.ptr
cf.br ^b18
^b17:
cf.br ^b18
^b18:
%v138 = arith.constant 0 : i32
%v139 = arith.extsi %v138 : i32 to i64
%v140 = llvm.getelementptr %arg0[%v139] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v141 = llvm.load %v140 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v142 = arith.constant 0 : i32
%v143 = arith.extsi %v142 : i32 to i64
%v144 = llvm.getelementptr %arg0[%v143] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v145 = llvm.getelementptr %v144[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v146 = llvm.load %v145 : !llvm.ptr -> !llvm.ptr
%v147 = llvm.load %v135 : !llvm.ptr -> i32
%v148 = arith.constant 1 : i32
%v149 = arith.addi %v147, %v148 : i32
%v150 = arith.extsi %v149 : i32 to i64
%v151 = func.call @flow_mem_realloc(%v146, %v150) : (!llvm.ptr, i64) -> !llvm.ptr
%v152 = llvm.mlir.zero : !llvm.ptr
%v153 = llvm.icmp "eq" %v151, %v152 : !llvm.ptr
cf.cond_br %v153, ^b19, ^b20
^b19:
%v154 = arith.constant 1 : i32
%v155 = arith.constant 0 : i32
%v156 = arith.extsi %v155 : i32 to i64
%v157 = llvm.getelementptr %arg0[%v156] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v158 = llvm.getelementptr %v157[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
llvm.store %v154, %v158 : i32, !llvm.ptr
%v159 = arith.constant 0 : i1
func.return %v159 : i1
^b20:
cf.br ^b21
^b21:
%v160 = arith.constant 0 : i32
%v161 = arith.extsi %v160 : i32 to i64
%v162 = llvm.getelementptr %arg0[%v161] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v163 = llvm.getelementptr %v162[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
llvm.store %v151, %v163 : !llvm.ptr, !llvm.ptr
%v164 = llvm.load %v135 : !llvm.ptr -> i32
%v165 = arith.constant 0 : i32
%v166 = arith.extsi %v165 : i32 to i64
%v167 = llvm.getelementptr %arg0[%v166] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v168 = llvm.getelementptr %v167[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
llvm.store %v164, %v168 : i32, !llvm.ptr
%v169 = arith.constant 1 : i1
func.return %v169 : i1
}
func.func @bb_putc(%arg0: !llvm.ptr, %arg1: i8) -> () {
%v170 = arith.constant 0 : i32
%v171 = arith.extsi %v170 : i32 to i64
%v172 = llvm.getelementptr %arg0[%v171] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v173 = llvm.load %v172 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v174 = arith.constant 0 : i32
%v175 = arith.extsi %v174 : i32 to i64
%v176 = llvm.getelementptr %arg0[%v175] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v177 = llvm.getelementptr %v176[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v178 = llvm.load %v177 : !llvm.ptr -> i32
%v179 = arith.constant 0 : i32
%v180 = arith.extsi %v179 : i32 to i64
%v181 = llvm.getelementptr %arg0[%v180] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v182 = llvm.load %v181 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v183 = arith.constant 0 : i32
%v184 = arith.extsi %v183 : i32 to i64
%v185 = llvm.getelementptr %arg0[%v184] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v186 = llvm.getelementptr %v185[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v187 = llvm.load %v186 : !llvm.ptr -> i32
%v188 = arith.cmpi sge, %v178, %v187 : i32
cf.cond_br %v188, ^b22, ^b23
^b22:
%v189 = arith.constant 1 : i32
%v190 = func.call @bb_reserve(%arg0, %v189) : (!llvm.ptr, i32) -> i1
%v191 = arith.constant 0 : i1
%v192 = arith.cmpi eq, %v190, %v191 : i1
cf.cond_br %v192, ^b24, ^b25
^b24:
func.return
^b25:
cf.br ^b26
^b26:
cf.br ^b27
^b23:
cf.br ^b27
^b27:
%v193 = arith.constant 0 : i32
%v194 = arith.extsi %v193 : i32 to i64
%v195 = llvm.getelementptr %arg0[%v194] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v196 = llvm.load %v195 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v197 = arith.constant 0 : i32
%v198 = arith.extsi %v197 : i32 to i64
%v199 = llvm.getelementptr %arg0[%v198] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v200 = llvm.getelementptr %v199[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v201 = llvm.load %v200 : !llvm.ptr -> !llvm.ptr
%v202 = arith.constant 0 : i32
%v203 = arith.extsi %v202 : i32 to i64
%v204 = llvm.getelementptr %arg0[%v203] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v205 = llvm.load %v204 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v206 = arith.constant 0 : i32
%v207 = arith.extsi %v206 : i32 to i64
%v208 = llvm.getelementptr %arg0[%v207] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v209 = llvm.getelementptr %v208[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v210 = llvm.load %v209 : !llvm.ptr -> i32
%v211 = arith.extsi %v210 : i32 to i64
%v212 = llvm.getelementptr %v201[%v211] : (!llvm.ptr, i64) -> !llvm.ptr, i8
llvm.store %arg1, %v212 : i8, !llvm.ptr
%v213 = arith.constant 0 : i32
%v214 = arith.extsi %v213 : i32 to i64
%v215 = llvm.getelementptr %arg0[%v214] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v216 = llvm.load %v215 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v217 = arith.constant 0 : i32
%v218 = arith.extsi %v217 : i32 to i64
%v219 = llvm.getelementptr %arg0[%v218] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v220 = llvm.getelementptr %v219[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v221 = llvm.load %v220 : !llvm.ptr -> i32
%v222 = arith.constant 1 : i32
%v223 = arith.addi %v221, %v222 : i32
%v224 = arith.constant 0 : i32
%v225 = arith.extsi %v224 : i32 to i64
%v226 = llvm.getelementptr %arg0[%v225] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v227 = llvm.getelementptr %v226[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
llvm.store %v223, %v227 : i32, !llvm.ptr
%v228 = arith.constant 0 : i32
%v229 = arith.constant 0 : i32
%v230 = arith.extsi %v229 : i32 to i64
%v231 = llvm.getelementptr %arg0[%v230] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v232 = llvm.load %v231 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v233 = arith.constant 0 : i32
%v234 = arith.extsi %v233 : i32 to i64
%v235 = llvm.getelementptr %arg0[%v234] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v236 = llvm.getelementptr %v235[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v237 = llvm.load %v236 : !llvm.ptr -> !llvm.ptr
%v238 = arith.constant 0 : i32
%v239 = arith.extsi %v238 : i32 to i64
%v240 = llvm.getelementptr %arg0[%v239] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v241 = llvm.load %v240 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v242 = arith.constant 0 : i32
%v243 = arith.extsi %v242 : i32 to i64
%v244 = llvm.getelementptr %arg0[%v243] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v245 = llvm.getelementptr %v244[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v246 = llvm.load %v245 : !llvm.ptr -> i32
%v247 = arith.trunci %v228 : i32 to i8
%v248 = arith.extsi %v246 : i32 to i64
%v249 = llvm.getelementptr %v237[%v248] : (!llvm.ptr, i64) -> !llvm.ptr, i8
llvm.store %v247, %v249 : i8, !llvm.ptr
func.return
}
func.func @bb_put_bytes(%arg0: !llvm.ptr, %arg1: !llvm.ptr, %arg2: i32) -> () {
%v250 = arith.constant 0 : i32
%v251 = arith.cmpi sle, %arg2, %v250 : i32
cf.cond_br %v251, ^b28, ^b29
^b28:
func.return
^b29:
cf.br ^b30
^b30:
%v252 = func.call @bb_reserve(%arg0, %arg2) : (!llvm.ptr, i32) -> i1
%v253 = arith.constant 0 : i1
%v254 = arith.cmpi eq, %v252, %v253 : i1
cf.cond_br %v254, ^b31, ^b32
^b31:
func.return
^b32:
cf.br ^b33
^b33:
%v255 = arith.constant 0 : i32
%v256 = arith.extsi %v255 : i32 to i64
%v257 = llvm.getelementptr %arg0[%v256] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v258 = llvm.load %v257 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v259 = arith.constant 0 : i32
%v260 = arith.extsi %v259 : i32 to i64
%v261 = llvm.getelementptr %arg0[%v260] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v262 = llvm.getelementptr %v261[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v263 = llvm.load %v262 : !llvm.ptr -> !llvm.ptr
%v264 = arith.constant 0 : i32
%v265 = arith.extsi %v264 : i32 to i64
%v266 = llvm.getelementptr %arg0[%v265] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v267 = llvm.load %v266 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v268 = arith.constant 0 : i32
%v269 = arith.extsi %v268 : i32 to i64
%v270 = llvm.getelementptr %arg0[%v269] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v271 = llvm.getelementptr %v270[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v272 = llvm.load %v271 : !llvm.ptr -> i32
%v273 = arith.constant 0 : i32
%v274 = llvm.mlir.constant(1 : i64) : i64
%v275 = llvm.alloca %v274 x i32 : (i64) -> !llvm.ptr
llvm.store %v273, %v275 : i32, !llvm.ptr
cf.br ^b34
^b34:
%v276 = llvm.load %v275 : !llvm.ptr -> i32
%v277 = arith.cmpi slt, %v276, %arg2 : i32
cf.cond_br %v277, ^b35, ^b36
^b35:
%v278 = llvm.load %v275 : !llvm.ptr -> i32
%v279 = arith.extsi %v278 : i32 to i64
%v280 = llvm.getelementptr %arg1[%v279] : (!llvm.ptr, i64) -> !llvm.ptr, i8
%v281 = llvm.load %v280 : !llvm.ptr -> i8
%v282 = llvm.load %v275 : !llvm.ptr -> i32
%v283 = arith.addi %v272, %v282 : i32
%v284 = arith.extsi %v283 : i32 to i64
%v285 = llvm.getelementptr %v263[%v284] : (!llvm.ptr, i64) -> !llvm.ptr, i8
llvm.store %v281, %v285 : i8, !llvm.ptr
%v286 = llvm.load %v275 : !llvm.ptr -> i32
%v287 = arith.constant 1 : i32
%v288 = arith.addi %v286, %v287 : i32
llvm.store %v288, %v275 : i32, !llvm.ptr
cf.br ^b34
^b36:
%v289 = arith.addi %v272, %arg2 : i32
%v290 = arith.constant 0 : i32
%v291 = arith.extsi %v290 : i32 to i64
%v292 = llvm.getelementptr %arg0[%v291] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v293 = llvm.getelementptr %v292[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
llvm.store %v289, %v293 : i32, !llvm.ptr
%v294 = arith.constant 0 : i32
%v295 = arith.constant 0 : i32
%v296 = arith.extsi %v295 : i32 to i64
%v297 = llvm.getelementptr %arg0[%v296] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v298 = llvm.load %v297 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v299 = arith.constant 0 : i32
%v300 = arith.extsi %v299 : i32 to i64
%v301 = llvm.getelementptr %arg0[%v300] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v302 = llvm.getelementptr %v301[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v303 = llvm.load %v302 : !llvm.ptr -> i32
%v304 = arith.trunci %v294 : i32 to i8
%v305 = arith.extsi %v303 : i32 to i64
%v306 = llvm.getelementptr %v263[%v305] : (!llvm.ptr, i64) -> !llvm.ptr, i8
llvm.store %v304, %v306 : i8, !llvm.ptr
func.return
}
func.func @bb_puts(%arg0: !llvm.ptr, %arg1: !llvm.ptr) -> () {
%v307 = func.call @strlen(%arg1) : (!llvm.ptr) -> i64
%v308 = arith.trunci %v307 : i64 to i32
func.call @bb_put_bytes(%arg0, %arg1, %v308) : (!llvm.ptr, !llvm.ptr, i32) -> ()
func.return
}
func.func @bb_put_span(%arg0: !llvm.ptr, %arg1: !llvm.ptr, %arg2: i32, %arg3: i32) -> () {
%v309 = arith.cmpi sle, %arg3, %arg2 : i32
cf.cond_br %v309, ^b37, ^b38
^b37:
func.return
^b38:
cf.br ^b39
^b39:
%v310 = arith.subi %arg3, %arg2 : i32
%v311 = func.call @bb_reserve(%arg0, %v310) : (!llvm.ptr, i32) -> i1
%v312 = arith.constant 0 : i1
%v313 = arith.cmpi eq, %v311, %v312 : i1
cf.cond_br %v313, ^b40, ^b41
^b40:
func.return
^b41:
cf.br ^b42
^b42:
%v314 = arith.constant 0 : i32
%v315 = arith.extsi %v314 : i32 to i64
%v316 = llvm.getelementptr %arg0[%v315] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v317 = llvm.load %v316 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v318 = arith.constant 0 : i32
%v319 = arith.extsi %v318 : i32 to i64
%v320 = llvm.getelementptr %arg0[%v319] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v321 = llvm.getelementptr %v320[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v322 = llvm.load %v321 : !llvm.ptr -> !llvm.ptr
%v323 = arith.constant 0 : i32
%v324 = arith.extsi %v323 : i32 to i64
%v325 = llvm.getelementptr %arg0[%v324] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v326 = llvm.load %v325 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v327 = arith.constant 0 : i32
%v328 = arith.extsi %v327 : i32 to i64
%v329 = llvm.getelementptr %arg0[%v328] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v330 = llvm.getelementptr %v329[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v331 = llvm.load %v330 : !llvm.ptr -> i32
%v332 = llvm.mlir.constant(1 : i64) : i64
%v333 = llvm.alloca %v332 x i32 : (i64) -> !llvm.ptr
llvm.store %v331, %v333 : i32, !llvm.ptr
%v334 = llvm.mlir.constant(1 : i64) : i64
%v335 = llvm.alloca %v334 x i32 : (i64) -> !llvm.ptr
llvm.store %arg2, %v335 : i32, !llvm.ptr
cf.br ^b43
^b43:
%v336 = llvm.load %v335 : !llvm.ptr -> i32
%v337 = arith.cmpi slt, %v336, %arg3 : i32
cf.cond_br %v337, ^b44, ^b45
^b44:
%v338 = llvm.load %v335 : !llvm.ptr -> i32
%v339 = arith.extsi %v338 : i32 to i64
%v340 = llvm.getelementptr %arg1[%v339] : (!llvm.ptr, i64) -> !llvm.ptr, i8
%v341 = llvm.load %v340 : !llvm.ptr -> i8
%v342 = llvm.load %v333 : !llvm.ptr -> i32
%v343 = arith.extsi %v342 : i32 to i64
%v344 = llvm.getelementptr %v322[%v343] : (!llvm.ptr, i64) -> !llvm.ptr, i8
llvm.store %v341, %v344 : i8, !llvm.ptr
%v345 = llvm.load %v333 : !llvm.ptr -> i32
%v346 = arith.constant 1 : i32
%v347 = arith.addi %v345, %v346 : i32
llvm.store %v347, %v333 : i32, !llvm.ptr
%v348 = llvm.load %v335 : !llvm.ptr -> i32
%v349 = arith.constant 1 : i32
%v350 = arith.addi %v348, %v349 : i32
llvm.store %v350, %v335 : i32, !llvm.ptr
cf.br ^b43
^b45:
%v351 = llvm.load %v333 : !llvm.ptr -> i32
%v352 = arith.constant 0 : i32
%v353 = arith.extsi %v352 : i32 to i64
%v354 = llvm.getelementptr %arg0[%v353] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v355 = llvm.getelementptr %v354[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
llvm.store %v351, %v355 : i32, !llvm.ptr
%v356 = arith.constant 0 : i32
%v357 = llvm.load %v333 : !llvm.ptr -> i32
%v358 = arith.trunci %v356 : i32 to i8
%v359 = arith.extsi %v357 : i32 to i64
%v360 = llvm.getelementptr %v322[%v359] : (!llvm.ptr, i64) -> !llvm.ptr, i8
llvm.store %v358, %v360 : i8, !llvm.ptr
func.return
}
func.func @bb_put_i64(%arg0: !llvm.ptr, %arg1: i64) -> () {
%v361 = arith.constant 0 : i32
%v362 = arith.extsi %v361 : i32 to i64
%v363 = arith.cmpi slt, %arg1, %v362 : i64
cf.cond_br %v363, ^b46, ^b47
^b46:
%v364 = arith.constant 45 : i32
%v365 = arith.trunci %v364 : i32 to i8
func.call @bb_putc(%arg0, %v365) : (!llvm.ptr, i8) -> ()
%v366 = arith.constant 0 : i32
%v367 = arith.constant 10 : i32
%v368 = arith.subi %v366, %v367 : i32
%v369 = arith.extsi %v368 : i32 to i64
%v370 = arith.cmpi sle, %arg1, %v369 : i64
cf.cond_br %v370, ^b48, ^b49
^b48:
%v371 = arith.constant 0 : i32
%v372 = arith.constant 10 : i32
%v373 = arith.extsi %v372 : i32 to i64
%v374 = arith.divsi %arg1, %v373 : i64
%v375 = arith.extsi %v371 : i32 to i64
%v376 = arith.subi %v375, %v374 : i64
func.call @bb_put_i64(%arg0, %v376) : (!llvm.ptr, i64) -> ()
cf.br ^b50
^b49:
cf.br ^b50
^b50:
%v377 = arith.constant 48 : i32
%v378 = arith.constant 10 : i32
%v379 = arith.extsi %v378 : i32 to i64
%v380 = arith.remsi %arg1, %v379 : i64
%v381 = arith.extsi %v377 : i32 to i64
%v382 = arith.subi %v381, %v380 : i64
%v383 = arith.trunci %v382 : i64 to i8
func.call @bb_putc(%arg0, %v383) : (!llvm.ptr, i8) -> ()
func.return
^b47:
cf.br ^b51
^b51:
%v384 = arith.constant 10 : i32
%v385 = arith.extsi %v384 : i32 to i64
%v386 = arith.cmpi sge, %arg1, %v385 : i64
cf.cond_br %v386, ^b52, ^b53
^b52:
%v387 = arith.constant 10 : i32
%v388 = arith.extsi %v387 : i32 to i64
%v389 = arith.divsi %arg1, %v388 : i64
func.call @bb_put_i64(%arg0, %v389) : (!llvm.ptr, i64) -> ()
cf.br ^b54
^b53:
cf.br ^b54
^b54:
%v390 = arith.constant 48 : i32
%v391 = arith.constant 10 : i32
%v392 = arith.extsi %v391 : i32 to i64
%v393 = arith.remsi %arg1, %v392 : i64
%v394 = arith.extsi %v390 : i32 to i64
%v395 = arith.addi %v394, %v393 : i64
%v396 = arith.trunci %v395 : i64 to i8
func.call @bb_putc(%arg0, %v396) : (!llvm.ptr, i8) -> ()
func.return
}
func.func @bb_put_i32(%arg0: !llvm.ptr, %arg1: i32) -> () {
%v397 = arith.extsi %arg1 : i32 to i64
func.call @bb_put_i64(%arg0, %v397) : (!llvm.ptr, i64) -> ()
func.return
}
func.func @bb_len(%arg0: !llvm.ptr) -> i32 {
%v398 = arith.constant 0 : i32
%v399 = arith.extsi %v398 : i32 to i64
%v400 = llvm.getelementptr %arg0[%v399] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v401 = llvm.load %v400 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v402 = arith.constant 0 : i32
%v403 = arith.extsi %v402 : i32 to i64
%v404 = llvm.getelementptr %arg0[%v403] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v405 = llvm.getelementptr %v404[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v406 = llvm.load %v405 : !llvm.ptr -> i32
func.return %v406 : i32
}
func.func @bb_at(%arg0: !llvm.ptr, %arg1: i32) -> i32 {
%v407 = arith.constant 0 : i32
%v408 = arith.cmpi slt, %arg1, %v407 : i32
%v409 = scf.if %v408 -> (i1) {
%v410 = arith.constant true
scf.yield %v410 : i1
} else {
%v411 = arith.constant 0 : i32
%v412 = arith.extsi %v411 : i32 to i64
%v413 = llvm.getelementptr %arg0[%v412] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v414 = llvm.load %v413 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v415 = arith.constant 0 : i32
%v416 = arith.extsi %v415 : i32 to i64
%v417 = llvm.getelementptr %arg0[%v416] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v418 = llvm.getelementptr %v417[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v419 = llvm.load %v418 : !llvm.ptr -> i32
%v420 = arith.cmpi sge, %arg1, %v419 : i32
scf.yield %v420 : i1
}
cf.cond_br %v409, ^b55, ^b56
^b55:
%v421 = arith.constant 0 : i32
%v422 = arith.constant 1 : i32
%v423 = arith.subi %v421, %v422 : i32
func.return %v423 : i32
^b56:
cf.br ^b57
^b57:
%v424 = arith.constant 0 : i32
%v425 = arith.extsi %v424 : i32 to i64
%v426 = llvm.getelementptr %arg0[%v425] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v427 = llvm.load %v426 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v428 = arith.constant 0 : i32
%v429 = arith.extsi %v428 : i32 to i64
%v430 = llvm.getelementptr %arg0[%v429] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v431 = llvm.getelementptr %v430[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v432 = llvm.load %v431 : !llvm.ptr -> !llvm.ptr
%v433 = arith.extsi %arg1 : i32 to i64
%v434 = llvm.getelementptr %v432[%v433] : (!llvm.ptr, i64) -> !llvm.ptr, i8
%v435 = llvm.load %v434 : !llvm.ptr -> i8
%v436 = arith.extui %v435 : i8 to i32
func.return %v436 : i32
}
func.func @bb_cstr(%arg0: !llvm.ptr) -> !llvm.ptr {
%v437 = arith.constant 0 : i32
%v438 = arith.extsi %v437 : i32 to i64
%v439 = llvm.getelementptr %arg0[%v438] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v440 = llvm.load %v439 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v441 = arith.constant 0 : i32
%v442 = arith.extsi %v441 : i32 to i64
%v443 = llvm.getelementptr %arg0[%v442] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v444 = llvm.getelementptr %v443[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v445 = llvm.load %v444 : !llvm.ptr -> !llvm.ptr
func.return %v445 : !llvm.ptr
}
func.func @bb_str(%arg0: !llvm.ptr) -> !llvm.ptr {
%v446 = arith.constant 0 : i32
%v447 = arith.extsi %v446 : i32 to i64
%v448 = llvm.getelementptr %arg0[%v447] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v449 = llvm.load %v448 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v450 = arith.constant 0 : i32
%v451 = arith.extsi %v450 : i32 to i64
%v452 = llvm.getelementptr %arg0[%v451] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v453 = llvm.getelementptr %v452[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v454 = llvm.load %v453 : !llvm.ptr -> i32
%v455 = arith.constant 1 : i32
%v456 = arith.addi %v454, %v455 : i32
%v457 = arith.extsi %v456 : i32 to i64
%v458 = func.call @flow_mem_malloc(%v457) : (i64) -> !llvm.ptr
%v459 = arith.constant 0 : i32
%v460 = llvm.mlir.constant(1 : i64) : i64
%v461 = llvm.alloca %v460 x i32 : (i64) -> !llvm.ptr
llvm.store %v459, %v461 : i32, !llvm.ptr
cf.br ^b58
^b58:
%v462 = llvm.load %v461 : !llvm.ptr -> i32
%v463 = arith.constant 0 : i32
%v464 = arith.extsi %v463 : i32 to i64
%v465 = llvm.getelementptr %arg0[%v464] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v466 = llvm.load %v465 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v467 = arith.constant 0 : i32
%v468 = arith.extsi %v467 : i32 to i64
%v469 = llvm.getelementptr %arg0[%v468] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v470 = llvm.getelementptr %v469[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v471 = llvm.load %v470 : !llvm.ptr -> i32
%v472 = arith.cmpi slt, %v462, %v471 : i32
cf.cond_br %v472, ^b59, ^b60
^b59:
%v473 = arith.constant 0 : i32
%v474 = arith.extsi %v473 : i32 to i64
%v475 = llvm.getelementptr %arg0[%v474] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v476 = llvm.load %v475 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v477 = arith.constant 0 : i32
%v478 = arith.extsi %v477 : i32 to i64
%v479 = llvm.getelementptr %arg0[%v478] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v480 = llvm.getelementptr %v479[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v481 = llvm.load %v480 : !llvm.ptr -> !llvm.ptr
%v482 = llvm.load %v461 : !llvm.ptr -> i32
%v483 = arith.extsi %v482 : i32 to i64
%v484 = llvm.getelementptr %v481[%v483] : (!llvm.ptr, i64) -> !llvm.ptr, i8
%v485 = llvm.load %v484 : !llvm.ptr -> i8
%v486 = llvm.load %v461 : !llvm.ptr -> i32
%v487 = arith.extsi %v486 : i32 to i64
%v488 = llvm.getelementptr %v458[%v487] : (!llvm.ptr, i64) -> !llvm.ptr, i8
llvm.store %v485, %v488 : i8, !llvm.ptr
%v489 = llvm.load %v461 : !llvm.ptr -> i32
%v490 = arith.constant 1 : i32
%v491 = arith.addi %v489, %v490 : i32
llvm.store %v491, %v461 : i32, !llvm.ptr
cf.br ^b58
^b60:
%v492 = arith.constant 0 : i32
%v493 = arith.constant 0 : i32
%v494 = arith.extsi %v493 : i32 to i64
%v495 = llvm.getelementptr %arg0[%v494] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v496 = llvm.load %v495 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v497 = arith.constant 0 : i32
%v498 = arith.extsi %v497 : i32 to i64
%v499 = llvm.getelementptr %arg0[%v498] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v500 = llvm.getelementptr %v499[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v501 = llvm.load %v500 : !llvm.ptr -> i32
%v502 = arith.trunci %v492 : i32 to i8
%v503 = arith.extsi %v501 : i32 to i64
%v504 = llvm.getelementptr %v458[%v503] : (!llvm.ptr, i64) -> !llvm.ptr, i8
llvm.store %v502, %v504 : i8, !llvm.ptr
func.return %v458 : !llvm.ptr
}
func.func @bb_truncate(%arg0: !llvm.ptr, %arg1: i32) -> () {
%v505 = arith.constant 0 : i32
%v506 = arith.cmpi sge, %arg1, %v505 : i32
%v507 = scf.if %v506 -> (i1) {
%v508 = arith.constant 0 : i32
%v509 = arith.extsi %v508 : i32 to i64
%v510 = llvm.getelementptr %arg0[%v509] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v511 = llvm.load %v510 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v512 = arith.constant 0 : i32
%v513 = arith.extsi %v512 : i32 to i64
%v514 = llvm.getelementptr %arg0[%v513] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v515 = llvm.getelementptr %v514[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v516 = llvm.load %v515 : !llvm.ptr -> i32
%v517 = arith.cmpi slt, %arg1, %v516 : i32
scf.yield %v517 : i1
} else {
%v518 = arith.constant false
scf.yield %v518 : i1
}
cf.cond_br %v507, ^b61, ^b62
^b61:
%v519 = arith.constant 0 : i32
%v520 = arith.extsi %v519 : i32 to i64
%v521 = llvm.getelementptr %arg0[%v520] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v522 = llvm.getelementptr %v521[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
llvm.store %arg1, %v522 : i32, !llvm.ptr
%v523 = arith.constant 0 : i32
%v524 = arith.constant 0 : i32
%v525 = arith.extsi %v524 : i32 to i64
%v526 = llvm.getelementptr %arg0[%v525] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v527 = llvm.load %v526 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v528 = arith.constant 0 : i32
%v529 = arith.extsi %v528 : i32 to i64
%v530 = llvm.getelementptr %arg0[%v529] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v531 = llvm.getelementptr %v530[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32)>
%v532 = llvm.load %v531 : !llvm.ptr -> !llvm.ptr
%v533 = arith.trunci %v523 : i32 to i8
%v534 = arith.extsi %arg1 : i32 to i64
%v535 = llvm.getelementptr %v532[%v534] : (!llvm.ptr, i64) -> !llvm.ptr, i8
llvm.store %v533, %v535 : i8, !llvm.ptr
cf.br ^b63
^b62:
cf.br ^b63
^b63:
func.return
}
func.func @bb_clear(%arg0: !llvm.ptr) -> () {
%v536 = arith.constant 0 : i32
func.call @bb_truncate(%arg0, %v536) : (!llvm.ptr, i32) -> ()
func.return
}
func.func @bb_is_space(%arg0: i8) -> i1 {
%v537 = arith.constant 32 : i32
%v538 = arith.extui %arg0 : i8 to i32
%v539 = arith.cmpi eq, %v538, %v537 : i32
%v540 = scf.if %v539 -> (i1) {
%v541 = arith.constant true
scf.yield %v541 : i1
} else {
%v542 = arith.constant 9 : i32
%v543 = arith.extui %arg0 : i8 to i32
%v544 = arith.cmpi uge, %v543, %v542 : i32
%v545 = scf.if %v544 -> (i1) {
%v546 = arith.constant 13 : i32
%v547 = arith.extui %arg0 : i8 to i32
%v548 = arith.cmpi ule, %v547, %v546 : i32
scf.yield %v548 : i1
} else {
%v549 = arith.constant false
scf.yield %v549 : i1
}
scf.yield %v545 : i1
}
%v550 = scf.if %v540 -> (i1) {
%v551 = arith.constant true
scf.yield %v551 : i1
} else {
%v552 = arith.constant 28 : i32
%v553 = arith.extui %arg0 : i8 to i32
%v554 = arith.cmpi uge, %v553, %v552 : i32
%v555 = scf.if %v554 -> (i1) {
%v556 = arith.constant 31 : i32
%v557 = arith.extui %arg0 : i8 to i32
%v558 = arith.cmpi ule, %v557, %v556 : i32
scf.yield %v558 : i1
} else {
%v559 = arith.constant false
scf.yield %v559 : i1
}
scf.yield %v555 : i1
}
func.return %v550 : i1
}
func.func @bb_is_digit(%arg0: i8) -> i1 {
%v560 = arith.constant 48 : i32
%v561 = arith.extui %arg0 : i8 to i32
%v562 = arith.cmpi uge, %v561, %v560 : i32
%v563 = scf.if %v562 -> (i1) {
%v564 = arith.constant 57 : i32
%v565 = arith.extui %arg0 : i8 to i32
%v566 = arith.cmpi ule, %v565, %v564 : i32
scf.yield %v566 : i1
} else {
%v567 = arith.constant false
scf.yield %v567 : i1
}
func.return %v563 : i1
}
func.func @bb_is_alpha(%arg0: i8) -> i1 {
%v568 = arith.constant 65 : i32
%v569 = arith.extui %arg0 : i8 to i32
%v570 = arith.cmpi uge, %v569, %v568 : i32
%v571 = scf.if %v570 -> (i1) {
%v572 = arith.constant 90 : i32
%v573 = arith.extui %arg0 : i8 to i32
%v574 = arith.cmpi ule, %v573, %v572 : i32
scf.yield %v574 : i1
} else {
%v575 = arith.constant false
scf.yield %v575 : i1
}
%v576 = scf.if %v571 -> (i1) {
%v577 = arith.constant true
scf.yield %v577 : i1
} else {
%v578 = arith.constant 97 : i32
%v579 = arith.extui %arg0 : i8 to i32
%v580 = arith.cmpi uge, %v579, %v578 : i32
%v581 = scf.if %v580 -> (i1) {
%v582 = arith.constant 122 : i32
%v583 = arith.extui %arg0 : i8 to i32
%v584 = arith.cmpi ule, %v583, %v582 : i32
scf.yield %v584 : i1
} else {
%v585 = arith.constant false
scf.yield %v585 : i1
}
scf.yield %v581 : i1
}
func.return %v576 : i1
}
func.func @bb_is_word(%arg0: i8) -> i1 {
%v586 = func.call @bb_is_alpha(%arg0) : (i8) -> i1
%v587 = scf.if %v586 -> (i1) {
%v588 = arith.constant true
scf.yield %v588 : i1
} else {
%v589 = func.call @bb_is_digit(%arg0) : (i8) -> i1
scf.yield %v589 : i1
}
%v590 = scf.if %v587 -> (i1) {
%v591 = arith.constant true
scf.yield %v591 : i1
} else {
%v592 = arith.constant 95 : i32
%v593 = arith.extui %arg0 : i8 to i32
%v594 = arith.cmpi eq, %v593, %v592 : i32
scf.yield %v594 : i1
}
func.return %v590 : i1
}
func.func @bb_span_eq(%arg0: !llvm.ptr, %arg1: i32, %arg2: i32, %arg3: !llvm.ptr, %arg4: i32, %arg5: i32) -> i1 {
%v595 = arith.subi %arg2, %arg1 : i32
%v596 = arith.subi %arg5, %arg4 : i32
%v597 = arith.cmpi ne, %v595, %v596 : i32
cf.cond_br %v597, ^b64, ^b65
^b64:
%v598 = arith.constant 0 : i1
func.return %v598 : i1
^b65:
cf.br ^b66
^b66:
%v599 = arith.constant 0 : i32
%v600 = llvm.mlir.constant(1 : i64) : i64
%v601 = llvm.alloca %v600 x i32 : (i64) -> !llvm.ptr
llvm.store %v599, %v601 : i32, !llvm.ptr
cf.br ^b67
^b67:
%v602 = llvm.load %v601 : !llvm.ptr -> i32
%v603 = arith.subi %arg2, %arg1 : i32
%v604 = arith.cmpi slt, %v602, %v603 : i32
cf.cond_br %v604, ^b68, ^b69
^b68:
%v605 = llvm.load %v601 : !llvm.ptr -> i32
%v606 = arith.addi %arg1, %v605 : i32
%v607 = arith.extsi %v606 : i32 to i64
%v608 = llvm.getelementptr %arg0[%v607] : (!llvm.ptr, i64) -> !llvm.ptr, i8
%v609 = llvm.load %v608 : !llvm.ptr -> i8
%v610 = llvm.load %v601 : !llvm.ptr -> i32
%v611 = arith.addi %arg4, %v610 : i32
%v612 = arith.extsi %v611 : i32 to i64
%v613 = llvm.getelementptr %arg3[%v612] : (!llvm.ptr, i64) -> !llvm.ptr, i8
%v614 = llvm.load %v613 : !llvm.ptr -> i8
%v615 = arith.extui %v609 : i8 to i32
%v616 = arith.extui %v614 : i8 to i32
%v617 = arith.cmpi ne, %v615, %v616 : i32
cf.cond_br %v617, ^b70, ^b71
^b70:
%v618 = arith.constant 0 : i1
func.return %v618 : i1
^b71:
cf.br ^b72
^b72:
%v619 = llvm.load %v601 : !llvm.ptr -> i32
%v620 = arith.constant 1 : i32
%v621 = arith.addi %v619, %v620 : i32
llvm.store %v621, %v601 : i32, !llvm.ptr
cf.br ^b67
^b69:
%v622 = arith.constant 1 : i1
func.return %v622 : i1
}
func.func @main() -> i32 {
%v623 = arith.constant 4 : i32
%v624 = func.call @dep_scale(%v623) : (i32) -> i32
%v625 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v626 = llvm.call @printf(%v625, %v624) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v627 = arith.constant 0 : i32
%v628 = arith.constant 16 : i32
%v629 = func.call @bb_new(%v628) : (i32) -> !llvm.ptr
%v630 = llvm.mlir.addressof @str_13 : !llvm.ptr
func.call @bb_puts(%v629, %v630) : (!llvm.ptr, !llvm.ptr) -> ()
%v631 = func.call @bb_len(%v629) : (!llvm.ptr) -> i32
%v632 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v633 = llvm.call @printf(%v632, %v631) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v634 = arith.constant 0 : i32
func.call @bb_free(%v629) : (!llvm.ptr) -> ()
%v635 = llvm.mlir.addressof @dep_calls : !llvm.ptr
%v636 = llvm.load %v635 : !llvm.ptr -> i32
%v637 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v638 = llvm.call @printf(%v637, %v636) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v639 = arith.constant 0 : i32
%v640 = arith.constant 0 : i32
func.return %v640 : i32
}
}
