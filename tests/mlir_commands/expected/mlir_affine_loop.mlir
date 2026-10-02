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
}
