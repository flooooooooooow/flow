module {
func.func @run_fusion(%arg0: memref<?xf32>, %arg1: memref<?xf32>, %arg2: memref<?xf32>) -> () {
%v1 = arith.constant 0 : i32
%v2 = arith.constant 100 : i32
%v3 = arith.index_cast %v1 : i32 to index
%v4 = arith.index_cast %v2 : i32 to index
affine.for %v5 = %v3 to %v4 step 1 {
%v6 = arith.constant 1.0 : f64
%v7 = arith.truncf %v6 : f64 to f32
memref.store %v7, %arg0[%v5] : memref<?xf32>
%v8 = arith.constant 2.0 : f64
%v9 = arith.truncf %v8 : f64 to f32
memref.store %v9, %arg1[%v5] : memref<?xf32>
}
%v10 = arith.constant 0 : i32
%v11 = arith.constant 100 : i32
%v12 = arith.index_cast %v10 : i32 to index
%v13 = arith.index_cast %v11 : i32 to index
affine.for %v14 = %v12 to %v13 step 1 {
%v15 = memref.load %arg0[%v14] : memref<?xf32>
%v16 = memref.load %arg1[%v14] : memref<?xf32>
%v17 = arith.addf %v15, %v16 : f32
%v18 = arith.constant 2.0 : f64
%v19 = arith.extf %v17 : f32 to f64
%v20 = arith.mulf %v19, %v18 : f64
%v21 = arith.truncf %v20 : f64 to f32
memref.store %v21, %arg2[%v14] : memref<?xf32>
}
%v22 = arith.constant 0.0 : f64
%v23 = arith.truncf %v22 : f64 to f32
%v24 = llvm.mlir.constant(1 : i64) : i64
%v25 = llvm.alloca %v24 x f32 : (i64) -> !llvm.ptr
llvm.store %v23, %v25 : f32, !llvm.ptr
%v26 = arith.constant 0 : i32
%v27 = arith.constant 100 : i32
%v28 = arith.index_cast %v26 : i32 to index
%v29 = arith.index_cast %v27 : i32 to index
affine.for %v30 = %v28 to %v29 step 1 {
%v31 = llvm.load %v25 : !llvm.ptr -> f32
%v32 = memref.load %arg2[%v30] : memref<?xf32>
%v33 = arith.addf %v31, %v32 : f32
llvm.store %v33, %v25 : f32, !llvm.ptr
}
func.return
}
}
