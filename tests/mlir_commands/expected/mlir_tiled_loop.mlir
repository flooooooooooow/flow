module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%lld\0A\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
func.func @fill(%arg0: memref<?xf32>, %arg1: i32) -> () {
%v1 = arith.constant 0 : index
%v2 = arith.constant 16 : i32
%v3 = arith.index_cast %v2 : i32 to index
%v4 = arith.constant 4 : index
affine.for %v5 = %v1 to %v3 step 4 {
%v6 = arith.subi %v3, %v5 : index
%v7 = affine.min affine_map<(d0) -> (d0, 4)> (%v6)
affine.for %v8 = %v1 to %v7 step 1 {
%v9 = arith.addi %v5, %v8 : index
%v10 = arith.constant 1.0 : f64
%v11 = arith.truncf %v10 : f64 to f32
memref.store %v11, %arg0[%v9] : memref<?xf32>
}
}
func.return
}
func.func @count() -> () {
%v12 = arith.constant 0 : index
%v13 = arith.constant 4 : i32
%v14 = arith.index_cast %v13 : i32 to index
%v15 = arith.constant 4 : index
affine.for %v16 = %v12 to %v14 step 4 {
%v17 = arith.subi %v14, %v16 : index
%v18 = affine.min affine_map<(d0) -> (d0, 4)> (%v17)
affine.for %v19 = %v12 to %v18 step 1 {
%v20 = arith.addi %v16, %v19 : index
%v21 = arith.index_cast %v20 : index to i64
%v22 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v23 = llvm.call @printf(%v22, %v21) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v24 = arith.constant 0 : i32
}
}
func.return
}
func.func @fill_dynamic(%arg0: memref<?xf32>, %arg1: i32) -> () {
%v25 = arith.constant 0 : index
%v26 = arith.index_cast %arg1 : i32 to index
%v27 = arith.constant 4 : index
affine.for %v28 = %v25 to %v26 step 4 {
%v29 = arith.subi %v26, %v28 : index
%v30 = affine.min affine_map<(d0) -> (d0, 4)> (%v29)
affine.for %v31 = %v25 to %v30 step 1 {
%v32 = arith.addi %v28, %v31 : index
%v33 = arith.constant 2.0 : f64
%v34 = arith.truncf %v33 : f64 to f32
memref.store %v34, %arg0[%v32] : memref<?xf32>
}
}
func.return
}
func.func @fill_parallel(%arg0: memref<?xf32>, %arg1: i32) -> () {
%v35 = arith.constant 0 : i32
%v36 = arith.index_cast %v35 : i32 to index
%v37 = arith.index_cast %arg1 : i32 to index
affine.parallel (%v38) = (%v36) to (%v37) step (1) {
%v39 = arith.constant 3.0 : f64
%v40 = arith.truncf %v39 : f64 to f32
memref.store %v40, %arg0[%v38] : memref<?xf32>
}
func.return
}
func.func @fill_tiled(%arg0: !llvm.ptr) -> () {
%v41 = arith.constant 0 : index
%v42 = arith.constant 8 : i32
%v43 = arith.index_cast %v42 : i32 to index
%v44 = arith.constant 4 : index
affine.for %v45 = %v41 to %v43 step 4 {
%v46 = arith.subi %v43, %v45 : index
%v47 = affine.min affine_map<(d0) -> (d0, 4)> (%v46)
affine.for %v48 = %v41 to %v47 step 1 {
%v49 = arith.addi %v45, %v48 : index
%v50 = arith.constant 4.0 : f64
%v51 = arith.truncf %v50 : f64 to f32
%v52 = arith.index_cast %v49 : index to i64
%v53 = llvm.getelementptr %arg0[0, %v52] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<8 x f32>
llvm.store %v51, %v53 : f32, !llvm.ptr
}
}
func.return
}
}
