module {
func.func private @malloc(i64) -> !llvm.ptr
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_1("%lld\0A\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
llvm.mlir.global internal constant @str_2("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
// Constant: K
llvm.mlir.global internal constant @K(3 : i32) : i32
// Constant: MASK
llvm.mlir.global internal constant @MASK(16 : i32) : i32
// Constant: NEG
llvm.mlir.global internal constant @NEG(-5 : i64) : i64
// Constant: ZERO_F
// Module static: counter
llvm.mlir.global internal @counter(42 : i32) : i32
func.func @total(%arg0: !llvm.struct<(!llvm.ptr, i64)>) -> f64 {
%v1 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v2 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i64)>
%v3 = llvm.insertvalue %v2, %v1[0] : !llvm.struct<(!llvm.ptr, i64)>
%v4 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i64)>
%v5 = llvm.insertvalue %v4, %v3[1] : !llvm.struct<(!llvm.ptr, i64)>
%v6 = llvm.mlir.constant(1 : i64) : i64
%v7 = llvm.alloca %v6 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v5, %v7 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v8 = arith.constant 0.0 : f64
%v9 = llvm.mlir.constant(1 : i64) : i64
%v10 = llvm.alloca %v9 x f64 : (i64) -> !llvm.ptr
llvm.store %v8, %v10 : f64, !llvm.ptr
%v11 = arith.constant 0 : i32
%v12 = llvm.mlir.constant(1 : i64) : i64
%v13 = llvm.alloca %v12 x i32 : (i64) -> !llvm.ptr
llvm.store %v11, %v13 : i32, !llvm.ptr
cf.br ^b1
^b1:
%v14 = llvm.load %v13 : !llvm.ptr -> i32
%v15 = llvm.load %v7 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v16 = llvm.extractvalue %v15[1] : !llvm.struct<(!llvm.ptr, i64)>
%v17 = arith.extsi %v14 : i32 to i64
%v18 = arith.cmpi slt, %v17, %v16 : i64
cf.cond_br %v18, ^b2, ^b3
^b2:
%v19 = llvm.load %v10 : !llvm.ptr -> f64
%v20 = llvm.load %v7 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v21 = llvm.load %v13 : !llvm.ptr -> i32
%v22 = llvm.extractvalue %v20[0] : !llvm.struct<(!llvm.ptr, i64)>
%v23 = arith.extsi %v21 : i32 to i64
%v24 = llvm.getelementptr %v22[%v23] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v25 = llvm.load %v24 : !llvm.ptr -> f64
%v26 = arith.addf %v19, %v25 : f64
llvm.store %v26, %v10 : f64, !llvm.ptr
%v27 = llvm.load %v13 : !llvm.ptr -> i32
%v28 = arith.constant 1 : i32
%v29 = arith.addi %v27, %v28 : i32
llvm.store %v29, %v13 : i32, !llvm.ptr
cf.br ^b1
^b3:
%v30 = llvm.load %v10 : !llvm.ptr -> f64
func.return %v30 : f64
}
func.func @fill(%arg0: !llvm.struct<(!llvm.ptr, i64)>, %arg1: f64) -> () {
%v31 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v32 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i64)>
%v33 = llvm.insertvalue %v32, %v31[0] : !llvm.struct<(!llvm.ptr, i64)>
%v34 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i64)>
%v35 = llvm.insertvalue %v34, %v33[1] : !llvm.struct<(!llvm.ptr, i64)>
%v36 = llvm.mlir.constant(1 : i64) : i64
%v37 = llvm.alloca %v36 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v35, %v37 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v38 = arith.constant 0 : i32
%v39 = arith.extsi %v38 : i32 to i64
%v40 = llvm.mlir.constant(1 : i64) : i64
%v41 = llvm.alloca %v40 x i64 : (i64) -> !llvm.ptr
llvm.store %v39, %v41 : i64, !llvm.ptr
cf.br ^b4
^b4:
%v42 = llvm.load %v41 : !llvm.ptr -> i64
%v43 = llvm.load %v37 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v44 = llvm.extractvalue %v43[1] : !llvm.struct<(!llvm.ptr, i64)>
%v45 = arith.cmpi slt, %v42, %v44 : i64
cf.cond_br %v45, ^b5, ^b6
^b5:
%v46 = llvm.load %v37 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v47 = llvm.load %v41 : !llvm.ptr -> i64
%v48 = llvm.extractvalue %v46[0] : !llvm.struct<(!llvm.ptr, i64)>
%v49 = llvm.getelementptr %v48[%v47] : (!llvm.ptr, i64) -> !llvm.ptr, f64
llvm.store %arg1, %v49 : f64, !llvm.ptr
%v50 = llvm.load %v41 : !llvm.ptr -> i64
%v51 = arith.constant 1 : i32
%v52 = arith.extsi %v51 : i32 to i64
%v53 = arith.addi %v50, %v52 : i64
llvm.store %v53, %v41 : i64, !llvm.ptr
cf.br ^b4
^b6:
func.return
}
func.func @make(%arg0: i32) -> !llvm.struct<(!llvm.ptr, i64)> {
%v54 = arith.extsi %arg0 : i32 to i64
%v55 = arith.constant 8 : i32
%v56 = arith.extsi %v55 : i32 to i64
%v57 = arith.muli %v54, %v56 : i64
%v58 = func.call @malloc(%v57) : (i64) -> !llvm.ptr
%v59 = arith.constant 0 : i32
%v60 = arith.extsi %v59 : i32 to i64
%v61 = arith.extsi %arg0 : i32 to i64
%v62 = llvm.getelementptr %v58[%v60] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v63 = arith.subi %v61, %v60 : i64
%v64 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v65 = llvm.insertvalue %v62, %v64[0] : !llvm.struct<(!llvm.ptr, i64)>
%v66 = llvm.insertvalue %v63, %v65[1] : !llvm.struct<(!llvm.ptr, i64)>
%v67 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v68 = llvm.extractvalue %v66[0] : !llvm.struct<(!llvm.ptr, i64)>
%v69 = llvm.insertvalue %v68, %v67[0] : !llvm.struct<(!llvm.ptr, i64)>
%v70 = llvm.extractvalue %v66[1] : !llvm.struct<(!llvm.ptr, i64)>
%v71 = llvm.insertvalue %v70, %v69[1] : !llvm.struct<(!llvm.ptr, i64)>
%v72 = llvm.mlir.constant(1 : i64) : i64
%v73 = llvm.alloca %v72 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v71, %v73 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v74 = llvm.load %v73 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
func.return %v74 : !llvm.struct<(!llvm.ptr, i64)>
}
func.func @first4(%arg0: !llvm.struct<(!llvm.ptr, i64)>) -> i32 {
%v75 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v76 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i64)>
%v77 = llvm.insertvalue %v76, %v75[0] : !llvm.struct<(!llvm.ptr, i64)>
%v78 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i64)>
%v79 = llvm.insertvalue %v78, %v77[1] : !llvm.struct<(!llvm.ptr, i64)>
%v80 = llvm.mlir.constant(1 : i64) : i64
%v81 = llvm.alloca %v80 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v79, %v81 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v82 = llvm.load %v81 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v83 = arith.constant 0 : i32
%v84 = llvm.extractvalue %v82[0] : !llvm.struct<(!llvm.ptr, i64)>
%v85 = arith.extsi %v83 : i32 to i64
%v86 = llvm.getelementptr %v84[%v85] : (!llvm.ptr, i64) -> !llvm.ptr, i32
%v87 = llvm.load %v86 : !llvm.ptr -> i32
%v88 = llvm.load %v81 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v89 = arith.constant 3 : i32
%v90 = llvm.extractvalue %v88[0] : !llvm.struct<(!llvm.ptr, i64)>
%v91 = arith.extsi %v89 : i32 to i64
%v92 = llvm.getelementptr %v90[%v91] : (!llvm.ptr, i64) -> !llvm.ptr, i32
%v93 = llvm.load %v92 : !llvm.ptr -> i32
%v94 = arith.addi %v87, %v93 : i32
func.return %v94 : i32
}
func.func @scale(%arg0: memref<?xf32>, %arg1: memref<?xf32>, %arg2: i32, %arg3: f32) -> () {
// flow: vectorized elementwise f32 loop (VF=4)
%v95 = arith.constant 0 : i32
%v96 = arith.index_cast %v95 : i32 to index
%v97 = arith.index_cast %arg2 : i32 to index
%v98 = arith.constant 1 : index
%v99 = arith.constant 4 : index
%v100 = arith.subi %v97, %v96 : index
%v101 = arith.remsi %v100, %v99 : index
%v102 = arith.subi %v100, %v101 : index
%v103 = arith.addi %v96, %v102 : index
scf.for %v104 = %v96 to %v103 step %v99 {
%v105 = arith.constant 0.0 : f32
%v106 = vector.transfer_read %arg1[%v104], %v105 {in_bounds = [true]} : memref<?xf32>, vector<4xf32>
%v107 = arith.negf %v106 : vector<4xf32>
%v108 = vector.broadcast %arg3 : f32 to vector<4xf32>
%v109 = arith.mulf %v107, %v108 : vector<4xf32>
%v110 = arith.constant 2.0 : f32
%v111 = vector.broadcast %v110 : f32 to vector<4xf32>
%v112 = arith.addf %v109, %v111 : vector<4xf32>
%v113 = arith.constant 0.0 : f32
%v114 = vector.transfer_read %arg0[%v104], %v113 {in_bounds = [true]} : memref<?xf32>, vector<4xf32>
%v115 = arith.constant 4.0 : f32
%v116 = vector.broadcast %v115 : f32 to vector<4xf32>
%v117 = arith.divf %v114, %v116 : vector<4xf32>
%v118 = arith.subf %v112, %v117 : vector<4xf32>
vector.transfer_write %v118, %arg0[%v104] {in_bounds = [true]} : vector<4xf32>, memref<?xf32>
}
scf.for %v119 = %v103 to %v97 step %v98 {
%v120 = memref.load %arg1[%v119] : memref<?xf32>
%v121 = arith.negf %v120 : f32
%v122 = arith.mulf %v121, %arg3 : f32
%v123 = arith.constant 2.0 : f64
%v124 = arith.extf %v122 : f32 to f64
%v125 = arith.addf %v124, %v123 : f64
%v126 = memref.load %arg0[%v119] : memref<?xf32>
%v127 = arith.constant 4.0 : f64
%v128 = arith.extf %v126 : f32 to f64
%v129 = arith.divf %v128, %v127 : f64
%v130 = arith.subf %v125, %v129 : f64
%v131 = arith.truncf %v130 : f64 to f32
memref.store %v131, %arg0[%v119] : memref<?xf32>
}
func.return
}
func.func @dot(%arg0: memref<?xf32>, %arg1: memref<?xf32>, %arg2: i32) -> f32 {
%v132 = arith.constant 0.0 : f64
%v133 = arith.truncf %v132 : f64 to f32
%v134 = llvm.mlir.constant(1 : i64) : i64
%v135 = llvm.alloca %v134 x f32 : (i64) -> !llvm.ptr
llvm.store %v133, %v135 : f32, !llvm.ptr
%v136 = arith.constant 0 : i32
%v137 = arith.index_cast %v136 : i32 to index
%v138 = arith.index_cast %arg2 : i32 to index
%v139 = arith.constant 1 : index
%v140 = arith.constant -1 : index
%v141 = arith.cmpi sle, %v137, %v138 : index
%v142 = arith.select %v141, %v139, %v140 : index
cf.br ^b7(%v137 : index)
^b7(%v143: index):
%v144 = arith.cmpi slt, %v143, %v138 : index
%v145 = arith.cmpi sgt, %v143, %v138 : index
%v146 = arith.select %v141, %v144, %v145 : i1
cf.cond_br %v146, ^b8(%v143 : index), ^b9(%v143 : index)
^b8(%v147: index):
%v148 = llvm.load %v135 : !llvm.ptr -> f32
%v149 = memref.load %arg0[%v147] : memref<?xf32>
%v150 = memref.load %arg1[%v147] : memref<?xf32>
%v151 = llvm.intr.fma(%v149, %v150, %v148) : (f32, f32, f32) -> f32
llvm.store %v151, %v135 : f32, !llvm.ptr
%v152 = arith.addi %v147, %v142 : index
cf.br ^b7(%v152 : index)
^b9(%v153: index):
%v154 = llvm.load %v135 : !llvm.ptr -> f32
func.return %v154 : f32
}
func.func @main() -> i32 {
%v155 = arith.constant 4 : i32
%v156 = func.call @make(%v155) : (i32) -> !llvm.struct<(!llvm.ptr, i64)>
%v157 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v158 = llvm.extractvalue %v156[0] : !llvm.struct<(!llvm.ptr, i64)>
%v159 = llvm.insertvalue %v158, %v157[0] : !llvm.struct<(!llvm.ptr, i64)>
%v160 = llvm.extractvalue %v156[1] : !llvm.struct<(!llvm.ptr, i64)>
%v161 = llvm.insertvalue %v160, %v159[1] : !llvm.struct<(!llvm.ptr, i64)>
%v162 = llvm.mlir.constant(1 : i64) : i64
%v163 = llvm.alloca %v162 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v161, %v163 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v164 = llvm.load %v163 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v165 = llvm.mlir.constant(1 : i64) : i64
%v166 = llvm.alloca %v165 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v164, %v166 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v167 = llvm.load %v166 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v168 = arith.constant 2.5 : f64
func.call @fill(%v167, %v168) : (!llvm.struct<(!llvm.ptr, i64)>, f64) -> ()
%v169 = llvm.load %v166 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v170 = llvm.extractvalue %v169[0] : !llvm.struct<(!llvm.ptr, i64)>
%v171 = arith.constant 1 : i32
%v172 = arith.constant 3 : i32
%v173 = arith.extsi %v171 : i32 to i64
%v174 = arith.extsi %v172 : i32 to i64
%v175 = llvm.getelementptr %v170[%v173] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v176 = arith.subi %v174, %v173 : i64
%v177 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v178 = llvm.insertvalue %v175, %v177[0] : !llvm.struct<(!llvm.ptr, i64)>
%v179 = llvm.insertvalue %v176, %v178[1] : !llvm.struct<(!llvm.ptr, i64)>
%v180 = llvm.mlir.constant(1 : i64) : i64
%v181 = llvm.alloca %v180 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v179, %v181 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v182 = arith.constant 2 : i32
%v183 = func.call @make(%v182) : (i32) -> !llvm.struct<(!llvm.ptr, i64)>
%v184 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v185 = llvm.extractvalue %v183[0] : !llvm.struct<(!llvm.ptr, i64)>
%v186 = llvm.insertvalue %v185, %v184[0] : !llvm.struct<(!llvm.ptr, i64)>
%v187 = llvm.extractvalue %v183[1] : !llvm.struct<(!llvm.ptr, i64)>
%v188 = llvm.insertvalue %v187, %v186[1] : !llvm.struct<(!llvm.ptr, i64)>
%v189 = llvm.mlir.constant(1 : i64) : i64
%v190 = llvm.alloca %v189 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v188, %v190 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v191 = llvm.load %v190 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v192 = llvm.mlir.constant(1 : i64) : i64
%v193 = llvm.alloca %v192 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v191, %v193 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v194 = llvm.load %v166 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
llvm.store %v194, %v193 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v195 = llvm.load %v181 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v196 = func.call @total(%v195) : (!llvm.struct<(!llvm.ptr, i64)>) -> f64
%v197 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v198 = llvm.call @printf(%v197, %v196) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v199 = arith.constant 0 : i32
%v200 = llvm.load %v193 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v201 = llvm.extractvalue %v200[1] : !llvm.struct<(!llvm.ptr, i64)>
%v202 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v203 = llvm.call @printf(%v202, %v201) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v204 = arith.constant 0 : i32
%v205 = llvm.load %v166 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v206 = llvm.extractvalue %v205[0] : !llvm.struct<(!llvm.ptr, i64)>
%v207 = arith.constant 0 : i32
%v208 = arith.constant 2 : i32
%v209 = arith.extsi %v207 : i32 to i64
%v210 = arith.extsi %v208 : i32 to i64
%v211 = llvm.getelementptr %v206[%v209] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v212 = arith.subi %v210, %v209 : i64
%v213 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v214 = llvm.insertvalue %v211, %v213[0] : !llvm.struct<(!llvm.ptr, i64)>
%v215 = llvm.insertvalue %v212, %v214[1] : !llvm.struct<(!llvm.ptr, i64)>
%v216 = func.call @total(%v215) : (!llvm.struct<(!llvm.ptr, i64)>) -> f64
%v217 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v218 = llvm.call @printf(%v217, %v216) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v219 = arith.constant 0 : i32
%v220 = arith.constant 7 : i32
%v221 = arith.constant 0 : index
%v222 = arith.constant 4 : index
%v223 = arith.constant 1 : index
%v224 = llvm.mlir.constant(1 : i64) : i64
%v225 = llvm.alloca %v224 x !llvm.array<4 x i32> : (i64) -> !llvm.ptr
scf.for %v226 = %v221 to %v222 step %v223 {
%v227 = arith.index_cast %v226 : index to i64
%v228 = llvm.getelementptr %v225[0, %v227] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x i32>
llvm.store %v220, %v228 : i32, !llvm.ptr
}
%v229 = arith.constant 2 : i32
%v230 = arith.extsi %v229 : i32 to i64
%v231 = llvm.getelementptr %v225[0, %v230] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x i32>
%v232 = llvm.load %v231 : !llvm.ptr -> i32
%v233 = arith.constant 7 : i32
%v234 = arith.constant 0 : index
%v235 = arith.constant 4 : index
%v236 = arith.constant 1 : index
%v237 = memref.alloca() : memref<4xi32>
scf.for %v238 = %v234 to %v235 step %v236 {
memref.store %v233, %v237[%v238] : memref<4xi32>
}
%v239 = memref.extract_aligned_pointer_as_index %v237 : memref<4xi32> -> index
%v240 = arith.index_cast %v239 : index to i64
%v241 = llvm.inttoptr %v240 : i64 to !llvm.ptr
%v242 = arith.constant 0 : index
%v243 = memref.dim %v237, %v242 : memref<4xi32>
%v244 = arith.index_cast %v243 : index to i64
%v245 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v246 = llvm.insertvalue %v241, %v245[0] : !llvm.struct<(!llvm.ptr, i64)>
%v247 = llvm.insertvalue %v244, %v246[1] : !llvm.struct<(!llvm.ptr, i64)>
%v248 = func.call @first4(%v247) : (!llvm.struct<(!llvm.ptr, i64)>) -> i32
%v249 = arith.addi %v232, %v248 : i32
%v250 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v251 = llvm.call @printf(%v250, %v249) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v252 = arith.constant 0 : i32
%v253 = arith.constant 8 : i32
%v254 = arith.index_cast %v253 : i32 to index
%v255 = memref.alloc(%v254) : memref<?xf32>
%v256 = arith.constant 8 : i32
%v257 = arith.index_cast %v256 : i32 to index
%v258 = memref.alloc(%v257) : memref<?xf32>
%v259 = arith.constant 0 : i32
%v260 = arith.constant 8 : i32
%v261 = arith.index_cast %v259 : i32 to index
%v262 = arith.index_cast %v260 : i32 to index
%v263 = arith.constant 1 : index
%v264 = arith.constant -1 : index
%v265 = arith.cmpi sle, %v261, %v262 : index
%v266 = arith.select %v265, %v263, %v264 : index
cf.br ^b10(%v261 : index)
^b10(%v267: index):
%v268 = arith.cmpi slt, %v267, %v262 : index
%v269 = arith.cmpi sgt, %v267, %v262 : index
%v270 = arith.select %v265, %v268, %v269 : i1
cf.cond_br %v270, ^b11(%v267 : index), ^b12(%v267 : index)
^b11(%v271: index):
%v272 = arith.constant 1.5 : f64
%v273 = arith.truncf %v272 : f64 to f32
memref.store %v273, %v258[%v271] : memref<?xf32>
%v274 = arith.constant 2.0 : f64
%v275 = arith.truncf %v274 : f64 to f32
memref.store %v275, %v255[%v271] : memref<?xf32>
%v276 = arith.addi %v271, %v266 : index
cf.br ^b10(%v276 : index)
^b12(%v277: index):
%v278 = arith.constant 8 : i32
%v279 = arith.constant 0.5 : f64
%v280 = arith.truncf %v279 : f64 to f32
func.call @scale(%v255, %v258, %v278, %v280) : (memref<?xf32>, memref<?xf32>, i32, f32) -> ()
%v281 = arith.constant 3 : i32
%v282 = arith.index_cast %v281 : i32 to index
%v283 = memref.load %v255[%v282] : memref<?xf32>
%v284 = arith.extf %v283 : f32 to f64
%v285 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v286 = llvm.call @printf(%v285, %v284) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v287 = arith.constant 0 : i32
%v288 = arith.constant 1.0 : f64
%v289 = arith.constant 2.0 : f64
%v290 = arith.constant 3.0 : f64
%v291 = arith.truncf %v288 : f64 to f32
%v292 = arith.truncf %v289 : f64 to f32
%v293 = arith.truncf %v290 : f64 to f32
%v294 = memref.alloca() : memref<3xf32>
%v295 = arith.constant 0 : index
memref.store %v291, %v294[%v295] : memref<3xf32>
%v296 = arith.constant 1 : index
memref.store %v292, %v294[%v296] : memref<3xf32>
%v297 = arith.constant 2 : index
memref.store %v293, %v294[%v297] : memref<3xf32>
%v298 = arith.constant 4.0 : f64
%v299 = arith.constant 5.0 : f64
%v300 = arith.constant 6.0 : f64
%v301 = arith.truncf %v298 : f64 to f32
%v302 = arith.truncf %v299 : f64 to f32
%v303 = arith.truncf %v300 : f64 to f32
%v304 = memref.alloca() : memref<3xf32>
%v305 = arith.constant 0 : index
memref.store %v301, %v304[%v305] : memref<3xf32>
%v306 = arith.constant 1 : index
memref.store %v302, %v304[%v306] : memref<3xf32>
%v307 = arith.constant 2 : index
memref.store %v303, %v304[%v307] : memref<3xf32>
%v308 = arith.constant 3 : i32
%v309 = memref.cast %v294 : memref<3xf32> to memref<?xf32>
%v310 = memref.cast %v304 : memref<3xf32> to memref<?xf32>
%v311 = func.call @dot(%v309, %v310, %v308) : (memref<?xf32>, memref<?xf32>, i32) -> f32
%v312 = arith.extf %v311 : f32 to f64
%v313 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v314 = llvm.call @printf(%v313, %v312) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v315 = arith.constant 0 : i32
%v316 = arith.constant 1 : i32
%v317 = arith.constant 2 : i32
%v318 = arith.constant 3 : i32
%v319 = llvm.mlir.constant(1 : i64) : i64
%v320 = llvm.alloca %v319 x !llvm.array<3 x i32> : (i64) -> !llvm.ptr
%v321 = llvm.mlir.zero : !llvm.array<3 x i32>
llvm.store %v321, %v320 : !llvm.array<3 x i32>, !llvm.ptr
%v322 = llvm.mlir.constant(0 : i64) : i64
%v323 = llvm.getelementptr %v320[0, %v322] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v316, %v323 : i32, !llvm.ptr
%v324 = llvm.mlir.constant(1 : i64) : i64
%v325 = llvm.getelementptr %v320[0, %v324] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v317, %v325 : i32, !llvm.ptr
%v326 = llvm.mlir.constant(2 : i64) : i64
%v327 = llvm.getelementptr %v320[0, %v326] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v318, %v327 : i32, !llvm.ptr
%v328 = arith.constant 0 : i32
%v329 = llvm.mlir.constant(1 : i64) : i64
%v330 = llvm.alloca %v329 x i32 : (i64) -> !llvm.ptr
llvm.store %v328, %v330 : i32, !llvm.ptr
%v331 = arith.constant 0 : i32
%v332 = arith.extsi %v331 : i32 to i64
%v333 = llvm.getelementptr %v320[0, %v332] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
%v334 = llvm.load %v333 : !llvm.ptr -> i32
%v335 = arith.constant 1 : i32
%v336 = arith.cmpi eq, %v334, %v335 : i32
%v337 = arith.constant 1 : i32
%v338 = arith.extsi %v337 : i32 to i64
%v339 = llvm.getelementptr %v320[0, %v338] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
%v340 = llvm.load %v339 : !llvm.ptr -> i32
%v341 = arith.constant 2 : i32
%v342 = arith.extsi %v341 : i32 to i64
%v343 = llvm.getelementptr %v320[0, %v342] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
%v344 = llvm.load %v343 : !llvm.ptr -> i32
cf.cond_br %v336, ^b13, ^b14
^b13:
%v345 = arith.addi %v340, %v344 : i32
llvm.store %v345, %v330 : i32, !llvm.ptr
cf.br ^b15
^b14:
%v346 = arith.constant 99 : i32
llvm.store %v346, %v330 : i32, !llvm.ptr
cf.br ^b15
^b15:
%v347 = llvm.load %v330 : !llvm.ptr -> i32
%v348 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v349 = llvm.call @printf(%v348, %v347) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v350 = arith.constant 0 : i32
%v351 = llvm.mlir.addressof @K : !llvm.ptr
%v352 = llvm.load %v351 : !llvm.ptr -> i32
%v353 = llvm.mlir.addressof @MASK : !llvm.ptr
%v354 = llvm.load %v353 : !llvm.ptr -> i32
%v355 = arith.addi %v352, %v354 : i32
%v356 = llvm.mlir.addressof @counter : !llvm.ptr
%v357 = llvm.load %v356 : !llvm.ptr -> i32
%v358 = arith.addi %v355, %v357 : i32
%v359 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v360 = llvm.call @printf(%v359, %v358) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v361 = arith.constant 0 : i32
%v362 = llvm.mlir.addressof @NEG : !llvm.ptr
%v363 = llvm.load %v362 : !llvm.ptr -> i64
%v364 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v365 = llvm.call @printf(%v364, %v363) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v366 = arith.constant 0 : i32
%v367 = arith.constant 1.5 : f64
%v368 = arith.constant 2.0 : f64
%v369 = arith.mulf %v367, %v368 : f64
%v370 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v371 = llvm.call @printf(%v370, %v369) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v372 = arith.constant 0 : i32
%v373 = arith.constant 0 : i32
func.return %v373 : i32
}
}
