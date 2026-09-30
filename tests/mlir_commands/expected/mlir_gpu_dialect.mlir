module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\n\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
func.func @main() -> i32 {
%v1 = arith.constant 3 : i32
%v2 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v3 = llvm.call @printf(%v2, %v1) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v4 = arith.constant 0 : i32
%v5 = arith.constant 0 : i32
func.return %v5 : i32
}
gpu.module @flow_kernels {
gpu.func @saxpy(%arg0: memref<?xf32>, %arg1: memref<?xf32>, %arg2: f32, %arg3: i32) kernel attributes {spirv.entry_point_abi = #spirv.entry_point_abi<workgroup_size = [64, 1, 1]>} {
%v6 = gpu.block_id x
%v7 = arith.index_cast %v6 : index to i32
%v8 = gpu.block_dim x
%v9 = arith.index_cast %v8 : index to i32
%v10 = gpu.thread_id x
%v11 = arith.index_cast %v10 : index to i32
%v12 = arith.muli %v7, %v9 : i32
%v13 = arith.addi %v12, %v11 : i32
%v14 = arith.cmpi slt, %v13, %arg3 : i32
scf.if %v14 {
%v15 = arith.index_cast %v13 : i32 to index
%v16 = memref.load %arg0[%v15] : memref<?xf32>
%v17 = arith.mulf %arg2, %v16 : f32
%v18 = arith.index_cast %v13 : i32 to index
%v19 = memref.load %arg1[%v18] : memref<?xf32>
%v20 = arith.addf %v17, %v19 : f32
%v21 = arith.index_cast %v13 : i32 to index
memref.store %v20, %arg1[%v21] : memref<?xf32>
} else {
// return ignored in gpu kernel
}
gpu.return
}
gpu.func @row_sum(%arg0: memref<?xf32>, %arg1: memref<?xf32>, %arg2: i32) kernel attributes {spirv.entry_point_abi = #spirv.entry_point_abi<workgroup_size = [64, 1, 1]>} {
%v22 = gpu.block_id x
%v23 = arith.index_cast %v22 : index to i32
%v24 = arith.constant 0.0 : f32
%v25 = arith.constant 0 : i32
%v26 = arith.index_cast %v25 : i32 to index
%v27 = arith.index_cast %arg2 : i32 to index
%v28 = arith.constant 1 : index
%v29 = scf.for %v30 = %v26 to %v27 step %v28 iter_args(%v31 = %v24) -> (f32) {
%v32 = arith.index_cast %v30 : index to i32
%v33 = arith.muli %v23, %arg2 : i32
%v34 = arith.addi %v33, %v32 : i32
%v35 = arith.index_cast %v34 : i32 to index
%v36 = memref.load %arg0[%v35] : memref<?xf32>
%v37 = arith.addf %v31, %v36 : f32
scf.yield %v37 : f32
}
gpu.barrier
%v38 = arith.index_cast %v23 : i32 to index
memref.store %v29, %arg1[%v38] : memref<?xf32>
gpu.return
}
gpu.func @tiles(%arg0: memref<?xi32>) kernel attributes {spirv.entry_point_abi = #spirv.entry_point_abi<workgroup_size = [64, 1, 1]>} {
%v39 = gpu.thread_id x
%v40 = arith.index_cast %v39 : index to i32
%v41 = gpu.block_dim x
%v42 = arith.index_cast %v41 : index to i32
%v43 = arith.constant 1 : i32
%v44 = arith.subi %v42, %v43 : i32
%v45 = arith.index_cast %v40 : i32 to index
memref.store %v44, %arg0[%v45] : memref<?xi32>
gpu.return
}
}
}
