module {
func.func @run_fusion(%arg0: memref<?xf32>, %arg1: memref<?xf32>, %arg2: memref<?xf32>) -> () {
%v1 = llvm.mlir.constant(1 : i64) : i64
%v2 = llvm.alloca %v1 x f32 : (i64) -> !llvm.ptr
%v3 = arith.constant 0 : i32
%v4 = arith.constant 100 : i32
%v5 = arith.index_cast %v3 : i32 to index
%v6 = arith.index_cast %v4 : i32 to index
affine.for %v7 = %v5 to %v6 step 1 {
%v8 = arith.constant 1.0 : f64
%v9 = arith.truncf %v8 : f64 to f32
memref.store %v9, %arg0[%v7] : memref<?xf32>
%v10 = arith.constant 2.0 : f64
%v11 = arith.truncf %v10 : f64 to f32
memref.store %v11, %arg1[%v7] : memref<?xf32>
}
%v12 = arith.constant 0 : i32
%v13 = arith.constant 100 : i32
%v14 = arith.index_cast %v12 : i32 to index
%v15 = arith.index_cast %v13 : i32 to index
affine.for %v16 = %v14 to %v15 step 1 {
%v17 = memref.load %arg0[%v16] : memref<?xf32>
%v18 = memref.load %arg1[%v16] : memref<?xf32>
%v19 = arith.addf %v17, %v18 : f32
%v20 = arith.constant 2.0 : f64
%v21 = arith.extf %v19 : f32 to f64
%v22 = arith.mulf %v21, %v20 : f64
%v23 = arith.truncf %v22 : f64 to f32
memref.store %v23, %arg2[%v16] : memref<?xf32>
}
%v24 = arith.constant 0.0 : f64
%v25 = arith.truncf %v24 : f64 to f32
llvm.store %v25, %v2 : f32, !llvm.ptr
%v26 = arith.constant 0 : i32
%v27 = arith.constant 100 : i32
%v28 = arith.index_cast %v26 : i32 to index
%v29 = arith.index_cast %v27 : i32 to index
affine.for %v30 = %v28 to %v29 step 1 {
%v31 = llvm.load %v2 : !llvm.ptr -> f32
%v32 = memref.load %arg2[%v30] : memref<?xf32>
%v33 = arith.addf %v31, %v32 : f32
llvm.store %v33, %v2 : f32, !llvm.ptr
}
func.return
}
}
