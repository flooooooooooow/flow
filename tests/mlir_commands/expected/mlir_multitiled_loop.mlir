module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%lld\0A\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
func.func @fill(%arg0: memref<?xf32>, %arg1: i32) -> () {
%v1 = arith.constant 0 : i32
%v2 = arith.index_cast %v1 : i32 to index
%v3 = arith.constant 0 : index
%v4 = arith.constant 16 : i32
%v5 = arith.index_cast %v4 : i32 to index
affine.for %v6 = %v2 to %v5 step 8 {
%v7 = arith.subi %v5, %v6 : index
%v8 = affine.min affine_map<(d0) -> (d0, 8)> (%v7)
affine.for %v9 = %v3 to %v8 step 4 {
%v10 = arith.subi %v8, %v9 : index
%v11 = affine.min affine_map<(d0) -> (d0, 4)> (%v10)
affine.for %v12 = %v3 to %v11 step 1 {
%v13 = arith.addi %v6, %v9 : index
%v14 = arith.addi %v13, %v12 : index
%v15 = arith.constant 1.0 : f64
%v16 = arith.truncf %v15 : f64 to f32
memref.store %v16, %arg0[%v14] : memref<?xf32>
}
}
}
func.return
}
func.func @count() -> () {
%v17 = arith.constant 0 : i32
%v18 = arith.index_cast %v17 : i32 to index
%v19 = arith.constant 0 : index
%v20 = arith.constant 4 : i32
%v21 = arith.index_cast %v20 : i32 to index
affine.for %v22 = %v18 to %v21 step 8 {
%v23 = arith.subi %v21, %v22 : index
%v24 = affine.min affine_map<(d0) -> (d0, 8)> (%v23)
affine.for %v25 = %v19 to %v24 step 4 {
%v26 = arith.subi %v24, %v25 : index
%v27 = affine.min affine_map<(d0) -> (d0, 4)> (%v26)
affine.for %v28 = %v19 to %v27 step 1 {
%v29 = arith.addi %v22, %v25 : index
%v30 = arith.addi %v29, %v28 : index
%v31 = arith.index_cast %v30 : index to i64
%v32 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v33 = llvm.call @printf(%v32, %v31) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v34 = arith.constant 0 : i32
}
}
}
func.return
}
func.func @fill_dynamic(%arg0: memref<?xf32>, %arg1: i32) -> () {
%v35 = arith.constant 0 : i32
%v36 = arith.index_cast %v35 : i32 to index
%v37 = arith.constant 0 : index
%v38 = arith.index_cast %arg1 : i32 to index
affine.for %v39 = %v36 to %v38 step 8 {
%v40 = arith.subi %v38, %v39 : index
%v41 = affine.min affine_map<(d0) -> (d0, 8)> (%v40)
affine.for %v42 = %v37 to %v41 step 4 {
%v43 = arith.subi %v41, %v42 : index
%v44 = affine.min affine_map<(d0) -> (d0, 4)> (%v43)
affine.for %v45 = %v37 to %v44 step 1 {
%v46 = arith.addi %v39, %v42 : index
%v47 = arith.addi %v46, %v45 : index
%v48 = arith.constant 2.0 : f64
%v49 = arith.truncf %v48 : f64 to f32
memref.store %v49, %arg0[%v47] : memref<?xf32>
}
}
}
func.return
}
func.func @fill_parallel(%arg0: memref<?xf32>, %arg1: i32) -> () {
%v50 = arith.constant 0 : i32
%v51 = arith.index_cast %v50 : i32 to index
%v52 = arith.index_cast %arg1 : i32 to index
affine.parallel (%v53) = (%v51) to (%v52) step (1) {
%v54 = arith.constant 3.0 : f64
%v55 = arith.truncf %v54 : f64 to f32
memref.store %v55, %arg0[%v53] : memref<?xf32>
}
func.return
}
func.func @fill_tiled(%arg0: !llvm.ptr) -> () {
%v56 = arith.constant 0 : i32
%v57 = arith.index_cast %v56 : i32 to index
%v58 = arith.constant 0 : index
%v59 = arith.constant 8 : i32
%v60 = arith.index_cast %v59 : i32 to index
affine.for %v61 = %v57 to %v60 step 8 {
%v62 = arith.subi %v60, %v61 : index
%v63 = affine.min affine_map<(d0) -> (d0, 8)> (%v62)
affine.for %v64 = %v58 to %v63 step 4 {
%v65 = arith.subi %v63, %v64 : index
%v66 = affine.min affine_map<(d0) -> (d0, 4)> (%v65)
affine.for %v67 = %v58 to %v66 step 1 {
%v68 = arith.addi %v61, %v64 : index
%v69 = arith.addi %v68, %v67 : index
%v70 = arith.constant 4.0 : f64
%v71 = arith.truncf %v70 : f64 to f32
%v72 = arith.index_cast %v69 : index to i64
%v73 = llvm.getelementptr %arg0[0, %v72] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<8 x f32>
llvm.store %v71, %v73 : f32, !llvm.ptr
}
}
}
func.return
}
func.func @fill_tiled_offset(%arg0: !llvm.ptr) -> () {
%v74 = arith.constant 2 : i32
%v75 = arith.index_cast %v74 : i32 to index
%v76 = arith.constant 0 : index
%v77 = arith.constant 10 : i32
%v78 = arith.index_cast %v77 : i32 to index
affine.for %v79 = %v75 to %v78 step 8 {
%v80 = arith.subi %v78, %v79 : index
%v81 = affine.min affine_map<(d0) -> (d0, 8)> (%v80)
affine.for %v82 = %v76 to %v81 step 4 {
%v83 = arith.subi %v81, %v82 : index
%v84 = affine.min affine_map<(d0) -> (d0, 4)> (%v83)
affine.for %v85 = %v76 to %v84 step 1 {
%v86 = arith.addi %v79, %v82 : index
%v87 = arith.addi %v86, %v85 : index
%v88 = arith.constant 5.0 : f64
%v89 = arith.truncf %v88 : f64 to f32
%v90 = arith.index_cast %v87 : index to i64
%v91 = llvm.getelementptr %arg0[0, %v90] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<12 x f32>
llvm.store %v89, %v91 : f32, !llvm.ptr
}
}
}
func.return
}
func.func @fill_multitiled(%arg0: !llvm.ptr) -> () {
%v92 = arith.constant 0 : i32
%v93 = arith.index_cast %v92 : i32 to index
%v94 = arith.constant 0 : index
%v95 = arith.constant 12 : i32
%v96 = arith.index_cast %v95 : i32 to index
affine.for %v97 = %v93 to %v96 step 8 {
%v98 = arith.subi %v96, %v97 : index
%v99 = affine.min affine_map<(d0) -> (d0, 8)> (%v98)
affine.for %v100 = %v94 to %v99 step 4 {
%v101 = arith.subi %v99, %v100 : index
%v102 = affine.min affine_map<(d0) -> (d0, 4)> (%v101)
affine.for %v103 = %v94 to %v102 step 1 {
%v104 = arith.addi %v97, %v100 : index
%v105 = arith.addi %v104, %v103 : index
%v106 = arith.constant 6.0 : f64
%v107 = arith.truncf %v106 : f64 to f32
%v108 = arith.index_cast %v105 : index to i64
%v109 = llvm.getelementptr %arg0[0, %v108] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<12 x f32>
llvm.store %v107, %v109 : f32, !llvm.ptr
}
}
}
func.return
}
}
