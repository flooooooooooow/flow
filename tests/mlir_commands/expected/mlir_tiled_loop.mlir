module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%lld\0A\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
func.func @fill(%arg0: memref<?xf32>, %arg1: i32) -> () {
%v1 = arith.constant 0 : index
%v2 = arith.constant 16 : index
%v3 = arith.constant 4 : index
affine.for %v4 = %v1 to %v2 step 4 {
affine.for %v5 = %v1 to %v3 step 1 {
%v6 = arith.addi %v4, %v5 : index
%v7 = arith.constant 1.0 : f64
%v8 = arith.truncf %v7 : f64 to f32
memref.store %v8, %arg0[%v6] : memref<?xf32>
}
}
func.return
}
func.func @count() -> () {
%v9 = arith.constant 0 : index
%v10 = arith.constant 4 : index
%v11 = arith.constant 4 : index
affine.for %v12 = %v9 to %v10 step 4 {
affine.for %v13 = %v9 to %v11 step 1 {
%v14 = arith.addi %v12, %v13 : index
%v15 = arith.index_cast %v14 : index to i64
%v16 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v17 = llvm.call @printf(%v16, %v15) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v18 = arith.constant 0 : i32
}
}
func.return
}
func.func @fill_dynamic(%arg0: memref<?xf32>, %arg1: i32) -> () {
%v19 = arith.constant 0 : i32
%v20 = arith.index_cast %v19 : i32 to index
%v21 = arith.index_cast %arg1 : i32 to index
affine.for %v22 = %v20 to %v21 step 1 {
%v23 = arith.constant 2.0 : f64
%v24 = arith.truncf %v23 : f64 to f32
memref.store %v24, %arg0[%v22] : memref<?xf32>
}
func.return
}
func.func @fill_parallel(%arg0: memref<?xf32>, %arg1: i32) -> () {
%v25 = arith.constant 0 : i32
%v26 = arith.index_cast %v25 : i32 to index
%v27 = arith.index_cast %arg1 : i32 to index
affine.parallel (%v28) = (%v26) to (%v27) step (1) {
%v29 = arith.constant 3.0 : f64
%v30 = arith.truncf %v29 : f64 to f32
memref.store %v30, %arg0[%v28] : memref<?xf32>
}
func.return
}
func.func @fill_tiled(%arg0: !llvm.ptr) -> () {
%v31 = arith.constant 0 : index
%v32 = arith.constant 8 : index
%v33 = arith.constant 4 : index
affine.for %v34 = %v31 to %v32 step 4 {
affine.for %v35 = %v31 to %v33 step 1 {
%v36 = arith.addi %v34, %v35 : index
%v37 = arith.constant 4.0 : f64
%v38 = arith.truncf %v37 : f64 to f32
%v39 = arith.index_cast %v36 : index to i64
%v40 = llvm.getelementptr %arg0[0, %v39] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<8 x f32>
llvm.store %v38, %v40 : f32, !llvm.ptr
}
}
func.return
}
}
