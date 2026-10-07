module {
func.func private @strlen(!llvm.ptr) -> i64
func.func private @memcpy(!llvm.ptr, !llvm.ptr, i64) -> !llvm.ptr
func.func private @write(i32, !llvm.ptr, i64) -> i64
func.func private @abort() -> ()
func.func private @malloc(i64) -> !llvm.ptr
func.func private @memset(!llvm.ptr, i32, i64) -> !llvm.ptr
func.func private @sqrt(f64) -> f64
func.func private @log(f64) -> f64
func.func private @free(!llvm.ptr) -> ()
func.func private @exp(f64) -> f64
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
llvm.mlir.global internal constant @str_12("flow: \00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
llvm.mlir.global internal constant @str_13("\0A\00") {addr_space = 0 : i32} : !llvm.array<2 x i8>
llvm.mlir.global internal constant @str_14("division by zero\00") {addr_space = 0 : i32} : !llvm.array<17 x i8>
llvm.mlir.global internal constant @str_15("Tensor(\00") {addr_space = 0 : i32} : !llvm.array<8 x i8>
llvm.mlir.global internal constant @str_16("%d\00") {addr_space = 0 : i32} : !llvm.array<3 x i8>
llvm.mlir.global internal constant @str_17(", \00") {addr_space = 0 : i32} : !llvm.array<3 x i8>
llvm.mlir.global internal constant @str_18(")\0A\00") {addr_space = 0 : i32} : !llvm.array<3 x i8>
llvm.mlir.global internal constant @str_19("  [\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_20("%f\00") {addr_space = 0 : i32} : !llvm.array<3 x i8>
llvm.mlir.global internal constant @str_21(", ...\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
llvm.mlir.global internal constant @str_22("]\0A\00") {addr_space = 0 : i32} : !llvm.array<3 x i8>
llvm.mlir.global internal constant @str_23("MLIR Tensor Benchmark\0A\00") {addr_space = 0 : i32} : !llvm.array<23 x i8>
llvm.mlir.global internal constant @str_24("=====================\0A\00") {addr_space = 0 : i32} : !llvm.array<23 x i8>
llvm.mlir.global internal constant @str_25("matmul 64x64 sum checkpoint\0A\00") {addr_space = 0 : i32} : !llvm.array<29 x i8>
llvm.mlir.global internal constant @str_26("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_27("matmul 128x128 sum checkpoint\0A\00") {addr_space = 0 : i32} : !llvm.array<31 x i8>
llvm.mlir.global internal constant @str_28("done\0A\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
func.func private @__flow_fault(%arg0: !llvm.ptr) {
%fd = arith.constant 2 : i32
%pre = llvm.mlir.addressof @str_12 : !llvm.ptr
%n6 = arith.constant 6 : i64
%w0 = func.call @write(%fd, %pre, %n6) : (i32, !llvm.ptr, i64) -> i64
%n = func.call @strlen(%arg0) : (!llvm.ptr) -> i64
%w1 = func.call @write(%fd, %arg0, %n) : (i32, !llvm.ptr, i64) -> i64
%nl = llvm.mlir.addressof @str_13 : !llvm.ptr
%n1 = arith.constant 1 : i64
%w2 = func.call @write(%fd, %nl, %n1) : (i32, !llvm.ptr, i64) -> i64
func.call @abort() : () -> ()
func.return
}
// Struct: Tensor
// Fields:
//   data: !llvm.ptr
//   size: i32
//   dim0: i32
//   dim1: i32
//   dim2: i32
//   dim3: i32
func.func @tensor_zeros(%arg0: i32, %arg1: i32, %arg2: i32, %arg3: i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1 = arith.muli %arg0, %arg1 : i32
%v2 = arith.muli %v1, %arg2 : i32
%v3 = arith.muli %v2, %arg3 : i32
%v4 = arith.extsi %v3 : i32 to i64
%v5 = arith.constant 4 : i32
%v6 = arith.extsi %v5 : i32 to i64
%v7 = arith.muli %v4, %v6 : i64
%v8 = func.call @flow_mem_malloc(%v7) : (i64) -> !llvm.ptr
%v9 = arith.constant 0 : i32
%v10 = func.call @memset(%v8, %v9, %v7) : (!llvm.ptr, i32, i64) -> !llvm.ptr
%v11 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v12 = llvm.insertvalue %v8, %v11[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v13 = llvm.insertvalue %v3, %v12[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v14 = llvm.insertvalue %arg0, %v13[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v15 = llvm.insertvalue %arg1, %v14[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v16 = llvm.insertvalue %arg2, %v15[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v17 = llvm.insertvalue %arg3, %v16[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v18 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v19 = llvm.extractvalue %v17[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v20 = llvm.insertvalue %v19, %v18[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v21 = llvm.extractvalue %v17[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v22 = llvm.insertvalue %v21, %v20[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v23 = llvm.extractvalue %v17[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v24 = llvm.insertvalue %v23, %v22[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v25 = llvm.extractvalue %v17[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v26 = llvm.insertvalue %v25, %v24[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v27 = llvm.extractvalue %v17[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v28 = llvm.insertvalue %v27, %v26[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v29 = llvm.extractvalue %v17[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v30 = llvm.insertvalue %v29, %v28[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v31 = llvm.mlir.constant(1 : i64) : i64
%v32 = llvm.alloca %v31 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v30, %v32 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v33 = llvm.load %v32 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v33 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_ones(%arg0: i32, %arg1: i32, %arg2: i32, %arg3: i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v34 = func.call @tensor_zeros(%arg0, %arg1, %arg2, %arg3) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v35 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v36 = llvm.extractvalue %v34[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v37 = llvm.insertvalue %v36, %v35[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v38 = llvm.extractvalue %v34[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v39 = llvm.insertvalue %v38, %v37[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v40 = llvm.extractvalue %v34[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v41 = llvm.insertvalue %v40, %v39[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v42 = llvm.extractvalue %v34[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v43 = llvm.insertvalue %v42, %v41[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v44 = llvm.extractvalue %v34[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v45 = llvm.insertvalue %v44, %v43[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v46 = llvm.extractvalue %v34[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v47 = llvm.insertvalue %v46, %v45[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v48 = llvm.mlir.constant(1 : i64) : i64
%v49 = llvm.alloca %v48 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v47, %v49 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v50 = llvm.load %v49 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v51 = llvm.mlir.constant(1 : i64) : i64
%v52 = llvm.alloca %v51 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v50, %v52 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v53 = arith.constant 0 : i32
%v54 = llvm.load %v52 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v55 = llvm.getelementptr %v52[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v56 = llvm.load %v55 : !llvm.ptr -> i32
%v57 = arith.index_cast %v53 : i32 to index
%v58 = arith.index_cast %v56 : i32 to index
%v59 = arith.constant 1 : index
%v60 = arith.constant -1 : index
%v61 = arith.cmpi sle, %v57, %v58 : index
%v62 = arith.select %v61, %v59, %v60 : index
cf.br ^b1(%v57 : index)
^b1(%v63: index):
%v64 = arith.cmpi slt, %v63, %v58 : index
%v65 = arith.cmpi sgt, %v63, %v58 : index
%v66 = arith.select %v61, %v64, %v65 : i1
cf.cond_br %v66, ^b2(%v63 : index), ^b3(%v63 : index)
^b2(%v67: index):
%v68 = arith.constant 1.0 : f64
%v69 = llvm.load %v52 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v70 = llvm.getelementptr %v52[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v71 = llvm.load %v70 : !llvm.ptr -> !llvm.ptr
%v72 = arith.truncf %v68 : f64 to f32
%v73 = arith.index_cast %v67 : index to i64
%v74 = llvm.getelementptr %v71[%v73] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v72, %v74 : f32, !llvm.ptr
%v75 = arith.addi %v67, %v62 : index
cf.br ^b1(%v75 : index)
^b3(%v76: index):
%v77 = llvm.load %v52 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v78 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v79 = llvm.extractvalue %v77[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v80 = llvm.insertvalue %v79, %v78[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v81 = llvm.extractvalue %v77[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v82 = llvm.insertvalue %v81, %v80[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v83 = llvm.extractvalue %v77[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v84 = llvm.insertvalue %v83, %v82[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v85 = llvm.extractvalue %v77[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v86 = llvm.insertvalue %v85, %v84[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v87 = llvm.extractvalue %v77[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v88 = llvm.insertvalue %v87, %v86[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v89 = llvm.extractvalue %v77[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v90 = llvm.insertvalue %v89, %v88[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v91 = llvm.mlir.constant(1 : i64) : i64
%v92 = llvm.alloca %v91 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v90, %v92 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v93 = llvm.load %v92 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v93 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_fill(%arg0: i32, %arg1: i32, %arg2: i32, %arg3: i32, %arg4: f32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v94 = func.call @tensor_zeros(%arg0, %arg1, %arg2, %arg3) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v95 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v96 = llvm.extractvalue %v94[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v97 = llvm.insertvalue %v96, %v95[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v98 = llvm.extractvalue %v94[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v99 = llvm.insertvalue %v98, %v97[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v100 = llvm.extractvalue %v94[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v101 = llvm.insertvalue %v100, %v99[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v102 = llvm.extractvalue %v94[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v103 = llvm.insertvalue %v102, %v101[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v104 = llvm.extractvalue %v94[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v105 = llvm.insertvalue %v104, %v103[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v106 = llvm.extractvalue %v94[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v107 = llvm.insertvalue %v106, %v105[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v108 = llvm.mlir.constant(1 : i64) : i64
%v109 = llvm.alloca %v108 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v107, %v109 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v110 = llvm.load %v109 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v111 = llvm.mlir.constant(1 : i64) : i64
%v112 = llvm.alloca %v111 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v110, %v112 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v113 = arith.constant 0 : i32
%v114 = llvm.load %v112 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v115 = llvm.getelementptr %v112[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v116 = llvm.load %v115 : !llvm.ptr -> i32
%v117 = arith.index_cast %v113 : i32 to index
%v118 = arith.index_cast %v116 : i32 to index
%v119 = arith.constant 1 : index
%v120 = arith.constant -1 : index
%v121 = arith.cmpi sle, %v117, %v118 : index
%v122 = arith.select %v121, %v119, %v120 : index
cf.br ^b4(%v117 : index)
^b4(%v123: index):
%v124 = arith.cmpi slt, %v123, %v118 : index
%v125 = arith.cmpi sgt, %v123, %v118 : index
%v126 = arith.select %v121, %v124, %v125 : i1
cf.cond_br %v126, ^b5(%v123 : index), ^b6(%v123 : index)
^b5(%v127: index):
%v128 = llvm.load %v112 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v129 = llvm.getelementptr %v112[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v130 = llvm.load %v129 : !llvm.ptr -> !llvm.ptr
%v131 = arith.index_cast %v127 : index to i64
%v132 = llvm.getelementptr %v130[%v131] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %arg4, %v132 : f32, !llvm.ptr
%v133 = arith.addi %v127, %v122 : index
cf.br ^b4(%v133 : index)
^b6(%v134: index):
%v135 = llvm.load %v112 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v136 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v137 = llvm.extractvalue %v135[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v138 = llvm.insertvalue %v137, %v136[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v139 = llvm.extractvalue %v135[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v140 = llvm.insertvalue %v139, %v138[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v141 = llvm.extractvalue %v135[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v142 = llvm.insertvalue %v141, %v140[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v143 = llvm.extractvalue %v135[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v144 = llvm.insertvalue %v143, %v142[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v145 = llvm.extractvalue %v135[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v146 = llvm.insertvalue %v145, %v144[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v147 = llvm.extractvalue %v135[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v148 = llvm.insertvalue %v147, %v146[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v149 = llvm.mlir.constant(1 : i64) : i64
%v150 = llvm.alloca %v149 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v148, %v150 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v151 = llvm.load %v150 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v151 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_rand(%arg0: i32, %arg1: i32, %arg2: i32, %arg3: i32, %arg4: i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v152 = func.call @tensor_zeros(%arg0, %arg1, %arg2, %arg3) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v153 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v154 = llvm.extractvalue %v152[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v155 = llvm.insertvalue %v154, %v153[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v156 = llvm.extractvalue %v152[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v157 = llvm.insertvalue %v156, %v155[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v158 = llvm.extractvalue %v152[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v159 = llvm.insertvalue %v158, %v157[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v160 = llvm.extractvalue %v152[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v161 = llvm.insertvalue %v160, %v159[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v162 = llvm.extractvalue %v152[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v163 = llvm.insertvalue %v162, %v161[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v164 = llvm.extractvalue %v152[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v165 = llvm.insertvalue %v164, %v163[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v166 = llvm.mlir.constant(1 : i64) : i64
%v167 = llvm.alloca %v166 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v165, %v167 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v168 = llvm.load %v167 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v169 = llvm.mlir.constant(1 : i64) : i64
%v170 = llvm.alloca %v169 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v168, %v170 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v171 = llvm.mlir.constant(1 : i64) : i64
%v172 = llvm.alloca %v171 x i32 : (i64) -> !llvm.ptr
llvm.store %arg4, %v172 : i32, !llvm.ptr
%v173 = arith.constant 0 : i32
%v174 = llvm.load %v170 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v175 = llvm.getelementptr %v170[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v176 = llvm.load %v175 : !llvm.ptr -> i32
%v177 = arith.index_cast %v173 : i32 to index
%v178 = arith.index_cast %v176 : i32 to index
%v179 = arith.constant 1 : index
%v180 = arith.constant -1 : index
%v181 = arith.cmpi sle, %v177, %v178 : index
%v182 = arith.select %v181, %v179, %v180 : index
cf.br ^b7(%v177 : index)
^b7(%v183: index):
%v184 = arith.cmpi slt, %v183, %v178 : index
%v185 = arith.cmpi sgt, %v183, %v178 : index
%v186 = arith.select %v181, %v184, %v185 : i1
cf.cond_br %v186, ^b8(%v183 : index), ^b9(%v183 : index)
^b8(%v187: index):
%v188 = llvm.load %v172 : !llvm.ptr -> i32
%v189 = arith.constant 1103515245 : i32
%v190 = arith.muli %v188, %v189 : i32
%v191 = arith.constant 12345 : i32
%v192 = arith.addi %v190, %v191 : i32
%v193 = arith.constant 2147483647 : i32
%v194 = arith.constant 0 : i32
%v195 = arith.cmpi eq, %v193, %v194 : i32
scf.if %v195 {
%v196 = llvm.mlir.addressof @str_14 : !llvm.ptr
func.call @__flow_fault(%v196) : (!llvm.ptr) -> ()
}
%v197 = arith.remsi %v192, %v193 : i32
llvm.store %v197, %v172 : i32, !llvm.ptr
%v198 = llvm.load %v172 : !llvm.ptr -> i32
%v199 = arith.constant 0 : i32
%v200 = arith.cmpi slt, %v198, %v199 : i32
cf.cond_br %v200, ^b10, ^b11
^b10:
%v201 = arith.constant 0 : i32
%v202 = llvm.load %v172 : !llvm.ptr -> i32
%v203 = arith.subi %v201, %v202 : i32
llvm.store %v203, %v172 : i32, !llvm.ptr
cf.br ^b12
^b11:
cf.br ^b12
^b12:
%v204 = llvm.load %v172 : !llvm.ptr -> i32
%v205 = arith.constant 10000 : i32
%v206 = arith.constant 0 : i32
%v207 = arith.cmpi eq, %v205, %v206 : i32
scf.if %v207 {
%v208 = llvm.mlir.addressof @str_14 : !llvm.ptr
func.call @__flow_fault(%v208) : (!llvm.ptr) -> ()
}
%v209 = arith.remsi %v204, %v205 : i32
%v210 = arith.constant 10000.0 : f64
%v211 = arith.sitofp %v209 : i32 to f64
%v212 = arith.divf %v211, %v210 : f64
%v213 = llvm.load %v170 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v214 = llvm.getelementptr %v170[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v215 = llvm.load %v214 : !llvm.ptr -> !llvm.ptr
%v216 = arith.truncf %v212 : f64 to f32
%v217 = arith.index_cast %v187 : index to i64
%v218 = llvm.getelementptr %v215[%v217] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v216, %v218 : f32, !llvm.ptr
%v219 = arith.addi %v187, %v182 : index
cf.br ^b7(%v219 : index)
^b9(%v220: index):
%v221 = llvm.load %v170 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v222 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v223 = llvm.extractvalue %v221[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v224 = llvm.insertvalue %v223, %v222[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v225 = llvm.extractvalue %v221[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v226 = llvm.insertvalue %v225, %v224[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v227 = llvm.extractvalue %v221[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v228 = llvm.insertvalue %v227, %v226[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v229 = llvm.extractvalue %v221[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v230 = llvm.insertvalue %v229, %v228[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v231 = llvm.extractvalue %v221[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v232 = llvm.insertvalue %v231, %v230[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v233 = llvm.extractvalue %v221[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v234 = llvm.insertvalue %v233, %v232[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v235 = llvm.mlir.constant(1 : i64) : i64
%v236 = llvm.alloca %v235 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v234, %v236 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v237 = llvm.load %v236 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v237 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_randn(%arg0: i32, %arg1: i32, %arg2: i32, %arg3: i32, %arg4: i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v238 = func.call @tensor_zeros(%arg0, %arg1, %arg2, %arg3) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v239 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v240 = llvm.extractvalue %v238[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v241 = llvm.insertvalue %v240, %v239[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v242 = llvm.extractvalue %v238[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v243 = llvm.insertvalue %v242, %v241[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v244 = llvm.extractvalue %v238[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v245 = llvm.insertvalue %v244, %v243[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v246 = llvm.extractvalue %v238[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v247 = llvm.insertvalue %v246, %v245[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v248 = llvm.extractvalue %v238[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v249 = llvm.insertvalue %v248, %v247[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v250 = llvm.extractvalue %v238[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v251 = llvm.insertvalue %v250, %v249[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v252 = llvm.mlir.constant(1 : i64) : i64
%v253 = llvm.alloca %v252 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v251, %v253 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v254 = llvm.load %v253 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v255 = llvm.mlir.constant(1 : i64) : i64
%v256 = llvm.alloca %v255 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v254, %v256 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v257 = llvm.mlir.constant(1 : i64) : i64
%v258 = llvm.alloca %v257 x i32 : (i64) -> !llvm.ptr
llvm.store %arg4, %v258 : i32, !llvm.ptr
%v259 = arith.constant 0 : i32
%v260 = llvm.load %v256 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v261 = llvm.getelementptr %v256[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v262 = llvm.load %v261 : !llvm.ptr -> i32
%v263 = arith.index_cast %v259 : i32 to index
%v264 = arith.index_cast %v262 : i32 to index
%v265 = arith.constant 1 : index
%v266 = arith.constant -1 : index
%v267 = arith.cmpi sle, %v263, %v264 : index
%v268 = arith.select %v267, %v265, %v266 : index
cf.br ^b13(%v263 : index)
^b13(%v269: index):
%v270 = arith.cmpi slt, %v269, %v264 : index
%v271 = arith.cmpi sgt, %v269, %v264 : index
%v272 = arith.select %v267, %v270, %v271 : i1
cf.cond_br %v272, ^b14(%v269 : index), ^b15(%v269 : index)
^b14(%v273: index):
%v274 = llvm.load %v258 : !llvm.ptr -> i32
%v275 = arith.constant 1103515245 : i32
%v276 = arith.muli %v274, %v275 : i32
%v277 = arith.constant 12345 : i32
%v278 = arith.addi %v276, %v277 : i32
%v279 = arith.constant 2147483647 : i32
%v280 = arith.constant 0 : i32
%v281 = arith.cmpi eq, %v279, %v280 : i32
scf.if %v281 {
%v282 = llvm.mlir.addressof @str_14 : !llvm.ptr
func.call @__flow_fault(%v282) : (!llvm.ptr) -> ()
}
%v283 = arith.remsi %v278, %v279 : i32
llvm.store %v283, %v258 : i32, !llvm.ptr
%v284 = llvm.load %v258 : !llvm.ptr -> i32
%v285 = arith.constant 0 : i32
%v286 = arith.cmpi slt, %v284, %v285 : i32
cf.cond_br %v286, ^b16, ^b17
^b16:
%v287 = arith.constant 0 : i32
%v288 = llvm.load %v258 : !llvm.ptr -> i32
%v289 = arith.subi %v287, %v288 : i32
llvm.store %v289, %v258 : i32, !llvm.ptr
cf.br ^b18
^b17:
cf.br ^b18
^b18:
%v290 = llvm.load %v258 : !llvm.ptr -> i32
%v291 = arith.constant 10000 : i32
%v292 = arith.constant 0 : i32
%v293 = arith.cmpi eq, %v291, %v292 : i32
scf.if %v293 {
%v294 = llvm.mlir.addressof @str_14 : !llvm.ptr
func.call @__flow_fault(%v294) : (!llvm.ptr) -> ()
}
%v295 = arith.remsi %v290, %v291 : i32
%v296 = arith.constant 1 : i32
%v297 = arith.addi %v295, %v296 : i32
%v298 = arith.constant 10001.0 : f64
%v299 = arith.sitofp %v297 : i32 to f64
%v300 = arith.divf %v299, %v298 : f64
%v301 = llvm.load %v258 : !llvm.ptr -> i32
%v302 = arith.constant 1103515245 : i32
%v303 = arith.muli %v301, %v302 : i32
%v304 = arith.constant 12345 : i32
%v305 = arith.addi %v303, %v304 : i32
%v306 = arith.constant 2147483647 : i32
%v307 = arith.constant 0 : i32
%v308 = arith.cmpi eq, %v306, %v307 : i32
scf.if %v308 {
%v309 = llvm.mlir.addressof @str_14 : !llvm.ptr
func.call @__flow_fault(%v309) : (!llvm.ptr) -> ()
}
%v310 = arith.remsi %v305, %v306 : i32
llvm.store %v310, %v258 : i32, !llvm.ptr
%v311 = llvm.load %v258 : !llvm.ptr -> i32
%v312 = arith.constant 0 : i32
%v313 = arith.cmpi slt, %v311, %v312 : i32
cf.cond_br %v313, ^b19, ^b20
^b19:
%v314 = arith.constant 0 : i32
%v315 = llvm.load %v258 : !llvm.ptr -> i32
%v316 = arith.subi %v314, %v315 : i32
llvm.store %v316, %v258 : i32, !llvm.ptr
cf.br ^b21
^b20:
cf.br ^b21
^b21:
%v317 = llvm.load %v258 : !llvm.ptr -> i32
%v318 = arith.constant 10000 : i32
%v319 = arith.constant 0 : i32
%v320 = arith.cmpi eq, %v318, %v319 : i32
scf.if %v320 {
%v321 = llvm.mlir.addressof @str_14 : !llvm.ptr
func.call @__flow_fault(%v321) : (!llvm.ptr) -> ()
}
%v322 = arith.remsi %v317, %v318 : i32
%v323 = arith.constant 10000.0 : f64
%v324 = arith.sitofp %v322 : i32 to f64
%v325 = arith.divf %v324, %v323 : f64
%v326 = arith.constant 0.0 : f64
%v327 = arith.constant 2.0 : f64
%v328 = func.call @log(%v300) : (f64) -> f64
%v329 = arith.negf %v327 : f64
%v330 = llvm.intr.fmuladd(%v329, %v328, %v326) : (f64, f64, f64) -> f64
%v331 = func.call @sqrt(%v330) : (f64) -> f64
%v332 = arith.constant 0.5 : f64
%v333 = arith.mulf %v331, %v332 : f64
%v334 = llvm.load %v256 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v335 = llvm.getelementptr %v256[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v336 = llvm.load %v335 : !llvm.ptr -> !llvm.ptr
%v337 = arith.truncf %v333 : f64 to f32
%v338 = arith.index_cast %v273 : index to i64
%v339 = llvm.getelementptr %v336[%v338] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v337, %v339 : f32, !llvm.ptr
%v340 = arith.addi %v273, %v268 : index
cf.br ^b13(%v340 : index)
^b15(%v341: index):
%v342 = llvm.load %v256 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v343 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v344 = llvm.extractvalue %v342[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v345 = llvm.insertvalue %v344, %v343[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v346 = llvm.extractvalue %v342[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v347 = llvm.insertvalue %v346, %v345[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v348 = llvm.extractvalue %v342[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v349 = llvm.insertvalue %v348, %v347[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v350 = llvm.extractvalue %v342[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v351 = llvm.insertvalue %v350, %v349[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v352 = llvm.extractvalue %v342[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v353 = llvm.insertvalue %v352, %v351[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v354 = llvm.extractvalue %v342[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v355 = llvm.insertvalue %v354, %v353[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v356 = llvm.mlir.constant(1 : i64) : i64
%v357 = llvm.alloca %v356 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v355, %v357 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v358 = llvm.load %v357 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v358 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_free(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> () {
%v359 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v360 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v361 = llvm.insertvalue %v360, %v359[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v362 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v363 = llvm.insertvalue %v362, %v361[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v364 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v365 = llvm.insertvalue %v364, %v363[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v366 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v367 = llvm.insertvalue %v366, %v365[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v368 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v369 = llvm.insertvalue %v368, %v367[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v370 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v371 = llvm.insertvalue %v370, %v369[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v372 = llvm.mlir.constant(1 : i64) : i64
%v373 = llvm.alloca %v372 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v371, %v373 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v374 = llvm.load %v373 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v375 = llvm.getelementptr %v373[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v376 = llvm.load %v375 : !llvm.ptr -> !llvm.ptr
func.call @flow_mem_free(%v376) : (!llvm.ptr) -> ()
func.return
}
func.func @tensor_idx(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: i32, %arg2: i32, %arg3: i32, %arg4: i32) -> i32 {
%v377 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v378 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v379 = llvm.insertvalue %v378, %v377[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v380 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v381 = llvm.insertvalue %v380, %v379[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v382 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v383 = llvm.insertvalue %v382, %v381[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v384 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v385 = llvm.insertvalue %v384, %v383[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v386 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v387 = llvm.insertvalue %v386, %v385[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v388 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v389 = llvm.insertvalue %v388, %v387[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v390 = llvm.mlir.constant(1 : i64) : i64
%v391 = llvm.alloca %v390 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v389, %v391 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v392 = llvm.load %v391 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v393 = llvm.getelementptr %v391[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v394 = llvm.load %v393 : !llvm.ptr -> i32
%v395 = arith.muli %arg1, %v394 : i32
%v396 = arith.addi %v395, %arg2 : i32
%v397 = llvm.load %v391 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v398 = llvm.getelementptr %v391[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v399 = llvm.load %v398 : !llvm.ptr -> i32
%v400 = arith.muli %v396, %v399 : i32
%v401 = arith.addi %v400, %arg3 : i32
%v402 = llvm.load %v391 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v403 = llvm.getelementptr %v391[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v404 = llvm.load %v403 : !llvm.ptr -> i32
%v405 = arith.muli %v401, %v404 : i32
%v406 = arith.addi %v405, %arg4 : i32
func.return %v406 : i32
}
func.func @tensor_get(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: i32, %arg2: i32, %arg3: i32, %arg4: i32) -> f32 {
%v407 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v408 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v409 = llvm.insertvalue %v408, %v407[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v410 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v411 = llvm.insertvalue %v410, %v409[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v412 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v413 = llvm.insertvalue %v412, %v411[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v414 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v415 = llvm.insertvalue %v414, %v413[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v416 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v417 = llvm.insertvalue %v416, %v415[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v418 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v419 = llvm.insertvalue %v418, %v417[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v420 = llvm.mlir.constant(1 : i64) : i64
%v421 = llvm.alloca %v420 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v419, %v421 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v422 = llvm.load %v421 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v423 = llvm.getelementptr %v421[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v424 = llvm.load %v423 : !llvm.ptr -> !llvm.ptr
%v425 = llvm.load %v421 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v426 = func.call @tensor_idx(%v425, %arg1, %arg2, %arg3, %arg4) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, i32, i32, i32, i32) -> i32
%v427 = arith.extsi %v426 : i32 to i64
%v428 = llvm.getelementptr %v424[%v427] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v429 = llvm.load %v428 : !llvm.ptr -> f32
func.return %v429 : f32
}
func.func @tensor_set(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: i32, %arg2: i32, %arg3: i32, %arg4: i32, %arg5: f32) -> () {
%v430 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v431 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v432 = llvm.insertvalue %v431, %v430[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v433 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v434 = llvm.insertvalue %v433, %v432[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v435 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v436 = llvm.insertvalue %v435, %v434[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v437 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v438 = llvm.insertvalue %v437, %v436[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v439 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v440 = llvm.insertvalue %v439, %v438[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v441 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v442 = llvm.insertvalue %v441, %v440[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v443 = llvm.mlir.constant(1 : i64) : i64
%v444 = llvm.alloca %v443 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v442, %v444 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v445 = llvm.load %v444 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v446 = llvm.getelementptr %v444[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v447 = llvm.load %v446 : !llvm.ptr -> !llvm.ptr
%v448 = llvm.load %v444 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v449 = func.call @tensor_idx(%v448, %arg1, %arg2, %arg3, %arg4) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, i32, i32, i32, i32) -> i32
%v450 = arith.extsi %v449 : i32 to i64
%v451 = llvm.getelementptr %v447[%v450] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %arg5, %v451 : f32, !llvm.ptr
func.return
}
func.func @tensor_get2(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: i32, %arg2: i32) -> f32 {
%v452 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v453 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v454 = llvm.insertvalue %v453, %v452[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v455 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v456 = llvm.insertvalue %v455, %v454[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v457 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v458 = llvm.insertvalue %v457, %v456[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v459 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v460 = llvm.insertvalue %v459, %v458[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v461 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v462 = llvm.insertvalue %v461, %v460[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v463 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v464 = llvm.insertvalue %v463, %v462[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v465 = llvm.mlir.constant(1 : i64) : i64
%v466 = llvm.alloca %v465 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v464, %v466 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v467 = llvm.load %v466 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v468 = llvm.getelementptr %v466[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v469 = llvm.load %v468 : !llvm.ptr -> !llvm.ptr
%v470 = llvm.load %v466 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v471 = llvm.getelementptr %v466[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v472 = llvm.load %v471 : !llvm.ptr -> i32
%v473 = arith.muli %arg1, %v472 : i32
%v474 = arith.addi %v473, %arg2 : i32
%v475 = arith.extsi %v474 : i32 to i64
%v476 = llvm.getelementptr %v469[%v475] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v477 = llvm.load %v476 : !llvm.ptr -> f32
func.return %v477 : f32
}
func.func @tensor_set2(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: i32, %arg2: i32, %arg3: f32) -> () {
%v478 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v479 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v480 = llvm.insertvalue %v479, %v478[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v481 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v482 = llvm.insertvalue %v481, %v480[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v483 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v484 = llvm.insertvalue %v483, %v482[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v485 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v486 = llvm.insertvalue %v485, %v484[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v487 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v488 = llvm.insertvalue %v487, %v486[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v489 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v490 = llvm.insertvalue %v489, %v488[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v491 = llvm.mlir.constant(1 : i64) : i64
%v492 = llvm.alloca %v491 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v490, %v492 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v493 = llvm.load %v492 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v494 = llvm.getelementptr %v492[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v495 = llvm.load %v494 : !llvm.ptr -> !llvm.ptr
%v496 = llvm.load %v492 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v497 = llvm.getelementptr %v492[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v498 = llvm.load %v497 : !llvm.ptr -> i32
%v499 = arith.muli %arg1, %v498 : i32
%v500 = arith.addi %v499, %arg2 : i32
%v501 = arith.extsi %v500 : i32 to i64
%v502 = llvm.getelementptr %v495[%v501] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %arg3, %v502 : f32, !llvm.ptr
func.return
}
func.func @tensor_get1(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: i32) -> f32 {
%v503 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v504 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v505 = llvm.insertvalue %v504, %v503[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v506 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v507 = llvm.insertvalue %v506, %v505[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v508 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v509 = llvm.insertvalue %v508, %v507[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v510 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v511 = llvm.insertvalue %v510, %v509[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v512 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v513 = llvm.insertvalue %v512, %v511[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v514 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v515 = llvm.insertvalue %v514, %v513[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v516 = llvm.mlir.constant(1 : i64) : i64
%v517 = llvm.alloca %v516 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v515, %v517 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v518 = llvm.load %v517 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v519 = llvm.getelementptr %v517[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v520 = llvm.load %v519 : !llvm.ptr -> !llvm.ptr
%v521 = arith.extsi %arg1 : i32 to i64
%v522 = llvm.getelementptr %v520[%v521] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v523 = llvm.load %v522 : !llvm.ptr -> f32
func.return %v523 : f32
}
func.func @tensor_set1(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: i32, %arg2: f32) -> () {
%v524 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v525 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v526 = llvm.insertvalue %v525, %v524[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v527 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v528 = llvm.insertvalue %v527, %v526[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v529 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v530 = llvm.insertvalue %v529, %v528[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v531 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v532 = llvm.insertvalue %v531, %v530[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v533 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v534 = llvm.insertvalue %v533, %v532[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v535 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v536 = llvm.insertvalue %v535, %v534[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v537 = llvm.mlir.constant(1 : i64) : i64
%v538 = llvm.alloca %v537 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v536, %v538 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v539 = llvm.load %v538 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v540 = llvm.getelementptr %v538[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v541 = llvm.load %v540 : !llvm.ptr -> !llvm.ptr
%v542 = arith.extsi %arg1 : i32 to i64
%v543 = llvm.getelementptr %v541[%v542] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %arg2, %v543 : f32, !llvm.ptr
func.return
}
func.func @tensor_add(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v544 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v545 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v546 = llvm.insertvalue %v545, %v544[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v547 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v548 = llvm.insertvalue %v547, %v546[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v549 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v550 = llvm.insertvalue %v549, %v548[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v551 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v552 = llvm.insertvalue %v551, %v550[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v553 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v554 = llvm.insertvalue %v553, %v552[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v555 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v556 = llvm.insertvalue %v555, %v554[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v557 = llvm.mlir.constant(1 : i64) : i64
%v558 = llvm.alloca %v557 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v556, %v558 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v559 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v560 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v561 = llvm.insertvalue %v560, %v559[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v562 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v563 = llvm.insertvalue %v562, %v561[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v564 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v565 = llvm.insertvalue %v564, %v563[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v566 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v567 = llvm.insertvalue %v566, %v565[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v568 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v569 = llvm.insertvalue %v568, %v567[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v570 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v571 = llvm.insertvalue %v570, %v569[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v572 = llvm.mlir.constant(1 : i64) : i64
%v573 = llvm.alloca %v572 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v571, %v573 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v574 = llvm.load %v558 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v575 = llvm.getelementptr %v558[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v576 = llvm.load %v575 : !llvm.ptr -> i32
%v577 = llvm.load %v558 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v578 = llvm.getelementptr %v558[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v579 = llvm.load %v578 : !llvm.ptr -> i32
%v580 = llvm.load %v558 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v581 = llvm.getelementptr %v558[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v582 = llvm.load %v581 : !llvm.ptr -> i32
%v583 = llvm.load %v558 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v584 = llvm.getelementptr %v558[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v585 = llvm.load %v584 : !llvm.ptr -> i32
%v586 = func.call @tensor_zeros(%v576, %v579, %v582, %v585) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v587 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v588 = llvm.extractvalue %v586[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v589 = llvm.insertvalue %v588, %v587[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v590 = llvm.extractvalue %v586[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v591 = llvm.insertvalue %v590, %v589[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v592 = llvm.extractvalue %v586[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v593 = llvm.insertvalue %v592, %v591[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v594 = llvm.extractvalue %v586[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v595 = llvm.insertvalue %v594, %v593[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v596 = llvm.extractvalue %v586[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v597 = llvm.insertvalue %v596, %v595[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v598 = llvm.extractvalue %v586[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v599 = llvm.insertvalue %v598, %v597[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v600 = llvm.mlir.constant(1 : i64) : i64
%v601 = llvm.alloca %v600 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v599, %v601 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v602 = llvm.load %v601 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v603 = llvm.mlir.constant(1 : i64) : i64
%v604 = llvm.alloca %v603 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v602, %v604 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v605 = arith.constant 0 : i32
%v606 = llvm.load %v558 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v607 = llvm.getelementptr %v558[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v608 = llvm.load %v607 : !llvm.ptr -> i32
%v609 = arith.index_cast %v605 : i32 to index
%v610 = arith.index_cast %v608 : i32 to index
%v611 = arith.constant 1 : index
%v612 = arith.constant -1 : index
%v613 = arith.cmpi sle, %v609, %v610 : index
%v614 = arith.select %v613, %v611, %v612 : index
cf.br ^b22(%v609 : index)
^b22(%v615: index):
%v616 = arith.cmpi slt, %v615, %v610 : index
%v617 = arith.cmpi sgt, %v615, %v610 : index
%v618 = arith.select %v613, %v616, %v617 : i1
cf.cond_br %v618, ^b23(%v615 : index), ^b24(%v615 : index)
^b23(%v619: index):
%v620 = llvm.load %v558 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v621 = llvm.getelementptr %v558[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v622 = llvm.load %v621 : !llvm.ptr -> !llvm.ptr
%v623 = arith.index_cast %v619 : index to i64
%v624 = llvm.getelementptr %v622[%v623] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v625 = llvm.load %v624 : !llvm.ptr -> f32
%v626 = llvm.load %v573 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v627 = llvm.getelementptr %v573[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v628 = llvm.load %v627 : !llvm.ptr -> !llvm.ptr
%v629 = arith.index_cast %v619 : index to i64
%v630 = llvm.getelementptr %v628[%v629] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v631 = llvm.load %v630 : !llvm.ptr -> f32
%v632 = arith.addf %v625, %v631 : f32
%v633 = llvm.load %v604 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v634 = llvm.getelementptr %v604[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v635 = llvm.load %v634 : !llvm.ptr -> !llvm.ptr
%v636 = arith.index_cast %v619 : index to i64
%v637 = llvm.getelementptr %v635[%v636] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v632, %v637 : f32, !llvm.ptr
%v638 = arith.addi %v619, %v614 : index
cf.br ^b22(%v638 : index)
^b24(%v639: index):
%v640 = llvm.load %v604 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v641 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v642 = llvm.extractvalue %v640[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v643 = llvm.insertvalue %v642, %v641[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v644 = llvm.extractvalue %v640[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v645 = llvm.insertvalue %v644, %v643[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v646 = llvm.extractvalue %v640[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v647 = llvm.insertvalue %v646, %v645[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v648 = llvm.extractvalue %v640[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v649 = llvm.insertvalue %v648, %v647[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v650 = llvm.extractvalue %v640[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v651 = llvm.insertvalue %v650, %v649[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v652 = llvm.extractvalue %v640[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v653 = llvm.insertvalue %v652, %v651[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v654 = llvm.mlir.constant(1 : i64) : i64
%v655 = llvm.alloca %v654 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v653, %v655 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v656 = llvm.load %v655 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v656 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_sub(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v657 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v658 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v659 = llvm.insertvalue %v658, %v657[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v660 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v661 = llvm.insertvalue %v660, %v659[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v662 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v663 = llvm.insertvalue %v662, %v661[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v664 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v665 = llvm.insertvalue %v664, %v663[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v666 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v667 = llvm.insertvalue %v666, %v665[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v668 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v669 = llvm.insertvalue %v668, %v667[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v670 = llvm.mlir.constant(1 : i64) : i64
%v671 = llvm.alloca %v670 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v669, %v671 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v672 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v673 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v674 = llvm.insertvalue %v673, %v672[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v675 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v676 = llvm.insertvalue %v675, %v674[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v677 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v678 = llvm.insertvalue %v677, %v676[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v679 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v680 = llvm.insertvalue %v679, %v678[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v681 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v682 = llvm.insertvalue %v681, %v680[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v683 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v684 = llvm.insertvalue %v683, %v682[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v685 = llvm.mlir.constant(1 : i64) : i64
%v686 = llvm.alloca %v685 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v684, %v686 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v687 = llvm.load %v671 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v688 = llvm.getelementptr %v671[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v689 = llvm.load %v688 : !llvm.ptr -> i32
%v690 = llvm.load %v671 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v691 = llvm.getelementptr %v671[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v692 = llvm.load %v691 : !llvm.ptr -> i32
%v693 = llvm.load %v671 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v694 = llvm.getelementptr %v671[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v695 = llvm.load %v694 : !llvm.ptr -> i32
%v696 = llvm.load %v671 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v697 = llvm.getelementptr %v671[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v698 = llvm.load %v697 : !llvm.ptr -> i32
%v699 = func.call @tensor_zeros(%v689, %v692, %v695, %v698) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v700 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v701 = llvm.extractvalue %v699[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v702 = llvm.insertvalue %v701, %v700[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v703 = llvm.extractvalue %v699[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v704 = llvm.insertvalue %v703, %v702[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v705 = llvm.extractvalue %v699[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v706 = llvm.insertvalue %v705, %v704[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v707 = llvm.extractvalue %v699[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v708 = llvm.insertvalue %v707, %v706[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v709 = llvm.extractvalue %v699[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v710 = llvm.insertvalue %v709, %v708[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v711 = llvm.extractvalue %v699[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v712 = llvm.insertvalue %v711, %v710[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v713 = llvm.mlir.constant(1 : i64) : i64
%v714 = llvm.alloca %v713 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v712, %v714 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v715 = llvm.load %v714 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v716 = llvm.mlir.constant(1 : i64) : i64
%v717 = llvm.alloca %v716 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v715, %v717 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v718 = arith.constant 0 : i32
%v719 = llvm.load %v671 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v720 = llvm.getelementptr %v671[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v721 = llvm.load %v720 : !llvm.ptr -> i32
%v722 = arith.index_cast %v718 : i32 to index
%v723 = arith.index_cast %v721 : i32 to index
%v724 = arith.constant 1 : index
%v725 = arith.constant -1 : index
%v726 = arith.cmpi sle, %v722, %v723 : index
%v727 = arith.select %v726, %v724, %v725 : index
cf.br ^b25(%v722 : index)
^b25(%v728: index):
%v729 = arith.cmpi slt, %v728, %v723 : index
%v730 = arith.cmpi sgt, %v728, %v723 : index
%v731 = arith.select %v726, %v729, %v730 : i1
cf.cond_br %v731, ^b26(%v728 : index), ^b27(%v728 : index)
^b26(%v732: index):
%v733 = llvm.load %v671 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v734 = llvm.getelementptr %v671[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v735 = llvm.load %v734 : !llvm.ptr -> !llvm.ptr
%v736 = arith.index_cast %v732 : index to i64
%v737 = llvm.getelementptr %v735[%v736] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v738 = llvm.load %v737 : !llvm.ptr -> f32
%v739 = llvm.load %v686 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v740 = llvm.getelementptr %v686[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v741 = llvm.load %v740 : !llvm.ptr -> !llvm.ptr
%v742 = arith.index_cast %v732 : index to i64
%v743 = llvm.getelementptr %v741[%v742] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v744 = llvm.load %v743 : !llvm.ptr -> f32
%v745 = arith.subf %v738, %v744 : f32
%v746 = llvm.load %v717 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v747 = llvm.getelementptr %v717[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v748 = llvm.load %v747 : !llvm.ptr -> !llvm.ptr
%v749 = arith.index_cast %v732 : index to i64
%v750 = llvm.getelementptr %v748[%v749] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v745, %v750 : f32, !llvm.ptr
%v751 = arith.addi %v732, %v727 : index
cf.br ^b25(%v751 : index)
^b27(%v752: index):
%v753 = llvm.load %v717 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v754 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v755 = llvm.extractvalue %v753[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v756 = llvm.insertvalue %v755, %v754[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v757 = llvm.extractvalue %v753[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v758 = llvm.insertvalue %v757, %v756[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v759 = llvm.extractvalue %v753[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v760 = llvm.insertvalue %v759, %v758[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v761 = llvm.extractvalue %v753[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v762 = llvm.insertvalue %v761, %v760[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v763 = llvm.extractvalue %v753[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v764 = llvm.insertvalue %v763, %v762[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v765 = llvm.extractvalue %v753[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v766 = llvm.insertvalue %v765, %v764[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v767 = llvm.mlir.constant(1 : i64) : i64
%v768 = llvm.alloca %v767 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v766, %v768 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v769 = llvm.load %v768 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v769 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_mul(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v770 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v771 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v772 = llvm.insertvalue %v771, %v770[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v773 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v774 = llvm.insertvalue %v773, %v772[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v775 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v776 = llvm.insertvalue %v775, %v774[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v777 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v778 = llvm.insertvalue %v777, %v776[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v779 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v780 = llvm.insertvalue %v779, %v778[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v781 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v782 = llvm.insertvalue %v781, %v780[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v783 = llvm.mlir.constant(1 : i64) : i64
%v784 = llvm.alloca %v783 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v782, %v784 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v785 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v786 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v787 = llvm.insertvalue %v786, %v785[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v788 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v789 = llvm.insertvalue %v788, %v787[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v790 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v791 = llvm.insertvalue %v790, %v789[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v792 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v793 = llvm.insertvalue %v792, %v791[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v794 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v795 = llvm.insertvalue %v794, %v793[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v796 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v797 = llvm.insertvalue %v796, %v795[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v798 = llvm.mlir.constant(1 : i64) : i64
%v799 = llvm.alloca %v798 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v797, %v799 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v800 = llvm.load %v784 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v801 = llvm.getelementptr %v784[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v802 = llvm.load %v801 : !llvm.ptr -> i32
%v803 = llvm.load %v784 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v804 = llvm.getelementptr %v784[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v805 = llvm.load %v804 : !llvm.ptr -> i32
%v806 = llvm.load %v784 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v807 = llvm.getelementptr %v784[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v808 = llvm.load %v807 : !llvm.ptr -> i32
%v809 = llvm.load %v784 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v810 = llvm.getelementptr %v784[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v811 = llvm.load %v810 : !llvm.ptr -> i32
%v812 = func.call @tensor_zeros(%v802, %v805, %v808, %v811) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v813 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v814 = llvm.extractvalue %v812[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v815 = llvm.insertvalue %v814, %v813[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v816 = llvm.extractvalue %v812[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v817 = llvm.insertvalue %v816, %v815[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v818 = llvm.extractvalue %v812[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v819 = llvm.insertvalue %v818, %v817[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v820 = llvm.extractvalue %v812[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v821 = llvm.insertvalue %v820, %v819[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v822 = llvm.extractvalue %v812[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v823 = llvm.insertvalue %v822, %v821[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v824 = llvm.extractvalue %v812[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v825 = llvm.insertvalue %v824, %v823[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v826 = llvm.mlir.constant(1 : i64) : i64
%v827 = llvm.alloca %v826 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v825, %v827 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v828 = llvm.load %v827 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v829 = llvm.mlir.constant(1 : i64) : i64
%v830 = llvm.alloca %v829 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v828, %v830 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v831 = arith.constant 0 : i32
%v832 = llvm.load %v784 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v833 = llvm.getelementptr %v784[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v834 = llvm.load %v833 : !llvm.ptr -> i32
%v835 = arith.index_cast %v831 : i32 to index
%v836 = arith.index_cast %v834 : i32 to index
%v837 = arith.constant 1 : index
%v838 = arith.constant -1 : index
%v839 = arith.cmpi sle, %v835, %v836 : index
%v840 = arith.select %v839, %v837, %v838 : index
cf.br ^b28(%v835 : index)
^b28(%v841: index):
%v842 = arith.cmpi slt, %v841, %v836 : index
%v843 = arith.cmpi sgt, %v841, %v836 : index
%v844 = arith.select %v839, %v842, %v843 : i1
cf.cond_br %v844, ^b29(%v841 : index), ^b30(%v841 : index)
^b29(%v845: index):
%v846 = llvm.load %v784 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v847 = llvm.getelementptr %v784[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v848 = llvm.load %v847 : !llvm.ptr -> !llvm.ptr
%v849 = arith.index_cast %v845 : index to i64
%v850 = llvm.getelementptr %v848[%v849] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v851 = llvm.load %v850 : !llvm.ptr -> f32
%v852 = llvm.load %v799 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v853 = llvm.getelementptr %v799[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v854 = llvm.load %v853 : !llvm.ptr -> !llvm.ptr
%v855 = arith.index_cast %v845 : index to i64
%v856 = llvm.getelementptr %v854[%v855] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v857 = llvm.load %v856 : !llvm.ptr -> f32
%v858 = arith.mulf %v851, %v857 : f32
%v859 = llvm.load %v830 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v860 = llvm.getelementptr %v830[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v861 = llvm.load %v860 : !llvm.ptr -> !llvm.ptr
%v862 = arith.index_cast %v845 : index to i64
%v863 = llvm.getelementptr %v861[%v862] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v858, %v863 : f32, !llvm.ptr
%v864 = arith.addi %v845, %v840 : index
cf.br ^b28(%v864 : index)
^b30(%v865: index):
%v866 = llvm.load %v830 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v867 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v868 = llvm.extractvalue %v866[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v869 = llvm.insertvalue %v868, %v867[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v870 = llvm.extractvalue %v866[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v871 = llvm.insertvalue %v870, %v869[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v872 = llvm.extractvalue %v866[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v873 = llvm.insertvalue %v872, %v871[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v874 = llvm.extractvalue %v866[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v875 = llvm.insertvalue %v874, %v873[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v876 = llvm.extractvalue %v866[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v877 = llvm.insertvalue %v876, %v875[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v878 = llvm.extractvalue %v866[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v879 = llvm.insertvalue %v878, %v877[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v880 = llvm.mlir.constant(1 : i64) : i64
%v881 = llvm.alloca %v880 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v879, %v881 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v882 = llvm.load %v881 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v882 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_div(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v883 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v884 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v885 = llvm.insertvalue %v884, %v883[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v886 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v887 = llvm.insertvalue %v886, %v885[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v888 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v889 = llvm.insertvalue %v888, %v887[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v890 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v891 = llvm.insertvalue %v890, %v889[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v892 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v893 = llvm.insertvalue %v892, %v891[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v894 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v895 = llvm.insertvalue %v894, %v893[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v896 = llvm.mlir.constant(1 : i64) : i64
%v897 = llvm.alloca %v896 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v895, %v897 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v898 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v899 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v900 = llvm.insertvalue %v899, %v898[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v901 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v902 = llvm.insertvalue %v901, %v900[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v903 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v904 = llvm.insertvalue %v903, %v902[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v905 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v906 = llvm.insertvalue %v905, %v904[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v907 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v908 = llvm.insertvalue %v907, %v906[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v909 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v910 = llvm.insertvalue %v909, %v908[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v911 = llvm.mlir.constant(1 : i64) : i64
%v912 = llvm.alloca %v911 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v910, %v912 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v913 = llvm.load %v897 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v914 = llvm.getelementptr %v897[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v915 = llvm.load %v914 : !llvm.ptr -> i32
%v916 = llvm.load %v897 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v917 = llvm.getelementptr %v897[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v918 = llvm.load %v917 : !llvm.ptr -> i32
%v919 = llvm.load %v897 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v920 = llvm.getelementptr %v897[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v921 = llvm.load %v920 : !llvm.ptr -> i32
%v922 = llvm.load %v897 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v923 = llvm.getelementptr %v897[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v924 = llvm.load %v923 : !llvm.ptr -> i32
%v925 = func.call @tensor_zeros(%v915, %v918, %v921, %v924) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v926 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v927 = llvm.extractvalue %v925[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v928 = llvm.insertvalue %v927, %v926[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v929 = llvm.extractvalue %v925[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v930 = llvm.insertvalue %v929, %v928[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v931 = llvm.extractvalue %v925[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v932 = llvm.insertvalue %v931, %v930[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v933 = llvm.extractvalue %v925[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v934 = llvm.insertvalue %v933, %v932[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v935 = llvm.extractvalue %v925[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v936 = llvm.insertvalue %v935, %v934[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v937 = llvm.extractvalue %v925[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v938 = llvm.insertvalue %v937, %v936[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v939 = llvm.mlir.constant(1 : i64) : i64
%v940 = llvm.alloca %v939 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v938, %v940 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v941 = llvm.load %v940 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v942 = llvm.mlir.constant(1 : i64) : i64
%v943 = llvm.alloca %v942 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v941, %v943 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v944 = arith.constant 0 : i32
%v945 = llvm.load %v897 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v946 = llvm.getelementptr %v897[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v947 = llvm.load %v946 : !llvm.ptr -> i32
%v948 = arith.index_cast %v944 : i32 to index
%v949 = arith.index_cast %v947 : i32 to index
%v950 = arith.constant 1 : index
%v951 = arith.constant -1 : index
%v952 = arith.cmpi sle, %v948, %v949 : index
%v953 = arith.select %v952, %v950, %v951 : index
cf.br ^b31(%v948 : index)
^b31(%v954: index):
%v955 = arith.cmpi slt, %v954, %v949 : index
%v956 = arith.cmpi sgt, %v954, %v949 : index
%v957 = arith.select %v952, %v955, %v956 : i1
cf.cond_br %v957, ^b32(%v954 : index), ^b33(%v954 : index)
^b32(%v958: index):
%v959 = llvm.load %v897 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v960 = llvm.getelementptr %v897[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v961 = llvm.load %v960 : !llvm.ptr -> !llvm.ptr
%v962 = arith.index_cast %v958 : index to i64
%v963 = llvm.getelementptr %v961[%v962] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v964 = llvm.load %v963 : !llvm.ptr -> f32
%v965 = llvm.load %v912 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v966 = llvm.getelementptr %v912[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v967 = llvm.load %v966 : !llvm.ptr -> !llvm.ptr
%v968 = arith.index_cast %v958 : index to i64
%v969 = llvm.getelementptr %v967[%v968] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v970 = llvm.load %v969 : !llvm.ptr -> f32
%v971 = arith.divf %v964, %v970 : f32
%v972 = llvm.load %v943 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v973 = llvm.getelementptr %v943[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v974 = llvm.load %v973 : !llvm.ptr -> !llvm.ptr
%v975 = arith.index_cast %v958 : index to i64
%v976 = llvm.getelementptr %v974[%v975] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v971, %v976 : f32, !llvm.ptr
%v977 = arith.addi %v958, %v953 : index
cf.br ^b31(%v977 : index)
^b33(%v978: index):
%v979 = llvm.load %v943 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v980 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v981 = llvm.extractvalue %v979[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v982 = llvm.insertvalue %v981, %v980[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v983 = llvm.extractvalue %v979[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v984 = llvm.insertvalue %v983, %v982[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v985 = llvm.extractvalue %v979[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v986 = llvm.insertvalue %v985, %v984[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v987 = llvm.extractvalue %v979[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v988 = llvm.insertvalue %v987, %v986[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v989 = llvm.extractvalue %v979[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v990 = llvm.insertvalue %v989, %v988[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v991 = llvm.extractvalue %v979[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v992 = llvm.insertvalue %v991, %v990[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v993 = llvm.mlir.constant(1 : i64) : i64
%v994 = llvm.alloca %v993 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v992, %v994 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v995 = llvm.load %v994 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v995 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_scale(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: f32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v996 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v997 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v998 = llvm.insertvalue %v997, %v996[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v999 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1000 = llvm.insertvalue %v999, %v998[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1001 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1002 = llvm.insertvalue %v1001, %v1000[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1003 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1004 = llvm.insertvalue %v1003, %v1002[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1005 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1006 = llvm.insertvalue %v1005, %v1004[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1007 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1008 = llvm.insertvalue %v1007, %v1006[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1009 = llvm.mlir.constant(1 : i64) : i64
%v1010 = llvm.alloca %v1009 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1008, %v1010 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1011 = llvm.load %v1010 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1012 = llvm.getelementptr %v1010[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1013 = llvm.load %v1012 : !llvm.ptr -> i32
%v1014 = llvm.load %v1010 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1015 = llvm.getelementptr %v1010[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1016 = llvm.load %v1015 : !llvm.ptr -> i32
%v1017 = llvm.load %v1010 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1018 = llvm.getelementptr %v1010[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1019 = llvm.load %v1018 : !llvm.ptr -> i32
%v1020 = llvm.load %v1010 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1021 = llvm.getelementptr %v1010[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1022 = llvm.load %v1021 : !llvm.ptr -> i32
%v1023 = func.call @tensor_zeros(%v1013, %v1016, %v1019, %v1022) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1024 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1025 = llvm.extractvalue %v1023[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1026 = llvm.insertvalue %v1025, %v1024[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1027 = llvm.extractvalue %v1023[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1028 = llvm.insertvalue %v1027, %v1026[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1029 = llvm.extractvalue %v1023[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1030 = llvm.insertvalue %v1029, %v1028[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1031 = llvm.extractvalue %v1023[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1032 = llvm.insertvalue %v1031, %v1030[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1033 = llvm.extractvalue %v1023[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1034 = llvm.insertvalue %v1033, %v1032[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1035 = llvm.extractvalue %v1023[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1036 = llvm.insertvalue %v1035, %v1034[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1037 = llvm.mlir.constant(1 : i64) : i64
%v1038 = llvm.alloca %v1037 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1036, %v1038 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1039 = llvm.load %v1038 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1040 = llvm.mlir.constant(1 : i64) : i64
%v1041 = llvm.alloca %v1040 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1039, %v1041 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1042 = arith.constant 0 : i32
%v1043 = llvm.load %v1010 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1044 = llvm.getelementptr %v1010[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1045 = llvm.load %v1044 : !llvm.ptr -> i32
%v1046 = arith.index_cast %v1042 : i32 to index
%v1047 = arith.index_cast %v1045 : i32 to index
%v1048 = arith.constant 1 : index
%v1049 = arith.constant -1 : index
%v1050 = arith.cmpi sle, %v1046, %v1047 : index
%v1051 = arith.select %v1050, %v1048, %v1049 : index
cf.br ^b34(%v1046 : index)
^b34(%v1052: index):
%v1053 = arith.cmpi slt, %v1052, %v1047 : index
%v1054 = arith.cmpi sgt, %v1052, %v1047 : index
%v1055 = arith.select %v1050, %v1053, %v1054 : i1
cf.cond_br %v1055, ^b35(%v1052 : index), ^b36(%v1052 : index)
^b35(%v1056: index):
%v1057 = llvm.load %v1010 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1058 = llvm.getelementptr %v1010[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1059 = llvm.load %v1058 : !llvm.ptr -> !llvm.ptr
%v1060 = arith.index_cast %v1056 : index to i64
%v1061 = llvm.getelementptr %v1059[%v1060] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1062 = llvm.load %v1061 : !llvm.ptr -> f32
%v1063 = arith.mulf %v1062, %arg1 : f32
%v1064 = llvm.load %v1041 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1065 = llvm.getelementptr %v1041[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1066 = llvm.load %v1065 : !llvm.ptr -> !llvm.ptr
%v1067 = arith.index_cast %v1056 : index to i64
%v1068 = llvm.getelementptr %v1066[%v1067] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1063, %v1068 : f32, !llvm.ptr
%v1069 = arith.addi %v1056, %v1051 : index
cf.br ^b34(%v1069 : index)
^b36(%v1070: index):
%v1071 = llvm.load %v1041 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1072 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1073 = llvm.extractvalue %v1071[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1074 = llvm.insertvalue %v1073, %v1072[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1075 = llvm.extractvalue %v1071[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1076 = llvm.insertvalue %v1075, %v1074[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1077 = llvm.extractvalue %v1071[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1078 = llvm.insertvalue %v1077, %v1076[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1079 = llvm.extractvalue %v1071[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1080 = llvm.insertvalue %v1079, %v1078[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1081 = llvm.extractvalue %v1071[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1082 = llvm.insertvalue %v1081, %v1080[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1083 = llvm.extractvalue %v1071[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1084 = llvm.insertvalue %v1083, %v1082[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1085 = llvm.mlir.constant(1 : i64) : i64
%v1086 = llvm.alloca %v1085 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1084, %v1086 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1087 = llvm.load %v1086 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1087 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_add_scalar(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: f32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1088 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1089 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1090 = llvm.insertvalue %v1089, %v1088[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1091 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1092 = llvm.insertvalue %v1091, %v1090[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1093 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1094 = llvm.insertvalue %v1093, %v1092[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1095 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1096 = llvm.insertvalue %v1095, %v1094[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1097 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1098 = llvm.insertvalue %v1097, %v1096[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1099 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1100 = llvm.insertvalue %v1099, %v1098[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1101 = llvm.mlir.constant(1 : i64) : i64
%v1102 = llvm.alloca %v1101 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1100, %v1102 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1103 = llvm.load %v1102 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1104 = llvm.getelementptr %v1102[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1105 = llvm.load %v1104 : !llvm.ptr -> i32
%v1106 = llvm.load %v1102 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1107 = llvm.getelementptr %v1102[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1108 = llvm.load %v1107 : !llvm.ptr -> i32
%v1109 = llvm.load %v1102 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1110 = llvm.getelementptr %v1102[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1111 = llvm.load %v1110 : !llvm.ptr -> i32
%v1112 = llvm.load %v1102 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1113 = llvm.getelementptr %v1102[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1114 = llvm.load %v1113 : !llvm.ptr -> i32
%v1115 = func.call @tensor_zeros(%v1105, %v1108, %v1111, %v1114) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1116 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1117 = llvm.extractvalue %v1115[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1118 = llvm.insertvalue %v1117, %v1116[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1119 = llvm.extractvalue %v1115[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1120 = llvm.insertvalue %v1119, %v1118[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1121 = llvm.extractvalue %v1115[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1122 = llvm.insertvalue %v1121, %v1120[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1123 = llvm.extractvalue %v1115[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1124 = llvm.insertvalue %v1123, %v1122[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1125 = llvm.extractvalue %v1115[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1126 = llvm.insertvalue %v1125, %v1124[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1127 = llvm.extractvalue %v1115[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1128 = llvm.insertvalue %v1127, %v1126[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1129 = llvm.mlir.constant(1 : i64) : i64
%v1130 = llvm.alloca %v1129 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1128, %v1130 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1131 = llvm.load %v1130 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1132 = llvm.mlir.constant(1 : i64) : i64
%v1133 = llvm.alloca %v1132 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1131, %v1133 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1134 = arith.constant 0 : i32
%v1135 = llvm.load %v1102 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1136 = llvm.getelementptr %v1102[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1137 = llvm.load %v1136 : !llvm.ptr -> i32
%v1138 = arith.index_cast %v1134 : i32 to index
%v1139 = arith.index_cast %v1137 : i32 to index
%v1140 = arith.constant 1 : index
%v1141 = arith.constant -1 : index
%v1142 = arith.cmpi sle, %v1138, %v1139 : index
%v1143 = arith.select %v1142, %v1140, %v1141 : index
cf.br ^b37(%v1138 : index)
^b37(%v1144: index):
%v1145 = arith.cmpi slt, %v1144, %v1139 : index
%v1146 = arith.cmpi sgt, %v1144, %v1139 : index
%v1147 = arith.select %v1142, %v1145, %v1146 : i1
cf.cond_br %v1147, ^b38(%v1144 : index), ^b39(%v1144 : index)
^b38(%v1148: index):
%v1149 = llvm.load %v1102 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1150 = llvm.getelementptr %v1102[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1151 = llvm.load %v1150 : !llvm.ptr -> !llvm.ptr
%v1152 = arith.index_cast %v1148 : index to i64
%v1153 = llvm.getelementptr %v1151[%v1152] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1154 = llvm.load %v1153 : !llvm.ptr -> f32
%v1155 = arith.addf %v1154, %arg1 : f32
%v1156 = llvm.load %v1133 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1157 = llvm.getelementptr %v1133[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1158 = llvm.load %v1157 : !llvm.ptr -> !llvm.ptr
%v1159 = arith.index_cast %v1148 : index to i64
%v1160 = llvm.getelementptr %v1158[%v1159] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1155, %v1160 : f32, !llvm.ptr
%v1161 = arith.addi %v1148, %v1143 : index
cf.br ^b37(%v1161 : index)
^b39(%v1162: index):
%v1163 = llvm.load %v1133 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1164 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1165 = llvm.extractvalue %v1163[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1166 = llvm.insertvalue %v1165, %v1164[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1167 = llvm.extractvalue %v1163[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1168 = llvm.insertvalue %v1167, %v1166[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1169 = llvm.extractvalue %v1163[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1170 = llvm.insertvalue %v1169, %v1168[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1171 = llvm.extractvalue %v1163[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1172 = llvm.insertvalue %v1171, %v1170[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1173 = llvm.extractvalue %v1163[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1174 = llvm.insertvalue %v1173, %v1172[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1175 = llvm.extractvalue %v1163[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1176 = llvm.insertvalue %v1175, %v1174[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1177 = llvm.mlir.constant(1 : i64) : i64
%v1178 = llvm.alloca %v1177 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1176, %v1178 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1179 = llvm.load %v1178 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1179 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_neg(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1180 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1181 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1182 = llvm.insertvalue %v1181, %v1180[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1183 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1184 = llvm.insertvalue %v1183, %v1182[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1185 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1186 = llvm.insertvalue %v1185, %v1184[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1187 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1188 = llvm.insertvalue %v1187, %v1186[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1189 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1190 = llvm.insertvalue %v1189, %v1188[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1191 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1192 = llvm.insertvalue %v1191, %v1190[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1193 = llvm.mlir.constant(1 : i64) : i64
%v1194 = llvm.alloca %v1193 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1192, %v1194 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1195 = llvm.load %v1194 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1196 = llvm.getelementptr %v1194[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1197 = llvm.load %v1196 : !llvm.ptr -> i32
%v1198 = llvm.load %v1194 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1199 = llvm.getelementptr %v1194[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1200 = llvm.load %v1199 : !llvm.ptr -> i32
%v1201 = llvm.load %v1194 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1202 = llvm.getelementptr %v1194[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1203 = llvm.load %v1202 : !llvm.ptr -> i32
%v1204 = llvm.load %v1194 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1205 = llvm.getelementptr %v1194[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1206 = llvm.load %v1205 : !llvm.ptr -> i32
%v1207 = func.call @tensor_zeros(%v1197, %v1200, %v1203, %v1206) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1208 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1209 = llvm.extractvalue %v1207[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1210 = llvm.insertvalue %v1209, %v1208[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1211 = llvm.extractvalue %v1207[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1212 = llvm.insertvalue %v1211, %v1210[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1213 = llvm.extractvalue %v1207[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1214 = llvm.insertvalue %v1213, %v1212[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1215 = llvm.extractvalue %v1207[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1216 = llvm.insertvalue %v1215, %v1214[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1217 = llvm.extractvalue %v1207[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1218 = llvm.insertvalue %v1217, %v1216[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1219 = llvm.extractvalue %v1207[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1220 = llvm.insertvalue %v1219, %v1218[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1221 = llvm.mlir.constant(1 : i64) : i64
%v1222 = llvm.alloca %v1221 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1220, %v1222 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1223 = llvm.load %v1222 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1224 = llvm.mlir.constant(1 : i64) : i64
%v1225 = llvm.alloca %v1224 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1223, %v1225 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1226 = arith.constant 0 : i32
%v1227 = llvm.load %v1194 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1228 = llvm.getelementptr %v1194[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1229 = llvm.load %v1228 : !llvm.ptr -> i32
%v1230 = arith.index_cast %v1226 : i32 to index
%v1231 = arith.index_cast %v1229 : i32 to index
%v1232 = arith.constant 1 : index
%v1233 = arith.constant -1 : index
%v1234 = arith.cmpi sle, %v1230, %v1231 : index
%v1235 = arith.select %v1234, %v1232, %v1233 : index
cf.br ^b40(%v1230 : index)
^b40(%v1236: index):
%v1237 = arith.cmpi slt, %v1236, %v1231 : index
%v1238 = arith.cmpi sgt, %v1236, %v1231 : index
%v1239 = arith.select %v1234, %v1237, %v1238 : i1
cf.cond_br %v1239, ^b41(%v1236 : index), ^b42(%v1236 : index)
^b41(%v1240: index):
%v1241 = arith.constant 0.0 : f64
%v1242 = llvm.load %v1194 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1243 = llvm.getelementptr %v1194[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1244 = llvm.load %v1243 : !llvm.ptr -> !llvm.ptr
%v1245 = arith.index_cast %v1240 : index to i64
%v1246 = llvm.getelementptr %v1244[%v1245] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1247 = llvm.load %v1246 : !llvm.ptr -> f32
%v1248 = arith.extf %v1247 : f32 to f64
%v1249 = arith.subf %v1241, %v1248 : f64
%v1250 = llvm.load %v1225 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1251 = llvm.getelementptr %v1225[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1252 = llvm.load %v1251 : !llvm.ptr -> !llvm.ptr
%v1253 = arith.truncf %v1249 : f64 to f32
%v1254 = arith.index_cast %v1240 : index to i64
%v1255 = llvm.getelementptr %v1252[%v1254] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1253, %v1255 : f32, !llvm.ptr
%v1256 = arith.addi %v1240, %v1235 : index
cf.br ^b40(%v1256 : index)
^b42(%v1257: index):
%v1258 = llvm.load %v1225 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1259 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1260 = llvm.extractvalue %v1258[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1261 = llvm.insertvalue %v1260, %v1259[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1262 = llvm.extractvalue %v1258[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1263 = llvm.insertvalue %v1262, %v1261[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1264 = llvm.extractvalue %v1258[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1265 = llvm.insertvalue %v1264, %v1263[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1266 = llvm.extractvalue %v1258[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1267 = llvm.insertvalue %v1266, %v1265[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1268 = llvm.extractvalue %v1258[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1269 = llvm.insertvalue %v1268, %v1267[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1270 = llvm.extractvalue %v1258[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1271 = llvm.insertvalue %v1270, %v1269[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1272 = llvm.mlir.constant(1 : i64) : i64
%v1273 = llvm.alloca %v1272 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1271, %v1273 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1274 = llvm.load %v1273 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1274 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_relu(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1275 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1276 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1277 = llvm.insertvalue %v1276, %v1275[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1278 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1279 = llvm.insertvalue %v1278, %v1277[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1280 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1281 = llvm.insertvalue %v1280, %v1279[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1282 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1283 = llvm.insertvalue %v1282, %v1281[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1284 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1285 = llvm.insertvalue %v1284, %v1283[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1286 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1287 = llvm.insertvalue %v1286, %v1285[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1288 = llvm.mlir.constant(1 : i64) : i64
%v1289 = llvm.alloca %v1288 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1287, %v1289 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1290 = llvm.load %v1289 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1291 = llvm.getelementptr %v1289[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1292 = llvm.load %v1291 : !llvm.ptr -> i32
%v1293 = llvm.load %v1289 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1294 = llvm.getelementptr %v1289[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1295 = llvm.load %v1294 : !llvm.ptr -> i32
%v1296 = llvm.load %v1289 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1297 = llvm.getelementptr %v1289[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1298 = llvm.load %v1297 : !llvm.ptr -> i32
%v1299 = llvm.load %v1289 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1300 = llvm.getelementptr %v1289[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1301 = llvm.load %v1300 : !llvm.ptr -> i32
%v1302 = func.call @tensor_zeros(%v1292, %v1295, %v1298, %v1301) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1303 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1304 = llvm.extractvalue %v1302[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1305 = llvm.insertvalue %v1304, %v1303[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1306 = llvm.extractvalue %v1302[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1307 = llvm.insertvalue %v1306, %v1305[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1308 = llvm.extractvalue %v1302[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1309 = llvm.insertvalue %v1308, %v1307[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1310 = llvm.extractvalue %v1302[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1311 = llvm.insertvalue %v1310, %v1309[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1312 = llvm.extractvalue %v1302[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1313 = llvm.insertvalue %v1312, %v1311[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1314 = llvm.extractvalue %v1302[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1315 = llvm.insertvalue %v1314, %v1313[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1316 = llvm.mlir.constant(1 : i64) : i64
%v1317 = llvm.alloca %v1316 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1315, %v1317 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1318 = llvm.load %v1317 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1319 = llvm.mlir.constant(1 : i64) : i64
%v1320 = llvm.alloca %v1319 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1318, %v1320 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1321 = arith.constant 0 : i32
%v1322 = llvm.load %v1289 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1323 = llvm.getelementptr %v1289[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1324 = llvm.load %v1323 : !llvm.ptr -> i32
%v1325 = arith.index_cast %v1321 : i32 to index
%v1326 = arith.index_cast %v1324 : i32 to index
%v1327 = arith.constant 1 : index
%v1328 = arith.constant -1 : index
%v1329 = arith.cmpi sle, %v1325, %v1326 : index
%v1330 = arith.select %v1329, %v1327, %v1328 : index
cf.br ^b43(%v1325 : index)
^b43(%v1331: index):
%v1332 = arith.cmpi slt, %v1331, %v1326 : index
%v1333 = arith.cmpi sgt, %v1331, %v1326 : index
%v1334 = arith.select %v1329, %v1332, %v1333 : i1
cf.cond_br %v1334, ^b44(%v1331 : index), ^b45(%v1331 : index)
^b44(%v1335: index):
%v1336 = llvm.load %v1289 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1337 = llvm.getelementptr %v1289[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1338 = llvm.load %v1337 : !llvm.ptr -> !llvm.ptr
%v1339 = arith.index_cast %v1335 : index to i64
%v1340 = llvm.getelementptr %v1338[%v1339] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1341 = llvm.load %v1340 : !llvm.ptr -> f32
%v1342 = arith.constant 0.0 : f64
%v1343 = arith.extf %v1341 : f32 to f64
%v1344 = arith.cmpf ogt, %v1343, %v1342 : f64
cf.cond_br %v1344, ^b46, ^b47
^b46:
%v1345 = llvm.load %v1289 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1346 = llvm.getelementptr %v1289[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1347 = llvm.load %v1346 : !llvm.ptr -> !llvm.ptr
%v1348 = arith.index_cast %v1335 : index to i64
%v1349 = llvm.getelementptr %v1347[%v1348] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1350 = llvm.load %v1349 : !llvm.ptr -> f32
%v1351 = llvm.load %v1320 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1352 = llvm.getelementptr %v1320[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1353 = llvm.load %v1352 : !llvm.ptr -> !llvm.ptr
%v1354 = arith.index_cast %v1335 : index to i64
%v1355 = llvm.getelementptr %v1353[%v1354] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1350, %v1355 : f32, !llvm.ptr
cf.br ^b48
^b47:
%v1356 = arith.constant 0.0 : f64
%v1357 = llvm.load %v1320 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1358 = llvm.getelementptr %v1320[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1359 = llvm.load %v1358 : !llvm.ptr -> !llvm.ptr
%v1360 = arith.truncf %v1356 : f64 to f32
%v1361 = arith.index_cast %v1335 : index to i64
%v1362 = llvm.getelementptr %v1359[%v1361] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1360, %v1362 : f32, !llvm.ptr
cf.br ^b48
^b48:
%v1363 = arith.addi %v1335, %v1330 : index
cf.br ^b43(%v1363 : index)
^b45(%v1364: index):
%v1365 = llvm.load %v1320 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1366 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1367 = llvm.extractvalue %v1365[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1368 = llvm.insertvalue %v1367, %v1366[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1369 = llvm.extractvalue %v1365[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1370 = llvm.insertvalue %v1369, %v1368[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1371 = llvm.extractvalue %v1365[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1372 = llvm.insertvalue %v1371, %v1370[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1373 = llvm.extractvalue %v1365[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1374 = llvm.insertvalue %v1373, %v1372[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1375 = llvm.extractvalue %v1365[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1376 = llvm.insertvalue %v1375, %v1374[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1377 = llvm.extractvalue %v1365[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1378 = llvm.insertvalue %v1377, %v1376[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1379 = llvm.mlir.constant(1 : i64) : i64
%v1380 = llvm.alloca %v1379 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1378, %v1380 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1381 = llvm.load %v1380 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1381 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_sigmoid(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1382 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1383 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1384 = llvm.insertvalue %v1383, %v1382[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1385 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1386 = llvm.insertvalue %v1385, %v1384[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1387 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1388 = llvm.insertvalue %v1387, %v1386[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1389 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1390 = llvm.insertvalue %v1389, %v1388[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1391 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1392 = llvm.insertvalue %v1391, %v1390[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1393 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1394 = llvm.insertvalue %v1393, %v1392[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1395 = llvm.mlir.constant(1 : i64) : i64
%v1396 = llvm.alloca %v1395 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1394, %v1396 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1397 = llvm.load %v1396 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1398 = llvm.getelementptr %v1396[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1399 = llvm.load %v1398 : !llvm.ptr -> i32
%v1400 = llvm.load %v1396 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1401 = llvm.getelementptr %v1396[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1402 = llvm.load %v1401 : !llvm.ptr -> i32
%v1403 = llvm.load %v1396 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1404 = llvm.getelementptr %v1396[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1405 = llvm.load %v1404 : !llvm.ptr -> i32
%v1406 = llvm.load %v1396 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1407 = llvm.getelementptr %v1396[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1408 = llvm.load %v1407 : !llvm.ptr -> i32
%v1409 = func.call @tensor_zeros(%v1399, %v1402, %v1405, %v1408) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1410 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1411 = llvm.extractvalue %v1409[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1412 = llvm.insertvalue %v1411, %v1410[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1413 = llvm.extractvalue %v1409[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1414 = llvm.insertvalue %v1413, %v1412[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1415 = llvm.extractvalue %v1409[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1416 = llvm.insertvalue %v1415, %v1414[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1417 = llvm.extractvalue %v1409[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1418 = llvm.insertvalue %v1417, %v1416[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1419 = llvm.extractvalue %v1409[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1420 = llvm.insertvalue %v1419, %v1418[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1421 = llvm.extractvalue %v1409[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1422 = llvm.insertvalue %v1421, %v1420[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1423 = llvm.mlir.constant(1 : i64) : i64
%v1424 = llvm.alloca %v1423 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1422, %v1424 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1425 = llvm.load %v1424 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1426 = llvm.mlir.constant(1 : i64) : i64
%v1427 = llvm.alloca %v1426 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1425, %v1427 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1428 = arith.constant 0 : i32
%v1429 = llvm.load %v1396 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1430 = llvm.getelementptr %v1396[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1431 = llvm.load %v1430 : !llvm.ptr -> i32
%v1432 = arith.index_cast %v1428 : i32 to index
%v1433 = arith.index_cast %v1431 : i32 to index
%v1434 = arith.constant 1 : index
%v1435 = arith.constant -1 : index
%v1436 = arith.cmpi sle, %v1432, %v1433 : index
%v1437 = arith.select %v1436, %v1434, %v1435 : index
cf.br ^b49(%v1432 : index)
^b49(%v1438: index):
%v1439 = arith.cmpi slt, %v1438, %v1433 : index
%v1440 = arith.cmpi sgt, %v1438, %v1433 : index
%v1441 = arith.select %v1436, %v1439, %v1440 : i1
cf.cond_br %v1441, ^b50(%v1438 : index), ^b51(%v1438 : index)
^b50(%v1442: index):
%v1443 = arith.constant 0.0 : f64
%v1444 = llvm.load %v1396 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1445 = llvm.getelementptr %v1396[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1446 = llvm.load %v1445 : !llvm.ptr -> !llvm.ptr
%v1447 = arith.index_cast %v1442 : index to i64
%v1448 = llvm.getelementptr %v1446[%v1447] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1449 = llvm.load %v1448 : !llvm.ptr -> f32
%v1450 = arith.extf %v1449 : f32 to f64
%v1451 = arith.subf %v1443, %v1450 : f64
%v1452 = func.call @exp(%v1451) : (f64) -> f64
%v1453 = arith.constant 1.0 : f64
%v1454 = arith.constant 1.0 : f64
%v1455 = arith.addf %v1454, %v1452 : f64
%v1456 = arith.divf %v1453, %v1455 : f64
%v1457 = llvm.load %v1427 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1458 = llvm.getelementptr %v1427[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1459 = llvm.load %v1458 : !llvm.ptr -> !llvm.ptr
%v1460 = arith.truncf %v1456 : f64 to f32
%v1461 = arith.index_cast %v1442 : index to i64
%v1462 = llvm.getelementptr %v1459[%v1461] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1460, %v1462 : f32, !llvm.ptr
%v1463 = arith.addi %v1442, %v1437 : index
cf.br ^b49(%v1463 : index)
^b51(%v1464: index):
%v1465 = llvm.load %v1427 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1466 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1467 = llvm.extractvalue %v1465[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1468 = llvm.insertvalue %v1467, %v1466[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1469 = llvm.extractvalue %v1465[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1470 = llvm.insertvalue %v1469, %v1468[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1471 = llvm.extractvalue %v1465[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1472 = llvm.insertvalue %v1471, %v1470[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1473 = llvm.extractvalue %v1465[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1474 = llvm.insertvalue %v1473, %v1472[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1475 = llvm.extractvalue %v1465[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1476 = llvm.insertvalue %v1475, %v1474[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1477 = llvm.extractvalue %v1465[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1478 = llvm.insertvalue %v1477, %v1476[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1479 = llvm.mlir.constant(1 : i64) : i64
%v1480 = llvm.alloca %v1479 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1478, %v1480 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1481 = llvm.load %v1480 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1481 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_tanh(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1482 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1483 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1484 = llvm.insertvalue %v1483, %v1482[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1485 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1486 = llvm.insertvalue %v1485, %v1484[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1487 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1488 = llvm.insertvalue %v1487, %v1486[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1489 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1490 = llvm.insertvalue %v1489, %v1488[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1491 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1492 = llvm.insertvalue %v1491, %v1490[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1493 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1494 = llvm.insertvalue %v1493, %v1492[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1495 = llvm.mlir.constant(1 : i64) : i64
%v1496 = llvm.alloca %v1495 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1494, %v1496 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1497 = llvm.load %v1496 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1498 = llvm.getelementptr %v1496[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1499 = llvm.load %v1498 : !llvm.ptr -> i32
%v1500 = llvm.load %v1496 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1501 = llvm.getelementptr %v1496[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1502 = llvm.load %v1501 : !llvm.ptr -> i32
%v1503 = llvm.load %v1496 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1504 = llvm.getelementptr %v1496[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1505 = llvm.load %v1504 : !llvm.ptr -> i32
%v1506 = llvm.load %v1496 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1507 = llvm.getelementptr %v1496[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1508 = llvm.load %v1507 : !llvm.ptr -> i32
%v1509 = func.call @tensor_zeros(%v1499, %v1502, %v1505, %v1508) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1510 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1511 = llvm.extractvalue %v1509[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1512 = llvm.insertvalue %v1511, %v1510[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1513 = llvm.extractvalue %v1509[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1514 = llvm.insertvalue %v1513, %v1512[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1515 = llvm.extractvalue %v1509[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1516 = llvm.insertvalue %v1515, %v1514[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1517 = llvm.extractvalue %v1509[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1518 = llvm.insertvalue %v1517, %v1516[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1519 = llvm.extractvalue %v1509[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1520 = llvm.insertvalue %v1519, %v1518[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1521 = llvm.extractvalue %v1509[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1522 = llvm.insertvalue %v1521, %v1520[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1523 = llvm.mlir.constant(1 : i64) : i64
%v1524 = llvm.alloca %v1523 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1522, %v1524 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1525 = llvm.load %v1524 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1526 = llvm.mlir.constant(1 : i64) : i64
%v1527 = llvm.alloca %v1526 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1525, %v1527 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1528 = arith.constant 0 : i32
%v1529 = llvm.load %v1496 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1530 = llvm.getelementptr %v1496[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1531 = llvm.load %v1530 : !llvm.ptr -> i32
%v1532 = arith.index_cast %v1528 : i32 to index
%v1533 = arith.index_cast %v1531 : i32 to index
%v1534 = arith.constant 1 : index
%v1535 = arith.constant -1 : index
%v1536 = arith.cmpi sle, %v1532, %v1533 : index
%v1537 = arith.select %v1536, %v1534, %v1535 : index
cf.br ^b52(%v1532 : index)
^b52(%v1538: index):
%v1539 = arith.cmpi slt, %v1538, %v1533 : index
%v1540 = arith.cmpi sgt, %v1538, %v1533 : index
%v1541 = arith.select %v1536, %v1539, %v1540 : i1
cf.cond_br %v1541, ^b53(%v1538 : index), ^b54(%v1538 : index)
^b53(%v1542: index):
%v1543 = llvm.load %v1496 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1544 = llvm.getelementptr %v1496[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1545 = llvm.load %v1544 : !llvm.ptr -> !llvm.ptr
%v1546 = arith.index_cast %v1542 : index to i64
%v1547 = llvm.getelementptr %v1545[%v1546] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1548 = llvm.load %v1547 : !llvm.ptr -> f32
%v1549 = arith.extf %v1548 : f32 to f64
%v1550 = func.call @exp(%v1549) : (f64) -> f64
%v1551 = arith.constant 0.0 : f64
%v1552 = llvm.load %v1496 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1553 = llvm.getelementptr %v1496[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1554 = llvm.load %v1553 : !llvm.ptr -> !llvm.ptr
%v1555 = arith.index_cast %v1542 : index to i64
%v1556 = llvm.getelementptr %v1554[%v1555] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1557 = llvm.load %v1556 : !llvm.ptr -> f32
%v1558 = arith.extf %v1557 : f32 to f64
%v1559 = arith.subf %v1551, %v1558 : f64
%v1560 = func.call @exp(%v1559) : (f64) -> f64
%v1561 = arith.subf %v1550, %v1560 : f64
%v1562 = arith.addf %v1550, %v1560 : f64
%v1563 = arith.divf %v1561, %v1562 : f64
%v1564 = llvm.load %v1527 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1565 = llvm.getelementptr %v1527[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1566 = llvm.load %v1565 : !llvm.ptr -> !llvm.ptr
%v1567 = arith.truncf %v1563 : f64 to f32
%v1568 = arith.index_cast %v1542 : index to i64
%v1569 = llvm.getelementptr %v1566[%v1568] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1567, %v1569 : f32, !llvm.ptr
%v1570 = arith.addi %v1542, %v1537 : index
cf.br ^b52(%v1570 : index)
^b54(%v1571: index):
%v1572 = llvm.load %v1527 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1573 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1574 = llvm.extractvalue %v1572[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1575 = llvm.insertvalue %v1574, %v1573[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1576 = llvm.extractvalue %v1572[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1577 = llvm.insertvalue %v1576, %v1575[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1578 = llvm.extractvalue %v1572[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1579 = llvm.insertvalue %v1578, %v1577[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1580 = llvm.extractvalue %v1572[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1581 = llvm.insertvalue %v1580, %v1579[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1582 = llvm.extractvalue %v1572[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1583 = llvm.insertvalue %v1582, %v1581[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1584 = llvm.extractvalue %v1572[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1585 = llvm.insertvalue %v1584, %v1583[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1586 = llvm.mlir.constant(1 : i64) : i64
%v1587 = llvm.alloca %v1586 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1585, %v1587 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1588 = llvm.load %v1587 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1588 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_softmax(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1589 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1590 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1591 = llvm.insertvalue %v1590, %v1589[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1592 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1593 = llvm.insertvalue %v1592, %v1591[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1594 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1595 = llvm.insertvalue %v1594, %v1593[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1596 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1597 = llvm.insertvalue %v1596, %v1595[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1598 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1599 = llvm.insertvalue %v1598, %v1597[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1600 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1601 = llvm.insertvalue %v1600, %v1599[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1602 = llvm.mlir.constant(1 : i64) : i64
%v1603 = llvm.alloca %v1602 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1601, %v1603 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1604 = llvm.load %v1603 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1605 = llvm.getelementptr %v1603[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1606 = llvm.load %v1605 : !llvm.ptr -> i32
%v1607 = llvm.load %v1603 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1608 = llvm.getelementptr %v1603[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1609 = llvm.load %v1608 : !llvm.ptr -> i32
%v1610 = arith.constant 1 : i32
%v1611 = arith.constant 1 : i32
%v1612 = func.call @tensor_zeros(%v1606, %v1609, %v1610, %v1611) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1613 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1614 = llvm.extractvalue %v1612[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1615 = llvm.insertvalue %v1614, %v1613[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1616 = llvm.extractvalue %v1612[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1617 = llvm.insertvalue %v1616, %v1615[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1618 = llvm.extractvalue %v1612[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1619 = llvm.insertvalue %v1618, %v1617[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1620 = llvm.extractvalue %v1612[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1621 = llvm.insertvalue %v1620, %v1619[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1622 = llvm.extractvalue %v1612[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1623 = llvm.insertvalue %v1622, %v1621[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1624 = llvm.extractvalue %v1612[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1625 = llvm.insertvalue %v1624, %v1623[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1626 = llvm.mlir.constant(1 : i64) : i64
%v1627 = llvm.alloca %v1626 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1625, %v1627 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1628 = llvm.load %v1627 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1629 = llvm.mlir.constant(1 : i64) : i64
%v1630 = llvm.alloca %v1629 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1628, %v1630 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1631 = arith.constant 0 : i32
%v1632 = llvm.load %v1603 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1633 = llvm.getelementptr %v1603[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1634 = llvm.load %v1633 : !llvm.ptr -> i32
%v1635 = arith.index_cast %v1631 : i32 to index
%v1636 = arith.index_cast %v1634 : i32 to index
%v1637 = arith.constant 1 : index
%v1638 = arith.constant -1 : index
%v1639 = arith.cmpi sle, %v1635, %v1636 : index
%v1640 = arith.select %v1639, %v1637, %v1638 : index
cf.br ^b55(%v1635 : index)
^b55(%v1641: index):
%v1642 = arith.cmpi slt, %v1641, %v1636 : index
%v1643 = arith.cmpi sgt, %v1641, %v1636 : index
%v1644 = arith.select %v1639, %v1642, %v1643 : i1
cf.cond_br %v1644, ^b56(%v1641 : index), ^b57(%v1641 : index)
^b56(%v1645: index):
%v1646 = llvm.load %v1603 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1647 = llvm.getelementptr %v1603[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1648 = llvm.load %v1647 : !llvm.ptr -> !llvm.ptr
%v1649 = llvm.load %v1603 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1650 = llvm.getelementptr %v1603[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1651 = llvm.load %v1650 : !llvm.ptr -> i32
%v1652 = arith.index_cast %v1645 : index to i32
%v1653 = arith.muli %v1652, %v1651 : i32
%v1654 = arith.extsi %v1653 : i32 to i64
%v1655 = llvm.getelementptr %v1648[%v1654] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1656 = llvm.load %v1655 : !llvm.ptr -> f32
%v1657 = llvm.mlir.constant(1 : i64) : i64
%v1658 = llvm.alloca %v1657 x f32 : (i64) -> !llvm.ptr
llvm.store %v1656, %v1658 : f32, !llvm.ptr
%v1659 = arith.constant 1 : i32
%v1660 = llvm.load %v1603 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1661 = llvm.getelementptr %v1603[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1662 = llvm.load %v1661 : !llvm.ptr -> i32
%v1663 = arith.index_cast %v1659 : i32 to index
%v1664 = arith.index_cast %v1662 : i32 to index
%v1665 = arith.constant 1 : index
%v1666 = arith.constant -1 : index
%v1667 = arith.cmpi sle, %v1663, %v1664 : index
%v1668 = arith.select %v1667, %v1665, %v1666 : index
cf.br ^b58(%v1663 : index)
^b58(%v1669: index):
%v1670 = arith.cmpi slt, %v1669, %v1664 : index
%v1671 = arith.cmpi sgt, %v1669, %v1664 : index
%v1672 = arith.select %v1667, %v1670, %v1671 : i1
cf.cond_br %v1672, ^b59(%v1669 : index), ^b60(%v1669 : index)
^b59(%v1673: index):
%v1674 = llvm.load %v1603 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1675 = llvm.getelementptr %v1603[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1676 = llvm.load %v1675 : !llvm.ptr -> !llvm.ptr
%v1677 = llvm.load %v1603 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1678 = llvm.getelementptr %v1603[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1679 = llvm.load %v1678 : !llvm.ptr -> i32
%v1680 = arith.index_cast %v1645 : index to i32
%v1681 = arith.muli %v1680, %v1679 : i32
%v1682 = arith.index_cast %v1673 : index to i32
%v1683 = arith.addi %v1681, %v1682 : i32
%v1684 = arith.extsi %v1683 : i32 to i64
%v1685 = llvm.getelementptr %v1676[%v1684] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1686 = llvm.load %v1685 : !llvm.ptr -> f32
%v1687 = llvm.load %v1658 : !llvm.ptr -> f32
%v1688 = arith.cmpf ogt, %v1686, %v1687 : f32
cf.cond_br %v1688, ^b61, ^b62
^b61:
%v1689 = llvm.load %v1603 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1690 = llvm.getelementptr %v1603[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1691 = llvm.load %v1690 : !llvm.ptr -> !llvm.ptr
%v1692 = llvm.load %v1603 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1693 = llvm.getelementptr %v1603[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1694 = llvm.load %v1693 : !llvm.ptr -> i32
%v1695 = arith.index_cast %v1645 : index to i32
%v1696 = arith.muli %v1695, %v1694 : i32
%v1697 = arith.index_cast %v1673 : index to i32
%v1698 = arith.addi %v1696, %v1697 : i32
%v1699 = arith.extsi %v1698 : i32 to i64
%v1700 = llvm.getelementptr %v1691[%v1699] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1701 = llvm.load %v1700 : !llvm.ptr -> f32
llvm.store %v1701, %v1658 : f32, !llvm.ptr
cf.br ^b63
^b62:
cf.br ^b63
^b63:
%v1702 = arith.addi %v1673, %v1668 : index
cf.br ^b58(%v1702 : index)
^b60(%v1703: index):
%v1704 = arith.constant 0.0 : f64
%v1705 = llvm.mlir.constant(1 : i64) : i64
%v1706 = llvm.alloca %v1705 x f64 : (i64) -> !llvm.ptr
llvm.store %v1704, %v1706 : f64, !llvm.ptr
%v1707 = arith.constant 0 : i32
%v1708 = llvm.load %v1603 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1709 = llvm.getelementptr %v1603[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1710 = llvm.load %v1709 : !llvm.ptr -> i32
%v1711 = arith.index_cast %v1707 : i32 to index
%v1712 = arith.index_cast %v1710 : i32 to index
%v1713 = arith.constant 1 : index
%v1714 = arith.constant -1 : index
%v1715 = arith.cmpi sle, %v1711, %v1712 : index
%v1716 = arith.select %v1715, %v1713, %v1714 : index
cf.br ^b64(%v1711 : index)
^b64(%v1717: index):
%v1718 = arith.cmpi slt, %v1717, %v1712 : index
%v1719 = arith.cmpi sgt, %v1717, %v1712 : index
%v1720 = arith.select %v1715, %v1718, %v1719 : i1
cf.cond_br %v1720, ^b65(%v1717 : index), ^b66(%v1717 : index)
^b65(%v1721: index):
%v1722 = llvm.load %v1603 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1723 = llvm.getelementptr %v1603[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1724 = llvm.load %v1723 : !llvm.ptr -> !llvm.ptr
%v1725 = llvm.load %v1603 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1726 = llvm.getelementptr %v1603[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1727 = llvm.load %v1726 : !llvm.ptr -> i32
%v1728 = arith.index_cast %v1645 : index to i32
%v1729 = arith.muli %v1728, %v1727 : i32
%v1730 = arith.index_cast %v1721 : index to i32
%v1731 = arith.addi %v1729, %v1730 : i32
%v1732 = arith.extsi %v1731 : i32 to i64
%v1733 = llvm.getelementptr %v1724[%v1732] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1734 = llvm.load %v1733 : !llvm.ptr -> f32
%v1735 = llvm.load %v1658 : !llvm.ptr -> f32
%v1736 = arith.subf %v1734, %v1735 : f32
%v1737 = arith.extf %v1736 : f32 to f64
%v1738 = func.call @exp(%v1737) : (f64) -> f64
%v1739 = llvm.load %v1630 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1740 = llvm.getelementptr %v1630[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1741 = llvm.load %v1740 : !llvm.ptr -> !llvm.ptr
%v1742 = llvm.load %v1603 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1743 = llvm.getelementptr %v1603[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1744 = llvm.load %v1743 : !llvm.ptr -> i32
%v1745 = arith.index_cast %v1645 : index to i32
%v1746 = arith.muli %v1745, %v1744 : i32
%v1747 = arith.index_cast %v1721 : index to i32
%v1748 = arith.addi %v1746, %v1747 : i32
%v1749 = arith.truncf %v1738 : f64 to f32
%v1750 = arith.extsi %v1748 : i32 to i64
%v1751 = llvm.getelementptr %v1741[%v1750] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1749, %v1751 : f32, !llvm.ptr
%v1752 = llvm.load %v1706 : !llvm.ptr -> f64
%v1753 = arith.addf %v1752, %v1738 : f64
llvm.store %v1753, %v1706 : f64, !llvm.ptr
%v1754 = arith.addi %v1721, %v1716 : index
cf.br ^b64(%v1754 : index)
^b66(%v1755: index):
%v1756 = arith.constant 0 : i32
%v1757 = llvm.load %v1603 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1758 = llvm.getelementptr %v1603[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1759 = llvm.load %v1758 : !llvm.ptr -> i32
%v1760 = arith.index_cast %v1756 : i32 to index
%v1761 = arith.index_cast %v1759 : i32 to index
%v1762 = arith.constant 1 : index
%v1763 = arith.constant -1 : index
%v1764 = arith.cmpi sle, %v1760, %v1761 : index
%v1765 = arith.select %v1764, %v1762, %v1763 : index
cf.br ^b67(%v1760 : index)
^b67(%v1766: index):
%v1767 = arith.cmpi slt, %v1766, %v1761 : index
%v1768 = arith.cmpi sgt, %v1766, %v1761 : index
%v1769 = arith.select %v1764, %v1767, %v1768 : i1
cf.cond_br %v1769, ^b68(%v1766 : index), ^b69(%v1766 : index)
^b68(%v1770: index):
%v1771 = llvm.load %v1630 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1772 = llvm.getelementptr %v1630[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1773 = llvm.load %v1772 : !llvm.ptr -> !llvm.ptr
%v1774 = llvm.load %v1603 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1775 = llvm.getelementptr %v1603[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1776 = llvm.load %v1775 : !llvm.ptr -> i32
%v1777 = arith.index_cast %v1645 : index to i32
%v1778 = arith.muli %v1777, %v1776 : i32
%v1779 = arith.index_cast %v1770 : index to i32
%v1780 = arith.addi %v1778, %v1779 : i32
%v1781 = arith.extsi %v1780 : i32 to i64
%v1782 = llvm.getelementptr %v1773[%v1781] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1783 = llvm.load %v1782 : !llvm.ptr -> f32
%v1784 = llvm.load %v1706 : !llvm.ptr -> f64
%v1785 = arith.extf %v1783 : f32 to f64
%v1786 = arith.divf %v1785, %v1784 : f64
%v1787 = llvm.load %v1630 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1788 = llvm.getelementptr %v1630[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1789 = llvm.load %v1788 : !llvm.ptr -> !llvm.ptr
%v1790 = llvm.load %v1603 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1791 = llvm.getelementptr %v1603[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1792 = llvm.load %v1791 : !llvm.ptr -> i32
%v1793 = arith.index_cast %v1645 : index to i32
%v1794 = arith.muli %v1793, %v1792 : i32
%v1795 = arith.index_cast %v1770 : index to i32
%v1796 = arith.addi %v1794, %v1795 : i32
%v1797 = arith.truncf %v1786 : f64 to f32
%v1798 = arith.extsi %v1796 : i32 to i64
%v1799 = llvm.getelementptr %v1789[%v1798] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1797, %v1799 : f32, !llvm.ptr
%v1800 = arith.addi %v1770, %v1765 : index
cf.br ^b67(%v1800 : index)
^b69(%v1801: index):
%v1802 = arith.addi %v1645, %v1640 : index
cf.br ^b55(%v1802 : index)
^b57(%v1803: index):
%v1804 = llvm.load %v1630 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1805 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1806 = llvm.extractvalue %v1804[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1807 = llvm.insertvalue %v1806, %v1805[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1808 = llvm.extractvalue %v1804[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1809 = llvm.insertvalue %v1808, %v1807[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1810 = llvm.extractvalue %v1804[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1811 = llvm.insertvalue %v1810, %v1809[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1812 = llvm.extractvalue %v1804[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1813 = llvm.insertvalue %v1812, %v1811[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1814 = llvm.extractvalue %v1804[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1815 = llvm.insertvalue %v1814, %v1813[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1816 = llvm.extractvalue %v1804[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1817 = llvm.insertvalue %v1816, %v1815[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1818 = llvm.mlir.constant(1 : i64) : i64
%v1819 = llvm.alloca %v1818 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1817, %v1819 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1820 = llvm.load %v1819 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1820 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_relu_backward(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1821 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1822 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1823 = llvm.insertvalue %v1822, %v1821[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1824 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1825 = llvm.insertvalue %v1824, %v1823[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1826 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1827 = llvm.insertvalue %v1826, %v1825[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1828 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1829 = llvm.insertvalue %v1828, %v1827[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1830 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1831 = llvm.insertvalue %v1830, %v1829[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1832 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1833 = llvm.insertvalue %v1832, %v1831[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1834 = llvm.mlir.constant(1 : i64) : i64
%v1835 = llvm.alloca %v1834 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1833, %v1835 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1836 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1837 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1838 = llvm.insertvalue %v1837, %v1836[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1839 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1840 = llvm.insertvalue %v1839, %v1838[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1841 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1842 = llvm.insertvalue %v1841, %v1840[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1843 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1844 = llvm.insertvalue %v1843, %v1842[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1845 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1846 = llvm.insertvalue %v1845, %v1844[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1847 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1848 = llvm.insertvalue %v1847, %v1846[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1849 = llvm.mlir.constant(1 : i64) : i64
%v1850 = llvm.alloca %v1849 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1848, %v1850 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1851 = llvm.load %v1835 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1852 = llvm.getelementptr %v1835[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1853 = llvm.load %v1852 : !llvm.ptr -> i32
%v1854 = llvm.load %v1835 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1855 = llvm.getelementptr %v1835[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1856 = llvm.load %v1855 : !llvm.ptr -> i32
%v1857 = llvm.load %v1835 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1858 = llvm.getelementptr %v1835[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1859 = llvm.load %v1858 : !llvm.ptr -> i32
%v1860 = llvm.load %v1835 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1861 = llvm.getelementptr %v1835[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1862 = llvm.load %v1861 : !llvm.ptr -> i32
%v1863 = func.call @tensor_zeros(%v1853, %v1856, %v1859, %v1862) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1864 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1865 = llvm.extractvalue %v1863[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1866 = llvm.insertvalue %v1865, %v1864[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1867 = llvm.extractvalue %v1863[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1868 = llvm.insertvalue %v1867, %v1866[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1869 = llvm.extractvalue %v1863[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1870 = llvm.insertvalue %v1869, %v1868[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1871 = llvm.extractvalue %v1863[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1872 = llvm.insertvalue %v1871, %v1870[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1873 = llvm.extractvalue %v1863[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1874 = llvm.insertvalue %v1873, %v1872[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1875 = llvm.extractvalue %v1863[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1876 = llvm.insertvalue %v1875, %v1874[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1877 = llvm.mlir.constant(1 : i64) : i64
%v1878 = llvm.alloca %v1877 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1876, %v1878 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1879 = llvm.load %v1878 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1880 = llvm.mlir.constant(1 : i64) : i64
%v1881 = llvm.alloca %v1880 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1879, %v1881 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1882 = arith.constant 0 : i32
%v1883 = llvm.load %v1835 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1884 = llvm.getelementptr %v1835[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1885 = llvm.load %v1884 : !llvm.ptr -> i32
%v1886 = arith.index_cast %v1882 : i32 to index
%v1887 = arith.index_cast %v1885 : i32 to index
%v1888 = arith.constant 1 : index
%v1889 = arith.constant -1 : index
%v1890 = arith.cmpi sle, %v1886, %v1887 : index
%v1891 = arith.select %v1890, %v1888, %v1889 : index
cf.br ^b70(%v1886 : index)
^b70(%v1892: index):
%v1893 = arith.cmpi slt, %v1892, %v1887 : index
%v1894 = arith.cmpi sgt, %v1892, %v1887 : index
%v1895 = arith.select %v1890, %v1893, %v1894 : i1
cf.cond_br %v1895, ^b71(%v1892 : index), ^b72(%v1892 : index)
^b71(%v1896: index):
%v1897 = llvm.load %v1835 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1898 = llvm.getelementptr %v1835[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1899 = llvm.load %v1898 : !llvm.ptr -> !llvm.ptr
%v1900 = arith.index_cast %v1896 : index to i64
%v1901 = llvm.getelementptr %v1899[%v1900] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1902 = llvm.load %v1901 : !llvm.ptr -> f32
%v1903 = arith.constant 0.0 : f64
%v1904 = arith.extf %v1902 : f32 to f64
%v1905 = arith.cmpf ogt, %v1904, %v1903 : f64
cf.cond_br %v1905, ^b73, ^b74
^b73:
%v1906 = llvm.load %v1850 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1907 = llvm.getelementptr %v1850[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1908 = llvm.load %v1907 : !llvm.ptr -> !llvm.ptr
%v1909 = arith.index_cast %v1896 : index to i64
%v1910 = llvm.getelementptr %v1908[%v1909] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1911 = llvm.load %v1910 : !llvm.ptr -> f32
%v1912 = llvm.load %v1881 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1913 = llvm.getelementptr %v1881[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1914 = llvm.load %v1913 : !llvm.ptr -> !llvm.ptr
%v1915 = arith.index_cast %v1896 : index to i64
%v1916 = llvm.getelementptr %v1914[%v1915] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1911, %v1916 : f32, !llvm.ptr
cf.br ^b75
^b74:
%v1917 = arith.constant 0.0 : f64
%v1918 = llvm.load %v1881 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1919 = llvm.getelementptr %v1881[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1920 = llvm.load %v1919 : !llvm.ptr -> !llvm.ptr
%v1921 = arith.truncf %v1917 : f64 to f32
%v1922 = arith.index_cast %v1896 : index to i64
%v1923 = llvm.getelementptr %v1920[%v1922] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1921, %v1923 : f32, !llvm.ptr
cf.br ^b75
^b75:
%v1924 = arith.addi %v1896, %v1891 : index
cf.br ^b70(%v1924 : index)
^b72(%v1925: index):
%v1926 = llvm.load %v1881 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1927 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1928 = llvm.extractvalue %v1926[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1929 = llvm.insertvalue %v1928, %v1927[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1930 = llvm.extractvalue %v1926[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1931 = llvm.insertvalue %v1930, %v1929[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1932 = llvm.extractvalue %v1926[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1933 = llvm.insertvalue %v1932, %v1931[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1934 = llvm.extractvalue %v1926[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1935 = llvm.insertvalue %v1934, %v1933[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1936 = llvm.extractvalue %v1926[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1937 = llvm.insertvalue %v1936, %v1935[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1938 = llvm.extractvalue %v1926[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1939 = llvm.insertvalue %v1938, %v1937[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1940 = llvm.mlir.constant(1 : i64) : i64
%v1941 = llvm.alloca %v1940 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1939, %v1941 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1942 = llvm.load %v1941 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1942 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_sigmoid_backward(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1943 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1944 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1945 = llvm.insertvalue %v1944, %v1943[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1946 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1947 = llvm.insertvalue %v1946, %v1945[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1948 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1949 = llvm.insertvalue %v1948, %v1947[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1950 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1951 = llvm.insertvalue %v1950, %v1949[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1952 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1953 = llvm.insertvalue %v1952, %v1951[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1954 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1955 = llvm.insertvalue %v1954, %v1953[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1956 = llvm.mlir.constant(1 : i64) : i64
%v1957 = llvm.alloca %v1956 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1955, %v1957 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1958 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1959 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1960 = llvm.insertvalue %v1959, %v1958[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1961 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1962 = llvm.insertvalue %v1961, %v1960[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1963 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1964 = llvm.insertvalue %v1963, %v1962[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1965 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1966 = llvm.insertvalue %v1965, %v1964[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1967 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1968 = llvm.insertvalue %v1967, %v1966[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1969 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1970 = llvm.insertvalue %v1969, %v1968[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1971 = llvm.mlir.constant(1 : i64) : i64
%v1972 = llvm.alloca %v1971 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1970, %v1972 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1973 = llvm.load %v1957 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1974 = llvm.getelementptr %v1957[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1975 = llvm.load %v1974 : !llvm.ptr -> i32
%v1976 = llvm.load %v1957 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1977 = llvm.getelementptr %v1957[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1978 = llvm.load %v1977 : !llvm.ptr -> i32
%v1979 = llvm.load %v1957 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1980 = llvm.getelementptr %v1957[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1981 = llvm.load %v1980 : !llvm.ptr -> i32
%v1982 = llvm.load %v1957 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1983 = llvm.getelementptr %v1957[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1984 = llvm.load %v1983 : !llvm.ptr -> i32
%v1985 = func.call @tensor_zeros(%v1975, %v1978, %v1981, %v1984) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1986 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1987 = llvm.extractvalue %v1985[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1988 = llvm.insertvalue %v1987, %v1986[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1989 = llvm.extractvalue %v1985[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1990 = llvm.insertvalue %v1989, %v1988[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1991 = llvm.extractvalue %v1985[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1992 = llvm.insertvalue %v1991, %v1990[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1993 = llvm.extractvalue %v1985[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1994 = llvm.insertvalue %v1993, %v1992[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1995 = llvm.extractvalue %v1985[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1996 = llvm.insertvalue %v1995, %v1994[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1997 = llvm.extractvalue %v1985[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1998 = llvm.insertvalue %v1997, %v1996[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1999 = llvm.mlir.constant(1 : i64) : i64
%v2000 = llvm.alloca %v1999 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1998, %v2000 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2001 = llvm.load %v2000 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2002 = llvm.mlir.constant(1 : i64) : i64
%v2003 = llvm.alloca %v2002 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2001, %v2003 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2004 = arith.constant 0 : i32
%v2005 = llvm.load %v1957 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2006 = llvm.getelementptr %v1957[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2007 = llvm.load %v2006 : !llvm.ptr -> i32
%v2008 = arith.index_cast %v2004 : i32 to index
%v2009 = arith.index_cast %v2007 : i32 to index
%v2010 = arith.constant 1 : index
%v2011 = arith.constant -1 : index
%v2012 = arith.cmpi sle, %v2008, %v2009 : index
%v2013 = arith.select %v2012, %v2010, %v2011 : index
cf.br ^b76(%v2008 : index)
^b76(%v2014: index):
%v2015 = arith.cmpi slt, %v2014, %v2009 : index
%v2016 = arith.cmpi sgt, %v2014, %v2009 : index
%v2017 = arith.select %v2012, %v2015, %v2016 : i1
cf.cond_br %v2017, ^b77(%v2014 : index), ^b78(%v2014 : index)
^b77(%v2018: index):
%v2019 = llvm.load %v1957 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2020 = llvm.getelementptr %v1957[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2021 = llvm.load %v2020 : !llvm.ptr -> !llvm.ptr
%v2022 = arith.index_cast %v2018 : index to i64
%v2023 = llvm.getelementptr %v2021[%v2022] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2024 = llvm.load %v2023 : !llvm.ptr -> f32
%v2025 = llvm.mlir.constant(1 : i64) : i64
%v2026 = llvm.alloca %v2025 x f32 : (i64) -> !llvm.ptr
llvm.store %v2024, %v2026 : f32, !llvm.ptr
%v2027 = llvm.load %v1972 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2028 = llvm.getelementptr %v1972[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2029 = llvm.load %v2028 : !llvm.ptr -> !llvm.ptr
%v2030 = arith.index_cast %v2018 : index to i64
%v2031 = llvm.getelementptr %v2029[%v2030] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2032 = llvm.load %v2031 : !llvm.ptr -> f32
%v2033 = llvm.load %v2026 : !llvm.ptr -> f32
%v2034 = arith.mulf %v2032, %v2033 : f32
%v2035 = arith.constant 1.0 : f64
%v2036 = llvm.load %v2026 : !llvm.ptr -> f32
%v2037 = arith.extf %v2036 : f32 to f64
%v2038 = arith.subf %v2035, %v2037 : f64
%v2039 = arith.extf %v2034 : f32 to f64
%v2040 = arith.mulf %v2039, %v2038 : f64
%v2041 = llvm.load %v2003 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2042 = llvm.getelementptr %v2003[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2043 = llvm.load %v2042 : !llvm.ptr -> !llvm.ptr
%v2044 = arith.truncf %v2040 : f64 to f32
%v2045 = arith.index_cast %v2018 : index to i64
%v2046 = llvm.getelementptr %v2043[%v2045] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v2044, %v2046 : f32, !llvm.ptr
%v2047 = arith.addi %v2018, %v2013 : index
cf.br ^b76(%v2047 : index)
^b78(%v2048: index):
%v2049 = llvm.load %v2003 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2050 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2051 = llvm.extractvalue %v2049[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2052 = llvm.insertvalue %v2051, %v2050[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2053 = llvm.extractvalue %v2049[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2054 = llvm.insertvalue %v2053, %v2052[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2055 = llvm.extractvalue %v2049[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2056 = llvm.insertvalue %v2055, %v2054[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2057 = llvm.extractvalue %v2049[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2058 = llvm.insertvalue %v2057, %v2056[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2059 = llvm.extractvalue %v2049[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2060 = llvm.insertvalue %v2059, %v2058[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2061 = llvm.extractvalue %v2049[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2062 = llvm.insertvalue %v2061, %v2060[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2063 = llvm.mlir.constant(1 : i64) : i64
%v2064 = llvm.alloca %v2063 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2062, %v2064 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2065 = llvm.load %v2064 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v2065 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_tanh_backward(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v2066 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2067 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2068 = llvm.insertvalue %v2067, %v2066[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2069 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2070 = llvm.insertvalue %v2069, %v2068[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2071 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2072 = llvm.insertvalue %v2071, %v2070[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2073 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2074 = llvm.insertvalue %v2073, %v2072[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2075 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2076 = llvm.insertvalue %v2075, %v2074[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2077 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2078 = llvm.insertvalue %v2077, %v2076[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2079 = llvm.mlir.constant(1 : i64) : i64
%v2080 = llvm.alloca %v2079 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2078, %v2080 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2081 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2082 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2083 = llvm.insertvalue %v2082, %v2081[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2084 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2085 = llvm.insertvalue %v2084, %v2083[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2086 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2087 = llvm.insertvalue %v2086, %v2085[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2088 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2089 = llvm.insertvalue %v2088, %v2087[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2090 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2091 = llvm.insertvalue %v2090, %v2089[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2092 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2093 = llvm.insertvalue %v2092, %v2091[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2094 = llvm.mlir.constant(1 : i64) : i64
%v2095 = llvm.alloca %v2094 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2093, %v2095 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2096 = llvm.load %v2080 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2097 = llvm.getelementptr %v2080[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2098 = llvm.load %v2097 : !llvm.ptr -> i32
%v2099 = llvm.load %v2080 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2100 = llvm.getelementptr %v2080[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2101 = llvm.load %v2100 : !llvm.ptr -> i32
%v2102 = llvm.load %v2080 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2103 = llvm.getelementptr %v2080[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2104 = llvm.load %v2103 : !llvm.ptr -> i32
%v2105 = llvm.load %v2080 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2106 = llvm.getelementptr %v2080[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2107 = llvm.load %v2106 : !llvm.ptr -> i32
%v2108 = func.call @tensor_zeros(%v2098, %v2101, %v2104, %v2107) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2109 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2110 = llvm.extractvalue %v2108[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2111 = llvm.insertvalue %v2110, %v2109[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2112 = llvm.extractvalue %v2108[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2113 = llvm.insertvalue %v2112, %v2111[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2114 = llvm.extractvalue %v2108[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2115 = llvm.insertvalue %v2114, %v2113[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2116 = llvm.extractvalue %v2108[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2117 = llvm.insertvalue %v2116, %v2115[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2118 = llvm.extractvalue %v2108[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2119 = llvm.insertvalue %v2118, %v2117[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2120 = llvm.extractvalue %v2108[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2121 = llvm.insertvalue %v2120, %v2119[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2122 = llvm.mlir.constant(1 : i64) : i64
%v2123 = llvm.alloca %v2122 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2121, %v2123 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2124 = llvm.load %v2123 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2125 = llvm.mlir.constant(1 : i64) : i64
%v2126 = llvm.alloca %v2125 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2124, %v2126 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2127 = arith.constant 0 : i32
%v2128 = llvm.load %v2080 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2129 = llvm.getelementptr %v2080[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2130 = llvm.load %v2129 : !llvm.ptr -> i32
%v2131 = arith.index_cast %v2127 : i32 to index
%v2132 = arith.index_cast %v2130 : i32 to index
%v2133 = arith.constant 1 : index
%v2134 = arith.constant -1 : index
%v2135 = arith.cmpi sle, %v2131, %v2132 : index
%v2136 = arith.select %v2135, %v2133, %v2134 : index
cf.br ^b79(%v2131 : index)
^b79(%v2137: index):
%v2138 = arith.cmpi slt, %v2137, %v2132 : index
%v2139 = arith.cmpi sgt, %v2137, %v2132 : index
%v2140 = arith.select %v2135, %v2138, %v2139 : i1
cf.cond_br %v2140, ^b80(%v2137 : index), ^b81(%v2137 : index)
^b80(%v2141: index):
%v2142 = llvm.load %v2080 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2143 = llvm.getelementptr %v2080[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2144 = llvm.load %v2143 : !llvm.ptr -> !llvm.ptr
%v2145 = arith.index_cast %v2141 : index to i64
%v2146 = llvm.getelementptr %v2144[%v2145] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2147 = llvm.load %v2146 : !llvm.ptr -> f32
%v2148 = llvm.load %v2095 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2149 = llvm.getelementptr %v2095[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2150 = llvm.load %v2149 : !llvm.ptr -> !llvm.ptr
%v2151 = arith.index_cast %v2141 : index to i64
%v2152 = llvm.getelementptr %v2150[%v2151] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2153 = llvm.load %v2152 : !llvm.ptr -> f32
%v2154 = arith.constant 1.0 : f64
%v2155 = arith.mulf %v2147, %v2147 : f32
%v2156 = arith.extf %v2155 : f32 to f64
%v2157 = arith.subf %v2154, %v2156 : f64
%v2158 = arith.extf %v2153 : f32 to f64
%v2159 = arith.mulf %v2158, %v2157 : f64
%v2160 = llvm.load %v2126 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2161 = llvm.getelementptr %v2126[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2162 = llvm.load %v2161 : !llvm.ptr -> !llvm.ptr
%v2163 = arith.truncf %v2159 : f64 to f32
%v2164 = arith.index_cast %v2141 : index to i64
%v2165 = llvm.getelementptr %v2162[%v2164] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v2163, %v2165 : f32, !llvm.ptr
%v2166 = arith.addi %v2141, %v2136 : index
cf.br ^b79(%v2166 : index)
^b81(%v2167: index):
%v2168 = llvm.load %v2126 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2169 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2170 = llvm.extractvalue %v2168[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2171 = llvm.insertvalue %v2170, %v2169[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2172 = llvm.extractvalue %v2168[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2173 = llvm.insertvalue %v2172, %v2171[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2174 = llvm.extractvalue %v2168[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2175 = llvm.insertvalue %v2174, %v2173[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2176 = llvm.extractvalue %v2168[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2177 = llvm.insertvalue %v2176, %v2175[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2178 = llvm.extractvalue %v2168[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2179 = llvm.insertvalue %v2178, %v2177[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2180 = llvm.extractvalue %v2168[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2181 = llvm.insertvalue %v2180, %v2179[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2182 = llvm.mlir.constant(1 : i64) : i64
%v2183 = llvm.alloca %v2182 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2181, %v2183 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2184 = llvm.load %v2183 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v2184 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_mul_backward_a(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg2: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v2185 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2186 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2187 = llvm.insertvalue %v2186, %v2185[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2188 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2189 = llvm.insertvalue %v2188, %v2187[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2190 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2191 = llvm.insertvalue %v2190, %v2189[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2192 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2193 = llvm.insertvalue %v2192, %v2191[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2194 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2195 = llvm.insertvalue %v2194, %v2193[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2196 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2197 = llvm.insertvalue %v2196, %v2195[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2198 = llvm.mlir.constant(1 : i64) : i64
%v2199 = llvm.alloca %v2198 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2197, %v2199 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2200 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2201 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2202 = llvm.insertvalue %v2201, %v2200[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2203 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2204 = llvm.insertvalue %v2203, %v2202[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2205 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2206 = llvm.insertvalue %v2205, %v2204[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2207 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2208 = llvm.insertvalue %v2207, %v2206[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2209 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2210 = llvm.insertvalue %v2209, %v2208[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2211 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2212 = llvm.insertvalue %v2211, %v2210[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2213 = llvm.mlir.constant(1 : i64) : i64
%v2214 = llvm.alloca %v2213 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2212, %v2214 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2215 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2216 = llvm.extractvalue %arg2[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2217 = llvm.insertvalue %v2216, %v2215[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2218 = llvm.extractvalue %arg2[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2219 = llvm.insertvalue %v2218, %v2217[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2220 = llvm.extractvalue %arg2[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2221 = llvm.insertvalue %v2220, %v2219[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2222 = llvm.extractvalue %arg2[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2223 = llvm.insertvalue %v2222, %v2221[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2224 = llvm.extractvalue %arg2[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2225 = llvm.insertvalue %v2224, %v2223[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2226 = llvm.extractvalue %arg2[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2227 = llvm.insertvalue %v2226, %v2225[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2228 = llvm.mlir.constant(1 : i64) : i64
%v2229 = llvm.alloca %v2228 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2227, %v2229 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2230 = llvm.load %v2199 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2231 = llvm.getelementptr %v2199[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2232 = llvm.load %v2231 : !llvm.ptr -> i32
%v2233 = llvm.load %v2199 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2234 = llvm.getelementptr %v2199[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2235 = llvm.load %v2234 : !llvm.ptr -> i32
%v2236 = llvm.load %v2199 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2237 = llvm.getelementptr %v2199[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2238 = llvm.load %v2237 : !llvm.ptr -> i32
%v2239 = llvm.load %v2199 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2240 = llvm.getelementptr %v2199[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2241 = llvm.load %v2240 : !llvm.ptr -> i32
%v2242 = func.call @tensor_zeros(%v2232, %v2235, %v2238, %v2241) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2243 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2244 = llvm.extractvalue %v2242[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2245 = llvm.insertvalue %v2244, %v2243[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2246 = llvm.extractvalue %v2242[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2247 = llvm.insertvalue %v2246, %v2245[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2248 = llvm.extractvalue %v2242[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2249 = llvm.insertvalue %v2248, %v2247[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2250 = llvm.extractvalue %v2242[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2251 = llvm.insertvalue %v2250, %v2249[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2252 = llvm.extractvalue %v2242[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2253 = llvm.insertvalue %v2252, %v2251[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2254 = llvm.extractvalue %v2242[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2255 = llvm.insertvalue %v2254, %v2253[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2256 = llvm.mlir.constant(1 : i64) : i64
%v2257 = llvm.alloca %v2256 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2255, %v2257 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2258 = llvm.load %v2257 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2259 = llvm.mlir.constant(1 : i64) : i64
%v2260 = llvm.alloca %v2259 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2258, %v2260 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2261 = arith.constant 0 : i32
%v2262 = llvm.load %v2199 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2263 = llvm.getelementptr %v2199[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2264 = llvm.load %v2263 : !llvm.ptr -> i32
%v2265 = arith.index_cast %v2261 : i32 to index
%v2266 = arith.index_cast %v2264 : i32 to index
%v2267 = arith.constant 1 : index
%v2268 = arith.constant -1 : index
%v2269 = arith.cmpi sle, %v2265, %v2266 : index
%v2270 = arith.select %v2269, %v2267, %v2268 : index
cf.br ^b82(%v2265 : index)
^b82(%v2271: index):
%v2272 = arith.cmpi slt, %v2271, %v2266 : index
%v2273 = arith.cmpi sgt, %v2271, %v2266 : index
%v2274 = arith.select %v2269, %v2272, %v2273 : i1
cf.cond_br %v2274, ^b83(%v2271 : index), ^b84(%v2271 : index)
^b83(%v2275: index):
%v2276 = llvm.load %v2229 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2277 = llvm.getelementptr %v2229[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2278 = llvm.load %v2277 : !llvm.ptr -> !llvm.ptr
%v2279 = arith.index_cast %v2275 : index to i64
%v2280 = llvm.getelementptr %v2278[%v2279] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2281 = llvm.load %v2280 : !llvm.ptr -> f32
%v2282 = llvm.load %v2214 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2283 = llvm.getelementptr %v2214[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2284 = llvm.load %v2283 : !llvm.ptr -> !llvm.ptr
%v2285 = arith.index_cast %v2275 : index to i64
%v2286 = llvm.getelementptr %v2284[%v2285] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2287 = llvm.load %v2286 : !llvm.ptr -> f32
%v2288 = arith.mulf %v2281, %v2287 : f32
%v2289 = llvm.load %v2260 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2290 = llvm.getelementptr %v2260[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2291 = llvm.load %v2290 : !llvm.ptr -> !llvm.ptr
%v2292 = arith.index_cast %v2275 : index to i64
%v2293 = llvm.getelementptr %v2291[%v2292] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v2288, %v2293 : f32, !llvm.ptr
%v2294 = arith.addi %v2275, %v2270 : index
cf.br ^b82(%v2294 : index)
^b84(%v2295: index):
%v2296 = llvm.load %v2260 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2297 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2298 = llvm.extractvalue %v2296[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2299 = llvm.insertvalue %v2298, %v2297[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2300 = llvm.extractvalue %v2296[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2301 = llvm.insertvalue %v2300, %v2299[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2302 = llvm.extractvalue %v2296[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2303 = llvm.insertvalue %v2302, %v2301[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2304 = llvm.extractvalue %v2296[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2305 = llvm.insertvalue %v2304, %v2303[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2306 = llvm.extractvalue %v2296[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2307 = llvm.insertvalue %v2306, %v2305[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2308 = llvm.extractvalue %v2296[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2309 = llvm.insertvalue %v2308, %v2307[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2310 = llvm.mlir.constant(1 : i64) : i64
%v2311 = llvm.alloca %v2310 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2309, %v2311 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2312 = llvm.load %v2311 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v2312 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_mul_backward_b(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg2: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v2313 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2314 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2315 = llvm.insertvalue %v2314, %v2313[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2316 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2317 = llvm.insertvalue %v2316, %v2315[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2318 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2319 = llvm.insertvalue %v2318, %v2317[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2320 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2321 = llvm.insertvalue %v2320, %v2319[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2322 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2323 = llvm.insertvalue %v2322, %v2321[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2324 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2325 = llvm.insertvalue %v2324, %v2323[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2326 = llvm.mlir.constant(1 : i64) : i64
%v2327 = llvm.alloca %v2326 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2325, %v2327 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2328 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2329 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2330 = llvm.insertvalue %v2329, %v2328[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2331 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2332 = llvm.insertvalue %v2331, %v2330[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2333 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2334 = llvm.insertvalue %v2333, %v2332[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2335 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2336 = llvm.insertvalue %v2335, %v2334[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2337 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2338 = llvm.insertvalue %v2337, %v2336[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2339 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2340 = llvm.insertvalue %v2339, %v2338[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2341 = llvm.mlir.constant(1 : i64) : i64
%v2342 = llvm.alloca %v2341 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2340, %v2342 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2343 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2344 = llvm.extractvalue %arg2[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2345 = llvm.insertvalue %v2344, %v2343[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2346 = llvm.extractvalue %arg2[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2347 = llvm.insertvalue %v2346, %v2345[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2348 = llvm.extractvalue %arg2[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2349 = llvm.insertvalue %v2348, %v2347[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2350 = llvm.extractvalue %arg2[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2351 = llvm.insertvalue %v2350, %v2349[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2352 = llvm.extractvalue %arg2[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2353 = llvm.insertvalue %v2352, %v2351[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2354 = llvm.extractvalue %arg2[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2355 = llvm.insertvalue %v2354, %v2353[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2356 = llvm.mlir.constant(1 : i64) : i64
%v2357 = llvm.alloca %v2356 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2355, %v2357 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2358 = llvm.load %v2342 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2359 = llvm.getelementptr %v2342[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2360 = llvm.load %v2359 : !llvm.ptr -> i32
%v2361 = llvm.load %v2342 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2362 = llvm.getelementptr %v2342[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2363 = llvm.load %v2362 : !llvm.ptr -> i32
%v2364 = llvm.load %v2342 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2365 = llvm.getelementptr %v2342[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2366 = llvm.load %v2365 : !llvm.ptr -> i32
%v2367 = llvm.load %v2342 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2368 = llvm.getelementptr %v2342[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2369 = llvm.load %v2368 : !llvm.ptr -> i32
%v2370 = func.call @tensor_zeros(%v2360, %v2363, %v2366, %v2369) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2371 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2372 = llvm.extractvalue %v2370[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2373 = llvm.insertvalue %v2372, %v2371[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2374 = llvm.extractvalue %v2370[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2375 = llvm.insertvalue %v2374, %v2373[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2376 = llvm.extractvalue %v2370[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2377 = llvm.insertvalue %v2376, %v2375[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2378 = llvm.extractvalue %v2370[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2379 = llvm.insertvalue %v2378, %v2377[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2380 = llvm.extractvalue %v2370[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2381 = llvm.insertvalue %v2380, %v2379[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2382 = llvm.extractvalue %v2370[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2383 = llvm.insertvalue %v2382, %v2381[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2384 = llvm.mlir.constant(1 : i64) : i64
%v2385 = llvm.alloca %v2384 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2383, %v2385 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2386 = llvm.load %v2385 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2387 = llvm.mlir.constant(1 : i64) : i64
%v2388 = llvm.alloca %v2387 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2386, %v2388 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2389 = arith.constant 0 : i32
%v2390 = llvm.load %v2342 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2391 = llvm.getelementptr %v2342[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2392 = llvm.load %v2391 : !llvm.ptr -> i32
%v2393 = arith.index_cast %v2389 : i32 to index
%v2394 = arith.index_cast %v2392 : i32 to index
%v2395 = arith.constant 1 : index
%v2396 = arith.constant -1 : index
%v2397 = arith.cmpi sle, %v2393, %v2394 : index
%v2398 = arith.select %v2397, %v2395, %v2396 : index
cf.br ^b85(%v2393 : index)
^b85(%v2399: index):
%v2400 = arith.cmpi slt, %v2399, %v2394 : index
%v2401 = arith.cmpi sgt, %v2399, %v2394 : index
%v2402 = arith.select %v2397, %v2400, %v2401 : i1
cf.cond_br %v2402, ^b86(%v2399 : index), ^b87(%v2399 : index)
^b86(%v2403: index):
%v2404 = llvm.load %v2357 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2405 = llvm.getelementptr %v2357[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2406 = llvm.load %v2405 : !llvm.ptr -> !llvm.ptr
%v2407 = arith.index_cast %v2403 : index to i64
%v2408 = llvm.getelementptr %v2406[%v2407] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2409 = llvm.load %v2408 : !llvm.ptr -> f32
%v2410 = llvm.load %v2327 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2411 = llvm.getelementptr %v2327[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2412 = llvm.load %v2411 : !llvm.ptr -> !llvm.ptr
%v2413 = arith.index_cast %v2403 : index to i64
%v2414 = llvm.getelementptr %v2412[%v2413] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2415 = llvm.load %v2414 : !llvm.ptr -> f32
%v2416 = arith.mulf %v2409, %v2415 : f32
%v2417 = llvm.load %v2388 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2418 = llvm.getelementptr %v2388[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2419 = llvm.load %v2418 : !llvm.ptr -> !llvm.ptr
%v2420 = arith.index_cast %v2403 : index to i64
%v2421 = llvm.getelementptr %v2419[%v2420] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v2416, %v2421 : f32, !llvm.ptr
%v2422 = arith.addi %v2403, %v2398 : index
cf.br ^b85(%v2422 : index)
^b87(%v2423: index):
%v2424 = llvm.load %v2388 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2425 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2426 = llvm.extractvalue %v2424[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2427 = llvm.insertvalue %v2426, %v2425[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2428 = llvm.extractvalue %v2424[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2429 = llvm.insertvalue %v2428, %v2427[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2430 = llvm.extractvalue %v2424[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2431 = llvm.insertvalue %v2430, %v2429[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2432 = llvm.extractvalue %v2424[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2433 = llvm.insertvalue %v2432, %v2431[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2434 = llvm.extractvalue %v2424[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2435 = llvm.insertvalue %v2434, %v2433[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2436 = llvm.extractvalue %v2424[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2437 = llvm.insertvalue %v2436, %v2435[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2438 = llvm.mlir.constant(1 : i64) : i64
%v2439 = llvm.alloca %v2438 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2437, %v2439 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2440 = llvm.load %v2439 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v2440 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_broadcast_add(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v2441 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2442 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2443 = llvm.insertvalue %v2442, %v2441[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2444 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2445 = llvm.insertvalue %v2444, %v2443[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2446 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2447 = llvm.insertvalue %v2446, %v2445[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2448 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2449 = llvm.insertvalue %v2448, %v2447[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2450 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2451 = llvm.insertvalue %v2450, %v2449[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2452 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2453 = llvm.insertvalue %v2452, %v2451[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2454 = llvm.mlir.constant(1 : i64) : i64
%v2455 = llvm.alloca %v2454 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2453, %v2455 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2456 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2457 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2458 = llvm.insertvalue %v2457, %v2456[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2459 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2460 = llvm.insertvalue %v2459, %v2458[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2461 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2462 = llvm.insertvalue %v2461, %v2460[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2463 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2464 = llvm.insertvalue %v2463, %v2462[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2465 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2466 = llvm.insertvalue %v2465, %v2464[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2467 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2468 = llvm.insertvalue %v2467, %v2466[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2469 = llvm.mlir.constant(1 : i64) : i64
%v2470 = llvm.alloca %v2469 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2468, %v2470 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2471 = llvm.load %v2455 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2472 = llvm.getelementptr %v2455[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2473 = llvm.load %v2472 : !llvm.ptr -> i32
%v2474 = llvm.load %v2455 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2475 = llvm.getelementptr %v2455[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2476 = llvm.load %v2475 : !llvm.ptr -> i32
%v2477 = llvm.load %v2455 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2478 = llvm.getelementptr %v2455[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2479 = llvm.load %v2478 : !llvm.ptr -> i32
%v2480 = llvm.load %v2455 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2481 = llvm.getelementptr %v2455[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2482 = llvm.load %v2481 : !llvm.ptr -> i32
%v2483 = func.call @tensor_zeros(%v2473, %v2476, %v2479, %v2482) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2484 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2485 = llvm.extractvalue %v2483[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2486 = llvm.insertvalue %v2485, %v2484[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2487 = llvm.extractvalue %v2483[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2488 = llvm.insertvalue %v2487, %v2486[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2489 = llvm.extractvalue %v2483[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2490 = llvm.insertvalue %v2489, %v2488[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2491 = llvm.extractvalue %v2483[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2492 = llvm.insertvalue %v2491, %v2490[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2493 = llvm.extractvalue %v2483[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2494 = llvm.insertvalue %v2493, %v2492[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2495 = llvm.extractvalue %v2483[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2496 = llvm.insertvalue %v2495, %v2494[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2497 = llvm.mlir.constant(1 : i64) : i64
%v2498 = llvm.alloca %v2497 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2496, %v2498 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2499 = llvm.load %v2498 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2500 = llvm.mlir.constant(1 : i64) : i64
%v2501 = llvm.alloca %v2500 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2499, %v2501 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2502 = arith.constant 0 : i32
%v2503 = llvm.load %v2455 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2504 = llvm.getelementptr %v2455[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2505 = llvm.load %v2504 : !llvm.ptr -> i32
%v2506 = arith.index_cast %v2502 : i32 to index
%v2507 = arith.index_cast %v2505 : i32 to index
%v2508 = arith.constant 1 : index
%v2509 = arith.constant -1 : index
%v2510 = arith.cmpi sle, %v2506, %v2507 : index
%v2511 = arith.select %v2510, %v2508, %v2509 : index
cf.br ^b88(%v2506 : index)
^b88(%v2512: index):
%v2513 = arith.cmpi slt, %v2512, %v2507 : index
%v2514 = arith.cmpi sgt, %v2512, %v2507 : index
%v2515 = arith.select %v2510, %v2513, %v2514 : i1
cf.cond_br %v2515, ^b89(%v2512 : index), ^b90(%v2512 : index)
^b89(%v2516: index):
%v2517 = arith.constant 0 : i32
%v2518 = llvm.mlir.constant(1 : i64) : i64
%v2519 = llvm.alloca %v2518 x i32 : (i64) -> !llvm.ptr
llvm.store %v2517, %v2519 : i32, !llvm.ptr
%v2520 = llvm.load %v2470 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2521 = llvm.getelementptr %v2470[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2522 = llvm.load %v2521 : !llvm.ptr -> i32
%v2523 = arith.constant 1 : i32
%v2524 = arith.cmpi sgt, %v2522, %v2523 : i32
cf.cond_br %v2524, ^b91, ^b92
^b91:
%v2525 = arith.index_cast %v2516 : index to i32
llvm.store %v2525, %v2519 : i32, !llvm.ptr
cf.br ^b93
^b92:
cf.br ^b93
^b93:
%v2526 = arith.constant 0 : i32
%v2527 = llvm.load %v2455 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2528 = llvm.getelementptr %v2455[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2529 = llvm.load %v2528 : !llvm.ptr -> i32
%v2530 = arith.index_cast %v2526 : i32 to index
%v2531 = arith.index_cast %v2529 : i32 to index
%v2532 = arith.constant 1 : index
%v2533 = arith.constant -1 : index
%v2534 = arith.cmpi sle, %v2530, %v2531 : index
%v2535 = arith.select %v2534, %v2532, %v2533 : index
cf.br ^b94(%v2530 : index)
^b94(%v2536: index):
%v2537 = arith.cmpi slt, %v2536, %v2531 : index
%v2538 = arith.cmpi sgt, %v2536, %v2531 : index
%v2539 = arith.select %v2534, %v2537, %v2538 : i1
cf.cond_br %v2539, ^b95(%v2536 : index), ^b96(%v2536 : index)
^b95(%v2540: index):
%v2541 = arith.constant 0 : i32
%v2542 = llvm.mlir.constant(1 : i64) : i64
%v2543 = llvm.alloca %v2542 x i32 : (i64) -> !llvm.ptr
llvm.store %v2541, %v2543 : i32, !llvm.ptr
%v2544 = llvm.load %v2470 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2545 = llvm.getelementptr %v2470[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2546 = llvm.load %v2545 : !llvm.ptr -> i32
%v2547 = arith.constant 1 : i32
%v2548 = arith.cmpi sgt, %v2546, %v2547 : i32
cf.cond_br %v2548, ^b97, ^b98
^b97:
%v2549 = arith.index_cast %v2540 : index to i32
llvm.store %v2549, %v2543 : i32, !llvm.ptr
cf.br ^b99
^b98:
cf.br ^b99
^b99:
%v2550 = llvm.load %v2455 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2551 = arith.constant 0 : i32
%v2552 = arith.constant 0 : i32
%v2553 = arith.index_cast %v2516 : index to i32
%v2554 = arith.index_cast %v2540 : index to i32
%v2555 = func.call @tensor_idx(%v2550, %v2553, %v2554, %v2551, %v2552) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, i32, i32, i32, i32) -> i32
%v2556 = llvm.load %v2470 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2557 = llvm.load %v2519 : !llvm.ptr -> i32
%v2558 = llvm.load %v2543 : !llvm.ptr -> i32
%v2559 = arith.constant 0 : i32
%v2560 = arith.constant 0 : i32
%v2561 = func.call @tensor_idx(%v2556, %v2557, %v2558, %v2559, %v2560) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, i32, i32, i32, i32) -> i32
%v2562 = llvm.load %v2455 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2563 = llvm.getelementptr %v2455[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2564 = llvm.load %v2563 : !llvm.ptr -> !llvm.ptr
%v2565 = arith.extsi %v2555 : i32 to i64
%v2566 = llvm.getelementptr %v2564[%v2565] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2567 = llvm.load %v2566 : !llvm.ptr -> f32
%v2568 = llvm.load %v2470 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2569 = llvm.getelementptr %v2470[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2570 = llvm.load %v2569 : !llvm.ptr -> !llvm.ptr
%v2571 = arith.extsi %v2561 : i32 to i64
%v2572 = llvm.getelementptr %v2570[%v2571] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2573 = llvm.load %v2572 : !llvm.ptr -> f32
%v2574 = arith.addf %v2567, %v2573 : f32
%v2575 = llvm.load %v2501 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2576 = llvm.getelementptr %v2501[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2577 = llvm.load %v2576 : !llvm.ptr -> !llvm.ptr
%v2578 = arith.extsi %v2555 : i32 to i64
%v2579 = llvm.getelementptr %v2577[%v2578] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v2574, %v2579 : f32, !llvm.ptr
%v2580 = arith.addi %v2540, %v2535 : index
cf.br ^b94(%v2580 : index)
^b96(%v2581: index):
%v2582 = arith.addi %v2516, %v2511 : index
cf.br ^b88(%v2582 : index)
^b90(%v2583: index):
%v2584 = llvm.load %v2501 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2585 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2586 = llvm.extractvalue %v2584[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2587 = llvm.insertvalue %v2586, %v2585[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2588 = llvm.extractvalue %v2584[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2589 = llvm.insertvalue %v2588, %v2587[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2590 = llvm.extractvalue %v2584[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2591 = llvm.insertvalue %v2590, %v2589[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2592 = llvm.extractvalue %v2584[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2593 = llvm.insertvalue %v2592, %v2591[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2594 = llvm.extractvalue %v2584[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2595 = llvm.insertvalue %v2594, %v2593[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2596 = llvm.extractvalue %v2584[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2597 = llvm.insertvalue %v2596, %v2595[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2598 = llvm.mlir.constant(1 : i64) : i64
%v2599 = llvm.alloca %v2598 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2597, %v2599 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2600 = llvm.load %v2599 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v2600 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_matmul(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v2601 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2602 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2603 = llvm.insertvalue %v2602, %v2601[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2604 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2605 = llvm.insertvalue %v2604, %v2603[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2606 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2607 = llvm.insertvalue %v2606, %v2605[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2608 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2609 = llvm.insertvalue %v2608, %v2607[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2610 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2611 = llvm.insertvalue %v2610, %v2609[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2612 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2613 = llvm.insertvalue %v2612, %v2611[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2614 = llvm.mlir.constant(1 : i64) : i64
%v2615 = llvm.alloca %v2614 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2613, %v2615 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2616 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2617 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2618 = llvm.insertvalue %v2617, %v2616[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2619 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2620 = llvm.insertvalue %v2619, %v2618[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2621 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2622 = llvm.insertvalue %v2621, %v2620[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2623 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2624 = llvm.insertvalue %v2623, %v2622[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2625 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2626 = llvm.insertvalue %v2625, %v2624[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2627 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2628 = llvm.insertvalue %v2627, %v2626[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2629 = llvm.mlir.constant(1 : i64) : i64
%v2630 = llvm.alloca %v2629 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2628, %v2630 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2631 = llvm.load %v2615 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2632 = llvm.getelementptr %v2615[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2633 = llvm.load %v2632 : !llvm.ptr -> i32
%v2634 = llvm.load %v2615 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2635 = llvm.getelementptr %v2615[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2636 = llvm.load %v2635 : !llvm.ptr -> i32
%v2637 = llvm.load %v2630 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2638 = llvm.getelementptr %v2630[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2639 = llvm.load %v2638 : !llvm.ptr -> i32
%v2640 = arith.constant 1 : i32
%v2641 = arith.constant 1 : i32
%v2642 = func.call @tensor_zeros(%v2633, %v2639, %v2640, %v2641) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2643 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2644 = llvm.extractvalue %v2642[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2645 = llvm.insertvalue %v2644, %v2643[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2646 = llvm.extractvalue %v2642[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2647 = llvm.insertvalue %v2646, %v2645[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2648 = llvm.extractvalue %v2642[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2649 = llvm.insertvalue %v2648, %v2647[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2650 = llvm.extractvalue %v2642[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2651 = llvm.insertvalue %v2650, %v2649[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2652 = llvm.extractvalue %v2642[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2653 = llvm.insertvalue %v2652, %v2651[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2654 = llvm.extractvalue %v2642[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2655 = llvm.insertvalue %v2654, %v2653[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2656 = llvm.mlir.constant(1 : i64) : i64
%v2657 = llvm.alloca %v2656 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2655, %v2657 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2658 = llvm.load %v2657 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2659 = llvm.mlir.constant(1 : i64) : i64
%v2660 = llvm.alloca %v2659 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2658, %v2660 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2661 = arith.constant 0 : i32
%v2662 = arith.index_cast %v2661 : i32 to index
%v2663 = arith.index_cast %v2633 : i32 to index
%v2664 = arith.constant 1 : index
%v2665 = arith.constant -1 : index
%v2666 = arith.cmpi sle, %v2662, %v2663 : index
%v2667 = arith.select %v2666, %v2664, %v2665 : index
cf.br ^b100(%v2662 : index)
^b100(%v2668: index):
%v2669 = arith.cmpi slt, %v2668, %v2663 : index
%v2670 = arith.cmpi sgt, %v2668, %v2663 : index
%v2671 = arith.select %v2666, %v2669, %v2670 : i1
cf.cond_br %v2671, ^b101(%v2668 : index), ^b102(%v2668 : index)
^b101(%v2672: index):
%v2673 = arith.constant 0 : i32
%v2674 = arith.index_cast %v2673 : i32 to index
%v2675 = arith.index_cast %v2639 : i32 to index
%v2676 = arith.constant 1 : index
%v2677 = arith.constant -1 : index
%v2678 = arith.cmpi sle, %v2674, %v2675 : index
%v2679 = arith.select %v2678, %v2676, %v2677 : index
cf.br ^b103(%v2674 : index)
^b103(%v2680: index):
%v2681 = arith.cmpi slt, %v2680, %v2675 : index
%v2682 = arith.cmpi sgt, %v2680, %v2675 : index
%v2683 = arith.select %v2678, %v2681, %v2682 : i1
cf.cond_br %v2683, ^b104(%v2680 : index), ^b105(%v2680 : index)
^b104(%v2684: index):
%v2685 = arith.constant 0.0 : f64
%v2686 = arith.truncf %v2685 : f64 to f32
%v2687 = llvm.mlir.constant(1 : i64) : i64
%v2688 = llvm.alloca %v2687 x f32 : (i64) -> !llvm.ptr
llvm.store %v2686, %v2688 : f32, !llvm.ptr
%v2689 = arith.constant 0 : i32
%v2690 = arith.index_cast %v2689 : i32 to index
%v2691 = arith.index_cast %v2636 : i32 to index
%v2692 = arith.constant 1 : index
%v2693 = arith.constant -1 : index
%v2694 = arith.cmpi sle, %v2690, %v2691 : index
%v2695 = arith.select %v2694, %v2692, %v2693 : index
cf.br ^b106(%v2690 : index)
^b106(%v2696: index):
%v2697 = arith.cmpi slt, %v2696, %v2691 : index
%v2698 = arith.cmpi sgt, %v2696, %v2691 : index
%v2699 = arith.select %v2694, %v2697, %v2698 : i1
cf.cond_br %v2699, ^b107(%v2696 : index), ^b108(%v2696 : index)
^b107(%v2700: index):
%v2701 = llvm.load %v2688 : !llvm.ptr -> f32
%v2702 = llvm.load %v2615 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2703 = llvm.getelementptr %v2615[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2704 = llvm.load %v2703 : !llvm.ptr -> !llvm.ptr
%v2705 = arith.index_cast %v2672 : index to i32
%v2706 = arith.muli %v2705, %v2636 : i32
%v2707 = arith.index_cast %v2700 : index to i32
%v2708 = arith.addi %v2706, %v2707 : i32
%v2709 = arith.extsi %v2708 : i32 to i64
%v2710 = llvm.getelementptr %v2704[%v2709] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2711 = llvm.load %v2710 : !llvm.ptr -> f32
%v2712 = llvm.load %v2630 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2713 = llvm.getelementptr %v2630[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2714 = llvm.load %v2713 : !llvm.ptr -> !llvm.ptr
%v2715 = arith.index_cast %v2700 : index to i32
%v2716 = arith.muli %v2715, %v2639 : i32
%v2717 = arith.index_cast %v2684 : index to i32
%v2718 = arith.addi %v2716, %v2717 : i32
%v2719 = arith.extsi %v2718 : i32 to i64
%v2720 = llvm.getelementptr %v2714[%v2719] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2721 = llvm.load %v2720 : !llvm.ptr -> f32
%v2722 = llvm.intr.fmuladd(%v2711, %v2721, %v2701) : (f32, f32, f32) -> f32
llvm.store %v2722, %v2688 : f32, !llvm.ptr
%v2723 = arith.addi %v2700, %v2695 : index
cf.br ^b106(%v2723 : index)
^b108(%v2724: index):
%v2725 = llvm.load %v2688 : !llvm.ptr -> f32
%v2726 = llvm.load %v2660 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2727 = llvm.getelementptr %v2660[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2728 = llvm.load %v2727 : !llvm.ptr -> !llvm.ptr
%v2729 = arith.index_cast %v2672 : index to i32
%v2730 = arith.muli %v2729, %v2639 : i32
%v2731 = arith.index_cast %v2684 : index to i32
%v2732 = arith.addi %v2730, %v2731 : i32
%v2733 = arith.extsi %v2732 : i32 to i64
%v2734 = llvm.getelementptr %v2728[%v2733] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v2725, %v2734 : f32, !llvm.ptr
%v2735 = arith.addi %v2684, %v2679 : index
cf.br ^b103(%v2735 : index)
^b105(%v2736: index):
%v2737 = arith.addi %v2672, %v2667 : index
cf.br ^b100(%v2737 : index)
^b102(%v2738: index):
%v2739 = llvm.load %v2660 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2740 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2741 = llvm.extractvalue %v2739[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2742 = llvm.insertvalue %v2741, %v2740[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2743 = llvm.extractvalue %v2739[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2744 = llvm.insertvalue %v2743, %v2742[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2745 = llvm.extractvalue %v2739[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2746 = llvm.insertvalue %v2745, %v2744[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2747 = llvm.extractvalue %v2739[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2748 = llvm.insertvalue %v2747, %v2746[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2749 = llvm.extractvalue %v2739[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2750 = llvm.insertvalue %v2749, %v2748[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2751 = llvm.extractvalue %v2739[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2752 = llvm.insertvalue %v2751, %v2750[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2753 = llvm.mlir.constant(1 : i64) : i64
%v2754 = llvm.alloca %v2753 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2752, %v2754 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2755 = llvm.load %v2754 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v2755 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_matmul_backward_a(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg2: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v2756 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2757 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2758 = llvm.insertvalue %v2757, %v2756[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2759 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2760 = llvm.insertvalue %v2759, %v2758[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2761 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2762 = llvm.insertvalue %v2761, %v2760[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2763 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2764 = llvm.insertvalue %v2763, %v2762[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2765 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2766 = llvm.insertvalue %v2765, %v2764[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2767 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2768 = llvm.insertvalue %v2767, %v2766[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2769 = llvm.mlir.constant(1 : i64) : i64
%v2770 = llvm.alloca %v2769 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2768, %v2770 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2771 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2772 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2773 = llvm.insertvalue %v2772, %v2771[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2774 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2775 = llvm.insertvalue %v2774, %v2773[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2776 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2777 = llvm.insertvalue %v2776, %v2775[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2778 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2779 = llvm.insertvalue %v2778, %v2777[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2780 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2781 = llvm.insertvalue %v2780, %v2779[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2782 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2783 = llvm.insertvalue %v2782, %v2781[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2784 = llvm.mlir.constant(1 : i64) : i64
%v2785 = llvm.alloca %v2784 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2783, %v2785 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2786 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2787 = llvm.extractvalue %arg2[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2788 = llvm.insertvalue %v2787, %v2786[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2789 = llvm.extractvalue %arg2[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2790 = llvm.insertvalue %v2789, %v2788[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2791 = llvm.extractvalue %arg2[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2792 = llvm.insertvalue %v2791, %v2790[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2793 = llvm.extractvalue %arg2[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2794 = llvm.insertvalue %v2793, %v2792[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2795 = llvm.extractvalue %arg2[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2796 = llvm.insertvalue %v2795, %v2794[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2797 = llvm.extractvalue %arg2[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2798 = llvm.insertvalue %v2797, %v2796[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2799 = llvm.mlir.constant(1 : i64) : i64
%v2800 = llvm.alloca %v2799 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2798, %v2800 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2801 = llvm.load %v2800 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2802 = llvm.getelementptr %v2800[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2803 = llvm.load %v2802 : !llvm.ptr -> i32
%v2804 = llvm.load %v2800 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2805 = llvm.getelementptr %v2800[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2806 = llvm.load %v2805 : !llvm.ptr -> i32
%v2807 = llvm.load %v2770 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2808 = llvm.getelementptr %v2770[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2809 = llvm.load %v2808 : !llvm.ptr -> i32
%v2810 = arith.constant 1 : i32
%v2811 = arith.constant 1 : i32
%v2812 = func.call @tensor_zeros(%v2803, %v2809, %v2810, %v2811) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2813 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2814 = llvm.extractvalue %v2812[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2815 = llvm.insertvalue %v2814, %v2813[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2816 = llvm.extractvalue %v2812[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2817 = llvm.insertvalue %v2816, %v2815[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2818 = llvm.extractvalue %v2812[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2819 = llvm.insertvalue %v2818, %v2817[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2820 = llvm.extractvalue %v2812[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2821 = llvm.insertvalue %v2820, %v2819[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2822 = llvm.extractvalue %v2812[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2823 = llvm.insertvalue %v2822, %v2821[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2824 = llvm.extractvalue %v2812[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2825 = llvm.insertvalue %v2824, %v2823[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2826 = llvm.mlir.constant(1 : i64) : i64
%v2827 = llvm.alloca %v2826 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2825, %v2827 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2828 = llvm.load %v2827 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2829 = llvm.mlir.constant(1 : i64) : i64
%v2830 = llvm.alloca %v2829 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2828, %v2830 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2831 = arith.constant 0 : i32
%v2832 = arith.index_cast %v2831 : i32 to index
%v2833 = arith.index_cast %v2803 : i32 to index
%v2834 = arith.constant 1 : index
%v2835 = arith.constant -1 : index
%v2836 = arith.cmpi sle, %v2832, %v2833 : index
%v2837 = arith.select %v2836, %v2834, %v2835 : index
cf.br ^b109(%v2832 : index)
^b109(%v2838: index):
%v2839 = arith.cmpi slt, %v2838, %v2833 : index
%v2840 = arith.cmpi sgt, %v2838, %v2833 : index
%v2841 = arith.select %v2836, %v2839, %v2840 : i1
cf.cond_br %v2841, ^b110(%v2838 : index), ^b111(%v2838 : index)
^b110(%v2842: index):
%v2843 = arith.constant 0 : i32
%v2844 = arith.index_cast %v2843 : i32 to index
%v2845 = arith.index_cast %v2809 : i32 to index
%v2846 = arith.constant 1 : index
%v2847 = arith.constant -1 : index
%v2848 = arith.cmpi sle, %v2844, %v2845 : index
%v2849 = arith.select %v2848, %v2846, %v2847 : index
cf.br ^b112(%v2844 : index)
^b112(%v2850: index):
%v2851 = arith.cmpi slt, %v2850, %v2845 : index
%v2852 = arith.cmpi sgt, %v2850, %v2845 : index
%v2853 = arith.select %v2848, %v2851, %v2852 : i1
cf.cond_br %v2853, ^b113(%v2850 : index), ^b114(%v2850 : index)
^b113(%v2854: index):
%v2855 = arith.constant 0.0 : f64
%v2856 = arith.truncf %v2855 : f64 to f32
%v2857 = llvm.mlir.constant(1 : i64) : i64
%v2858 = llvm.alloca %v2857 x f32 : (i64) -> !llvm.ptr
llvm.store %v2856, %v2858 : f32, !llvm.ptr
%v2859 = arith.constant 0 : i32
%v2860 = arith.index_cast %v2859 : i32 to index
%v2861 = arith.index_cast %v2806 : i32 to index
%v2862 = arith.constant 1 : index
%v2863 = arith.constant -1 : index
%v2864 = arith.cmpi sle, %v2860, %v2861 : index
%v2865 = arith.select %v2864, %v2862, %v2863 : index
cf.br ^b115(%v2860 : index)
^b115(%v2866: index):
%v2867 = arith.cmpi slt, %v2866, %v2861 : index
%v2868 = arith.cmpi sgt, %v2866, %v2861 : index
%v2869 = arith.select %v2864, %v2867, %v2868 : i1
cf.cond_br %v2869, ^b116(%v2866 : index), ^b117(%v2866 : index)
^b116(%v2870: index):
%v2871 = llvm.load %v2858 : !llvm.ptr -> f32
%v2872 = llvm.load %v2800 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2873 = llvm.getelementptr %v2800[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2874 = llvm.load %v2873 : !llvm.ptr -> !llvm.ptr
%v2875 = arith.index_cast %v2842 : index to i32
%v2876 = arith.muli %v2875, %v2806 : i32
%v2877 = arith.index_cast %v2870 : index to i32
%v2878 = arith.addi %v2876, %v2877 : i32
%v2879 = arith.extsi %v2878 : i32 to i64
%v2880 = llvm.getelementptr %v2874[%v2879] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2881 = llvm.load %v2880 : !llvm.ptr -> f32
%v2882 = llvm.load %v2785 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2883 = llvm.getelementptr %v2785[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2884 = llvm.load %v2883 : !llvm.ptr -> !llvm.ptr
%v2885 = arith.index_cast %v2854 : index to i32
%v2886 = arith.muli %v2885, %v2806 : i32
%v2887 = arith.index_cast %v2870 : index to i32
%v2888 = arith.addi %v2886, %v2887 : i32
%v2889 = arith.extsi %v2888 : i32 to i64
%v2890 = llvm.getelementptr %v2884[%v2889] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2891 = llvm.load %v2890 : !llvm.ptr -> f32
%v2892 = llvm.intr.fmuladd(%v2881, %v2891, %v2871) : (f32, f32, f32) -> f32
llvm.store %v2892, %v2858 : f32, !llvm.ptr
%v2893 = arith.addi %v2870, %v2865 : index
cf.br ^b115(%v2893 : index)
^b117(%v2894: index):
%v2895 = llvm.load %v2858 : !llvm.ptr -> f32
%v2896 = llvm.load %v2830 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2897 = llvm.getelementptr %v2830[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2898 = llvm.load %v2897 : !llvm.ptr -> !llvm.ptr
%v2899 = arith.index_cast %v2842 : index to i32
%v2900 = arith.muli %v2899, %v2809 : i32
%v2901 = arith.index_cast %v2854 : index to i32
%v2902 = arith.addi %v2900, %v2901 : i32
%v2903 = arith.extsi %v2902 : i32 to i64
%v2904 = llvm.getelementptr %v2898[%v2903] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v2895, %v2904 : f32, !llvm.ptr
%v2905 = arith.addi %v2854, %v2849 : index
cf.br ^b112(%v2905 : index)
^b114(%v2906: index):
%v2907 = arith.addi %v2842, %v2837 : index
cf.br ^b109(%v2907 : index)
^b111(%v2908: index):
%v2909 = llvm.load %v2830 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2910 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2911 = llvm.extractvalue %v2909[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2912 = llvm.insertvalue %v2911, %v2910[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2913 = llvm.extractvalue %v2909[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2914 = llvm.insertvalue %v2913, %v2912[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2915 = llvm.extractvalue %v2909[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2916 = llvm.insertvalue %v2915, %v2914[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2917 = llvm.extractvalue %v2909[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2918 = llvm.insertvalue %v2917, %v2916[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2919 = llvm.extractvalue %v2909[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2920 = llvm.insertvalue %v2919, %v2918[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2921 = llvm.extractvalue %v2909[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2922 = llvm.insertvalue %v2921, %v2920[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2923 = llvm.mlir.constant(1 : i64) : i64
%v2924 = llvm.alloca %v2923 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2922, %v2924 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2925 = llvm.load %v2924 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v2925 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_matmul_backward_b(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg2: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v2926 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2927 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2928 = llvm.insertvalue %v2927, %v2926[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2929 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2930 = llvm.insertvalue %v2929, %v2928[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2931 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2932 = llvm.insertvalue %v2931, %v2930[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2933 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2934 = llvm.insertvalue %v2933, %v2932[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2935 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2936 = llvm.insertvalue %v2935, %v2934[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2937 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2938 = llvm.insertvalue %v2937, %v2936[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2939 = llvm.mlir.constant(1 : i64) : i64
%v2940 = llvm.alloca %v2939 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2938, %v2940 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2941 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2942 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2943 = llvm.insertvalue %v2942, %v2941[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2944 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2945 = llvm.insertvalue %v2944, %v2943[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2946 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2947 = llvm.insertvalue %v2946, %v2945[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2948 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2949 = llvm.insertvalue %v2948, %v2947[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2950 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2951 = llvm.insertvalue %v2950, %v2949[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2952 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2953 = llvm.insertvalue %v2952, %v2951[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2954 = llvm.mlir.constant(1 : i64) : i64
%v2955 = llvm.alloca %v2954 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2953, %v2955 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2956 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2957 = llvm.extractvalue %arg2[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2958 = llvm.insertvalue %v2957, %v2956[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2959 = llvm.extractvalue %arg2[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2960 = llvm.insertvalue %v2959, %v2958[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2961 = llvm.extractvalue %arg2[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2962 = llvm.insertvalue %v2961, %v2960[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2963 = llvm.extractvalue %arg2[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2964 = llvm.insertvalue %v2963, %v2962[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2965 = llvm.extractvalue %arg2[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2966 = llvm.insertvalue %v2965, %v2964[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2967 = llvm.extractvalue %arg2[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2968 = llvm.insertvalue %v2967, %v2966[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2969 = llvm.mlir.constant(1 : i64) : i64
%v2970 = llvm.alloca %v2969 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2968, %v2970 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2971 = llvm.load %v2940 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2972 = llvm.getelementptr %v2940[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2973 = llvm.load %v2972 : !llvm.ptr -> i32
%v2974 = llvm.load %v2940 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2975 = llvm.getelementptr %v2940[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2976 = llvm.load %v2975 : !llvm.ptr -> i32
%v2977 = llvm.load %v2970 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2978 = llvm.getelementptr %v2970[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2979 = llvm.load %v2978 : !llvm.ptr -> i32
%v2980 = arith.constant 1 : i32
%v2981 = arith.constant 1 : i32
%v2982 = func.call @tensor_zeros(%v2976, %v2979, %v2980, %v2981) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2983 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2984 = llvm.extractvalue %v2982[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2985 = llvm.insertvalue %v2984, %v2983[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2986 = llvm.extractvalue %v2982[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2987 = llvm.insertvalue %v2986, %v2985[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2988 = llvm.extractvalue %v2982[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2989 = llvm.insertvalue %v2988, %v2987[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2990 = llvm.extractvalue %v2982[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2991 = llvm.insertvalue %v2990, %v2989[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2992 = llvm.extractvalue %v2982[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2993 = llvm.insertvalue %v2992, %v2991[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2994 = llvm.extractvalue %v2982[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2995 = llvm.insertvalue %v2994, %v2993[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2996 = llvm.mlir.constant(1 : i64) : i64
%v2997 = llvm.alloca %v2996 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2995, %v2997 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2998 = llvm.load %v2997 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2999 = llvm.mlir.constant(1 : i64) : i64
%v3000 = llvm.alloca %v2999 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2998, %v3000 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3001 = arith.constant 0 : i32
%v3002 = arith.index_cast %v3001 : i32 to index
%v3003 = arith.index_cast %v2976 : i32 to index
%v3004 = arith.constant 1 : index
%v3005 = arith.constant -1 : index
%v3006 = arith.cmpi sle, %v3002, %v3003 : index
%v3007 = arith.select %v3006, %v3004, %v3005 : index
cf.br ^b118(%v3002 : index)
^b118(%v3008: index):
%v3009 = arith.cmpi slt, %v3008, %v3003 : index
%v3010 = arith.cmpi sgt, %v3008, %v3003 : index
%v3011 = arith.select %v3006, %v3009, %v3010 : i1
cf.cond_br %v3011, ^b119(%v3008 : index), ^b120(%v3008 : index)
^b119(%v3012: index):
%v3013 = arith.constant 0 : i32
%v3014 = arith.index_cast %v3013 : i32 to index
%v3015 = arith.index_cast %v2979 : i32 to index
%v3016 = arith.constant 1 : index
%v3017 = arith.constant -1 : index
%v3018 = arith.cmpi sle, %v3014, %v3015 : index
%v3019 = arith.select %v3018, %v3016, %v3017 : index
cf.br ^b121(%v3014 : index)
^b121(%v3020: index):
%v3021 = arith.cmpi slt, %v3020, %v3015 : index
%v3022 = arith.cmpi sgt, %v3020, %v3015 : index
%v3023 = arith.select %v3018, %v3021, %v3022 : i1
cf.cond_br %v3023, ^b122(%v3020 : index), ^b123(%v3020 : index)
^b122(%v3024: index):
%v3025 = arith.constant 0.0 : f64
%v3026 = arith.truncf %v3025 : f64 to f32
%v3027 = llvm.mlir.constant(1 : i64) : i64
%v3028 = llvm.alloca %v3027 x f32 : (i64) -> !llvm.ptr
llvm.store %v3026, %v3028 : f32, !llvm.ptr
%v3029 = arith.constant 0 : i32
%v3030 = arith.index_cast %v3029 : i32 to index
%v3031 = arith.index_cast %v2973 : i32 to index
%v3032 = arith.constant 1 : index
%v3033 = arith.constant -1 : index
%v3034 = arith.cmpi sle, %v3030, %v3031 : index
%v3035 = arith.select %v3034, %v3032, %v3033 : index
cf.br ^b124(%v3030 : index)
^b124(%v3036: index):
%v3037 = arith.cmpi slt, %v3036, %v3031 : index
%v3038 = arith.cmpi sgt, %v3036, %v3031 : index
%v3039 = arith.select %v3034, %v3037, %v3038 : i1
cf.cond_br %v3039, ^b125(%v3036 : index), ^b126(%v3036 : index)
^b125(%v3040: index):
%v3041 = llvm.load %v3028 : !llvm.ptr -> f32
%v3042 = llvm.load %v2940 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3043 = llvm.getelementptr %v2940[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3044 = llvm.load %v3043 : !llvm.ptr -> !llvm.ptr
%v3045 = arith.index_cast %v3040 : index to i32
%v3046 = arith.muli %v3045, %v2976 : i32
%v3047 = arith.index_cast %v3012 : index to i32
%v3048 = arith.addi %v3046, %v3047 : i32
%v3049 = arith.extsi %v3048 : i32 to i64
%v3050 = llvm.getelementptr %v3044[%v3049] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3051 = llvm.load %v3050 : !llvm.ptr -> f32
%v3052 = llvm.load %v2970 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3053 = llvm.getelementptr %v2970[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3054 = llvm.load %v3053 : !llvm.ptr -> !llvm.ptr
%v3055 = arith.index_cast %v3040 : index to i32
%v3056 = arith.muli %v3055, %v2979 : i32
%v3057 = arith.index_cast %v3024 : index to i32
%v3058 = arith.addi %v3056, %v3057 : i32
%v3059 = arith.extsi %v3058 : i32 to i64
%v3060 = llvm.getelementptr %v3054[%v3059] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3061 = llvm.load %v3060 : !llvm.ptr -> f32
%v3062 = llvm.intr.fmuladd(%v3051, %v3061, %v3041) : (f32, f32, f32) -> f32
llvm.store %v3062, %v3028 : f32, !llvm.ptr
%v3063 = arith.addi %v3040, %v3035 : index
cf.br ^b124(%v3063 : index)
^b126(%v3064: index):
%v3065 = llvm.load %v3028 : !llvm.ptr -> f32
%v3066 = llvm.load %v3000 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3067 = llvm.getelementptr %v3000[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3068 = llvm.load %v3067 : !llvm.ptr -> !llvm.ptr
%v3069 = arith.index_cast %v3012 : index to i32
%v3070 = arith.muli %v3069, %v2979 : i32
%v3071 = arith.index_cast %v3024 : index to i32
%v3072 = arith.addi %v3070, %v3071 : i32
%v3073 = arith.extsi %v3072 : i32 to i64
%v3074 = llvm.getelementptr %v3068[%v3073] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v3065, %v3074 : f32, !llvm.ptr
%v3075 = arith.addi %v3024, %v3019 : index
cf.br ^b121(%v3075 : index)
^b123(%v3076: index):
%v3077 = arith.addi %v3012, %v3007 : index
cf.br ^b118(%v3077 : index)
^b120(%v3078: index):
%v3079 = llvm.load %v3000 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3080 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3081 = llvm.extractvalue %v3079[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3082 = llvm.insertvalue %v3081, %v3080[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3083 = llvm.extractvalue %v3079[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3084 = llvm.insertvalue %v3083, %v3082[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3085 = llvm.extractvalue %v3079[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3086 = llvm.insertvalue %v3085, %v3084[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3087 = llvm.extractvalue %v3079[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3088 = llvm.insertvalue %v3087, %v3086[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3089 = llvm.extractvalue %v3079[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3090 = llvm.insertvalue %v3089, %v3088[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3091 = llvm.extractvalue %v3079[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3092 = llvm.insertvalue %v3091, %v3090[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3093 = llvm.mlir.constant(1 : i64) : i64
%v3094 = llvm.alloca %v3093 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3092, %v3094 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3095 = llvm.load %v3094 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v3095 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_transpose(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v3096 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3097 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3098 = llvm.insertvalue %v3097, %v3096[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3099 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3100 = llvm.insertvalue %v3099, %v3098[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3101 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3102 = llvm.insertvalue %v3101, %v3100[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3103 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3104 = llvm.insertvalue %v3103, %v3102[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3105 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3106 = llvm.insertvalue %v3105, %v3104[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3107 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3108 = llvm.insertvalue %v3107, %v3106[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3109 = llvm.mlir.constant(1 : i64) : i64
%v3110 = llvm.alloca %v3109 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3108, %v3110 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3111 = llvm.load %v3110 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3112 = llvm.getelementptr %v3110[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3113 = llvm.load %v3112 : !llvm.ptr -> i32
%v3114 = llvm.load %v3110 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3115 = llvm.getelementptr %v3110[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3116 = llvm.load %v3115 : !llvm.ptr -> i32
%v3117 = arith.constant 1 : i32
%v3118 = arith.constant 1 : i32
%v3119 = func.call @tensor_zeros(%v3113, %v3116, %v3117, %v3118) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3120 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3121 = llvm.extractvalue %v3119[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3122 = llvm.insertvalue %v3121, %v3120[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3123 = llvm.extractvalue %v3119[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3124 = llvm.insertvalue %v3123, %v3122[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3125 = llvm.extractvalue %v3119[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3126 = llvm.insertvalue %v3125, %v3124[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3127 = llvm.extractvalue %v3119[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3128 = llvm.insertvalue %v3127, %v3126[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3129 = llvm.extractvalue %v3119[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3130 = llvm.insertvalue %v3129, %v3128[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3131 = llvm.extractvalue %v3119[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3132 = llvm.insertvalue %v3131, %v3130[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3133 = llvm.mlir.constant(1 : i64) : i64
%v3134 = llvm.alloca %v3133 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3132, %v3134 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3135 = llvm.load %v3134 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3136 = llvm.mlir.constant(1 : i64) : i64
%v3137 = llvm.alloca %v3136 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3135, %v3137 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3138 = arith.constant 0 : i32
%v3139 = llvm.load %v3110 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3140 = llvm.getelementptr %v3110[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3141 = llvm.load %v3140 : !llvm.ptr -> i32
%v3142 = arith.index_cast %v3138 : i32 to index
%v3143 = arith.index_cast %v3141 : i32 to index
%v3144 = arith.constant 1 : index
%v3145 = arith.constant -1 : index
%v3146 = arith.cmpi sle, %v3142, %v3143 : index
%v3147 = arith.select %v3146, %v3144, %v3145 : index
cf.br ^b127(%v3142 : index)
^b127(%v3148: index):
%v3149 = arith.cmpi slt, %v3148, %v3143 : index
%v3150 = arith.cmpi sgt, %v3148, %v3143 : index
%v3151 = arith.select %v3146, %v3149, %v3150 : i1
cf.cond_br %v3151, ^b128(%v3148 : index), ^b129(%v3148 : index)
^b128(%v3152: index):
%v3153 = arith.constant 0 : i32
%v3154 = llvm.load %v3110 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3155 = llvm.getelementptr %v3110[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3156 = llvm.load %v3155 : !llvm.ptr -> i32
%v3157 = arith.index_cast %v3153 : i32 to index
%v3158 = arith.index_cast %v3156 : i32 to index
%v3159 = arith.constant 1 : index
%v3160 = arith.constant -1 : index
%v3161 = arith.cmpi sle, %v3157, %v3158 : index
%v3162 = arith.select %v3161, %v3159, %v3160 : index
cf.br ^b130(%v3157 : index)
^b130(%v3163: index):
%v3164 = arith.cmpi slt, %v3163, %v3158 : index
%v3165 = arith.cmpi sgt, %v3163, %v3158 : index
%v3166 = arith.select %v3161, %v3164, %v3165 : i1
cf.cond_br %v3166, ^b131(%v3163 : index), ^b132(%v3163 : index)
^b131(%v3167: index):
%v3168 = llvm.load %v3110 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3169 = llvm.getelementptr %v3110[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3170 = llvm.load %v3169 : !llvm.ptr -> !llvm.ptr
%v3171 = llvm.load %v3110 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3172 = llvm.getelementptr %v3110[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3173 = llvm.load %v3172 : !llvm.ptr -> i32
%v3174 = arith.index_cast %v3152 : index to i32
%v3175 = arith.muli %v3174, %v3173 : i32
%v3176 = arith.index_cast %v3167 : index to i32
%v3177 = arith.addi %v3175, %v3176 : i32
%v3178 = arith.extsi %v3177 : i32 to i64
%v3179 = llvm.getelementptr %v3170[%v3178] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3180 = llvm.load %v3179 : !llvm.ptr -> f32
%v3181 = llvm.load %v3137 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3182 = llvm.getelementptr %v3137[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3183 = llvm.load %v3182 : !llvm.ptr -> !llvm.ptr
%v3184 = llvm.load %v3110 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3185 = llvm.getelementptr %v3110[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3186 = llvm.load %v3185 : !llvm.ptr -> i32
%v3187 = arith.index_cast %v3167 : index to i32
%v3188 = arith.muli %v3187, %v3186 : i32
%v3189 = arith.index_cast %v3152 : index to i32
%v3190 = arith.addi %v3188, %v3189 : i32
%v3191 = arith.extsi %v3190 : i32 to i64
%v3192 = llvm.getelementptr %v3183[%v3191] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v3180, %v3192 : f32, !llvm.ptr
%v3193 = arith.addi %v3167, %v3162 : index
cf.br ^b130(%v3193 : index)
^b132(%v3194: index):
%v3195 = arith.addi %v3152, %v3147 : index
cf.br ^b127(%v3195 : index)
^b129(%v3196: index):
%v3197 = llvm.load %v3137 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3198 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3199 = llvm.extractvalue %v3197[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3200 = llvm.insertvalue %v3199, %v3198[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3201 = llvm.extractvalue %v3197[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3202 = llvm.insertvalue %v3201, %v3200[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3203 = llvm.extractvalue %v3197[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3204 = llvm.insertvalue %v3203, %v3202[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3205 = llvm.extractvalue %v3197[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3206 = llvm.insertvalue %v3205, %v3204[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3207 = llvm.extractvalue %v3197[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3208 = llvm.insertvalue %v3207, %v3206[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3209 = llvm.extractvalue %v3197[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3210 = llvm.insertvalue %v3209, %v3208[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3211 = llvm.mlir.constant(1 : i64) : i64
%v3212 = llvm.alloca %v3211 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3210, %v3212 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3213 = llvm.load %v3212 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v3213 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_sum(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> f32 {
%v3214 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3215 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3216 = llvm.insertvalue %v3215, %v3214[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3217 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3218 = llvm.insertvalue %v3217, %v3216[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3219 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3220 = llvm.insertvalue %v3219, %v3218[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3221 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3222 = llvm.insertvalue %v3221, %v3220[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3223 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3224 = llvm.insertvalue %v3223, %v3222[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3225 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3226 = llvm.insertvalue %v3225, %v3224[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3227 = llvm.mlir.constant(1 : i64) : i64
%v3228 = llvm.alloca %v3227 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3226, %v3228 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3229 = arith.constant 0.0 : f64
%v3230 = arith.truncf %v3229 : f64 to f32
%v3231 = llvm.mlir.constant(1 : i64) : i64
%v3232 = llvm.alloca %v3231 x f32 : (i64) -> !llvm.ptr
llvm.store %v3230, %v3232 : f32, !llvm.ptr
%v3233 = arith.constant 0 : i32
%v3234 = llvm.load %v3228 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3235 = llvm.getelementptr %v3228[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3236 = llvm.load %v3235 : !llvm.ptr -> i32
%v3237 = arith.index_cast %v3233 : i32 to index
%v3238 = arith.index_cast %v3236 : i32 to index
%v3239 = arith.constant 1 : index
%v3240 = arith.constant -1 : index
%v3241 = arith.cmpi sle, %v3237, %v3238 : index
%v3242 = arith.select %v3241, %v3239, %v3240 : index
cf.br ^b133(%v3237 : index)
^b133(%v3243: index):
%v3244 = arith.cmpi slt, %v3243, %v3238 : index
%v3245 = arith.cmpi sgt, %v3243, %v3238 : index
%v3246 = arith.select %v3241, %v3244, %v3245 : i1
cf.cond_br %v3246, ^b134(%v3243 : index), ^b135(%v3243 : index)
^b134(%v3247: index):
%v3248 = llvm.load %v3232 : !llvm.ptr -> f32
%v3249 = llvm.load %v3228 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3250 = llvm.getelementptr %v3228[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3251 = llvm.load %v3250 : !llvm.ptr -> !llvm.ptr
%v3252 = arith.index_cast %v3247 : index to i64
%v3253 = llvm.getelementptr %v3251[%v3252] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3254 = llvm.load %v3253 : !llvm.ptr -> f32
%v3255 = arith.addf %v3248, %v3254 : f32
llvm.store %v3255, %v3232 : f32, !llvm.ptr
%v3256 = arith.addi %v3247, %v3242 : index
cf.br ^b133(%v3256 : index)
^b135(%v3257: index):
%v3258 = llvm.load %v3232 : !llvm.ptr -> f32
func.return %v3258 : f32
}
func.func @tensor_mean(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> f32 {
%v3259 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3260 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3261 = llvm.insertvalue %v3260, %v3259[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3262 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3263 = llvm.insertvalue %v3262, %v3261[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3264 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3265 = llvm.insertvalue %v3264, %v3263[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3266 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3267 = llvm.insertvalue %v3266, %v3265[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3268 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3269 = llvm.insertvalue %v3268, %v3267[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3270 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3271 = llvm.insertvalue %v3270, %v3269[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3272 = llvm.mlir.constant(1 : i64) : i64
%v3273 = llvm.alloca %v3272 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3271, %v3273 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3274 = llvm.load %v3273 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3275 = func.call @tensor_sum(%v3274) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> f32
%v3276 = llvm.load %v3273 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3277 = llvm.getelementptr %v3273[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3278 = llvm.load %v3277 : !llvm.ptr -> i32
%v3279 = arith.sitofp %v3278 : i32 to f32
%v3280 = arith.divf %v3275, %v3279 : f32
func.return %v3280 : f32
}
func.func @tensor_max(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> f32 {
%v3281 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3282 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3283 = llvm.insertvalue %v3282, %v3281[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3284 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3285 = llvm.insertvalue %v3284, %v3283[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3286 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3287 = llvm.insertvalue %v3286, %v3285[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3288 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3289 = llvm.insertvalue %v3288, %v3287[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3290 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3291 = llvm.insertvalue %v3290, %v3289[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3292 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3293 = llvm.insertvalue %v3292, %v3291[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3294 = llvm.mlir.constant(1 : i64) : i64
%v3295 = llvm.alloca %v3294 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3293, %v3295 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3296 = llvm.load %v3295 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3297 = llvm.getelementptr %v3295[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3298 = llvm.load %v3297 : !llvm.ptr -> !llvm.ptr
%v3299 = arith.constant 0 : i32
%v3300 = arith.extsi %v3299 : i32 to i64
%v3301 = llvm.getelementptr %v3298[%v3300] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3302 = llvm.load %v3301 : !llvm.ptr -> f32
%v3303 = llvm.mlir.constant(1 : i64) : i64
%v3304 = llvm.alloca %v3303 x f32 : (i64) -> !llvm.ptr
llvm.store %v3302, %v3304 : f32, !llvm.ptr
%v3305 = arith.constant 1 : i32
%v3306 = llvm.load %v3295 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3307 = llvm.getelementptr %v3295[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3308 = llvm.load %v3307 : !llvm.ptr -> i32
%v3309 = arith.index_cast %v3305 : i32 to index
%v3310 = arith.index_cast %v3308 : i32 to index
%v3311 = arith.constant 1 : index
%v3312 = arith.constant -1 : index
%v3313 = arith.cmpi sle, %v3309, %v3310 : index
%v3314 = arith.select %v3313, %v3311, %v3312 : index
cf.br ^b136(%v3309 : index)
^b136(%v3315: index):
%v3316 = arith.cmpi slt, %v3315, %v3310 : index
%v3317 = arith.cmpi sgt, %v3315, %v3310 : index
%v3318 = arith.select %v3313, %v3316, %v3317 : i1
cf.cond_br %v3318, ^b137(%v3315 : index), ^b138(%v3315 : index)
^b137(%v3319: index):
%v3320 = llvm.load %v3295 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3321 = llvm.getelementptr %v3295[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3322 = llvm.load %v3321 : !llvm.ptr -> !llvm.ptr
%v3323 = arith.index_cast %v3319 : index to i64
%v3324 = llvm.getelementptr %v3322[%v3323] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3325 = llvm.load %v3324 : !llvm.ptr -> f32
%v3326 = llvm.load %v3304 : !llvm.ptr -> f32
%v3327 = arith.cmpf ogt, %v3325, %v3326 : f32
cf.cond_br %v3327, ^b139, ^b140
^b139:
%v3328 = llvm.load %v3295 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3329 = llvm.getelementptr %v3295[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3330 = llvm.load %v3329 : !llvm.ptr -> !llvm.ptr
%v3331 = arith.index_cast %v3319 : index to i64
%v3332 = llvm.getelementptr %v3330[%v3331] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3333 = llvm.load %v3332 : !llvm.ptr -> f32
llvm.store %v3333, %v3304 : f32, !llvm.ptr
cf.br ^b141
^b140:
cf.br ^b141
^b141:
%v3334 = arith.addi %v3319, %v3314 : index
cf.br ^b136(%v3334 : index)
^b138(%v3335: index):
%v3336 = llvm.load %v3304 : !llvm.ptr -> f32
func.return %v3336 : f32
}
func.func @tensor_min(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> f32 {
%v3337 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3338 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3339 = llvm.insertvalue %v3338, %v3337[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3340 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3341 = llvm.insertvalue %v3340, %v3339[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3342 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3343 = llvm.insertvalue %v3342, %v3341[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3344 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3345 = llvm.insertvalue %v3344, %v3343[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3346 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3347 = llvm.insertvalue %v3346, %v3345[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3348 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3349 = llvm.insertvalue %v3348, %v3347[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3350 = llvm.mlir.constant(1 : i64) : i64
%v3351 = llvm.alloca %v3350 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3349, %v3351 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3352 = llvm.load %v3351 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3353 = llvm.getelementptr %v3351[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3354 = llvm.load %v3353 : !llvm.ptr -> !llvm.ptr
%v3355 = arith.constant 0 : i32
%v3356 = arith.extsi %v3355 : i32 to i64
%v3357 = llvm.getelementptr %v3354[%v3356] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3358 = llvm.load %v3357 : !llvm.ptr -> f32
%v3359 = llvm.mlir.constant(1 : i64) : i64
%v3360 = llvm.alloca %v3359 x f32 : (i64) -> !llvm.ptr
llvm.store %v3358, %v3360 : f32, !llvm.ptr
%v3361 = arith.constant 1 : i32
%v3362 = llvm.load %v3351 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3363 = llvm.getelementptr %v3351[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3364 = llvm.load %v3363 : !llvm.ptr -> i32
%v3365 = arith.index_cast %v3361 : i32 to index
%v3366 = arith.index_cast %v3364 : i32 to index
%v3367 = arith.constant 1 : index
%v3368 = arith.constant -1 : index
%v3369 = arith.cmpi sle, %v3365, %v3366 : index
%v3370 = arith.select %v3369, %v3367, %v3368 : index
cf.br ^b142(%v3365 : index)
^b142(%v3371: index):
%v3372 = arith.cmpi slt, %v3371, %v3366 : index
%v3373 = arith.cmpi sgt, %v3371, %v3366 : index
%v3374 = arith.select %v3369, %v3372, %v3373 : i1
cf.cond_br %v3374, ^b143(%v3371 : index), ^b144(%v3371 : index)
^b143(%v3375: index):
%v3376 = llvm.load %v3351 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3377 = llvm.getelementptr %v3351[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3378 = llvm.load %v3377 : !llvm.ptr -> !llvm.ptr
%v3379 = arith.index_cast %v3375 : index to i64
%v3380 = llvm.getelementptr %v3378[%v3379] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3381 = llvm.load %v3380 : !llvm.ptr -> f32
%v3382 = llvm.load %v3360 : !llvm.ptr -> f32
%v3383 = arith.cmpf olt, %v3381, %v3382 : f32
cf.cond_br %v3383, ^b145, ^b146
^b145:
%v3384 = llvm.load %v3351 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3385 = llvm.getelementptr %v3351[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3386 = llvm.load %v3385 : !llvm.ptr -> !llvm.ptr
%v3387 = arith.index_cast %v3375 : index to i64
%v3388 = llvm.getelementptr %v3386[%v3387] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3389 = llvm.load %v3388 : !llvm.ptr -> f32
llvm.store %v3389, %v3360 : f32, !llvm.ptr
cf.br ^b147
^b146:
cf.br ^b147
^b147:
%v3390 = arith.addi %v3375, %v3370 : index
cf.br ^b142(%v3390 : index)
^b144(%v3391: index):
%v3392 = llvm.load %v3360 : !llvm.ptr -> f32
func.return %v3392 : f32
}
func.func @tensor_argmax(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> i32 {
%v3393 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3394 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3395 = llvm.insertvalue %v3394, %v3393[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3396 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3397 = llvm.insertvalue %v3396, %v3395[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3398 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3399 = llvm.insertvalue %v3398, %v3397[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3400 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3401 = llvm.insertvalue %v3400, %v3399[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3402 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3403 = llvm.insertvalue %v3402, %v3401[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3404 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3405 = llvm.insertvalue %v3404, %v3403[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3406 = llvm.mlir.constant(1 : i64) : i64
%v3407 = llvm.alloca %v3406 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3405, %v3407 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3408 = arith.constant 0 : i32
%v3409 = llvm.mlir.constant(1 : i64) : i64
%v3410 = llvm.alloca %v3409 x i32 : (i64) -> !llvm.ptr
llvm.store %v3408, %v3410 : i32, !llvm.ptr
%v3411 = llvm.load %v3407 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3412 = llvm.getelementptr %v3407[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3413 = llvm.load %v3412 : !llvm.ptr -> !llvm.ptr
%v3414 = arith.constant 0 : i32
%v3415 = arith.extsi %v3414 : i32 to i64
%v3416 = llvm.getelementptr %v3413[%v3415] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3417 = llvm.load %v3416 : !llvm.ptr -> f32
%v3418 = llvm.mlir.constant(1 : i64) : i64
%v3419 = llvm.alloca %v3418 x f32 : (i64) -> !llvm.ptr
llvm.store %v3417, %v3419 : f32, !llvm.ptr
%v3420 = arith.constant 1 : i32
%v3421 = llvm.load %v3407 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3422 = llvm.getelementptr %v3407[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3423 = llvm.load %v3422 : !llvm.ptr -> i32
%v3424 = arith.index_cast %v3420 : i32 to index
%v3425 = arith.index_cast %v3423 : i32 to index
%v3426 = arith.constant 1 : index
%v3427 = arith.constant -1 : index
%v3428 = arith.cmpi sle, %v3424, %v3425 : index
%v3429 = arith.select %v3428, %v3426, %v3427 : index
cf.br ^b148(%v3424 : index)
^b148(%v3430: index):
%v3431 = arith.cmpi slt, %v3430, %v3425 : index
%v3432 = arith.cmpi sgt, %v3430, %v3425 : index
%v3433 = arith.select %v3428, %v3431, %v3432 : i1
cf.cond_br %v3433, ^b149(%v3430 : index), ^b150(%v3430 : index)
^b149(%v3434: index):
%v3435 = llvm.load %v3407 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3436 = llvm.getelementptr %v3407[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3437 = llvm.load %v3436 : !llvm.ptr -> !llvm.ptr
%v3438 = arith.index_cast %v3434 : index to i64
%v3439 = llvm.getelementptr %v3437[%v3438] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3440 = llvm.load %v3439 : !llvm.ptr -> f32
%v3441 = llvm.load %v3419 : !llvm.ptr -> f32
%v3442 = arith.cmpf ogt, %v3440, %v3441 : f32
cf.cond_br %v3442, ^b151, ^b152
^b151:
%v3443 = llvm.load %v3407 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3444 = llvm.getelementptr %v3407[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3445 = llvm.load %v3444 : !llvm.ptr -> !llvm.ptr
%v3446 = arith.index_cast %v3434 : index to i64
%v3447 = llvm.getelementptr %v3445[%v3446] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3448 = llvm.load %v3447 : !llvm.ptr -> f32
llvm.store %v3448, %v3419 : f32, !llvm.ptr
%v3449 = arith.index_cast %v3434 : index to i32
llvm.store %v3449, %v3410 : i32, !llvm.ptr
cf.br ^b153
^b152:
cf.br ^b153
^b153:
%v3450 = arith.addi %v3434, %v3429 : index
cf.br ^b148(%v3450 : index)
^b150(%v3451: index):
%v3452 = llvm.load %v3410 : !llvm.ptr -> i32
func.return %v3452 : i32
}
func.func @tensor_copy(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v3453 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3454 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3455 = llvm.insertvalue %v3454, %v3453[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3456 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3457 = llvm.insertvalue %v3456, %v3455[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3458 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3459 = llvm.insertvalue %v3458, %v3457[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3460 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3461 = llvm.insertvalue %v3460, %v3459[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3462 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3463 = llvm.insertvalue %v3462, %v3461[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3464 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3465 = llvm.insertvalue %v3464, %v3463[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3466 = llvm.mlir.constant(1 : i64) : i64
%v3467 = llvm.alloca %v3466 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3465, %v3467 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3468 = llvm.load %v3467 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3469 = llvm.getelementptr %v3467[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3470 = llvm.load %v3469 : !llvm.ptr -> i32
%v3471 = llvm.load %v3467 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3472 = llvm.getelementptr %v3467[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3473 = llvm.load %v3472 : !llvm.ptr -> i32
%v3474 = llvm.load %v3467 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3475 = llvm.getelementptr %v3467[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3476 = llvm.load %v3475 : !llvm.ptr -> i32
%v3477 = llvm.load %v3467 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3478 = llvm.getelementptr %v3467[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3479 = llvm.load %v3478 : !llvm.ptr -> i32
%v3480 = func.call @tensor_zeros(%v3470, %v3473, %v3476, %v3479) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3481 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3482 = llvm.extractvalue %v3480[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3483 = llvm.insertvalue %v3482, %v3481[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3484 = llvm.extractvalue %v3480[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3485 = llvm.insertvalue %v3484, %v3483[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3486 = llvm.extractvalue %v3480[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3487 = llvm.insertvalue %v3486, %v3485[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3488 = llvm.extractvalue %v3480[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3489 = llvm.insertvalue %v3488, %v3487[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3490 = llvm.extractvalue %v3480[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3491 = llvm.insertvalue %v3490, %v3489[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3492 = llvm.extractvalue %v3480[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3493 = llvm.insertvalue %v3492, %v3491[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3494 = llvm.mlir.constant(1 : i64) : i64
%v3495 = llvm.alloca %v3494 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3493, %v3495 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3496 = llvm.load %v3495 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3497 = llvm.mlir.constant(1 : i64) : i64
%v3498 = llvm.alloca %v3497 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3496, %v3498 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3499 = arith.constant 0 : i32
%v3500 = llvm.load %v3467 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3501 = llvm.getelementptr %v3467[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3502 = llvm.load %v3501 : !llvm.ptr -> i32
%v3503 = arith.index_cast %v3499 : i32 to index
%v3504 = arith.index_cast %v3502 : i32 to index
%v3505 = arith.constant 1 : index
%v3506 = arith.constant -1 : index
%v3507 = arith.cmpi sle, %v3503, %v3504 : index
%v3508 = arith.select %v3507, %v3505, %v3506 : index
cf.br ^b154(%v3503 : index)
^b154(%v3509: index):
%v3510 = arith.cmpi slt, %v3509, %v3504 : index
%v3511 = arith.cmpi sgt, %v3509, %v3504 : index
%v3512 = arith.select %v3507, %v3510, %v3511 : i1
cf.cond_br %v3512, ^b155(%v3509 : index), ^b156(%v3509 : index)
^b155(%v3513: index):
%v3514 = llvm.load %v3467 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3515 = llvm.getelementptr %v3467[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3516 = llvm.load %v3515 : !llvm.ptr -> !llvm.ptr
%v3517 = arith.index_cast %v3513 : index to i64
%v3518 = llvm.getelementptr %v3516[%v3517] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3519 = llvm.load %v3518 : !llvm.ptr -> f32
%v3520 = llvm.load %v3498 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3521 = llvm.getelementptr %v3498[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3522 = llvm.load %v3521 : !llvm.ptr -> !llvm.ptr
%v3523 = arith.index_cast %v3513 : index to i64
%v3524 = llvm.getelementptr %v3522[%v3523] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v3519, %v3524 : f32, !llvm.ptr
%v3525 = arith.addi %v3513, %v3508 : index
cf.br ^b154(%v3525 : index)
^b156(%v3526: index):
%v3527 = llvm.load %v3498 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3528 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3529 = llvm.extractvalue %v3527[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3530 = llvm.insertvalue %v3529, %v3528[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3531 = llvm.extractvalue %v3527[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3532 = llvm.insertvalue %v3531, %v3530[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3533 = llvm.extractvalue %v3527[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3534 = llvm.insertvalue %v3533, %v3532[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3535 = llvm.extractvalue %v3527[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3536 = llvm.insertvalue %v3535, %v3534[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3537 = llvm.extractvalue %v3527[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3538 = llvm.insertvalue %v3537, %v3536[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3539 = llvm.extractvalue %v3527[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3540 = llvm.insertvalue %v3539, %v3538[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3541 = llvm.mlir.constant(1 : i64) : i64
%v3542 = llvm.alloca %v3541 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3540, %v3542 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3543 = llvm.load %v3542 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v3543 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_print(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> () {
%v3544 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3545 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3546 = llvm.insertvalue %v3545, %v3544[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3547 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3548 = llvm.insertvalue %v3547, %v3546[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3549 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3550 = llvm.insertvalue %v3549, %v3548[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3551 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3552 = llvm.insertvalue %v3551, %v3550[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3553 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3554 = llvm.insertvalue %v3553, %v3552[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3555 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3556 = llvm.insertvalue %v3555, %v3554[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3557 = llvm.mlir.constant(1 : i64) : i64
%v3558 = llvm.alloca %v3557 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3556, %v3558 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3559 = llvm.mlir.addressof @str_15 : !llvm.ptr
%v3560 = llvm.call @printf(%v3559) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3561 = arith.constant 0 : i32
%v3562 = llvm.load %v3558 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3563 = llvm.getelementptr %v3558[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3564 = llvm.load %v3563 : !llvm.ptr -> i32
%v3565 = llvm.mlir.addressof @str_16 : !llvm.ptr
%v3566 = llvm.call @printf(%v3565, %v3564) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v3567 = arith.constant 0 : i32
%v3568 = llvm.mlir.addressof @str_17 : !llvm.ptr
%v3569 = llvm.call @printf(%v3568) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3570 = arith.constant 0 : i32
%v3571 = llvm.load %v3558 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3572 = llvm.getelementptr %v3558[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3573 = llvm.load %v3572 : !llvm.ptr -> i32
%v3574 = llvm.mlir.addressof @str_16 : !llvm.ptr
%v3575 = llvm.call @printf(%v3574, %v3573) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v3576 = arith.constant 0 : i32
%v3577 = llvm.mlir.addressof @str_17 : !llvm.ptr
%v3578 = llvm.call @printf(%v3577) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3579 = arith.constant 0 : i32
%v3580 = llvm.load %v3558 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3581 = llvm.getelementptr %v3558[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3582 = llvm.load %v3581 : !llvm.ptr -> i32
%v3583 = llvm.mlir.addressof @str_16 : !llvm.ptr
%v3584 = llvm.call @printf(%v3583, %v3582) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v3585 = arith.constant 0 : i32
%v3586 = llvm.mlir.addressof @str_17 : !llvm.ptr
%v3587 = llvm.call @printf(%v3586) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3588 = arith.constant 0 : i32
%v3589 = llvm.load %v3558 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3590 = llvm.getelementptr %v3558[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3591 = llvm.load %v3590 : !llvm.ptr -> i32
%v3592 = llvm.mlir.addressof @str_16 : !llvm.ptr
%v3593 = llvm.call @printf(%v3592, %v3591) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v3594 = arith.constant 0 : i32
%v3595 = llvm.mlir.addressof @str_18 : !llvm.ptr
%v3596 = llvm.call @printf(%v3595) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3597 = arith.constant 0 : i32
%v3598 = llvm.load %v3558 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3599 = llvm.getelementptr %v3558[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3600 = llvm.load %v3599 : !llvm.ptr -> i32
%v3601 = llvm.mlir.constant(1 : i64) : i64
%v3602 = llvm.alloca %v3601 x i32 : (i64) -> !llvm.ptr
llvm.store %v3600, %v3602 : i32, !llvm.ptr
%v3603 = llvm.load %v3602 : !llvm.ptr -> i32
%v3604 = arith.constant 10 : i32
%v3605 = arith.cmpi sgt, %v3603, %v3604 : i32
cf.cond_br %v3605, ^b157, ^b158
^b157:
%v3606 = arith.constant 10 : i32
llvm.store %v3606, %v3602 : i32, !llvm.ptr
cf.br ^b159
^b158:
cf.br ^b159
^b159:
%v3607 = llvm.mlir.addressof @str_19 : !llvm.ptr
%v3608 = llvm.call @printf(%v3607) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3609 = arith.constant 0 : i32
%v3610 = arith.constant 0 : i32
%v3611 = llvm.load %v3602 : !llvm.ptr -> i32
%v3612 = arith.index_cast %v3610 : i32 to index
%v3613 = arith.index_cast %v3611 : i32 to index
%v3614 = arith.constant 1 : index
%v3615 = arith.constant -1 : index
%v3616 = arith.cmpi sle, %v3612, %v3613 : index
%v3617 = arith.select %v3616, %v3614, %v3615 : index
cf.br ^b160(%v3612 : index)
^b160(%v3618: index):
%v3619 = arith.cmpi slt, %v3618, %v3613 : index
%v3620 = arith.cmpi sgt, %v3618, %v3613 : index
%v3621 = arith.select %v3616, %v3619, %v3620 : i1
cf.cond_br %v3621, ^b161(%v3618 : index), ^b162(%v3618 : index)
^b161(%v3622: index):
%v3623 = llvm.load %v3558 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3624 = llvm.getelementptr %v3558[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3625 = llvm.load %v3624 : !llvm.ptr -> !llvm.ptr
%v3626 = arith.index_cast %v3622 : index to i64
%v3627 = llvm.getelementptr %v3625[%v3626] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3628 = llvm.load %v3627 : !llvm.ptr -> f32
%v3629 = arith.extf %v3628 : f32 to f64
%v3630 = llvm.mlir.addressof @str_20 : !llvm.ptr
%v3631 = llvm.call @printf(%v3630, %v3629) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v3632 = arith.constant 0 : i32
%v3633 = llvm.load %v3602 : !llvm.ptr -> i32
%v3634 = arith.constant 1 : i32
%v3635 = arith.subi %v3633, %v3634 : i32
%v3636 = arith.index_cast %v3622 : index to i32
%v3637 = arith.cmpi slt, %v3636, %v3635 : i32
cf.cond_br %v3637, ^b163, ^b164
^b163:
%v3638 = llvm.mlir.addressof @str_17 : !llvm.ptr
%v3639 = llvm.call @printf(%v3638) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3640 = arith.constant 0 : i32
cf.br ^b165
^b164:
cf.br ^b165
^b165:
%v3641 = arith.addi %v3622, %v3617 : index
cf.br ^b160(%v3641 : index)
^b162(%v3642: index):
%v3643 = llvm.load %v3558 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3644 = llvm.getelementptr %v3558[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3645 = llvm.load %v3644 : !llvm.ptr -> i32
%v3646 = arith.constant 10 : i32
%v3647 = arith.cmpi sgt, %v3645, %v3646 : i32
cf.cond_br %v3647, ^b166, ^b167
^b166:
%v3648 = llvm.mlir.addressof @str_21 : !llvm.ptr
%v3649 = llvm.call @printf(%v3648) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3650 = arith.constant 0 : i32
cf.br ^b168
^b167:
cf.br ^b168
^b168:
%v3651 = llvm.mlir.addressof @str_22 : !llvm.ptr
%v3652 = llvm.call @printf(%v3651) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3653 = arith.constant 0 : i32
func.return
}
func.func @bench_matmul(%arg0: i32, %arg1: i32, %arg2: i32) -> f32 {
%v3654 = arith.constant 1 : i32
%v3655 = arith.constant 1 : i32
%v3656 = arith.constant 42 : i32
%v3657 = func.call @tensor_rand(%arg0, %arg1, %v3654, %v3655, %v3656) : (i32, i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3658 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3659 = llvm.extractvalue %v3657[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3660 = llvm.insertvalue %v3659, %v3658[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3661 = llvm.extractvalue %v3657[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3662 = llvm.insertvalue %v3661, %v3660[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3663 = llvm.extractvalue %v3657[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3664 = llvm.insertvalue %v3663, %v3662[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3665 = llvm.extractvalue %v3657[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3666 = llvm.insertvalue %v3665, %v3664[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3667 = llvm.extractvalue %v3657[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3668 = llvm.insertvalue %v3667, %v3666[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3669 = llvm.extractvalue %v3657[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3670 = llvm.insertvalue %v3669, %v3668[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3671 = llvm.mlir.constant(1 : i64) : i64
%v3672 = llvm.alloca %v3671 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3670, %v3672 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3673 = llvm.load %v3672 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3674 = llvm.mlir.constant(1 : i64) : i64
%v3675 = llvm.alloca %v3674 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3673, %v3675 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3676 = arith.constant 1 : i32
%v3677 = arith.constant 1 : i32
%v3678 = arith.constant 99 : i32
%v3679 = func.call @tensor_rand(%arg1, %arg2, %v3676, %v3677, %v3678) : (i32, i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3680 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3681 = llvm.extractvalue %v3679[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3682 = llvm.insertvalue %v3681, %v3680[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3683 = llvm.extractvalue %v3679[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3684 = llvm.insertvalue %v3683, %v3682[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3685 = llvm.extractvalue %v3679[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3686 = llvm.insertvalue %v3685, %v3684[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3687 = llvm.extractvalue %v3679[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3688 = llvm.insertvalue %v3687, %v3686[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3689 = llvm.extractvalue %v3679[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3690 = llvm.insertvalue %v3689, %v3688[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3691 = llvm.extractvalue %v3679[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3692 = llvm.insertvalue %v3691, %v3690[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3693 = llvm.mlir.constant(1 : i64) : i64
%v3694 = llvm.alloca %v3693 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3692, %v3694 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3695 = llvm.load %v3694 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3696 = llvm.mlir.constant(1 : i64) : i64
%v3697 = llvm.alloca %v3696 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3695, %v3697 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3698 = llvm.load %v3675 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3699 = llvm.load %v3697 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3700 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3701 = llvm.extractvalue %v3699[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3702 = llvm.insertvalue %v3701, %v3700[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3703 = llvm.extractvalue %v3699[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3704 = llvm.insertvalue %v3703, %v3702[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3705 = llvm.extractvalue %v3699[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3706 = llvm.insertvalue %v3705, %v3704[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3707 = llvm.extractvalue %v3699[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3708 = llvm.insertvalue %v3707, %v3706[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3709 = llvm.extractvalue %v3699[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3710 = llvm.insertvalue %v3709, %v3708[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3711 = llvm.extractvalue %v3699[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3712 = llvm.insertvalue %v3711, %v3710[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3713 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3714 = llvm.extractvalue %v3698[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3715 = llvm.insertvalue %v3714, %v3713[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3716 = llvm.extractvalue %v3698[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3717 = llvm.insertvalue %v3716, %v3715[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3718 = llvm.extractvalue %v3698[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3719 = llvm.insertvalue %v3718, %v3717[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3720 = llvm.extractvalue %v3698[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3721 = llvm.insertvalue %v3720, %v3719[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3722 = llvm.extractvalue %v3698[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3723 = llvm.insertvalue %v3722, %v3721[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3724 = llvm.extractvalue %v3698[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3725 = llvm.insertvalue %v3724, %v3723[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3726 = func.call @tensor_matmul(%v3725, %v3712) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3727 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3728 = llvm.extractvalue %v3726[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3729 = llvm.insertvalue %v3728, %v3727[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3730 = llvm.extractvalue %v3726[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3731 = llvm.insertvalue %v3730, %v3729[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3732 = llvm.extractvalue %v3726[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3733 = llvm.insertvalue %v3732, %v3731[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3734 = llvm.extractvalue %v3726[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3735 = llvm.insertvalue %v3734, %v3733[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3736 = llvm.mlir.constant(1 : i64) : i64
%v3737 = llvm.alloca %v3736 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3735, %v3737 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3738 = llvm.load %v3737 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3739 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3740 = llvm.extractvalue %v3725[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3741 = llvm.insertvalue %v3740, %v3739[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3742 = llvm.extractvalue %v3725[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3743 = llvm.insertvalue %v3742, %v3741[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3744 = llvm.extractvalue %v3725[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3745 = llvm.insertvalue %v3744, %v3743[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3746 = llvm.extractvalue %v3725[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3747 = llvm.insertvalue %v3746, %v3745[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3748 = llvm.extractvalue %v3725[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3749 = llvm.insertvalue %v3748, %v3747[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3750 = llvm.extractvalue %v3725[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3751 = llvm.insertvalue %v3750, %v3749[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3751, %v3675 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3752 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3753 = llvm.extractvalue %v3712[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3754 = llvm.insertvalue %v3753, %v3752[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3755 = llvm.extractvalue %v3712[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3756 = llvm.insertvalue %v3755, %v3754[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3757 = llvm.extractvalue %v3712[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3758 = llvm.insertvalue %v3757, %v3756[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3759 = llvm.extractvalue %v3712[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3760 = llvm.insertvalue %v3759, %v3758[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3761 = llvm.extractvalue %v3712[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3762 = llvm.insertvalue %v3761, %v3760[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3763 = llvm.extractvalue %v3712[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3764 = llvm.insertvalue %v3763, %v3762[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3764, %v3697 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3765 = llvm.mlir.constant(1 : i64) : i64
%v3766 = llvm.alloca %v3765 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3738, %v3766 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3767 = llvm.load %v3766 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3768 = func.call @tensor_sum(%v3767) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> f32
%v3769 = llvm.load %v3675 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.call @tensor_free(%v3769) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> ()
%v3770 = llvm.load %v3697 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.call @tensor_free(%v3770) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> ()
%v3771 = llvm.load %v3766 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.call @tensor_free(%v3771) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> ()
func.return %v3768 : f32
}
func.func @main() -> i32 {
%v3772 = llvm.mlir.addressof @str_23 : !llvm.ptr
%v3773 = llvm.call @printf(%v3772) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3774 = arith.constant 0 : i32
%v3775 = llvm.mlir.addressof @str_24 : !llvm.ptr
%v3776 = llvm.call @printf(%v3775) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3777 = arith.constant 0 : i32
%v3778 = arith.constant 64 : i32
%v3779 = arith.constant 64 : i32
%v3780 = arith.constant 64 : i32
%v3781 = func.call @bench_matmul(%v3778, %v3779, %v3780) : (i32, i32, i32) -> f32
%v3782 = arith.constant 128 : i32
%v3783 = arith.constant 128 : i32
%v3784 = arith.constant 128 : i32
%v3785 = func.call @bench_matmul(%v3782, %v3783, %v3784) : (i32, i32, i32) -> f32
%v3786 = llvm.mlir.addressof @str_25 : !llvm.ptr
%v3787 = llvm.call @printf(%v3786) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3788 = arith.constant 0 : i32
%v3789 = arith.extf %v3781 : f32 to f64
%v3790 = llvm.mlir.addressof @str_26 : !llvm.ptr
%v3791 = llvm.call @printf(%v3790, %v3789) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v3792 = arith.constant 0 : i32
%v3793 = llvm.mlir.addressof @str_27 : !llvm.ptr
%v3794 = llvm.call @printf(%v3793) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3795 = arith.constant 0 : i32
%v3796 = arith.extf %v3785 : f32 to f64
%v3797 = llvm.mlir.addressof @str_26 : !llvm.ptr
%v3798 = llvm.call @printf(%v3797, %v3796) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v3799 = arith.constant 0 : i32
%v3800 = llvm.mlir.addressof @str_28 : !llvm.ptr
%v3801 = llvm.call @printf(%v3800) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3802 = arith.constant 0 : i32
%v3803 = arith.constant 0 : i32
func.return %v3803 : i32
}
}
