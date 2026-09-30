module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\n\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_1("%f\n\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
// Struct: Point
// Fields:
//   x: i32
//   y: i32
//   w: f64
func.func @moved(%arg0: !llvm.struct<(i32, i32, f64)>, %arg1: i32) -> !llvm.struct<(i32, i32, f64)> {
%v1 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v2 = llvm.extractvalue %arg0[0] : !llvm.struct<(i32, i32, f64)>
%v3 = llvm.insertvalue %v2, %v1[0] : !llvm.struct<(i32, i32, f64)>
%v4 = llvm.extractvalue %arg0[1] : !llvm.struct<(i32, i32, f64)>
%v5 = llvm.insertvalue %v4, %v3[1] : !llvm.struct<(i32, i32, f64)>
%v6 = llvm.extractvalue %arg0[2] : !llvm.struct<(i32, i32, f64)>
%v7 = llvm.insertvalue %v6, %v5[2] : !llvm.struct<(i32, i32, f64)>
%v8 = llvm.mlir.constant(1 : i64) : i64
%v9 = llvm.alloca %v8 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v7, %v9 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v10 = llvm.load %v9 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v11 = llvm.load %v9 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v12 = llvm.getelementptr %v9[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v13 = llvm.load %v12 : !llvm.ptr -> i32
%v14 = arith.addi %v13, %arg1 : i32
%v15 = llvm.insertvalue %v14, %v10[0] : !llvm.struct<(i32, i32, f64)>
%v16 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v17 = llvm.extractvalue %v15[0] : !llvm.struct<(i32, i32, f64)>
%v18 = llvm.insertvalue %v17, %v16[0] : !llvm.struct<(i32, i32, f64)>
%v19 = llvm.extractvalue %v15[1] : !llvm.struct<(i32, i32, f64)>
%v20 = llvm.insertvalue %v19, %v18[1] : !llvm.struct<(i32, i32, f64)>
%v21 = llvm.extractvalue %v15[2] : !llvm.struct<(i32, i32, f64)>
%v22 = llvm.insertvalue %v21, %v20[2] : !llvm.struct<(i32, i32, f64)>
%v23 = llvm.mlir.constant(1 : i64) : i64
%v24 = llvm.alloca %v23 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v22, %v24 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v25 = llvm.load %v24 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
func.return %v25 : !llvm.struct<(i32, i32, f64)>
}
func.func @make() -> !llvm.struct<(i32, i32, f64)> {
%v26 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v27 = arith.constant 1 : i32
%v28 = llvm.insertvalue %v27, %v26[0] : !llvm.struct<(i32, i32, f64)>
%v29 = arith.constant 2 : i32
%v30 = llvm.insertvalue %v29, %v28[1] : !llvm.struct<(i32, i32, f64)>
%v31 = arith.constant 0.5 : f32
%v32 = arith.extf %v31 : f32 to f64
%v33 = llvm.insertvalue %v32, %v30[2] : !llvm.struct<(i32, i32, f64)>
%v34 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v35 = llvm.extractvalue %v33[0] : !llvm.struct<(i32, i32, f64)>
%v36 = llvm.insertvalue %v35, %v34[0] : !llvm.struct<(i32, i32, f64)>
%v37 = llvm.extractvalue %v33[1] : !llvm.struct<(i32, i32, f64)>
%v38 = llvm.insertvalue %v37, %v36[1] : !llvm.struct<(i32, i32, f64)>
%v39 = llvm.extractvalue %v33[2] : !llvm.struct<(i32, i32, f64)>
%v40 = llvm.insertvalue %v39, %v38[2] : !llvm.struct<(i32, i32, f64)>
%v41 = llvm.mlir.constant(1 : i64) : i64
%v42 = llvm.alloca %v41 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v40, %v42 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v43 = llvm.load %v42 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
func.return %v43 : !llvm.struct<(i32, i32, f64)>
}
func.func @main() -> i32 {
%v44 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v45 = arith.constant 3 : i32
%v46 = llvm.insertvalue %v45, %v44[0] : !llvm.struct<(i32, i32, f64)>
%v47 = arith.constant 4 : i32
%v48 = llvm.insertvalue %v47, %v46[1] : !llvm.struct<(i32, i32, f64)>
%v49 = arith.constant 1.5 : f32
%v50 = arith.extf %v49 : f32 to f64
%v51 = llvm.insertvalue %v50, %v48[2] : !llvm.struct<(i32, i32, f64)>
%v52 = llvm.mlir.constant(1 : i64) : i64
%v53 = llvm.alloca %v52 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v51, %v53 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v54 = llvm.load %v53 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v55 = arith.constant 40 : i32
%v56 = llvm.insertvalue %v55, %v54[1] : !llvm.struct<(i32, i32, f64)>
%v57 = llvm.mlir.constant(1 : i64) : i64
%v58 = llvm.alloca %v57 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v56, %v58 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v59 = arith.constant 10 : i32
%v60 = llvm.load %v58 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v61 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v62 = llvm.extractvalue %v60[0] : !llvm.struct<(i32, i32, f64)>
%v63 = llvm.insertvalue %v62, %v61[0] : !llvm.struct<(i32, i32, f64)>
%v64 = llvm.extractvalue %v60[1] : !llvm.struct<(i32, i32, f64)>
%v65 = llvm.insertvalue %v64, %v63[1] : !llvm.struct<(i32, i32, f64)>
%v66 = llvm.extractvalue %v60[2] : !llvm.struct<(i32, i32, f64)>
%v67 = llvm.insertvalue %v66, %v65[2] : !llvm.struct<(i32, i32, f64)>
%v68 = func.call @moved(%v67, %v59) : (!llvm.struct<(i32, i32, f64)>, i32) -> !llvm.struct<(i32, i32, f64)>
%v69 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v70 = llvm.extractvalue %v68[0] : !llvm.struct<(i32, i32, f64)>
%v71 = llvm.insertvalue %v70, %v69[0] : !llvm.struct<(i32, i32, f64)>
%v72 = llvm.extractvalue %v68[1] : !llvm.struct<(i32, i32, f64)>
%v73 = llvm.insertvalue %v72, %v71[1] : !llvm.struct<(i32, i32, f64)>
%v74 = llvm.extractvalue %v68[2] : !llvm.struct<(i32, i32, f64)>
%v75 = llvm.insertvalue %v74, %v73[2] : !llvm.struct<(i32, i32, f64)>
%v76 = llvm.mlir.constant(1 : i64) : i64
%v77 = llvm.alloca %v76 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v75, %v77 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v78 = llvm.load %v77 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v79 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v80 = llvm.extractvalue %v67[0] : !llvm.struct<(i32, i32, f64)>
%v81 = llvm.insertvalue %v80, %v79[0] : !llvm.struct<(i32, i32, f64)>
%v82 = llvm.extractvalue %v67[1] : !llvm.struct<(i32, i32, f64)>
%v83 = llvm.insertvalue %v82, %v81[1] : !llvm.struct<(i32, i32, f64)>
%v84 = llvm.extractvalue %v67[2] : !llvm.struct<(i32, i32, f64)>
%v85 = llvm.insertvalue %v84, %v83[2] : !llvm.struct<(i32, i32, f64)>
%v86 = llvm.mlir.constant(1 : i64) : i64
%v87 = llvm.alloca %v86 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v85, %v87 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v88 = llvm.load %v87 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
llvm.store %v88, %v58 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v89 = llvm.mlir.constant(1 : i64) : i64
%v90 = llvm.alloca %v89 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v78, %v90 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v91 = func.call @make() : () -> !llvm.struct<(i32, i32, f64)>
%v92 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v93 = llvm.extractvalue %v91[0] : !llvm.struct<(i32, i32, f64)>
%v94 = llvm.insertvalue %v93, %v92[0] : !llvm.struct<(i32, i32, f64)>
%v95 = llvm.extractvalue %v91[1] : !llvm.struct<(i32, i32, f64)>
%v96 = llvm.insertvalue %v95, %v94[1] : !llvm.struct<(i32, i32, f64)>
%v97 = llvm.extractvalue %v91[2] : !llvm.struct<(i32, i32, f64)>
%v98 = llvm.insertvalue %v97, %v96[2] : !llvm.struct<(i32, i32, f64)>
%v99 = llvm.mlir.constant(1 : i64) : i64
%v100 = llvm.alloca %v99 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v98, %v100 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v101 = llvm.load %v100 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v102 = arith.constant 2 : i32
%v103 = arith.sitofp %v102 : i32 to f64
%v104 = llvm.insertvalue %v103, %v101[2] : !llvm.struct<(i32, i32, f64)>
%v105 = llvm.load %v90 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v106 = llvm.getelementptr %v90[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v107 = llvm.load %v106 : !llvm.ptr -> i32
%v108 = arith.constant 1 : i32
%v109 = arith.addi %v107, %v108 : i32
%v110 = llvm.insertvalue %v109, %v104[1] : !llvm.struct<(i32, i32, f64)>
%v111 = llvm.mlir.constant(1 : i64) : i64
%v112 = llvm.alloca %v111 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v110, %v112 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v113 = llvm.load %v58 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v114 = llvm.getelementptr %v58[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v115 = llvm.load %v114 : !llvm.ptr -> i32
%v116 = llvm.load %v58 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v117 = llvm.getelementptr %v58[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v118 = llvm.load %v117 : !llvm.ptr -> i32
%v119 = arith.addi %v115, %v118 : i32
%v120 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v121 = llvm.call @printf(%v120, %v119) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v122 = arith.constant 0 : i32
%v123 = llvm.load %v90 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v124 = llvm.getelementptr %v90[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v125 = llvm.load %v124 : !llvm.ptr -> i32
%v126 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v127 = llvm.call @printf(%v126, %v125) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v128 = arith.constant 0 : i32
%v129 = llvm.load %v112 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v130 = llvm.getelementptr %v112[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v131 = llvm.load %v130 : !llvm.ptr -> f64
%v132 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v133 = llvm.call @printf(%v132, %v131) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v134 = arith.constant 0 : i32
%v135 = llvm.load %v112 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v136 = llvm.getelementptr %v112[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v137 = llvm.load %v136 : !llvm.ptr -> i32
%v138 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v139 = llvm.call @printf(%v138, %v137) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v140 = arith.constant 0 : i32
%v141 = arith.constant 0 : i32
func.return %v141 : i32
}
}
