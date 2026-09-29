module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%f\n\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_1("%d\n\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
func.func private @malloc(i64) -> !llvm.ptr
// Constant: K
llvm.mlir.global internal constant @K(3 : i32) : i32
// Constant: MASK
llvm.mlir.global internal constant @MASK(16 : i32) : i32
// Constant: NEG
llvm.mlir.global internal constant @NEG(-5 : i64) : i64
// Constant: ZERO_F
llvm.mlir.global internal constant @ZERO_F(0.0 : f64) : f64
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
%v8 = arith.constant 0.0 : f32
%v9 = arith.extf %v8 : f32 to f64
%v10 = llvm.mlir.constant(1 : i64) : i64
%v11 = llvm.alloca %v10 x f64 : (i64) -> !llvm.ptr
llvm.store %v9, %v11 : f64, !llvm.ptr
%v12 = arith.constant 0 : i32
%v13 = llvm.mlir.constant(1 : i64) : i64
%v14 = llvm.alloca %v13 x i32 : (i64) -> !llvm.ptr
llvm.store %v12, %v14 : i32, !llvm.ptr
cf.br ^b1
^b1:
%v15 = llvm.load %v14 : !llvm.ptr -> i32
%v16 = llvm.load %v7 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v17 = llvm.extractvalue %v16[1] : !llvm.struct<(!llvm.ptr, i64)>
%v18 = arith.extsi %v15 : i32 to i64
%v19 = arith.cmpi slt, %v18, %v17 : i64
cf.cond_br %v19, ^b2, ^b3
^b2:
%v20 = llvm.load %v11 : !llvm.ptr -> f64
%v21 = llvm.load %v7 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v22 = llvm.load %v14 : !llvm.ptr -> i32
%v23 = llvm.extractvalue %v21[0] : !llvm.struct<(!llvm.ptr, i64)>
%v24 = arith.extsi %v22 : i32 to i64
%v25 = llvm.getelementptr %v23[%v24] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v26 = llvm.load %v25 : !llvm.ptr -> f64
%v27 = arith.addf %v20, %v26 : f64
llvm.store %v27, %v11 : f64, !llvm.ptr
%v28 = llvm.load %v14 : !llvm.ptr -> i32
%v29 = arith.constant 1 : i32
%v30 = arith.addi %v28, %v29 : i32
llvm.store %v30, %v14 : i32, !llvm.ptr
cf.br ^b1
^b3:
%v31 = llvm.load %v11 : !llvm.ptr -> f64
func.return %v31 : f64
}
func.func @fill(%arg0: !llvm.struct<(!llvm.ptr, i64)>, %arg1: f64) -> () {
%v32 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v33 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i64)>
%v34 = llvm.insertvalue %v33, %v32[0] : !llvm.struct<(!llvm.ptr, i64)>
%v35 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i64)>
%v36 = llvm.insertvalue %v35, %v34[1] : !llvm.struct<(!llvm.ptr, i64)>
%v37 = llvm.mlir.constant(1 : i64) : i64
%v38 = llvm.alloca %v37 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v36, %v38 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v39 = arith.constant 0 : i32
%v40 = arith.extsi %v39 : i32 to i64
%v41 = llvm.mlir.constant(1 : i64) : i64
%v42 = llvm.alloca %v41 x i64 : (i64) -> !llvm.ptr
llvm.store %v40, %v42 : i64, !llvm.ptr
cf.br ^b4
^b4:
%v43 = llvm.load %v42 : !llvm.ptr -> i64
%v44 = llvm.load %v38 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v45 = llvm.extractvalue %v44[1] : !llvm.struct<(!llvm.ptr, i64)>
%v46 = arith.cmpi slt, %v43, %v45 : i64
cf.cond_br %v46, ^b5, ^b6
^b5:
%v47 = llvm.load %v38 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v48 = llvm.load %v42 : !llvm.ptr -> i64
%v49 = llvm.extractvalue %v47[0] : !llvm.struct<(!llvm.ptr, i64)>
%v50 = llvm.getelementptr %v49[%v48] : (!llvm.ptr, i64) -> !llvm.ptr, f64
llvm.store %arg1, %v50 : f64, !llvm.ptr
%v51 = llvm.load %v42 : !llvm.ptr -> i64
%v52 = arith.constant 1 : i32
%v53 = arith.extsi %v52 : i32 to i64
%v54 = arith.addi %v51, %v53 : i64
llvm.store %v54, %v42 : i64, !llvm.ptr
cf.br ^b4
^b6:
func.return
}
func.func @make(%arg0: i32) -> !llvm.struct<(!llvm.ptr, i64)> {
%v55 = arith.extsi %arg0 : i32 to i64
%v56 = arith.constant 8 : i32
%v57 = arith.extsi %v56 : i32 to i64
%v58 = arith.muli %v55, %v57 : i64
%v59 = func.call @malloc(%v58) : (i64) -> !llvm.ptr
%v60 = arith.constant 0 : i32
%v61 = arith.extsi %v60 : i32 to i64
%v62 = arith.extsi %arg0 : i32 to i64
%v63 = llvm.getelementptr %v59[%v61] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v64 = arith.subi %v62, %v61 : i64
%v65 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v66 = llvm.insertvalue %v63, %v65[0] : !llvm.struct<(!llvm.ptr, i64)>
%v67 = llvm.insertvalue %v64, %v66[1] : !llvm.struct<(!llvm.ptr, i64)>
%v68 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v69 = llvm.extractvalue %v67[0] : !llvm.struct<(!llvm.ptr, i64)>
%v70 = llvm.insertvalue %v69, %v68[0] : !llvm.struct<(!llvm.ptr, i64)>
%v71 = llvm.extractvalue %v67[1] : !llvm.struct<(!llvm.ptr, i64)>
%v72 = llvm.insertvalue %v71, %v70[1] : !llvm.struct<(!llvm.ptr, i64)>
%v73 = llvm.mlir.constant(1 : i64) : i64
%v74 = llvm.alloca %v73 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v72, %v74 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v75 = llvm.load %v74 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
func.return %v75 : !llvm.struct<(!llvm.ptr, i64)>
}
func.func @first4(%arg0: !llvm.struct<(!llvm.ptr, i64)>) -> i32 {
%v76 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v77 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i64)>
%v78 = llvm.insertvalue %v77, %v76[0] : !llvm.struct<(!llvm.ptr, i64)>
%v79 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i64)>
%v80 = llvm.insertvalue %v79, %v78[1] : !llvm.struct<(!llvm.ptr, i64)>
%v81 = llvm.mlir.constant(1 : i64) : i64
%v82 = llvm.alloca %v81 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v80, %v82 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v83 = llvm.load %v82 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v84 = arith.constant 0 : i32
%v85 = llvm.extractvalue %v83[0] : !llvm.struct<(!llvm.ptr, i64)>
%v86 = arith.extsi %v84 : i32 to i64
%v87 = llvm.getelementptr %v85[%v86] : (!llvm.ptr, i64) -> !llvm.ptr, i32
%v88 = llvm.load %v87 : !llvm.ptr -> i32
%v89 = llvm.load %v82 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v90 = arith.constant 3 : i32
%v91 = llvm.extractvalue %v89[0] : !llvm.struct<(!llvm.ptr, i64)>
%v92 = arith.extsi %v90 : i32 to i64
%v93 = llvm.getelementptr %v91[%v92] : (!llvm.ptr, i64) -> !llvm.ptr, i32
%v94 = llvm.load %v93 : !llvm.ptr -> i32
%v95 = arith.addi %v88, %v94 : i32
func.return %v95 : i32
}
func.func @scale(%arg0: memref<?xf32>, %arg1: memref<?xf32>, %arg2: i32, %arg3: f32) -> () {
// flow: vectorized elementwise f32 loop (VF=4)
%v96 = arith.constant 0 : i32
%v97 = arith.index_cast %v96 : i32 to index
%v98 = arith.index_cast %arg2 : i32 to index
%v99 = arith.constant 1 : index
%v100 = arith.constant 4 : index
%v101 = arith.subi %v98, %v97 : index
%v102 = arith.remsi %v101, %v100 : index
%v103 = arith.subi %v101, %v102 : index
%v104 = arith.addi %v97, %v103 : index
scf.for %v105 = %v97 to %v104 step %v100 {
%v106 = arith.constant 0.0 : f32
%v107 = vector.transfer_read %arg1[%v105], %v106 {in_bounds = [true]} : memref<?xf32>, vector<4xf32>
%v108 = arith.negf %v107 : vector<4xf32>
%v109 = vector.broadcast %arg3 : f32 to vector<4xf32>
%v110 = arith.mulf %v108, %v109 : vector<4xf32>
%v111 = arith.constant 2.0 : f32
%v112 = vector.broadcast %v111 : f32 to vector<4xf32>
%v113 = arith.addf %v110, %v112 : vector<4xf32>
%v114 = arith.constant 0.0 : f32
%v115 = vector.transfer_read %arg0[%v105], %v114 {in_bounds = [true]} : memref<?xf32>, vector<4xf32>
%v116 = arith.constant 4.0 : f32
%v117 = vector.broadcast %v116 : f32 to vector<4xf32>
%v118 = arith.divf %v115, %v117 : vector<4xf32>
%v119 = arith.subf %v113, %v118 : vector<4xf32>
vector.transfer_write %v119, %arg0[%v105] {in_bounds = [true]} : vector<4xf32>, memref<?xf32>
}
scf.for %v120 = %v104 to %v98 step %v99 {
%v121 = memref.load %arg1[%v120] : memref<?xf32>
%v122 = arith.negf %v121 : f32
%v123 = arith.mulf %v122, %arg3 : f32
%v124 = arith.constant 2.0 : f32
%v125 = arith.addf %v123, %v124 : f32
%v126 = memref.load %arg0[%v120] : memref<?xf32>
%v127 = arith.constant 4.0 : f32
%v128 = arith.divf %v126, %v127 : f32
%v129 = arith.subf %v125, %v128 : f32
memref.store %v129, %arg0[%v120] : memref<?xf32>
}
func.return
}
func.func @dot(%arg0: memref<?xf32>, %arg1: memref<?xf32>, %arg2: i32) -> f32 {
%v130 = arith.constant 0.0 : f32
%v131 = llvm.mlir.constant(1 : i64) : i64
%v132 = llvm.alloca %v131 x f32 : (i64) -> !llvm.ptr
llvm.store %v130, %v132 : f32, !llvm.ptr
%v133 = arith.constant 0 : i32
%v134 = arith.index_cast %v133 : i32 to index
%v135 = arith.index_cast %arg2 : i32 to index
%v136 = arith.constant 1 : index
%v137 = arith.constant -1 : index
%v138 = arith.cmpi sle, %v134, %v135 : index
%v139 = arith.select %v138, %v136, %v137 : index
cf.br ^b7(%v134 : index)
^b7(%v140: index):
%v141 = arith.cmpi slt, %v140, %v135 : index
%v142 = arith.cmpi sgt, %v140, %v135 : index
%v143 = arith.select %v138, %v141, %v142 : i1
cf.cond_br %v143, ^b8(%v140 : index), ^b9(%v140 : index)
^b8(%v144: index):
%v145 = llvm.load %v132 : !llvm.ptr -> f32
%v146 = memref.load %arg0[%v144] : memref<?xf32>
%v147 = memref.load %arg1[%v144] : memref<?xf32>
%v148 = arith.mulf %v146, %v147 : f32
%v149 = arith.addf %v145, %v148 : f32
llvm.store %v149, %v132 : f32, !llvm.ptr
%v150 = arith.addi %v144, %v139 : index
cf.br ^b7(%v150 : index)
^b9(%v151: index):
%v152 = llvm.load %v132 : !llvm.ptr -> f32
func.return %v152 : f32
}
func.func @main() -> i32 {
%v153 = arith.constant 4 : i32
%v154 = func.call @make(%v153) : (i32) -> !llvm.struct<(!llvm.ptr, i64)>
%v155 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v156 = llvm.extractvalue %v154[0] : !llvm.struct<(!llvm.ptr, i64)>
%v157 = llvm.insertvalue %v156, %v155[0] : !llvm.struct<(!llvm.ptr, i64)>
%v158 = llvm.extractvalue %v154[1] : !llvm.struct<(!llvm.ptr, i64)>
%v159 = llvm.insertvalue %v158, %v157[1] : !llvm.struct<(!llvm.ptr, i64)>
%v160 = llvm.mlir.constant(1 : i64) : i64
%v161 = llvm.alloca %v160 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v159, %v161 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v162 = llvm.load %v161 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v163 = llvm.mlir.constant(1 : i64) : i64
%v164 = llvm.alloca %v163 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v162, %v164 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v165 = llvm.load %v164 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v166 = arith.constant 2.5 : f32
%v167 = arith.extf %v166 : f32 to f64
func.call @fill(%v165, %v167) : (!llvm.struct<(!llvm.ptr, i64)>, f64) -> ()
%v168 = llvm.load %v164 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v169 = llvm.extractvalue %v168[0] : !llvm.struct<(!llvm.ptr, i64)>
%v170 = arith.constant 1 : i32
%v171 = arith.constant 3 : i32
%v172 = arith.extsi %v170 : i32 to i64
%v173 = arith.extsi %v171 : i32 to i64
%v174 = llvm.getelementptr %v169[%v172] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v175 = arith.subi %v173, %v172 : i64
%v176 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v177 = llvm.insertvalue %v174, %v176[0] : !llvm.struct<(!llvm.ptr, i64)>
%v178 = llvm.insertvalue %v175, %v177[1] : !llvm.struct<(!llvm.ptr, i64)>
%v179 = llvm.mlir.constant(1 : i64) : i64
%v180 = llvm.alloca %v179 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v178, %v180 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v181 = arith.constant 2 : i32
%v182 = func.call @make(%v181) : (i32) -> !llvm.struct<(!llvm.ptr, i64)>
%v183 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v184 = llvm.extractvalue %v182[0] : !llvm.struct<(!llvm.ptr, i64)>
%v185 = llvm.insertvalue %v184, %v183[0] : !llvm.struct<(!llvm.ptr, i64)>
%v186 = llvm.extractvalue %v182[1] : !llvm.struct<(!llvm.ptr, i64)>
%v187 = llvm.insertvalue %v186, %v185[1] : !llvm.struct<(!llvm.ptr, i64)>
%v188 = llvm.mlir.constant(1 : i64) : i64
%v189 = llvm.alloca %v188 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v187, %v189 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v190 = llvm.load %v189 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v191 = llvm.mlir.constant(1 : i64) : i64
%v192 = llvm.alloca %v191 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v190, %v192 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v193 = llvm.load %v164 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
llvm.store %v193, %v192 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v194 = llvm.load %v180 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v195 = func.call @total(%v194) : (!llvm.struct<(!llvm.ptr, i64)>) -> f64
%v196 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v197 = llvm.call @printf(%v196, %v195) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v198 = arith.constant 0 : i32
%v199 = llvm.load %v192 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v200 = llvm.extractvalue %v199[1] : !llvm.struct<(!llvm.ptr, i64)>
%v201 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v202 = llvm.call @printf(%v201, %v200) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v203 = arith.constant 0 : i32
%v204 = llvm.load %v164 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v205 = llvm.extractvalue %v204[0] : !llvm.struct<(!llvm.ptr, i64)>
%v206 = arith.constant 0 : i32
%v207 = arith.constant 2 : i32
%v208 = arith.extsi %v206 : i32 to i64
%v209 = arith.extsi %v207 : i32 to i64
%v210 = llvm.getelementptr %v205[%v208] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v211 = arith.subi %v209, %v208 : i64
%v212 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v213 = llvm.insertvalue %v210, %v212[0] : !llvm.struct<(!llvm.ptr, i64)>
%v214 = llvm.insertvalue %v211, %v213[1] : !llvm.struct<(!llvm.ptr, i64)>
%v215 = func.call @total(%v214) : (!llvm.struct<(!llvm.ptr, i64)>) -> f64
%v216 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v217 = llvm.call @printf(%v216, %v215) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v218 = arith.constant 0 : i32
%v219 = arith.constant 7 : i32
%v220 = arith.constant 7 : i32
%v221 = arith.constant 7 : i32
%v222 = arith.constant 7 : i32
%v223 = llvm.mlir.constant(1 : i64) : i64
%v224 = llvm.alloca %v223 x !llvm.array<4 x i32> : (i64) -> !llvm.ptr
%v225 = llvm.mlir.zero : !llvm.array<4 x i32>
llvm.store %v225, %v224 : !llvm.array<4 x i32>, !llvm.ptr
%v226 = llvm.mlir.constant(0 : i64) : i64
%v227 = llvm.getelementptr %v224[0, %v226] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x i32>
llvm.store %v219, %v227 : i32, !llvm.ptr
%v228 = llvm.mlir.constant(1 : i64) : i64
%v229 = llvm.getelementptr %v224[0, %v228] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x i32>
llvm.store %v220, %v229 : i32, !llvm.ptr
%v230 = llvm.mlir.constant(2 : i64) : i64
%v231 = llvm.getelementptr %v224[0, %v230] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x i32>
llvm.store %v221, %v231 : i32, !llvm.ptr
%v232 = llvm.mlir.constant(3 : i64) : i64
%v233 = llvm.getelementptr %v224[0, %v232] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x i32>
llvm.store %v222, %v233 : i32, !llvm.ptr
%v234 = arith.constant 2 : i32
%v235 = arith.extsi %v234 : i32 to i64
%v236 = llvm.getelementptr %v224[0, %v235] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x i32>
%v237 = llvm.load %v236 : !llvm.ptr -> i32
%v238 = arith.constant 7 : i32
%v239 = arith.constant 7 : i32
%v240 = arith.constant 7 : i32
%v241 = arith.constant 7 : i32
%v242 = memref.alloca() : memref<4xi32>
%v243 = arith.constant 0 : index
memref.store %v238, %v242[%v243] : memref<4xi32>
%v244 = arith.constant 1 : index
memref.store %v239, %v242[%v244] : memref<4xi32>
%v245 = arith.constant 2 : index
memref.store %v240, %v242[%v245] : memref<4xi32>
%v246 = arith.constant 3 : index
memref.store %v241, %v242[%v246] : memref<4xi32>
%v247 = memref.extract_aligned_pointer_as_index %v242 : memref<4xi32> -> index
%v248 = arith.index_cast %v247 : index to i64
%v249 = llvm.inttoptr %v248 : i64 to !llvm.ptr
%v250 = arith.constant 0 : index
%v251 = memref.dim %v242, %v250 : memref<4xi32>
%v252 = arith.index_cast %v251 : index to i64
%v253 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v254 = llvm.insertvalue %v249, %v253[0] : !llvm.struct<(!llvm.ptr, i64)>
%v255 = llvm.insertvalue %v252, %v254[1] : !llvm.struct<(!llvm.ptr, i64)>
%v256 = func.call @first4(%v255) : (!llvm.struct<(!llvm.ptr, i64)>) -> i32
%v257 = arith.addi %v237, %v256 : i32
%v258 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v259 = llvm.call @printf(%v258, %v257) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v260 = arith.constant 0 : i32
%v261 = arith.constant 8 : i32
%v262 = arith.index_cast %v261 : i32 to index
%v263 = memref.alloc(%v262) : memref<?xf32>
%v264 = arith.constant 8 : i32
%v265 = arith.index_cast %v264 : i32 to index
%v266 = memref.alloc(%v265) : memref<?xf32>
%v267 = arith.constant 0 : i32
%v268 = arith.constant 8 : i32
%v269 = arith.index_cast %v267 : i32 to index
%v270 = arith.index_cast %v268 : i32 to index
%v271 = arith.constant 1 : index
%v272 = arith.constant -1 : index
%v273 = arith.cmpi sle, %v269, %v270 : index
%v274 = arith.select %v273, %v271, %v272 : index
cf.br ^b10(%v269 : index)
^b10(%v275: index):
%v276 = arith.cmpi slt, %v275, %v270 : index
%v277 = arith.cmpi sgt, %v275, %v270 : index
%v278 = arith.select %v273, %v276, %v277 : i1
cf.cond_br %v278, ^b11(%v275 : index), ^b12(%v275 : index)
^b11(%v279: index):
%v280 = arith.constant 1.5 : f32
memref.store %v280, %v266[%v279] : memref<?xf32>
%v281 = arith.constant 2.0 : f32
memref.store %v281, %v263[%v279] : memref<?xf32>
%v282 = arith.addi %v279, %v274 : index
cf.br ^b10(%v282 : index)
^b12(%v283: index):
%v284 = arith.constant 8 : i32
%v285 = arith.constant 0.5 : f32
func.call @scale(%v263, %v266, %v284, %v285) : (memref<?xf32>, memref<?xf32>, i32, f32) -> ()
%v286 = arith.constant 3 : i32
%v287 = arith.index_cast %v286 : i32 to index
%v288 = memref.load %v263[%v287] : memref<?xf32>
%v289 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v290 = arith.extf %v288 : f32 to f64
%v291 = llvm.call @printf(%v289, %v290) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v292 = arith.constant 0 : i32
%v293 = arith.constant 1.0 : f32
%v294 = arith.constant 2.0 : f32
%v295 = arith.constant 3.0 : f32
%v296 = memref.alloca() : memref<3xf32>
%v297 = arith.constant 0 : index
memref.store %v293, %v296[%v297] : memref<3xf32>
%v298 = arith.constant 1 : index
memref.store %v294, %v296[%v298] : memref<3xf32>
%v299 = arith.constant 2 : index
memref.store %v295, %v296[%v299] : memref<3xf32>
%v300 = arith.constant 4.0 : f32
%v301 = arith.constant 5.0 : f32
%v302 = arith.constant 6.0 : f32
%v303 = memref.alloca() : memref<3xf32>
%v304 = arith.constant 0 : index
memref.store %v300, %v303[%v304] : memref<3xf32>
%v305 = arith.constant 1 : index
memref.store %v301, %v303[%v305] : memref<3xf32>
%v306 = arith.constant 2 : index
memref.store %v302, %v303[%v306] : memref<3xf32>
%v307 = arith.constant 3 : i32
%v308 = memref.cast %v296 : memref<3xf32> to memref<?xf32>
%v309 = memref.cast %v303 : memref<3xf32> to memref<?xf32>
%v310 = func.call @dot(%v308, %v309, %v307) : (memref<?xf32>, memref<?xf32>, i32) -> f32
%v311 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v312 = arith.extf %v310 : f32 to f64
%v313 = llvm.call @printf(%v311, %v312) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v314 = arith.constant 0 : i32
%v315 = arith.constant 1 : i32
%v316 = arith.constant 2 : i32
%v317 = arith.constant 3 : i32
%v318 = llvm.mlir.constant(1 : i64) : i64
%v319 = llvm.alloca %v318 x !llvm.array<3 x i32> : (i64) -> !llvm.ptr
%v320 = llvm.mlir.zero : !llvm.array<3 x i32>
llvm.store %v320, %v319 : !llvm.array<3 x i32>, !llvm.ptr
%v321 = llvm.mlir.constant(0 : i64) : i64
%v322 = llvm.getelementptr %v319[0, %v321] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v315, %v322 : i32, !llvm.ptr
%v323 = llvm.mlir.constant(1 : i64) : i64
%v324 = llvm.getelementptr %v319[0, %v323] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v316, %v324 : i32, !llvm.ptr
%v325 = llvm.mlir.constant(2 : i64) : i64
%v326 = llvm.getelementptr %v319[0, %v325] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v317, %v326 : i32, !llvm.ptr
%v327 = arith.constant 0 : i32
%v328 = llvm.mlir.constant(1 : i64) : i64
%v329 = llvm.alloca %v328 x i32 : (i64) -> !llvm.ptr
llvm.store %v327, %v329 : i32, !llvm.ptr
%v330 = arith.constant 0 : i32
%v331 = arith.extsi %v330 : i32 to i64
%v332 = llvm.getelementptr %v319[0, %v331] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
%v333 = llvm.load %v332 : !llvm.ptr -> i32
%v334 = arith.constant 1 : i32
%v335 = arith.cmpi eq, %v333, %v334 : i32
%v336 = arith.constant 1 : i32
%v337 = arith.extsi %v336 : i32 to i64
%v338 = llvm.getelementptr %v319[0, %v337] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
%v339 = llvm.load %v338 : !llvm.ptr -> i32
%v340 = arith.constant 2 : i32
%v341 = arith.extsi %v340 : i32 to i64
%v342 = llvm.getelementptr %v319[0, %v341] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
%v343 = llvm.load %v342 : !llvm.ptr -> i32
cf.cond_br %v335, ^b13, ^b14
^b13:
%v344 = arith.addi %v339, %v343 : i32
llvm.store %v344, %v329 : i32, !llvm.ptr
cf.br ^b15
^b14:
%v345 = arith.constant 99 : i32
llvm.store %v345, %v329 : i32, !llvm.ptr
cf.br ^b15
^b15:
%v346 = llvm.load %v329 : !llvm.ptr -> i32
%v347 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v348 = llvm.call @printf(%v347, %v346) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v349 = arith.constant 0 : i32
%v350 = llvm.mlir.addressof @K : !llvm.ptr
%v351 = llvm.load %v350 : !llvm.ptr -> i32
%v352 = llvm.mlir.addressof @MASK : !llvm.ptr
%v353 = llvm.load %v352 : !llvm.ptr -> i32
%v354 = arith.addi %v351, %v353 : i32
%v355 = llvm.mlir.addressof @counter : !llvm.ptr
%v356 = llvm.load %v355 : !llvm.ptr -> i32
%v357 = arith.addi %v354, %v356 : i32
%v358 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v359 = llvm.call @printf(%v358, %v357) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v360 = arith.constant 0 : i32
%v361 = llvm.mlir.addressof @NEG : !llvm.ptr
%v362 = llvm.load %v361 : !llvm.ptr -> i64
%v363 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v364 = llvm.call @printf(%v363, %v362) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v365 = arith.constant 0 : i32
%v366 = llvm.mlir.addressof @ZERO_F : !llvm.ptr
%v367 = llvm.load %v366 : !llvm.ptr -> f64
%v368 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v369 = llvm.call @printf(%v368, %v367) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v370 = arith.constant 0 : i32
%v371 = arith.constant 0 : i32
func.return %v371 : i32
}
}
