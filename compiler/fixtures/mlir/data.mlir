module {
func.func private @memcpy(!llvm.ptr, !llvm.ptr, i64) -> !llvm.ptr
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
llvm.mlir.global internal constant @str_13("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
// Struct: P
// Fields:
//   x: i32
//   y: f32
// Struct: Box
// Fields:
//   vals: memref<4xi32>
//   n: i32
func.func @sum(%arg0: !llvm.ptr) -> i32 {
%v1 = arith.constant 0 : i32
%v2 = llvm.mlir.constant(1 : i64) : i64
%v3 = llvm.alloca %v2 x i32 : (i64) -> !llvm.ptr
llvm.store %v1, %v3 : i32, !llvm.ptr
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
%v17 = llvm.load %v3 : !llvm.ptr -> i32
%v18 = arith.index_cast %v16 : index to i64
%v19 = llvm.getelementptr %arg0[0, %v18] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
%v20 = llvm.load %v19 : !llvm.ptr -> !llvm.struct<(i32, f32)>
%v21 = arith.index_cast %v16 : index to i64
%v22 = llvm.getelementptr %arg0[0, %v21] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
%v23 = llvm.getelementptr %v22[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, f32)>
%v24 = llvm.load %v23 : !llvm.ptr -> i32
%v25 = arith.addi %v17, %v24 : i32
llvm.store %v25, %v3 : i32, !llvm.ptr
%v26 = arith.addi %v16, %v11 : index
cf.br ^b1(%v26 : index)
^b3(%v27: index):
%v28 = llvm.load %v3 : !llvm.ptr -> i32
func.return %v28 : i32
}
func.func @add4(%arg0: !llvm.ptr, %arg1: !llvm.ptr, %arg2: !llvm.ptr, %arg3: i32) -> () {
%v29 = arith.constant 0 : i32
%v30 = arith.index_cast %v29 : i32 to index
%v31 = arith.index_cast %arg3 : i32 to index
%v32 = arith.constant 1 : index
%v33 = arith.constant -1 : index
%v34 = arith.cmpi sle, %v30, %v31 : index
%v35 = arith.select %v34, %v32, %v33 : index
cf.br ^b4(%v30 : index)
^b4(%v36: index):
%v37 = arith.cmpi slt, %v36, %v31 : index
%v38 = arith.cmpi sgt, %v36, %v31 : index
%v39 = arith.select %v34, %v37, %v38 : i1
cf.cond_br %v39, ^b5(%v36 : index), ^b6(%v36 : index)
^b5(%v40: index):
%v41 = arith.index_cast %v40 : index to i64
%v42 = llvm.getelementptr %arg1[%v41] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v43 = llvm.load %v42 : !llvm.ptr -> f32
%v44 = arith.index_cast %v40 : index to i64
%v45 = llvm.getelementptr %arg2[%v44] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v46 = llvm.load %v45 : !llvm.ptr -> f32
%v47 = arith.addf %v43, %v46 : f32
%v48 = arith.index_cast %v40 : index to i64
%v49 = llvm.getelementptr %arg0[%v48] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v47, %v49 : f32, !llvm.ptr
%v50 = arith.addi %v40, %v35 : index
cf.br ^b4(%v50 : index)
^b6(%v51: index):
func.return
}
func.func @main() -> i32 {
%v52 = llvm.mlir.undef : !llvm.struct<(i32, f32)>
%v53 = arith.constant 1 : i32
%v54 = llvm.insertvalue %v53, %v52[0] : !llvm.struct<(i32, f32)>
%v55 = arith.constant 1.0 : f64
%v56 = arith.truncf %v55 : f64 to f32
%v57 = llvm.insertvalue %v56, %v54[1] : !llvm.struct<(i32, f32)>
%v58 = llvm.mlir.undef : !llvm.struct<(i32, f32)>
%v59 = arith.constant 2 : i32
%v60 = llvm.insertvalue %v59, %v58[0] : !llvm.struct<(i32, f32)>
%v61 = arith.constant 2.0 : f64
%v62 = arith.truncf %v61 : f64 to f32
%v63 = llvm.insertvalue %v62, %v60[1] : !llvm.struct<(i32, f32)>
%v64 = llvm.mlir.undef : !llvm.struct<(i32, f32)>
%v65 = arith.constant 3 : i32
%v66 = llvm.insertvalue %v65, %v64[0] : !llvm.struct<(i32, f32)>
%v67 = arith.constant 3.0 : f64
%v68 = arith.truncf %v67 : f64 to f32
%v69 = llvm.insertvalue %v68, %v66[1] : !llvm.struct<(i32, f32)>
%v70 = llvm.mlir.constant(1 : i64) : i64
%v71 = llvm.alloca %v70 x !llvm.array<3 x !llvm.struct<(i32, f32)>> : (i64) -> !llvm.ptr
%v72 = arith.constant 24 : i64
func.call @flow_mem_note_stack(%v72) : (i64) -> ()
%v73 = llvm.mlir.zero : !llvm.array<3 x !llvm.struct<(i32, f32)>>
llvm.store %v73, %v71 : !llvm.array<3 x !llvm.struct<(i32, f32)>>, !llvm.ptr
%v74 = llvm.mlir.constant(0 : i64) : i64
%v75 = llvm.getelementptr %v71[0, %v74] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
llvm.store %v57, %v75 : !llvm.struct<(i32, f32)>, !llvm.ptr
%v76 = llvm.mlir.constant(1 : i64) : i64
%v77 = llvm.getelementptr %v71[0, %v76] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
llvm.store %v63, %v77 : !llvm.struct<(i32, f32)>, !llvm.ptr
%v78 = llvm.mlir.constant(2 : i64) : i64
%v79 = llvm.getelementptr %v71[0, %v78] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
llvm.store %v69, %v79 : !llvm.struct<(i32, f32)>, !llvm.ptr
%v80 = llvm.mlir.constant(1 : i64) : i64
%v81 = llvm.alloca %v80 x !llvm.ptr : (i64) -> !llvm.ptr
llvm.store %v71, %v81 : !llvm.ptr, !llvm.ptr
%v82 = arith.constant 20 : i32
%v83 = llvm.load %v81 : !llvm.ptr -> !llvm.ptr
%v84 = arith.constant 1 : i32
%v85 = arith.extsi %v84 : i32 to i64
%v86 = llvm.getelementptr %v83[0, %v85] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
%v87 = llvm.getelementptr %v86[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, f32)>
llvm.store %v82, %v87 : i32, !llvm.ptr
%v88 = llvm.load %v81 : !llvm.ptr -> !llvm.ptr
%v89 = arith.constant 2 : i32
%v90 = arith.extsi %v89 : i32 to i64
%v91 = llvm.getelementptr %v88[0, %v90] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
%v92 = llvm.load %v91 : !llvm.ptr -> !llvm.struct<(i32, f32)>
%v93 = llvm.mlir.constant(1 : i64) : i64
%v94 = llvm.alloca %v93 x !llvm.struct<(i32, f32)> : (i64) -> !llvm.ptr
llvm.store %v92, %v94 : !llvm.struct<(i32, f32)>, !llvm.ptr
%v95 = llvm.mlir.undef : !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v96 = llvm.mlir.zero : !llvm.array<4 x i32>
%v97 = arith.constant 1 : i32
%v98 = llvm.insertvalue %v97, %v96[0] : !llvm.array<4 x i32>
%v99 = arith.constant 2 : i32
%v100 = llvm.insertvalue %v99, %v98[1] : !llvm.array<4 x i32>
%v101 = arith.constant 3 : i32
%v102 = llvm.insertvalue %v101, %v100[2] : !llvm.array<4 x i32>
%v103 = arith.constant 4 : i32
%v104 = llvm.insertvalue %v103, %v102[3] : !llvm.array<4 x i32>
%v105 = llvm.insertvalue %v104, %v95[0] : !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v106 = arith.constant 4 : i32
%v107 = llvm.insertvalue %v106, %v105[1] : !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v108 = llvm.mlir.constant(1 : i64) : i64
%v109 = llvm.alloca %v108 x !llvm.struct<(!llvm.array<4 x i32>, i32)> : (i64) -> !llvm.ptr
llvm.store %v107, %v109 : !llvm.struct<(!llvm.array<4 x i32>, i32)>, !llvm.ptr
%v110 = llvm.load %v81 : !llvm.ptr -> !llvm.ptr
%v111 = func.call @sum(%v110) : (!llvm.ptr) -> i32
%v112 = llvm.load %v94 : !llvm.ptr -> !llvm.struct<(i32, f32)>
%v113 = llvm.getelementptr %v94[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, f32)>
%v114 = llvm.load %v113 : !llvm.ptr -> i32
%v115 = arith.addi %v111, %v114 : i32
%v116 = llvm.load %v109 : !llvm.ptr -> !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v117 = llvm.getelementptr %v109[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v118 = arith.constant 3 : i32
%v119 = arith.extsi %v118 : i32 to i64
%v120 = llvm.getelementptr %v117[0, %v119] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x i32>
%v121 = llvm.load %v120 : !llvm.ptr -> i32
%v122 = arith.addi %v115, %v121 : i32
%v123 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v124 = llvm.call @printf(%v123, %v122) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v125 = arith.constant 0 : i32
%v126 = memref.alloca() : memref<8xi32>
%v127 = arith.constant 0 : i32
%v128 = arith.constant 8 : i32
%v129 = arith.index_cast %v127 : i32 to index
%v130 = arith.index_cast %v128 : i32 to index
%v131 = arith.constant 1 : index
%v132 = arith.constant -1 : index
%v133 = arith.cmpi sle, %v129, %v130 : index
%v134 = arith.select %v133, %v131, %v132 : index
cf.br ^b7(%v129 : index)
^b7(%v135: index):
%v136 = arith.cmpi slt, %v135, %v130 : index
%v137 = arith.cmpi sgt, %v135, %v130 : index
%v138 = arith.select %v133, %v136, %v137 : i1
cf.cond_br %v138, ^b8(%v135 : index), ^b9(%v135 : index)
^b8(%v139: index):
%v140 = arith.constant 2 : i32
%v141 = arith.index_cast %v139 : index to i32
%v142 = arith.muli %v141, %v140 : i32
memref.store %v142, %v126[%v139] : memref<8xi32>
%v143 = arith.addi %v139, %v134 : index
cf.br ^b7(%v143 : index)
^b9(%v144: index):
%v145 = arith.constant 0 : i32
%v146 = llvm.mlir.constant(1 : i64) : i64
%v147 = llvm.alloca %v146 x i32 : (i64) -> !llvm.ptr
llvm.store %v145, %v147 : i32, !llvm.ptr
%v148 = arith.constant 0 : i32
%v149 = arith.constant 8 : i32
%v150 = arith.index_cast %v148 : i32 to index
%v151 = arith.index_cast %v149 : i32 to index
%v152 = arith.constant 1 : index
%v153 = arith.constant -1 : index
%v154 = arith.cmpi sle, %v150, %v151 : index
%v155 = arith.select %v154, %v152, %v153 : index
cf.br ^b10(%v150 : index)
^b10(%v156: index):
%v157 = arith.cmpi slt, %v156, %v151 : index
%v158 = arith.cmpi sgt, %v156, %v151 : index
%v159 = arith.select %v154, %v157, %v158 : i1
cf.cond_br %v159, ^b11(%v156 : index), ^b12(%v156 : index)
^b11(%v160: index):
%v161 = llvm.load %v147 : !llvm.ptr -> i32
%v162 = memref.load %v126[%v160] : memref<8xi32>
%v163 = arith.addi %v161, %v162 : i32
llvm.store %v163, %v147 : i32, !llvm.ptr
%v164 = arith.addi %v160, %v155 : index
cf.br ^b10(%v164 : index)
^b12(%v165: index):
%v166 = llvm.load %v147 : !llvm.ptr -> i32
%v167 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v168 = llvm.call @printf(%v167, %v166) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v169 = arith.constant 0 : i32
%v170 = arith.constant 16 : i32
%v171 = arith.extsi %v170 : i32 to i64
%v172 = func.call @flow_mem_malloc(%v171) : (i64) -> !llvm.ptr
%v173 = arith.constant 16 : i32
%v174 = arith.extsi %v173 : i32 to i64
%v175 = func.call @flow_mem_malloc(%v174) : (i64) -> !llvm.ptr
%v176 = arith.constant 16 : i32
%v177 = arith.extsi %v176 : i32 to i64
%v178 = func.call @flow_mem_malloc(%v177) : (i64) -> !llvm.ptr
%v179 = arith.constant 0 : i32
%v180 = arith.constant 4 : i32
%v181 = arith.index_cast %v179 : i32 to index
%v182 = arith.index_cast %v180 : i32 to index
%v183 = arith.constant 1 : index
%v184 = arith.constant -1 : index
%v185 = arith.cmpi sle, %v181, %v182 : index
%v186 = arith.select %v185, %v183, %v184 : index
cf.br ^b13(%v181 : index)
^b13(%v187: index):
%v188 = arith.cmpi slt, %v187, %v182 : index
%v189 = arith.cmpi sgt, %v187, %v182 : index
%v190 = arith.select %v185, %v188, %v189 : i1
cf.cond_br %v190, ^b14(%v187 : index), ^b15(%v187 : index)
^b14(%v191: index):
%v192 = arith.constant 1.5 : f64
%v193 = arith.truncf %v192 : f64 to f32
%v194 = arith.index_cast %v191 : index to i64
%v195 = llvm.getelementptr %v175[%v194] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v193, %v195 : f32, !llvm.ptr
%v196 = arith.constant 2.0 : f64
%v197 = arith.truncf %v196 : f64 to f32
%v198 = arith.index_cast %v191 : index to i64
%v199 = llvm.getelementptr %v178[%v198] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v197, %v199 : f32, !llvm.ptr
%v200 = arith.addi %v191, %v186 : index
cf.br ^b13(%v200 : index)
^b15(%v201: index):
%v202 = arith.constant 4 : i32
func.call @add4(%v172, %v175, %v178, %v202) : (!llvm.ptr, !llvm.ptr, !llvm.ptr, i32) -> ()
%v203 = arith.constant 3 : i32
%v204 = arith.extsi %v203 : i32 to i64
%v205 = llvm.getelementptr %v172[%v204] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v206 = llvm.load %v205 : !llvm.ptr -> f32
%v207 = arith.extf %v206 : f32 to f64
%v208 = llvm.mlir.addressof @str_13 : !llvm.ptr
%v209 = llvm.call @printf(%v208, %v207) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v210 = arith.constant 0 : i32
%v211 = arith.constant 0 : i32
func.return %v211 : i32
}
}
