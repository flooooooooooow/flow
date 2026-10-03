module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%lld\0A\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
func.func @fill(%arg0: memref<?xf32>, %arg1: i32) -> () {
%v1 = arith.constant 0 : i32
%v2 = arith.index_cast %v1 : i32 to index
%v3 = arith.constant 0 : index
%v4 = arith.constant 16 : i32
%v5 = arith.index_cast %v4 : i32 to index
%v6 = arith.constant 4 : index
affine.for %v7 = %v2 to %v5 step 4 {
%v8 = arith.subi %v5, %v7 : index
%v9 = affine.min affine_map<(d0) -> (d0, 4)> (%v8)
affine.for %v10 = %v3 to %v9 step 1 {
%v11 = arith.addi %v7, %v10 : index
%v12 = arith.constant 1.0 : f64
%v13 = arith.truncf %v12 : f64 to f32
memref.store %v13, %arg0[%v11] : memref<?xf32>
}
}
func.return
}
func.func @count() -> () {
%v14 = arith.constant 0 : i32
%v15 = arith.index_cast %v14 : i32 to index
%v16 = arith.constant 0 : index
%v17 = arith.constant 4 : i32
%v18 = arith.index_cast %v17 : i32 to index
%v19 = arith.constant 4 : index
affine.for %v20 = %v15 to %v18 step 4 {
%v21 = arith.subi %v18, %v20 : index
%v22 = affine.min affine_map<(d0) -> (d0, 4)> (%v21)
affine.for %v23 = %v16 to %v22 step 1 {
%v24 = arith.addi %v20, %v23 : index
%v25 = arith.index_cast %v24 : index to i64
%v26 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v27 = llvm.call @printf(%v26, %v25) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v28 = arith.constant 0 : i32
}
}
func.return
}
func.func @fill_dynamic(%arg0: memref<?xf32>, %arg1: i32) -> () {
%v29 = arith.constant 0 : i32
%v30 = arith.index_cast %v29 : i32 to index
%v31 = arith.constant 0 : index
%v32 = arith.index_cast %arg1 : i32 to index
%v33 = arith.constant 4 : index
affine.for %v34 = %v30 to %v32 step 4 {
%v35 = arith.subi %v32, %v34 : index
%v36 = affine.min affine_map<(d0) -> (d0, 4)> (%v35)
affine.for %v37 = %v31 to %v36 step 1 {
%v38 = arith.addi %v34, %v37 : index
%v39 = arith.constant 2.0 : f64
%v40 = arith.truncf %v39 : f64 to f32
memref.store %v40, %arg0[%v38] : memref<?xf32>
}
}
func.return
}
func.func @fill_parallel(%arg0: memref<?xf32>, %arg1: i32) -> () {
%v41 = arith.constant 0 : i32
%v42 = arith.index_cast %v41 : i32 to index
%v43 = arith.index_cast %arg1 : i32 to index
affine.parallel (%v44) = (%v42) to (%v43) step (1) {
%v45 = arith.constant 3.0 : f64
%v46 = arith.truncf %v45 : f64 to f32
memref.store %v46, %arg0[%v44] : memref<?xf32>
}
func.return
}
func.func @fill_tiled(%arg0: !llvm.ptr) -> () {
%v47 = arith.constant 0 : i32
%v48 = arith.index_cast %v47 : i32 to index
%v49 = arith.constant 0 : index
%v50 = arith.constant 8 : i32
%v51 = arith.index_cast %v50 : i32 to index
%v52 = arith.constant 4 : index
affine.for %v53 = %v48 to %v51 step 4 {
%v54 = arith.subi %v51, %v53 : index
%v55 = affine.min affine_map<(d0) -> (d0, 4)> (%v54)
affine.for %v56 = %v49 to %v55 step 1 {
%v57 = arith.addi %v53, %v56 : index
%v58 = arith.constant 4.0 : f64
%v59 = arith.truncf %v58 : f64 to f32
%v60 = arith.index_cast %v57 : index to i64
%v61 = llvm.getelementptr %arg0[0, %v60] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<8 x f32>
llvm.store %v59, %v61 : f32, !llvm.ptr
}
}
func.return
}
func.func @fill_tiled_offset(%arg0: !llvm.ptr) -> () {
%v62 = arith.constant 2 : i32
%v63 = arith.index_cast %v62 : i32 to index
%v64 = arith.constant 0 : index
%v65 = arith.constant 10 : i32
%v66 = arith.index_cast %v65 : i32 to index
%v67 = arith.constant 4 : index
affine.for %v68 = %v63 to %v66 step 4 {
%v69 = arith.subi %v66, %v68 : index
%v70 = affine.min affine_map<(d0) -> (d0, 4)> (%v69)
affine.for %v71 = %v64 to %v70 step 1 {
%v72 = arith.addi %v68, %v71 : index
%v73 = arith.constant 5.0 : f64
%v74 = arith.truncf %v73 : f64 to f32
%v75 = arith.index_cast %v72 : index to i64
%v76 = llvm.getelementptr %arg0[0, %v75] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<12 x f32>
llvm.store %v74, %v76 : f32, !llvm.ptr
}
}
func.return
}
func.func @fill_multitiled(%arg0: !llvm.ptr) -> () {
%v77 = arith.constant 0 : i32
%v78 = arith.index_cast %v77 : i32 to index
%v79 = arith.constant 0 : index
%v80 = arith.constant 12 : i32
%v81 = arith.index_cast %v80 : i32 to index
%v82 = arith.constant 4 : index
affine.for %v83 = %v78 to %v81 step 4 {
%v84 = arith.subi %v81, %v83 : index
%v85 = affine.min affine_map<(d0) -> (d0, 4)> (%v84)
affine.for %v86 = %v79 to %v85 step 1 {
%v87 = arith.addi %v83, %v86 : index
%v88 = arith.constant 6.0 : f64
%v89 = arith.truncf %v88 : f64 to f32
%v90 = arith.index_cast %v87 : index to i64
%v91 = llvm.getelementptr %arg0[0, %v90] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<12 x f32>
llvm.store %v89, %v91 : f32, !llvm.ptr
}
}
func.return
}
}
