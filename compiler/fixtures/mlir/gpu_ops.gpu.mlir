module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
func.func @main() -> i32 {
%v1 = arith.constant 5 : i32
%v2 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v3 = llvm.call @printf(%v2, %v1) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v4 = arith.constant 0 : i32
%v5 = arith.constant 0 : i32
func.return %v5 : i32
}
gpu.module @flow_kernels {
gpu.func @bands(%arg0: memref<?xi32>, %arg1: i32, %arg2: i32) kernel attributes {spirv.entry_point_abi = #spirv.entry_point_abi<workgroup_size = [64, 1, 1]>} {
%v6 = gpu.block_id x
%v7 = arith.index_cast %v6 : index to i32
%v8 = gpu.block_dim x
%v9 = arith.index_cast %v8 : index to i32
%v10 = gpu.thread_id x
%v11 = arith.index_cast %v10 : index to i32
%v12 = arith.muli %v7, %v9 : i32
%v13 = arith.addi %v12, %v11 : i32
%v14 = arith.constant 0 : i32
%v15 = arith.subi %v14, %v13 : i32
%v16 = arith.constant 0 : i32
%v17 = arith.cmpi eq, %v13, %v16 : i32
%v18 = arith.cmpi slt, %v13, %arg1 : i32
%v19 = arith.constant true
%v20 = arith.xori %v18, %v19 : i1
scf.if %v20 {
%v21 = arith.index_cast %v13 : i32 to index
memref.store %v15, %arg0[%v21] : memref<?xi32>
}
%v22 = arith.cmpi slt, %v13, %arg1 : i32
scf.if %v22 {
%v23 = arith.constant 1 : i32
%v24 = arith.index_cast %v13 : i32 to index
memref.store %v23, %arg0[%v24] : memref<?xi32>
} else {
%v25 = arith.cmpi slt, %v13, %arg2 : i32
scf.if %v25 {
%v26 = arith.constant 2 : i32
%v27 = arith.index_cast %v13 : i32 to index
memref.store %v26, %arg0[%v27] : memref<?xi32>
} else {
%v28 = arith.constant 3 : i32
%v29 = arith.index_cast %v13 : i32 to index
memref.store %v28, %arg0[%v29] : memref<?xi32>
}
}
gpu.return
}
}
}
