module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("info %d\n\00") {addr_space = 0 : i32} : !llvm.array<9 x i8>
llvm.mlir.global internal constant @str_1("unhandled %f\n\00") {addr_space = 0 : i32} : !llvm.array<14 x i8>
llvm.mlir.global internal constant @str_2("handled %f\n\00") {addr_space = 0 : i32} : !llvm.array<12 x i8>
llvm.mlir.global internal constant @str_3("clock %d\n\00") {addr_space = 0 : i32} : !llvm.array<10 x i8>
llvm.mlir.global internal constant @str_4("partial %f\n\00") {addr_space = 0 : i32} : !llvm.array<12 x i8>
llvm.mlir.global internal constant @str_5("%d-%d\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
llvm.mlir.global internal constant @str_6("%s %d\n\00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
llvm.func @snprintf(!llvm.ptr, i64, !llvm.ptr, ...) -> i32
func.func private @malloc(i64) -> !llvm.ptr
// Effect: Log
llvm.mlir.global internal @_current_Log_handler() {addr_space = 0 : i32} : !llvm.ptr {
%v1 = llvm.mlir.zero : !llvm.ptr
llvm.return %v1 : !llvm.ptr
}
func.func @Log_info(%arg0: i32) -> () {
%v2 = llvm.mlir.addressof @_current_Log_handler : !llvm.ptr
%v3 = llvm.load %v2 : !llvm.ptr -> !llvm.ptr
%v4 = llvm.mlir.zero : !llvm.ptr
%v5 = llvm.icmp "ne" %v3, %v4 : !llvm.ptr
scf.if %v5 {
%v6 = llvm.getelementptr %v3[0] : (!llvm.ptr) -> !llvm.ptr, !llvm.ptr
%v7 = llvm.load %v6 : !llvm.ptr -> !llvm.ptr
%v8 = llvm.icmp "ne" %v7, %v4 : !llvm.ptr
scf.if %v8 {
llvm.call %v7(%arg0) : !llvm.ptr, (i32) -> ()
}
}
func.return
}
func.func @Log_scale(%arg0: f64) -> f64 {
%v9 = llvm.mlir.addressof @_current_Log_handler : !llvm.ptr
%v10 = llvm.load %v9 : !llvm.ptr -> !llvm.ptr
%v11 = llvm.mlir.zero : !llvm.ptr
%v12 = llvm.icmp "ne" %v10, %v11 : !llvm.ptr
%v13 = scf.if %v12 -> (f64) {
%v14 = llvm.getelementptr %v10[1] : (!llvm.ptr) -> !llvm.ptr, !llvm.ptr
%v15 = llvm.load %v14 : !llvm.ptr -> !llvm.ptr
%v16 = llvm.icmp "ne" %v15, %v11 : !llvm.ptr
%v17 = scf.if %v16 -> (f64) {
%v18 = llvm.call %v15(%arg0) : !llvm.ptr, (f64) -> f64
scf.yield %v18 : f64
} else {
%v19 = arith.constant 0.0 : f64
scf.yield %v19 : f64
}
scf.yield %v17 : f64
} else {
%v20 = arith.constant 0.0 : f64
scf.yield %v20 : f64
}
func.return %v13 : f64
}
// Effect: Clock
llvm.mlir.global internal @_current_Clock_handler() {addr_space = 0 : i32} : !llvm.ptr {
%v21 = llvm.mlir.zero : !llvm.ptr
llvm.return %v21 : !llvm.ptr
}
func.func @Clock_now() -> i64 {
%v22 = llvm.mlir.addressof @_current_Clock_handler : !llvm.ptr
%v23 = llvm.load %v22 : !llvm.ptr -> !llvm.ptr
%v24 = llvm.mlir.zero : !llvm.ptr
%v25 = llvm.icmp "ne" %v23, %v24 : !llvm.ptr
%v26 = scf.if %v25 -> (i64) {
%v27 = llvm.getelementptr %v23[0] : (!llvm.ptr) -> !llvm.ptr, !llvm.ptr
%v28 = llvm.load %v27 : !llvm.ptr -> !llvm.ptr
%v29 = llvm.icmp "ne" %v28, %v24 : !llvm.ptr
%v30 = scf.if %v29 -> (i64) {
%v31 = llvm.call %v28() : !llvm.ptr, () -> i64
scf.yield %v31 : i64
} else {
%v32 = arith.constant 0 : i64
scf.yield %v32 : i64
}
scf.yield %v30 : i64
} else {
%v33 = arith.constant 0 : i64
scf.yield %v33 : i64
}
func.return %v26 : i64
}
// Capability: Console (effects: Log)
func.func @Console_info(%arg0: i32) -> () {
%v34 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v35 = llvm.call @printf(%v34, %arg0) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
func.return
}
func.func @Console_scale(%arg0: f64) -> f64 {
%v36 = arith.constant 3.0 : f32
%v37 = arith.extf %v36 : f32 to f64
%v38 = arith.mulf %arg0, %v37 : f64
func.return %v38 : f64
}
llvm.mlir.global internal @_Console_Log_vtable() {addr_space = 0 : i32} : !llvm.array<2 x ptr> {
%v39 = llvm.mlir.zero : !llvm.ptr
%v40 = llvm.mlir.undef : !llvm.array<2 x ptr>
%v41 = llvm.insertvalue %v39, %v40[0] : !llvm.array<2 x ptr>
%v42 = llvm.insertvalue %v39, %v41[1] : !llvm.array<2 x ptr>
llvm.return %v42 : !llvm.array<2 x ptr>
}
// Capability: Fixed (effects: Clock, Log)
func.func @Fixed_now() -> i64 {
%v43 = arith.constant 1234 : i32
%v44 = arith.extsi %v43 : i32 to i64
func.return %v44 : i64
}
llvm.mlir.global internal @_Fixed_Clock_vtable() {addr_space = 0 : i32} : !llvm.array<1 x ptr> {
%v45 = llvm.mlir.zero : !llvm.ptr
%v46 = llvm.mlir.undef : !llvm.array<1 x ptr>
%v47 = llvm.insertvalue %v45, %v46[0] : !llvm.array<1 x ptr>
llvm.return %v47 : !llvm.array<1 x ptr>
}
llvm.mlir.global internal @_Fixed_Log_vtable() {addr_space = 0 : i32} : !llvm.array<2 x ptr> {
%v48 = llvm.mlir.zero : !llvm.ptr
%v49 = llvm.mlir.undef : !llvm.array<2 x ptr>
%v50 = llvm.insertvalue %v48, %v49[0] : !llvm.array<2 x ptr>
%v51 = llvm.insertvalue %v48, %v50[1] : !llvm.array<2 x ptr>
llvm.return %v51 : !llvm.array<2 x ptr>
}
func.func @work(%arg0: i32) -> f64 {
func.call @Log_info(%arg0) : (i32) -> ()
%v52 = arith.sitofp %arg0 : i32 to f64
%v53 = func.call @Log_scale(%v52) : (f64) -> f64
func.return %v53 : f64
}
func.func @main() -> i32 {
func.call @_flow_effects_init() : () -> ()
%v54 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v55 = arith.constant 1 : i32
%v56 = func.call @work(%v55) : (i32) -> f64
%v57 = llvm.call @printf(%v54, %v56) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v58 = llvm.mlir.addressof @_Console_Log_vtable : !llvm.ptr
%v59 = llvm.mlir.addressof @_current_Log_handler : !llvm.ptr
%v60 = llvm.load %v59 : !llvm.ptr -> !llvm.ptr
llvm.store %v58, %v59 : !llvm.ptr, !llvm.ptr
%v61 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v62 = arith.constant 2 : i32
%v63 = func.call @work(%v62) : (i32) -> f64
%v64 = llvm.call @printf(%v61, %v63) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v65 = arith.constant 7 : i32
func.call @Console_info(%v65) : (i32) -> ()
llvm.store %v60, %v59 : !llvm.ptr, !llvm.ptr
%v66 = llvm.mlir.addressof @_Fixed_Clock_vtable : !llvm.ptr
%v67 = llvm.mlir.addressof @_current_Clock_handler : !llvm.ptr
%v68 = llvm.load %v67 : !llvm.ptr -> !llvm.ptr
llvm.store %v66, %v67 : !llvm.ptr, !llvm.ptr
%v69 = llvm.mlir.addressof @_Fixed_Log_vtable : !llvm.ptr
%v70 = llvm.mlir.addressof @_current_Log_handler : !llvm.ptr
%v71 = llvm.load %v70 : !llvm.ptr -> !llvm.ptr
llvm.store %v69, %v70 : !llvm.ptr, !llvm.ptr
%v72 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v73 = func.call @Fixed_now() : () -> i64
%v74 = llvm.call @printf(%v72, %v73) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v75 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v76 = arith.constant 3 : i32
%v77 = func.call @work(%v76) : (i32) -> f64
%v78 = llvm.call @printf(%v75, %v77) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
llvm.store %v71, %v70 : !llvm.ptr, !llvm.ptr
llvm.store %v68, %v67 : !llvm.ptr, !llvm.ptr
%v79 = arith.constant 64 : i32
%v80 = arith.extsi %v79 : i32 to i64
%v81 = func.call @malloc(%v80) : (i64) -> !llvm.ptr
%v82 = arith.constant 64 : i32
%v83 = llvm.mlir.addressof @str_5 : !llvm.ptr
%v84 = arith.constant 4 : i32
%v85 = arith.constant 5 : i32
%v86 = arith.extsi %v82 : i32 to i64
%v87 = llvm.call @snprintf(%v81, %v86, %v83, %v84, %v85) vararg(!llvm.func<i32 (ptr, i64, ptr, ...)>) : (!llvm.ptr, i64, !llvm.ptr, i32, i32) -> i32
%v88 = llvm.mlir.addressof @str_6 : !llvm.ptr
%v89 = llvm.call @printf(%v88, %v81, %v87) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, !llvm.ptr, i32) -> i32
%v90 = arith.constant 0 : i32
func.return %v90 : i32
}
func.func @_flow_effects_init() {
%v91 = llvm.mlir.addressof @_Console_Log_vtable : !llvm.ptr
%v92 = func.constant @Console_info : (i32) -> ()
%v93 = builtin.unrealized_conversion_cast %v92 : (i32) -> () to !llvm.ptr
%v94 = llvm.getelementptr %v91[0] : (!llvm.ptr) -> !llvm.ptr, !llvm.ptr
llvm.store %v93, %v94 : !llvm.ptr, !llvm.ptr
%v95 = func.constant @Console_scale : (f64) -> f64
%v96 = builtin.unrealized_conversion_cast %v95 : (f64) -> f64 to !llvm.ptr
%v97 = llvm.getelementptr %v91[1] : (!llvm.ptr) -> !llvm.ptr, !llvm.ptr
llvm.store %v96, %v97 : !llvm.ptr, !llvm.ptr
%v98 = llvm.mlir.addressof @_Fixed_Clock_vtable : !llvm.ptr
%v99 = func.constant @Fixed_now : () -> i64
%v100 = builtin.unrealized_conversion_cast %v99 : () -> i64 to !llvm.ptr
%v101 = llvm.getelementptr %v98[0] : (!llvm.ptr) -> !llvm.ptr, !llvm.ptr
llvm.store %v100, %v101 : !llvm.ptr, !llvm.ptr
%v102 = llvm.mlir.addressof @_Fixed_Log_vtable : !llvm.ptr
func.return
}
}
