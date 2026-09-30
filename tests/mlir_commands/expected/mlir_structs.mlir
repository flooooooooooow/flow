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
%v1 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v2 = llvm.insertvalue %arg0, %v1[0] : !llvm.struct<(f64, f64)>
%v3 = llvm.insertvalue %arg1, %v2[1] : !llvm.struct<(f64, f64)>
%v4 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v5 = llvm.extractvalue %v3[0] : !llvm.struct<(f64, f64)>
%v6 = llvm.insertvalue %v5, %v4[0] : !llvm.struct<(f64, f64)>
%v7 = llvm.extractvalue %v3[1] : !llvm.struct<(f64, f64)>
%v8 = llvm.insertvalue %v7, %v6[1] : !llvm.struct<(f64, f64)>
%v9 = llvm.mlir.constant(1 : i64) : i64
%v10 = llvm.alloca %v9 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v8, %v10 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v11 = llvm.load %v10 : !llvm.ptr -> !llvm.struct<(f64, f64)>
func.return %v11 : !llvm.struct<(f64, f64)>
}
func.func @add(%arg0: !llvm.struct<(f64, f64)>, %arg1: !llvm.struct<(f64, f64)>) -> !llvm.struct<(f64, f64)> {
%v12 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v13 = llvm.extractvalue %arg0[0] : !llvm.struct<(f64, f64)>
%v14 = llvm.insertvalue %v13, %v12[0] : !llvm.struct<(f64, f64)>
%v15 = llvm.extractvalue %arg0[1] : !llvm.struct<(f64, f64)>
%v16 = llvm.insertvalue %v15, %v14[1] : !llvm.struct<(f64, f64)>
%v17 = llvm.mlir.constant(1 : i64) : i64
%v18 = llvm.alloca %v17 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v16, %v18 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v19 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v20 = llvm.extractvalue %arg1[0] : !llvm.struct<(f64, f64)>
%v21 = llvm.insertvalue %v20, %v19[0] : !llvm.struct<(f64, f64)>
%v22 = llvm.extractvalue %arg1[1] : !llvm.struct<(f64, f64)>
%v23 = llvm.insertvalue %v22, %v21[1] : !llvm.struct<(f64, f64)>
%v24 = llvm.mlir.constant(1 : i64) : i64
%v25 = llvm.alloca %v24 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v23, %v25 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v26 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v27 = llvm.load %v18 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v28 = llvm.getelementptr %v18[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v29 = llvm.load %v28 : !llvm.ptr -> f64
%v30 = llvm.load %v25 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v31 = llvm.getelementptr %v25[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v32 = llvm.load %v31 : !llvm.ptr -> f64
%v33 = arith.addf %v29, %v32 : f64
%v34 = llvm.insertvalue %v33, %v26[0] : !llvm.struct<(f64, f64)>
%v35 = llvm.load %v18 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v36 = llvm.getelementptr %v18[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v37 = llvm.load %v36 : !llvm.ptr -> f64
%v38 = llvm.load %v25 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v39 = llvm.getelementptr %v25[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v40 = llvm.load %v39 : !llvm.ptr -> f64
%v41 = arith.addf %v37, %v40 : f64
%v42 = llvm.insertvalue %v41, %v34[1] : !llvm.struct<(f64, f64)>
%v43 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v44 = llvm.extractvalue %v42[0] : !llvm.struct<(f64, f64)>
%v45 = llvm.insertvalue %v44, %v43[0] : !llvm.struct<(f64, f64)>
%v46 = llvm.extractvalue %v42[1] : !llvm.struct<(f64, f64)>
%v47 = llvm.insertvalue %v46, %v45[1] : !llvm.struct<(f64, f64)>
%v48 = llvm.mlir.constant(1 : i64) : i64
%v49 = llvm.alloca %v48 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v47, %v49 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v50 = llvm.load %v49 : !llvm.ptr -> !llvm.struct<(f64, f64)>
func.return %v50 : !llvm.struct<(f64, f64)>
}
func.func @dot(%arg0: !llvm.struct<(f64, f64)>, %arg1: !llvm.struct<(f64, f64)>) -> f64 {
%v51 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v52 = llvm.extractvalue %arg0[0] : !llvm.struct<(f64, f64)>
%v53 = llvm.insertvalue %v52, %v51[0] : !llvm.struct<(f64, f64)>
%v54 = llvm.extractvalue %arg0[1] : !llvm.struct<(f64, f64)>
%v55 = llvm.insertvalue %v54, %v53[1] : !llvm.struct<(f64, f64)>
%v56 = llvm.mlir.constant(1 : i64) : i64
%v57 = llvm.alloca %v56 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v55, %v57 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v58 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v59 = llvm.extractvalue %arg1[0] : !llvm.struct<(f64, f64)>
%v60 = llvm.insertvalue %v59, %v58[0] : !llvm.struct<(f64, f64)>
%v61 = llvm.extractvalue %arg1[1] : !llvm.struct<(f64, f64)>
%v62 = llvm.insertvalue %v61, %v60[1] : !llvm.struct<(f64, f64)>
%v63 = llvm.mlir.constant(1 : i64) : i64
%v64 = llvm.alloca %v63 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v62, %v64 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v65 = llvm.load %v57 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v66 = llvm.getelementptr %v57[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v67 = llvm.load %v66 : !llvm.ptr -> f64
%v68 = llvm.load %v64 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v69 = llvm.getelementptr %v64[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v70 = llvm.load %v69 : !llvm.ptr -> f64
%v71 = llvm.load %v57 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v72 = llvm.getelementptr %v57[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v73 = llvm.load %v72 : !llvm.ptr -> f64
%v74 = llvm.load %v64 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v75 = llvm.getelementptr %v64[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v76 = llvm.load %v75 : !llvm.ptr -> f64
%v77 = arith.mulf %v73, %v76 : f64
%v78 = llvm.intr.fma(%v67, %v70, %v77) : (f64, f64, f64) -> f64
func.return %v78 : f64
}
func.func @step(%arg0: !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, %arg1: f64) -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> {
%v79 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v80 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v81 = llvm.insertvalue %v80, %v79[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v82 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v83 = llvm.insertvalue %v82, %v81[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v84 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v85 = llvm.insertvalue %v84, %v83[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v86 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v87 = llvm.insertvalue %v86, %v85[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v88 = llvm.mlir.constant(1 : i64) : i64
%v89 = llvm.alloca %v88 x !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> : (i64) -> !llvm.ptr
llvm.store %v87, %v89 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v90 = llvm.load %v89 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v91 = llvm.mlir.constant(1 : i64) : i64
%v92 = llvm.alloca %v91 x !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> : (i64) -> !llvm.ptr
llvm.store %v90, %v92 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v93 = llvm.load %v89 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v94 = llvm.getelementptr %v89[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v95 = llvm.load %v94 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v96 = llvm.getelementptr %v89[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v97 = llvm.getelementptr %v96[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v98 = llvm.load %v97 : !llvm.ptr -> f64
%v99 = llvm.load %v89 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v100 = llvm.getelementptr %v89[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v101 = llvm.load %v100 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v102 = llvm.getelementptr %v89[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v103 = llvm.getelementptr %v102[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v104 = llvm.load %v103 : !llvm.ptr -> f64
%v105 = llvm.intr.fma(%v104, %arg1, %v98) : (f64, f64, f64) -> f64
%v106 = llvm.getelementptr %v92[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v107 = llvm.getelementptr %v106[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
llvm.store %v105, %v107 : f64, !llvm.ptr
%v108 = llvm.load %v89 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v109 = llvm.getelementptr %v89[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v110 = llvm.load %v109 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v111 = llvm.getelementptr %v89[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v112 = llvm.getelementptr %v111[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v113 = llvm.load %v112 : !llvm.ptr -> f64
%v114 = llvm.load %v89 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v115 = llvm.getelementptr %v89[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v116 = llvm.load %v115 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v117 = llvm.getelementptr %v89[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v118 = llvm.getelementptr %v117[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v119 = llvm.load %v118 : !llvm.ptr -> f64
%v120 = llvm.intr.fma(%v119, %arg1, %v113) : (f64, f64, f64) -> f64
%v121 = llvm.getelementptr %v92[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v122 = llvm.getelementptr %v121[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
llvm.store %v120, %v122 : f64, !llvm.ptr
%v123 = llvm.load %v92 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v124 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v125 = llvm.extractvalue %v123[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v126 = llvm.insertvalue %v125, %v124[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v127 = llvm.extractvalue %v123[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v128 = llvm.insertvalue %v127, %v126[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v129 = llvm.extractvalue %v123[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v130 = llvm.insertvalue %v129, %v128[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v131 = llvm.extractvalue %v123[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v132 = llvm.insertvalue %v131, %v130[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v133 = llvm.mlir.constant(1 : i64) : i64
%v134 = llvm.alloca %v133 x !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> : (i64) -> !llvm.ptr
llvm.store %v132, %v134 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v135 = llvm.load %v134 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
func.return %v135 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
}
func.func @main() -> i32 {
%v136 = arith.constant 1.0 : f64
%v137 = arith.constant 2.0 : f64
%v138 = func.call @vec2(%v136, %v137) : (f64, f64) -> !llvm.struct<(f64, f64)>
%v139 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v140 = llvm.extractvalue %v138[0] : !llvm.struct<(f64, f64)>
%v141 = llvm.insertvalue %v140, %v139[0] : !llvm.struct<(f64, f64)>
%v142 = llvm.extractvalue %v138[1] : !llvm.struct<(f64, f64)>
%v143 = llvm.insertvalue %v142, %v141[1] : !llvm.struct<(f64, f64)>
%v144 = llvm.mlir.constant(1 : i64) : i64
%v145 = llvm.alloca %v144 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v143, %v145 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v146 = llvm.load %v145 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v147 = llvm.mlir.constant(1 : i64) : i64
%v148 = llvm.alloca %v147 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v146, %v148 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v149 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v150 = arith.constant 0.5 : f64
%v151 = llvm.insertvalue %v150, %v149[0] : !llvm.struct<(f64, f64)>
%v152 = arith.constant 4.0 : f64
%v153 = llvm.insertvalue %v152, %v151[1] : !llvm.struct<(f64, f64)>
%v154 = llvm.mlir.constant(1 : i64) : i64
%v155 = llvm.alloca %v154 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v153, %v155 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v156 = llvm.load %v148 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v157 = llvm.load %v155 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v158 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v159 = llvm.extractvalue %v156[0] : !llvm.struct<(f64, f64)>
%v160 = llvm.insertvalue %v159, %v158[0] : !llvm.struct<(f64, f64)>
%v161 = llvm.extractvalue %v156[1] : !llvm.struct<(f64, f64)>
%v162 = llvm.insertvalue %v161, %v160[1] : !llvm.struct<(f64, f64)>
%v163 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v164 = llvm.extractvalue %v157[0] : !llvm.struct<(f64, f64)>
%v165 = llvm.insertvalue %v164, %v163[0] : !llvm.struct<(f64, f64)>
%v166 = llvm.extractvalue %v157[1] : !llvm.struct<(f64, f64)>
%v167 = llvm.insertvalue %v166, %v165[1] : !llvm.struct<(f64, f64)>
%v168 = func.call @add(%v162, %v167) : (!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>) -> !llvm.struct<(f64, f64)>
%v169 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v170 = llvm.extractvalue %v168[0] : !llvm.struct<(f64, f64)>
%v171 = llvm.insertvalue %v170, %v169[0] : !llvm.struct<(f64, f64)>
%v172 = llvm.extractvalue %v168[1] : !llvm.struct<(f64, f64)>
%v173 = llvm.insertvalue %v172, %v171[1] : !llvm.struct<(f64, f64)>
%v174 = llvm.mlir.constant(1 : i64) : i64
%v175 = llvm.alloca %v174 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v173, %v175 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v176 = llvm.load %v175 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v177 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v178 = llvm.extractvalue %v162[0] : !llvm.struct<(f64, f64)>
%v179 = llvm.insertvalue %v178, %v177[0] : !llvm.struct<(f64, f64)>
%v180 = llvm.extractvalue %v162[1] : !llvm.struct<(f64, f64)>
%v181 = llvm.insertvalue %v180, %v179[1] : !llvm.struct<(f64, f64)>
%v182 = llvm.mlir.constant(1 : i64) : i64
%v183 = llvm.alloca %v182 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v181, %v183 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v184 = llvm.load %v183 : !llvm.ptr -> !llvm.struct<(f64, f64)>
llvm.store %v184, %v148 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v185 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v186 = llvm.extractvalue %v167[0] : !llvm.struct<(f64, f64)>
%v187 = llvm.insertvalue %v186, %v185[0] : !llvm.struct<(f64, f64)>
%v188 = llvm.extractvalue %v167[1] : !llvm.struct<(f64, f64)>
%v189 = llvm.insertvalue %v188, %v187[1] : !llvm.struct<(f64, f64)>
%v190 = llvm.mlir.constant(1 : i64) : i64
%v191 = llvm.alloca %v190 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v189, %v191 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v192 = llvm.load %v191 : !llvm.ptr -> !llvm.struct<(f64, f64)>
llvm.store %v192, %v155 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v193 = llvm.mlir.constant(1 : i64) : i64
%v194 = llvm.alloca %v193 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v176, %v194 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v195 = llvm.load %v194 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v196 = llvm.getelementptr %v194[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v197 = llvm.load %v196 : !llvm.ptr -> f64
%v198 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v199 = llvm.call @printf(%v198, %v197) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v200 = arith.constant 0 : i32
%v201 = llvm.load %v194 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v202 = llvm.getelementptr %v194[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v203 = llvm.load %v202 : !llvm.ptr -> f64
%v204 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v205 = llvm.call @printf(%v204, %v203) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v206 = arith.constant 0 : i32
%v207 = llvm.load %v148 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v208 = llvm.load %v155 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v209 = func.call @dot(%v207, %v208) : (!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>) -> f64
%v210 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v211 = llvm.call @printf(%v210, %v209) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v212 = arith.constant 0 : i32
%v213 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v214 = llvm.load %v148 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v215 = llvm.insertvalue %v214, %v213[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v216 = llvm.load %v155 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v217 = llvm.insertvalue %v216, %v215[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v218 = arith.constant 2.0 : f64
%v219 = llvm.insertvalue %v218, %v217[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v220 = arith.constant 7 : i32
%v221 = llvm.insertvalue %v220, %v219[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v222 = llvm.mlir.constant(1 : i64) : i64
%v223 = llvm.alloca %v222 x !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> : (i64) -> !llvm.ptr
llvm.store %v221, %v223 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v224 = llvm.load %v223 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v225 = arith.constant 0.5 : f64
%v226 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v227 = llvm.extractvalue %v224[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v228 = llvm.insertvalue %v227, %v226[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v229 = llvm.extractvalue %v224[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v230 = llvm.insertvalue %v229, %v228[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v231 = llvm.extractvalue %v224[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v232 = llvm.insertvalue %v231, %v230[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v233 = llvm.extractvalue %v224[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v234 = llvm.insertvalue %v233, %v232[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v235 = func.call @step(%v234, %v225) : (!llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, f64) -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v236 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v237 = llvm.extractvalue %v235[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v238 = llvm.insertvalue %v237, %v236[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v239 = llvm.extractvalue %v235[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v240 = llvm.insertvalue %v239, %v238[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v241 = llvm.extractvalue %v235[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v242 = llvm.insertvalue %v241, %v240[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v243 = llvm.extractvalue %v235[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v244 = llvm.insertvalue %v243, %v242[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v245 = llvm.mlir.constant(1 : i64) : i64
%v246 = llvm.alloca %v245 x !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> : (i64) -> !llvm.ptr
llvm.store %v244, %v246 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v247 = llvm.load %v246 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v248 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v249 = llvm.extractvalue %v234[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v250 = llvm.insertvalue %v249, %v248[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v251 = llvm.extractvalue %v234[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v252 = llvm.insertvalue %v251, %v250[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v253 = llvm.extractvalue %v234[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v254 = llvm.insertvalue %v253, %v252[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v255 = llvm.extractvalue %v234[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v256 = llvm.insertvalue %v255, %v254[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v257 = llvm.mlir.constant(1 : i64) : i64
%v258 = llvm.alloca %v257 x !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> : (i64) -> !llvm.ptr
llvm.store %v256, %v258 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v259 = llvm.load %v258 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
llvm.store %v259, %v223 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
llvm.store %v247, %v223 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v260 = llvm.load %v223 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v261 = llvm.getelementptr %v223[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v262 = llvm.load %v261 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v263 = llvm.getelementptr %v223[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v264 = llvm.getelementptr %v263[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v265 = llvm.load %v264 : !llvm.ptr -> f64
%v266 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v267 = llvm.call @printf(%v266, %v265) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v268 = arith.constant 0 : i32
%v269 = llvm.load %v223 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v270 = llvm.getelementptr %v223[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v271 = llvm.load %v270 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v272 = llvm.getelementptr %v223[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v273 = llvm.getelementptr %v272[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v274 = llvm.load %v273 : !llvm.ptr -> f64
%v275 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v276 = llvm.call @printf(%v275, %v274) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v277 = arith.constant 0 : i32
%v278 = llvm.load %v223 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v279 = llvm.getelementptr %v223[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v280 = llvm.load %v279 : !llvm.ptr -> i32
%v281 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v282 = llvm.call @printf(%v281, %v280) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v283 = arith.constant 0 : i32
%v284 = llvm.load %v223 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v285 = llvm.getelementptr %v223[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v286 = llvm.load %v285 : !llvm.ptr -> i32
%v287 = arith.constant 3 : i32
%v288 = arith.muli %v286, %v287 : i32
%v289 = llvm.getelementptr %v223[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
llvm.store %v288, %v289 : i32, !llvm.ptr
%v290 = llvm.load %v223 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v291 = llvm.getelementptr %v223[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v292 = llvm.load %v291 : !llvm.ptr -> f64
%v293 = arith.constant 1.0 : f64
%v294 = arith.addf %v292, %v293 : f64
%v295 = llvm.getelementptr %v223[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
llvm.store %v294, %v295 : f64, !llvm.ptr
%v296 = llvm.load %v223 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v297 = llvm.getelementptr %v223[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v298 = llvm.load %v297 : !llvm.ptr -> i32
%v299 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v300 = llvm.call @printf(%v299, %v298) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v301 = arith.constant 0 : i32
%v302 = llvm.load %v223 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v303 = llvm.getelementptr %v223[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v304 = llvm.load %v303 : !llvm.ptr -> f64
%v305 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v306 = llvm.call @printf(%v305, %v304) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v307 = arith.constant 0 : i32
%v308 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v309 = llvm.mlir.zero : !llvm.struct<(f64, f64)>
%v310 = llvm.insertvalue %v309, %v308[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v311 = llvm.mlir.zero : !llvm.struct<(f64, f64)>
%v312 = llvm.insertvalue %v311, %v310[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v313 = arith.constant 0.0 : f64
%v314 = llvm.insertvalue %v313, %v312[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v315 = arith.constant 1 : i32
%v316 = llvm.insertvalue %v315, %v314[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v317 = llvm.mlir.constant(1 : i64) : i64
%v318 = llvm.alloca %v317 x !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> : (i64) -> !llvm.ptr
llvm.store %v316, %v318 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v319 = llvm.load %v318 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v320 = llvm.getelementptr %v318[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v321 = llvm.load %v320 : !llvm.ptr -> f64
%v322 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v323 = llvm.call @printf(%v322, %v321) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v324 = arith.constant 0 : i32
%v325 = arith.constant 0 : i32
func.return %v325 : i32
}
}
