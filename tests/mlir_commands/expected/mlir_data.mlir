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
llvm.mlir.global internal constant @str_16("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
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
// Struct: P
// Fields:
//   x: i32
//   y: f32
// Struct: Box
// Fields:
//   vals: memref<4xi32>
//   n: i32
func.func @sum(%arg0: !llvm.ptr) -> i32 {
%v1 = llvm.mlir.constant(1 : i64) : i64
%v2 = llvm.alloca %v1 x i32 : (i64) -> !llvm.ptr
%v3 = arith.constant 0 : i32
llvm.store %v3, %v2 : i32, !llvm.ptr
%v4 = arith.constant 0 : i32
%v5 = arith.constant 3 : i32
%v6 = arith.index_cast %v4 : i32 to index
%v7 = arith.index_cast %v5 : i32 to index
%v8 = arith.constant 1 : index
%v9 = arith.constant -1 : index
%v10 = arith.cmpi sle, %v6, %v7 : index
%v11 = arith.select %v10, %v8, %v9 : index
cf.br ^b1(%v6 : index)
^b1(%v12: index):
%v13 = arith.cmpi slt, %v12, %v7 : index
%v14 = arith.cmpi sgt, %v12, %v7 : index
%v15 = arith.select %v10, %v13, %v14 : i1
cf.cond_br %v15, ^b2(%v12 : index), ^b3(%v12 : index)
^b2(%v16: index):
%v17 = llvm.load %v2 : !llvm.ptr -> i32
%v18 = arith.index_cast %v16 : index to i32
%v19 = arith.constant 3 : i32
%v20 = arith.cmpi uge, %v18, %v19 : i32
scf.if %v20 {
%v21 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v21) : (!llvm.ptr) -> ()
}
%v22 = arith.index_cast %v16 : index to i64
%v23 = llvm.getelementptr %arg0[0, %v22] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
%v24 = llvm.load %v23 : !llvm.ptr -> !llvm.struct<(i32, f32)>
%v25 = arith.index_cast %v16 : index to i64
%v26 = llvm.getelementptr %arg0[0, %v25] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
%v27 = llvm.getelementptr %v26[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, f32)>
%v28 = llvm.load %v27 : !llvm.ptr -> i32
%v29 = arith.addi %v17, %v28 : i32
llvm.store %v29, %v2 : i32, !llvm.ptr
%v30 = arith.addi %v16, %v11 : index
cf.br ^b1(%v30 : index)
^b3(%v31: index):
%v32 = llvm.load %v2 : !llvm.ptr -> i32
func.return %v32 : i32
}
func.func @add4(%arg0: !llvm.ptr, %arg1: !llvm.ptr, %arg2: !llvm.ptr, %arg3: i32) -> () {
%v33 = arith.constant 0 : i32
%v34 = arith.index_cast %v33 : i32 to index
%v35 = arith.index_cast %arg3 : i32 to index
%v36 = arith.constant 1 : index
%v37 = arith.constant -1 : index
%v38 = arith.cmpi sle, %v34, %v35 : index
%v39 = arith.select %v38, %v36, %v37 : index
cf.br ^b4(%v34 : index)
^b4(%v40: index):
%v41 = arith.cmpi slt, %v40, %v35 : index
%v42 = arith.cmpi sgt, %v40, %v35 : index
%v43 = arith.select %v38, %v41, %v42 : i1
cf.cond_br %v43, ^b5(%v40 : index), ^b6(%v40 : index)
^b5(%v44: index):
%v45 = arith.index_cast %v44 : index to i64
%v46 = llvm.getelementptr %arg1[%v45] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v47 = llvm.load %v46 : !llvm.ptr -> f32
%v48 = arith.index_cast %v44 : index to i64
%v49 = llvm.getelementptr %arg2[%v48] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v50 = llvm.load %v49 : !llvm.ptr -> f32
%v51 = arith.addf %v47, %v50 : f32
%v52 = arith.index_cast %v44 : index to i64
%v53 = llvm.getelementptr %arg0[%v52] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v51, %v53 : f32, !llvm.ptr
%v54 = arith.addi %v44, %v39 : index
cf.br ^b4(%v54 : index)
^b6(%v55: index):
func.return
}
func.func @main() -> i32 {
%v56 = llvm.mlir.constant(1 : i64) : i64
%v57 = llvm.alloca %v56 x !llvm.array<3 x !llvm.struct<(i32, f32)>> : (i64) -> !llvm.ptr
%v58 = llvm.mlir.constant(1 : i64) : i64
%v59 = llvm.alloca %v58 x !llvm.ptr : (i64) -> !llvm.ptr
%v60 = llvm.mlir.constant(1 : i64) : i64
%v61 = llvm.alloca %v60 x !llvm.struct<(i32, f32)> : (i64) -> !llvm.ptr
%v62 = llvm.mlir.constant(1 : i64) : i64
%v63 = llvm.alloca %v62 x !llvm.struct<(!llvm.array<4 x i32>, i32)> : (i64) -> !llvm.ptr
%v64 = llvm.mlir.constant(1 : i64) : i64
%v65 = llvm.alloca %v64 x i32 : (i64) -> !llvm.ptr
%v66 = llvm.mlir.undef : !llvm.struct<(i32, f32)>
%v67 = arith.constant 1 : i32
%v68 = llvm.insertvalue %v67, %v66[0] : !llvm.struct<(i32, f32)>
%v69 = arith.constant 1.0 : f64
%v70 = arith.truncf %v69 : f64 to f32
%v71 = llvm.insertvalue %v70, %v68[1] : !llvm.struct<(i32, f32)>
%v72 = llvm.mlir.undef : !llvm.struct<(i32, f32)>
%v73 = arith.constant 2 : i32
%v74 = llvm.insertvalue %v73, %v72[0] : !llvm.struct<(i32, f32)>
%v75 = arith.constant 2.0 : f64
%v76 = arith.truncf %v75 : f64 to f32
%v77 = llvm.insertvalue %v76, %v74[1] : !llvm.struct<(i32, f32)>
%v78 = llvm.mlir.undef : !llvm.struct<(i32, f32)>
%v79 = arith.constant 3 : i32
%v80 = llvm.insertvalue %v79, %v78[0] : !llvm.struct<(i32, f32)>
%v81 = arith.constant 3.0 : f64
%v82 = arith.truncf %v81 : f64 to f32
%v83 = llvm.insertvalue %v82, %v80[1] : !llvm.struct<(i32, f32)>
%v84 = arith.constant 24 : i64
func.call @flow_mem_note_stack(%v84) : (i64) -> ()
%v85 = llvm.mlir.zero : !llvm.array<3 x !llvm.struct<(i32, f32)>>
llvm.store %v85, %v57 : !llvm.array<3 x !llvm.struct<(i32, f32)>>, !llvm.ptr
%v86 = llvm.mlir.constant(0 : i64) : i64
%v87 = llvm.getelementptr %v57[0, %v86] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
llvm.store %v71, %v87 : !llvm.struct<(i32, f32)>, !llvm.ptr
%v88 = llvm.mlir.constant(1 : i64) : i64
%v89 = llvm.getelementptr %v57[0, %v88] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
llvm.store %v77, %v89 : !llvm.struct<(i32, f32)>, !llvm.ptr
%v90 = llvm.mlir.constant(2 : i64) : i64
%v91 = llvm.getelementptr %v57[0, %v90] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
llvm.store %v83, %v91 : !llvm.struct<(i32, f32)>, !llvm.ptr
llvm.store %v57, %v59 : !llvm.ptr, !llvm.ptr
%v92 = arith.constant 20 : i32
%v93 = llvm.load %v59 : !llvm.ptr -> !llvm.ptr
%v94 = arith.constant 1 : i32
%v95 = arith.extsi %v94 : i32 to i64
%v96 = llvm.getelementptr %v93[0, %v95] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
%v97 = llvm.getelementptr %v96[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, f32)>
llvm.store %v92, %v97 : i32, !llvm.ptr
%v98 = llvm.load %v59 : !llvm.ptr -> !llvm.ptr
%v99 = arith.constant 2 : i32
%v100 = arith.constant 3 : i32
%v101 = arith.cmpi uge, %v99, %v100 : i32
scf.if %v101 {
%v102 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v102) : (!llvm.ptr) -> ()
}
%v103 = arith.extsi %v99 : i32 to i64
%v104 = llvm.getelementptr %v98[0, %v103] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
%v105 = llvm.load %v104 : !llvm.ptr -> !llvm.struct<(i32, f32)>
llvm.store %v105, %v61 : !llvm.struct<(i32, f32)>, !llvm.ptr
%v106 = llvm.mlir.undef : !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v107 = llvm.mlir.zero : !llvm.array<4 x i32>
%v108 = arith.constant 1 : i32
%v109 = llvm.insertvalue %v108, %v107[0] : !llvm.array<4 x i32>
%v110 = arith.constant 2 : i32
%v111 = llvm.insertvalue %v110, %v109[1] : !llvm.array<4 x i32>
%v112 = arith.constant 3 : i32
%v113 = llvm.insertvalue %v112, %v111[2] : !llvm.array<4 x i32>
%v114 = arith.constant 4 : i32
%v115 = llvm.insertvalue %v114, %v113[3] : !llvm.array<4 x i32>
%v116 = llvm.insertvalue %v115, %v106[0] : !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v117 = arith.constant 4 : i32
%v118 = llvm.insertvalue %v117, %v116[1] : !llvm.struct<(!llvm.array<4 x i32>, i32)>
llvm.store %v118, %v63 : !llvm.struct<(!llvm.array<4 x i32>, i32)>, !llvm.ptr
%v119 = llvm.load %v59 : !llvm.ptr -> !llvm.ptr
%v120 = func.call @sum(%v119) : (!llvm.ptr) -> i32
%v121 = llvm.load %v61 : !llvm.ptr -> !llvm.struct<(i32, f32)>
%v122 = llvm.getelementptr %v61[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, f32)>
%v123 = llvm.load %v122 : !llvm.ptr -> i32
%v124 = arith.addi %v120, %v123 : i32
%v125 = llvm.load %v63 : !llvm.ptr -> !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v126 = llvm.getelementptr %v63[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v127 = arith.constant 3 : i32
%v128 = arith.extsi %v127 : i32 to i64
%v129 = llvm.getelementptr %v126[0, %v128] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x i32>
%v130 = llvm.load %v129 : !llvm.ptr -> i32
%v131 = arith.addi %v124, %v130 : i32
%v132 = llvm.mlir.addressof @str_15 : !llvm.ptr
%v133 = llvm.call @printf(%v132, %v131) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v134 = arith.constant 0 : i32
%v135 = memref.alloca() : memref<8xi32>
%v136 = arith.constant 0 : i32
%v137 = arith.constant 8 : i32
%v138 = arith.index_cast %v136 : i32 to index
%v139 = arith.index_cast %v137 : i32 to index
%v140 = arith.constant 1 : index
%v141 = arith.constant -1 : index
%v142 = arith.cmpi sle, %v138, %v139 : index
%v143 = arith.select %v142, %v140, %v141 : index
cf.br ^b7(%v138 : index)
^b7(%v144: index):
%v145 = arith.cmpi slt, %v144, %v139 : index
%v146 = arith.cmpi sgt, %v144, %v139 : index
%v147 = arith.select %v142, %v145, %v146 : i1
cf.cond_br %v147, ^b8(%v144 : index), ^b9(%v144 : index)
^b8(%v148: index):
%v149 = arith.constant 2 : i32
%v150 = arith.index_cast %v148 : index to i32
%v151 = arith.muli %v150, %v149 : i32
memref.store %v151, %v135[%v148] : memref<8xi32>
%v152 = arith.addi %v148, %v143 : index
cf.br ^b7(%v152 : index)
^b9(%v153: index):
%v154 = arith.constant 0 : i32
llvm.store %v154, %v65 : i32, !llvm.ptr
%v155 = arith.constant 0 : i32
%v156 = arith.constant 8 : i32
%v157 = arith.index_cast %v155 : i32 to index
%v158 = arith.index_cast %v156 : i32 to index
%v159 = arith.constant 1 : index
%v160 = arith.constant -1 : index
%v161 = arith.cmpi sle, %v157, %v158 : index
%v162 = arith.select %v161, %v159, %v160 : index
cf.br ^b10(%v157 : index)
^b10(%v163: index):
%v164 = arith.cmpi slt, %v163, %v158 : index
%v165 = arith.cmpi sgt, %v163, %v158 : index
%v166 = arith.select %v161, %v164, %v165 : i1
cf.cond_br %v166, ^b11(%v163 : index), ^b12(%v163 : index)
^b11(%v167: index):
%v168 = llvm.load %v65 : !llvm.ptr -> i32
%v169 = arith.index_cast %v167 : index to i32
%v170 = arith.constant 8 : i32
%v171 = arith.cmpi uge, %v169, %v170 : i32
scf.if %v171 {
%v172 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v172) : (!llvm.ptr) -> ()
}
%v173 = memref.load %v135[%v167] : memref<8xi32>
%v174 = arith.addi %v168, %v173 : i32
llvm.store %v174, %v65 : i32, !llvm.ptr
%v175 = arith.addi %v167, %v162 : index
cf.br ^b10(%v175 : index)
^b12(%v176: index):
%v177 = llvm.load %v65 : !llvm.ptr -> i32
%v178 = llvm.mlir.addressof @str_15 : !llvm.ptr
%v179 = llvm.call @printf(%v178, %v177) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v180 = arith.constant 0 : i32
%v181 = arith.constant 16 : i32
%v182 = arith.extsi %v181 : i32 to i64
%v183 = func.call @flow_mem_malloc(%v182) : (i64) -> !llvm.ptr
%v184 = arith.constant 16 : i32
%v185 = arith.extsi %v184 : i32 to i64
%v186 = func.call @flow_mem_malloc(%v185) : (i64) -> !llvm.ptr
%v187 = arith.constant 16 : i32
%v188 = arith.extsi %v187 : i32 to i64
%v189 = func.call @flow_mem_malloc(%v188) : (i64) -> !llvm.ptr
%v190 = arith.constant 0 : i32
%v191 = arith.constant 4 : i32
%v192 = arith.index_cast %v190 : i32 to index
%v193 = arith.index_cast %v191 : i32 to index
%v194 = arith.constant 1 : index
%v195 = arith.constant -1 : index
%v196 = arith.cmpi sle, %v192, %v193 : index
%v197 = arith.select %v196, %v194, %v195 : index
cf.br ^b13(%v192 : index)
^b13(%v198: index):
%v199 = arith.cmpi slt, %v198, %v193 : index
%v200 = arith.cmpi sgt, %v198, %v193 : index
%v201 = arith.select %v196, %v199, %v200 : i1
cf.cond_br %v201, ^b14(%v198 : index), ^b15(%v198 : index)
^b14(%v202: index):
%v203 = arith.constant 1.5 : f64
%v204 = arith.truncf %v203 : f64 to f32
%v205 = arith.index_cast %v202 : index to i64
%v206 = llvm.getelementptr %v186[%v205] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v204, %v206 : f32, !llvm.ptr
%v207 = arith.constant 2.0 : f64
%v208 = arith.truncf %v207 : f64 to f32
%v209 = arith.index_cast %v202 : index to i64
%v210 = llvm.getelementptr %v189[%v209] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v208, %v210 : f32, !llvm.ptr
%v211 = arith.addi %v202, %v197 : index
cf.br ^b13(%v211 : index)
^b15(%v212: index):
%v213 = arith.constant 4 : i32
func.call @add4(%v183, %v186, %v189, %v213) : (!llvm.ptr, !llvm.ptr, !llvm.ptr, i32) -> ()
%v214 = arith.constant 3 : i32
%v215 = arith.extsi %v214 : i32 to i64
%v216 = llvm.getelementptr %v183[%v215] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v217 = llvm.load %v216 : !llvm.ptr -> f32
%v218 = arith.extf %v217 : f32 to f64
%v219 = llvm.mlir.addressof @str_16 : !llvm.ptr
%v220 = llvm.call @printf(%v219, %v218) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v221 = arith.constant 0 : i32
%v222 = arith.constant 0 : i32
func.return %v222 : i32
}
}
