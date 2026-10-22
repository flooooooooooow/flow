module {
func.func private @abs(i32) -> i32
func.func private @puts(!llvm.ptr) -> i32
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_1("%lld\0A\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
llvm.mlir.global internal constant @str_2("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
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
%v15 = arith.remsi %arg0, %arg1 : i32
%v16 = func.call @gcd(%arg1, %v15) : (i32, i32) -> i32
func.return %v16 : i32
}
func.func @report(%arg0: i32) -> () {
%v17 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v18 = llvm.call @printf(%v17, %arg0) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v19 = arith.constant 0 : i32
func.return
}
func.func @main() -> i32 {
%v20 = llvm.mlir.addressof @LIMIT : !llvm.ptr
%v21 = llvm.load %v20 : !llvm.ptr -> i32
%v22 = func.call @fib(%v21) : (i32) -> i64
%v23 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v24 = llvm.call @printf(%v23, %v22) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v25 = arith.constant 0 : i32
%v26 = arith.constant 84 : i32
%v27 = arith.constant 36 : i32
%v28 = func.call @gcd(%v26, %v27) : (i32, i32) -> i32
%v29 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v30 = llvm.call @printf(%v29, %v28) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v31 = arith.constant 0 : i32
%v32 = arith.constant 0 : i32
%v33 = arith.constant 17 : i32
%v34 = arith.subi %v32, %v33 : i32
%v35 = func.call @abs(%v34) : (i32) -> i32
func.call @report(%v35) : (i32) -> ()
%v36 = llvm.mlir.addressof @NAME : !llvm.ptr
%v37 = func.call @puts(%v36) : (!llvm.ptr) -> i32
%v38 = llvm.mlir.addressof @WIDE : !llvm.ptr
%v39 = llvm.load %v38 : !llvm.ptr -> i64
%v40 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v41 = llvm.call @printf(%v40, %v39) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v42 = arith.constant 0 : i32
%v43 = llvm.mlir.addressof @SCALE : !llvm.ptr
%v44 = llvm.load %v43 : !llvm.ptr -> f64
%v45 = arith.constant 3.0 : f64
%v46 = arith.mulf %v44, %v45 : f64
%v47 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v48 = llvm.call @printf(%v47, %v46) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v49 = arith.constant 0 : i32
%v50 = llvm.mlir.addressof @MASK : !llvm.ptr
%v51 = llvm.load %v50 : !llvm.ptr -> i32
%v52 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v53 = llvm.call @printf(%v52, %v51) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v54 = arith.constant 0 : i32
%v55 = arith.constant 0 : i32
%v56 = llvm.mlir.constant(1 : i64) : i64
%v57 = llvm.alloca %v56 x i32 : (i64) -> !llvm.ptr
llvm.store %v55, %v57 : i32, !llvm.ptr
%v58 = arith.constant 0 : i32
%v59 = llvm.mlir.addressof @LIMIT : !llvm.ptr
%v60 = llvm.load %v59 : !llvm.ptr -> i32
%v61 = arith.index_cast %v58 : i32 to index
%v62 = arith.index_cast %v60 : i32 to index
%v63 = arith.constant 1 : index
%v64 = arith.constant -1 : index
%v65 = arith.cmpi sle, %v61, %v62 : index
%v66 = arith.select %v65, %v63, %v64 : index
cf.br ^b7(%v61 : index)
^b7(%v67: index):
%v68 = arith.cmpi slt, %v67, %v62 : index
%v69 = arith.cmpi sgt, %v67, %v62 : index
%v70 = arith.select %v65, %v68, %v69 : i1
cf.cond_br %v70, ^b8(%v67 : index), ^b9(%v67 : index)
^b8(%v71: index):
%v72 = llvm.load %v57 : !llvm.ptr -> i32
%v73 = arith.index_cast %v71 : index to i32
%v74 = arith.addi %v72, %v73 : i32
llvm.store %v74, %v57 : i32, !llvm.ptr
%v75 = arith.addi %v71, %v66 : index
cf.br ^b7(%v75 : index)
^b9(%v76: index):
%v77 = llvm.load %v57 : !llvm.ptr -> i32
func.call @report(%v77) : (i32) -> ()
%v78 = arith.constant 0 : i32
func.return %v78 : i32
}
}
