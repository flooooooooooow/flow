module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
// Struct: Pair_i32_f32
// Fields:
//   first: i32
//   second: f32
// Struct: Box_i32
// Fields:
//   value: i32
func.func @identity_i32(%arg0: i32) -> i32 {
func.return %arg0 : i32
}
func.func @box_make_i32(%arg0: i32) -> !llvm.struct<(i32)> {
%v1 = llvm.mlir.undef : !llvm.struct<(i32)>
%v2 = llvm.insertvalue %arg0, %v1[0] : !llvm.struct<(i32)>
%v3 = llvm.mlir.undef : !llvm.struct<(i32)>
%v4 = llvm.extractvalue %v2[0] : !llvm.struct<(i32)>
%v5 = llvm.insertvalue %v4, %v3[0] : !llvm.struct<(i32)>
%v6 = llvm.mlir.constant(1 : i64) : i64
%v7 = llvm.alloca %v6 x !llvm.struct<(i32)> : (i64) -> !llvm.ptr
llvm.store %v5, %v7 : !llvm.struct<(i32)>, !llvm.ptr
%v8 = llvm.load %v7 : !llvm.ptr -> !llvm.struct<(i32)>
func.return %v8 : !llvm.struct<(i32)>
}
// Struct: Stats
// Fields:
//   doubled: i32
//   squared: i32
func.func @twice(%arg0: i32) -> i32 {
%v9 = arith.constant 2 : i32
%v10 = arith.muli %arg0, %v9 : i32
func.return %v10 : i32
}
func.func @square(%arg0: i32) -> i32 {
%v11 = arith.muli %arg0, %arg0 : i32
func.return %v11 : i32
}
func.func @span_sum(%arg0: i32, %arg1: i32, %arg2: i32) -> i32 {
%v12 = func.call @__flow_sum_range(%arg0, %arg1, %arg2) : (i32, i32, i32) -> i32
func.return %v12 : i32
}
func.func @main() -> i32 {
%v13 = arith.constant 7 : i32
%v14 = func.call @box_make_i32(%v13) : (i32) -> !llvm.struct<(i32)>
%v15 = llvm.mlir.undef : !llvm.struct<(i32)>
%v16 = llvm.extractvalue %v14[0] : !llvm.struct<(i32)>
%v17 = llvm.insertvalue %v16, %v15[0] : !llvm.struct<(i32)>
%v18 = llvm.mlir.constant(1 : i64) : i64
%v19 = llvm.alloca %v18 x !llvm.struct<(i32)> : (i64) -> !llvm.ptr
llvm.store %v17, %v19 : !llvm.struct<(i32)>, !llvm.ptr
%v20 = llvm.load %v19 : !llvm.ptr -> !llvm.struct<(i32)>
%v21 = llvm.mlir.constant(1 : i64) : i64
%v22 = llvm.alloca %v21 x !llvm.struct<(i32)> : (i64) -> !llvm.ptr
llvm.store %v20, %v22 : !llvm.struct<(i32)>, !llvm.ptr
%v23 = llvm.load %v22 : !llvm.ptr -> !llvm.struct<(i32)>
%v24 = llvm.getelementptr %v22[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32)>
%v25 = llvm.load %v24 : !llvm.ptr -> i32
%v26 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v27 = llvm.call @printf(%v26, %v25) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v28 = arith.constant 0 : i32
%v29 = llvm.mlir.undef : !llvm.struct<(i32, f32)>
%v30 = arith.constant 3 : i32
%v31 = llvm.insertvalue %v30, %v29[0] : !llvm.struct<(i32, f32)>
%v32 = arith.constant 1.5 : f64
%v33 = arith.truncf %v32 : f64 to f32
%v34 = llvm.insertvalue %v33, %v31[1] : !llvm.struct<(i32, f32)>
%v35 = llvm.mlir.constant(1 : i64) : i64
%v36 = llvm.alloca %v35 x !llvm.struct<(i32, f32)> : (i64) -> !llvm.ptr
llvm.store %v34, %v36 : !llvm.struct<(i32, f32)>, !llvm.ptr
%v37 = llvm.load %v36 : !llvm.ptr -> !llvm.struct<(i32, f32)>
%v38 = llvm.getelementptr %v36[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, f32)>
%v39 = llvm.load %v38 : !llvm.ptr -> i32
%v40 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v41 = llvm.call @printf(%v40, %v39) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v42 = arith.constant 0 : i32
%v43 = arith.constant 41 : i32
%v44 = func.call @identity_i32(%v43) : (i32) -> i32
%v45 = arith.constant 1 : i32
%v46 = arith.addi %v44, %v45 : i32
%v47 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v48 = llvm.call @printf(%v47, %v46) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v49 = arith.constant 0 : i32
%v50 = arith.constant 6 : i32
%v51 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v52 = func.call @twice(%v50) : (i32) -> i32
%v53 = llvm.insertvalue %v52, %v51[0] : !llvm.struct<(i32, i32)>
%v54 = func.call @square(%v50) : (i32) -> i32
%v55 = llvm.insertvalue %v54, %v53[1] : !llvm.struct<(i32, i32)>
%v56 = llvm.mlir.constant(1 : i64) : i64
%v57 = llvm.alloca %v56 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v55, %v57 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v58 = llvm.load %v57 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v59 = llvm.getelementptr %v57[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v60 = llvm.load %v59 : !llvm.ptr -> i32
%v61 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v62 = llvm.call @printf(%v61, %v60) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v63 = arith.constant 0 : i32
%v64 = llvm.load %v57 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v65 = llvm.getelementptr %v57[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v66 = llvm.load %v65 : !llvm.ptr -> i32
%v67 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v68 = llvm.call @printf(%v67, %v66) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v69 = arith.constant 0 : i32
%v70 = arith.constant 18 : i32
%v71 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v72 = llvm.call @printf(%v71, %v70) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v73 = arith.constant 0 : i32
%v74 = arith.constant 2318 : i32
%v75 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v76 = llvm.call @printf(%v75, %v74) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v77 = arith.constant 0 : i32
%v78 = arith.constant 1 : i32
%v79 = arith.constant 20 : i32
%v80 = arith.constant 4 : i32
%v81 = func.call @span_sum(%v78, %v79, %v80) : (i32, i32, i32) -> i32
%v82 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v83 = llvm.call @printf(%v82, %v81) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v84 = arith.constant 0 : i32
%v85 = arith.constant 0 : i32
func.return %v85 : i32
}
func.func @__flow_sum_range(%arg0: i32, %arg1: i32, %arg2: i32) -> i32 {
%v86 = arith.constant 0 : i32
%v87 = arith.cmpi eq, %arg2, %v86 : i32
cf.cond_br %v87, ^b1, ^b2
^b1:
%v88 = arith.constant 0 : i32
func.return %v88 : i32
^b2:
cf.br ^b3
^b3:
%v89 = arith.constant 0 : i32
%v90 = llvm.mlir.constant(1 : i64) : i64
%v91 = llvm.alloca %v90 x i32 : (i64) -> !llvm.ptr
llvm.store %v89, %v91 : i32, !llvm.ptr
%v92 = arith.constant 0 : i32
%v93 = arith.cmpi sgt, %arg2, %v92 : i32
cf.cond_br %v93, ^b4, ^b5
^b4:
%v94 = arith.cmpi sge, %arg0, %arg1 : i32
cf.cond_br %v94, ^b6, ^b7
^b6:
%v95 = arith.constant 0 : i32
func.return %v95 : i32
^b7:
cf.br ^b8
^b8:
%v96 = arith.subi %arg1, %arg0 : i32
%v97 = arith.addi %v96, %arg2 : i32
%v98 = arith.constant 1 : i32
%v99 = arith.subi %v97, %v98 : i32
%v100 = arith.divsi %v99, %arg2 : i32
llvm.store %v100, %v91 : i32, !llvm.ptr
cf.br ^b9
^b5:
%v101 = arith.cmpi sle, %arg0, %arg1 : i32
cf.cond_br %v101, ^b10, ^b11
^b10:
%v102 = arith.constant 0 : i32
func.return %v102 : i32
^b11:
cf.br ^b12
^b12:
%v103 = arith.subi %arg0, %arg1 : i32
%v104 = arith.constant 0 : i32
%v105 = arith.subi %v104, %arg2 : i32
%v106 = arith.addi %v103, %v105 : i32
%v107 = arith.constant 1 : i32
%v108 = arith.subi %v106, %v107 : i32
%v109 = arith.constant 0 : i32
%v110 = arith.subi %v109, %arg2 : i32
%v111 = arith.divsi %v108, %v110 : i32
llvm.store %v111, %v91 : i32, !llvm.ptr
cf.br ^b9
^b9:
%v112 = arith.constant 2 : i32
%v113 = arith.muli %v112, %arg0 : i32
%v114 = llvm.load %v91 : !llvm.ptr -> i32
%v115 = arith.constant 1 : i32
%v116 = arith.subi %v114, %v115 : i32
%v117 = arith.muli %v116, %arg2 : i32
%v118 = arith.addi %v113, %v117 : i32
%v119 = llvm.load %v91 : !llvm.ptr -> i32
%v120 = arith.constant 2 : i32
%v121 = arith.remsi %v119, %v120 : i32
%v122 = arith.constant 0 : i32
%v123 = arith.cmpi eq, %v121, %v122 : i32
cf.cond_br %v123, ^b13, ^b14
^b13:
%v124 = llvm.load %v91 : !llvm.ptr -> i32
%v125 = arith.constant 2 : i32
%v126 = arith.divsi %v124, %v125 : i32
%v127 = arith.muli %v126, %v118 : i32
func.return %v127 : i32
^b14:
cf.br ^b15
^b15:
%v128 = llvm.load %v91 : !llvm.ptr -> i32
%v129 = arith.constant 2 : i32
%v130 = arith.divsi %v118, %v129 : i32
%v131 = arith.muli %v128, %v130 : i32
func.return %v131 : i32
}
}
