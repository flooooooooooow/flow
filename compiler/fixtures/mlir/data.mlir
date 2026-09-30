module {
func.func private @malloc(i64) -> !llvm.ptr
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_1("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
// Struct: P
// Fields:
//   x: i32
//   y: f32
// Struct: Box
// Fields:
//   vals: memref<4xi32>
//   n: i32
func.func @sum(%arg0: !llvm.ptr) -> i32 {
%v1 = arith.constant 0 : i32
%v2 = llvm.mlir.constant(1 : i64) : i64
%v3 = llvm.alloca %v2 x i32 : (i64) -> !llvm.ptr
llvm.store %v1, %v3 : i32, !llvm.ptr
%v4 = arith.constant 0 : i32
%v5 = arith.constant 3 : i32
%v6 = arith.index_cast %v4 : i32 to index
%v7 = arith.index_cast %v5 : i32 to index
%v8 = arith.constant 1 : index
%v9 = arith.constant -1 : index
%v10 = arith.cmpi sle, %v6, %v7 : index
%v11 = arith.select %v10, %v8, %v9 : index
cf.br ^b1(%v6 : index)
^b1(%v12: index):
%v13 = arith.cmpi slt, %v12, %v7 : index
%v14 = arith.cmpi sgt, %v12, %v7 : index
%v15 = arith.select %v10, %v13, %v14 : i1
cf.cond_br %v15, ^b2(%v12 : index), ^b3(%v12 : index)
^b2(%v16: index):
%v17 = llvm.load %v3 : !llvm.ptr -> i32
%v18 = arith.index_cast %v16 : index to i64
%v19 = llvm.getelementptr %arg0[0, %v18] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
%v20 = llvm.load %v19 : !llvm.ptr -> !llvm.struct<(i32, f32)>
%v21 = arith.index_cast %v16 : index to i64
%v22 = llvm.getelementptr %arg0[0, %v21] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
%v23 = llvm.getelementptr %v22[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, f32)>
%v24 = llvm.load %v23 : !llvm.ptr -> i32
%v25 = arith.addi %v17, %v24 : i32
llvm.store %v25, %v3 : i32, !llvm.ptr
%v26 = arith.addi %v16, %v11 : index
cf.br ^b1(%v26 : index)
^b3(%v27: index):
%v28 = llvm.load %v3 : !llvm.ptr -> i32
func.return %v28 : i32
}
func.func @add4(%arg0: !llvm.ptr, %arg1: !llvm.ptr, %arg2: !llvm.ptr, %arg3: i32) -> () {
%v29 = arith.constant 0 : i32
%v30 = arith.index_cast %v29 : i32 to index
%v31 = arith.index_cast %arg3 : i32 to index
%v32 = arith.constant 1 : index
%v33 = arith.constant -1 : index
%v34 = arith.cmpi sle, %v30, %v31 : index
%v35 = arith.select %v34, %v32, %v33 : index
cf.br ^b4(%v30 : index)
^b4(%v36: index):
%v37 = arith.cmpi slt, %v36, %v31 : index
%v38 = arith.cmpi sgt, %v36, %v31 : index
%v39 = arith.select %v34, %v37, %v38 : i1
cf.cond_br %v39, ^b5(%v36 : index), ^b6(%v36 : index)
^b5(%v40: index):
%v41 = arith.index_cast %v40 : index to i64
%v42 = llvm.getelementptr %arg1[%v41] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v43 = llvm.load %v42 : !llvm.ptr -> f32
%v44 = arith.index_cast %v40 : index to i64
%v45 = llvm.getelementptr %arg2[%v44] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v46 = llvm.load %v45 : !llvm.ptr -> f32
%v47 = arith.addf %v43, %v46 : f32
%v48 = arith.index_cast %v40 : index to i64
%v49 = llvm.getelementptr %arg0[%v48] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v47, %v49 : f32, !llvm.ptr
%v50 = arith.addi %v40, %v35 : index
cf.br ^b4(%v50 : index)
^b6(%v51: index):
func.return
}
func.func @main() -> i32 {
%v52 = llvm.mlir.undef : !llvm.struct<(i32, f32)>
%v53 = arith.constant 1 : i32
%v54 = llvm.insertvalue %v53, %v52[0] : !llvm.struct<(i32, f32)>
%v55 = arith.constant 1.0 : f64
%v56 = arith.truncf %v55 : f64 to f32
%v57 = llvm.insertvalue %v56, %v54[1] : !llvm.struct<(i32, f32)>
%v58 = llvm.mlir.undef : !llvm.struct<(i32, f32)>
%v59 = arith.constant 2 : i32
%v60 = llvm.insertvalue %v59, %v58[0] : !llvm.struct<(i32, f32)>
%v61 = arith.constant 2.0 : f64
%v62 = arith.truncf %v61 : f64 to f32
%v63 = llvm.insertvalue %v62, %v60[1] : !llvm.struct<(i32, f32)>
%v64 = llvm.mlir.undef : !llvm.struct<(i32, f32)>
%v65 = arith.constant 3 : i32
%v66 = llvm.insertvalue %v65, %v64[0] : !llvm.struct<(i32, f32)>
%v67 = arith.constant 3.0 : f64
%v68 = arith.truncf %v67 : f64 to f32
%v69 = llvm.insertvalue %v68, %v66[1] : !llvm.struct<(i32, f32)>
%v70 = llvm.mlir.constant(1 : i64) : i64
%v71 = llvm.alloca %v70 x !llvm.array<3 x !llvm.struct<(i32, f32)>> : (i64) -> !llvm.ptr
%v72 = llvm.mlir.zero : !llvm.array<3 x !llvm.struct<(i32, f32)>>
llvm.store %v72, %v71 : !llvm.array<3 x !llvm.struct<(i32, f32)>>, !llvm.ptr
%v73 = llvm.mlir.constant(0 : i64) : i64
%v74 = llvm.getelementptr %v71[0, %v73] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
llvm.store %v57, %v74 : !llvm.struct<(i32, f32)>, !llvm.ptr
%v75 = llvm.mlir.constant(1 : i64) : i64
%v76 = llvm.getelementptr %v71[0, %v75] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
llvm.store %v63, %v76 : !llvm.struct<(i32, f32)>, !llvm.ptr
%v77 = llvm.mlir.constant(2 : i64) : i64
%v78 = llvm.getelementptr %v71[0, %v77] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
llvm.store %v69, %v78 : !llvm.struct<(i32, f32)>, !llvm.ptr
%v79 = llvm.mlir.constant(1 : i64) : i64
%v80 = llvm.alloca %v79 x !llvm.ptr : (i64) -> !llvm.ptr
llvm.store %v71, %v80 : !llvm.ptr, !llvm.ptr
%v81 = arith.constant 20 : i32
%v82 = llvm.load %v80 : !llvm.ptr -> !llvm.ptr
%v83 = arith.constant 1 : i32
%v84 = arith.extsi %v83 : i32 to i64
%v85 = llvm.getelementptr %v82[0, %v84] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
%v86 = llvm.getelementptr %v85[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, f32)>
llvm.store %v81, %v86 : i32, !llvm.ptr
%v87 = llvm.load %v80 : !llvm.ptr -> !llvm.ptr
%v88 = arith.constant 2 : i32
%v89 = arith.extsi %v88 : i32 to i64
%v90 = llvm.getelementptr %v87[0, %v89] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
%v91 = llvm.load %v90 : !llvm.ptr -> !llvm.struct<(i32, f32)>
%v92 = llvm.mlir.constant(1 : i64) : i64
%v93 = llvm.alloca %v92 x !llvm.struct<(i32, f32)> : (i64) -> !llvm.ptr
llvm.store %v91, %v93 : !llvm.struct<(i32, f32)>, !llvm.ptr
%v94 = llvm.mlir.undef : !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v95 = llvm.mlir.zero : !llvm.array<4 x i32>
%v96 = arith.constant 1 : i32
%v97 = llvm.insertvalue %v96, %v95[0] : !llvm.array<4 x i32>
%v98 = arith.constant 2 : i32
%v99 = llvm.insertvalue %v98, %v97[1] : !llvm.array<4 x i32>
%v100 = arith.constant 3 : i32
%v101 = llvm.insertvalue %v100, %v99[2] : !llvm.array<4 x i32>
%v102 = arith.constant 4 : i32
%v103 = llvm.insertvalue %v102, %v101[3] : !llvm.array<4 x i32>
%v104 = llvm.insertvalue %v103, %v94[0] : !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v105 = arith.constant 4 : i32
%v106 = llvm.insertvalue %v105, %v104[1] : !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v107 = llvm.mlir.constant(1 : i64) : i64
%v108 = llvm.alloca %v107 x !llvm.struct<(!llvm.array<4 x i32>, i32)> : (i64) -> !llvm.ptr
llvm.store %v106, %v108 : !llvm.struct<(!llvm.array<4 x i32>, i32)>, !llvm.ptr
%v109 = llvm.load %v80 : !llvm.ptr -> !llvm.ptr
%v110 = func.call @sum(%v109) : (!llvm.ptr) -> i32
%v111 = llvm.load %v93 : !llvm.ptr -> !llvm.struct<(i32, f32)>
%v112 = llvm.getelementptr %v93[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, f32)>
%v113 = llvm.load %v112 : !llvm.ptr -> i32
%v114 = arith.addi %v110, %v113 : i32
%v115 = llvm.load %v108 : !llvm.ptr -> !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v116 = llvm.getelementptr %v108[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v117 = arith.constant 3 : i32
%v118 = arith.extsi %v117 : i32 to i64
%v119 = llvm.getelementptr %v116[0, %v118] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x i32>
%v120 = llvm.load %v119 : !llvm.ptr -> i32
%v121 = arith.addi %v114, %v120 : i32
%v122 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v123 = llvm.call @printf(%v122, %v121) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v124 = arith.constant 0 : i32
%v125 = memref.alloca() {type = memref<8xi32>} : memref<8xi32>
%v126 = arith.constant 0 : i32
%v127 = arith.constant 8 : i32
%v128 = arith.index_cast %v126 : i32 to index
%v129 = arith.index_cast %v127 : i32 to index
%v130 = arith.constant 1 : index
%v131 = arith.constant -1 : index
%v132 = arith.cmpi sle, %v128, %v129 : index
%v133 = arith.select %v132, %v130, %v131 : index
cf.br ^b7(%v128 : index)
^b7(%v134: index):
%v135 = arith.cmpi slt, %v134, %v129 : index
%v136 = arith.cmpi sgt, %v134, %v129 : index
%v137 = arith.select %v132, %v135, %v136 : i1
cf.cond_br %v137, ^b8(%v134 : index), ^b9(%v134 : index)
^b8(%v138: index):
%v139 = arith.constant 2 : i32
%v140 = arith.index_cast %v138 : index to i32
%v141 = arith.muli %v140, %v139 : i32
memref.store %v141, %v125[%v138] : memref<8xi32>
%v142 = arith.addi %v138, %v133 : index
cf.br ^b7(%v142 : index)
^b9(%v143: index):
%v144 = arith.constant 0 : i32
%v145 = llvm.mlir.constant(1 : i64) : i64
%v146 = llvm.alloca %v145 x i32 : (i64) -> !llvm.ptr
llvm.store %v144, %v146 : i32, !llvm.ptr
%v147 = arith.constant 0 : i32
%v148 = arith.constant 8 : i32
%v149 = arith.index_cast %v147 : i32 to index
%v150 = arith.index_cast %v148 : i32 to index
%v151 = arith.constant 1 : index
%v152 = arith.constant -1 : index
%v153 = arith.cmpi sle, %v149, %v150 : index
%v154 = arith.select %v153, %v151, %v152 : index
cf.br ^b10(%v149 : index)
^b10(%v155: index):
%v156 = arith.cmpi slt, %v155, %v150 : index
%v157 = arith.cmpi sgt, %v155, %v150 : index
%v158 = arith.select %v153, %v156, %v157 : i1
cf.cond_br %v158, ^b11(%v155 : index), ^b12(%v155 : index)
^b11(%v159: index):
%v160 = llvm.load %v146 : !llvm.ptr -> i32
%v161 = memref.load %v125[%v159] : memref<8xi32>
%v162 = arith.addi %v160, %v161 : i32
llvm.store %v162, %v146 : i32, !llvm.ptr
%v163 = arith.addi %v159, %v154 : index
cf.br ^b10(%v163 : index)
^b12(%v164: index):
%v165 = llvm.load %v146 : !llvm.ptr -> i32
%v166 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v167 = llvm.call @printf(%v166, %v165) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v168 = arith.constant 0 : i32
%v169 = arith.constant 16 : i32
%v170 = arith.extsi %v169 : i32 to i64
%v171 = func.call @malloc(%v170) : (i64) -> !llvm.ptr
%v172 = arith.constant 16 : i32
%v173 = arith.extsi %v172 : i32 to i64
%v174 = func.call @malloc(%v173) : (i64) -> !llvm.ptr
%v175 = arith.constant 16 : i32
%v176 = arith.extsi %v175 : i32 to i64
%v177 = func.call @malloc(%v176) : (i64) -> !llvm.ptr
%v178 = arith.constant 0 : i32
%v179 = arith.constant 4 : i32
%v180 = arith.index_cast %v178 : i32 to index
%v181 = arith.index_cast %v179 : i32 to index
%v182 = arith.constant 1 : index
%v183 = arith.constant -1 : index
%v184 = arith.cmpi sle, %v180, %v181 : index
%v185 = arith.select %v184, %v182, %v183 : index
cf.br ^b13(%v180 : index)
^b13(%v186: index):
%v187 = arith.cmpi slt, %v186, %v181 : index
%v188 = arith.cmpi sgt, %v186, %v181 : index
%v189 = arith.select %v184, %v187, %v188 : i1
cf.cond_br %v189, ^b14(%v186 : index), ^b15(%v186 : index)
^b14(%v190: index):
%v191 = arith.constant 1.5 : f64
%v192 = arith.truncf %v191 : f64 to f32
%v193 = arith.index_cast %v190 : index to i64
%v194 = llvm.getelementptr %v174[%v193] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v192, %v194 : f32, !llvm.ptr
%v195 = arith.constant 2.0 : f64
%v196 = arith.truncf %v195 : f64 to f32
%v197 = arith.index_cast %v190 : index to i64
%v198 = llvm.getelementptr %v177[%v197] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v196, %v198 : f32, !llvm.ptr
%v199 = arith.addi %v190, %v185 : index
cf.br ^b13(%v199 : index)
^b15(%v200: index):
%v201 = arith.constant 4 : i32
func.call @add4(%v171, %v174, %v177, %v201) : (!llvm.ptr, !llvm.ptr, !llvm.ptr, i32) -> ()
%v202 = arith.constant 3 : i32
%v203 = arith.extsi %v202 : i32 to i64
%v204 = llvm.getelementptr %v171[%v203] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v205 = llvm.load %v204 : !llvm.ptr -> f32
%v206 = arith.extf %v205 : f32 to f64
%v207 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v208 = llvm.call @printf(%v207, %v206) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v209 = arith.constant 0 : i32
%v210 = arith.constant 0 : i32
func.return %v210 : i32
}
}
