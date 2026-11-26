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
%v1 = llvm.mlir.constant(1 : i64) : i64
%v2 = llvm.alloca %v1 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v3 = arith.muli %arg0, %arg1 : i32
%v4 = arith.muli %v3, %arg2 : i32
%v5 = arith.muli %v4, %arg3 : i32
%v6 = arith.extsi %v5 : i32 to i64
%v7 = arith.constant 4 : i32
%v8 = arith.extsi %v7 : i32 to i64
%v9 = arith.muli %v6, %v8 : i64
%v10 = func.call @flow_mem_malloc(%v9) : (i64) -> !llvm.ptr
%v11 = arith.constant 0 : i32
%v12 = func.call @memset(%v10, %v11, %v9) : (!llvm.ptr, i32, i64) -> !llvm.ptr
%v13 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v14 = llvm.insertvalue %v10, %v13[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v15 = llvm.insertvalue %v5, %v14[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v16 = llvm.insertvalue %arg0, %v15[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v17 = llvm.insertvalue %arg1, %v16[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v18 = llvm.insertvalue %arg2, %v17[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v19 = llvm.insertvalue %arg3, %v18[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v20 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v21 = llvm.extractvalue %v19[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v22 = llvm.insertvalue %v21, %v20[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v23 = llvm.extractvalue %v19[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v24 = llvm.insertvalue %v23, %v22[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v25 = llvm.extractvalue %v19[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v26 = llvm.insertvalue %v25, %v24[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v27 = llvm.extractvalue %v19[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v28 = llvm.insertvalue %v27, %v26[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v29 = llvm.extractvalue %v19[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v30 = llvm.insertvalue %v29, %v28[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v31 = llvm.extractvalue %v19[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v32 = llvm.insertvalue %v31, %v30[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v32, %v2 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v33 = llvm.load %v2 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v33 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_ones(%arg0: i32, %arg1: i32, %arg2: i32, %arg3: i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v34 = llvm.mlir.constant(1 : i64) : i64
%v35 = llvm.alloca %v34 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v36 = llvm.mlir.constant(1 : i64) : i64
%v37 = llvm.alloca %v36 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v38 = llvm.mlir.constant(1 : i64) : i64
%v39 = llvm.alloca %v38 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v40 = func.call @tensor_zeros(%arg0, %arg1, %arg2, %arg3) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v41 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v42 = llvm.extractvalue %v40[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v43 = llvm.insertvalue %v42, %v41[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v44 = llvm.extractvalue %v40[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v45 = llvm.insertvalue %v44, %v43[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v46 = llvm.extractvalue %v40[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v47 = llvm.insertvalue %v46, %v45[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v48 = llvm.extractvalue %v40[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v49 = llvm.insertvalue %v48, %v47[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v50 = llvm.extractvalue %v40[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v51 = llvm.insertvalue %v50, %v49[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v52 = llvm.extractvalue %v40[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v53 = llvm.insertvalue %v52, %v51[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v53, %v35 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v54 = llvm.load %v35 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v54, %v37 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v55 = arith.constant 0 : i32
%v56 = llvm.load %v37 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v57 = llvm.getelementptr %v37[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v58 = llvm.load %v57 : !llvm.ptr -> i32
%v59 = arith.index_cast %v55 : i32 to index
%v60 = arith.index_cast %v58 : i32 to index
%v61 = arith.constant 1 : index
%v62 = arith.constant -1 : index
%v63 = arith.cmpi sle, %v59, %v60 : index
%v64 = arith.select %v63, %v61, %v62 : index
cf.br ^b1(%v59 : index)
^b1(%v65: index):
%v66 = arith.cmpi slt, %v65, %v60 : index
%v67 = arith.cmpi sgt, %v65, %v60 : index
%v68 = arith.select %v63, %v66, %v67 : i1
cf.cond_br %v68, ^b2(%v65 : index), ^b3(%v65 : index)
^b2(%v69: index):
%v70 = arith.constant 1.0 : f64
%v71 = llvm.load %v37 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v72 = llvm.getelementptr %v37[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v73 = llvm.load %v72 : !llvm.ptr -> !llvm.ptr
%v74 = arith.truncf %v70 : f64 to f32
%v75 = arith.index_cast %v69 : index to i64
%v76 = llvm.getelementptr %v73[%v75] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v74, %v76 : f32, !llvm.ptr
%v77 = arith.addi %v69, %v64 : index
cf.br ^b1(%v77 : index)
^b3(%v78: index):
%v79 = llvm.load %v37 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v80 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v81 = llvm.extractvalue %v79[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v82 = llvm.insertvalue %v81, %v80[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v83 = llvm.extractvalue %v79[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v84 = llvm.insertvalue %v83, %v82[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v85 = llvm.extractvalue %v79[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v86 = llvm.insertvalue %v85, %v84[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v87 = llvm.extractvalue %v79[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v88 = llvm.insertvalue %v87, %v86[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v89 = llvm.extractvalue %v79[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v90 = llvm.insertvalue %v89, %v88[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v91 = llvm.extractvalue %v79[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v92 = llvm.insertvalue %v91, %v90[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v92, %v39 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v93 = llvm.load %v39 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v93 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_fill(%arg0: i32, %arg1: i32, %arg2: i32, %arg3: i32, %arg4: f32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v94 = llvm.mlir.constant(1 : i64) : i64
%v95 = llvm.alloca %v94 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v96 = llvm.mlir.constant(1 : i64) : i64
%v97 = llvm.alloca %v96 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v98 = llvm.mlir.constant(1 : i64) : i64
%v99 = llvm.alloca %v98 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v100 = func.call @tensor_zeros(%arg0, %arg1, %arg2, %arg3) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v101 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v102 = llvm.extractvalue %v100[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v103 = llvm.insertvalue %v102, %v101[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v104 = llvm.extractvalue %v100[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v105 = llvm.insertvalue %v104, %v103[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v106 = llvm.extractvalue %v100[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v107 = llvm.insertvalue %v106, %v105[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v108 = llvm.extractvalue %v100[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v109 = llvm.insertvalue %v108, %v107[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v110 = llvm.extractvalue %v100[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v111 = llvm.insertvalue %v110, %v109[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v112 = llvm.extractvalue %v100[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v113 = llvm.insertvalue %v112, %v111[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v113, %v95 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v114 = llvm.load %v95 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v114, %v97 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v115 = arith.constant 0 : i32
%v116 = llvm.load %v97 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v117 = llvm.getelementptr %v97[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v118 = llvm.load %v117 : !llvm.ptr -> i32
%v119 = arith.index_cast %v115 : i32 to index
%v120 = arith.index_cast %v118 : i32 to index
%v121 = arith.constant 1 : index
%v122 = arith.constant -1 : index
%v123 = arith.cmpi sle, %v119, %v120 : index
%v124 = arith.select %v123, %v121, %v122 : index
cf.br ^b4(%v119 : index)
^b4(%v125: index):
%v126 = arith.cmpi slt, %v125, %v120 : index
%v127 = arith.cmpi sgt, %v125, %v120 : index
%v128 = arith.select %v123, %v126, %v127 : i1
cf.cond_br %v128, ^b5(%v125 : index), ^b6(%v125 : index)
^b5(%v129: index):
%v130 = llvm.load %v97 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v131 = llvm.getelementptr %v97[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v132 = llvm.load %v131 : !llvm.ptr -> !llvm.ptr
%v133 = arith.index_cast %v129 : index to i64
%v134 = llvm.getelementptr %v132[%v133] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %arg4, %v134 : f32, !llvm.ptr
%v135 = arith.addi %v129, %v124 : index
cf.br ^b4(%v135 : index)
^b6(%v136: index):
%v137 = llvm.load %v97 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v138 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v139 = llvm.extractvalue %v137[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v140 = llvm.insertvalue %v139, %v138[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v141 = llvm.extractvalue %v137[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v142 = llvm.insertvalue %v141, %v140[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v143 = llvm.extractvalue %v137[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v144 = llvm.insertvalue %v143, %v142[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v145 = llvm.extractvalue %v137[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v146 = llvm.insertvalue %v145, %v144[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v147 = llvm.extractvalue %v137[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v148 = llvm.insertvalue %v147, %v146[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v149 = llvm.extractvalue %v137[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v150 = llvm.insertvalue %v149, %v148[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v150, %v99 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v151 = llvm.load %v99 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v151 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_rand(%arg0: i32, %arg1: i32, %arg2: i32, %arg3: i32, %arg4: i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v152 = llvm.mlir.constant(1 : i64) : i64
%v153 = llvm.alloca %v152 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v154 = llvm.mlir.constant(1 : i64) : i64
%v155 = llvm.alloca %v154 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v156 = llvm.mlir.constant(1 : i64) : i64
%v157 = llvm.alloca %v156 x i32 : (i64) -> !llvm.ptr
%v158 = llvm.mlir.constant(1 : i64) : i64
%v159 = llvm.alloca %v158 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v160 = func.call @tensor_zeros(%arg0, %arg1, %arg2, %arg3) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v161 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v162 = llvm.extractvalue %v160[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v163 = llvm.insertvalue %v162, %v161[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v164 = llvm.extractvalue %v160[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v165 = llvm.insertvalue %v164, %v163[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v166 = llvm.extractvalue %v160[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v167 = llvm.insertvalue %v166, %v165[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v168 = llvm.extractvalue %v160[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v169 = llvm.insertvalue %v168, %v167[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v170 = llvm.extractvalue %v160[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v171 = llvm.insertvalue %v170, %v169[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v172 = llvm.extractvalue %v160[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v173 = llvm.insertvalue %v172, %v171[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v173, %v153 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v174 = llvm.load %v153 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v174, %v155 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
llvm.store %arg4, %v157 : i32, !llvm.ptr
%v175 = arith.constant 0 : i32
%v176 = llvm.load %v155 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v177 = llvm.getelementptr %v155[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v178 = llvm.load %v177 : !llvm.ptr -> i32
%v179 = arith.index_cast %v175 : i32 to index
%v180 = arith.index_cast %v178 : i32 to index
%v181 = arith.constant 1 : index
%v182 = arith.constant -1 : index
%v183 = arith.cmpi sle, %v179, %v180 : index
%v184 = arith.select %v183, %v181, %v182 : index
cf.br ^b7(%v179 : index)
^b7(%v185: index):
%v186 = arith.cmpi slt, %v185, %v180 : index
%v187 = arith.cmpi sgt, %v185, %v180 : index
%v188 = arith.select %v183, %v186, %v187 : i1
cf.cond_br %v188, ^b8(%v185 : index), ^b9(%v185 : index)
^b8(%v189: index):
%v190 = llvm.load %v157 : !llvm.ptr -> i32
%v191 = arith.constant 1103515245 : i32
%v192 = arith.muli %v190, %v191 : i32
%v193 = arith.constant 12345 : i32
%v194 = arith.addi %v192, %v193 : i32
%v195 = arith.constant 2147483647 : i32
%v196 = arith.constant 0 : i32
%v197 = arith.cmpi eq, %v195, %v196 : i32
scf.if %v197 {
%v198 = llvm.mlir.addressof @str_14 : !llvm.ptr
func.call @__flow_fault(%v198) : (!llvm.ptr) -> ()
}
%v199 = arith.remsi %v194, %v195 : i32
llvm.store %v199, %v157 : i32, !llvm.ptr
%v200 = llvm.load %v157 : !llvm.ptr -> i32
%v201 = arith.constant 0 : i32
%v202 = arith.cmpi slt, %v200, %v201 : i32
cf.cond_br %v202, ^b10, ^b11
^b10:
%v203 = arith.constant 0 : i32
%v204 = llvm.load %v157 : !llvm.ptr -> i32
%v205 = arith.subi %v203, %v204 : i32
llvm.store %v205, %v157 : i32, !llvm.ptr
cf.br ^b12
^b11:
cf.br ^b12
^b12:
%v206 = llvm.load %v157 : !llvm.ptr -> i32
%v207 = arith.constant 10000 : i32
%v208 = arith.constant 0 : i32
%v209 = arith.cmpi eq, %v207, %v208 : i32
scf.if %v209 {
%v210 = llvm.mlir.addressof @str_14 : !llvm.ptr
func.call @__flow_fault(%v210) : (!llvm.ptr) -> ()
}
%v211 = arith.remsi %v206, %v207 : i32
%v212 = arith.constant 10000.0 : f64
%v213 = arith.sitofp %v211 : i32 to f64
%v214 = arith.divf %v213, %v212 : f64
%v215 = llvm.load %v155 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v216 = llvm.getelementptr %v155[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v217 = llvm.load %v216 : !llvm.ptr -> !llvm.ptr
%v218 = arith.truncf %v214 : f64 to f32
%v219 = arith.index_cast %v189 : index to i64
%v220 = llvm.getelementptr %v217[%v219] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v218, %v220 : f32, !llvm.ptr
%v221 = arith.addi %v189, %v184 : index
cf.br ^b7(%v221 : index)
^b9(%v222: index):
%v223 = llvm.load %v155 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v224 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v225 = llvm.extractvalue %v223[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v226 = llvm.insertvalue %v225, %v224[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v227 = llvm.extractvalue %v223[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v228 = llvm.insertvalue %v227, %v226[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v229 = llvm.extractvalue %v223[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v230 = llvm.insertvalue %v229, %v228[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v231 = llvm.extractvalue %v223[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v232 = llvm.insertvalue %v231, %v230[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v233 = llvm.extractvalue %v223[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v234 = llvm.insertvalue %v233, %v232[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v235 = llvm.extractvalue %v223[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v236 = llvm.insertvalue %v235, %v234[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v236, %v159 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v237 = llvm.load %v159 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v237 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_randn(%arg0: i32, %arg1: i32, %arg2: i32, %arg3: i32, %arg4: i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v238 = llvm.mlir.constant(1 : i64) : i64
%v239 = llvm.alloca %v238 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v240 = llvm.mlir.constant(1 : i64) : i64
%v241 = llvm.alloca %v240 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v242 = llvm.mlir.constant(1 : i64) : i64
%v243 = llvm.alloca %v242 x i32 : (i64) -> !llvm.ptr
%v244 = llvm.mlir.constant(1 : i64) : i64
%v245 = llvm.alloca %v244 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v246 = func.call @tensor_zeros(%arg0, %arg1, %arg2, %arg3) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v247 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v248 = llvm.extractvalue %v246[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v249 = llvm.insertvalue %v248, %v247[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v250 = llvm.extractvalue %v246[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v251 = llvm.insertvalue %v250, %v249[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v252 = llvm.extractvalue %v246[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v253 = llvm.insertvalue %v252, %v251[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v254 = llvm.extractvalue %v246[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v255 = llvm.insertvalue %v254, %v253[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v256 = llvm.extractvalue %v246[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v257 = llvm.insertvalue %v256, %v255[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v258 = llvm.extractvalue %v246[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v259 = llvm.insertvalue %v258, %v257[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v259, %v239 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v260 = llvm.load %v239 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v260, %v241 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
llvm.store %arg4, %v243 : i32, !llvm.ptr
%v261 = arith.constant 0 : i32
%v262 = llvm.load %v241 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v263 = llvm.getelementptr %v241[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v264 = llvm.load %v263 : !llvm.ptr -> i32
%v265 = arith.index_cast %v261 : i32 to index
%v266 = arith.index_cast %v264 : i32 to index
%v267 = arith.constant 1 : index
%v268 = arith.constant -1 : index
%v269 = arith.cmpi sle, %v265, %v266 : index
%v270 = arith.select %v269, %v267, %v268 : index
cf.br ^b13(%v265 : index)
^b13(%v271: index):
%v272 = arith.cmpi slt, %v271, %v266 : index
%v273 = arith.cmpi sgt, %v271, %v266 : index
%v274 = arith.select %v269, %v272, %v273 : i1
cf.cond_br %v274, ^b14(%v271 : index), ^b15(%v271 : index)
^b14(%v275: index):
%v276 = llvm.load %v243 : !llvm.ptr -> i32
%v277 = arith.constant 1103515245 : i32
%v278 = arith.muli %v276, %v277 : i32
%v279 = arith.constant 12345 : i32
%v280 = arith.addi %v278, %v279 : i32
%v281 = arith.constant 2147483647 : i32
%v282 = arith.constant 0 : i32
%v283 = arith.cmpi eq, %v281, %v282 : i32
scf.if %v283 {
%v284 = llvm.mlir.addressof @str_14 : !llvm.ptr
func.call @__flow_fault(%v284) : (!llvm.ptr) -> ()
}
%v285 = arith.remsi %v280, %v281 : i32
llvm.store %v285, %v243 : i32, !llvm.ptr
%v286 = llvm.load %v243 : !llvm.ptr -> i32
%v287 = arith.constant 0 : i32
%v288 = arith.cmpi slt, %v286, %v287 : i32
cf.cond_br %v288, ^b16, ^b17
^b16:
%v289 = arith.constant 0 : i32
%v290 = llvm.load %v243 : !llvm.ptr -> i32
%v291 = arith.subi %v289, %v290 : i32
llvm.store %v291, %v243 : i32, !llvm.ptr
cf.br ^b18
^b17:
cf.br ^b18
^b18:
%v292 = llvm.load %v243 : !llvm.ptr -> i32
%v293 = arith.constant 10000 : i32
%v294 = arith.constant 0 : i32
%v295 = arith.cmpi eq, %v293, %v294 : i32
scf.if %v295 {
%v296 = llvm.mlir.addressof @str_14 : !llvm.ptr
func.call @__flow_fault(%v296) : (!llvm.ptr) -> ()
}
%v297 = arith.remsi %v292, %v293 : i32
%v298 = arith.constant 1 : i32
%v299 = arith.addi %v297, %v298 : i32
%v300 = arith.constant 10001.0 : f64
%v301 = arith.sitofp %v299 : i32 to f64
%v302 = arith.divf %v301, %v300 : f64
%v303 = llvm.load %v243 : !llvm.ptr -> i32
%v304 = arith.constant 1103515245 : i32
%v305 = arith.muli %v303, %v304 : i32
%v306 = arith.constant 12345 : i32
%v307 = arith.addi %v305, %v306 : i32
%v308 = arith.constant 2147483647 : i32
%v309 = arith.constant 0 : i32
%v310 = arith.cmpi eq, %v308, %v309 : i32
scf.if %v310 {
%v311 = llvm.mlir.addressof @str_14 : !llvm.ptr
func.call @__flow_fault(%v311) : (!llvm.ptr) -> ()
}
%v312 = arith.remsi %v307, %v308 : i32
llvm.store %v312, %v243 : i32, !llvm.ptr
%v313 = llvm.load %v243 : !llvm.ptr -> i32
%v314 = arith.constant 0 : i32
%v315 = arith.cmpi slt, %v313, %v314 : i32
cf.cond_br %v315, ^b19, ^b20
^b19:
%v316 = arith.constant 0 : i32
%v317 = llvm.load %v243 : !llvm.ptr -> i32
%v318 = arith.subi %v316, %v317 : i32
llvm.store %v318, %v243 : i32, !llvm.ptr
cf.br ^b21
^b20:
cf.br ^b21
^b21:
%v319 = llvm.load %v243 : !llvm.ptr -> i32
%v320 = arith.constant 10000 : i32
%v321 = arith.constant 0 : i32
%v322 = arith.cmpi eq, %v320, %v321 : i32
scf.if %v322 {
%v323 = llvm.mlir.addressof @str_14 : !llvm.ptr
func.call @__flow_fault(%v323) : (!llvm.ptr) -> ()
}
%v324 = arith.remsi %v319, %v320 : i32
%v325 = arith.constant 10000.0 : f64
%v326 = arith.sitofp %v324 : i32 to f64
%v327 = arith.divf %v326, %v325 : f64
%v328 = arith.constant 0.0 : f64
%v329 = arith.constant 2.0 : f64
%v330 = func.call @log(%v302) : (f64) -> f64
%v331 = arith.negf %v329 : f64
%v332 = llvm.intr.fmuladd(%v331, %v330, %v328) : (f64, f64, f64) -> f64
%v333 = func.call @sqrt(%v332) : (f64) -> f64
%v334 = arith.constant 0.5 : f64
%v335 = arith.mulf %v333, %v334 : f64
%v336 = llvm.load %v241 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v337 = llvm.getelementptr %v241[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v338 = llvm.load %v337 : !llvm.ptr -> !llvm.ptr
%v339 = arith.truncf %v335 : f64 to f32
%v340 = arith.index_cast %v275 : index to i64
%v341 = llvm.getelementptr %v338[%v340] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v339, %v341 : f32, !llvm.ptr
%v342 = arith.addi %v275, %v270 : index
cf.br ^b13(%v342 : index)
^b15(%v343: index):
%v344 = llvm.load %v241 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v345 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v346 = llvm.extractvalue %v344[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v347 = llvm.insertvalue %v346, %v345[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v348 = llvm.extractvalue %v344[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v349 = llvm.insertvalue %v348, %v347[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v350 = llvm.extractvalue %v344[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v351 = llvm.insertvalue %v350, %v349[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v352 = llvm.extractvalue %v344[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v353 = llvm.insertvalue %v352, %v351[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v354 = llvm.extractvalue %v344[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v355 = llvm.insertvalue %v354, %v353[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v356 = llvm.extractvalue %v344[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v357 = llvm.insertvalue %v356, %v355[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v357, %v245 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v358 = llvm.load %v245 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v358 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_free(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> () {
%v359 = llvm.mlir.constant(1 : i64) : i64
%v360 = llvm.alloca %v359 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v361 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v362 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v363 = llvm.insertvalue %v362, %v361[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v364 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v365 = llvm.insertvalue %v364, %v363[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v366 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v367 = llvm.insertvalue %v366, %v365[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v368 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v369 = llvm.insertvalue %v368, %v367[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v370 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v371 = llvm.insertvalue %v370, %v369[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v372 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v373 = llvm.insertvalue %v372, %v371[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v373, %v360 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v374 = llvm.load %v360 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v375 = llvm.getelementptr %v360[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v376 = llvm.load %v375 : !llvm.ptr -> !llvm.ptr
func.call @flow_mem_free(%v376) : (!llvm.ptr) -> ()
func.return
}
func.func @tensor_idx(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: i32, %arg2: i32, %arg3: i32, %arg4: i32) -> i32 {
%v377 = llvm.mlir.constant(1 : i64) : i64
%v378 = llvm.alloca %v377 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v379 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v380 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v381 = llvm.insertvalue %v380, %v379[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v382 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v383 = llvm.insertvalue %v382, %v381[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v384 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v385 = llvm.insertvalue %v384, %v383[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v386 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v387 = llvm.insertvalue %v386, %v385[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v388 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v389 = llvm.insertvalue %v388, %v387[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v390 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v391 = llvm.insertvalue %v390, %v389[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v391, %v378 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v392 = llvm.load %v378 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v393 = llvm.getelementptr %v378[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v394 = llvm.load %v393 : !llvm.ptr -> i32
%v395 = arith.muli %arg1, %v394 : i32
%v396 = arith.addi %v395, %arg2 : i32
%v397 = llvm.load %v378 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v398 = llvm.getelementptr %v378[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v399 = llvm.load %v398 : !llvm.ptr -> i32
%v400 = arith.muli %v396, %v399 : i32
%v401 = arith.addi %v400, %arg3 : i32
%v402 = llvm.load %v378 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v403 = llvm.getelementptr %v378[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v404 = llvm.load %v403 : !llvm.ptr -> i32
%v405 = arith.muli %v401, %v404 : i32
%v406 = arith.addi %v405, %arg4 : i32
func.return %v406 : i32
}
func.func @tensor_get(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: i32, %arg2: i32, %arg3: i32, %arg4: i32) -> f32 {
%v407 = llvm.mlir.constant(1 : i64) : i64
%v408 = llvm.alloca %v407 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v409 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v410 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v411 = llvm.insertvalue %v410, %v409[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v412 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v413 = llvm.insertvalue %v412, %v411[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v414 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v415 = llvm.insertvalue %v414, %v413[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v416 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v417 = llvm.insertvalue %v416, %v415[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v418 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v419 = llvm.insertvalue %v418, %v417[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v420 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v421 = llvm.insertvalue %v420, %v419[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v421, %v408 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v422 = llvm.load %v408 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v423 = llvm.getelementptr %v408[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v424 = llvm.load %v423 : !llvm.ptr -> !llvm.ptr
%v425 = llvm.load %v408 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v426 = func.call @tensor_idx(%v425, %arg1, %arg2, %arg3, %arg4) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, i32, i32, i32, i32) -> i32
%v427 = arith.extsi %v426 : i32 to i64
%v428 = llvm.getelementptr %v424[%v427] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v429 = llvm.load %v428 : !llvm.ptr -> f32
func.return %v429 : f32
}
func.func @tensor_set(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: i32, %arg2: i32, %arg3: i32, %arg4: i32, %arg5: f32) -> () {
%v430 = llvm.mlir.constant(1 : i64) : i64
%v431 = llvm.alloca %v430 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v432 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v433 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v434 = llvm.insertvalue %v433, %v432[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v435 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v436 = llvm.insertvalue %v435, %v434[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v437 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v438 = llvm.insertvalue %v437, %v436[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v439 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v440 = llvm.insertvalue %v439, %v438[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v441 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v442 = llvm.insertvalue %v441, %v440[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v443 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v444 = llvm.insertvalue %v443, %v442[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v444, %v431 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v445 = llvm.load %v431 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v446 = llvm.getelementptr %v431[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v447 = llvm.load %v446 : !llvm.ptr -> !llvm.ptr
%v448 = llvm.load %v431 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v449 = func.call @tensor_idx(%v448, %arg1, %arg2, %arg3, %arg4) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, i32, i32, i32, i32) -> i32
%v450 = arith.extsi %v449 : i32 to i64
%v451 = llvm.getelementptr %v447[%v450] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %arg5, %v451 : f32, !llvm.ptr
func.return
}
func.func @tensor_get2(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: i32, %arg2: i32) -> f32 {
%v452 = llvm.mlir.constant(1 : i64) : i64
%v453 = llvm.alloca %v452 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v454 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v455 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v456 = llvm.insertvalue %v455, %v454[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v457 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v458 = llvm.insertvalue %v457, %v456[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v459 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v460 = llvm.insertvalue %v459, %v458[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v461 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v462 = llvm.insertvalue %v461, %v460[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v463 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v464 = llvm.insertvalue %v463, %v462[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v465 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v466 = llvm.insertvalue %v465, %v464[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v466, %v453 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v467 = llvm.load %v453 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v468 = llvm.getelementptr %v453[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v469 = llvm.load %v468 : !llvm.ptr -> !llvm.ptr
%v470 = llvm.load %v453 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v471 = llvm.getelementptr %v453[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v472 = llvm.load %v471 : !llvm.ptr -> i32
%v473 = arith.muli %arg1, %v472 : i32
%v474 = arith.addi %v473, %arg2 : i32
%v475 = arith.extsi %v474 : i32 to i64
%v476 = llvm.getelementptr %v469[%v475] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v477 = llvm.load %v476 : !llvm.ptr -> f32
func.return %v477 : f32
}
func.func @tensor_set2(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: i32, %arg2: i32, %arg3: f32) -> () {
%v478 = llvm.mlir.constant(1 : i64) : i64
%v479 = llvm.alloca %v478 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v480 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v481 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v482 = llvm.insertvalue %v481, %v480[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v483 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v484 = llvm.insertvalue %v483, %v482[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v485 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v486 = llvm.insertvalue %v485, %v484[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v487 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v488 = llvm.insertvalue %v487, %v486[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v489 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v490 = llvm.insertvalue %v489, %v488[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v491 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v492 = llvm.insertvalue %v491, %v490[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v492, %v479 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v493 = llvm.load %v479 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v494 = llvm.getelementptr %v479[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v495 = llvm.load %v494 : !llvm.ptr -> !llvm.ptr
%v496 = llvm.load %v479 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v497 = llvm.getelementptr %v479[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v498 = llvm.load %v497 : !llvm.ptr -> i32
%v499 = arith.muli %arg1, %v498 : i32
%v500 = arith.addi %v499, %arg2 : i32
%v501 = arith.extsi %v500 : i32 to i64
%v502 = llvm.getelementptr %v495[%v501] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %arg3, %v502 : f32, !llvm.ptr
func.return
}
func.func @tensor_get1(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: i32) -> f32 {
%v503 = llvm.mlir.constant(1 : i64) : i64
%v504 = llvm.alloca %v503 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v505 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v506 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v507 = llvm.insertvalue %v506, %v505[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v508 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v509 = llvm.insertvalue %v508, %v507[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v510 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v511 = llvm.insertvalue %v510, %v509[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v512 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v513 = llvm.insertvalue %v512, %v511[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v514 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v515 = llvm.insertvalue %v514, %v513[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v516 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v517 = llvm.insertvalue %v516, %v515[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v517, %v504 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v518 = llvm.load %v504 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v519 = llvm.getelementptr %v504[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v520 = llvm.load %v519 : !llvm.ptr -> !llvm.ptr
%v521 = arith.extsi %arg1 : i32 to i64
%v522 = llvm.getelementptr %v520[%v521] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v523 = llvm.load %v522 : !llvm.ptr -> f32
func.return %v523 : f32
}
func.func @tensor_set1(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: i32, %arg2: f32) -> () {
%v524 = llvm.mlir.constant(1 : i64) : i64
%v525 = llvm.alloca %v524 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v526 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v527 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v528 = llvm.insertvalue %v527, %v526[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v529 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v530 = llvm.insertvalue %v529, %v528[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v531 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v532 = llvm.insertvalue %v531, %v530[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v533 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v534 = llvm.insertvalue %v533, %v532[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v535 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v536 = llvm.insertvalue %v535, %v534[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v537 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v538 = llvm.insertvalue %v537, %v536[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v538, %v525 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v539 = llvm.load %v525 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v540 = llvm.getelementptr %v525[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v541 = llvm.load %v540 : !llvm.ptr -> !llvm.ptr
%v542 = arith.extsi %arg1 : i32 to i64
%v543 = llvm.getelementptr %v541[%v542] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %arg2, %v543 : f32, !llvm.ptr
func.return
}
func.func @tensor_add(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v544 = llvm.mlir.constant(1 : i64) : i64
%v545 = llvm.alloca %v544 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v546 = llvm.mlir.constant(1 : i64) : i64
%v547 = llvm.alloca %v546 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v548 = llvm.mlir.constant(1 : i64) : i64
%v549 = llvm.alloca %v548 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v550 = llvm.mlir.constant(1 : i64) : i64
%v551 = llvm.alloca %v550 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v552 = llvm.mlir.constant(1 : i64) : i64
%v553 = llvm.alloca %v552 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v554 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v555 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v556 = llvm.insertvalue %v555, %v554[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v557 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v558 = llvm.insertvalue %v557, %v556[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v559 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v560 = llvm.insertvalue %v559, %v558[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v561 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v562 = llvm.insertvalue %v561, %v560[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v563 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v564 = llvm.insertvalue %v563, %v562[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v565 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v566 = llvm.insertvalue %v565, %v564[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v566, %v545 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v567 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v568 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v569 = llvm.insertvalue %v568, %v567[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v570 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v571 = llvm.insertvalue %v570, %v569[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v572 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v573 = llvm.insertvalue %v572, %v571[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v574 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v575 = llvm.insertvalue %v574, %v573[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v576 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v577 = llvm.insertvalue %v576, %v575[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v578 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v579 = llvm.insertvalue %v578, %v577[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v579, %v547 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v580 = llvm.load %v545 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v581 = llvm.getelementptr %v545[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v582 = llvm.load %v581 : !llvm.ptr -> i32
%v583 = llvm.load %v545 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v584 = llvm.getelementptr %v545[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v585 = llvm.load %v584 : !llvm.ptr -> i32
%v586 = llvm.load %v545 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v587 = llvm.getelementptr %v545[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v588 = llvm.load %v587 : !llvm.ptr -> i32
%v589 = llvm.load %v545 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v590 = llvm.getelementptr %v545[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v591 = llvm.load %v590 : !llvm.ptr -> i32
%v592 = func.call @tensor_zeros(%v582, %v585, %v588, %v591) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v593 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v594 = llvm.extractvalue %v592[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v595 = llvm.insertvalue %v594, %v593[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v596 = llvm.extractvalue %v592[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v597 = llvm.insertvalue %v596, %v595[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v598 = llvm.extractvalue %v592[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v599 = llvm.insertvalue %v598, %v597[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v600 = llvm.extractvalue %v592[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v601 = llvm.insertvalue %v600, %v599[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v602 = llvm.extractvalue %v592[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v603 = llvm.insertvalue %v602, %v601[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v604 = llvm.extractvalue %v592[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v605 = llvm.insertvalue %v604, %v603[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v605, %v549 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v606 = llvm.load %v549 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v606, %v551 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v607 = arith.constant 0 : i32
%v608 = llvm.load %v545 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v609 = llvm.getelementptr %v545[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v610 = llvm.load %v609 : !llvm.ptr -> i32
%v611 = arith.index_cast %v607 : i32 to index
%v612 = arith.index_cast %v610 : i32 to index
%v613 = arith.constant 1 : index
%v614 = arith.constant -1 : index
%v615 = arith.cmpi sle, %v611, %v612 : index
%v616 = arith.select %v615, %v613, %v614 : index
cf.br ^b22(%v611 : index)
^b22(%v617: index):
%v618 = arith.cmpi slt, %v617, %v612 : index
%v619 = arith.cmpi sgt, %v617, %v612 : index
%v620 = arith.select %v615, %v618, %v619 : i1
cf.cond_br %v620, ^b23(%v617 : index), ^b24(%v617 : index)
^b23(%v621: index):
%v622 = llvm.load %v545 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v623 = llvm.getelementptr %v545[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v624 = llvm.load %v623 : !llvm.ptr -> !llvm.ptr
%v625 = arith.index_cast %v621 : index to i64
%v626 = llvm.getelementptr %v624[%v625] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v627 = llvm.load %v626 : !llvm.ptr -> f32
%v628 = llvm.load %v547 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v629 = llvm.getelementptr %v547[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v630 = llvm.load %v629 : !llvm.ptr -> !llvm.ptr
%v631 = arith.index_cast %v621 : index to i64
%v632 = llvm.getelementptr %v630[%v631] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v633 = llvm.load %v632 : !llvm.ptr -> f32
%v634 = arith.addf %v627, %v633 : f32
%v635 = llvm.load %v551 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v636 = llvm.getelementptr %v551[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v637 = llvm.load %v636 : !llvm.ptr -> !llvm.ptr
%v638 = arith.index_cast %v621 : index to i64
%v639 = llvm.getelementptr %v637[%v638] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v634, %v639 : f32, !llvm.ptr
%v640 = arith.addi %v621, %v616 : index
cf.br ^b22(%v640 : index)
^b24(%v641: index):
%v642 = llvm.load %v551 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v643 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v644 = llvm.extractvalue %v642[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v645 = llvm.insertvalue %v644, %v643[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v646 = llvm.extractvalue %v642[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v647 = llvm.insertvalue %v646, %v645[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v648 = llvm.extractvalue %v642[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v649 = llvm.insertvalue %v648, %v647[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v650 = llvm.extractvalue %v642[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v651 = llvm.insertvalue %v650, %v649[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v652 = llvm.extractvalue %v642[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v653 = llvm.insertvalue %v652, %v651[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v654 = llvm.extractvalue %v642[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v655 = llvm.insertvalue %v654, %v653[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v655, %v553 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v656 = llvm.load %v553 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v656 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_sub(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v657 = llvm.mlir.constant(1 : i64) : i64
%v658 = llvm.alloca %v657 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v659 = llvm.mlir.constant(1 : i64) : i64
%v660 = llvm.alloca %v659 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v661 = llvm.mlir.constant(1 : i64) : i64
%v662 = llvm.alloca %v661 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v663 = llvm.mlir.constant(1 : i64) : i64
%v664 = llvm.alloca %v663 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v665 = llvm.mlir.constant(1 : i64) : i64
%v666 = llvm.alloca %v665 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v667 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v668 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v669 = llvm.insertvalue %v668, %v667[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v670 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v671 = llvm.insertvalue %v670, %v669[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v672 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v673 = llvm.insertvalue %v672, %v671[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v674 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v675 = llvm.insertvalue %v674, %v673[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v676 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v677 = llvm.insertvalue %v676, %v675[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v678 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v679 = llvm.insertvalue %v678, %v677[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v679, %v658 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v680 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v681 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v682 = llvm.insertvalue %v681, %v680[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v683 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v684 = llvm.insertvalue %v683, %v682[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v685 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v686 = llvm.insertvalue %v685, %v684[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v687 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v688 = llvm.insertvalue %v687, %v686[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v689 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v690 = llvm.insertvalue %v689, %v688[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v691 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v692 = llvm.insertvalue %v691, %v690[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v692, %v660 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v693 = llvm.load %v658 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v694 = llvm.getelementptr %v658[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v695 = llvm.load %v694 : !llvm.ptr -> i32
%v696 = llvm.load %v658 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v697 = llvm.getelementptr %v658[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v698 = llvm.load %v697 : !llvm.ptr -> i32
%v699 = llvm.load %v658 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v700 = llvm.getelementptr %v658[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v701 = llvm.load %v700 : !llvm.ptr -> i32
%v702 = llvm.load %v658 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v703 = llvm.getelementptr %v658[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v704 = llvm.load %v703 : !llvm.ptr -> i32
%v705 = func.call @tensor_zeros(%v695, %v698, %v701, %v704) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v706 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v707 = llvm.extractvalue %v705[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v708 = llvm.insertvalue %v707, %v706[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v709 = llvm.extractvalue %v705[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v710 = llvm.insertvalue %v709, %v708[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v711 = llvm.extractvalue %v705[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v712 = llvm.insertvalue %v711, %v710[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v713 = llvm.extractvalue %v705[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v714 = llvm.insertvalue %v713, %v712[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v715 = llvm.extractvalue %v705[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v716 = llvm.insertvalue %v715, %v714[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v717 = llvm.extractvalue %v705[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v718 = llvm.insertvalue %v717, %v716[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v718, %v662 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v719 = llvm.load %v662 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v719, %v664 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v720 = arith.constant 0 : i32
%v721 = llvm.load %v658 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v722 = llvm.getelementptr %v658[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v723 = llvm.load %v722 : !llvm.ptr -> i32
%v724 = arith.index_cast %v720 : i32 to index
%v725 = arith.index_cast %v723 : i32 to index
%v726 = arith.constant 1 : index
%v727 = arith.constant -1 : index
%v728 = arith.cmpi sle, %v724, %v725 : index
%v729 = arith.select %v728, %v726, %v727 : index
cf.br ^b25(%v724 : index)
^b25(%v730: index):
%v731 = arith.cmpi slt, %v730, %v725 : index
%v732 = arith.cmpi sgt, %v730, %v725 : index
%v733 = arith.select %v728, %v731, %v732 : i1
cf.cond_br %v733, ^b26(%v730 : index), ^b27(%v730 : index)
^b26(%v734: index):
%v735 = llvm.load %v658 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v736 = llvm.getelementptr %v658[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v737 = llvm.load %v736 : !llvm.ptr -> !llvm.ptr
%v738 = arith.index_cast %v734 : index to i64
%v739 = llvm.getelementptr %v737[%v738] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v740 = llvm.load %v739 : !llvm.ptr -> f32
%v741 = llvm.load %v660 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v742 = llvm.getelementptr %v660[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v743 = llvm.load %v742 : !llvm.ptr -> !llvm.ptr
%v744 = arith.index_cast %v734 : index to i64
%v745 = llvm.getelementptr %v743[%v744] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v746 = llvm.load %v745 : !llvm.ptr -> f32
%v747 = arith.subf %v740, %v746 : f32
%v748 = llvm.load %v664 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v749 = llvm.getelementptr %v664[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v750 = llvm.load %v749 : !llvm.ptr -> !llvm.ptr
%v751 = arith.index_cast %v734 : index to i64
%v752 = llvm.getelementptr %v750[%v751] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v747, %v752 : f32, !llvm.ptr
%v753 = arith.addi %v734, %v729 : index
cf.br ^b25(%v753 : index)
^b27(%v754: index):
%v755 = llvm.load %v664 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v756 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v757 = llvm.extractvalue %v755[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v758 = llvm.insertvalue %v757, %v756[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v759 = llvm.extractvalue %v755[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v760 = llvm.insertvalue %v759, %v758[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v761 = llvm.extractvalue %v755[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v762 = llvm.insertvalue %v761, %v760[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v763 = llvm.extractvalue %v755[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v764 = llvm.insertvalue %v763, %v762[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v765 = llvm.extractvalue %v755[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v766 = llvm.insertvalue %v765, %v764[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v767 = llvm.extractvalue %v755[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v768 = llvm.insertvalue %v767, %v766[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v768, %v666 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v769 = llvm.load %v666 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v769 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_mul(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v770 = llvm.mlir.constant(1 : i64) : i64
%v771 = llvm.alloca %v770 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v772 = llvm.mlir.constant(1 : i64) : i64
%v773 = llvm.alloca %v772 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v774 = llvm.mlir.constant(1 : i64) : i64
%v775 = llvm.alloca %v774 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v776 = llvm.mlir.constant(1 : i64) : i64
%v777 = llvm.alloca %v776 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v778 = llvm.mlir.constant(1 : i64) : i64
%v779 = llvm.alloca %v778 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v780 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v781 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v782 = llvm.insertvalue %v781, %v780[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v783 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v784 = llvm.insertvalue %v783, %v782[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v785 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v786 = llvm.insertvalue %v785, %v784[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v787 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v788 = llvm.insertvalue %v787, %v786[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v789 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v790 = llvm.insertvalue %v789, %v788[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v791 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v792 = llvm.insertvalue %v791, %v790[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v792, %v771 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v793 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v794 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v795 = llvm.insertvalue %v794, %v793[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v796 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v797 = llvm.insertvalue %v796, %v795[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v798 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v799 = llvm.insertvalue %v798, %v797[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v800 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v801 = llvm.insertvalue %v800, %v799[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v802 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v803 = llvm.insertvalue %v802, %v801[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v804 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v805 = llvm.insertvalue %v804, %v803[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v805, %v773 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v806 = llvm.load %v771 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v807 = llvm.getelementptr %v771[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v808 = llvm.load %v807 : !llvm.ptr -> i32
%v809 = llvm.load %v771 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v810 = llvm.getelementptr %v771[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v811 = llvm.load %v810 : !llvm.ptr -> i32
%v812 = llvm.load %v771 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v813 = llvm.getelementptr %v771[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v814 = llvm.load %v813 : !llvm.ptr -> i32
%v815 = llvm.load %v771 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v816 = llvm.getelementptr %v771[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v817 = llvm.load %v816 : !llvm.ptr -> i32
%v818 = func.call @tensor_zeros(%v808, %v811, %v814, %v817) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v819 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v820 = llvm.extractvalue %v818[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v821 = llvm.insertvalue %v820, %v819[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v822 = llvm.extractvalue %v818[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v823 = llvm.insertvalue %v822, %v821[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v824 = llvm.extractvalue %v818[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v825 = llvm.insertvalue %v824, %v823[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v826 = llvm.extractvalue %v818[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v827 = llvm.insertvalue %v826, %v825[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v828 = llvm.extractvalue %v818[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v829 = llvm.insertvalue %v828, %v827[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v830 = llvm.extractvalue %v818[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v831 = llvm.insertvalue %v830, %v829[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v831, %v775 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v832 = llvm.load %v775 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v832, %v777 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v833 = arith.constant 0 : i32
%v834 = llvm.load %v771 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v835 = llvm.getelementptr %v771[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v836 = llvm.load %v835 : !llvm.ptr -> i32
%v837 = arith.index_cast %v833 : i32 to index
%v838 = arith.index_cast %v836 : i32 to index
%v839 = arith.constant 1 : index
%v840 = arith.constant -1 : index
%v841 = arith.cmpi sle, %v837, %v838 : index
%v842 = arith.select %v841, %v839, %v840 : index
cf.br ^b28(%v837 : index)
^b28(%v843: index):
%v844 = arith.cmpi slt, %v843, %v838 : index
%v845 = arith.cmpi sgt, %v843, %v838 : index
%v846 = arith.select %v841, %v844, %v845 : i1
cf.cond_br %v846, ^b29(%v843 : index), ^b30(%v843 : index)
^b29(%v847: index):
%v848 = llvm.load %v771 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v849 = llvm.getelementptr %v771[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v850 = llvm.load %v849 : !llvm.ptr -> !llvm.ptr
%v851 = arith.index_cast %v847 : index to i64
%v852 = llvm.getelementptr %v850[%v851] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v853 = llvm.load %v852 : !llvm.ptr -> f32
%v854 = llvm.load %v773 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v855 = llvm.getelementptr %v773[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v856 = llvm.load %v855 : !llvm.ptr -> !llvm.ptr
%v857 = arith.index_cast %v847 : index to i64
%v858 = llvm.getelementptr %v856[%v857] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v859 = llvm.load %v858 : !llvm.ptr -> f32
%v860 = arith.mulf %v853, %v859 : f32
%v861 = llvm.load %v777 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v862 = llvm.getelementptr %v777[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v863 = llvm.load %v862 : !llvm.ptr -> !llvm.ptr
%v864 = arith.index_cast %v847 : index to i64
%v865 = llvm.getelementptr %v863[%v864] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v860, %v865 : f32, !llvm.ptr
%v866 = arith.addi %v847, %v842 : index
cf.br ^b28(%v866 : index)
^b30(%v867: index):
%v868 = llvm.load %v777 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v869 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v870 = llvm.extractvalue %v868[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v871 = llvm.insertvalue %v870, %v869[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v872 = llvm.extractvalue %v868[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v873 = llvm.insertvalue %v872, %v871[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v874 = llvm.extractvalue %v868[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v875 = llvm.insertvalue %v874, %v873[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v876 = llvm.extractvalue %v868[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v877 = llvm.insertvalue %v876, %v875[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v878 = llvm.extractvalue %v868[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v879 = llvm.insertvalue %v878, %v877[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v880 = llvm.extractvalue %v868[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v881 = llvm.insertvalue %v880, %v879[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v881, %v779 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v882 = llvm.load %v779 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v882 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_div(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v883 = llvm.mlir.constant(1 : i64) : i64
%v884 = llvm.alloca %v883 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v885 = llvm.mlir.constant(1 : i64) : i64
%v886 = llvm.alloca %v885 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v887 = llvm.mlir.constant(1 : i64) : i64
%v888 = llvm.alloca %v887 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v889 = llvm.mlir.constant(1 : i64) : i64
%v890 = llvm.alloca %v889 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v891 = llvm.mlir.constant(1 : i64) : i64
%v892 = llvm.alloca %v891 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v893 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v894 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v895 = llvm.insertvalue %v894, %v893[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v896 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v897 = llvm.insertvalue %v896, %v895[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v898 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v899 = llvm.insertvalue %v898, %v897[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v900 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v901 = llvm.insertvalue %v900, %v899[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v902 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v903 = llvm.insertvalue %v902, %v901[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v904 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v905 = llvm.insertvalue %v904, %v903[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v905, %v884 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v906 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v907 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v908 = llvm.insertvalue %v907, %v906[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v909 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v910 = llvm.insertvalue %v909, %v908[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v911 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v912 = llvm.insertvalue %v911, %v910[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v913 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v914 = llvm.insertvalue %v913, %v912[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v915 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v916 = llvm.insertvalue %v915, %v914[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v917 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v918 = llvm.insertvalue %v917, %v916[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v918, %v886 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v919 = llvm.load %v884 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v920 = llvm.getelementptr %v884[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v921 = llvm.load %v920 : !llvm.ptr -> i32
%v922 = llvm.load %v884 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v923 = llvm.getelementptr %v884[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v924 = llvm.load %v923 : !llvm.ptr -> i32
%v925 = llvm.load %v884 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v926 = llvm.getelementptr %v884[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v927 = llvm.load %v926 : !llvm.ptr -> i32
%v928 = llvm.load %v884 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v929 = llvm.getelementptr %v884[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v930 = llvm.load %v929 : !llvm.ptr -> i32
%v931 = func.call @tensor_zeros(%v921, %v924, %v927, %v930) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v932 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v933 = llvm.extractvalue %v931[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v934 = llvm.insertvalue %v933, %v932[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v935 = llvm.extractvalue %v931[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v936 = llvm.insertvalue %v935, %v934[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v937 = llvm.extractvalue %v931[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v938 = llvm.insertvalue %v937, %v936[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v939 = llvm.extractvalue %v931[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v940 = llvm.insertvalue %v939, %v938[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v941 = llvm.extractvalue %v931[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v942 = llvm.insertvalue %v941, %v940[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v943 = llvm.extractvalue %v931[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v944 = llvm.insertvalue %v943, %v942[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v944, %v888 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v945 = llvm.load %v888 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v945, %v890 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v946 = arith.constant 0 : i32
%v947 = llvm.load %v884 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v948 = llvm.getelementptr %v884[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v949 = llvm.load %v948 : !llvm.ptr -> i32
%v950 = arith.index_cast %v946 : i32 to index
%v951 = arith.index_cast %v949 : i32 to index
%v952 = arith.constant 1 : index
%v953 = arith.constant -1 : index
%v954 = arith.cmpi sle, %v950, %v951 : index
%v955 = arith.select %v954, %v952, %v953 : index
cf.br ^b31(%v950 : index)
^b31(%v956: index):
%v957 = arith.cmpi slt, %v956, %v951 : index
%v958 = arith.cmpi sgt, %v956, %v951 : index
%v959 = arith.select %v954, %v957, %v958 : i1
cf.cond_br %v959, ^b32(%v956 : index), ^b33(%v956 : index)
^b32(%v960: index):
%v961 = llvm.load %v884 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v962 = llvm.getelementptr %v884[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v963 = llvm.load %v962 : !llvm.ptr -> !llvm.ptr
%v964 = arith.index_cast %v960 : index to i64
%v965 = llvm.getelementptr %v963[%v964] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v966 = llvm.load %v965 : !llvm.ptr -> f32
%v967 = llvm.load %v886 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v968 = llvm.getelementptr %v886[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v969 = llvm.load %v968 : !llvm.ptr -> !llvm.ptr
%v970 = arith.index_cast %v960 : index to i64
%v971 = llvm.getelementptr %v969[%v970] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v972 = llvm.load %v971 : !llvm.ptr -> f32
%v973 = arith.divf %v966, %v972 : f32
%v974 = llvm.load %v890 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v975 = llvm.getelementptr %v890[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v976 = llvm.load %v975 : !llvm.ptr -> !llvm.ptr
%v977 = arith.index_cast %v960 : index to i64
%v978 = llvm.getelementptr %v976[%v977] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v973, %v978 : f32, !llvm.ptr
%v979 = arith.addi %v960, %v955 : index
cf.br ^b31(%v979 : index)
^b33(%v980: index):
%v981 = llvm.load %v890 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v982 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v983 = llvm.extractvalue %v981[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v984 = llvm.insertvalue %v983, %v982[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v985 = llvm.extractvalue %v981[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v986 = llvm.insertvalue %v985, %v984[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v987 = llvm.extractvalue %v981[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v988 = llvm.insertvalue %v987, %v986[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v989 = llvm.extractvalue %v981[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v990 = llvm.insertvalue %v989, %v988[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v991 = llvm.extractvalue %v981[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v992 = llvm.insertvalue %v991, %v990[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v993 = llvm.extractvalue %v981[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v994 = llvm.insertvalue %v993, %v992[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v994, %v892 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v995 = llvm.load %v892 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v995 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_scale(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: f32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v996 = llvm.mlir.constant(1 : i64) : i64
%v997 = llvm.alloca %v996 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v998 = llvm.mlir.constant(1 : i64) : i64
%v999 = llvm.alloca %v998 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1000 = llvm.mlir.constant(1 : i64) : i64
%v1001 = llvm.alloca %v1000 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1002 = llvm.mlir.constant(1 : i64) : i64
%v1003 = llvm.alloca %v1002 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1004 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1005 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1006 = llvm.insertvalue %v1005, %v1004[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1007 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1008 = llvm.insertvalue %v1007, %v1006[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1009 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1010 = llvm.insertvalue %v1009, %v1008[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1011 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1012 = llvm.insertvalue %v1011, %v1010[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1013 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1014 = llvm.insertvalue %v1013, %v1012[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1015 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1016 = llvm.insertvalue %v1015, %v1014[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1016, %v997 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1017 = llvm.load %v997 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1018 = llvm.getelementptr %v997[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1019 = llvm.load %v1018 : !llvm.ptr -> i32
%v1020 = llvm.load %v997 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1021 = llvm.getelementptr %v997[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1022 = llvm.load %v1021 : !llvm.ptr -> i32
%v1023 = llvm.load %v997 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1024 = llvm.getelementptr %v997[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1025 = llvm.load %v1024 : !llvm.ptr -> i32
%v1026 = llvm.load %v997 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1027 = llvm.getelementptr %v997[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1028 = llvm.load %v1027 : !llvm.ptr -> i32
%v1029 = func.call @tensor_zeros(%v1019, %v1022, %v1025, %v1028) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1030 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1031 = llvm.extractvalue %v1029[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1032 = llvm.insertvalue %v1031, %v1030[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1033 = llvm.extractvalue %v1029[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1034 = llvm.insertvalue %v1033, %v1032[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1035 = llvm.extractvalue %v1029[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1036 = llvm.insertvalue %v1035, %v1034[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1037 = llvm.extractvalue %v1029[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1038 = llvm.insertvalue %v1037, %v1036[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1039 = llvm.extractvalue %v1029[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1040 = llvm.insertvalue %v1039, %v1038[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1041 = llvm.extractvalue %v1029[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1042 = llvm.insertvalue %v1041, %v1040[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1042, %v999 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1043 = llvm.load %v999 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1043, %v1001 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1044 = arith.constant 0 : i32
%v1045 = llvm.load %v997 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1046 = llvm.getelementptr %v997[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1047 = llvm.load %v1046 : !llvm.ptr -> i32
%v1048 = arith.index_cast %v1044 : i32 to index
%v1049 = arith.index_cast %v1047 : i32 to index
%v1050 = arith.constant 1 : index
%v1051 = arith.constant -1 : index
%v1052 = arith.cmpi sle, %v1048, %v1049 : index
%v1053 = arith.select %v1052, %v1050, %v1051 : index
cf.br ^b34(%v1048 : index)
^b34(%v1054: index):
%v1055 = arith.cmpi slt, %v1054, %v1049 : index
%v1056 = arith.cmpi sgt, %v1054, %v1049 : index
%v1057 = arith.select %v1052, %v1055, %v1056 : i1
cf.cond_br %v1057, ^b35(%v1054 : index), ^b36(%v1054 : index)
^b35(%v1058: index):
%v1059 = llvm.load %v997 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1060 = llvm.getelementptr %v997[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1061 = llvm.load %v1060 : !llvm.ptr -> !llvm.ptr
%v1062 = arith.index_cast %v1058 : index to i64
%v1063 = llvm.getelementptr %v1061[%v1062] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1064 = llvm.load %v1063 : !llvm.ptr -> f32
%v1065 = arith.mulf %v1064, %arg1 : f32
%v1066 = llvm.load %v1001 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1067 = llvm.getelementptr %v1001[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1068 = llvm.load %v1067 : !llvm.ptr -> !llvm.ptr
%v1069 = arith.index_cast %v1058 : index to i64
%v1070 = llvm.getelementptr %v1068[%v1069] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1065, %v1070 : f32, !llvm.ptr
%v1071 = arith.addi %v1058, %v1053 : index
cf.br ^b34(%v1071 : index)
^b36(%v1072: index):
%v1073 = llvm.load %v1001 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1074 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1075 = llvm.extractvalue %v1073[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1076 = llvm.insertvalue %v1075, %v1074[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1077 = llvm.extractvalue %v1073[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1078 = llvm.insertvalue %v1077, %v1076[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1079 = llvm.extractvalue %v1073[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1080 = llvm.insertvalue %v1079, %v1078[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1081 = llvm.extractvalue %v1073[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1082 = llvm.insertvalue %v1081, %v1080[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1083 = llvm.extractvalue %v1073[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1084 = llvm.insertvalue %v1083, %v1082[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1085 = llvm.extractvalue %v1073[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1086 = llvm.insertvalue %v1085, %v1084[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1086, %v1003 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1087 = llvm.load %v1003 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1087 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_add_scalar(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: f32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1088 = llvm.mlir.constant(1 : i64) : i64
%v1089 = llvm.alloca %v1088 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1090 = llvm.mlir.constant(1 : i64) : i64
%v1091 = llvm.alloca %v1090 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1092 = llvm.mlir.constant(1 : i64) : i64
%v1093 = llvm.alloca %v1092 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1094 = llvm.mlir.constant(1 : i64) : i64
%v1095 = llvm.alloca %v1094 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1096 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1097 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1098 = llvm.insertvalue %v1097, %v1096[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1099 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1100 = llvm.insertvalue %v1099, %v1098[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1101 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1102 = llvm.insertvalue %v1101, %v1100[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1103 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1104 = llvm.insertvalue %v1103, %v1102[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1105 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1106 = llvm.insertvalue %v1105, %v1104[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1107 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1108 = llvm.insertvalue %v1107, %v1106[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1108, %v1089 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1109 = llvm.load %v1089 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1110 = llvm.getelementptr %v1089[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1111 = llvm.load %v1110 : !llvm.ptr -> i32
%v1112 = llvm.load %v1089 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1113 = llvm.getelementptr %v1089[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1114 = llvm.load %v1113 : !llvm.ptr -> i32
%v1115 = llvm.load %v1089 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1116 = llvm.getelementptr %v1089[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1117 = llvm.load %v1116 : !llvm.ptr -> i32
%v1118 = llvm.load %v1089 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1119 = llvm.getelementptr %v1089[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1120 = llvm.load %v1119 : !llvm.ptr -> i32
%v1121 = func.call @tensor_zeros(%v1111, %v1114, %v1117, %v1120) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1122 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1123 = llvm.extractvalue %v1121[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1124 = llvm.insertvalue %v1123, %v1122[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1125 = llvm.extractvalue %v1121[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1126 = llvm.insertvalue %v1125, %v1124[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1127 = llvm.extractvalue %v1121[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1128 = llvm.insertvalue %v1127, %v1126[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1129 = llvm.extractvalue %v1121[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1130 = llvm.insertvalue %v1129, %v1128[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1131 = llvm.extractvalue %v1121[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1132 = llvm.insertvalue %v1131, %v1130[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1133 = llvm.extractvalue %v1121[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1134 = llvm.insertvalue %v1133, %v1132[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1134, %v1091 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1135 = llvm.load %v1091 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1135, %v1093 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1136 = arith.constant 0 : i32
%v1137 = llvm.load %v1089 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1138 = llvm.getelementptr %v1089[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1139 = llvm.load %v1138 : !llvm.ptr -> i32
%v1140 = arith.index_cast %v1136 : i32 to index
%v1141 = arith.index_cast %v1139 : i32 to index
%v1142 = arith.constant 1 : index
%v1143 = arith.constant -1 : index
%v1144 = arith.cmpi sle, %v1140, %v1141 : index
%v1145 = arith.select %v1144, %v1142, %v1143 : index
cf.br ^b37(%v1140 : index)
^b37(%v1146: index):
%v1147 = arith.cmpi slt, %v1146, %v1141 : index
%v1148 = arith.cmpi sgt, %v1146, %v1141 : index
%v1149 = arith.select %v1144, %v1147, %v1148 : i1
cf.cond_br %v1149, ^b38(%v1146 : index), ^b39(%v1146 : index)
^b38(%v1150: index):
%v1151 = llvm.load %v1089 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1152 = llvm.getelementptr %v1089[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1153 = llvm.load %v1152 : !llvm.ptr -> !llvm.ptr
%v1154 = arith.index_cast %v1150 : index to i64
%v1155 = llvm.getelementptr %v1153[%v1154] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1156 = llvm.load %v1155 : !llvm.ptr -> f32
%v1157 = arith.addf %v1156, %arg1 : f32
%v1158 = llvm.load %v1093 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1159 = llvm.getelementptr %v1093[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1160 = llvm.load %v1159 : !llvm.ptr -> !llvm.ptr
%v1161 = arith.index_cast %v1150 : index to i64
%v1162 = llvm.getelementptr %v1160[%v1161] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1157, %v1162 : f32, !llvm.ptr
%v1163 = arith.addi %v1150, %v1145 : index
cf.br ^b37(%v1163 : index)
^b39(%v1164: index):
%v1165 = llvm.load %v1093 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1166 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1167 = llvm.extractvalue %v1165[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1168 = llvm.insertvalue %v1167, %v1166[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1169 = llvm.extractvalue %v1165[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1170 = llvm.insertvalue %v1169, %v1168[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1171 = llvm.extractvalue %v1165[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1172 = llvm.insertvalue %v1171, %v1170[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1173 = llvm.extractvalue %v1165[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1174 = llvm.insertvalue %v1173, %v1172[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1175 = llvm.extractvalue %v1165[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1176 = llvm.insertvalue %v1175, %v1174[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1177 = llvm.extractvalue %v1165[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1178 = llvm.insertvalue %v1177, %v1176[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1178, %v1095 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1179 = llvm.load %v1095 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1179 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_neg(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1180 = llvm.mlir.constant(1 : i64) : i64
%v1181 = llvm.alloca %v1180 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1182 = llvm.mlir.constant(1 : i64) : i64
%v1183 = llvm.alloca %v1182 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1184 = llvm.mlir.constant(1 : i64) : i64
%v1185 = llvm.alloca %v1184 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1186 = llvm.mlir.constant(1 : i64) : i64
%v1187 = llvm.alloca %v1186 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1188 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1189 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1190 = llvm.insertvalue %v1189, %v1188[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1191 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1192 = llvm.insertvalue %v1191, %v1190[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1193 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1194 = llvm.insertvalue %v1193, %v1192[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1195 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1196 = llvm.insertvalue %v1195, %v1194[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1197 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1198 = llvm.insertvalue %v1197, %v1196[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1199 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1200 = llvm.insertvalue %v1199, %v1198[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1200, %v1181 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1201 = llvm.load %v1181 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1202 = llvm.getelementptr %v1181[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1203 = llvm.load %v1202 : !llvm.ptr -> i32
%v1204 = llvm.load %v1181 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1205 = llvm.getelementptr %v1181[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1206 = llvm.load %v1205 : !llvm.ptr -> i32
%v1207 = llvm.load %v1181 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1208 = llvm.getelementptr %v1181[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1209 = llvm.load %v1208 : !llvm.ptr -> i32
%v1210 = llvm.load %v1181 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1211 = llvm.getelementptr %v1181[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1212 = llvm.load %v1211 : !llvm.ptr -> i32
%v1213 = func.call @tensor_zeros(%v1203, %v1206, %v1209, %v1212) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1214 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1215 = llvm.extractvalue %v1213[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1216 = llvm.insertvalue %v1215, %v1214[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1217 = llvm.extractvalue %v1213[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1218 = llvm.insertvalue %v1217, %v1216[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1219 = llvm.extractvalue %v1213[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1220 = llvm.insertvalue %v1219, %v1218[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1221 = llvm.extractvalue %v1213[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1222 = llvm.insertvalue %v1221, %v1220[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1223 = llvm.extractvalue %v1213[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1224 = llvm.insertvalue %v1223, %v1222[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1225 = llvm.extractvalue %v1213[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1226 = llvm.insertvalue %v1225, %v1224[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1226, %v1183 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1227 = llvm.load %v1183 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1227, %v1185 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1228 = arith.constant 0 : i32
%v1229 = llvm.load %v1181 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1230 = llvm.getelementptr %v1181[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1231 = llvm.load %v1230 : !llvm.ptr -> i32
%v1232 = arith.index_cast %v1228 : i32 to index
%v1233 = arith.index_cast %v1231 : i32 to index
%v1234 = arith.constant 1 : index
%v1235 = arith.constant -1 : index
%v1236 = arith.cmpi sle, %v1232, %v1233 : index
%v1237 = arith.select %v1236, %v1234, %v1235 : index
cf.br ^b40(%v1232 : index)
^b40(%v1238: index):
%v1239 = arith.cmpi slt, %v1238, %v1233 : index
%v1240 = arith.cmpi sgt, %v1238, %v1233 : index
%v1241 = arith.select %v1236, %v1239, %v1240 : i1
cf.cond_br %v1241, ^b41(%v1238 : index), ^b42(%v1238 : index)
^b41(%v1242: index):
%v1243 = arith.constant 0.0 : f64
%v1244 = llvm.load %v1181 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1245 = llvm.getelementptr %v1181[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1246 = llvm.load %v1245 : !llvm.ptr -> !llvm.ptr
%v1247 = arith.index_cast %v1242 : index to i64
%v1248 = llvm.getelementptr %v1246[%v1247] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1249 = llvm.load %v1248 : !llvm.ptr -> f32
%v1250 = arith.extf %v1249 : f32 to f64
%v1251 = arith.subf %v1243, %v1250 : f64
%v1252 = llvm.load %v1185 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1253 = llvm.getelementptr %v1185[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1254 = llvm.load %v1253 : !llvm.ptr -> !llvm.ptr
%v1255 = arith.truncf %v1251 : f64 to f32
%v1256 = arith.index_cast %v1242 : index to i64
%v1257 = llvm.getelementptr %v1254[%v1256] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1255, %v1257 : f32, !llvm.ptr
%v1258 = arith.addi %v1242, %v1237 : index
cf.br ^b40(%v1258 : index)
^b42(%v1259: index):
%v1260 = llvm.load %v1185 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1261 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1262 = llvm.extractvalue %v1260[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1263 = llvm.insertvalue %v1262, %v1261[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1264 = llvm.extractvalue %v1260[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1265 = llvm.insertvalue %v1264, %v1263[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1266 = llvm.extractvalue %v1260[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1267 = llvm.insertvalue %v1266, %v1265[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1268 = llvm.extractvalue %v1260[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1269 = llvm.insertvalue %v1268, %v1267[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1270 = llvm.extractvalue %v1260[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1271 = llvm.insertvalue %v1270, %v1269[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1272 = llvm.extractvalue %v1260[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1273 = llvm.insertvalue %v1272, %v1271[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1273, %v1187 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1274 = llvm.load %v1187 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1274 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_relu(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1275 = llvm.mlir.constant(1 : i64) : i64
%v1276 = llvm.alloca %v1275 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1277 = llvm.mlir.constant(1 : i64) : i64
%v1278 = llvm.alloca %v1277 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1279 = llvm.mlir.constant(1 : i64) : i64
%v1280 = llvm.alloca %v1279 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1281 = llvm.mlir.constant(1 : i64) : i64
%v1282 = llvm.alloca %v1281 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1283 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1284 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1285 = llvm.insertvalue %v1284, %v1283[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1286 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1287 = llvm.insertvalue %v1286, %v1285[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1288 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1289 = llvm.insertvalue %v1288, %v1287[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1290 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1291 = llvm.insertvalue %v1290, %v1289[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1292 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1293 = llvm.insertvalue %v1292, %v1291[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1294 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1295 = llvm.insertvalue %v1294, %v1293[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1295, %v1276 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1296 = llvm.load %v1276 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1297 = llvm.getelementptr %v1276[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1298 = llvm.load %v1297 : !llvm.ptr -> i32
%v1299 = llvm.load %v1276 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1300 = llvm.getelementptr %v1276[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1301 = llvm.load %v1300 : !llvm.ptr -> i32
%v1302 = llvm.load %v1276 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1303 = llvm.getelementptr %v1276[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1304 = llvm.load %v1303 : !llvm.ptr -> i32
%v1305 = llvm.load %v1276 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1306 = llvm.getelementptr %v1276[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1307 = llvm.load %v1306 : !llvm.ptr -> i32
%v1308 = func.call @tensor_zeros(%v1298, %v1301, %v1304, %v1307) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1309 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1310 = llvm.extractvalue %v1308[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1311 = llvm.insertvalue %v1310, %v1309[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1312 = llvm.extractvalue %v1308[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1313 = llvm.insertvalue %v1312, %v1311[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1314 = llvm.extractvalue %v1308[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1315 = llvm.insertvalue %v1314, %v1313[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1316 = llvm.extractvalue %v1308[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1317 = llvm.insertvalue %v1316, %v1315[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1318 = llvm.extractvalue %v1308[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1319 = llvm.insertvalue %v1318, %v1317[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1320 = llvm.extractvalue %v1308[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1321 = llvm.insertvalue %v1320, %v1319[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1321, %v1278 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1322 = llvm.load %v1278 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1322, %v1280 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1323 = arith.constant 0 : i32
%v1324 = llvm.load %v1276 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1325 = llvm.getelementptr %v1276[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1326 = llvm.load %v1325 : !llvm.ptr -> i32
%v1327 = arith.index_cast %v1323 : i32 to index
%v1328 = arith.index_cast %v1326 : i32 to index
%v1329 = arith.constant 1 : index
%v1330 = arith.constant -1 : index
%v1331 = arith.cmpi sle, %v1327, %v1328 : index
%v1332 = arith.select %v1331, %v1329, %v1330 : index
cf.br ^b43(%v1327 : index)
^b43(%v1333: index):
%v1334 = arith.cmpi slt, %v1333, %v1328 : index
%v1335 = arith.cmpi sgt, %v1333, %v1328 : index
%v1336 = arith.select %v1331, %v1334, %v1335 : i1
cf.cond_br %v1336, ^b44(%v1333 : index), ^b45(%v1333 : index)
^b44(%v1337: index):
%v1338 = llvm.load %v1276 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1339 = llvm.getelementptr %v1276[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1340 = llvm.load %v1339 : !llvm.ptr -> !llvm.ptr
%v1341 = arith.index_cast %v1337 : index to i64
%v1342 = llvm.getelementptr %v1340[%v1341] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1343 = llvm.load %v1342 : !llvm.ptr -> f32
%v1344 = arith.constant 0.0 : f64
%v1345 = arith.extf %v1343 : f32 to f64
%v1346 = arith.cmpf ogt, %v1345, %v1344 : f64
cf.cond_br %v1346, ^b46, ^b47
^b46:
%v1347 = llvm.load %v1276 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1348 = llvm.getelementptr %v1276[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1349 = llvm.load %v1348 : !llvm.ptr -> !llvm.ptr
%v1350 = arith.index_cast %v1337 : index to i64
%v1351 = llvm.getelementptr %v1349[%v1350] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1352 = llvm.load %v1351 : !llvm.ptr -> f32
%v1353 = llvm.load %v1280 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1354 = llvm.getelementptr %v1280[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1355 = llvm.load %v1354 : !llvm.ptr -> !llvm.ptr
%v1356 = arith.index_cast %v1337 : index to i64
%v1357 = llvm.getelementptr %v1355[%v1356] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1352, %v1357 : f32, !llvm.ptr
cf.br ^b48
^b47:
%v1358 = arith.constant 0.0 : f64
%v1359 = llvm.load %v1280 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1360 = llvm.getelementptr %v1280[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1361 = llvm.load %v1360 : !llvm.ptr -> !llvm.ptr
%v1362 = arith.truncf %v1358 : f64 to f32
%v1363 = arith.index_cast %v1337 : index to i64
%v1364 = llvm.getelementptr %v1361[%v1363] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1362, %v1364 : f32, !llvm.ptr
cf.br ^b48
^b48:
%v1365 = arith.addi %v1337, %v1332 : index
cf.br ^b43(%v1365 : index)
^b45(%v1366: index):
%v1367 = llvm.load %v1280 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1368 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1369 = llvm.extractvalue %v1367[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1370 = llvm.insertvalue %v1369, %v1368[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1371 = llvm.extractvalue %v1367[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1372 = llvm.insertvalue %v1371, %v1370[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1373 = llvm.extractvalue %v1367[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1374 = llvm.insertvalue %v1373, %v1372[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1375 = llvm.extractvalue %v1367[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1376 = llvm.insertvalue %v1375, %v1374[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1377 = llvm.extractvalue %v1367[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1378 = llvm.insertvalue %v1377, %v1376[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1379 = llvm.extractvalue %v1367[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1380 = llvm.insertvalue %v1379, %v1378[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1380, %v1282 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1381 = llvm.load %v1282 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1381 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_sigmoid(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1382 = llvm.mlir.constant(1 : i64) : i64
%v1383 = llvm.alloca %v1382 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1384 = llvm.mlir.constant(1 : i64) : i64
%v1385 = llvm.alloca %v1384 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1386 = llvm.mlir.constant(1 : i64) : i64
%v1387 = llvm.alloca %v1386 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1388 = llvm.mlir.constant(1 : i64) : i64
%v1389 = llvm.alloca %v1388 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1390 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1391 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1392 = llvm.insertvalue %v1391, %v1390[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1393 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1394 = llvm.insertvalue %v1393, %v1392[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1395 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1396 = llvm.insertvalue %v1395, %v1394[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1397 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1398 = llvm.insertvalue %v1397, %v1396[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1399 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1400 = llvm.insertvalue %v1399, %v1398[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1401 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1402 = llvm.insertvalue %v1401, %v1400[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1402, %v1383 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1403 = llvm.load %v1383 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1404 = llvm.getelementptr %v1383[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1405 = llvm.load %v1404 : !llvm.ptr -> i32
%v1406 = llvm.load %v1383 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1407 = llvm.getelementptr %v1383[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1408 = llvm.load %v1407 : !llvm.ptr -> i32
%v1409 = llvm.load %v1383 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1410 = llvm.getelementptr %v1383[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1411 = llvm.load %v1410 : !llvm.ptr -> i32
%v1412 = llvm.load %v1383 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1413 = llvm.getelementptr %v1383[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1414 = llvm.load %v1413 : !llvm.ptr -> i32
%v1415 = func.call @tensor_zeros(%v1405, %v1408, %v1411, %v1414) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1416 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1417 = llvm.extractvalue %v1415[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1418 = llvm.insertvalue %v1417, %v1416[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1419 = llvm.extractvalue %v1415[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1420 = llvm.insertvalue %v1419, %v1418[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1421 = llvm.extractvalue %v1415[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1422 = llvm.insertvalue %v1421, %v1420[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1423 = llvm.extractvalue %v1415[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1424 = llvm.insertvalue %v1423, %v1422[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1425 = llvm.extractvalue %v1415[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1426 = llvm.insertvalue %v1425, %v1424[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1427 = llvm.extractvalue %v1415[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1428 = llvm.insertvalue %v1427, %v1426[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1428, %v1385 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1429 = llvm.load %v1385 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1429, %v1387 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1430 = arith.constant 0 : i32
%v1431 = llvm.load %v1383 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1432 = llvm.getelementptr %v1383[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1433 = llvm.load %v1432 : !llvm.ptr -> i32
%v1434 = arith.index_cast %v1430 : i32 to index
%v1435 = arith.index_cast %v1433 : i32 to index
%v1436 = arith.constant 1 : index
%v1437 = arith.constant -1 : index
%v1438 = arith.cmpi sle, %v1434, %v1435 : index
%v1439 = arith.select %v1438, %v1436, %v1437 : index
cf.br ^b49(%v1434 : index)
^b49(%v1440: index):
%v1441 = arith.cmpi slt, %v1440, %v1435 : index
%v1442 = arith.cmpi sgt, %v1440, %v1435 : index
%v1443 = arith.select %v1438, %v1441, %v1442 : i1
cf.cond_br %v1443, ^b50(%v1440 : index), ^b51(%v1440 : index)
^b50(%v1444: index):
%v1445 = arith.constant 0.0 : f64
%v1446 = llvm.load %v1383 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1447 = llvm.getelementptr %v1383[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1448 = llvm.load %v1447 : !llvm.ptr -> !llvm.ptr
%v1449 = arith.index_cast %v1444 : index to i64
%v1450 = llvm.getelementptr %v1448[%v1449] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1451 = llvm.load %v1450 : !llvm.ptr -> f32
%v1452 = arith.extf %v1451 : f32 to f64
%v1453 = arith.subf %v1445, %v1452 : f64
%v1454 = func.call @exp(%v1453) : (f64) -> f64
%v1455 = arith.constant 1.0 : f64
%v1456 = arith.constant 1.0 : f64
%v1457 = arith.addf %v1456, %v1454 : f64
%v1458 = arith.divf %v1455, %v1457 : f64
%v1459 = llvm.load %v1387 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1460 = llvm.getelementptr %v1387[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1461 = llvm.load %v1460 : !llvm.ptr -> !llvm.ptr
%v1462 = arith.truncf %v1458 : f64 to f32
%v1463 = arith.index_cast %v1444 : index to i64
%v1464 = llvm.getelementptr %v1461[%v1463] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1462, %v1464 : f32, !llvm.ptr
%v1465 = arith.addi %v1444, %v1439 : index
cf.br ^b49(%v1465 : index)
^b51(%v1466: index):
%v1467 = llvm.load %v1387 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1468 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1469 = llvm.extractvalue %v1467[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1470 = llvm.insertvalue %v1469, %v1468[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1471 = llvm.extractvalue %v1467[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1472 = llvm.insertvalue %v1471, %v1470[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1473 = llvm.extractvalue %v1467[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1474 = llvm.insertvalue %v1473, %v1472[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1475 = llvm.extractvalue %v1467[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1476 = llvm.insertvalue %v1475, %v1474[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1477 = llvm.extractvalue %v1467[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1478 = llvm.insertvalue %v1477, %v1476[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1479 = llvm.extractvalue %v1467[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1480 = llvm.insertvalue %v1479, %v1478[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1480, %v1389 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1481 = llvm.load %v1389 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1481 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_tanh(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1482 = llvm.mlir.constant(1 : i64) : i64
%v1483 = llvm.alloca %v1482 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1484 = llvm.mlir.constant(1 : i64) : i64
%v1485 = llvm.alloca %v1484 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1486 = llvm.mlir.constant(1 : i64) : i64
%v1487 = llvm.alloca %v1486 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1488 = llvm.mlir.constant(1 : i64) : i64
%v1489 = llvm.alloca %v1488 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1490 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1491 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1492 = llvm.insertvalue %v1491, %v1490[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1493 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1494 = llvm.insertvalue %v1493, %v1492[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1495 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1496 = llvm.insertvalue %v1495, %v1494[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1497 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1498 = llvm.insertvalue %v1497, %v1496[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1499 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1500 = llvm.insertvalue %v1499, %v1498[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1501 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1502 = llvm.insertvalue %v1501, %v1500[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1502, %v1483 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1503 = llvm.load %v1483 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1504 = llvm.getelementptr %v1483[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1505 = llvm.load %v1504 : !llvm.ptr -> i32
%v1506 = llvm.load %v1483 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1507 = llvm.getelementptr %v1483[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1508 = llvm.load %v1507 : !llvm.ptr -> i32
%v1509 = llvm.load %v1483 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1510 = llvm.getelementptr %v1483[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1511 = llvm.load %v1510 : !llvm.ptr -> i32
%v1512 = llvm.load %v1483 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1513 = llvm.getelementptr %v1483[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1514 = llvm.load %v1513 : !llvm.ptr -> i32
%v1515 = func.call @tensor_zeros(%v1505, %v1508, %v1511, %v1514) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1516 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1517 = llvm.extractvalue %v1515[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1518 = llvm.insertvalue %v1517, %v1516[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1519 = llvm.extractvalue %v1515[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1520 = llvm.insertvalue %v1519, %v1518[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1521 = llvm.extractvalue %v1515[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1522 = llvm.insertvalue %v1521, %v1520[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1523 = llvm.extractvalue %v1515[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1524 = llvm.insertvalue %v1523, %v1522[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1525 = llvm.extractvalue %v1515[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1526 = llvm.insertvalue %v1525, %v1524[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1527 = llvm.extractvalue %v1515[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1528 = llvm.insertvalue %v1527, %v1526[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1528, %v1485 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1529 = llvm.load %v1485 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1529, %v1487 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1530 = arith.constant 0 : i32
%v1531 = llvm.load %v1483 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1532 = llvm.getelementptr %v1483[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1533 = llvm.load %v1532 : !llvm.ptr -> i32
%v1534 = arith.index_cast %v1530 : i32 to index
%v1535 = arith.index_cast %v1533 : i32 to index
%v1536 = arith.constant 1 : index
%v1537 = arith.constant -1 : index
%v1538 = arith.cmpi sle, %v1534, %v1535 : index
%v1539 = arith.select %v1538, %v1536, %v1537 : index
cf.br ^b52(%v1534 : index)
^b52(%v1540: index):
%v1541 = arith.cmpi slt, %v1540, %v1535 : index
%v1542 = arith.cmpi sgt, %v1540, %v1535 : index
%v1543 = arith.select %v1538, %v1541, %v1542 : i1
cf.cond_br %v1543, ^b53(%v1540 : index), ^b54(%v1540 : index)
^b53(%v1544: index):
%v1545 = llvm.load %v1483 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1546 = llvm.getelementptr %v1483[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1547 = llvm.load %v1546 : !llvm.ptr -> !llvm.ptr
%v1548 = arith.index_cast %v1544 : index to i64
%v1549 = llvm.getelementptr %v1547[%v1548] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1550 = llvm.load %v1549 : !llvm.ptr -> f32
%v1551 = arith.extf %v1550 : f32 to f64
%v1552 = func.call @exp(%v1551) : (f64) -> f64
%v1553 = arith.constant 0.0 : f64
%v1554 = llvm.load %v1483 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1555 = llvm.getelementptr %v1483[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1556 = llvm.load %v1555 : !llvm.ptr -> !llvm.ptr
%v1557 = arith.index_cast %v1544 : index to i64
%v1558 = llvm.getelementptr %v1556[%v1557] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1559 = llvm.load %v1558 : !llvm.ptr -> f32
%v1560 = arith.extf %v1559 : f32 to f64
%v1561 = arith.subf %v1553, %v1560 : f64
%v1562 = func.call @exp(%v1561) : (f64) -> f64
%v1563 = arith.subf %v1552, %v1562 : f64
%v1564 = arith.addf %v1552, %v1562 : f64
%v1565 = arith.divf %v1563, %v1564 : f64
%v1566 = llvm.load %v1487 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1567 = llvm.getelementptr %v1487[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1568 = llvm.load %v1567 : !llvm.ptr -> !llvm.ptr
%v1569 = arith.truncf %v1565 : f64 to f32
%v1570 = arith.index_cast %v1544 : index to i64
%v1571 = llvm.getelementptr %v1568[%v1570] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1569, %v1571 : f32, !llvm.ptr
%v1572 = arith.addi %v1544, %v1539 : index
cf.br ^b52(%v1572 : index)
^b54(%v1573: index):
%v1574 = llvm.load %v1487 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1575 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1576 = llvm.extractvalue %v1574[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1577 = llvm.insertvalue %v1576, %v1575[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1578 = llvm.extractvalue %v1574[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1579 = llvm.insertvalue %v1578, %v1577[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1580 = llvm.extractvalue %v1574[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1581 = llvm.insertvalue %v1580, %v1579[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1582 = llvm.extractvalue %v1574[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1583 = llvm.insertvalue %v1582, %v1581[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1584 = llvm.extractvalue %v1574[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1585 = llvm.insertvalue %v1584, %v1583[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1586 = llvm.extractvalue %v1574[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1587 = llvm.insertvalue %v1586, %v1585[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1587, %v1489 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1588 = llvm.load %v1489 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1588 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_softmax(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1589 = llvm.mlir.constant(1 : i64) : i64
%v1590 = llvm.alloca %v1589 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1591 = llvm.mlir.constant(1 : i64) : i64
%v1592 = llvm.alloca %v1591 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1593 = llvm.mlir.constant(1 : i64) : i64
%v1594 = llvm.alloca %v1593 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1595 = llvm.mlir.constant(1 : i64) : i64
%v1596 = llvm.alloca %v1595 x f32 : (i64) -> !llvm.ptr
%v1597 = llvm.mlir.constant(1 : i64) : i64
%v1598 = llvm.alloca %v1597 x f64 : (i64) -> !llvm.ptr
%v1599 = llvm.mlir.constant(1 : i64) : i64
%v1600 = llvm.alloca %v1599 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1601 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1602 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1603 = llvm.insertvalue %v1602, %v1601[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1604 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1605 = llvm.insertvalue %v1604, %v1603[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1606 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1607 = llvm.insertvalue %v1606, %v1605[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1608 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1609 = llvm.insertvalue %v1608, %v1607[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1610 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1611 = llvm.insertvalue %v1610, %v1609[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1612 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1613 = llvm.insertvalue %v1612, %v1611[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1613, %v1590 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1614 = llvm.load %v1590 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1615 = llvm.getelementptr %v1590[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1616 = llvm.load %v1615 : !llvm.ptr -> i32
%v1617 = llvm.load %v1590 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1618 = llvm.getelementptr %v1590[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1619 = llvm.load %v1618 : !llvm.ptr -> i32
%v1620 = arith.constant 1 : i32
%v1621 = arith.constant 1 : i32
%v1622 = func.call @tensor_zeros(%v1616, %v1619, %v1620, %v1621) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1623 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1624 = llvm.extractvalue %v1622[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1625 = llvm.insertvalue %v1624, %v1623[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1626 = llvm.extractvalue %v1622[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1627 = llvm.insertvalue %v1626, %v1625[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1628 = llvm.extractvalue %v1622[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1629 = llvm.insertvalue %v1628, %v1627[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1630 = llvm.extractvalue %v1622[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1631 = llvm.insertvalue %v1630, %v1629[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1632 = llvm.extractvalue %v1622[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1633 = llvm.insertvalue %v1632, %v1631[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1634 = llvm.extractvalue %v1622[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1635 = llvm.insertvalue %v1634, %v1633[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1635, %v1592 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1636 = llvm.load %v1592 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1636, %v1594 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1637 = arith.constant 0 : i32
%v1638 = llvm.load %v1590 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1639 = llvm.getelementptr %v1590[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1640 = llvm.load %v1639 : !llvm.ptr -> i32
%v1641 = arith.index_cast %v1637 : i32 to index
%v1642 = arith.index_cast %v1640 : i32 to index
%v1643 = arith.constant 1 : index
%v1644 = arith.constant -1 : index
%v1645 = arith.cmpi sle, %v1641, %v1642 : index
%v1646 = arith.select %v1645, %v1643, %v1644 : index
cf.br ^b55(%v1641 : index)
^b55(%v1647: index):
%v1648 = arith.cmpi slt, %v1647, %v1642 : index
%v1649 = arith.cmpi sgt, %v1647, %v1642 : index
%v1650 = arith.select %v1645, %v1648, %v1649 : i1
cf.cond_br %v1650, ^b56(%v1647 : index), ^b57(%v1647 : index)
^b56(%v1651: index):
%v1652 = llvm.load %v1590 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1653 = llvm.getelementptr %v1590[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1654 = llvm.load %v1653 : !llvm.ptr -> !llvm.ptr
%v1655 = llvm.load %v1590 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1656 = llvm.getelementptr %v1590[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1657 = llvm.load %v1656 : !llvm.ptr -> i32
%v1658 = arith.index_cast %v1651 : index to i32
%v1659 = arith.muli %v1658, %v1657 : i32
%v1660 = arith.extsi %v1659 : i32 to i64
%v1661 = llvm.getelementptr %v1654[%v1660] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1662 = llvm.load %v1661 : !llvm.ptr -> f32
llvm.store %v1662, %v1596 : f32, !llvm.ptr
%v1663 = arith.constant 1 : i32
%v1664 = llvm.load %v1590 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1665 = llvm.getelementptr %v1590[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1666 = llvm.load %v1665 : !llvm.ptr -> i32
%v1667 = arith.index_cast %v1663 : i32 to index
%v1668 = arith.index_cast %v1666 : i32 to index
%v1669 = arith.constant 1 : index
%v1670 = arith.constant -1 : index
%v1671 = arith.cmpi sle, %v1667, %v1668 : index
%v1672 = arith.select %v1671, %v1669, %v1670 : index
cf.br ^b58(%v1667 : index)
^b58(%v1673: index):
%v1674 = arith.cmpi slt, %v1673, %v1668 : index
%v1675 = arith.cmpi sgt, %v1673, %v1668 : index
%v1676 = arith.select %v1671, %v1674, %v1675 : i1
cf.cond_br %v1676, ^b59(%v1673 : index), ^b60(%v1673 : index)
^b59(%v1677: index):
%v1678 = llvm.load %v1590 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1679 = llvm.getelementptr %v1590[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1680 = llvm.load %v1679 : !llvm.ptr -> !llvm.ptr
%v1681 = llvm.load %v1590 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1682 = llvm.getelementptr %v1590[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1683 = llvm.load %v1682 : !llvm.ptr -> i32
%v1684 = arith.index_cast %v1651 : index to i32
%v1685 = arith.muli %v1684, %v1683 : i32
%v1686 = arith.index_cast %v1677 : index to i32
%v1687 = arith.addi %v1685, %v1686 : i32
%v1688 = arith.extsi %v1687 : i32 to i64
%v1689 = llvm.getelementptr %v1680[%v1688] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1690 = llvm.load %v1689 : !llvm.ptr -> f32
%v1691 = llvm.load %v1596 : !llvm.ptr -> f32
%v1692 = arith.cmpf ogt, %v1690, %v1691 : f32
cf.cond_br %v1692, ^b61, ^b62
^b61:
%v1693 = llvm.load %v1590 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1694 = llvm.getelementptr %v1590[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1695 = llvm.load %v1694 : !llvm.ptr -> !llvm.ptr
%v1696 = llvm.load %v1590 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1697 = llvm.getelementptr %v1590[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1698 = llvm.load %v1697 : !llvm.ptr -> i32
%v1699 = arith.index_cast %v1651 : index to i32
%v1700 = arith.muli %v1699, %v1698 : i32
%v1701 = arith.index_cast %v1677 : index to i32
%v1702 = arith.addi %v1700, %v1701 : i32
%v1703 = arith.extsi %v1702 : i32 to i64
%v1704 = llvm.getelementptr %v1695[%v1703] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1705 = llvm.load %v1704 : !llvm.ptr -> f32
llvm.store %v1705, %v1596 : f32, !llvm.ptr
cf.br ^b63
^b62:
cf.br ^b63
^b63:
%v1706 = arith.addi %v1677, %v1672 : index
cf.br ^b58(%v1706 : index)
^b60(%v1707: index):
%v1708 = arith.constant 0.0 : f64
llvm.store %v1708, %v1598 : f64, !llvm.ptr
%v1709 = arith.constant 0 : i32
%v1710 = llvm.load %v1590 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1711 = llvm.getelementptr %v1590[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1712 = llvm.load %v1711 : !llvm.ptr -> i32
%v1713 = arith.index_cast %v1709 : i32 to index
%v1714 = arith.index_cast %v1712 : i32 to index
%v1715 = arith.constant 1 : index
%v1716 = arith.constant -1 : index
%v1717 = arith.cmpi sle, %v1713, %v1714 : index
%v1718 = arith.select %v1717, %v1715, %v1716 : index
cf.br ^b64(%v1713 : index)
^b64(%v1719: index):
%v1720 = arith.cmpi slt, %v1719, %v1714 : index
%v1721 = arith.cmpi sgt, %v1719, %v1714 : index
%v1722 = arith.select %v1717, %v1720, %v1721 : i1
cf.cond_br %v1722, ^b65(%v1719 : index), ^b66(%v1719 : index)
^b65(%v1723: index):
%v1724 = llvm.load %v1590 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1725 = llvm.getelementptr %v1590[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1726 = llvm.load %v1725 : !llvm.ptr -> !llvm.ptr
%v1727 = llvm.load %v1590 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1728 = llvm.getelementptr %v1590[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1729 = llvm.load %v1728 : !llvm.ptr -> i32
%v1730 = arith.index_cast %v1651 : index to i32
%v1731 = arith.muli %v1730, %v1729 : i32
%v1732 = arith.index_cast %v1723 : index to i32
%v1733 = arith.addi %v1731, %v1732 : i32
%v1734 = arith.extsi %v1733 : i32 to i64
%v1735 = llvm.getelementptr %v1726[%v1734] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1736 = llvm.load %v1735 : !llvm.ptr -> f32
%v1737 = llvm.load %v1596 : !llvm.ptr -> f32
%v1738 = arith.subf %v1736, %v1737 : f32
%v1739 = arith.extf %v1738 : f32 to f64
%v1740 = func.call @exp(%v1739) : (f64) -> f64
%v1741 = llvm.load %v1594 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1742 = llvm.getelementptr %v1594[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1743 = llvm.load %v1742 : !llvm.ptr -> !llvm.ptr
%v1744 = llvm.load %v1590 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1745 = llvm.getelementptr %v1590[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1746 = llvm.load %v1745 : !llvm.ptr -> i32
%v1747 = arith.index_cast %v1651 : index to i32
%v1748 = arith.muli %v1747, %v1746 : i32
%v1749 = arith.index_cast %v1723 : index to i32
%v1750 = arith.addi %v1748, %v1749 : i32
%v1751 = arith.truncf %v1740 : f64 to f32
%v1752 = arith.extsi %v1750 : i32 to i64
%v1753 = llvm.getelementptr %v1743[%v1752] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1751, %v1753 : f32, !llvm.ptr
%v1754 = llvm.load %v1598 : !llvm.ptr -> f64
%v1755 = arith.addf %v1754, %v1740 : f64
llvm.store %v1755, %v1598 : f64, !llvm.ptr
%v1756 = arith.addi %v1723, %v1718 : index
cf.br ^b64(%v1756 : index)
^b66(%v1757: index):
%v1758 = arith.constant 0 : i32
%v1759 = llvm.load %v1590 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1760 = llvm.getelementptr %v1590[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1761 = llvm.load %v1760 : !llvm.ptr -> i32
%v1762 = arith.index_cast %v1758 : i32 to index
%v1763 = arith.index_cast %v1761 : i32 to index
%v1764 = arith.constant 1 : index
%v1765 = arith.constant -1 : index
%v1766 = arith.cmpi sle, %v1762, %v1763 : index
%v1767 = arith.select %v1766, %v1764, %v1765 : index
cf.br ^b67(%v1762 : index)
^b67(%v1768: index):
%v1769 = arith.cmpi slt, %v1768, %v1763 : index
%v1770 = arith.cmpi sgt, %v1768, %v1763 : index
%v1771 = arith.select %v1766, %v1769, %v1770 : i1
cf.cond_br %v1771, ^b68(%v1768 : index), ^b69(%v1768 : index)
^b68(%v1772: index):
%v1773 = llvm.load %v1594 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1774 = llvm.getelementptr %v1594[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1775 = llvm.load %v1774 : !llvm.ptr -> !llvm.ptr
%v1776 = llvm.load %v1590 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1777 = llvm.getelementptr %v1590[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1778 = llvm.load %v1777 : !llvm.ptr -> i32
%v1779 = arith.index_cast %v1651 : index to i32
%v1780 = arith.muli %v1779, %v1778 : i32
%v1781 = arith.index_cast %v1772 : index to i32
%v1782 = arith.addi %v1780, %v1781 : i32
%v1783 = arith.extsi %v1782 : i32 to i64
%v1784 = llvm.getelementptr %v1775[%v1783] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1785 = llvm.load %v1784 : !llvm.ptr -> f32
%v1786 = llvm.load %v1598 : !llvm.ptr -> f64
%v1787 = arith.extf %v1785 : f32 to f64
%v1788 = arith.divf %v1787, %v1786 : f64
%v1789 = llvm.load %v1594 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1790 = llvm.getelementptr %v1594[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1791 = llvm.load %v1790 : !llvm.ptr -> !llvm.ptr
%v1792 = llvm.load %v1590 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1793 = llvm.getelementptr %v1590[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1794 = llvm.load %v1793 : !llvm.ptr -> i32
%v1795 = arith.index_cast %v1651 : index to i32
%v1796 = arith.muli %v1795, %v1794 : i32
%v1797 = arith.index_cast %v1772 : index to i32
%v1798 = arith.addi %v1796, %v1797 : i32
%v1799 = arith.truncf %v1788 : f64 to f32
%v1800 = arith.extsi %v1798 : i32 to i64
%v1801 = llvm.getelementptr %v1791[%v1800] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1799, %v1801 : f32, !llvm.ptr
%v1802 = arith.addi %v1772, %v1767 : index
cf.br ^b67(%v1802 : index)
^b69(%v1803: index):
%v1804 = arith.addi %v1651, %v1646 : index
cf.br ^b55(%v1804 : index)
^b57(%v1805: index):
%v1806 = llvm.load %v1594 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1807 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1808 = llvm.extractvalue %v1806[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1809 = llvm.insertvalue %v1808, %v1807[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1810 = llvm.extractvalue %v1806[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1811 = llvm.insertvalue %v1810, %v1809[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1812 = llvm.extractvalue %v1806[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1813 = llvm.insertvalue %v1812, %v1811[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1814 = llvm.extractvalue %v1806[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1815 = llvm.insertvalue %v1814, %v1813[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1816 = llvm.extractvalue %v1806[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1817 = llvm.insertvalue %v1816, %v1815[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1818 = llvm.extractvalue %v1806[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1819 = llvm.insertvalue %v1818, %v1817[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1819, %v1600 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1820 = llvm.load %v1600 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1820 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_relu_backward(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1821 = llvm.mlir.constant(1 : i64) : i64
%v1822 = llvm.alloca %v1821 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1823 = llvm.mlir.constant(1 : i64) : i64
%v1824 = llvm.alloca %v1823 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1825 = llvm.mlir.constant(1 : i64) : i64
%v1826 = llvm.alloca %v1825 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1827 = llvm.mlir.constant(1 : i64) : i64
%v1828 = llvm.alloca %v1827 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1829 = llvm.mlir.constant(1 : i64) : i64
%v1830 = llvm.alloca %v1829 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1831 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1832 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1833 = llvm.insertvalue %v1832, %v1831[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1834 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1835 = llvm.insertvalue %v1834, %v1833[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1836 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1837 = llvm.insertvalue %v1836, %v1835[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1838 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1839 = llvm.insertvalue %v1838, %v1837[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1840 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1841 = llvm.insertvalue %v1840, %v1839[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1842 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1843 = llvm.insertvalue %v1842, %v1841[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1843, %v1822 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1844 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1845 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1846 = llvm.insertvalue %v1845, %v1844[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1847 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1848 = llvm.insertvalue %v1847, %v1846[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1849 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1850 = llvm.insertvalue %v1849, %v1848[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1851 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1852 = llvm.insertvalue %v1851, %v1850[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1853 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1854 = llvm.insertvalue %v1853, %v1852[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1855 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1856 = llvm.insertvalue %v1855, %v1854[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1856, %v1824 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1857 = llvm.load %v1822 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1858 = llvm.getelementptr %v1822[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1859 = llvm.load %v1858 : !llvm.ptr -> i32
%v1860 = llvm.load %v1822 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1861 = llvm.getelementptr %v1822[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1862 = llvm.load %v1861 : !llvm.ptr -> i32
%v1863 = llvm.load %v1822 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1864 = llvm.getelementptr %v1822[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1865 = llvm.load %v1864 : !llvm.ptr -> i32
%v1866 = llvm.load %v1822 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1867 = llvm.getelementptr %v1822[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1868 = llvm.load %v1867 : !llvm.ptr -> i32
%v1869 = func.call @tensor_zeros(%v1859, %v1862, %v1865, %v1868) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1870 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1871 = llvm.extractvalue %v1869[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1872 = llvm.insertvalue %v1871, %v1870[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1873 = llvm.extractvalue %v1869[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1874 = llvm.insertvalue %v1873, %v1872[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1875 = llvm.extractvalue %v1869[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1876 = llvm.insertvalue %v1875, %v1874[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1877 = llvm.extractvalue %v1869[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1878 = llvm.insertvalue %v1877, %v1876[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1879 = llvm.extractvalue %v1869[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1880 = llvm.insertvalue %v1879, %v1878[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1881 = llvm.extractvalue %v1869[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1882 = llvm.insertvalue %v1881, %v1880[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1882, %v1826 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1883 = llvm.load %v1826 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1883, %v1828 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1884 = arith.constant 0 : i32
%v1885 = llvm.load %v1822 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1886 = llvm.getelementptr %v1822[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1887 = llvm.load %v1886 : !llvm.ptr -> i32
%v1888 = arith.index_cast %v1884 : i32 to index
%v1889 = arith.index_cast %v1887 : i32 to index
%v1890 = arith.constant 1 : index
%v1891 = arith.constant -1 : index
%v1892 = arith.cmpi sle, %v1888, %v1889 : index
%v1893 = arith.select %v1892, %v1890, %v1891 : index
cf.br ^b70(%v1888 : index)
^b70(%v1894: index):
%v1895 = arith.cmpi slt, %v1894, %v1889 : index
%v1896 = arith.cmpi sgt, %v1894, %v1889 : index
%v1897 = arith.select %v1892, %v1895, %v1896 : i1
cf.cond_br %v1897, ^b71(%v1894 : index), ^b72(%v1894 : index)
^b71(%v1898: index):
%v1899 = llvm.load %v1822 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1900 = llvm.getelementptr %v1822[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1901 = llvm.load %v1900 : !llvm.ptr -> !llvm.ptr
%v1902 = arith.index_cast %v1898 : index to i64
%v1903 = llvm.getelementptr %v1901[%v1902] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1904 = llvm.load %v1903 : !llvm.ptr -> f32
%v1905 = arith.constant 0.0 : f64
%v1906 = arith.extf %v1904 : f32 to f64
%v1907 = arith.cmpf ogt, %v1906, %v1905 : f64
cf.cond_br %v1907, ^b73, ^b74
^b73:
%v1908 = llvm.load %v1824 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1909 = llvm.getelementptr %v1824[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1910 = llvm.load %v1909 : !llvm.ptr -> !llvm.ptr
%v1911 = arith.index_cast %v1898 : index to i64
%v1912 = llvm.getelementptr %v1910[%v1911] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1913 = llvm.load %v1912 : !llvm.ptr -> f32
%v1914 = llvm.load %v1828 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1915 = llvm.getelementptr %v1828[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1916 = llvm.load %v1915 : !llvm.ptr -> !llvm.ptr
%v1917 = arith.index_cast %v1898 : index to i64
%v1918 = llvm.getelementptr %v1916[%v1917] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1913, %v1918 : f32, !llvm.ptr
cf.br ^b75
^b74:
%v1919 = arith.constant 0.0 : f64
%v1920 = llvm.load %v1828 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1921 = llvm.getelementptr %v1828[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1922 = llvm.load %v1921 : !llvm.ptr -> !llvm.ptr
%v1923 = arith.truncf %v1919 : f64 to f32
%v1924 = arith.index_cast %v1898 : index to i64
%v1925 = llvm.getelementptr %v1922[%v1924] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1923, %v1925 : f32, !llvm.ptr
cf.br ^b75
^b75:
%v1926 = arith.addi %v1898, %v1893 : index
cf.br ^b70(%v1926 : index)
^b72(%v1927: index):
%v1928 = llvm.load %v1828 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1929 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1930 = llvm.extractvalue %v1928[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1931 = llvm.insertvalue %v1930, %v1929[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1932 = llvm.extractvalue %v1928[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1933 = llvm.insertvalue %v1932, %v1931[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1934 = llvm.extractvalue %v1928[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1935 = llvm.insertvalue %v1934, %v1933[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1936 = llvm.extractvalue %v1928[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1937 = llvm.insertvalue %v1936, %v1935[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1938 = llvm.extractvalue %v1928[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1939 = llvm.insertvalue %v1938, %v1937[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1940 = llvm.extractvalue %v1928[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1941 = llvm.insertvalue %v1940, %v1939[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1941, %v1830 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1942 = llvm.load %v1830 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1942 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_sigmoid_backward(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1943 = llvm.mlir.constant(1 : i64) : i64
%v1944 = llvm.alloca %v1943 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1945 = llvm.mlir.constant(1 : i64) : i64
%v1946 = llvm.alloca %v1945 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1947 = llvm.mlir.constant(1 : i64) : i64
%v1948 = llvm.alloca %v1947 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1949 = llvm.mlir.constant(1 : i64) : i64
%v1950 = llvm.alloca %v1949 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1951 = llvm.mlir.constant(1 : i64) : i64
%v1952 = llvm.alloca %v1951 x f32 : (i64) -> !llvm.ptr
%v1953 = llvm.mlir.constant(1 : i64) : i64
%v1954 = llvm.alloca %v1953 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v1955 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1956 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1957 = llvm.insertvalue %v1956, %v1955[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1958 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1959 = llvm.insertvalue %v1958, %v1957[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1960 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1961 = llvm.insertvalue %v1960, %v1959[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1962 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1963 = llvm.insertvalue %v1962, %v1961[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1964 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1965 = llvm.insertvalue %v1964, %v1963[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1966 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1967 = llvm.insertvalue %v1966, %v1965[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1967, %v1944 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1968 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1969 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1970 = llvm.insertvalue %v1969, %v1968[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1971 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1972 = llvm.insertvalue %v1971, %v1970[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1973 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1974 = llvm.insertvalue %v1973, %v1972[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1975 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1976 = llvm.insertvalue %v1975, %v1974[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1977 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1978 = llvm.insertvalue %v1977, %v1976[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1979 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1980 = llvm.insertvalue %v1979, %v1978[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v1980, %v1946 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1981 = llvm.load %v1944 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1982 = llvm.getelementptr %v1944[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1983 = llvm.load %v1982 : !llvm.ptr -> i32
%v1984 = llvm.load %v1944 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1985 = llvm.getelementptr %v1944[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1986 = llvm.load %v1985 : !llvm.ptr -> i32
%v1987 = llvm.load %v1944 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1988 = llvm.getelementptr %v1944[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1989 = llvm.load %v1988 : !llvm.ptr -> i32
%v1990 = llvm.load %v1944 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1991 = llvm.getelementptr %v1944[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1992 = llvm.load %v1991 : !llvm.ptr -> i32
%v1993 = func.call @tensor_zeros(%v1983, %v1986, %v1989, %v1992) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1994 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1995 = llvm.extractvalue %v1993[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1996 = llvm.insertvalue %v1995, %v1994[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1997 = llvm.extractvalue %v1993[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1998 = llvm.insertvalue %v1997, %v1996[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1999 = llvm.extractvalue %v1993[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2000 = llvm.insertvalue %v1999, %v1998[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2001 = llvm.extractvalue %v1993[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2002 = llvm.insertvalue %v2001, %v2000[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2003 = llvm.extractvalue %v1993[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2004 = llvm.insertvalue %v2003, %v2002[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2005 = llvm.extractvalue %v1993[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2006 = llvm.insertvalue %v2005, %v2004[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2006, %v1948 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2007 = llvm.load %v1948 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2007, %v1950 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2008 = arith.constant 0 : i32
%v2009 = llvm.load %v1944 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2010 = llvm.getelementptr %v1944[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2011 = llvm.load %v2010 : !llvm.ptr -> i32
%v2012 = arith.index_cast %v2008 : i32 to index
%v2013 = arith.index_cast %v2011 : i32 to index
%v2014 = arith.constant 1 : index
%v2015 = arith.constant -1 : index
%v2016 = arith.cmpi sle, %v2012, %v2013 : index
%v2017 = arith.select %v2016, %v2014, %v2015 : index
cf.br ^b76(%v2012 : index)
^b76(%v2018: index):
%v2019 = arith.cmpi slt, %v2018, %v2013 : index
%v2020 = arith.cmpi sgt, %v2018, %v2013 : index
%v2021 = arith.select %v2016, %v2019, %v2020 : i1
cf.cond_br %v2021, ^b77(%v2018 : index), ^b78(%v2018 : index)
^b77(%v2022: index):
%v2023 = llvm.load %v1944 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2024 = llvm.getelementptr %v1944[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2025 = llvm.load %v2024 : !llvm.ptr -> !llvm.ptr
%v2026 = arith.index_cast %v2022 : index to i64
%v2027 = llvm.getelementptr %v2025[%v2026] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2028 = llvm.load %v2027 : !llvm.ptr -> f32
llvm.store %v2028, %v1952 : f32, !llvm.ptr
%v2029 = llvm.load %v1946 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2030 = llvm.getelementptr %v1946[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2031 = llvm.load %v2030 : !llvm.ptr -> !llvm.ptr
%v2032 = arith.index_cast %v2022 : index to i64
%v2033 = llvm.getelementptr %v2031[%v2032] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2034 = llvm.load %v2033 : !llvm.ptr -> f32
%v2035 = llvm.load %v1952 : !llvm.ptr -> f32
%v2036 = arith.mulf %v2034, %v2035 : f32
%v2037 = arith.constant 1.0 : f64
%v2038 = llvm.load %v1952 : !llvm.ptr -> f32
%v2039 = arith.extf %v2038 : f32 to f64
%v2040 = arith.subf %v2037, %v2039 : f64
%v2041 = arith.extf %v2036 : f32 to f64
%v2042 = arith.mulf %v2041, %v2040 : f64
%v2043 = llvm.load %v1950 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2044 = llvm.getelementptr %v1950[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2045 = llvm.load %v2044 : !llvm.ptr -> !llvm.ptr
%v2046 = arith.truncf %v2042 : f64 to f32
%v2047 = arith.index_cast %v2022 : index to i64
%v2048 = llvm.getelementptr %v2045[%v2047] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v2046, %v2048 : f32, !llvm.ptr
%v2049 = arith.addi %v2022, %v2017 : index
cf.br ^b76(%v2049 : index)
^b78(%v2050: index):
%v2051 = llvm.load %v1950 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2052 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2053 = llvm.extractvalue %v2051[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2054 = llvm.insertvalue %v2053, %v2052[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2055 = llvm.extractvalue %v2051[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2056 = llvm.insertvalue %v2055, %v2054[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2057 = llvm.extractvalue %v2051[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2058 = llvm.insertvalue %v2057, %v2056[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2059 = llvm.extractvalue %v2051[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2060 = llvm.insertvalue %v2059, %v2058[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2061 = llvm.extractvalue %v2051[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2062 = llvm.insertvalue %v2061, %v2060[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2063 = llvm.extractvalue %v2051[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2064 = llvm.insertvalue %v2063, %v2062[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2064, %v1954 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2065 = llvm.load %v1954 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v2065 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_tanh_backward(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v2066 = llvm.mlir.constant(1 : i64) : i64
%v2067 = llvm.alloca %v2066 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2068 = llvm.mlir.constant(1 : i64) : i64
%v2069 = llvm.alloca %v2068 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2070 = llvm.mlir.constant(1 : i64) : i64
%v2071 = llvm.alloca %v2070 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2072 = llvm.mlir.constant(1 : i64) : i64
%v2073 = llvm.alloca %v2072 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2074 = llvm.mlir.constant(1 : i64) : i64
%v2075 = llvm.alloca %v2074 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2076 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2077 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2078 = llvm.insertvalue %v2077, %v2076[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2079 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2080 = llvm.insertvalue %v2079, %v2078[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2081 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2082 = llvm.insertvalue %v2081, %v2080[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2083 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2084 = llvm.insertvalue %v2083, %v2082[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2085 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2086 = llvm.insertvalue %v2085, %v2084[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2087 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2088 = llvm.insertvalue %v2087, %v2086[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2088, %v2067 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2089 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2090 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2091 = llvm.insertvalue %v2090, %v2089[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2092 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2093 = llvm.insertvalue %v2092, %v2091[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2094 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2095 = llvm.insertvalue %v2094, %v2093[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2096 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2097 = llvm.insertvalue %v2096, %v2095[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2098 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2099 = llvm.insertvalue %v2098, %v2097[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2100 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2101 = llvm.insertvalue %v2100, %v2099[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2101, %v2069 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2102 = llvm.load %v2067 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2103 = llvm.getelementptr %v2067[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2104 = llvm.load %v2103 : !llvm.ptr -> i32
%v2105 = llvm.load %v2067 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2106 = llvm.getelementptr %v2067[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2107 = llvm.load %v2106 : !llvm.ptr -> i32
%v2108 = llvm.load %v2067 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2109 = llvm.getelementptr %v2067[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2110 = llvm.load %v2109 : !llvm.ptr -> i32
%v2111 = llvm.load %v2067 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2112 = llvm.getelementptr %v2067[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2113 = llvm.load %v2112 : !llvm.ptr -> i32
%v2114 = func.call @tensor_zeros(%v2104, %v2107, %v2110, %v2113) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2115 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2116 = llvm.extractvalue %v2114[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2117 = llvm.insertvalue %v2116, %v2115[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2118 = llvm.extractvalue %v2114[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2119 = llvm.insertvalue %v2118, %v2117[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2120 = llvm.extractvalue %v2114[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2121 = llvm.insertvalue %v2120, %v2119[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2122 = llvm.extractvalue %v2114[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2123 = llvm.insertvalue %v2122, %v2121[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2124 = llvm.extractvalue %v2114[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2125 = llvm.insertvalue %v2124, %v2123[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2126 = llvm.extractvalue %v2114[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2127 = llvm.insertvalue %v2126, %v2125[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2127, %v2071 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2128 = llvm.load %v2071 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2128, %v2073 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2129 = arith.constant 0 : i32
%v2130 = llvm.load %v2067 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2131 = llvm.getelementptr %v2067[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2132 = llvm.load %v2131 : !llvm.ptr -> i32
%v2133 = arith.index_cast %v2129 : i32 to index
%v2134 = arith.index_cast %v2132 : i32 to index
%v2135 = arith.constant 1 : index
%v2136 = arith.constant -1 : index
%v2137 = arith.cmpi sle, %v2133, %v2134 : index
%v2138 = arith.select %v2137, %v2135, %v2136 : index
cf.br ^b79(%v2133 : index)
^b79(%v2139: index):
%v2140 = arith.cmpi slt, %v2139, %v2134 : index
%v2141 = arith.cmpi sgt, %v2139, %v2134 : index
%v2142 = arith.select %v2137, %v2140, %v2141 : i1
cf.cond_br %v2142, ^b80(%v2139 : index), ^b81(%v2139 : index)
^b80(%v2143: index):
%v2144 = llvm.load %v2067 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2145 = llvm.getelementptr %v2067[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2146 = llvm.load %v2145 : !llvm.ptr -> !llvm.ptr
%v2147 = arith.index_cast %v2143 : index to i64
%v2148 = llvm.getelementptr %v2146[%v2147] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2149 = llvm.load %v2148 : !llvm.ptr -> f32
%v2150 = llvm.load %v2069 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2151 = llvm.getelementptr %v2069[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2152 = llvm.load %v2151 : !llvm.ptr -> !llvm.ptr
%v2153 = arith.index_cast %v2143 : index to i64
%v2154 = llvm.getelementptr %v2152[%v2153] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2155 = llvm.load %v2154 : !llvm.ptr -> f32
%v2156 = arith.constant 1.0 : f64
%v2157 = arith.mulf %v2149, %v2149 : f32
%v2158 = arith.extf %v2157 : f32 to f64
%v2159 = arith.subf %v2156, %v2158 : f64
%v2160 = arith.extf %v2155 : f32 to f64
%v2161 = arith.mulf %v2160, %v2159 : f64
%v2162 = llvm.load %v2073 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2163 = llvm.getelementptr %v2073[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2164 = llvm.load %v2163 : !llvm.ptr -> !llvm.ptr
%v2165 = arith.truncf %v2161 : f64 to f32
%v2166 = arith.index_cast %v2143 : index to i64
%v2167 = llvm.getelementptr %v2164[%v2166] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v2165, %v2167 : f32, !llvm.ptr
%v2168 = arith.addi %v2143, %v2138 : index
cf.br ^b79(%v2168 : index)
^b81(%v2169: index):
%v2170 = llvm.load %v2073 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2171 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2172 = llvm.extractvalue %v2170[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2173 = llvm.insertvalue %v2172, %v2171[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2174 = llvm.extractvalue %v2170[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2175 = llvm.insertvalue %v2174, %v2173[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2176 = llvm.extractvalue %v2170[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2177 = llvm.insertvalue %v2176, %v2175[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2178 = llvm.extractvalue %v2170[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2179 = llvm.insertvalue %v2178, %v2177[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2180 = llvm.extractvalue %v2170[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2181 = llvm.insertvalue %v2180, %v2179[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2182 = llvm.extractvalue %v2170[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2183 = llvm.insertvalue %v2182, %v2181[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2183, %v2075 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2184 = llvm.load %v2075 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v2184 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_mul_backward_a(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg2: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v2185 = llvm.mlir.constant(1 : i64) : i64
%v2186 = llvm.alloca %v2185 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2187 = llvm.mlir.constant(1 : i64) : i64
%v2188 = llvm.alloca %v2187 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2189 = llvm.mlir.constant(1 : i64) : i64
%v2190 = llvm.alloca %v2189 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2191 = llvm.mlir.constant(1 : i64) : i64
%v2192 = llvm.alloca %v2191 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2193 = llvm.mlir.constant(1 : i64) : i64
%v2194 = llvm.alloca %v2193 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2195 = llvm.mlir.constant(1 : i64) : i64
%v2196 = llvm.alloca %v2195 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2197 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2198 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2199 = llvm.insertvalue %v2198, %v2197[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2200 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2201 = llvm.insertvalue %v2200, %v2199[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2202 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2203 = llvm.insertvalue %v2202, %v2201[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2204 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2205 = llvm.insertvalue %v2204, %v2203[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2206 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2207 = llvm.insertvalue %v2206, %v2205[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2208 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2209 = llvm.insertvalue %v2208, %v2207[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2209, %v2186 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2210 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2211 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2212 = llvm.insertvalue %v2211, %v2210[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2213 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2214 = llvm.insertvalue %v2213, %v2212[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2215 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2216 = llvm.insertvalue %v2215, %v2214[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2217 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2218 = llvm.insertvalue %v2217, %v2216[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2219 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2220 = llvm.insertvalue %v2219, %v2218[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2221 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2222 = llvm.insertvalue %v2221, %v2220[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2222, %v2188 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2223 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2224 = llvm.extractvalue %arg2[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2225 = llvm.insertvalue %v2224, %v2223[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2226 = llvm.extractvalue %arg2[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2227 = llvm.insertvalue %v2226, %v2225[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2228 = llvm.extractvalue %arg2[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2229 = llvm.insertvalue %v2228, %v2227[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2230 = llvm.extractvalue %arg2[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2231 = llvm.insertvalue %v2230, %v2229[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2232 = llvm.extractvalue %arg2[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2233 = llvm.insertvalue %v2232, %v2231[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2234 = llvm.extractvalue %arg2[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2235 = llvm.insertvalue %v2234, %v2233[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2235, %v2190 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2236 = llvm.load %v2186 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2237 = llvm.getelementptr %v2186[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2238 = llvm.load %v2237 : !llvm.ptr -> i32
%v2239 = llvm.load %v2186 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2240 = llvm.getelementptr %v2186[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2241 = llvm.load %v2240 : !llvm.ptr -> i32
%v2242 = llvm.load %v2186 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2243 = llvm.getelementptr %v2186[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2244 = llvm.load %v2243 : !llvm.ptr -> i32
%v2245 = llvm.load %v2186 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2246 = llvm.getelementptr %v2186[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2247 = llvm.load %v2246 : !llvm.ptr -> i32
%v2248 = func.call @tensor_zeros(%v2238, %v2241, %v2244, %v2247) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2249 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2250 = llvm.extractvalue %v2248[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2251 = llvm.insertvalue %v2250, %v2249[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2252 = llvm.extractvalue %v2248[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2253 = llvm.insertvalue %v2252, %v2251[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2254 = llvm.extractvalue %v2248[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2255 = llvm.insertvalue %v2254, %v2253[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2256 = llvm.extractvalue %v2248[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2257 = llvm.insertvalue %v2256, %v2255[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2258 = llvm.extractvalue %v2248[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2259 = llvm.insertvalue %v2258, %v2257[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2260 = llvm.extractvalue %v2248[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2261 = llvm.insertvalue %v2260, %v2259[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2261, %v2192 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2262 = llvm.load %v2192 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2262, %v2194 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2263 = arith.constant 0 : i32
%v2264 = llvm.load %v2186 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2265 = llvm.getelementptr %v2186[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2266 = llvm.load %v2265 : !llvm.ptr -> i32
%v2267 = arith.index_cast %v2263 : i32 to index
%v2268 = arith.index_cast %v2266 : i32 to index
%v2269 = arith.constant 1 : index
%v2270 = arith.constant -1 : index
%v2271 = arith.cmpi sle, %v2267, %v2268 : index
%v2272 = arith.select %v2271, %v2269, %v2270 : index
cf.br ^b82(%v2267 : index)
^b82(%v2273: index):
%v2274 = arith.cmpi slt, %v2273, %v2268 : index
%v2275 = arith.cmpi sgt, %v2273, %v2268 : index
%v2276 = arith.select %v2271, %v2274, %v2275 : i1
cf.cond_br %v2276, ^b83(%v2273 : index), ^b84(%v2273 : index)
^b83(%v2277: index):
%v2278 = llvm.load %v2190 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2279 = llvm.getelementptr %v2190[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2280 = llvm.load %v2279 : !llvm.ptr -> !llvm.ptr
%v2281 = arith.index_cast %v2277 : index to i64
%v2282 = llvm.getelementptr %v2280[%v2281] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2283 = llvm.load %v2282 : !llvm.ptr -> f32
%v2284 = llvm.load %v2188 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2285 = llvm.getelementptr %v2188[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2286 = llvm.load %v2285 : !llvm.ptr -> !llvm.ptr
%v2287 = arith.index_cast %v2277 : index to i64
%v2288 = llvm.getelementptr %v2286[%v2287] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2289 = llvm.load %v2288 : !llvm.ptr -> f32
%v2290 = arith.mulf %v2283, %v2289 : f32
%v2291 = llvm.load %v2194 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2292 = llvm.getelementptr %v2194[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2293 = llvm.load %v2292 : !llvm.ptr -> !llvm.ptr
%v2294 = arith.index_cast %v2277 : index to i64
%v2295 = llvm.getelementptr %v2293[%v2294] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v2290, %v2295 : f32, !llvm.ptr
%v2296 = arith.addi %v2277, %v2272 : index
cf.br ^b82(%v2296 : index)
^b84(%v2297: index):
%v2298 = llvm.load %v2194 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2299 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2300 = llvm.extractvalue %v2298[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2301 = llvm.insertvalue %v2300, %v2299[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2302 = llvm.extractvalue %v2298[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2303 = llvm.insertvalue %v2302, %v2301[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2304 = llvm.extractvalue %v2298[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2305 = llvm.insertvalue %v2304, %v2303[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2306 = llvm.extractvalue %v2298[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2307 = llvm.insertvalue %v2306, %v2305[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2308 = llvm.extractvalue %v2298[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2309 = llvm.insertvalue %v2308, %v2307[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2310 = llvm.extractvalue %v2298[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2311 = llvm.insertvalue %v2310, %v2309[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2311, %v2196 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2312 = llvm.load %v2196 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v2312 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_mul_backward_b(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg2: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v2313 = llvm.mlir.constant(1 : i64) : i64
%v2314 = llvm.alloca %v2313 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2315 = llvm.mlir.constant(1 : i64) : i64
%v2316 = llvm.alloca %v2315 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2317 = llvm.mlir.constant(1 : i64) : i64
%v2318 = llvm.alloca %v2317 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2319 = llvm.mlir.constant(1 : i64) : i64
%v2320 = llvm.alloca %v2319 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2321 = llvm.mlir.constant(1 : i64) : i64
%v2322 = llvm.alloca %v2321 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2323 = llvm.mlir.constant(1 : i64) : i64
%v2324 = llvm.alloca %v2323 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2325 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2326 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2327 = llvm.insertvalue %v2326, %v2325[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2328 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2329 = llvm.insertvalue %v2328, %v2327[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2330 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2331 = llvm.insertvalue %v2330, %v2329[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2332 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2333 = llvm.insertvalue %v2332, %v2331[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2334 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2335 = llvm.insertvalue %v2334, %v2333[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2336 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2337 = llvm.insertvalue %v2336, %v2335[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2337, %v2314 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2338 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2339 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2340 = llvm.insertvalue %v2339, %v2338[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2341 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2342 = llvm.insertvalue %v2341, %v2340[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2343 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2344 = llvm.insertvalue %v2343, %v2342[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2345 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2346 = llvm.insertvalue %v2345, %v2344[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2347 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2348 = llvm.insertvalue %v2347, %v2346[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2349 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2350 = llvm.insertvalue %v2349, %v2348[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2350, %v2316 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2351 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2352 = llvm.extractvalue %arg2[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2353 = llvm.insertvalue %v2352, %v2351[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2354 = llvm.extractvalue %arg2[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2355 = llvm.insertvalue %v2354, %v2353[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2356 = llvm.extractvalue %arg2[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2357 = llvm.insertvalue %v2356, %v2355[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2358 = llvm.extractvalue %arg2[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2359 = llvm.insertvalue %v2358, %v2357[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2360 = llvm.extractvalue %arg2[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2361 = llvm.insertvalue %v2360, %v2359[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2362 = llvm.extractvalue %arg2[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2363 = llvm.insertvalue %v2362, %v2361[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2363, %v2318 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2364 = llvm.load %v2316 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2365 = llvm.getelementptr %v2316[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2366 = llvm.load %v2365 : !llvm.ptr -> i32
%v2367 = llvm.load %v2316 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2368 = llvm.getelementptr %v2316[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2369 = llvm.load %v2368 : !llvm.ptr -> i32
%v2370 = llvm.load %v2316 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2371 = llvm.getelementptr %v2316[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2372 = llvm.load %v2371 : !llvm.ptr -> i32
%v2373 = llvm.load %v2316 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2374 = llvm.getelementptr %v2316[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2375 = llvm.load %v2374 : !llvm.ptr -> i32
%v2376 = func.call @tensor_zeros(%v2366, %v2369, %v2372, %v2375) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2377 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2378 = llvm.extractvalue %v2376[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2379 = llvm.insertvalue %v2378, %v2377[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2380 = llvm.extractvalue %v2376[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2381 = llvm.insertvalue %v2380, %v2379[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2382 = llvm.extractvalue %v2376[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2383 = llvm.insertvalue %v2382, %v2381[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2384 = llvm.extractvalue %v2376[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2385 = llvm.insertvalue %v2384, %v2383[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2386 = llvm.extractvalue %v2376[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2387 = llvm.insertvalue %v2386, %v2385[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2388 = llvm.extractvalue %v2376[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2389 = llvm.insertvalue %v2388, %v2387[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2389, %v2320 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2390 = llvm.load %v2320 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2390, %v2322 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2391 = arith.constant 0 : i32
%v2392 = llvm.load %v2316 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2393 = llvm.getelementptr %v2316[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2394 = llvm.load %v2393 : !llvm.ptr -> i32
%v2395 = arith.index_cast %v2391 : i32 to index
%v2396 = arith.index_cast %v2394 : i32 to index
%v2397 = arith.constant 1 : index
%v2398 = arith.constant -1 : index
%v2399 = arith.cmpi sle, %v2395, %v2396 : index
%v2400 = arith.select %v2399, %v2397, %v2398 : index
cf.br ^b85(%v2395 : index)
^b85(%v2401: index):
%v2402 = arith.cmpi slt, %v2401, %v2396 : index
%v2403 = arith.cmpi sgt, %v2401, %v2396 : index
%v2404 = arith.select %v2399, %v2402, %v2403 : i1
cf.cond_br %v2404, ^b86(%v2401 : index), ^b87(%v2401 : index)
^b86(%v2405: index):
%v2406 = llvm.load %v2318 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2407 = llvm.getelementptr %v2318[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2408 = llvm.load %v2407 : !llvm.ptr -> !llvm.ptr
%v2409 = arith.index_cast %v2405 : index to i64
%v2410 = llvm.getelementptr %v2408[%v2409] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2411 = llvm.load %v2410 : !llvm.ptr -> f32
%v2412 = llvm.load %v2314 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2413 = llvm.getelementptr %v2314[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2414 = llvm.load %v2413 : !llvm.ptr -> !llvm.ptr
%v2415 = arith.index_cast %v2405 : index to i64
%v2416 = llvm.getelementptr %v2414[%v2415] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2417 = llvm.load %v2416 : !llvm.ptr -> f32
%v2418 = arith.mulf %v2411, %v2417 : f32
%v2419 = llvm.load %v2322 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2420 = llvm.getelementptr %v2322[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2421 = llvm.load %v2420 : !llvm.ptr -> !llvm.ptr
%v2422 = arith.index_cast %v2405 : index to i64
%v2423 = llvm.getelementptr %v2421[%v2422] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v2418, %v2423 : f32, !llvm.ptr
%v2424 = arith.addi %v2405, %v2400 : index
cf.br ^b85(%v2424 : index)
^b87(%v2425: index):
%v2426 = llvm.load %v2322 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2427 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2428 = llvm.extractvalue %v2426[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2429 = llvm.insertvalue %v2428, %v2427[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2430 = llvm.extractvalue %v2426[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2431 = llvm.insertvalue %v2430, %v2429[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2432 = llvm.extractvalue %v2426[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2433 = llvm.insertvalue %v2432, %v2431[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2434 = llvm.extractvalue %v2426[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2435 = llvm.insertvalue %v2434, %v2433[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2436 = llvm.extractvalue %v2426[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2437 = llvm.insertvalue %v2436, %v2435[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2438 = llvm.extractvalue %v2426[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2439 = llvm.insertvalue %v2438, %v2437[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2439, %v2324 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2440 = llvm.load %v2324 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v2440 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_broadcast_add(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v2441 = llvm.mlir.constant(1 : i64) : i64
%v2442 = llvm.alloca %v2441 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2443 = llvm.mlir.constant(1 : i64) : i64
%v2444 = llvm.alloca %v2443 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2445 = llvm.mlir.constant(1 : i64) : i64
%v2446 = llvm.alloca %v2445 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2447 = llvm.mlir.constant(1 : i64) : i64
%v2448 = llvm.alloca %v2447 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2449 = llvm.mlir.constant(1 : i64) : i64
%v2450 = llvm.alloca %v2449 x i32 : (i64) -> !llvm.ptr
%v2451 = llvm.mlir.constant(1 : i64) : i64
%v2452 = llvm.alloca %v2451 x i32 : (i64) -> !llvm.ptr
%v2453 = llvm.mlir.constant(1 : i64) : i64
%v2454 = llvm.alloca %v2453 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2455 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2456 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2457 = llvm.insertvalue %v2456, %v2455[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2458 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2459 = llvm.insertvalue %v2458, %v2457[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2460 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2461 = llvm.insertvalue %v2460, %v2459[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2462 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2463 = llvm.insertvalue %v2462, %v2461[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2464 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2465 = llvm.insertvalue %v2464, %v2463[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2466 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2467 = llvm.insertvalue %v2466, %v2465[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2467, %v2442 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2468 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2469 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2470 = llvm.insertvalue %v2469, %v2468[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2471 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2472 = llvm.insertvalue %v2471, %v2470[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2473 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2474 = llvm.insertvalue %v2473, %v2472[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2475 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2476 = llvm.insertvalue %v2475, %v2474[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2477 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2478 = llvm.insertvalue %v2477, %v2476[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2479 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2480 = llvm.insertvalue %v2479, %v2478[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2480, %v2444 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2481 = llvm.load %v2442 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2482 = llvm.getelementptr %v2442[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2483 = llvm.load %v2482 : !llvm.ptr -> i32
%v2484 = llvm.load %v2442 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2485 = llvm.getelementptr %v2442[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2486 = llvm.load %v2485 : !llvm.ptr -> i32
%v2487 = llvm.load %v2442 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2488 = llvm.getelementptr %v2442[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2489 = llvm.load %v2488 : !llvm.ptr -> i32
%v2490 = llvm.load %v2442 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2491 = llvm.getelementptr %v2442[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2492 = llvm.load %v2491 : !llvm.ptr -> i32
%v2493 = func.call @tensor_zeros(%v2483, %v2486, %v2489, %v2492) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2494 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2495 = llvm.extractvalue %v2493[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2496 = llvm.insertvalue %v2495, %v2494[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2497 = llvm.extractvalue %v2493[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2498 = llvm.insertvalue %v2497, %v2496[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2499 = llvm.extractvalue %v2493[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2500 = llvm.insertvalue %v2499, %v2498[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2501 = llvm.extractvalue %v2493[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2502 = llvm.insertvalue %v2501, %v2500[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2503 = llvm.extractvalue %v2493[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2504 = llvm.insertvalue %v2503, %v2502[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2505 = llvm.extractvalue %v2493[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2506 = llvm.insertvalue %v2505, %v2504[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2506, %v2446 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2507 = llvm.load %v2446 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2507, %v2448 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2508 = arith.constant 0 : i32
%v2509 = llvm.load %v2442 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2510 = llvm.getelementptr %v2442[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2511 = llvm.load %v2510 : !llvm.ptr -> i32
%v2512 = arith.index_cast %v2508 : i32 to index
%v2513 = arith.index_cast %v2511 : i32 to index
%v2514 = arith.constant 1 : index
%v2515 = arith.constant -1 : index
%v2516 = arith.cmpi sle, %v2512, %v2513 : index
%v2517 = arith.select %v2516, %v2514, %v2515 : index
cf.br ^b88(%v2512 : index)
^b88(%v2518: index):
%v2519 = arith.cmpi slt, %v2518, %v2513 : index
%v2520 = arith.cmpi sgt, %v2518, %v2513 : index
%v2521 = arith.select %v2516, %v2519, %v2520 : i1
cf.cond_br %v2521, ^b89(%v2518 : index), ^b90(%v2518 : index)
^b89(%v2522: index):
%v2523 = arith.constant 0 : i32
llvm.store %v2523, %v2450 : i32, !llvm.ptr
%v2524 = llvm.load %v2444 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2525 = llvm.getelementptr %v2444[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2526 = llvm.load %v2525 : !llvm.ptr -> i32
%v2527 = arith.constant 1 : i32
%v2528 = arith.cmpi sgt, %v2526, %v2527 : i32
cf.cond_br %v2528, ^b91, ^b92
^b91:
%v2529 = arith.index_cast %v2522 : index to i32
llvm.store %v2529, %v2450 : i32, !llvm.ptr
cf.br ^b93
^b92:
cf.br ^b93
^b93:
%v2530 = arith.constant 0 : i32
%v2531 = llvm.load %v2442 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2532 = llvm.getelementptr %v2442[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2533 = llvm.load %v2532 : !llvm.ptr -> i32
%v2534 = arith.index_cast %v2530 : i32 to index
%v2535 = arith.index_cast %v2533 : i32 to index
%v2536 = arith.constant 1 : index
%v2537 = arith.constant -1 : index
%v2538 = arith.cmpi sle, %v2534, %v2535 : index
%v2539 = arith.select %v2538, %v2536, %v2537 : index
cf.br ^b94(%v2534 : index)
^b94(%v2540: index):
%v2541 = arith.cmpi slt, %v2540, %v2535 : index
%v2542 = arith.cmpi sgt, %v2540, %v2535 : index
%v2543 = arith.select %v2538, %v2541, %v2542 : i1
cf.cond_br %v2543, ^b95(%v2540 : index), ^b96(%v2540 : index)
^b95(%v2544: index):
%v2545 = arith.constant 0 : i32
llvm.store %v2545, %v2452 : i32, !llvm.ptr
%v2546 = llvm.load %v2444 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2547 = llvm.getelementptr %v2444[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2548 = llvm.load %v2547 : !llvm.ptr -> i32
%v2549 = arith.constant 1 : i32
%v2550 = arith.cmpi sgt, %v2548, %v2549 : i32
cf.cond_br %v2550, ^b97, ^b98
^b97:
%v2551 = arith.index_cast %v2544 : index to i32
llvm.store %v2551, %v2452 : i32, !llvm.ptr
cf.br ^b99
^b98:
cf.br ^b99
^b99:
%v2552 = llvm.load %v2442 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2553 = arith.constant 0 : i32
%v2554 = arith.constant 0 : i32
%v2555 = arith.index_cast %v2522 : index to i32
%v2556 = arith.index_cast %v2544 : index to i32
%v2557 = func.call @tensor_idx(%v2552, %v2555, %v2556, %v2553, %v2554) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, i32, i32, i32, i32) -> i32
%v2558 = llvm.load %v2444 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2559 = llvm.load %v2450 : !llvm.ptr -> i32
%v2560 = llvm.load %v2452 : !llvm.ptr -> i32
%v2561 = arith.constant 0 : i32
%v2562 = arith.constant 0 : i32
%v2563 = func.call @tensor_idx(%v2558, %v2559, %v2560, %v2561, %v2562) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, i32, i32, i32, i32) -> i32
%v2564 = llvm.load %v2442 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2565 = llvm.getelementptr %v2442[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2566 = llvm.load %v2565 : !llvm.ptr -> !llvm.ptr
%v2567 = arith.extsi %v2557 : i32 to i64
%v2568 = llvm.getelementptr %v2566[%v2567] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2569 = llvm.load %v2568 : !llvm.ptr -> f32
%v2570 = llvm.load %v2444 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2571 = llvm.getelementptr %v2444[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2572 = llvm.load %v2571 : !llvm.ptr -> !llvm.ptr
%v2573 = arith.extsi %v2563 : i32 to i64
%v2574 = llvm.getelementptr %v2572[%v2573] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2575 = llvm.load %v2574 : !llvm.ptr -> f32
%v2576 = arith.addf %v2569, %v2575 : f32
%v2577 = llvm.load %v2448 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2578 = llvm.getelementptr %v2448[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2579 = llvm.load %v2578 : !llvm.ptr -> !llvm.ptr
%v2580 = arith.extsi %v2557 : i32 to i64
%v2581 = llvm.getelementptr %v2579[%v2580] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v2576, %v2581 : f32, !llvm.ptr
%v2582 = arith.addi %v2544, %v2539 : index
cf.br ^b94(%v2582 : index)
^b96(%v2583: index):
%v2584 = arith.addi %v2522, %v2517 : index
cf.br ^b88(%v2584 : index)
^b90(%v2585: index):
%v2586 = llvm.load %v2448 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2587 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2588 = llvm.extractvalue %v2586[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2589 = llvm.insertvalue %v2588, %v2587[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2590 = llvm.extractvalue %v2586[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2591 = llvm.insertvalue %v2590, %v2589[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2592 = llvm.extractvalue %v2586[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2593 = llvm.insertvalue %v2592, %v2591[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2594 = llvm.extractvalue %v2586[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2595 = llvm.insertvalue %v2594, %v2593[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2596 = llvm.extractvalue %v2586[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2597 = llvm.insertvalue %v2596, %v2595[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2598 = llvm.extractvalue %v2586[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2599 = llvm.insertvalue %v2598, %v2597[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2599, %v2454 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2600 = llvm.load %v2454 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v2600 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_matmul(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v2601 = llvm.mlir.constant(1 : i64) : i64
%v2602 = llvm.alloca %v2601 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2603 = llvm.mlir.constant(1 : i64) : i64
%v2604 = llvm.alloca %v2603 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2605 = llvm.mlir.constant(1 : i64) : i64
%v2606 = llvm.alloca %v2605 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2607 = llvm.mlir.constant(1 : i64) : i64
%v2608 = llvm.alloca %v2607 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2609 = llvm.mlir.constant(1 : i64) : i64
%v2610 = llvm.alloca %v2609 x f32 : (i64) -> !llvm.ptr
%v2611 = llvm.mlir.constant(1 : i64) : i64
%v2612 = llvm.alloca %v2611 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2613 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2614 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2615 = llvm.insertvalue %v2614, %v2613[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2616 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2617 = llvm.insertvalue %v2616, %v2615[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2618 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2619 = llvm.insertvalue %v2618, %v2617[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2620 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2621 = llvm.insertvalue %v2620, %v2619[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2622 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2623 = llvm.insertvalue %v2622, %v2621[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2624 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2625 = llvm.insertvalue %v2624, %v2623[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2625, %v2602 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2626 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2627 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2628 = llvm.insertvalue %v2627, %v2626[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2629 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2630 = llvm.insertvalue %v2629, %v2628[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2631 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2632 = llvm.insertvalue %v2631, %v2630[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2633 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2634 = llvm.insertvalue %v2633, %v2632[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2635 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2636 = llvm.insertvalue %v2635, %v2634[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2637 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2638 = llvm.insertvalue %v2637, %v2636[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2638, %v2604 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2639 = llvm.load %v2602 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2640 = llvm.getelementptr %v2602[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2641 = llvm.load %v2640 : !llvm.ptr -> i32
%v2642 = llvm.load %v2602 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2643 = llvm.getelementptr %v2602[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2644 = llvm.load %v2643 : !llvm.ptr -> i32
%v2645 = llvm.load %v2604 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2646 = llvm.getelementptr %v2604[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2647 = llvm.load %v2646 : !llvm.ptr -> i32
%v2648 = arith.constant 1 : i32
%v2649 = arith.constant 1 : i32
%v2650 = func.call @tensor_zeros(%v2641, %v2647, %v2648, %v2649) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2651 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2652 = llvm.extractvalue %v2650[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2653 = llvm.insertvalue %v2652, %v2651[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2654 = llvm.extractvalue %v2650[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2655 = llvm.insertvalue %v2654, %v2653[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2656 = llvm.extractvalue %v2650[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2657 = llvm.insertvalue %v2656, %v2655[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2658 = llvm.extractvalue %v2650[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2659 = llvm.insertvalue %v2658, %v2657[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2660 = llvm.extractvalue %v2650[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2661 = llvm.insertvalue %v2660, %v2659[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2662 = llvm.extractvalue %v2650[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2663 = llvm.insertvalue %v2662, %v2661[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2663, %v2606 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2664 = llvm.load %v2606 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2664, %v2608 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2665 = arith.constant 0 : i32
%v2666 = arith.index_cast %v2665 : i32 to index
%v2667 = arith.index_cast %v2641 : i32 to index
%v2668 = arith.constant 1 : index
%v2669 = arith.constant -1 : index
%v2670 = arith.cmpi sle, %v2666, %v2667 : index
%v2671 = arith.select %v2670, %v2668, %v2669 : index
cf.br ^b100(%v2666 : index)
^b100(%v2672: index):
%v2673 = arith.cmpi slt, %v2672, %v2667 : index
%v2674 = arith.cmpi sgt, %v2672, %v2667 : index
%v2675 = arith.select %v2670, %v2673, %v2674 : i1
cf.cond_br %v2675, ^b101(%v2672 : index), ^b102(%v2672 : index)
^b101(%v2676: index):
%v2677 = arith.constant 0 : i32
%v2678 = arith.index_cast %v2677 : i32 to index
%v2679 = arith.index_cast %v2647 : i32 to index
%v2680 = arith.constant 1 : index
%v2681 = arith.constant -1 : index
%v2682 = arith.cmpi sle, %v2678, %v2679 : index
%v2683 = arith.select %v2682, %v2680, %v2681 : index
cf.br ^b103(%v2678 : index)
^b103(%v2684: index):
%v2685 = arith.cmpi slt, %v2684, %v2679 : index
%v2686 = arith.cmpi sgt, %v2684, %v2679 : index
%v2687 = arith.select %v2682, %v2685, %v2686 : i1
cf.cond_br %v2687, ^b104(%v2684 : index), ^b105(%v2684 : index)
^b104(%v2688: index):
%v2689 = arith.constant 0.0 : f64
%v2690 = arith.truncf %v2689 : f64 to f32
llvm.store %v2690, %v2610 : f32, !llvm.ptr
%v2691 = arith.constant 0 : i32
%v2692 = arith.index_cast %v2691 : i32 to index
%v2693 = arith.index_cast %v2644 : i32 to index
%v2694 = arith.constant 1 : index
%v2695 = arith.constant -1 : index
%v2696 = arith.cmpi sle, %v2692, %v2693 : index
%v2697 = arith.select %v2696, %v2694, %v2695 : index
cf.br ^b106(%v2692 : index)
^b106(%v2698: index):
%v2699 = arith.cmpi slt, %v2698, %v2693 : index
%v2700 = arith.cmpi sgt, %v2698, %v2693 : index
%v2701 = arith.select %v2696, %v2699, %v2700 : i1
cf.cond_br %v2701, ^b107(%v2698 : index), ^b108(%v2698 : index)
^b107(%v2702: index):
%v2703 = llvm.load %v2610 : !llvm.ptr -> f32
%v2704 = llvm.load %v2602 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2705 = llvm.getelementptr %v2602[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2706 = llvm.load %v2705 : !llvm.ptr -> !llvm.ptr
%v2707 = arith.index_cast %v2676 : index to i32
%v2708 = arith.muli %v2707, %v2644 : i32
%v2709 = arith.index_cast %v2702 : index to i32
%v2710 = arith.addi %v2708, %v2709 : i32
%v2711 = arith.extsi %v2710 : i32 to i64
%v2712 = llvm.getelementptr %v2706[%v2711] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2713 = llvm.load %v2712 : !llvm.ptr -> f32
%v2714 = llvm.load %v2604 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2715 = llvm.getelementptr %v2604[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2716 = llvm.load %v2715 : !llvm.ptr -> !llvm.ptr
%v2717 = arith.index_cast %v2702 : index to i32
%v2718 = arith.muli %v2717, %v2647 : i32
%v2719 = arith.index_cast %v2688 : index to i32
%v2720 = arith.addi %v2718, %v2719 : i32
%v2721 = arith.extsi %v2720 : i32 to i64
%v2722 = llvm.getelementptr %v2716[%v2721] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2723 = llvm.load %v2722 : !llvm.ptr -> f32
%v2724 = llvm.intr.fmuladd(%v2713, %v2723, %v2703) : (f32, f32, f32) -> f32
llvm.store %v2724, %v2610 : f32, !llvm.ptr
%v2725 = arith.addi %v2702, %v2697 : index
cf.br ^b106(%v2725 : index)
^b108(%v2726: index):
%v2727 = llvm.load %v2610 : !llvm.ptr -> f32
%v2728 = llvm.load %v2608 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2729 = llvm.getelementptr %v2608[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2730 = llvm.load %v2729 : !llvm.ptr -> !llvm.ptr
%v2731 = arith.index_cast %v2676 : index to i32
%v2732 = arith.muli %v2731, %v2647 : i32
%v2733 = arith.index_cast %v2688 : index to i32
%v2734 = arith.addi %v2732, %v2733 : i32
%v2735 = arith.extsi %v2734 : i32 to i64
%v2736 = llvm.getelementptr %v2730[%v2735] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v2727, %v2736 : f32, !llvm.ptr
%v2737 = arith.addi %v2688, %v2683 : index
cf.br ^b103(%v2737 : index)
^b105(%v2738: index):
%v2739 = arith.addi %v2676, %v2671 : index
cf.br ^b100(%v2739 : index)
^b102(%v2740: index):
%v2741 = llvm.load %v2608 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2742 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2743 = llvm.extractvalue %v2741[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2744 = llvm.insertvalue %v2743, %v2742[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2745 = llvm.extractvalue %v2741[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2746 = llvm.insertvalue %v2745, %v2744[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2747 = llvm.extractvalue %v2741[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2748 = llvm.insertvalue %v2747, %v2746[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2749 = llvm.extractvalue %v2741[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2750 = llvm.insertvalue %v2749, %v2748[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2751 = llvm.extractvalue %v2741[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2752 = llvm.insertvalue %v2751, %v2750[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2753 = llvm.extractvalue %v2741[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2754 = llvm.insertvalue %v2753, %v2752[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2754, %v2612 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2755 = llvm.load %v2612 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v2755 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_matmul_backward_a(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg2: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v2756 = llvm.mlir.constant(1 : i64) : i64
%v2757 = llvm.alloca %v2756 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2758 = llvm.mlir.constant(1 : i64) : i64
%v2759 = llvm.alloca %v2758 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2760 = llvm.mlir.constant(1 : i64) : i64
%v2761 = llvm.alloca %v2760 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2762 = llvm.mlir.constant(1 : i64) : i64
%v2763 = llvm.alloca %v2762 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2764 = llvm.mlir.constant(1 : i64) : i64
%v2765 = llvm.alloca %v2764 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2766 = llvm.mlir.constant(1 : i64) : i64
%v2767 = llvm.alloca %v2766 x f32 : (i64) -> !llvm.ptr
%v2768 = llvm.mlir.constant(1 : i64) : i64
%v2769 = llvm.alloca %v2768 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2770 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2771 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2772 = llvm.insertvalue %v2771, %v2770[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2773 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2774 = llvm.insertvalue %v2773, %v2772[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2775 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2776 = llvm.insertvalue %v2775, %v2774[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2777 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2778 = llvm.insertvalue %v2777, %v2776[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2779 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2780 = llvm.insertvalue %v2779, %v2778[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2781 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2782 = llvm.insertvalue %v2781, %v2780[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2782, %v2757 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2783 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2784 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2785 = llvm.insertvalue %v2784, %v2783[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2786 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2787 = llvm.insertvalue %v2786, %v2785[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2788 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2789 = llvm.insertvalue %v2788, %v2787[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2790 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2791 = llvm.insertvalue %v2790, %v2789[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2792 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2793 = llvm.insertvalue %v2792, %v2791[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2794 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2795 = llvm.insertvalue %v2794, %v2793[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2795, %v2759 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2796 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2797 = llvm.extractvalue %arg2[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2798 = llvm.insertvalue %v2797, %v2796[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2799 = llvm.extractvalue %arg2[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2800 = llvm.insertvalue %v2799, %v2798[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2801 = llvm.extractvalue %arg2[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2802 = llvm.insertvalue %v2801, %v2800[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2803 = llvm.extractvalue %arg2[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2804 = llvm.insertvalue %v2803, %v2802[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2805 = llvm.extractvalue %arg2[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2806 = llvm.insertvalue %v2805, %v2804[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2807 = llvm.extractvalue %arg2[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2808 = llvm.insertvalue %v2807, %v2806[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2808, %v2761 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2809 = llvm.load %v2761 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2810 = llvm.getelementptr %v2761[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2811 = llvm.load %v2810 : !llvm.ptr -> i32
%v2812 = llvm.load %v2761 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2813 = llvm.getelementptr %v2761[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2814 = llvm.load %v2813 : !llvm.ptr -> i32
%v2815 = llvm.load %v2757 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2816 = llvm.getelementptr %v2757[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2817 = llvm.load %v2816 : !llvm.ptr -> i32
%v2818 = arith.constant 1 : i32
%v2819 = arith.constant 1 : i32
%v2820 = func.call @tensor_zeros(%v2811, %v2817, %v2818, %v2819) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2821 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2822 = llvm.extractvalue %v2820[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2823 = llvm.insertvalue %v2822, %v2821[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2824 = llvm.extractvalue %v2820[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2825 = llvm.insertvalue %v2824, %v2823[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2826 = llvm.extractvalue %v2820[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2827 = llvm.insertvalue %v2826, %v2825[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2828 = llvm.extractvalue %v2820[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2829 = llvm.insertvalue %v2828, %v2827[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2830 = llvm.extractvalue %v2820[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2831 = llvm.insertvalue %v2830, %v2829[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2832 = llvm.extractvalue %v2820[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2833 = llvm.insertvalue %v2832, %v2831[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2833, %v2763 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2834 = llvm.load %v2763 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2834, %v2765 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2835 = arith.constant 0 : i32
%v2836 = arith.index_cast %v2835 : i32 to index
%v2837 = arith.index_cast %v2811 : i32 to index
%v2838 = arith.constant 1 : index
%v2839 = arith.constant -1 : index
%v2840 = arith.cmpi sle, %v2836, %v2837 : index
%v2841 = arith.select %v2840, %v2838, %v2839 : index
cf.br ^b109(%v2836 : index)
^b109(%v2842: index):
%v2843 = arith.cmpi slt, %v2842, %v2837 : index
%v2844 = arith.cmpi sgt, %v2842, %v2837 : index
%v2845 = arith.select %v2840, %v2843, %v2844 : i1
cf.cond_br %v2845, ^b110(%v2842 : index), ^b111(%v2842 : index)
^b110(%v2846: index):
%v2847 = arith.constant 0 : i32
%v2848 = arith.index_cast %v2847 : i32 to index
%v2849 = arith.index_cast %v2817 : i32 to index
%v2850 = arith.constant 1 : index
%v2851 = arith.constant -1 : index
%v2852 = arith.cmpi sle, %v2848, %v2849 : index
%v2853 = arith.select %v2852, %v2850, %v2851 : index
cf.br ^b112(%v2848 : index)
^b112(%v2854: index):
%v2855 = arith.cmpi slt, %v2854, %v2849 : index
%v2856 = arith.cmpi sgt, %v2854, %v2849 : index
%v2857 = arith.select %v2852, %v2855, %v2856 : i1
cf.cond_br %v2857, ^b113(%v2854 : index), ^b114(%v2854 : index)
^b113(%v2858: index):
%v2859 = arith.constant 0.0 : f64
%v2860 = arith.truncf %v2859 : f64 to f32
llvm.store %v2860, %v2767 : f32, !llvm.ptr
%v2861 = arith.constant 0 : i32
%v2862 = arith.index_cast %v2861 : i32 to index
%v2863 = arith.index_cast %v2814 : i32 to index
%v2864 = arith.constant 1 : index
%v2865 = arith.constant -1 : index
%v2866 = arith.cmpi sle, %v2862, %v2863 : index
%v2867 = arith.select %v2866, %v2864, %v2865 : index
cf.br ^b115(%v2862 : index)
^b115(%v2868: index):
%v2869 = arith.cmpi slt, %v2868, %v2863 : index
%v2870 = arith.cmpi sgt, %v2868, %v2863 : index
%v2871 = arith.select %v2866, %v2869, %v2870 : i1
cf.cond_br %v2871, ^b116(%v2868 : index), ^b117(%v2868 : index)
^b116(%v2872: index):
%v2873 = llvm.load %v2767 : !llvm.ptr -> f32
%v2874 = llvm.load %v2761 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2875 = llvm.getelementptr %v2761[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2876 = llvm.load %v2875 : !llvm.ptr -> !llvm.ptr
%v2877 = arith.index_cast %v2846 : index to i32
%v2878 = arith.muli %v2877, %v2814 : i32
%v2879 = arith.index_cast %v2872 : index to i32
%v2880 = arith.addi %v2878, %v2879 : i32
%v2881 = arith.extsi %v2880 : i32 to i64
%v2882 = llvm.getelementptr %v2876[%v2881] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2883 = llvm.load %v2882 : !llvm.ptr -> f32
%v2884 = llvm.load %v2759 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2885 = llvm.getelementptr %v2759[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2886 = llvm.load %v2885 : !llvm.ptr -> !llvm.ptr
%v2887 = arith.index_cast %v2858 : index to i32
%v2888 = arith.muli %v2887, %v2814 : i32
%v2889 = arith.index_cast %v2872 : index to i32
%v2890 = arith.addi %v2888, %v2889 : i32
%v2891 = arith.extsi %v2890 : i32 to i64
%v2892 = llvm.getelementptr %v2886[%v2891] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2893 = llvm.load %v2892 : !llvm.ptr -> f32
%v2894 = llvm.intr.fmuladd(%v2883, %v2893, %v2873) : (f32, f32, f32) -> f32
llvm.store %v2894, %v2767 : f32, !llvm.ptr
%v2895 = arith.addi %v2872, %v2867 : index
cf.br ^b115(%v2895 : index)
^b117(%v2896: index):
%v2897 = llvm.load %v2767 : !llvm.ptr -> f32
%v2898 = llvm.load %v2765 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2899 = llvm.getelementptr %v2765[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2900 = llvm.load %v2899 : !llvm.ptr -> !llvm.ptr
%v2901 = arith.index_cast %v2846 : index to i32
%v2902 = arith.muli %v2901, %v2817 : i32
%v2903 = arith.index_cast %v2858 : index to i32
%v2904 = arith.addi %v2902, %v2903 : i32
%v2905 = arith.extsi %v2904 : i32 to i64
%v2906 = llvm.getelementptr %v2900[%v2905] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v2897, %v2906 : f32, !llvm.ptr
%v2907 = arith.addi %v2858, %v2853 : index
cf.br ^b112(%v2907 : index)
^b114(%v2908: index):
%v2909 = arith.addi %v2846, %v2841 : index
cf.br ^b109(%v2909 : index)
^b111(%v2910: index):
%v2911 = llvm.load %v2765 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2912 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2913 = llvm.extractvalue %v2911[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2914 = llvm.insertvalue %v2913, %v2912[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2915 = llvm.extractvalue %v2911[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2916 = llvm.insertvalue %v2915, %v2914[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2917 = llvm.extractvalue %v2911[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2918 = llvm.insertvalue %v2917, %v2916[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2919 = llvm.extractvalue %v2911[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2920 = llvm.insertvalue %v2919, %v2918[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2921 = llvm.extractvalue %v2911[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2922 = llvm.insertvalue %v2921, %v2920[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2923 = llvm.extractvalue %v2911[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2924 = llvm.insertvalue %v2923, %v2922[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2924, %v2769 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2925 = llvm.load %v2769 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v2925 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_matmul_backward_b(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg2: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v2926 = llvm.mlir.constant(1 : i64) : i64
%v2927 = llvm.alloca %v2926 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2928 = llvm.mlir.constant(1 : i64) : i64
%v2929 = llvm.alloca %v2928 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2930 = llvm.mlir.constant(1 : i64) : i64
%v2931 = llvm.alloca %v2930 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2932 = llvm.mlir.constant(1 : i64) : i64
%v2933 = llvm.alloca %v2932 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2934 = llvm.mlir.constant(1 : i64) : i64
%v2935 = llvm.alloca %v2934 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2936 = llvm.mlir.constant(1 : i64) : i64
%v2937 = llvm.alloca %v2936 x f32 : (i64) -> !llvm.ptr
%v2938 = llvm.mlir.constant(1 : i64) : i64
%v2939 = llvm.alloca %v2938 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v2940 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2941 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2942 = llvm.insertvalue %v2941, %v2940[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2943 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2944 = llvm.insertvalue %v2943, %v2942[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2945 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2946 = llvm.insertvalue %v2945, %v2944[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2947 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2948 = llvm.insertvalue %v2947, %v2946[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2949 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2950 = llvm.insertvalue %v2949, %v2948[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2951 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2952 = llvm.insertvalue %v2951, %v2950[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2952, %v2927 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2953 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2954 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2955 = llvm.insertvalue %v2954, %v2953[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2956 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2957 = llvm.insertvalue %v2956, %v2955[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2958 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2959 = llvm.insertvalue %v2958, %v2957[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2960 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2961 = llvm.insertvalue %v2960, %v2959[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2962 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2963 = llvm.insertvalue %v2962, %v2961[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2964 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2965 = llvm.insertvalue %v2964, %v2963[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2965, %v2929 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2966 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2967 = llvm.extractvalue %arg2[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2968 = llvm.insertvalue %v2967, %v2966[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2969 = llvm.extractvalue %arg2[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2970 = llvm.insertvalue %v2969, %v2968[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2971 = llvm.extractvalue %arg2[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2972 = llvm.insertvalue %v2971, %v2970[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2973 = llvm.extractvalue %arg2[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2974 = llvm.insertvalue %v2973, %v2972[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2975 = llvm.extractvalue %arg2[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2976 = llvm.insertvalue %v2975, %v2974[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2977 = llvm.extractvalue %arg2[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2978 = llvm.insertvalue %v2977, %v2976[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v2978, %v2931 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2979 = llvm.load %v2927 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2980 = llvm.getelementptr %v2927[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2981 = llvm.load %v2980 : !llvm.ptr -> i32
%v2982 = llvm.load %v2927 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2983 = llvm.getelementptr %v2927[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2984 = llvm.load %v2983 : !llvm.ptr -> i32
%v2985 = llvm.load %v2931 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2986 = llvm.getelementptr %v2931[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2987 = llvm.load %v2986 : !llvm.ptr -> i32
%v2988 = arith.constant 1 : i32
%v2989 = arith.constant 1 : i32
%v2990 = func.call @tensor_zeros(%v2984, %v2987, %v2988, %v2989) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2991 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2992 = llvm.extractvalue %v2990[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2993 = llvm.insertvalue %v2992, %v2991[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2994 = llvm.extractvalue %v2990[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2995 = llvm.insertvalue %v2994, %v2993[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2996 = llvm.extractvalue %v2990[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2997 = llvm.insertvalue %v2996, %v2995[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2998 = llvm.extractvalue %v2990[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2999 = llvm.insertvalue %v2998, %v2997[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3000 = llvm.extractvalue %v2990[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3001 = llvm.insertvalue %v3000, %v2999[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3002 = llvm.extractvalue %v2990[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3003 = llvm.insertvalue %v3002, %v3001[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3003, %v2933 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3004 = llvm.load %v2933 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3004, %v2935 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3005 = arith.constant 0 : i32
%v3006 = arith.index_cast %v3005 : i32 to index
%v3007 = arith.index_cast %v2984 : i32 to index
%v3008 = arith.constant 1 : index
%v3009 = arith.constant -1 : index
%v3010 = arith.cmpi sle, %v3006, %v3007 : index
%v3011 = arith.select %v3010, %v3008, %v3009 : index
cf.br ^b118(%v3006 : index)
^b118(%v3012: index):
%v3013 = arith.cmpi slt, %v3012, %v3007 : index
%v3014 = arith.cmpi sgt, %v3012, %v3007 : index
%v3015 = arith.select %v3010, %v3013, %v3014 : i1
cf.cond_br %v3015, ^b119(%v3012 : index), ^b120(%v3012 : index)
^b119(%v3016: index):
%v3017 = arith.constant 0 : i32
%v3018 = arith.index_cast %v3017 : i32 to index
%v3019 = arith.index_cast %v2987 : i32 to index
%v3020 = arith.constant 1 : index
%v3021 = arith.constant -1 : index
%v3022 = arith.cmpi sle, %v3018, %v3019 : index
%v3023 = arith.select %v3022, %v3020, %v3021 : index
cf.br ^b121(%v3018 : index)
^b121(%v3024: index):
%v3025 = arith.cmpi slt, %v3024, %v3019 : index
%v3026 = arith.cmpi sgt, %v3024, %v3019 : index
%v3027 = arith.select %v3022, %v3025, %v3026 : i1
cf.cond_br %v3027, ^b122(%v3024 : index), ^b123(%v3024 : index)
^b122(%v3028: index):
%v3029 = arith.constant 0.0 : f64
%v3030 = arith.truncf %v3029 : f64 to f32
llvm.store %v3030, %v2937 : f32, !llvm.ptr
%v3031 = arith.constant 0 : i32
%v3032 = arith.index_cast %v3031 : i32 to index
%v3033 = arith.index_cast %v2981 : i32 to index
%v3034 = arith.constant 1 : index
%v3035 = arith.constant -1 : index
%v3036 = arith.cmpi sle, %v3032, %v3033 : index
%v3037 = arith.select %v3036, %v3034, %v3035 : index
cf.br ^b124(%v3032 : index)
^b124(%v3038: index):
%v3039 = arith.cmpi slt, %v3038, %v3033 : index
%v3040 = arith.cmpi sgt, %v3038, %v3033 : index
%v3041 = arith.select %v3036, %v3039, %v3040 : i1
cf.cond_br %v3041, ^b125(%v3038 : index), ^b126(%v3038 : index)
^b125(%v3042: index):
%v3043 = llvm.load %v2937 : !llvm.ptr -> f32
%v3044 = llvm.load %v2927 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3045 = llvm.getelementptr %v2927[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3046 = llvm.load %v3045 : !llvm.ptr -> !llvm.ptr
%v3047 = arith.index_cast %v3042 : index to i32
%v3048 = arith.muli %v3047, %v2984 : i32
%v3049 = arith.index_cast %v3016 : index to i32
%v3050 = arith.addi %v3048, %v3049 : i32
%v3051 = arith.extsi %v3050 : i32 to i64
%v3052 = llvm.getelementptr %v3046[%v3051] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3053 = llvm.load %v3052 : !llvm.ptr -> f32
%v3054 = llvm.load %v2931 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3055 = llvm.getelementptr %v2931[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3056 = llvm.load %v3055 : !llvm.ptr -> !llvm.ptr
%v3057 = arith.index_cast %v3042 : index to i32
%v3058 = arith.muli %v3057, %v2987 : i32
%v3059 = arith.index_cast %v3028 : index to i32
%v3060 = arith.addi %v3058, %v3059 : i32
%v3061 = arith.extsi %v3060 : i32 to i64
%v3062 = llvm.getelementptr %v3056[%v3061] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3063 = llvm.load %v3062 : !llvm.ptr -> f32
%v3064 = llvm.intr.fmuladd(%v3053, %v3063, %v3043) : (f32, f32, f32) -> f32
llvm.store %v3064, %v2937 : f32, !llvm.ptr
%v3065 = arith.addi %v3042, %v3037 : index
cf.br ^b124(%v3065 : index)
^b126(%v3066: index):
%v3067 = llvm.load %v2937 : !llvm.ptr -> f32
%v3068 = llvm.load %v2935 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3069 = llvm.getelementptr %v2935[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3070 = llvm.load %v3069 : !llvm.ptr -> !llvm.ptr
%v3071 = arith.index_cast %v3016 : index to i32
%v3072 = arith.muli %v3071, %v2987 : i32
%v3073 = arith.index_cast %v3028 : index to i32
%v3074 = arith.addi %v3072, %v3073 : i32
%v3075 = arith.extsi %v3074 : i32 to i64
%v3076 = llvm.getelementptr %v3070[%v3075] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v3067, %v3076 : f32, !llvm.ptr
%v3077 = arith.addi %v3028, %v3023 : index
cf.br ^b121(%v3077 : index)
^b123(%v3078: index):
%v3079 = arith.addi %v3016, %v3011 : index
cf.br ^b118(%v3079 : index)
^b120(%v3080: index):
%v3081 = llvm.load %v2935 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3082 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3083 = llvm.extractvalue %v3081[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3084 = llvm.insertvalue %v3083, %v3082[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3085 = llvm.extractvalue %v3081[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3086 = llvm.insertvalue %v3085, %v3084[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3087 = llvm.extractvalue %v3081[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3088 = llvm.insertvalue %v3087, %v3086[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3089 = llvm.extractvalue %v3081[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3090 = llvm.insertvalue %v3089, %v3088[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3091 = llvm.extractvalue %v3081[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3092 = llvm.insertvalue %v3091, %v3090[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3093 = llvm.extractvalue %v3081[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3094 = llvm.insertvalue %v3093, %v3092[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3094, %v2939 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3095 = llvm.load %v2939 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v3095 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_transpose(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v3096 = llvm.mlir.constant(1 : i64) : i64
%v3097 = llvm.alloca %v3096 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v3098 = llvm.mlir.constant(1 : i64) : i64
%v3099 = llvm.alloca %v3098 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v3100 = llvm.mlir.constant(1 : i64) : i64
%v3101 = llvm.alloca %v3100 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v3102 = llvm.mlir.constant(1 : i64) : i64
%v3103 = llvm.alloca %v3102 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v3104 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3105 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3106 = llvm.insertvalue %v3105, %v3104[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3107 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3108 = llvm.insertvalue %v3107, %v3106[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3109 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3110 = llvm.insertvalue %v3109, %v3108[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3111 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3112 = llvm.insertvalue %v3111, %v3110[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3113 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3114 = llvm.insertvalue %v3113, %v3112[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3115 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3116 = llvm.insertvalue %v3115, %v3114[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3116, %v3097 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3117 = llvm.load %v3097 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3118 = llvm.getelementptr %v3097[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3119 = llvm.load %v3118 : !llvm.ptr -> i32
%v3120 = llvm.load %v3097 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3121 = llvm.getelementptr %v3097[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3122 = llvm.load %v3121 : !llvm.ptr -> i32
%v3123 = arith.constant 1 : i32
%v3124 = arith.constant 1 : i32
%v3125 = func.call @tensor_zeros(%v3119, %v3122, %v3123, %v3124) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3126 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3127 = llvm.extractvalue %v3125[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3128 = llvm.insertvalue %v3127, %v3126[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3129 = llvm.extractvalue %v3125[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3130 = llvm.insertvalue %v3129, %v3128[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3131 = llvm.extractvalue %v3125[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3132 = llvm.insertvalue %v3131, %v3130[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3133 = llvm.extractvalue %v3125[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3134 = llvm.insertvalue %v3133, %v3132[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3135 = llvm.extractvalue %v3125[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3136 = llvm.insertvalue %v3135, %v3134[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3137 = llvm.extractvalue %v3125[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3138 = llvm.insertvalue %v3137, %v3136[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3138, %v3099 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3139 = llvm.load %v3099 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3139, %v3101 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3140 = arith.constant 0 : i32
%v3141 = llvm.load %v3097 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3142 = llvm.getelementptr %v3097[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3143 = llvm.load %v3142 : !llvm.ptr -> i32
%v3144 = arith.index_cast %v3140 : i32 to index
%v3145 = arith.index_cast %v3143 : i32 to index
%v3146 = arith.constant 1 : index
%v3147 = arith.constant -1 : index
%v3148 = arith.cmpi sle, %v3144, %v3145 : index
%v3149 = arith.select %v3148, %v3146, %v3147 : index
cf.br ^b127(%v3144 : index)
^b127(%v3150: index):
%v3151 = arith.cmpi slt, %v3150, %v3145 : index
%v3152 = arith.cmpi sgt, %v3150, %v3145 : index
%v3153 = arith.select %v3148, %v3151, %v3152 : i1
cf.cond_br %v3153, ^b128(%v3150 : index), ^b129(%v3150 : index)
^b128(%v3154: index):
%v3155 = arith.constant 0 : i32
%v3156 = llvm.load %v3097 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3157 = llvm.getelementptr %v3097[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3158 = llvm.load %v3157 : !llvm.ptr -> i32
%v3159 = arith.index_cast %v3155 : i32 to index
%v3160 = arith.index_cast %v3158 : i32 to index
%v3161 = arith.constant 1 : index
%v3162 = arith.constant -1 : index
%v3163 = arith.cmpi sle, %v3159, %v3160 : index
%v3164 = arith.select %v3163, %v3161, %v3162 : index
cf.br ^b130(%v3159 : index)
^b130(%v3165: index):
%v3166 = arith.cmpi slt, %v3165, %v3160 : index
%v3167 = arith.cmpi sgt, %v3165, %v3160 : index
%v3168 = arith.select %v3163, %v3166, %v3167 : i1
cf.cond_br %v3168, ^b131(%v3165 : index), ^b132(%v3165 : index)
^b131(%v3169: index):
%v3170 = llvm.load %v3097 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3171 = llvm.getelementptr %v3097[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3172 = llvm.load %v3171 : !llvm.ptr -> !llvm.ptr
%v3173 = llvm.load %v3097 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3174 = llvm.getelementptr %v3097[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3175 = llvm.load %v3174 : !llvm.ptr -> i32
%v3176 = arith.index_cast %v3154 : index to i32
%v3177 = arith.muli %v3176, %v3175 : i32
%v3178 = arith.index_cast %v3169 : index to i32
%v3179 = arith.addi %v3177, %v3178 : i32
%v3180 = arith.extsi %v3179 : i32 to i64
%v3181 = llvm.getelementptr %v3172[%v3180] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3182 = llvm.load %v3181 : !llvm.ptr -> f32
%v3183 = llvm.load %v3101 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3184 = llvm.getelementptr %v3101[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3185 = llvm.load %v3184 : !llvm.ptr -> !llvm.ptr
%v3186 = llvm.load %v3097 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3187 = llvm.getelementptr %v3097[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3188 = llvm.load %v3187 : !llvm.ptr -> i32
%v3189 = arith.index_cast %v3169 : index to i32
%v3190 = arith.muli %v3189, %v3188 : i32
%v3191 = arith.index_cast %v3154 : index to i32
%v3192 = arith.addi %v3190, %v3191 : i32
%v3193 = arith.extsi %v3192 : i32 to i64
%v3194 = llvm.getelementptr %v3185[%v3193] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v3182, %v3194 : f32, !llvm.ptr
%v3195 = arith.addi %v3169, %v3164 : index
cf.br ^b130(%v3195 : index)
^b132(%v3196: index):
%v3197 = arith.addi %v3154, %v3149 : index
cf.br ^b127(%v3197 : index)
^b129(%v3198: index):
%v3199 = llvm.load %v3101 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3200 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3201 = llvm.extractvalue %v3199[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3202 = llvm.insertvalue %v3201, %v3200[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3203 = llvm.extractvalue %v3199[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3204 = llvm.insertvalue %v3203, %v3202[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3205 = llvm.extractvalue %v3199[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3206 = llvm.insertvalue %v3205, %v3204[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3207 = llvm.extractvalue %v3199[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3208 = llvm.insertvalue %v3207, %v3206[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3209 = llvm.extractvalue %v3199[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3210 = llvm.insertvalue %v3209, %v3208[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3211 = llvm.extractvalue %v3199[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3212 = llvm.insertvalue %v3211, %v3210[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3212, %v3103 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3213 = llvm.load %v3103 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v3213 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_sum(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> f32 {
%v3214 = llvm.mlir.constant(1 : i64) : i64
%v3215 = llvm.alloca %v3214 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v3216 = llvm.mlir.constant(1 : i64) : i64
%v3217 = llvm.alloca %v3216 x f32 : (i64) -> !llvm.ptr
%v3218 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3219 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3220 = llvm.insertvalue %v3219, %v3218[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3221 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3222 = llvm.insertvalue %v3221, %v3220[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3223 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3224 = llvm.insertvalue %v3223, %v3222[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3225 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3226 = llvm.insertvalue %v3225, %v3224[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3227 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3228 = llvm.insertvalue %v3227, %v3226[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3229 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3230 = llvm.insertvalue %v3229, %v3228[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3230, %v3215 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3231 = arith.constant 0.0 : f64
%v3232 = arith.truncf %v3231 : f64 to f32
llvm.store %v3232, %v3217 : f32, !llvm.ptr
%v3233 = arith.constant 0 : i32
%v3234 = llvm.load %v3215 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3235 = llvm.getelementptr %v3215[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
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
%v3248 = llvm.load %v3217 : !llvm.ptr -> f32
%v3249 = llvm.load %v3215 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3250 = llvm.getelementptr %v3215[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3251 = llvm.load %v3250 : !llvm.ptr -> !llvm.ptr
%v3252 = arith.index_cast %v3247 : index to i64
%v3253 = llvm.getelementptr %v3251[%v3252] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3254 = llvm.load %v3253 : !llvm.ptr -> f32
%v3255 = arith.addf %v3248, %v3254 : f32
llvm.store %v3255, %v3217 : f32, !llvm.ptr
%v3256 = arith.addi %v3247, %v3242 : index
cf.br ^b133(%v3256 : index)
^b135(%v3257: index):
%v3258 = llvm.load %v3217 : !llvm.ptr -> f32
func.return %v3258 : f32
}
func.func @tensor_mean(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> f32 {
%v3259 = llvm.mlir.constant(1 : i64) : i64
%v3260 = llvm.alloca %v3259 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v3261 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3262 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3263 = llvm.insertvalue %v3262, %v3261[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3264 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3265 = llvm.insertvalue %v3264, %v3263[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3266 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3267 = llvm.insertvalue %v3266, %v3265[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3268 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3269 = llvm.insertvalue %v3268, %v3267[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3270 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3271 = llvm.insertvalue %v3270, %v3269[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3272 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3273 = llvm.insertvalue %v3272, %v3271[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3273, %v3260 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3274 = llvm.load %v3260 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3275 = func.call @tensor_sum(%v3274) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> f32
%v3276 = llvm.load %v3260 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3277 = llvm.getelementptr %v3260[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3278 = llvm.load %v3277 : !llvm.ptr -> i32
%v3279 = arith.sitofp %v3278 : i32 to f32
%v3280 = arith.divf %v3275, %v3279 : f32
func.return %v3280 : f32
}
func.func @tensor_max(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> f32 {
%v3281 = llvm.mlir.constant(1 : i64) : i64
%v3282 = llvm.alloca %v3281 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v3283 = llvm.mlir.constant(1 : i64) : i64
%v3284 = llvm.alloca %v3283 x f32 : (i64) -> !llvm.ptr
%v3285 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3286 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3287 = llvm.insertvalue %v3286, %v3285[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3288 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3289 = llvm.insertvalue %v3288, %v3287[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3290 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3291 = llvm.insertvalue %v3290, %v3289[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3292 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3293 = llvm.insertvalue %v3292, %v3291[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3294 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3295 = llvm.insertvalue %v3294, %v3293[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3296 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3297 = llvm.insertvalue %v3296, %v3295[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3297, %v3282 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3298 = llvm.load %v3282 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3299 = llvm.getelementptr %v3282[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3300 = llvm.load %v3299 : !llvm.ptr -> !llvm.ptr
%v3301 = arith.constant 0 : i32
%v3302 = arith.extsi %v3301 : i32 to i64
%v3303 = llvm.getelementptr %v3300[%v3302] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3304 = llvm.load %v3303 : !llvm.ptr -> f32
llvm.store %v3304, %v3284 : f32, !llvm.ptr
%v3305 = arith.constant 1 : i32
%v3306 = llvm.load %v3282 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3307 = llvm.getelementptr %v3282[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
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
%v3320 = llvm.load %v3282 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3321 = llvm.getelementptr %v3282[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3322 = llvm.load %v3321 : !llvm.ptr -> !llvm.ptr
%v3323 = arith.index_cast %v3319 : index to i64
%v3324 = llvm.getelementptr %v3322[%v3323] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3325 = llvm.load %v3324 : !llvm.ptr -> f32
%v3326 = llvm.load %v3284 : !llvm.ptr -> f32
%v3327 = arith.cmpf ogt, %v3325, %v3326 : f32
cf.cond_br %v3327, ^b139, ^b140
^b139:
%v3328 = llvm.load %v3282 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3329 = llvm.getelementptr %v3282[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3330 = llvm.load %v3329 : !llvm.ptr -> !llvm.ptr
%v3331 = arith.index_cast %v3319 : index to i64
%v3332 = llvm.getelementptr %v3330[%v3331] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3333 = llvm.load %v3332 : !llvm.ptr -> f32
llvm.store %v3333, %v3284 : f32, !llvm.ptr
cf.br ^b141
^b140:
cf.br ^b141
^b141:
%v3334 = arith.addi %v3319, %v3314 : index
cf.br ^b136(%v3334 : index)
^b138(%v3335: index):
%v3336 = llvm.load %v3284 : !llvm.ptr -> f32
func.return %v3336 : f32
}
func.func @tensor_min(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> f32 {
%v3337 = llvm.mlir.constant(1 : i64) : i64
%v3338 = llvm.alloca %v3337 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v3339 = llvm.mlir.constant(1 : i64) : i64
%v3340 = llvm.alloca %v3339 x f32 : (i64) -> !llvm.ptr
%v3341 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3342 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3343 = llvm.insertvalue %v3342, %v3341[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3344 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3345 = llvm.insertvalue %v3344, %v3343[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3346 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3347 = llvm.insertvalue %v3346, %v3345[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3348 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3349 = llvm.insertvalue %v3348, %v3347[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3350 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3351 = llvm.insertvalue %v3350, %v3349[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3352 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3353 = llvm.insertvalue %v3352, %v3351[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3353, %v3338 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3354 = llvm.load %v3338 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3355 = llvm.getelementptr %v3338[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3356 = llvm.load %v3355 : !llvm.ptr -> !llvm.ptr
%v3357 = arith.constant 0 : i32
%v3358 = arith.extsi %v3357 : i32 to i64
%v3359 = llvm.getelementptr %v3356[%v3358] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3360 = llvm.load %v3359 : !llvm.ptr -> f32
llvm.store %v3360, %v3340 : f32, !llvm.ptr
%v3361 = arith.constant 1 : i32
%v3362 = llvm.load %v3338 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3363 = llvm.getelementptr %v3338[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
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
%v3376 = llvm.load %v3338 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3377 = llvm.getelementptr %v3338[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3378 = llvm.load %v3377 : !llvm.ptr -> !llvm.ptr
%v3379 = arith.index_cast %v3375 : index to i64
%v3380 = llvm.getelementptr %v3378[%v3379] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3381 = llvm.load %v3380 : !llvm.ptr -> f32
%v3382 = llvm.load %v3340 : !llvm.ptr -> f32
%v3383 = arith.cmpf olt, %v3381, %v3382 : f32
cf.cond_br %v3383, ^b145, ^b146
^b145:
%v3384 = llvm.load %v3338 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3385 = llvm.getelementptr %v3338[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3386 = llvm.load %v3385 : !llvm.ptr -> !llvm.ptr
%v3387 = arith.index_cast %v3375 : index to i64
%v3388 = llvm.getelementptr %v3386[%v3387] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3389 = llvm.load %v3388 : !llvm.ptr -> f32
llvm.store %v3389, %v3340 : f32, !llvm.ptr
cf.br ^b147
^b146:
cf.br ^b147
^b147:
%v3390 = arith.addi %v3375, %v3370 : index
cf.br ^b142(%v3390 : index)
^b144(%v3391: index):
%v3392 = llvm.load %v3340 : !llvm.ptr -> f32
func.return %v3392 : f32
}
func.func @tensor_argmax(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> i32 {
%v3393 = llvm.mlir.constant(1 : i64) : i64
%v3394 = llvm.alloca %v3393 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v3395 = llvm.mlir.constant(1 : i64) : i64
%v3396 = llvm.alloca %v3395 x i32 : (i64) -> !llvm.ptr
%v3397 = llvm.mlir.constant(1 : i64) : i64
%v3398 = llvm.alloca %v3397 x f32 : (i64) -> !llvm.ptr
%v3399 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3400 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3401 = llvm.insertvalue %v3400, %v3399[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3402 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3403 = llvm.insertvalue %v3402, %v3401[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3404 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3405 = llvm.insertvalue %v3404, %v3403[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3406 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3407 = llvm.insertvalue %v3406, %v3405[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3408 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3409 = llvm.insertvalue %v3408, %v3407[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3410 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3411 = llvm.insertvalue %v3410, %v3409[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3411, %v3394 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3412 = arith.constant 0 : i32
llvm.store %v3412, %v3396 : i32, !llvm.ptr
%v3413 = llvm.load %v3394 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3414 = llvm.getelementptr %v3394[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3415 = llvm.load %v3414 : !llvm.ptr -> !llvm.ptr
%v3416 = arith.constant 0 : i32
%v3417 = arith.extsi %v3416 : i32 to i64
%v3418 = llvm.getelementptr %v3415[%v3417] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3419 = llvm.load %v3418 : !llvm.ptr -> f32
llvm.store %v3419, %v3398 : f32, !llvm.ptr
%v3420 = arith.constant 1 : i32
%v3421 = llvm.load %v3394 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3422 = llvm.getelementptr %v3394[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
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
%v3435 = llvm.load %v3394 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3436 = llvm.getelementptr %v3394[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3437 = llvm.load %v3436 : !llvm.ptr -> !llvm.ptr
%v3438 = arith.index_cast %v3434 : index to i64
%v3439 = llvm.getelementptr %v3437[%v3438] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3440 = llvm.load %v3439 : !llvm.ptr -> f32
%v3441 = llvm.load %v3398 : !llvm.ptr -> f32
%v3442 = arith.cmpf ogt, %v3440, %v3441 : f32
cf.cond_br %v3442, ^b151, ^b152
^b151:
%v3443 = llvm.load %v3394 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3444 = llvm.getelementptr %v3394[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3445 = llvm.load %v3444 : !llvm.ptr -> !llvm.ptr
%v3446 = arith.index_cast %v3434 : index to i64
%v3447 = llvm.getelementptr %v3445[%v3446] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3448 = llvm.load %v3447 : !llvm.ptr -> f32
llvm.store %v3448, %v3398 : f32, !llvm.ptr
%v3449 = arith.index_cast %v3434 : index to i32
llvm.store %v3449, %v3396 : i32, !llvm.ptr
cf.br ^b153
^b152:
cf.br ^b153
^b153:
%v3450 = arith.addi %v3434, %v3429 : index
cf.br ^b148(%v3450 : index)
^b150(%v3451: index):
%v3452 = llvm.load %v3396 : !llvm.ptr -> i32
func.return %v3452 : i32
}
func.func @tensor_copy(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v3453 = llvm.mlir.constant(1 : i64) : i64
%v3454 = llvm.alloca %v3453 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v3455 = llvm.mlir.constant(1 : i64) : i64
%v3456 = llvm.alloca %v3455 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v3457 = llvm.mlir.constant(1 : i64) : i64
%v3458 = llvm.alloca %v3457 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v3459 = llvm.mlir.constant(1 : i64) : i64
%v3460 = llvm.alloca %v3459 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v3461 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3462 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3463 = llvm.insertvalue %v3462, %v3461[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3464 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3465 = llvm.insertvalue %v3464, %v3463[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3466 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3467 = llvm.insertvalue %v3466, %v3465[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3468 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3469 = llvm.insertvalue %v3468, %v3467[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3470 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3471 = llvm.insertvalue %v3470, %v3469[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3472 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3473 = llvm.insertvalue %v3472, %v3471[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3473, %v3454 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3474 = llvm.load %v3454 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3475 = llvm.getelementptr %v3454[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3476 = llvm.load %v3475 : !llvm.ptr -> i32
%v3477 = llvm.load %v3454 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3478 = llvm.getelementptr %v3454[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3479 = llvm.load %v3478 : !llvm.ptr -> i32
%v3480 = llvm.load %v3454 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3481 = llvm.getelementptr %v3454[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3482 = llvm.load %v3481 : !llvm.ptr -> i32
%v3483 = llvm.load %v3454 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3484 = llvm.getelementptr %v3454[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3485 = llvm.load %v3484 : !llvm.ptr -> i32
%v3486 = func.call @tensor_zeros(%v3476, %v3479, %v3482, %v3485) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3487 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3488 = llvm.extractvalue %v3486[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3489 = llvm.insertvalue %v3488, %v3487[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3490 = llvm.extractvalue %v3486[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3491 = llvm.insertvalue %v3490, %v3489[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3492 = llvm.extractvalue %v3486[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3493 = llvm.insertvalue %v3492, %v3491[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3494 = llvm.extractvalue %v3486[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3495 = llvm.insertvalue %v3494, %v3493[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3496 = llvm.extractvalue %v3486[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3497 = llvm.insertvalue %v3496, %v3495[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3498 = llvm.extractvalue %v3486[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3499 = llvm.insertvalue %v3498, %v3497[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3499, %v3456 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3500 = llvm.load %v3456 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3500, %v3458 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3501 = arith.constant 0 : i32
%v3502 = llvm.load %v3454 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3503 = llvm.getelementptr %v3454[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3504 = llvm.load %v3503 : !llvm.ptr -> i32
%v3505 = arith.index_cast %v3501 : i32 to index
%v3506 = arith.index_cast %v3504 : i32 to index
%v3507 = arith.constant 1 : index
%v3508 = arith.constant -1 : index
%v3509 = arith.cmpi sle, %v3505, %v3506 : index
%v3510 = arith.select %v3509, %v3507, %v3508 : index
cf.br ^b154(%v3505 : index)
^b154(%v3511: index):
%v3512 = arith.cmpi slt, %v3511, %v3506 : index
%v3513 = arith.cmpi sgt, %v3511, %v3506 : index
%v3514 = arith.select %v3509, %v3512, %v3513 : i1
cf.cond_br %v3514, ^b155(%v3511 : index), ^b156(%v3511 : index)
^b155(%v3515: index):
%v3516 = llvm.load %v3454 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3517 = llvm.getelementptr %v3454[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3518 = llvm.load %v3517 : !llvm.ptr -> !llvm.ptr
%v3519 = arith.index_cast %v3515 : index to i64
%v3520 = llvm.getelementptr %v3518[%v3519] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3521 = llvm.load %v3520 : !llvm.ptr -> f32
%v3522 = llvm.load %v3458 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3523 = llvm.getelementptr %v3458[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3524 = llvm.load %v3523 : !llvm.ptr -> !llvm.ptr
%v3525 = arith.index_cast %v3515 : index to i64
%v3526 = llvm.getelementptr %v3524[%v3525] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v3521, %v3526 : f32, !llvm.ptr
%v3527 = arith.addi %v3515, %v3510 : index
cf.br ^b154(%v3527 : index)
^b156(%v3528: index):
%v3529 = llvm.load %v3458 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3530 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3531 = llvm.extractvalue %v3529[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3532 = llvm.insertvalue %v3531, %v3530[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3533 = llvm.extractvalue %v3529[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3534 = llvm.insertvalue %v3533, %v3532[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3535 = llvm.extractvalue %v3529[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3536 = llvm.insertvalue %v3535, %v3534[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3537 = llvm.extractvalue %v3529[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3538 = llvm.insertvalue %v3537, %v3536[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3539 = llvm.extractvalue %v3529[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3540 = llvm.insertvalue %v3539, %v3538[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3541 = llvm.extractvalue %v3529[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3542 = llvm.insertvalue %v3541, %v3540[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3542, %v3460 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3543 = llvm.load %v3460 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v3543 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_print(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> () {
%v3544 = llvm.mlir.constant(1 : i64) : i64
%v3545 = llvm.alloca %v3544 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v3546 = llvm.mlir.constant(1 : i64) : i64
%v3547 = llvm.alloca %v3546 x i32 : (i64) -> !llvm.ptr
%v3548 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3549 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3550 = llvm.insertvalue %v3549, %v3548[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3551 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3552 = llvm.insertvalue %v3551, %v3550[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3553 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3554 = llvm.insertvalue %v3553, %v3552[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3555 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3556 = llvm.insertvalue %v3555, %v3554[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3557 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3558 = llvm.insertvalue %v3557, %v3556[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3559 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3560 = llvm.insertvalue %v3559, %v3558[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3560, %v3545 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3561 = llvm.mlir.addressof @str_15 : !llvm.ptr
%v3562 = llvm.call @printf(%v3561) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3563 = arith.constant 0 : i32
%v3564 = llvm.load %v3545 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3565 = llvm.getelementptr %v3545[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3566 = llvm.load %v3565 : !llvm.ptr -> i32
%v3567 = llvm.mlir.addressof @str_16 : !llvm.ptr
%v3568 = llvm.call @printf(%v3567, %v3566) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v3569 = arith.constant 0 : i32
%v3570 = llvm.mlir.addressof @str_17 : !llvm.ptr
%v3571 = llvm.call @printf(%v3570) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3572 = arith.constant 0 : i32
%v3573 = llvm.load %v3545 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3574 = llvm.getelementptr %v3545[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3575 = llvm.load %v3574 : !llvm.ptr -> i32
%v3576 = llvm.mlir.addressof @str_16 : !llvm.ptr
%v3577 = llvm.call @printf(%v3576, %v3575) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v3578 = arith.constant 0 : i32
%v3579 = llvm.mlir.addressof @str_17 : !llvm.ptr
%v3580 = llvm.call @printf(%v3579) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3581 = arith.constant 0 : i32
%v3582 = llvm.load %v3545 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3583 = llvm.getelementptr %v3545[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3584 = llvm.load %v3583 : !llvm.ptr -> i32
%v3585 = llvm.mlir.addressof @str_16 : !llvm.ptr
%v3586 = llvm.call @printf(%v3585, %v3584) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v3587 = arith.constant 0 : i32
%v3588 = llvm.mlir.addressof @str_17 : !llvm.ptr
%v3589 = llvm.call @printf(%v3588) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3590 = arith.constant 0 : i32
%v3591 = llvm.load %v3545 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3592 = llvm.getelementptr %v3545[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3593 = llvm.load %v3592 : !llvm.ptr -> i32
%v3594 = llvm.mlir.addressof @str_16 : !llvm.ptr
%v3595 = llvm.call @printf(%v3594, %v3593) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v3596 = arith.constant 0 : i32
%v3597 = llvm.mlir.addressof @str_18 : !llvm.ptr
%v3598 = llvm.call @printf(%v3597) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3599 = arith.constant 0 : i32
%v3600 = llvm.load %v3545 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3601 = llvm.getelementptr %v3545[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3602 = llvm.load %v3601 : !llvm.ptr -> i32
llvm.store %v3602, %v3547 : i32, !llvm.ptr
%v3603 = llvm.load %v3547 : !llvm.ptr -> i32
%v3604 = arith.constant 10 : i32
%v3605 = arith.cmpi sgt, %v3603, %v3604 : i32
cf.cond_br %v3605, ^b157, ^b158
^b157:
%v3606 = arith.constant 10 : i32
llvm.store %v3606, %v3547 : i32, !llvm.ptr
cf.br ^b159
^b158:
cf.br ^b159
^b159:
%v3607 = llvm.mlir.addressof @str_19 : !llvm.ptr
%v3608 = llvm.call @printf(%v3607) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3609 = arith.constant 0 : i32
%v3610 = arith.constant 0 : i32
%v3611 = llvm.load %v3547 : !llvm.ptr -> i32
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
%v3623 = llvm.load %v3545 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3624 = llvm.getelementptr %v3545[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3625 = llvm.load %v3624 : !llvm.ptr -> !llvm.ptr
%v3626 = arith.index_cast %v3622 : index to i64
%v3627 = llvm.getelementptr %v3625[%v3626] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3628 = llvm.load %v3627 : !llvm.ptr -> f32
%v3629 = arith.extf %v3628 : f32 to f64
%v3630 = llvm.mlir.addressof @str_20 : !llvm.ptr
%v3631 = llvm.call @printf(%v3630, %v3629) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v3632 = arith.constant 0 : i32
%v3633 = llvm.load %v3547 : !llvm.ptr -> i32
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
%v3643 = llvm.load %v3545 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3644 = llvm.getelementptr %v3545[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
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
%v3654 = llvm.mlir.constant(1 : i64) : i64
%v3655 = llvm.alloca %v3654 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v3656 = llvm.mlir.constant(1 : i64) : i64
%v3657 = llvm.alloca %v3656 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v3658 = llvm.mlir.constant(1 : i64) : i64
%v3659 = llvm.alloca %v3658 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v3660 = llvm.mlir.constant(1 : i64) : i64
%v3661 = llvm.alloca %v3660 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v3662 = llvm.mlir.constant(1 : i64) : i64
%v3663 = llvm.alloca %v3662 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v3664 = llvm.mlir.constant(1 : i64) : i64
%v3665 = llvm.alloca %v3664 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
%v3666 = arith.constant 1 : i32
%v3667 = arith.constant 1 : i32
%v3668 = arith.constant 42 : i32
%v3669 = func.call @tensor_rand(%arg0, %arg1, %v3666, %v3667, %v3668) : (i32, i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3670 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3671 = llvm.extractvalue %v3669[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3672 = llvm.insertvalue %v3671, %v3670[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3673 = llvm.extractvalue %v3669[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3674 = llvm.insertvalue %v3673, %v3672[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3675 = llvm.extractvalue %v3669[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3676 = llvm.insertvalue %v3675, %v3674[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3677 = llvm.extractvalue %v3669[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3678 = llvm.insertvalue %v3677, %v3676[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3679 = llvm.extractvalue %v3669[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3680 = llvm.insertvalue %v3679, %v3678[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3681 = llvm.extractvalue %v3669[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3682 = llvm.insertvalue %v3681, %v3680[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3682, %v3655 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3683 = llvm.load %v3655 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3683, %v3657 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3684 = arith.constant 1 : i32
%v3685 = arith.constant 1 : i32
%v3686 = arith.constant 99 : i32
%v3687 = func.call @tensor_rand(%arg1, %arg2, %v3684, %v3685, %v3686) : (i32, i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3688 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3689 = llvm.extractvalue %v3687[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3690 = llvm.insertvalue %v3689, %v3688[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3691 = llvm.extractvalue %v3687[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3692 = llvm.insertvalue %v3691, %v3690[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3693 = llvm.extractvalue %v3687[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3694 = llvm.insertvalue %v3693, %v3692[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3695 = llvm.extractvalue %v3687[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3696 = llvm.insertvalue %v3695, %v3694[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3697 = llvm.extractvalue %v3687[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3698 = llvm.insertvalue %v3697, %v3696[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3699 = llvm.extractvalue %v3687[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3700 = llvm.insertvalue %v3699, %v3698[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3700, %v3659 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3701 = llvm.load %v3659 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3701, %v3661 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3702 = llvm.load %v3657 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3703 = llvm.load %v3661 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3704 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3705 = llvm.extractvalue %v3703[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3706 = llvm.insertvalue %v3705, %v3704[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3707 = llvm.extractvalue %v3703[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3708 = llvm.insertvalue %v3707, %v3706[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3709 = llvm.extractvalue %v3703[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3710 = llvm.insertvalue %v3709, %v3708[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3711 = llvm.extractvalue %v3703[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3712 = llvm.insertvalue %v3711, %v3710[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3713 = llvm.extractvalue %v3703[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3714 = llvm.insertvalue %v3713, %v3712[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3715 = llvm.extractvalue %v3703[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3716 = llvm.insertvalue %v3715, %v3714[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3717 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3718 = llvm.extractvalue %v3702[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3719 = llvm.insertvalue %v3718, %v3717[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3720 = llvm.extractvalue %v3702[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3721 = llvm.insertvalue %v3720, %v3719[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3722 = llvm.extractvalue %v3702[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3723 = llvm.insertvalue %v3722, %v3721[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3724 = llvm.extractvalue %v3702[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3725 = llvm.insertvalue %v3724, %v3723[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3726 = llvm.extractvalue %v3702[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3727 = llvm.insertvalue %v3726, %v3725[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3728 = llvm.extractvalue %v3702[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3729 = llvm.insertvalue %v3728, %v3727[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3730 = func.call @tensor_matmul(%v3729, %v3716) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3731 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3732 = llvm.extractvalue %v3730[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3733 = llvm.insertvalue %v3732, %v3731[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3734 = llvm.extractvalue %v3730[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3735 = llvm.insertvalue %v3734, %v3733[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3736 = llvm.extractvalue %v3730[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3737 = llvm.insertvalue %v3736, %v3735[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3738 = llvm.extractvalue %v3730[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3739 = llvm.insertvalue %v3738, %v3737[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3739, %v3663 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3740 = llvm.load %v3663 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3741 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3742 = llvm.extractvalue %v3729[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3743 = llvm.insertvalue %v3742, %v3741[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3744 = llvm.extractvalue %v3729[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3745 = llvm.insertvalue %v3744, %v3743[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3746 = llvm.extractvalue %v3729[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3747 = llvm.insertvalue %v3746, %v3745[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3748 = llvm.extractvalue %v3729[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3749 = llvm.insertvalue %v3748, %v3747[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3750 = llvm.extractvalue %v3729[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3751 = llvm.insertvalue %v3750, %v3749[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3752 = llvm.extractvalue %v3729[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3753 = llvm.insertvalue %v3752, %v3751[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3753, %v3657 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3754 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3755 = llvm.extractvalue %v3716[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3756 = llvm.insertvalue %v3755, %v3754[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3757 = llvm.extractvalue %v3716[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3758 = llvm.insertvalue %v3757, %v3756[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3759 = llvm.extractvalue %v3716[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3760 = llvm.insertvalue %v3759, %v3758[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3761 = llvm.extractvalue %v3716[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3762 = llvm.insertvalue %v3761, %v3760[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3763 = llvm.extractvalue %v3716[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3764 = llvm.insertvalue %v3763, %v3762[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3765 = llvm.extractvalue %v3716[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3766 = llvm.insertvalue %v3765, %v3764[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3766, %v3661 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
llvm.store %v3740, %v3665 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3767 = llvm.load %v3665 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3768 = func.call @tensor_sum(%v3767) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> f32
%v3769 = llvm.load %v3657 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.call @tensor_free(%v3769) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> ()
%v3770 = llvm.load %v3661 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.call @tensor_free(%v3770) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> ()
%v3771 = llvm.load %v3665 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
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
