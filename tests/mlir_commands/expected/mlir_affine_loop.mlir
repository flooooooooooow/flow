module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%lld\0A\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
func.func @fill(%arg0: memref<?xf32>, %arg1: i32) -> () {
%v1 = arith.constant 0 : i32
%v2 = arith.constant 16 : i32
%v3 = arith.index_cast %v1 : i32 to index
%v4 = arith.index_cast %v2 : i32 to index
affine.for %v5 = %v3 to %v4 step 1 {
%v6 = arith.constant 1.0 : f64
%v7 = arith.truncf %v6 : f64 to f32
memref.store %v7, %arg0[%v5] : memref<?xf32>
}
func.return
}
func.func @count() -> () {
%v8 = arith.constant 0 : i32
%v9 = arith.constant 4 : i32
%v10 = arith.index_cast %v8 : i32 to index
%v11 = arith.index_cast %v9 : i32 to index
affine.for %v12 = %v10 to %v11 step 1 {
%v13 = arith.index_cast %v12 : index to i64
%v14 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v15 = llvm.call @printf(%v14, %v13) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v16 = arith.constant 0 : i32
}
func.return
}
func.func @fill_dynamic(%arg0: memref<?xf32>, %arg1: i32) -> () {
%v17 = arith.constant 0 : i32
%v18 = arith.index_cast %v17 : i32 to index
%v19 = arith.index_cast %arg1 : i32 to index
affine.for %v20 = %v18 to %v19 step 1 {
%v21 = arith.constant 2.0 : f64
%v22 = arith.truncf %v21 : f64 to f32
memref.store %v22, %arg0[%v20] : memref<?xf32>
}
func.return
}
func.func @fill_parallel(%arg0: memref<?xf32>, %arg1: i32) -> () {
%v23 = arith.constant 0 : i32
%v24 = arith.index_cast %v23 : i32 to index
%v25 = arith.index_cast %arg1 : i32 to index
affine.parallel (%v26) = (%v24) to (%v25) step (1) {
%v27 = arith.constant 3.0 : f64
%v28 = arith.truncf %v27 : f64 to f32
memref.store %v28, %arg0[%v26] : memref<?xf32>
}
func.return
}
func.func @fill_tiled(%arg0: !llvm.ptr) -> () {
%v29 = arith.constant 0 : i32
%v30 = arith.constant 8 : i32
%v31 = arith.index_cast %v29 : i32 to index
%v32 = arith.index_cast %v30 : i32 to index
affine.for %v33 = %v31 to %v32 step 1 {
%v34 = arith.constant 4.0 : f64
%v35 = arith.truncf %v34 : f64 to f32
%v36 = arith.index_cast %v33 : index to i64
%v37 = llvm.getelementptr %arg0[0, %v36] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<8 x f32>
llvm.store %v35, %v37 : f32, !llvm.ptr
}
func.return
}
func.func @fill_tiled_offset(%arg0: !llvm.ptr) -> () {
%v38 = arith.constant 2 : i32
%v39 = arith.constant 10 : i32
%v40 = arith.index_cast %v38 : i32 to index
%v41 = arith.index_cast %v39 : i32 to index
affine.for %v42 = %v40 to %v41 step 1 {
%v43 = arith.constant 5.0 : f64
%v44 = arith.truncf %v43 : f64 to f32
%v45 = arith.index_cast %v42 : index to i64
%v46 = llvm.getelementptr %arg0[0, %v45] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<12 x f32>
llvm.store %v44, %v46 : f32, !llvm.ptr
}
func.return
}
func.func @fill_multitiled(%arg0: !llvm.ptr) -> () {
%v47 = arith.constant 0 : i32
%v48 = arith.constant 12 : i32
%v49 = arith.index_cast %v47 : i32 to index
%v50 = arith.index_cast %v48 : i32 to index
affine.for %v51 = %v49 to %v50 step 1 {
%v52 = arith.constant 6.0 : f64
%v53 = arith.truncf %v52 : f64 to f32
%v54 = arith.index_cast %v51 : index to i64
%v55 = llvm.getelementptr %arg0[0, %v54] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<12 x f32>
llvm.store %v53, %v55 : f32, !llvm.ptr
}
func.return
}
}
