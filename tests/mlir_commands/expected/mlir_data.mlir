module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\n\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_1("%f\n\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
func.func private @malloc(i64) -> !llvm.ptr
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
%v55 = arith.constant 1.0 : f32
%v56 = llvm.insertvalue %v55, %v54[1] : !llvm.struct<(i32, f32)>
%v57 = llvm.mlir.undef : !llvm.struct<(i32, f32)>
%v58 = arith.constant 2 : i32
%v59 = llvm.insertvalue %v58, %v57[0] : !llvm.struct<(i32, f32)>
%v60 = arith.constant 2.0 : f32
%v61 = llvm.insertvalue %v60, %v59[1] : !llvm.struct<(i32, f32)>
%v62 = llvm.mlir.undef : !llvm.struct<(i32, f32)>
%v63 = arith.constant 3 : i32
%v64 = llvm.insertvalue %v63, %v62[0] : !llvm.struct<(i32, f32)>
%v65 = arith.constant 3.0 : f32
%v66 = llvm.insertvalue %v65, %v64[1] : !llvm.struct<(i32, f32)>
%v67 = llvm.mlir.constant(1 : i64) : i64
%v68 = llvm.alloca %v67 x !llvm.array<3 x !llvm.struct<(i32, f32)>> : (i64) -> !llvm.ptr
%v69 = llvm.mlir.zero : !llvm.array<3 x !llvm.struct<(i32, f32)>>
llvm.store %v69, %v68 : !llvm.array<3 x !llvm.struct<(i32, f32)>>, !llvm.ptr
%v70 = llvm.mlir.constant(0 : i64) : i64
%v71 = llvm.getelementptr %v68[0, %v70] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
llvm.store %v56, %v71 : !llvm.struct<(i32, f32)>, !llvm.ptr
%v72 = llvm.mlir.constant(1 : i64) : i64
%v73 = llvm.getelementptr %v68[0, %v72] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
llvm.store %v61, %v73 : !llvm.struct<(i32, f32)>, !llvm.ptr
%v74 = llvm.mlir.constant(2 : i64) : i64
%v75 = llvm.getelementptr %v68[0, %v74] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
llvm.store %v66, %v75 : !llvm.struct<(i32, f32)>, !llvm.ptr
%v76 = llvm.mlir.constant(1 : i64) : i64
%v77 = llvm.alloca %v76 x !llvm.ptr : (i64) -> !llvm.ptr
llvm.store %v68, %v77 : !llvm.ptr, !llvm.ptr
%v78 = arith.constant 20 : i32
%v79 = llvm.load %v77 : !llvm.ptr -> !llvm.ptr
%v80 = arith.constant 1 : i32
%v81 = arith.extsi %v80 : i32 to i64
%v82 = llvm.getelementptr %v79[0, %v81] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
%v83 = llvm.getelementptr %v82[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, f32)>
llvm.store %v78, %v83 : i32, !llvm.ptr
%v84 = llvm.load %v77 : !llvm.ptr -> !llvm.ptr
%v85 = arith.constant 2 : i32
%v86 = arith.extsi %v85 : i32 to i64
%v87 = llvm.getelementptr %v84[0, %v86] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
%v88 = llvm.load %v87 : !llvm.ptr -> !llvm.struct<(i32, f32)>
%v89 = llvm.mlir.constant(1 : i64) : i64
%v90 = llvm.alloca %v89 x !llvm.struct<(i32, f32)> : (i64) -> !llvm.ptr
llvm.store %v88, %v90 : !llvm.struct<(i32, f32)>, !llvm.ptr
%v91 = llvm.mlir.undef : !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v92 = llvm.mlir.zero : !llvm.array<4 x i32>
%v93 = arith.constant 1 : i32
%v94 = llvm.insertvalue %v93, %v92[0] : !llvm.array<4 x i32>
%v95 = arith.constant 2 : i32
%v96 = llvm.insertvalue %v95, %v94[1] : !llvm.array<4 x i32>
%v97 = arith.constant 3 : i32
%v98 = llvm.insertvalue %v97, %v96[2] : !llvm.array<4 x i32>
%v99 = arith.constant 4 : i32
%v100 = llvm.insertvalue %v99, %v98[3] : !llvm.array<4 x i32>
%v101 = llvm.insertvalue %v100, %v91[0] : !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v102 = arith.constant 4 : i32
%v103 = llvm.insertvalue %v102, %v101[1] : !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v104 = llvm.mlir.constant(1 : i64) : i64
%v105 = llvm.alloca %v104 x !llvm.struct<(!llvm.array<4 x i32>, i32)> : (i64) -> !llvm.ptr
llvm.store %v103, %v105 : !llvm.struct<(!llvm.array<4 x i32>, i32)>, !llvm.ptr
%v106 = llvm.load %v77 : !llvm.ptr -> !llvm.ptr
%v107 = func.call @sum(%v106) : (!llvm.ptr) -> i32
%v108 = llvm.load %v90 : !llvm.ptr -> !llvm.struct<(i32, f32)>
%v109 = llvm.getelementptr %v90[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, f32)>
%v110 = llvm.load %v109 : !llvm.ptr -> i32
%v111 = arith.addi %v107, %v110 : i32
%v112 = llvm.load %v105 : !llvm.ptr -> !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v113 = llvm.getelementptr %v105[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v114 = arith.constant 3 : i32
%v115 = arith.extsi %v114 : i32 to i64
%v116 = llvm.getelementptr %v113[0, %v115] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x i32>
%v117 = llvm.load %v116 : !llvm.ptr -> i32
%v118 = arith.addi %v111, %v117 : i32
%v119 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v120 = llvm.call @printf(%v119, %v118) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v121 = arith.constant 0 : i32
%v122 = memref.alloca() {type = memref<8xi32>} : memref<8xi32>
%v123 = arith.constant 0 : i32
%v124 = arith.constant 8 : i32
%v125 = arith.index_cast %v123 : i32 to index
%v126 = arith.index_cast %v124 : i32 to index
%v127 = arith.constant 1 : index
%v128 = arith.constant -1 : index
%v129 = arith.cmpi sle, %v125, %v126 : index
%v130 = arith.select %v129, %v127, %v128 : index
cf.br ^b7(%v125 : index)
^b7(%v131: index):
%v132 = arith.cmpi slt, %v131, %v126 : index
%v133 = arith.cmpi sgt, %v131, %v126 : index
%v134 = arith.select %v129, %v132, %v133 : i1
cf.cond_br %v134, ^b8(%v131 : index), ^b9(%v131 : index)
^b8(%v135: index):
%v136 = arith.constant 2 : i32
%v137 = arith.index_cast %v135 : index to i32
%v138 = arith.muli %v137, %v136 : i32
memref.store %v138, %v122[%v135] : memref<8xi32>
%v139 = arith.addi %v135, %v130 : index
cf.br ^b7(%v139 : index)
^b9(%v140: index):
%v141 = arith.constant 0 : i32
%v142 = llvm.mlir.constant(1 : i64) : i64
%v143 = llvm.alloca %v142 x i32 : (i64) -> !llvm.ptr
llvm.store %v141, %v143 : i32, !llvm.ptr
%v144 = arith.constant 0 : i32
%v145 = arith.constant 8 : i32
%v146 = arith.index_cast %v144 : i32 to index
%v147 = arith.index_cast %v145 : i32 to index
%v148 = arith.constant 1 : index
%v149 = arith.constant -1 : index
%v150 = arith.cmpi sle, %v146, %v147 : index
%v151 = arith.select %v150, %v148, %v149 : index
cf.br ^b10(%v146 : index)
^b10(%v152: index):
%v153 = arith.cmpi slt, %v152, %v147 : index
%v154 = arith.cmpi sgt, %v152, %v147 : index
%v155 = arith.select %v150, %v153, %v154 : i1
cf.cond_br %v155, ^b11(%v152 : index), ^b12(%v152 : index)
^b11(%v156: index):
%v157 = llvm.load %v143 : !llvm.ptr -> i32
%v158 = memref.load %v122[%v156] : memref<8xi32>
%v159 = arith.addi %v157, %v158 : i32
llvm.store %v159, %v143 : i32, !llvm.ptr
%v160 = arith.addi %v156, %v151 : index
cf.br ^b10(%v160 : index)
^b12(%v161: index):
%v162 = llvm.load %v143 : !llvm.ptr -> i32
%v163 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v164 = llvm.call @printf(%v163, %v162) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v165 = arith.constant 0 : i32
%v166 = arith.constant 16 : i32
%v167 = arith.extsi %v166 : i32 to i64
%v168 = func.call @malloc(%v167) : (i64) -> !llvm.ptr
%v169 = arith.constant 16 : i32
%v170 = arith.extsi %v169 : i32 to i64
%v171 = func.call @malloc(%v170) : (i64) -> !llvm.ptr
%v172 = arith.constant 16 : i32
%v173 = arith.extsi %v172 : i32 to i64
%v174 = func.call @malloc(%v173) : (i64) -> !llvm.ptr
%v175 = arith.constant 0 : i32
%v176 = arith.constant 4 : i32
%v177 = arith.index_cast %v175 : i32 to index
%v178 = arith.index_cast %v176 : i32 to index
%v179 = arith.constant 1 : index
%v180 = arith.constant -1 : index
%v181 = arith.cmpi sle, %v177, %v178 : index
%v182 = arith.select %v181, %v179, %v180 : index
cf.br ^b13(%v177 : index)
^b13(%v183: index):
%v184 = arith.cmpi slt, %v183, %v178 : index
%v185 = arith.cmpi sgt, %v183, %v178 : index
%v186 = arith.select %v181, %v184, %v185 : i1
cf.cond_br %v186, ^b14(%v183 : index), ^b15(%v183 : index)
^b14(%v187: index):
%v188 = arith.constant 1.5 : f32
%v189 = arith.index_cast %v187 : index to i64
%v190 = llvm.getelementptr %v171[%v189] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v188, %v190 : f32, !llvm.ptr
%v191 = arith.constant 2.0 : f32
%v192 = arith.index_cast %v187 : index to i64
%v193 = llvm.getelementptr %v174[%v192] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v191, %v193 : f32, !llvm.ptr
%v194 = arith.addi %v187, %v182 : index
cf.br ^b13(%v194 : index)
^b15(%v195: index):
%v196 = arith.constant 4 : i32
func.call @add4(%v168, %v171, %v174, %v196) : (!llvm.ptr, !llvm.ptr, !llvm.ptr, i32) -> ()
%v197 = arith.constant 3 : i32
%v198 = arith.extsi %v197 : i32 to i64
%v199 = llvm.getelementptr %v168[%v198] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v200 = llvm.load %v199 : !llvm.ptr -> f32
%v201 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v202 = arith.extf %v200 : f32 to f64
%v203 = llvm.call @printf(%v201, %v202) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v204 = arith.constant 0 : i32
%v205 = arith.constant 0 : i32
func.return %v205 : i32
}
}
