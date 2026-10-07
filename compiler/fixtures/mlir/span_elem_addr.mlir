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
llvm.mlir.global internal constant @str_12("%.1f %.1f\0A\00") {addr_space = 0 : i32} : !llvm.array<11 x i8>
func.func @put(%arg0: !llvm.ptr, %arg1: f64) -> () {
%v1 = arith.constant 0 : i32
%v2 = arith.extsi %v1 : i32 to i64
%v3 = llvm.getelementptr %arg0[%v2] : (!llvm.ptr, i64) -> !llvm.ptr, f64
llvm.store %arg1, %v3 : f64, !llvm.ptr
func.return
}
func.func @via_index(%arg0: !llvm.struct<(!llvm.ptr, i64)>, %arg1: i32) -> () {
%v4 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v5 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i64)>
%v6 = llvm.insertvalue %v5, %v4[0] : !llvm.struct<(!llvm.ptr, i64)>
%v7 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i64)>
%v8 = llvm.insertvalue %v7, %v6[1] : !llvm.struct<(!llvm.ptr, i64)>
%v9 = llvm.mlir.constant(1 : i64) : i64
%v10 = llvm.alloca %v9 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v8, %v10 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v11 = arith.constant 0 : i32
%v12 = arith.index_cast %v11 : i32 to index
%v13 = arith.index_cast %arg1 : i32 to index
%v14 = arith.constant 1 : index
%v15 = arith.constant -1 : index
%v16 = arith.cmpi sle, %v12, %v13 : index
%v17 = arith.select %v16, %v14, %v15 : index
cf.br ^b1(%v12 : index)
^b1(%v18: index):
%v19 = arith.cmpi slt, %v18, %v13 : index
%v20 = arith.cmpi sgt, %v18, %v13 : index
%v21 = arith.select %v16, %v19, %v20 : i1
cf.cond_br %v21, ^b2(%v18 : index), ^b3(%v18 : index)
^b2(%v22: index):
%v23 = llvm.load %v10 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v24 = llvm.extractvalue %v23[0] : !llvm.struct<(!llvm.ptr, i64)>
%v25 = arith.index_cast %v22 : index to i64
%v26 = llvm.getelementptr %v24[%v25] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v27 = arith.index_cast %v22 : index to i64
%v28 = arith.sitofp %v27 : i64 to f64
%v29 = arith.constant 0.5 : f64
%v30 = arith.addf %v28, %v29 : f64
func.call @put(%v26, %v30) : (!llvm.ptr, f64) -> ()
%v31 = arith.addi %v22, %v17 : index
cf.br ^b1(%v31 : index)
^b3(%v32: index):
func.return
}
func.func @via_data(%arg0: !llvm.struct<(!llvm.ptr, i64)>, %arg1: i32) -> () {
%v33 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v34 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i64)>
%v35 = llvm.insertvalue %v34, %v33[0] : !llvm.struct<(!llvm.ptr, i64)>
%v36 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i64)>
%v37 = llvm.insertvalue %v36, %v35[1] : !llvm.struct<(!llvm.ptr, i64)>
%v38 = llvm.mlir.constant(1 : i64) : i64
%v39 = llvm.alloca %v38 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v37, %v39 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v40 = arith.constant 0 : i32
%v41 = arith.index_cast %v40 : i32 to index
%v42 = arith.index_cast %arg1 : i32 to index
%v43 = arith.constant 1 : index
%v44 = arith.constant -1 : index
%v45 = arith.cmpi sle, %v41, %v42 : index
%v46 = arith.select %v45, %v43, %v44 : index
cf.br ^b4(%v41 : index)
^b4(%v47: index):
%v48 = arith.cmpi slt, %v47, %v42 : index
%v49 = arith.cmpi sgt, %v47, %v42 : index
%v50 = arith.select %v45, %v48, %v49 : i1
cf.cond_br %v50, ^b5(%v47 : index), ^b6(%v47 : index)
^b5(%v51: index):
%v52 = llvm.load %v39 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v53 = llvm.extractvalue %v52[0] : !llvm.struct<(!llvm.ptr, i64)>
%v54 = arith.index_cast %v51 : index to i64
%v55 = llvm.getelementptr %v53[%v54] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v56 = arith.index_cast %v51 : index to i64
%v57 = arith.sitofp %v56 : i64 to f64
%v58 = arith.constant 2.0 : f64
%v59 = arith.mulf %v57, %v58 : f64
func.call @put(%v55, %v59) : (!llvm.ptr, f64) -> ()
%v60 = arith.addi %v51, %v46 : index
cf.br ^b4(%v60 : index)
^b6(%v61: index):
func.return
}
func.func @main() -> i32 {
%v62 = arith.constant 32 : i32
%v63 = arith.extsi %v62 : i32 to i64
%v64 = func.call @flow_mem_malloc(%v63) : (i64) -> !llvm.ptr
%v65 = arith.constant 0 : i32
%v66 = arith.constant 4 : i32
%v67 = arith.extsi %v65 : i32 to i64
%v68 = arith.extsi %v66 : i32 to i64
%v69 = llvm.getelementptr %v64[%v67] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v70 = arith.subi %v68, %v67 : i64
%v71 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v72 = llvm.insertvalue %v69, %v71[0] : !llvm.struct<(!llvm.ptr, i64)>
%v73 = llvm.insertvalue %v70, %v72[1] : !llvm.struct<(!llvm.ptr, i64)>
%v74 = llvm.mlir.constant(1 : i64) : i64
%v75 = llvm.alloca %v74 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v73, %v75 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v76 = llvm.load %v75 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v77 = arith.constant 4 : i32
func.call @via_index(%v76, %v77) : (!llvm.struct<(!llvm.ptr, i64)>, i32) -> ()
%v78 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v79 = llvm.load %v75 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v80 = arith.constant 0 : i32
%v81 = llvm.extractvalue %v79[0] : !llvm.struct<(!llvm.ptr, i64)>
%v82 = arith.extsi %v80 : i32 to i64
%v83 = llvm.getelementptr %v81[%v82] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v84 = llvm.load %v83 : !llvm.ptr -> f64
%v85 = llvm.load %v75 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v86 = arith.constant 3 : i32
%v87 = llvm.extractvalue %v85[0] : !llvm.struct<(!llvm.ptr, i64)>
%v88 = arith.extsi %v86 : i32 to i64
%v89 = llvm.getelementptr %v87[%v88] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v90 = llvm.load %v89 : !llvm.ptr -> f64
%v91 = llvm.call @printf(%v78, %v84, %v90) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v92 = llvm.load %v75 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v93 = arith.constant 4 : i32
func.call @via_data(%v92, %v93) : (!llvm.struct<(!llvm.ptr, i64)>, i32) -> ()
%v94 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v95 = llvm.load %v75 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v96 = arith.constant 1 : i32
%v97 = llvm.extractvalue %v95[0] : !llvm.struct<(!llvm.ptr, i64)>
%v98 = arith.extsi %v96 : i32 to i64
%v99 = llvm.getelementptr %v97[%v98] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v100 = llvm.load %v99 : !llvm.ptr -> f64
%v101 = llvm.load %v75 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v102 = arith.constant 3 : i32
%v103 = llvm.extractvalue %v101[0] : !llvm.struct<(!llvm.ptr, i64)>
%v104 = arith.extsi %v102 : i32 to i64
%v105 = llvm.getelementptr %v103[%v104] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v106 = llvm.load %v105 : !llvm.ptr -> f64
%v107 = llvm.call @printf(%v94, %v100, %v106) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v108 = arith.constant 0 : i32
func.return %v108 : i32
}
}
