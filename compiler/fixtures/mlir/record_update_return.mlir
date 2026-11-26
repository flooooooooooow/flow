module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
// Struct: Point
// Fields:
//   x: i32
//   y: i32
func.func @bumped(%arg0: i32) -> !llvm.struct<(i32, i32)> {
%v1 = llvm.mlir.constant(1 : i64) : i64
%v2 = llvm.alloca %v1 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
%v3 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v4 = arith.constant 1 : i32
%v5 = llvm.insertvalue %v4, %v3[0] : !llvm.struct<(i32, i32)>
%v6 = arith.constant 2 : i32
%v7 = llvm.insertvalue %v6, %v5[1] : !llvm.struct<(i32, i32)>
llvm.store %v7, %v2 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v8 = llvm.getelementptr %v2[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
llvm.store %arg0, %v8 : i32, !llvm.ptr
%v9 = llvm.load %v2 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v10 = arith.constant 5 : i32
%v11 = llvm.insertvalue %v10, %v9[1] : !llvm.struct<(i32, i32)>
func.return %v11 : !llvm.struct<(i32, i32)>
}
func.func @shifted(%arg0: i32) -> !llvm.struct<(i32, i32)> {
%v12 = llvm.mlir.constant(1 : i64) : i64
%v13 = llvm.alloca %v12 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
%v14 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v15 = llvm.insertvalue %arg0, %v14[0] : !llvm.struct<(i32, i32)>
%v16 = arith.constant 1 : i32
%v17 = arith.addi %arg0, %v16 : i32
%v18 = llvm.insertvalue %v17, %v15[1] : !llvm.struct<(i32, i32)>
llvm.store %v18, %v13 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v19 = llvm.load %v13 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v20 = arith.constant 0 : i32
%v21 = llvm.insertvalue %v20, %v19[0] : !llvm.struct<(i32, i32)>
func.return %v21 : !llvm.struct<(i32, i32)>
}
func.func @main() -> i32 {
%v22 = llvm.mlir.constant(1 : i64) : i64
%v23 = llvm.alloca %v22 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
%v24 = llvm.mlir.constant(1 : i64) : i64
%v25 = llvm.alloca %v24 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
%v26 = llvm.mlir.constant(1 : i64) : i64
%v27 = llvm.alloca %v26 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
%v28 = llvm.mlir.constant(1 : i64) : i64
%v29 = llvm.alloca %v28 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
%v30 = arith.constant 7 : i32
%v31 = func.call @bumped(%v30) : (i32) -> !llvm.struct<(i32, i32)>
%v32 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v33 = llvm.extractvalue %v31[0] : !llvm.struct<(i32, i32)>
%v34 = llvm.insertvalue %v33, %v32[0] : !llvm.struct<(i32, i32)>
%v35 = llvm.extractvalue %v31[1] : !llvm.struct<(i32, i32)>
%v36 = llvm.insertvalue %v35, %v34[1] : !llvm.struct<(i32, i32)>
llvm.store %v36, %v23 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v37 = llvm.load %v23 : !llvm.ptr -> !llvm.struct<(i32, i32)>
llvm.store %v37, %v25 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v38 = arith.constant 3 : i32
%v39 = func.call @shifted(%v38) : (i32) -> !llvm.struct<(i32, i32)>
%v40 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v41 = llvm.extractvalue %v39[0] : !llvm.struct<(i32, i32)>
%v42 = llvm.insertvalue %v41, %v40[0] : !llvm.struct<(i32, i32)>
%v43 = llvm.extractvalue %v39[1] : !llvm.struct<(i32, i32)>
%v44 = llvm.insertvalue %v43, %v42[1] : !llvm.struct<(i32, i32)>
llvm.store %v44, %v27 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v45 = llvm.load %v27 : !llvm.ptr -> !llvm.struct<(i32, i32)>
llvm.store %v45, %v29 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v46 = llvm.load %v25 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v47 = llvm.getelementptr %v25[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v48 = llvm.load %v47 : !llvm.ptr -> i32
%v49 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v50 = llvm.call @printf(%v49, %v48) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v51 = arith.constant 0 : i32
%v52 = llvm.load %v25 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v53 = llvm.getelementptr %v25[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v54 = llvm.load %v53 : !llvm.ptr -> i32
%v55 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v56 = llvm.call @printf(%v55, %v54) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v57 = arith.constant 0 : i32
%v58 = llvm.load %v29 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v59 = llvm.getelementptr %v29[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v60 = llvm.load %v59 : !llvm.ptr -> i32
%v61 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v62 = llvm.call @printf(%v61, %v60) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v63 = arith.constant 0 : i32
%v64 = llvm.load %v29 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v65 = llvm.getelementptr %v29[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v66 = llvm.load %v65 : !llvm.ptr -> i32
%v67 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v68 = llvm.call @printf(%v67, %v66) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v69 = arith.constant 0 : i32
%v70 = arith.constant 0 : i32
func.return %v70 : i32
}
}
