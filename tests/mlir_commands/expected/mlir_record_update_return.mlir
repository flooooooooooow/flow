module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
// Struct: Point
// Fields:
//   x: i32
//   y: i32
func.func @bumped(%arg0: i32) -> !llvm.struct<(i32, i32)> {
%v1 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v2 = arith.constant 1 : i32
%v3 = llvm.insertvalue %v2, %v1[0] : !llvm.struct<(i32, i32)>
%v4 = arith.constant 2 : i32
%v5 = llvm.insertvalue %v4, %v3[1] : !llvm.struct<(i32, i32)>
%v6 = llvm.mlir.constant(1 : i64) : i64
%v7 = llvm.alloca %v6 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v5, %v7 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v8 = llvm.getelementptr %v7[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
llvm.store %arg0, %v8 : i32, !llvm.ptr
%v9 = llvm.load %v7 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v10 = arith.constant 5 : i32
%v11 = llvm.insertvalue %v10, %v9[1] : !llvm.struct<(i32, i32)>
func.return %v11 : !llvm.struct<(i32, i32)>
}
func.func @shifted(%arg0: i32) -> !llvm.struct<(i32, i32)> {
%v12 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v13 = llvm.insertvalue %arg0, %v12[0] : !llvm.struct<(i32, i32)>
%v14 = arith.constant 1 : i32
%v15 = arith.addi %arg0, %v14 : i32
%v16 = llvm.insertvalue %v15, %v13[1] : !llvm.struct<(i32, i32)>
%v17 = llvm.mlir.constant(1 : i64) : i64
%v18 = llvm.alloca %v17 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v16, %v18 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v19 = llvm.load %v18 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v20 = arith.constant 0 : i32
%v21 = llvm.insertvalue %v20, %v19[0] : !llvm.struct<(i32, i32)>
func.return %v21 : !llvm.struct<(i32, i32)>
}
func.func @main() -> i32 {
%v22 = arith.constant 7 : i32
%v23 = func.call @bumped(%v22) : (i32) -> !llvm.struct<(i32, i32)>
%v24 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v25 = llvm.extractvalue %v23[0] : !llvm.struct<(i32, i32)>
%v26 = llvm.insertvalue %v25, %v24[0] : !llvm.struct<(i32, i32)>
%v27 = llvm.extractvalue %v23[1] : !llvm.struct<(i32, i32)>
%v28 = llvm.insertvalue %v27, %v26[1] : !llvm.struct<(i32, i32)>
%v29 = llvm.mlir.constant(1 : i64) : i64
%v30 = llvm.alloca %v29 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v28, %v30 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v31 = llvm.load %v30 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v32 = llvm.mlir.constant(1 : i64) : i64
%v33 = llvm.alloca %v32 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v31, %v33 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v34 = arith.constant 3 : i32
%v35 = func.call @shifted(%v34) : (i32) -> !llvm.struct<(i32, i32)>
%v36 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v37 = llvm.extractvalue %v35[0] : !llvm.struct<(i32, i32)>
%v38 = llvm.insertvalue %v37, %v36[0] : !llvm.struct<(i32, i32)>
%v39 = llvm.extractvalue %v35[1] : !llvm.struct<(i32, i32)>
%v40 = llvm.insertvalue %v39, %v38[1] : !llvm.struct<(i32, i32)>
%v41 = llvm.mlir.constant(1 : i64) : i64
%v42 = llvm.alloca %v41 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v40, %v42 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v43 = llvm.load %v42 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v44 = llvm.mlir.constant(1 : i64) : i64
%v45 = llvm.alloca %v44 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v43, %v45 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v46 = llvm.load %v33 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v47 = llvm.getelementptr %v33[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v48 = llvm.load %v47 : !llvm.ptr -> i32
%v49 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v50 = llvm.call @printf(%v49, %v48) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v51 = arith.constant 0 : i32
%v52 = llvm.load %v33 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v53 = llvm.getelementptr %v33[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v54 = llvm.load %v53 : !llvm.ptr -> i32
%v55 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v56 = llvm.call @printf(%v55, %v54) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v57 = arith.constant 0 : i32
%v58 = llvm.load %v45 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v59 = llvm.getelementptr %v45[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v60 = llvm.load %v59 : !llvm.ptr -> i32
%v61 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v62 = llvm.call @printf(%v61, %v60) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v63 = arith.constant 0 : i32
%v64 = llvm.load %v45 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v65 = llvm.getelementptr %v45[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v66 = llvm.load %v65 : !llvm.ptr -> i32
%v67 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v68 = llvm.call @printf(%v67, %v66) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v69 = arith.constant 0 : i32
%v70 = arith.constant 0 : i32
func.return %v70 : i32
}
}
