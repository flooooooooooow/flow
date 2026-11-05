module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("square %d %d\0A\00") {addr_space = 0 : i32} : !llvm.array<14 x i8>
llvm.mlir.global internal constant @str_1("rect %d %d\0A\00") {addr_space = 0 : i32} : !llvm.array<12 x i8>
// Struct: Square
// Fields:
//   side: i32
// Struct: Rect
// Fields:
//   w: i32
//   h: i32
func.func @Square_Shape_area(%arg0: !llvm.struct<(i32)>) -> i32 {
%v1 = llvm.mlir.undef : !llvm.struct<(i32)>
%v2 = llvm.extractvalue %arg0[0] : !llvm.struct<(i32)>
%v3 = llvm.insertvalue %v2, %v1[0] : !llvm.struct<(i32)>
%v4 = llvm.mlir.constant(1 : i64) : i64
%v5 = llvm.alloca %v4 x !llvm.struct<(i32)> : (i64) -> !llvm.ptr
llvm.store %v3, %v5 : !llvm.struct<(i32)>, !llvm.ptr
%v6 = llvm.load %v5 : !llvm.ptr -> !llvm.struct<(i32)>
%v7 = llvm.getelementptr %v5[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32)>
%v8 = llvm.load %v7 : !llvm.ptr -> i32
%v9 = llvm.load %v5 : !llvm.ptr -> !llvm.struct<(i32)>
%v10 = llvm.getelementptr %v5[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32)>
%v11 = llvm.load %v10 : !llvm.ptr -> i32
%v12 = arith.muli %v8, %v11 : i32
func.return %v12 : i32
}
func.func @Square_Shape_scaled(%arg0: !llvm.struct<(i32)>, %arg1: i32) -> i32 {
%v13 = llvm.mlir.undef : !llvm.struct<(i32)>
%v14 = llvm.extractvalue %arg0[0] : !llvm.struct<(i32)>
%v15 = llvm.insertvalue %v14, %v13[0] : !llvm.struct<(i32)>
%v16 = llvm.mlir.constant(1 : i64) : i64
%v17 = llvm.alloca %v16 x !llvm.struct<(i32)> : (i64) -> !llvm.ptr
llvm.store %v15, %v17 : !llvm.struct<(i32)>, !llvm.ptr
%v18 = llvm.load %v17 : !llvm.ptr -> !llvm.struct<(i32)>
%v19 = func.call @Square_Shape_area(%v18) : (!llvm.struct<(i32)>) -> i32
%v20 = arith.muli %v19, %arg1 : i32
func.return %v20 : i32
}
func.func @Rect_Shape_area(%arg0: !llvm.struct<(i32, i32)>) -> i32 {
%v21 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v22 = llvm.extractvalue %arg0[0] : !llvm.struct<(i32, i32)>
%v23 = llvm.insertvalue %v22, %v21[0] : !llvm.struct<(i32, i32)>
%v24 = llvm.extractvalue %arg0[1] : !llvm.struct<(i32, i32)>
%v25 = llvm.insertvalue %v24, %v23[1] : !llvm.struct<(i32, i32)>
%v26 = llvm.mlir.constant(1 : i64) : i64
%v27 = llvm.alloca %v26 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v25, %v27 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v28 = llvm.load %v27 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v29 = llvm.getelementptr %v27[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v30 = llvm.load %v29 : !llvm.ptr -> i32
%v31 = llvm.load %v27 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v32 = llvm.getelementptr %v27[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v33 = llvm.load %v32 : !llvm.ptr -> i32
%v34 = arith.muli %v30, %v33 : i32
func.return %v34 : i32
}
func.func @Rect_Shape_scaled(%arg0: !llvm.struct<(i32, i32)>, %arg1: i32) -> i32 {
%v35 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v36 = llvm.extractvalue %arg0[0] : !llvm.struct<(i32, i32)>
%v37 = llvm.insertvalue %v36, %v35[0] : !llvm.struct<(i32, i32)>
%v38 = llvm.extractvalue %arg0[1] : !llvm.struct<(i32, i32)>
%v39 = llvm.insertvalue %v38, %v37[1] : !llvm.struct<(i32, i32)>
%v40 = llvm.mlir.constant(1 : i64) : i64
%v41 = llvm.alloca %v40 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v39, %v41 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v42 = llvm.load %v41 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v43 = llvm.getelementptr %v41[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v44 = llvm.load %v43 : !llvm.ptr -> i32
%v45 = llvm.load %v41 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v46 = llvm.getelementptr %v41[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v47 = llvm.load %v46 : !llvm.ptr -> i32
%v48 = arith.muli %v44, %v47 : i32
%v49 = arith.muli %v48, %arg1 : i32
func.return %v49 : i32
}
func.func @main() -> i32 {
%v50 = llvm.mlir.undef : !llvm.struct<(i32)>
%v51 = arith.constant 3 : i32
%v52 = llvm.insertvalue %v51, %v50[0] : !llvm.struct<(i32)>
%v53 = llvm.mlir.constant(1 : i64) : i64
%v54 = llvm.alloca %v53 x !llvm.struct<(i32)> : (i64) -> !llvm.ptr
llvm.store %v52, %v54 : !llvm.struct<(i32)>, !llvm.ptr
%v55 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v56 = arith.constant 2 : i32
%v57 = llvm.insertvalue %v56, %v55[0] : !llvm.struct<(i32, i32)>
%v58 = arith.constant 5 : i32
%v59 = llvm.insertvalue %v58, %v57[1] : !llvm.struct<(i32, i32)>
%v60 = llvm.mlir.constant(1 : i64) : i64
%v61 = llvm.alloca %v60 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v59, %v61 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v62 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v63 = llvm.load %v54 : !llvm.ptr -> !llvm.struct<(i32)>
%v64 = func.call @Square_Shape_area(%v63) : (!llvm.struct<(i32)>) -> i32
%v65 = llvm.load %v54 : !llvm.ptr -> !llvm.struct<(i32)>
%v66 = arith.constant 2 : i32
%v67 = func.call @Square_Shape_scaled(%v65, %v66) : (!llvm.struct<(i32)>, i32) -> i32
%v68 = llvm.call @printf(%v62, %v64, %v67) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32, i32) -> i32
%v69 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v70 = llvm.load %v61 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v71 = func.call @Rect_Shape_area(%v70) : (!llvm.struct<(i32, i32)>) -> i32
%v72 = llvm.load %v61 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v73 = arith.constant 3 : i32
%v74 = func.call @Rect_Shape_scaled(%v72, %v73) : (!llvm.struct<(i32, i32)>, i32) -> i32
%v75 = llvm.call @printf(%v69, %v71, %v74) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32, i32) -> i32
%v76 = arith.constant 0 : i32
func.return %v76 : i32
}
}
