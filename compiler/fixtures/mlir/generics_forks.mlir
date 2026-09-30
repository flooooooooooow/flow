module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\n\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
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
%v32 = arith.constant 1.5 : f32
%v33 = llvm.insertvalue %v32, %v31[1] : !llvm.struct<(i32, f32)>
%v34 = llvm.mlir.constant(1 : i64) : i64
%v35 = llvm.alloca %v34 x !llvm.struct<(i32, f32)> : (i64) -> !llvm.ptr
llvm.store %v33, %v35 : !llvm.struct<(i32, f32)>, !llvm.ptr
%v36 = llvm.load %v35 : !llvm.ptr -> !llvm.struct<(i32, f32)>
%v37 = llvm.getelementptr %v35[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, f32)>
%v38 = llvm.load %v37 : !llvm.ptr -> i32
%v39 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v40 = llvm.call @printf(%v39, %v38) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v41 = arith.constant 0 : i32
%v42 = arith.constant 41 : i32
%v43 = func.call @identity_i32(%v42) : (i32) -> i32
%v44 = arith.constant 1 : i32
%v45 = arith.addi %v43, %v44 : i32
%v46 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v47 = llvm.call @printf(%v46, %v45) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v48 = arith.constant 0 : i32
%v49 = arith.constant 6 : i32
%v50 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v51 = func.call @twice(%v49) : (i32) -> i32
%v52 = llvm.insertvalue %v51, %v50[0] : !llvm.struct<(i32, i32)>
%v53 = func.call @square(%v49) : (i32) -> i32
%v54 = llvm.insertvalue %v53, %v52[1] : !llvm.struct<(i32, i32)>
%v55 = llvm.mlir.constant(1 : i64) : i64
%v56 = llvm.alloca %v55 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v54, %v56 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v57 = llvm.load %v56 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v58 = llvm.getelementptr %v56[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v59 = llvm.load %v58 : !llvm.ptr -> i32
%v60 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v61 = llvm.call @printf(%v60, %v59) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v62 = arith.constant 0 : i32
%v63 = llvm.load %v56 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v64 = llvm.getelementptr %v56[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v65 = llvm.load %v64 : !llvm.ptr -> i32
%v66 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v67 = llvm.call @printf(%v66, %v65) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v68 = arith.constant 0 : i32
%v69 = arith.constant 18 : i32
%v70 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v71 = llvm.call @printf(%v70, %v69) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v72 = arith.constant 0 : i32
%v73 = arith.constant 2318 : i32
%v74 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v75 = llvm.call @printf(%v74, %v73) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v76 = arith.constant 0 : i32
%v77 = arith.constant 1 : i32
%v78 = arith.constant 20 : i32
%v79 = arith.constant 4 : i32
%v80 = func.call @span_sum(%v77, %v78, %v79) : (i32, i32, i32) -> i32
%v81 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v82 = llvm.call @printf(%v81, %v80) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v83 = arith.constant 0 : i32
%v84 = arith.constant 0 : i32
func.return %v84 : i32
}
func.func @__flow_sum_range(%arg0: i32, %arg1: i32, %arg2: i32) -> i32 {
%v85 = arith.constant 0 : i32
%v86 = arith.cmpi eq, %arg2, %v85 : i32
cf.cond_br %v86, ^b1, ^b2
^b1:
%v87 = arith.constant 0 : i32
func.return %v87 : i32
^b2:
cf.br ^b3
^b3:
%v88 = arith.constant 0 : i32
%v89 = llvm.mlir.constant(1 : i64) : i64
%v90 = llvm.alloca %v89 x i32 : (i64) -> !llvm.ptr
llvm.store %v88, %v90 : i32, !llvm.ptr
%v91 = arith.constant 0 : i32
%v92 = arith.cmpi sgt, %arg2, %v91 : i32
cf.cond_br %v92, ^b4, ^b5
^b4:
%v93 = arith.cmpi sge, %arg0, %arg1 : i32
cf.cond_br %v93, ^b6, ^b7
^b6:
%v94 = arith.constant 0 : i32
func.return %v94 : i32
^b7:
cf.br ^b8
^b8:
%v95 = arith.subi %arg1, %arg0 : i32
%v96 = arith.addi %v95, %arg2 : i32
%v97 = arith.constant 1 : i32
%v98 = arith.subi %v96, %v97 : i32
%v99 = arith.divsi %v98, %arg2 : i32
llvm.store %v99, %v90 : i32, !llvm.ptr
cf.br ^b9
^b5:
%v100 = arith.cmpi sle, %arg0, %arg1 : i32
cf.cond_br %v100, ^b10, ^b11
^b10:
%v101 = arith.constant 0 : i32
func.return %v101 : i32
^b11:
cf.br ^b12
^b12:
%v102 = arith.subi %arg0, %arg1 : i32
%v103 = arith.constant 0 : i32
%v104 = arith.subi %v103, %arg2 : i32
%v105 = arith.addi %v102, %v104 : i32
%v106 = arith.constant 1 : i32
%v107 = arith.subi %v105, %v106 : i32
%v108 = arith.constant 0 : i32
%v109 = arith.subi %v108, %arg2 : i32
%v110 = arith.divsi %v107, %v109 : i32
llvm.store %v110, %v90 : i32, !llvm.ptr
cf.br ^b9
^b9:
%v111 = arith.constant 2 : i32
%v112 = arith.muli %v111, %arg0 : i32
%v113 = llvm.load %v90 : !llvm.ptr -> i32
%v114 = arith.constant 1 : i32
%v115 = arith.subi %v113, %v114 : i32
%v116 = arith.muli %v115, %arg2 : i32
%v117 = arith.addi %v112, %v116 : i32
%v118 = llvm.load %v90 : !llvm.ptr -> i32
%v119 = arith.constant 2 : i32
%v120 = arith.remsi %v118, %v119 : i32
%v121 = arith.constant 0 : i32
%v122 = arith.cmpi eq, %v120, %v121 : i32
cf.cond_br %v122, ^b13, ^b14
^b13:
%v123 = llvm.load %v90 : !llvm.ptr -> i32
%v124 = arith.constant 2 : i32
%v125 = arith.divsi %v123, %v124 : i32
%v126 = arith.muli %v125, %v117 : i32
func.return %v126 : i32
^b14:
cf.br ^b15
^b15:
%v127 = llvm.load %v90 : !llvm.ptr -> i32
%v128 = arith.constant 2 : i32
%v129 = arith.divsi %v117, %v128 : i32
%v130 = arith.muli %v127, %v129 : i32
func.return %v130 : i32
}
}
