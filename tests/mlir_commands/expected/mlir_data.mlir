module {
func.func private @strlen(!llvm.ptr) -> i64
func.func private @write(i32, !llvm.ptr, i64) -> i64
func.func private @abort() -> ()
func.func private @malloc(i64) -> !llvm.ptr
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("flow: \00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
llvm.mlir.global internal constant @str_1("\0A\00") {addr_space = 0 : i32} : !llvm.array<2 x i8>
llvm.mlir.global internal constant @str_2("array index out of bounds\00") {addr_space = 0 : i32} : !llvm.array<26 x i8>
llvm.mlir.global internal constant @str_3("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_4("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
func.func private @__flow_fault(%arg0: !llvm.ptr) {
%fd = arith.constant 2 : i32
%pre = llvm.mlir.addressof @str_0 : !llvm.ptr
%n6 = arith.constant 6 : i64
%w0 = func.call @write(%fd, %pre, %n6) : (i32, !llvm.ptr, i64) -> i64
%n = func.call @strlen(%arg0) : (!llvm.ptr) -> i64
%w1 = func.call @write(%fd, %arg0, %n) : (i32, !llvm.ptr, i64) -> i64
%nl = llvm.mlir.addressof @str_1 : !llvm.ptr
%n1 = arith.constant 1 : i64
%w2 = func.call @write(%fd, %nl, %n1) : (i32, !llvm.ptr, i64) -> i64
func.call @abort() : () -> ()
func.return
}
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
%v18 = arith.index_cast %v16 : index to i32
%v19 = arith.constant 3 : i32
%v20 = arith.cmpi uge, %v18, %v19 : i32
scf.if %v20 {
%v21 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v21) : (!llvm.ptr) -> ()
}
%v22 = arith.index_cast %v16 : index to i64
%v23 = llvm.getelementptr %arg0[0, %v22] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
%v24 = llvm.load %v23 : !llvm.ptr -> !llvm.struct<(i32, f32)>
%v25 = arith.index_cast %v16 : index to i64
%v26 = llvm.getelementptr %arg0[0, %v25] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
%v27 = llvm.getelementptr %v26[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, f32)>
%v28 = llvm.load %v27 : !llvm.ptr -> i32
%v29 = arith.addi %v17, %v28 : i32
llvm.store %v29, %v3 : i32, !llvm.ptr
%v30 = arith.addi %v16, %v11 : index
cf.br ^b1(%v30 : index)
^b3(%v31: index):
%v32 = llvm.load %v3 : !llvm.ptr -> i32
func.return %v32 : i32
}
func.func @add4(%arg0: !llvm.ptr, %arg1: !llvm.ptr, %arg2: !llvm.ptr, %arg3: i32) -> () {
%v33 = arith.constant 0 : i32
%v34 = arith.index_cast %v33 : i32 to index
%v35 = arith.index_cast %arg3 : i32 to index
%v36 = arith.constant 1 : index
%v37 = arith.constant -1 : index
%v38 = arith.cmpi sle, %v34, %v35 : index
%v39 = arith.select %v38, %v36, %v37 : index
cf.br ^b4(%v34 : index)
^b4(%v40: index):
%v41 = arith.cmpi slt, %v40, %v35 : index
%v42 = arith.cmpi sgt, %v40, %v35 : index
%v43 = arith.select %v38, %v41, %v42 : i1
cf.cond_br %v43, ^b5(%v40 : index), ^b6(%v40 : index)
^b5(%v44: index):
%v45 = arith.index_cast %v44 : index to i64
%v46 = llvm.getelementptr %arg1[%v45] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v47 = llvm.load %v46 : !llvm.ptr -> f32
%v48 = arith.index_cast %v44 : index to i64
%v49 = llvm.getelementptr %arg2[%v48] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v50 = llvm.load %v49 : !llvm.ptr -> f32
%v51 = arith.addf %v47, %v50 : f32
%v52 = arith.index_cast %v44 : index to i64
%v53 = llvm.getelementptr %arg0[%v52] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v51, %v53 : f32, !llvm.ptr
%v54 = arith.addi %v44, %v39 : index
cf.br ^b4(%v54 : index)
^b6(%v55: index):
func.return
}
func.func @main() -> i32 {
%v56 = llvm.mlir.undef : !llvm.struct<(i32, f32)>
%v57 = arith.constant 1 : i32
%v58 = llvm.insertvalue %v57, %v56[0] : !llvm.struct<(i32, f32)>
%v59 = arith.constant 1.0 : f64
%v60 = arith.truncf %v59 : f64 to f32
%v61 = llvm.insertvalue %v60, %v58[1] : !llvm.struct<(i32, f32)>
%v62 = llvm.mlir.undef : !llvm.struct<(i32, f32)>
%v63 = arith.constant 2 : i32
%v64 = llvm.insertvalue %v63, %v62[0] : !llvm.struct<(i32, f32)>
%v65 = arith.constant 2.0 : f64
%v66 = arith.truncf %v65 : f64 to f32
%v67 = llvm.insertvalue %v66, %v64[1] : !llvm.struct<(i32, f32)>
%v68 = llvm.mlir.undef : !llvm.struct<(i32, f32)>
%v69 = arith.constant 3 : i32
%v70 = llvm.insertvalue %v69, %v68[0] : !llvm.struct<(i32, f32)>
%v71 = arith.constant 3.0 : f64
%v72 = arith.truncf %v71 : f64 to f32
%v73 = llvm.insertvalue %v72, %v70[1] : !llvm.struct<(i32, f32)>
%v74 = llvm.mlir.constant(1 : i64) : i64
%v75 = llvm.alloca %v74 x !llvm.array<3 x !llvm.struct<(i32, f32)>> : (i64) -> !llvm.ptr
%v76 = llvm.mlir.zero : !llvm.array<3 x !llvm.struct<(i32, f32)>>
llvm.store %v76, %v75 : !llvm.array<3 x !llvm.struct<(i32, f32)>>, !llvm.ptr
%v77 = llvm.mlir.constant(0 : i64) : i64
%v78 = llvm.getelementptr %v75[0, %v77] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
llvm.store %v61, %v78 : !llvm.struct<(i32, f32)>, !llvm.ptr
%v79 = llvm.mlir.constant(1 : i64) : i64
%v80 = llvm.getelementptr %v75[0, %v79] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
llvm.store %v67, %v80 : !llvm.struct<(i32, f32)>, !llvm.ptr
%v81 = llvm.mlir.constant(2 : i64) : i64
%v82 = llvm.getelementptr %v75[0, %v81] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
llvm.store %v73, %v82 : !llvm.struct<(i32, f32)>, !llvm.ptr
%v83 = llvm.mlir.constant(1 : i64) : i64
%v84 = llvm.alloca %v83 x !llvm.ptr : (i64) -> !llvm.ptr
llvm.store %v75, %v84 : !llvm.ptr, !llvm.ptr
%v85 = arith.constant 20 : i32
%v86 = llvm.load %v84 : !llvm.ptr -> !llvm.ptr
%v87 = arith.constant 1 : i32
%v88 = arith.extsi %v87 : i32 to i64
%v89 = llvm.getelementptr %v86[0, %v88] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
%v90 = llvm.getelementptr %v89[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, f32)>
llvm.store %v85, %v90 : i32, !llvm.ptr
%v91 = llvm.load %v84 : !llvm.ptr -> !llvm.ptr
%v92 = arith.constant 2 : i32
%v93 = arith.constant 3 : i32
%v94 = arith.cmpi uge, %v92, %v93 : i32
scf.if %v94 {
%v95 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v95) : (!llvm.ptr) -> ()
}
%v96 = arith.extsi %v92 : i32 to i64
%v97 = llvm.getelementptr %v91[0, %v96] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x !llvm.struct<(i32, f32)>>
%v98 = llvm.load %v97 : !llvm.ptr -> !llvm.struct<(i32, f32)>
%v99 = llvm.mlir.constant(1 : i64) : i64
%v100 = llvm.alloca %v99 x !llvm.struct<(i32, f32)> : (i64) -> !llvm.ptr
llvm.store %v98, %v100 : !llvm.struct<(i32, f32)>, !llvm.ptr
%v101 = llvm.mlir.undef : !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v102 = llvm.mlir.zero : !llvm.array<4 x i32>
%v103 = arith.constant 1 : i32
%v104 = llvm.insertvalue %v103, %v102[0] : !llvm.array<4 x i32>
%v105 = arith.constant 2 : i32
%v106 = llvm.insertvalue %v105, %v104[1] : !llvm.array<4 x i32>
%v107 = arith.constant 3 : i32
%v108 = llvm.insertvalue %v107, %v106[2] : !llvm.array<4 x i32>
%v109 = arith.constant 4 : i32
%v110 = llvm.insertvalue %v109, %v108[3] : !llvm.array<4 x i32>
%v111 = llvm.insertvalue %v110, %v101[0] : !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v112 = arith.constant 4 : i32
%v113 = llvm.insertvalue %v112, %v111[1] : !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v114 = llvm.mlir.constant(1 : i64) : i64
%v115 = llvm.alloca %v114 x !llvm.struct<(!llvm.array<4 x i32>, i32)> : (i64) -> !llvm.ptr
llvm.store %v113, %v115 : !llvm.struct<(!llvm.array<4 x i32>, i32)>, !llvm.ptr
%v116 = llvm.load %v84 : !llvm.ptr -> !llvm.ptr
%v117 = func.call @sum(%v116) : (!llvm.ptr) -> i32
%v118 = llvm.load %v100 : !llvm.ptr -> !llvm.struct<(i32, f32)>
%v119 = llvm.getelementptr %v100[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, f32)>
%v120 = llvm.load %v119 : !llvm.ptr -> i32
%v121 = arith.addi %v117, %v120 : i32
%v122 = llvm.load %v115 : !llvm.ptr -> !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v123 = llvm.getelementptr %v115[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.array<4 x i32>, i32)>
%v124 = arith.constant 3 : i32
%v125 = arith.extsi %v124 : i32 to i64
%v126 = llvm.getelementptr %v123[0, %v125] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x i32>
%v127 = llvm.load %v126 : !llvm.ptr -> i32
%v128 = arith.addi %v121, %v127 : i32
%v129 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v130 = llvm.call @printf(%v129, %v128) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v131 = arith.constant 0 : i32
%v132 = memref.alloca() : memref<8xi32>
%v133 = arith.constant 0 : i32
%v134 = arith.constant 8 : i32
%v135 = arith.index_cast %v133 : i32 to index
%v136 = arith.index_cast %v134 : i32 to index
%v137 = arith.constant 1 : index
%v138 = arith.constant -1 : index
%v139 = arith.cmpi sle, %v135, %v136 : index
%v140 = arith.select %v139, %v137, %v138 : index
cf.br ^b7(%v135 : index)
^b7(%v141: index):
%v142 = arith.cmpi slt, %v141, %v136 : index
%v143 = arith.cmpi sgt, %v141, %v136 : index
%v144 = arith.select %v139, %v142, %v143 : i1
cf.cond_br %v144, ^b8(%v141 : index), ^b9(%v141 : index)
^b8(%v145: index):
%v146 = arith.constant 2 : i32
%v147 = arith.index_cast %v145 : index to i32
%v148 = arith.muli %v147, %v146 : i32
memref.store %v148, %v132[%v145] : memref<8xi32>
%v149 = arith.addi %v145, %v140 : index
cf.br ^b7(%v149 : index)
^b9(%v150: index):
%v151 = arith.constant 0 : i32
%v152 = llvm.mlir.constant(1 : i64) : i64
%v153 = llvm.alloca %v152 x i32 : (i64) -> !llvm.ptr
llvm.store %v151, %v153 : i32, !llvm.ptr
%v154 = arith.constant 0 : i32
%v155 = arith.constant 8 : i32
%v156 = arith.index_cast %v154 : i32 to index
%v157 = arith.index_cast %v155 : i32 to index
%v158 = arith.constant 1 : index
%v159 = arith.constant -1 : index
%v160 = arith.cmpi sle, %v156, %v157 : index
%v161 = arith.select %v160, %v158, %v159 : index
cf.br ^b10(%v156 : index)
^b10(%v162: index):
%v163 = arith.cmpi slt, %v162, %v157 : index
%v164 = arith.cmpi sgt, %v162, %v157 : index
%v165 = arith.select %v160, %v163, %v164 : i1
cf.cond_br %v165, ^b11(%v162 : index), ^b12(%v162 : index)
^b11(%v166: index):
%v167 = llvm.load %v153 : !llvm.ptr -> i32
%v168 = arith.index_cast %v166 : index to i32
%v169 = arith.constant 8 : i32
%v170 = arith.cmpi uge, %v168, %v169 : i32
scf.if %v170 {
%v171 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v171) : (!llvm.ptr) -> ()
}
%v172 = memref.load %v132[%v166] : memref<8xi32>
%v173 = arith.addi %v167, %v172 : i32
llvm.store %v173, %v153 : i32, !llvm.ptr
%v174 = arith.addi %v166, %v161 : index
cf.br ^b10(%v174 : index)
^b12(%v175: index):
%v176 = llvm.load %v153 : !llvm.ptr -> i32
%v177 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v178 = llvm.call @printf(%v177, %v176) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v179 = arith.constant 0 : i32
%v180 = arith.constant 16 : i32
%v181 = arith.extsi %v180 : i32 to i64
%v182 = func.call @malloc(%v181) : (i64) -> !llvm.ptr
%v183 = arith.constant 16 : i32
%v184 = arith.extsi %v183 : i32 to i64
%v185 = func.call @malloc(%v184) : (i64) -> !llvm.ptr
%v186 = arith.constant 16 : i32
%v187 = arith.extsi %v186 : i32 to i64
%v188 = func.call @malloc(%v187) : (i64) -> !llvm.ptr
%v189 = arith.constant 0 : i32
%v190 = arith.constant 4 : i32
%v191 = arith.index_cast %v189 : i32 to index
%v192 = arith.index_cast %v190 : i32 to index
%v193 = arith.constant 1 : index
%v194 = arith.constant -1 : index
%v195 = arith.cmpi sle, %v191, %v192 : index
%v196 = arith.select %v195, %v193, %v194 : index
cf.br ^b13(%v191 : index)
^b13(%v197: index):
%v198 = arith.cmpi slt, %v197, %v192 : index
%v199 = arith.cmpi sgt, %v197, %v192 : index
%v200 = arith.select %v195, %v198, %v199 : i1
cf.cond_br %v200, ^b14(%v197 : index), ^b15(%v197 : index)
^b14(%v201: index):
%v202 = arith.constant 1.5 : f64
%v203 = arith.truncf %v202 : f64 to f32
%v204 = arith.index_cast %v201 : index to i64
%v205 = llvm.getelementptr %v185[%v204] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v203, %v205 : f32, !llvm.ptr
%v206 = arith.constant 2.0 : f64
%v207 = arith.truncf %v206 : f64 to f32
%v208 = arith.index_cast %v201 : index to i64
%v209 = llvm.getelementptr %v188[%v208] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v207, %v209 : f32, !llvm.ptr
%v210 = arith.addi %v201, %v196 : index
cf.br ^b13(%v210 : index)
^b15(%v211: index):
%v212 = arith.constant 4 : i32
func.call @add4(%v182, %v185, %v188, %v212) : (!llvm.ptr, !llvm.ptr, !llvm.ptr, i32) -> ()
%v213 = arith.constant 3 : i32
%v214 = arith.extsi %v213 : i32 to i64
%v215 = llvm.getelementptr %v182[%v214] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v216 = llvm.load %v215 : !llvm.ptr -> f32
%v217 = arith.extf %v216 : f32 to f64
%v218 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v219 = llvm.call @printf(%v218, %v217) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v220 = arith.constant 0 : i32
%v221 = arith.constant 0 : i32
func.return %v221 : i32
}
}
