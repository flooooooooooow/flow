module {
func.func private @strlen(!llvm.ptr) -> i64
func.func private @write(i32, !llvm.ptr, i64) -> i64
func.func private @abort() -> ()
func.func private @abs(i32) -> i32
func.func private @puts(!llvm.ptr) -> i32
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("flow: \00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
llvm.mlir.global internal constant @str_1("\0A\00") {addr_space = 0 : i32} : !llvm.array<2 x i8>
llvm.mlir.global internal constant @str_2("division by zero\00") {addr_space = 0 : i32} : !llvm.array<17 x i8>
llvm.mlir.global internal constant @str_3("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_4("%lld\0A\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
llvm.mlir.global internal constant @str_5("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
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
// Constant: LIMIT
llvm.mlir.global internal constant @LIMIT(12 : i32) : i32
// Constant: SCALE
llvm.mlir.global internal constant @SCALE(0.5 : f64) : f64
// Constant: WIDE
llvm.mlir.global internal constant @WIDE(-9000000000 : i64) : i64
// Constant: NAME
llvm.mlir.global internal constant @NAME("consts\00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
// Constant: MASK
llvm.mlir.global internal constant @MASK(240 : i32) : i32
func.func @limit() -> i32 {
%v1 = llvm.mlir.addressof @LIMIT : !llvm.ptr
%v2 = llvm.load %v1 : !llvm.ptr -> i32
func.return %v2 : i32
}
func.func @fib(%arg0: i32) -> i64 {
%v3 = arith.constant 2 : i32
%v4 = arith.cmpi slt, %arg0, %v3 : i32
cf.cond_br %v4, ^b1, ^b2
^b1:
%v5 = arith.extsi %arg0 : i32 to i64
func.return %v5 : i64
^b2:
cf.br ^b3
^b3:
%v6 = arith.constant 1 : i32
%v7 = arith.subi %arg0, %v6 : i32
%v8 = func.call @fib(%v7) : (i32) -> i64
%v9 = arith.constant 2 : i32
%v10 = arith.subi %arg0, %v9 : i32
%v11 = func.call @fib(%v10) : (i32) -> i64
%v12 = arith.addi %v8, %v11 : i64
func.return %v12 : i64
}
func.func @gcd(%arg0: i32, %arg1: i32) -> i32 {
%v13 = arith.constant 0 : i32
%v14 = arith.cmpi eq, %arg1, %v13 : i32
cf.cond_br %v14, ^b4, ^b5
^b4:
func.return %arg0 : i32
^b5:
cf.br ^b6
^b6:
%v15 = arith.constant 0 : i32
%v16 = arith.cmpi eq, %arg1, %v15 : i32
scf.if %v16 {
%v17 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v17) : (!llvm.ptr) -> ()
}
%v18 = arith.remsi %arg0, %arg1 : i32
%v19 = func.call @gcd(%arg1, %v18) : (i32, i32) -> i32
func.return %v19 : i32
}
func.func @report(%arg0: i32) -> () {
%v20 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v21 = llvm.call @printf(%v20, %arg0) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v22 = arith.constant 0 : i32
func.return
}
func.func @main() -> i32 {
%v23 = llvm.mlir.addressof @LIMIT : !llvm.ptr
%v24 = llvm.load %v23 : !llvm.ptr -> i32
%v25 = func.call @fib(%v24) : (i32) -> i64
%v26 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v27 = llvm.call @printf(%v26, %v25) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v28 = arith.constant 0 : i32
%v29 = arith.constant 84 : i32
%v30 = arith.constant 36 : i32
%v31 = func.call @gcd(%v29, %v30) : (i32, i32) -> i32
%v32 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v33 = llvm.call @printf(%v32, %v31) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v34 = arith.constant 0 : i32
%v35 = arith.constant 0 : i32
%v36 = arith.constant 17 : i32
%v37 = arith.subi %v35, %v36 : i32
%v38 = func.call @abs(%v37) : (i32) -> i32
func.call @report(%v38) : (i32) -> ()
%v39 = llvm.mlir.addressof @NAME : !llvm.ptr
%v40 = func.call @puts(%v39) : (!llvm.ptr) -> i32
%v41 = llvm.mlir.addressof @WIDE : !llvm.ptr
%v42 = llvm.load %v41 : !llvm.ptr -> i64
%v43 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v44 = llvm.call @printf(%v43, %v42) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v45 = arith.constant 0 : i32
%v46 = llvm.mlir.addressof @SCALE : !llvm.ptr
%v47 = llvm.load %v46 : !llvm.ptr -> f64
%v48 = arith.constant 3.0 : f64
%v49 = arith.mulf %v47, %v48 : f64
%v50 = llvm.mlir.addressof @str_5 : !llvm.ptr
%v51 = llvm.call @printf(%v50, %v49) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v52 = arith.constant 0 : i32
%v53 = llvm.mlir.addressof @MASK : !llvm.ptr
%v54 = llvm.load %v53 : !llvm.ptr -> i32
%v55 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v56 = llvm.call @printf(%v55, %v54) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v57 = arith.constant 0 : i32
%v58 = arith.constant 0 : i32
%v59 = llvm.mlir.constant(1 : i64) : i64
%v60 = llvm.alloca %v59 x i32 : (i64) -> !llvm.ptr
llvm.store %v58, %v60 : i32, !llvm.ptr
%v61 = arith.constant 0 : i32
%v62 = llvm.mlir.addressof @LIMIT : !llvm.ptr
%v63 = llvm.load %v62 : !llvm.ptr -> i32
%v64 = arith.index_cast %v61 : i32 to index
%v65 = arith.index_cast %v63 : i32 to index
%v66 = arith.constant 1 : index
%v67 = arith.constant -1 : index
%v68 = arith.cmpi sle, %v64, %v65 : index
%v69 = arith.select %v68, %v66, %v67 : index
cf.br ^b7(%v64 : index)
^b7(%v70: index):
%v71 = arith.cmpi slt, %v70, %v65 : index
%v72 = arith.cmpi sgt, %v70, %v65 : index
%v73 = arith.select %v68, %v71, %v72 : i1
cf.cond_br %v73, ^b8(%v70 : index), ^b9(%v70 : index)
^b8(%v74: index):
%v75 = llvm.load %v60 : !llvm.ptr -> i32
%v76 = arith.index_cast %v74 : index to i32
%v77 = arith.addi %v75, %v76 : i32
llvm.store %v77, %v60 : i32, !llvm.ptr
%v78 = arith.addi %v74, %v69 : index
cf.br ^b7(%v78 : index)
^b9(%v79: index):
%v80 = llvm.load %v60 : !llvm.ptr -> i32
func.call @report(%v80) : (i32) -> ()
%v81 = arith.constant 0 : i32
func.return %v81 : i32
}
}
