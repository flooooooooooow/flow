module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%f\n\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_1("%d\n\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
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
%v71 = arith.mulf %v67, %v70 : f64
%v72 = llvm.load %v57 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v73 = llvm.getelementptr %v57[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v74 = llvm.load %v73 : !llvm.ptr -> f64
%v75 = llvm.load %v64 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v76 = llvm.getelementptr %v64[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v77 = llvm.load %v76 : !llvm.ptr -> f64
%v78 = arith.mulf %v74, %v77 : f64
%v79 = arith.addf %v71, %v78 : f64
func.return %v79 : f64
}
func.func @step(%arg0: !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, %arg1: f64) -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> {
%v80 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v81 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v82 = llvm.insertvalue %v81, %v80[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v83 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v84 = llvm.insertvalue %v83, %v82[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v85 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v86 = llvm.insertvalue %v85, %v84[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v87 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v88 = llvm.insertvalue %v87, %v86[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v89 = llvm.mlir.constant(1 : i64) : i64
%v90 = llvm.alloca %v89 x !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> : (i64) -> !llvm.ptr
llvm.store %v88, %v90 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v91 = llvm.load %v90 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v92 = llvm.mlir.constant(1 : i64) : i64
%v93 = llvm.alloca %v92 x !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> : (i64) -> !llvm.ptr
llvm.store %v91, %v93 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v94 = llvm.load %v90 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v95 = llvm.getelementptr %v90[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v96 = llvm.load %v95 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v97 = llvm.getelementptr %v90[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v98 = llvm.getelementptr %v97[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v99 = llvm.load %v98 : !llvm.ptr -> f64
%v100 = llvm.load %v90 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v101 = llvm.getelementptr %v90[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v102 = llvm.load %v101 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v103 = llvm.getelementptr %v90[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v104 = llvm.getelementptr %v103[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v105 = llvm.load %v104 : !llvm.ptr -> f64
%v106 = arith.mulf %v105, %arg1 : f64
%v107 = arith.addf %v99, %v106 : f64
%v108 = llvm.getelementptr %v93[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v109 = llvm.getelementptr %v108[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
llvm.store %v107, %v109 : f64, !llvm.ptr
%v110 = llvm.load %v90 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v111 = llvm.getelementptr %v90[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v112 = llvm.load %v111 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v113 = llvm.getelementptr %v90[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v114 = llvm.getelementptr %v113[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v115 = llvm.load %v114 : !llvm.ptr -> f64
%v116 = llvm.load %v90 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v117 = llvm.getelementptr %v90[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v118 = llvm.load %v117 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v119 = llvm.getelementptr %v90[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v120 = llvm.getelementptr %v119[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v121 = llvm.load %v120 : !llvm.ptr -> f64
%v122 = arith.mulf %v121, %arg1 : f64
%v123 = arith.addf %v115, %v122 : f64
%v124 = llvm.getelementptr %v93[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v125 = llvm.getelementptr %v124[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
llvm.store %v123, %v125 : f64, !llvm.ptr
%v126 = llvm.load %v93 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v127 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v128 = llvm.extractvalue %v126[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v129 = llvm.insertvalue %v128, %v127[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v130 = llvm.extractvalue %v126[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v131 = llvm.insertvalue %v130, %v129[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v132 = llvm.extractvalue %v126[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v133 = llvm.insertvalue %v132, %v131[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v134 = llvm.extractvalue %v126[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v135 = llvm.insertvalue %v134, %v133[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v136 = llvm.mlir.constant(1 : i64) : i64
%v137 = llvm.alloca %v136 x !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> : (i64) -> !llvm.ptr
llvm.store %v135, %v137 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v138 = llvm.load %v137 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
func.return %v138 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
}
func.func @main() -> i32 {
%v139 = arith.constant 2.0 : f32
%v140 = arith.constant 1.0 : f32
%v141 = arith.extf %v140 : f32 to f64
%v142 = arith.extf %v139 : f32 to f64
%v143 = func.call @vec2(%v141, %v142) : (f64, f64) -> !llvm.struct<(f64, f64)>
%v144 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v145 = llvm.extractvalue %v143[0] : !llvm.struct<(f64, f64)>
%v146 = llvm.insertvalue %v145, %v144[0] : !llvm.struct<(f64, f64)>
%v147 = llvm.extractvalue %v143[1] : !llvm.struct<(f64, f64)>
%v148 = llvm.insertvalue %v147, %v146[1] : !llvm.struct<(f64, f64)>
%v149 = llvm.mlir.constant(1 : i64) : i64
%v150 = llvm.alloca %v149 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v148, %v150 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v151 = llvm.load %v150 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v152 = llvm.mlir.constant(1 : i64) : i64
%v153 = llvm.alloca %v152 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v151, %v153 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v154 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v155 = arith.constant 0.5 : f32
%v156 = arith.extf %v155 : f32 to f64
%v157 = llvm.insertvalue %v156, %v154[0] : !llvm.struct<(f64, f64)>
%v158 = arith.constant 4.0 : f32
%v159 = arith.extf %v158 : f32 to f64
%v160 = llvm.insertvalue %v159, %v157[1] : !llvm.struct<(f64, f64)>
%v161 = llvm.mlir.constant(1 : i64) : i64
%v162 = llvm.alloca %v161 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v160, %v162 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v163 = llvm.load %v162 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v164 = llvm.load %v153 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v165 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v166 = llvm.extractvalue %v164[0] : !llvm.struct<(f64, f64)>
%v167 = llvm.insertvalue %v166, %v165[0] : !llvm.struct<(f64, f64)>
%v168 = llvm.extractvalue %v164[1] : !llvm.struct<(f64, f64)>
%v169 = llvm.insertvalue %v168, %v167[1] : !llvm.struct<(f64, f64)>
%v170 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v171 = llvm.extractvalue %v163[0] : !llvm.struct<(f64, f64)>
%v172 = llvm.insertvalue %v171, %v170[0] : !llvm.struct<(f64, f64)>
%v173 = llvm.extractvalue %v163[1] : !llvm.struct<(f64, f64)>
%v174 = llvm.insertvalue %v173, %v172[1] : !llvm.struct<(f64, f64)>
%v175 = func.call @add(%v169, %v174) : (!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>) -> !llvm.struct<(f64, f64)>
%v176 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v177 = llvm.extractvalue %v175[0] : !llvm.struct<(f64, f64)>
%v178 = llvm.insertvalue %v177, %v176[0] : !llvm.struct<(f64, f64)>
%v179 = llvm.extractvalue %v175[1] : !llvm.struct<(f64, f64)>
%v180 = llvm.insertvalue %v179, %v178[1] : !llvm.struct<(f64, f64)>
%v181 = llvm.mlir.constant(1 : i64) : i64
%v182 = llvm.alloca %v181 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v180, %v182 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v183 = llvm.load %v182 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v184 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v185 = llvm.extractvalue %v169[0] : !llvm.struct<(f64, f64)>
%v186 = llvm.insertvalue %v185, %v184[0] : !llvm.struct<(f64, f64)>
%v187 = llvm.extractvalue %v169[1] : !llvm.struct<(f64, f64)>
%v188 = llvm.insertvalue %v187, %v186[1] : !llvm.struct<(f64, f64)>
%v189 = llvm.mlir.constant(1 : i64) : i64
%v190 = llvm.alloca %v189 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v188, %v190 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v191 = llvm.load %v190 : !llvm.ptr -> !llvm.struct<(f64, f64)>
llvm.store %v191, %v153 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v192 = llvm.mlir.undef : !llvm.struct<(f64, f64)>
%v193 = llvm.extractvalue %v174[0] : !llvm.struct<(f64, f64)>
%v194 = llvm.insertvalue %v193, %v192[0] : !llvm.struct<(f64, f64)>
%v195 = llvm.extractvalue %v174[1] : !llvm.struct<(f64, f64)>
%v196 = llvm.insertvalue %v195, %v194[1] : !llvm.struct<(f64, f64)>
%v197 = llvm.mlir.constant(1 : i64) : i64
%v198 = llvm.alloca %v197 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v196, %v198 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v199 = llvm.load %v198 : !llvm.ptr -> !llvm.struct<(f64, f64)>
llvm.store %v199, %v162 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v200 = llvm.mlir.constant(1 : i64) : i64
%v201 = llvm.alloca %v200 x !llvm.struct<(f64, f64)> : (i64) -> !llvm.ptr
llvm.store %v183, %v201 : !llvm.struct<(f64, f64)>, !llvm.ptr
%v202 = llvm.load %v201 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v203 = llvm.getelementptr %v201[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v204 = llvm.load %v203 : !llvm.ptr -> f64
%v205 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v206 = llvm.call @printf(%v205, %v204) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v207 = arith.constant 0 : i32
%v208 = llvm.load %v201 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v209 = llvm.getelementptr %v201[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v210 = llvm.load %v209 : !llvm.ptr -> f64
%v211 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v212 = llvm.call @printf(%v211, %v210) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v213 = arith.constant 0 : i32
%v214 = llvm.load %v153 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v215 = llvm.load %v162 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v216 = func.call @dot(%v214, %v215) : (!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>) -> f64
%v217 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v218 = llvm.call @printf(%v217, %v216) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v219 = arith.constant 0 : i32
%v220 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v221 = llvm.load %v153 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v222 = llvm.insertvalue %v221, %v220[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v223 = llvm.load %v162 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v224 = llvm.insertvalue %v223, %v222[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v225 = arith.constant 2.0 : f32
%v226 = arith.extf %v225 : f32 to f64
%v227 = llvm.insertvalue %v226, %v224[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v228 = arith.constant 7 : i32
%v229 = llvm.insertvalue %v228, %v227[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v230 = llvm.mlir.constant(1 : i64) : i64
%v231 = llvm.alloca %v230 x !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> : (i64) -> !llvm.ptr
llvm.store %v229, %v231 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v232 = arith.constant 0.5 : f32
%v233 = llvm.load %v231 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v234 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v235 = llvm.extractvalue %v233[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v236 = llvm.insertvalue %v235, %v234[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v237 = llvm.extractvalue %v233[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v238 = llvm.insertvalue %v237, %v236[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v239 = llvm.extractvalue %v233[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v240 = llvm.insertvalue %v239, %v238[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v241 = llvm.extractvalue %v233[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v242 = llvm.insertvalue %v241, %v240[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v243 = arith.extf %v232 : f32 to f64
%v244 = func.call @step(%v242, %v243) : (!llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, f64) -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v245 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v246 = llvm.extractvalue %v244[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v247 = llvm.insertvalue %v246, %v245[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v248 = llvm.extractvalue %v244[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v249 = llvm.insertvalue %v248, %v247[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v250 = llvm.extractvalue %v244[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v251 = llvm.insertvalue %v250, %v249[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v252 = llvm.extractvalue %v244[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v253 = llvm.insertvalue %v252, %v251[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v254 = llvm.mlir.constant(1 : i64) : i64
%v255 = llvm.alloca %v254 x !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> : (i64) -> !llvm.ptr
llvm.store %v253, %v255 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v256 = llvm.load %v255 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v257 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v258 = llvm.extractvalue %v242[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v259 = llvm.insertvalue %v258, %v257[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v260 = llvm.extractvalue %v242[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v261 = llvm.insertvalue %v260, %v259[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v262 = llvm.extractvalue %v242[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v263 = llvm.insertvalue %v262, %v261[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v264 = llvm.extractvalue %v242[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v265 = llvm.insertvalue %v264, %v263[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v266 = llvm.mlir.constant(1 : i64) : i64
%v267 = llvm.alloca %v266 x !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> : (i64) -> !llvm.ptr
llvm.store %v265, %v267 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v268 = llvm.load %v267 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
llvm.store %v268, %v231 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
llvm.store %v256, %v231 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v269 = llvm.load %v231 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v270 = llvm.getelementptr %v231[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v271 = llvm.load %v270 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v272 = llvm.getelementptr %v231[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v273 = llvm.getelementptr %v272[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v274 = llvm.load %v273 : !llvm.ptr -> f64
%v275 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v276 = llvm.call @printf(%v275, %v274) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v277 = arith.constant 0 : i32
%v278 = llvm.load %v231 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v279 = llvm.getelementptr %v231[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v280 = llvm.load %v279 : !llvm.ptr -> !llvm.struct<(f64, f64)>
%v281 = llvm.getelementptr %v231[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v282 = llvm.getelementptr %v281[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f64, f64)>
%v283 = llvm.load %v282 : !llvm.ptr -> f64
%v284 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v285 = llvm.call @printf(%v284, %v283) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v286 = arith.constant 0 : i32
%v287 = llvm.load %v231 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v288 = llvm.getelementptr %v231[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v289 = llvm.load %v288 : !llvm.ptr -> i32
%v290 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v291 = llvm.call @printf(%v290, %v289) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v292 = arith.constant 0 : i32
%v293 = llvm.load %v231 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v294 = llvm.getelementptr %v231[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v295 = llvm.load %v294 : !llvm.ptr -> i32
%v296 = arith.constant 3 : i32
%v297 = arith.muli %v295, %v296 : i32
%v298 = llvm.getelementptr %v231[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
llvm.store %v297, %v298 : i32, !llvm.ptr
%v299 = llvm.load %v231 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v300 = llvm.getelementptr %v231[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v301 = llvm.load %v300 : !llvm.ptr -> f64
%v302 = arith.constant 1.0 : f32
%v303 = arith.extf %v302 : f32 to f64
%v304 = arith.addf %v301, %v303 : f64
%v305 = llvm.getelementptr %v231[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
llvm.store %v304, %v305 : f64, !llvm.ptr
%v306 = llvm.load %v231 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v307 = llvm.getelementptr %v231[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v308 = llvm.load %v307 : !llvm.ptr -> i32
%v309 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v310 = llvm.call @printf(%v309, %v308) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v311 = arith.constant 0 : i32
%v312 = llvm.load %v231 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v313 = llvm.getelementptr %v231[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v314 = llvm.load %v313 : !llvm.ptr -> f64
%v315 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v316 = llvm.call @printf(%v315, %v314) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v317 = arith.constant 0 : i32
%v318 = llvm.mlir.undef : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v319 = llvm.mlir.zero : !llvm.struct<(f64, f64)>
%v320 = llvm.insertvalue %v319, %v318[0] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v321 = llvm.mlir.zero : !llvm.struct<(f64, f64)>
%v322 = llvm.insertvalue %v321, %v320[1] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v323 = arith.constant 0.0 : f64
%v324 = llvm.insertvalue %v323, %v322[2] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v325 = arith.constant 1 : i32
%v326 = llvm.insertvalue %v325, %v324[3] : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v327 = llvm.mlir.constant(1 : i64) : i64
%v328 = llvm.alloca %v327 x !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)> : (i64) -> !llvm.ptr
llvm.store %v326, %v328 : !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>, !llvm.ptr
%v329 = llvm.load %v328 : !llvm.ptr -> !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v330 = llvm.getelementptr %v328[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(f64, f64)>, !llvm.struct<(f64, f64)>, f64, i32)>
%v331 = llvm.load %v330 : !llvm.ptr -> f64
%v332 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v333 = llvm.call @printf(%v332, %v331) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v334 = arith.constant 0 : i32
%v335 = arith.constant 0 : i32
func.return %v335 : i32
}
}
