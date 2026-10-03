module {
func.func private @malloc(i64) -> !llvm.ptr
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("info %d\0A\00") {addr_space = 0 : i32} : !llvm.array<9 x i8>
llvm.mlir.global internal constant @str_1("unhandled %f\0A\00") {addr_space = 0 : i32} : !llvm.array<14 x i8>
llvm.mlir.global internal constant @str_2("handled %f\0A\00") {addr_space = 0 : i32} : !llvm.array<12 x i8>
llvm.mlir.global internal constant @str_3("clock %d\0A\00") {addr_space = 0 : i32} : !llvm.array<10 x i8>
llvm.mlir.global internal constant @str_4("partial %f\0A\00") {addr_space = 0 : i32} : !llvm.array<12 x i8>
llvm.mlir.global internal constant @str_5("%d-%d\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
llvm.mlir.global internal constant @str_6("%s %d\0A\00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
llvm.func @snprintf(!llvm.ptr, i64, !llvm.ptr, ...) -> i32
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
%v36 = arith.constant 3.0 : f64
%v37 = arith.mulf %arg0, %v36 : f64
func.return %v37 : f64
}
llvm.mlir.global internal @_Console_Log_vtable() {addr_space = 0 : i32} : !llvm.array<2 x ptr> {
%v38 = llvm.mlir.zero : !llvm.ptr
%v39 = llvm.mlir.undef : !llvm.array<2 x ptr>
%v40 = llvm.insertvalue %v38, %v39[0] : !llvm.array<2 x ptr>
%v41 = llvm.insertvalue %v38, %v40[1] : !llvm.array<2 x ptr>
llvm.return %v41 : !llvm.array<2 x ptr>
}
// Capability: Fixed (effects: Clock, Log)
func.func @Fixed_now() -> i64 {
%v42 = arith.constant 1234 : i32
%v43 = arith.extsi %v42 : i32 to i64
func.return %v43 : i64
}
llvm.mlir.global internal @_Fixed_Clock_vtable() {addr_space = 0 : i32} : !llvm.array<1 x ptr> {
%v44 = llvm.mlir.zero : !llvm.ptr
%v45 = llvm.mlir.undef : !llvm.array<1 x ptr>
%v46 = llvm.insertvalue %v44, %v45[0] : !llvm.array<1 x ptr>
llvm.return %v46 : !llvm.array<1 x ptr>
}
llvm.mlir.global internal @_Fixed_Log_vtable() {addr_space = 0 : i32} : !llvm.array<2 x ptr> {
%v47 = llvm.mlir.zero : !llvm.ptr
%v48 = llvm.mlir.undef : !llvm.array<2 x ptr>
%v49 = llvm.insertvalue %v47, %v48[0] : !llvm.array<2 x ptr>
%v50 = llvm.insertvalue %v47, %v49[1] : !llvm.array<2 x ptr>
llvm.return %v50 : !llvm.array<2 x ptr>
}
func.func @work(%arg0: i32) -> f64 {
func.call @Log_info(%arg0) : (i32) -> ()
%v51 = arith.sitofp %arg0 : i32 to f64
%v52 = func.call @Log_scale(%v51) : (f64) -> f64
func.return %v52 : f64
}
func.func @main() -> i32 {
func.call @_flow_effects_init() : () -> ()
%v53 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v54 = arith.constant 1 : i32
%v55 = func.call @work(%v54) : (i32) -> f64
%v56 = llvm.call @printf(%v53, %v55) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v57 = llvm.mlir.addressof @_Console_Log_vtable : !llvm.ptr
%v58 = llvm.mlir.addressof @_current_Log_handler : !llvm.ptr
%v59 = llvm.load %v58 : !llvm.ptr -> !llvm.ptr
llvm.store %v57, %v58 : !llvm.ptr, !llvm.ptr
%v60 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v61 = arith.constant 2 : i32
%v62 = func.call @work(%v61) : (i32) -> f64
%v63 = llvm.call @printf(%v60, %v62) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v64 = arith.constant 7 : i32
func.call @Console_info(%v64) : (i32) -> ()
llvm.store %v59, %v58 : !llvm.ptr, !llvm.ptr
%v65 = llvm.mlir.addressof @_Fixed_Clock_vtable : !llvm.ptr
%v66 = llvm.mlir.addressof @_current_Clock_handler : !llvm.ptr
%v67 = llvm.load %v66 : !llvm.ptr -> !llvm.ptr
llvm.store %v65, %v66 : !llvm.ptr, !llvm.ptr
%v68 = llvm.mlir.addressof @_Fixed_Log_vtable : !llvm.ptr
%v69 = llvm.mlir.addressof @_current_Log_handler : !llvm.ptr
%v70 = llvm.load %v69 : !llvm.ptr -> !llvm.ptr
llvm.store %v68, %v69 : !llvm.ptr, !llvm.ptr
%v71 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v72 = func.call @Fixed_now() : () -> i64
%v73 = llvm.call @printf(%v71, %v72) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v74 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v75 = arith.constant 3 : i32
%v76 = func.call @work(%v75) : (i32) -> f64
%v77 = llvm.call @printf(%v74, %v76) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
llvm.store %v70, %v69 : !llvm.ptr, !llvm.ptr
llvm.store %v67, %v66 : !llvm.ptr, !llvm.ptr
%v78 = arith.constant 64 : i32
%v79 = arith.extsi %v78 : i32 to i64
%v80 = func.call @malloc(%v79) : (i64) -> !llvm.ptr
%v81 = arith.constant 64 : i32
%v82 = llvm.mlir.addressof @str_5 : !llvm.ptr
%v83 = arith.constant 4 : i32
%v84 = arith.constant 5 : i32
%v85 = arith.extsi %v81 : i32 to i64
%v86 = llvm.call @snprintf(%v80, %v85, %v82, %v83, %v84) vararg(!llvm.func<i32 (ptr, i64, ptr, ...)>) : (!llvm.ptr, i64, !llvm.ptr, i32, i32) -> i32
%v87 = llvm.mlir.addressof @str_6 : !llvm.ptr
%v88 = llvm.call @printf(%v87, %v80, %v86) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, !llvm.ptr, i32) -> i32
%v89 = arith.constant 0 : i32
func.return %v89 : i32
}
func.func @_flow_effects_init() {
%v90 = llvm.mlir.addressof @_Console_Log_vtable : !llvm.ptr
%v91 = func.constant @Console_info : (i32) -> ()
%v92 = builtin.unrealized_conversion_cast %v91 : (i32) -> () to !llvm.ptr
%v93 = llvm.getelementptr %v90[0] : (!llvm.ptr) -> !llvm.ptr, !llvm.ptr
llvm.store %v92, %v93 : !llvm.ptr, !llvm.ptr
%v94 = func.constant @Console_scale : (f64) -> f64
%v95 = builtin.unrealized_conversion_cast %v94 : (f64) -> f64 to !llvm.ptr
%v96 = llvm.getelementptr %v90[1] : (!llvm.ptr) -> !llvm.ptr, !llvm.ptr
llvm.store %v95, %v96 : !llvm.ptr, !llvm.ptr
%v97 = llvm.mlir.addressof @_Fixed_Clock_vtable : !llvm.ptr
%v98 = func.constant @Fixed_now : () -> i64
%v99 = builtin.unrealized_conversion_cast %v98 : () -> i64 to !llvm.ptr
%v100 = llvm.getelementptr %v97[0] : (!llvm.ptr) -> !llvm.ptr, !llvm.ptr
llvm.store %v99, %v100 : !llvm.ptr, !llvm.ptr
%v101 = llvm.mlir.addressof @_Fixed_Log_vtable : !llvm.ptr
func.return
}
}
