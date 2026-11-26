module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_1("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
// Struct: Vec2
// Fields:
//   x: f64
//   y: f64
// Struct: Body
// Fields:
//   pos: !llvm.struct<(f64, f64)>
//   vel: !llvm.struct<(f64, f64)>
//   mass: f64
//   id: i32
func.func @vec2(%arg0: f64, %arg1: f64) -> !llvm.struct<(f64, f64)> {
%v1 = llvm.mlir.constant(1 : i64) : i64
%v2 = llvm.alloca %v1 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
%v3 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v4 = llvm.insertvalue %arg0, %v3[0] : !llvm.struct<(f64, f64)>
%v5 = llvm.insertvalue %arg1, %v4[1] : !llvm.struct<(f64, f64)>
%v6 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v7 = llvm.extractvalue %v5[0] : !llvm.struct<(f64, f64)>
%v8 = llvm.insertvalue %v7, %v6[0] : !llvm.struct<(f64, f64)>
%v9 = llvm.extractvalue %v5[1] : !llvm.struct<(f64, f64)>
%v10 = llvm.insertvalue %v9, %v8[1] : !llvm.struct<(f64, f64)>
llvm.store %v10, %v2 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v11 = llvm.load %v2 : !llvm.ptr -> !llvm.struct<(f64, f64)>
func.return %v11 : !llvm.struct<(f64, f64)>
}
func.func @add(%arg0: !llvm.struct<(f64, f64)>, %arg1: !llvm.struct<(f64, f64)>) -> !llvm.struct<(f64, f64)> {
%v12 = llvm.mlir.constant(1 : i64) : i64
%v13 = llvm.alloca %v12 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
%v14 = llvm.mlir.constant(1 : i64) : i64
%v15 = llvm.alloca %v14 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
%v16 = llvm.mlir.constant(1 : i64) : i64
%v17 = llvm.alloca %v16 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
%v18 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v19 = llvm.extractvalue %arg0[0] : !llvm.struct<(f64, f64)>
%v20 = llvm.insertvalue %v19, %v18[0] : !llvm.struct<(f64, f64)>
%v21 = llvm.extractvalue %arg0[1] : !llvm.struct<(f64, f64)>
%v22 = llvm.insertvalue %v21, %v20[1] : !llvm.struct<(f64, f64)>
llvm.store %v22, %v13 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v23 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v24 = llvm.extractvalue %arg1[0] : !llvm.struct<(f64, f64)>
%v25 = llvm.insertvalue %v24, %v23[0] : !llvm.struct<(f64, f64)>
%v26 = llvm.extractvalue %arg1[1] : !llvm.struct<(f64, f64)>
%v27 = llvm.insertvalue %v26, %v25[1] : !llvm.struct<(f64, f64)>
llvm.store %v27, %v15 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v28 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v29 = llvm.load %v13 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v30 = llvm.getelementptr %v13[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v31 = llvm.load %v30 : !llvm.ptr -> f64
%v32 = llvm.load %v15 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v33 = llvm.getelementptr %v15[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v34 = llvm.load %v33 : !llvm.ptr -> f64
%v35 = arith.addf %v31, %v34 : f64
%v36 = llvm.insertvalue %v35, %v28[0] : !llvm.struct<(f64, f64)>
%v37 = llvm.load %v13 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v38 = llvm.getelementptr %v13[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v39 = llvm.load %v38 : !llvm.ptr -> f64
%v40 = llvm.load %v15 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v41 = llvm.getelementptr %v15[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v42 = llvm.load %v41 : !llvm.ptr -> f64
%v43 = arith.addf %v39, %v42 : f64
%v44 = llvm.insertvalue %v43, %v36[1] : !llvm.struct<(f64, f64)>
%v45 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v46 = llvm.extractvalue %v44[0] : !llvm.struct<(f64, f64)>
%v47 = llvm.insertvalue %v46, %v45[0] : !llvm.struct<(f64, f64)>
%v48 = llvm.extractvalue %v44[1] : !llvm.struct<(f64, f64)>
%v49 = llvm.insertvalue %v48, %v47[1] : !llvm.struct<(f64, f64)>
llvm.store %v49, %v17 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v50 = llvm.load %v17 : !llvm.ptr -> !llvm.struct<(f64, f64)>
func.return %v50 : !llvm.struct<(f64, f64)>
}
func.func @dot(%arg0: !llvm.struct<(f64, f64)>, %arg1: !llvm.struct<(f64, f64)>) -> f64 {
%v51 = llvm.mlir.constant(1 : i64) : i64
%v52 = llvm.alloca %v51 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
%v53 = llvm.mlir.constant(1 : i64) : i64
%v54 = llvm.alloca %v53 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
%v55 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v56 = llvm.extractvalue %arg0[0] : !llvm.struct<(f64, f64)>
%v57 = llvm.insertvalue %v56, %v55[0] : !llvm.struct<(f64, f64)>
%v58 = llvm.extractvalue %arg0[1] : !llvm.struct<(f64, f64)>
%v59 = llvm.insertvalue %v58, %v57[1] : !llvm.struct<(f64, f64)>
llvm.store %v59, %v52 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v60 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v61 = llvm.extractvalue %arg1[0] : !llvm.struct<(f64, f64)>
%v62 = llvm.insertvalue %v61, %v60[0] : !llvm.struct<(f64, f64)>
%v63 = llvm.extractvalue %arg1[1] : !llvm.struct<(f64, f64)>
%v64 = llvm.insertvalue %v63, %v62[1] : !llvm.struct<(f64, f64)>
llvm.store %v64, %v54 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v65 = llvm.load %v52 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v66 = llvm.getelementptr %v52[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v67 = llvm.load %v66 : !llvm.ptr -> f64
%v68 = llvm.load %v54 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v69 = llvm.getelementptr %v54[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v70 = llvm.load %v69 : !llvm.ptr -> f64
%v71 = llvm.load %v52 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v72 = llvm.getelementptr %v52[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v73 = llvm.load %v72 : !llvm.ptr -> f64
%v74 = llvm.load %v54 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v75 = llvm.getelementptr %v54[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v76 = llvm.load %v75 : !llvm.ptr -> f64
%v77 = arith.mulf %v73, %v76 : f64
%v78 = llvm.intr.fmuladd(%v67, %v70, %v77) : (f64, f64, f64) -> f64
func.return %v78 : f64
}
func.func @step(%arg0: !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, %arg1: f64) -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> {
%v79 = llvm.mlir.constant(1 : i64) : i64
%v80 = llvm.alloca %v79 x !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> : (i64) -> !llvm.ptr
%v81 = llvm.mlir.constant(1 : i64) : i64
%v82 = llvm.alloca %v81 x !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> : (i64) -> !llvm.ptr
%v83 = llvm.mlir.constant(1 : i64) : i64
%v84 = llvm.alloca %v83 x !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> : (i64) -> !llvm.ptr
%v85 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v86 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v87 = llvm.insertvalue %v86, %v85[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v88 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v89 = llvm.insertvalue %v88, %v87[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v90 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v91 = llvm.insertvalue %v90, %v89[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v92 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v93 = llvm.insertvalue %v92, %v91[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
llvm.store %v93, %v80 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v94 = llvm.load %v80 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
llvm.store %v94, %v82 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v95 = llvm.load %v80 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v96 = llvm.getelementptr %v80[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v97 = llvm.load %v96 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v98 = llvm.getelementptr %v80[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v99 = llvm.getelementptr %v98[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v100 = llvm.load %v99 : !llvm.ptr -> f64
%v101 = llvm.load %v80 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v102 = llvm.getelementptr %v80[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v103 = llvm.load %v102 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v104 = llvm.getelementptr %v80[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v105 = llvm.getelementptr %v104[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v106 = llvm.load %v105 : !llvm.ptr -> f64
%v107 = llvm.intr.fmuladd(%v106, %arg1, %v100) : (f64, f64, f64) -> f64
%v108 = llvm.getelementptr %v82[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v109 = llvm.getelementptr %v108[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
llvm.store %v107, %v109 : f64, !llvm.ptr
%v110 = llvm.load %v80 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v111 = llvm.getelementptr %v80[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v112 = llvm.load %v111 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v113 = llvm.getelementptr %v80[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v114 = llvm.getelementptr %v113[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v115 = llvm.load %v114 : !llvm.ptr -> f64
%v116 = llvm.load %v80 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v117 = llvm.getelementptr %v80[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v118 = llvm.load %v117 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v119 = llvm.getelementptr %v80[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v120 = llvm.getelementptr %v119[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v121 = llvm.load %v120 : !llvm.ptr -> f64
%v122 = llvm.intr.fmuladd(%v121, %arg1, %v115) : (f64, f64, f64) -> f64
%v123 = llvm.getelementptr %v82[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v124 = llvm.getelementptr %v123[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
llvm.store %v122, %v124 : f64, !llvm.ptr
%v125 = llvm.load %v82 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v126 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v127 = llvm.extractvalue %v125[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v128 = llvm.insertvalue %v127, %v126[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v129 = llvm.extractvalue %v125[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v130 = llvm.insertvalue %v129, %v128[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v131 = llvm.extractvalue %v125[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v132 = llvm.insertvalue %v131, %v130[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v133 = llvm.extractvalue %v125[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v134 = llvm.insertvalue %v133, %v132[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
llvm.store %v134, %v84 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v135 = llvm.load %v84 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
func.return %v135 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
}
func.func @main() -> i32 {
%v136 = llvm.mlir.constant(1 : i64) : i64
%v137 = llvm.alloca %v136 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
%v138 = llvm.mlir.constant(1 : i64) : i64
%v139 = llvm.alloca %v138 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
%v140 = llvm.mlir.constant(1 : i64) : i64
%v141 = llvm.alloca %v140 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
%v142 = llvm.mlir.constant(1 : i64) : i64
%v143 = llvm.alloca %v142 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
%v144 = llvm.mlir.constant(1 : i64) : i64
%v145 = llvm.alloca %v144 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
%v146 = llvm.mlir.constant(1 : i64) : i64
%v147 = llvm.alloca %v146 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
%v148 = llvm.mlir.constant(1 : i64) : i64
%v149 = llvm.alloca %v148 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
%v150 = llvm.mlir.constant(1 : i64) : i64
%v151 = llvm.alloca %v150 x !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> : (i64) -> !llvm.ptr
%v152 = llvm.mlir.constant(1 : i64) : i64
%v153 = llvm.alloca %v152 x !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> : (i64) -> !llvm.ptr
%v154 = llvm.mlir.constant(1 : i64) : i64
%v155 = llvm.alloca %v154 x !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> : (i64) -> !llvm.ptr
%v156 = llvm.mlir.constant(1 : i64) : i64
%v157 = llvm.alloca %v156 x !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> : (i64) -> !llvm.ptr
%v158 = arith.constant 1.0 : f64
%v159 = arith.constant 2.0 : f64
%v160 = func.call @vec2(%v158, %v159) : (f64, f64) -> !llvm.struct<(f64, f64)>
%v161 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v162 = llvm.extractvalue %v160[0] : !llvm.struct<(f64, f64)>
%v163 = llvm.insertvalue %v162, %v161[0] : !llvm.struct<(f64, f64)>
%v164 = llvm.extractvalue %v160[1] : !llvm.struct<(f64, f64)>
%v165 = llvm.insertvalue %v164, %v163[1] : !llvm.struct<(f64, f64)>
llvm.store %v165, %v137 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v166 = llvm.load %v137 : !llvm.ptr -> !llvm.struct<(f64, f64)>
llvm.store %v166, %v139 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v167 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v168 = arith.constant 0.5 : f64
%v169 = llvm.insertvalue %v168, %v167[0] : !llvm.struct<(f64, f64)>
%v170 = arith.constant 4.0 : f64
%v171 = llvm.insertvalue %v170, %v169[1] : !llvm.struct<(f64, f64)>
llvm.store %v171, %v141 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v172 = llvm.load %v139 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v173 = llvm.load %v141 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v174 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v175 = llvm.extractvalue %v172[0] : !llvm.struct<(f64, f64)>
%v176 = llvm.insertvalue %v175, %v174[0] : !llvm.struct<(f64, f64)>
%v177 = llvm.extractvalue %v172[1] : !llvm.struct<(f64, f64)>
%v178 = llvm.insertvalue %v177, %v176[1] : !llvm.struct<(f64, f64)>
%v179 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v180 = llvm.extractvalue %v173[0] : !llvm.struct<(f64, f64)>
%v181 = llvm.insertvalue %v180, %v179[0] : !llvm.struct<(f64, f64)>
%v182 = llvm.extractvalue %v173[1] : !llvm.struct<(f64, f64)>
%v183 = llvm.insertvalue %v182, %v181[1] : !llvm.struct<(f64, f64)>
%v184 = func.call @add(%v178, %v183) : (!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>) -> !llvm.struct<(f64, f64)>
%v185 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v186 = llvm.extractvalue %v184[0] : !llvm.struct<(f64, f64)>
%v187 = llvm.insertvalue %v186, %v185[0] : !llvm.struct<(f64, f64)>
%v188 = llvm.extractvalue %v184[1] : !llvm.struct<(f64, f64)>
%v189 = llvm.insertvalue %v188, %v187[1] : !llvm.struct<(f64, f64)>
llvm.store %v189, %v143 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v190 = llvm.load %v143 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v191 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v192 = llvm.extractvalue %v178[0] : !llvm.struct<(f64, f64)>
%v193 = llvm.insertvalue %v192, %v191[0] : !llvm.struct<(f64, f64)>
%v194 = llvm.extractvalue %v178[1] : !llvm.struct<(f64, f64)>
%v195 = llvm.insertvalue %v194, %v193[1] : !llvm.struct<(f64, f64)>
llvm.store %v195, %v145 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v196 = llvm.load %v145 : !llvm.ptr -> !llvm.struct<(f64, f64)>
llvm.store %v196, %v139 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v197 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v198 = llvm.extractvalue %v183[0] : !llvm.struct<(f64, f64)>
%v199 = llvm.insertvalue %v198, %v197[0] : !llvm.struct<(f64, f64)>
%v200 = llvm.extractvalue %v183[1] : !llvm.struct<(f64, f64)>
%v201 = llvm.insertvalue %v200, %v199[1] : !llvm.struct<(f64, f64)>
llvm.store %v201, %v147 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v202 = llvm.load %v147 : !llvm.ptr -> !llvm.struct<(f64, f64)>
llvm.store %v202, %v141 : !llvm.struct<(f64, f64)>, !llvm.ptr
llvm.store %v190, %v149 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v203 = llvm.load %v149 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v204 = llvm.getelementptr %v149[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v205 = llvm.load %v204 : !llvm.ptr -> f64
%v206 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v207 = llvm.call @printf(%v206, %v205) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v208 = arith.constant 0 : i32
%v209 = llvm.load %v149 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v210 = llvm.getelementptr %v149[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v211 = llvm.load %v210 : !llvm.ptr -> f64
%v212 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v213 = llvm.call @printf(%v212, %v211) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v214 = arith.constant 0 : i32
%v215 = llvm.load %v139 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v216 = llvm.load %v141 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v217 = func.call @dot(%v215, %v216) : (!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>) -> f64
%v218 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v219 = llvm.call @printf(%v218, %v217) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v220 = arith.constant 0 : i32
%v221 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v222 = llvm.load %v139 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v223 = llvm.insertvalue %v222, %v221[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v224 = llvm.load %v141 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v225 = llvm.insertvalue %v224, %v223[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v226 = arith.constant 2.0 : f64
%v227 = llvm.insertvalue %v226, %v225[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v228 = arith.constant 7 : i32
%v229 = llvm.insertvalue %v228, %v227[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
llvm.store %v229, %v151 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v230 = llvm.load %v151 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v231 = arith.constant 0.5 : f64
%v232 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v233 = llvm.extractvalue %v230[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v234 = llvm.insertvalue %v233, %v232[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v235 = llvm.extractvalue %v230[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v236 = llvm.insertvalue %v235, %v234[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v237 = llvm.extractvalue %v230[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v238 = llvm.insertvalue %v237, %v236[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v239 = llvm.extractvalue %v230[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v240 = llvm.insertvalue %v239, %v238[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v241 = func.call @step(%v240, %v231) : (!llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, f64) -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v242 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v243 = llvm.extractvalue %v241[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v244 = llvm.insertvalue %v243, %v242[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v245 = llvm.extractvalue %v241[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v246 = llvm.insertvalue %v245, %v244[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v247 = llvm.extractvalue %v241[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v248 = llvm.insertvalue %v247, %v246[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v249 = llvm.extractvalue %v241[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v250 = llvm.insertvalue %v249, %v248[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
llvm.store %v250, %v153 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v251 = llvm.load %v153 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v252 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v253 = llvm.extractvalue %v240[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v254 = llvm.insertvalue %v253, %v252[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v255 = llvm.extractvalue %v240[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v256 = llvm.insertvalue %v255, %v254[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v257 = llvm.extractvalue %v240[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v258 = llvm.insertvalue %v257, %v256[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v259 = llvm.extractvalue %v240[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v260 = llvm.insertvalue %v259, %v258[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
llvm.store %v260, %v155 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v261 = llvm.load %v155 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
llvm.store %v261, %v151 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
llvm.store %v251, %v151 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v262 = llvm.load %v151 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v263 = llvm.getelementptr %v151[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v264 = llvm.load %v263 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v265 = llvm.getelementptr %v151[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v266 = llvm.getelementptr %v265[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v267 = llvm.load %v266 : !llvm.ptr -> f64
%v268 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v269 = llvm.call @printf(%v268, %v267) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v270 = arith.constant 0 : i32
%v271 = llvm.load %v151 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v272 = llvm.getelementptr %v151[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v273 = llvm.load %v272 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v274 = llvm.getelementptr %v151[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v275 = llvm.getelementptr %v274[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v276 = llvm.load %v275 : !llvm.ptr -> f64
%v277 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v278 = llvm.call @printf(%v277, %v276) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v279 = arith.constant 0 : i32
%v280 = llvm.load %v151 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v281 = llvm.getelementptr %v151[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v282 = llvm.load %v281 : !llvm.ptr -> i32
%v283 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v284 = llvm.call @printf(%v283, %v282) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v285 = arith.constant 0 : i32
%v286 = llvm.load %v151 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v287 = llvm.getelementptr %v151[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v288 = llvm.load %v287 : !llvm.ptr -> i32
%v289 = arith.constant 3 : i32
%v290 = arith.muli %v288, %v289 : i32
%v291 = llvm.getelementptr %v151[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
llvm.store %v290, %v291 : i32, !llvm.ptr
%v292 = llvm.load %v151 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v293 = llvm.getelementptr %v151[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v294 = llvm.load %v293 : !llvm.ptr -> f64
%v295 = arith.constant 1.0 : f64
%v296 = arith.addf %v294, %v295 : f64
%v297 = llvm.getelementptr %v151[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
llvm.store %v296, %v297 : f64, !llvm.ptr
%v298 = llvm.load %v151 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v299 = llvm.getelementptr %v151[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v300 = llvm.load %v299 : !llvm.ptr -> i32
%v301 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v302 = llvm.call @printf(%v301, %v300) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v303 = arith.constant 0 : i32
%v304 = llvm.load %v151 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v305 = llvm.getelementptr %v151[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v306 = llvm.load %v305 : !llvm.ptr -> f64
%v307 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v308 = llvm.call @printf(%v307, %v306) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v309 = arith.constant 0 : i32
%v310 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v311 = llvm.mlir.zero : !llvm.struct<(f64, f64)>
%v312 = llvm.insertvalue %v311, %v310[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v313 = llvm.mlir.zero : !llvm.struct<(f64, f64)>
%v314 = llvm.insertvalue %v313, %v312[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v315 = arith.constant 0.0 : f64
%v316 = llvm.insertvalue %v315, %v314[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v317 = arith.constant 1 : i32
%v318 = llvm.insertvalue %v317, %v316[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
llvm.store %v318, %v157 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v319 = llvm.load %v157 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v320 = llvm.getelementptr %v157[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v321 = llvm.load %v320 : !llvm.ptr -> f64
%v322 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v323 = llvm.call @printf(%v322, %v321) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v324 = arith.constant 0 : i32
%v325 = arith.constant 0 : i32
func.return %v325 : i32
}
}
