module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("gpu_kernels: use `flow gpu lib/stdlib/gpu_kernels.flow` to emit shaders\0A\00") {addr_space = 0 : i32} : !llvm.array<73 x i8>
func.func @main() -> i32 {
%v1 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v2 = llvm.call @printf(%v1) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3 = arith.constant 0 : i32
%v4 = arith.constant 0 : i32
func.return %v4 : i32
}
gpu.module @flow_kernels {
gpu.func @gpu_vector_add(%arg0: memref<?xf32>, %arg1: memref<?xf32>, %arg2: memref<?xf32>, %arg3: i32) kernel attributes {spirv.entry_point_abi = #spirv.entry_point_abi<workgroup_size = [64, 1, 1]>} {
%v5 = gpu.block_id x
%v6 = arith.index_cast %v5 : index to i32
%v7 = gpu.block_dim x
%v8 = arith.index_cast %v7 : index to i32
%v9 = gpu.thread_id x
%v10 = arith.index_cast %v9 : index to i32
%v11 = arith.muli %v6, %v8 : i32
%v12 = arith.addi %v11, %v10 : i32
%v13 = arith.cmpi slt, %v12, %arg3 : i32
scf.if %v13 {
%v14 = arith.index_cast %v12 : i32 to index
%v15 = memref.load %arg0[%v14] : memref<?xf32>
%v16 = arith.index_cast %v12 : i32 to index
%v17 = memref.load %arg1[%v16] : memref<?xf32>
%v18 = arith.addf %v15, %v17 : f32
%v19 = arith.index_cast %v12 : i32 to index
memref.store %v18, %arg2[%v19] : memref<?xf32>
}
gpu.return
}
gpu.func @gpu_scale(%arg0: memref<?xf32>, %arg1: memref<?xf32>, %arg2: i32, %arg3: f32) kernel attributes {spirv.entry_point_abi = #spirv.entry_point_abi<workgroup_size = [64, 1, 1]>} {
%v20 = gpu.block_id x
%v21 = arith.index_cast %v20 : index to i32
%v22 = gpu.block_dim x
%v23 = arith.index_cast %v22 : index to i32
%v24 = gpu.thread_id x
%v25 = arith.index_cast %v24 : index to i32
%v26 = arith.muli %v21, %v23 : i32
%v27 = arith.addi %v26, %v25 : i32
%v28 = arith.cmpi slt, %v27, %arg2 : i32
scf.if %v28 {
%v29 = arith.index_cast %v27 : i32 to index
%v30 = memref.load %arg0[%v29] : memref<?xf32>
%v31 = arith.mulf %v30, %arg3 : f32
%v32 = arith.index_cast %v27 : i32 to index
memref.store %v31, %arg1[%v32] : memref<?xf32>
}
gpu.return
}
gpu.func @gpu_matmul_row(%arg0: memref<?xf32>, %arg1: memref<?xf32>, %arg2: memref<?xf32>, %arg3: i32, %arg4: i32, %arg5: i32) kernel attributes {spirv.entry_point_abi = #spirv.entry_point_abi<workgroup_size = [64, 1, 1]>} {
%v33 = gpu.block_id x
%v34 = arith.index_cast %v33 : index to i32
%v35 = gpu.block_dim x
%v36 = arith.index_cast %v35 : index to i32
%v37 = gpu.thread_id x
%v38 = arith.index_cast %v37 : index to i32
%v39 = arith.muli %v34, %v36 : i32
%v40 = arith.addi %v39, %v38 : i32
%v41 = arith.cmpi slt, %v40, %arg3 : i32
scf.if %v41 {
%v42 = arith.constant 0 : i32
%v43 = arith.index_cast %v42 : i32 to index
%v44 = arith.index_cast %arg5 : i32 to index
%v45 = arith.constant 1 : index
scf.for %v46 = %v43 to %v44 step %v45 {
%v47 = arith.index_cast %v46 : index to i32
%v48 = arith.constant 0.0 : f32
%v49 = arith.constant 0 : i32
%v50 = arith.index_cast %v49 : i32 to index
%v51 = arith.index_cast %arg4 : i32 to index
%v52 = arith.constant 1 : index
%v53 = scf.for %v54 = %v50 to %v51 step %v52 iter_args(%v55 = %v48) -> (f32) {
%v56 = arith.index_cast %v54 : index to i32
%v57 = arith.muli %v40, %arg4 : i32
%v58 = arith.addi %v57, %v56 : i32
%v59 = arith.index_cast %v58 : i32 to index
%v60 = memref.load %arg0[%v59] : memref<?xf32>
%v61 = arith.muli %v56, %arg5 : i32
%v62 = arith.addi %v61, %v47 : i32
%v63 = arith.index_cast %v62 : i32 to index
%v64 = memref.load %arg1[%v63] : memref<?xf32>
%v65 = arith.mulf %v60, %v64 : f32
%v66 = arith.addf %v55, %v65 : f32
scf.yield %v66 : f32
}
%v67 = arith.muli %v40, %arg5 : i32
%v68 = arith.addi %v67, %v47 : i32
%v69 = arith.index_cast %v68 : i32 to index
memref.store %v53, %arg2[%v69] : memref<?xf32>
}
}
gpu.return
}
}
}
