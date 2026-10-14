module {
func.func private @strlen(!llvm.ptr) -> i64
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("abc\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_1("%d %d %d\0A\00") {addr_space = 0 : i32} : !llvm.array<10 x i8>
llvm.mlir.global internal constant @str_2("sum %d\0A\00") {addr_space = 0 : i32} : !llvm.array<8 x i8>
llvm.mlir.global internal constant @str_3("\C3\A9\00") {addr_space = 0 : i32} : !llvm.array<3 x i8>
llvm.mlir.global internal constant @str_4("high byte %d %d\0A\00") {addr_space = 0 : i32} : !llvm.array<17 x i8>
llvm.mlir.global internal constant @str_5("b at 1\0A\00") {addr_space = 0 : i32} : !llvm.array<8 x i8>
func.func @byte_sum(%arg0: !llvm.ptr) -> i32 {
%v1 = func.call @strlen(%arg0) : (!llvm.ptr) -> i64
%v2 = arith.trunci %v1 : i64 to i32
%v3 = arith.constant 0 : i32
%v4 = llvm.mlir.constant(1 : i64) : i64
%v5 = llvm.alloca %v4 x i32 : (i64) -> !llvm.ptr
llvm.store %v3, %v5 : i32, !llvm.ptr
%v6 = arith.constant 0 : i32
%v7 = llvm.mlir.constant(1 : i64) : i64
%v8 = llvm.alloca %v7 x i32 : (i64) -> !llvm.ptr
llvm.store %v6, %v8 : i32, !llvm.ptr
cf.br ^b1
^b1:
%v9 = llvm.load %v8 : !llvm.ptr -> i32
%v10 = arith.cmpi slt, %v9, %v2 : i32
cf.cond_br %v10, ^b2, ^b3
^b2:
%v11 = llvm.load %v5 : !llvm.ptr -> i32
%v12 = llvm.load %v8 : !llvm.ptr -> i32
%v13 = arith.extsi %v12 : i32 to i64
%v14 = llvm.getelementptr %arg0[%v13] : (!llvm.ptr, i64) -> !llvm.ptr, i8
%v15 = llvm.load %v14 : !llvm.ptr -> i8
%v16 = arith.extui %v15 : i8 to i32
%v17 = arith.addi %v11, %v16 : i32
llvm.store %v17, %v5 : i32, !llvm.ptr
%v18 = llvm.load %v8 : !llvm.ptr -> i32
%v19 = arith.constant 1 : i32
%v20 = arith.addi %v18, %v19 : i32
llvm.store %v20, %v8 : i32, !llvm.ptr
cf.br ^b1
^b3:
%v21 = llvm.load %v5 : !llvm.ptr -> i32
func.return %v21 : i32
}
func.func @main() -> i32 {
%v22 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v23 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v24 = arith.constant 0 : i32
%v25 = arith.extsi %v24 : i32 to i64
%v26 = llvm.getelementptr %v22[%v25] : (!llvm.ptr, i64) -> !llvm.ptr, i8
%v27 = llvm.load %v26 : !llvm.ptr -> i8
%v28 = arith.extui %v27 : i8 to i32
%v29 = arith.constant 1 : i32
%v30 = arith.extsi %v29 : i32 to i64
%v31 = llvm.getelementptr %v22[%v30] : (!llvm.ptr, i64) -> !llvm.ptr, i8
%v32 = llvm.load %v31 : !llvm.ptr -> i8
%v33 = arith.extui %v32 : i8 to i32
%v34 = arith.constant 2 : i32
%v35 = arith.extsi %v34 : i32 to i64
%v36 = llvm.getelementptr %v22[%v35] : (!llvm.ptr, i64) -> !llvm.ptr, i8
%v37 = llvm.load %v36 : !llvm.ptr -> i8
%v38 = arith.extui %v37 : i8 to i32
%v39 = llvm.call @printf(%v23, %v28, %v33, %v38) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32, i32, i32) -> i32
%v40 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v41 = func.call @byte_sum(%v22) : (!llvm.ptr) -> i32
%v42 = llvm.call @printf(%v40, %v41) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v43 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v44 = arith.constant 0 : i32
%v45 = arith.extsi %v44 : i32 to i64
%v46 = llvm.getelementptr %v43[%v45] : (!llvm.ptr, i64) -> !llvm.ptr, i8
%v47 = llvm.load %v46 : !llvm.ptr -> i8
%v48 = arith.extui %v47 : i8 to i32
%v49 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v50 = arith.constant 1 : i32
%v51 = arith.extsi %v50 : i32 to i64
%v52 = llvm.getelementptr %v43[%v51] : (!llvm.ptr, i64) -> !llvm.ptr, i8
%v53 = llvm.load %v52 : !llvm.ptr -> i8
%v54 = arith.extui %v53 : i8 to i32
%v55 = llvm.call @printf(%v49, %v48, %v54) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32, i32) -> i32
%v56 = arith.constant 1 : i32
%v57 = arith.extsi %v56 : i32 to i64
%v58 = llvm.getelementptr %v22[%v57] : (!llvm.ptr, i64) -> !llvm.ptr, i8
%v59 = llvm.load %v58 : !llvm.ptr -> i8
%v60 = arith.constant 98 : i32
%v61 = arith.extui %v59 : i8 to i32
%v62 = arith.cmpi eq, %v61, %v60 : i32
cf.cond_br %v62, ^b4, ^b5
^b4:
%v63 = llvm.mlir.addressof @str_5 : !llvm.ptr
%v64 = llvm.call @printf(%v63) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
cf.br ^b6
^b5:
cf.br ^b6
^b6:
%v65 = arith.constant 0 : i32
func.return %v65 : i32
}
}
