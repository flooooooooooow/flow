module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\n\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_1("%f\n\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
func.func private @abs(i32) -> i32
func.func private @puts(!llvm.ptr) -> i32
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
%v23 = llvm.mlir.addressof @str_0 : !llvm.ptr
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
%v40 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v41 = llvm.call @printf(%v40, %v39) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v42 = arith.constant 0 : i32
%v43 = llvm.mlir.addressof @SCALE : !llvm.ptr
%v44 = llvm.load %v43 : !llvm.ptr -> f64
%v45 = arith.constant 3.0 : f32
%v46 = arith.extf %v45 : f32 to f64
%v47 = arith.mulf %v44, %v46 : f64
%v48 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v49 = llvm.call @printf(%v48, %v47) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v50 = arith.constant 0 : i32
%v51 = llvm.mlir.addressof @MASK : !llvm.ptr
%v52 = llvm.load %v51 : !llvm.ptr -> i32
%v53 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v54 = llvm.call @printf(%v53, %v52) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v55 = arith.constant 0 : i32
%v56 = arith.constant 0 : i32
%v57 = llvm.mlir.constant(1 : i64) : i64
%v58 = llvm.alloca %v57 x i32 : (i64) -> !llvm.ptr
llvm.store %v56, %v58 : i32, !llvm.ptr
%v59 = arith.constant 0 : i32
%v60 = llvm.mlir.addressof @LIMIT : !llvm.ptr
%v61 = llvm.load %v60 : !llvm.ptr -> i32
%v62 = arith.index_cast %v59 : i32 to index
%v63 = arith.index_cast %v61 : i32 to index
%v64 = arith.constant 1 : index
%v65 = arith.constant -1 : index
%v66 = arith.cmpi sle, %v62, %v63 : index
%v67 = arith.select %v66, %v64, %v65 : index
cf.br ^b7(%v62 : index)
^b7(%v68: index):
%v69 = arith.cmpi slt, %v68, %v63 : index
%v70 = arith.cmpi sgt, %v68, %v63 : index
%v71 = arith.select %v66, %v69, %v70 : i1
cf.cond_br %v71, ^b8(%v68 : index), ^b9(%v68 : index)
^b8(%v72: index):
%v73 = llvm.load %v58 : !llvm.ptr -> i32
%v74 = arith.index_cast %v72 : index to i32
%v75 = arith.addi %v73, %v74 : i32
llvm.store %v75, %v58 : i32, !llvm.ptr
%v76 = arith.addi %v72, %v67 : index
cf.br ^b7(%v76 : index)
^b9(%v77: index):
%v78 = llvm.load %v58 : !llvm.ptr -> i32
func.call @report(%v78) : (i32) -> ()
%v79 = arith.constant 0 : i32
func.return %v79 : i32
}
}
