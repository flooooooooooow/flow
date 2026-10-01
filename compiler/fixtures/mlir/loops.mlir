module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_1("%lld\0A\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
func.func @sum_to(%arg0: i32) -> i32 {
%v1 = arith.constant 0 : i32
%v2 = llvm.mlir.constant(1 : i64) : i64
%v3 = llvm.alloca %v2 x i32 : (i64) -> !llvm.ptr
llvm.store %v1, %v3 : i32, !llvm.ptr
%v4 = arith.constant 0 : i32
%v5 = arith.index_cast %v4 : i32 to index
%v6 = arith.index_cast %arg0 : i32 to index
%v7 = arith.constant 1 : index
%v8 = arith.constant -1 : index
%v9 = arith.cmpi sle, %v5, %v6 : index
%v10 = arith.select %v9, %v7, %v8 : index
cf.br ^b1(%v5 : index)
^b1(%v11: index):
%v12 = arith.cmpi slt, %v11, %v6 : index
%v13 = arith.cmpi sgt, %v11, %v6 : index
%v14 = arith.select %v9, %v12, %v13 : i1
cf.cond_br %v14, ^b2(%v11 : index), ^b3(%v11 : index)
^b2(%v15: index):
%v16 = llvm.load %v3 : !llvm.ptr -> i32
%v17 = arith.index_cast %v15 : index to i32
%v18 = arith.addi %v16, %v17 : i32
llvm.store %v18, %v3 : i32, !llvm.ptr
%v19 = arith.addi %v15, %v10 : index
cf.br ^b1(%v19 : index)
^b3(%v20: index):
%v21 = llvm.load %v3 : !llvm.ptr -> i32
func.return %v21 : i32
}
func.func @main() -> i32 {
%v22 = arith.constant 10 : i32
%v23 = func.call @sum_to(%v22) : (i32) -> i32
%v24 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v25 = llvm.call @printf(%v24, %v23) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v26 = arith.constant 0 : i32
%v27 = arith.constant 0 : i32
%v28 = arith.constant 12 : i32
%v29 = arith.index_cast %v27 : i32 to index
%v30 = arith.index_cast %v28 : i32 to index
%v31 = arith.constant 3 : index
scf.for %v32 = %v29 to %v30 step %v31 {
%v33 = arith.constant 4 : i32
%v34 = arith.index_cast %v32 : index to i32
%v35 = arith.cmpi sgt, %v34, %v33 : i32
scf.if %v35 {
%v36 = arith.index_cast %v32 : index to i64
%v37 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v38 = llvm.call @printf(%v37, %v36) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v39 = arith.constant 0 : i32
} else {
%v40 = arith.constant 0 : i32
%v41 = arith.index_cast %v32 : index to i32
%v42 = arith.subi %v40, %v41 : i32
%v43 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v44 = llvm.call @printf(%v43, %v42) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v45 = arith.constant 0 : i32
}
}
%v46 = arith.constant 0 : i32
%v47 = llvm.mlir.constant(1 : i64) : i64
%v48 = llvm.alloca %v47 x i32 : (i64) -> !llvm.ptr
llvm.store %v46, %v48 : i32, !llvm.ptr
%v49 = arith.constant 10 : i32
%v50 = arith.constant 0 : i32
%v51 = arith.index_cast %v49 : i32 to index
%v52 = arith.index_cast %v50 : i32 to index
%v53 = arith.constant -2 : index
cf.br ^b4(%v51 : index)
^b4(%v54: index):
%v55 = arith.cmpi sgt, %v54, %v52 : index
cf.cond_br %v55, ^b5(%v54 : index), ^b6(%v54 : index)
^b5(%v56: index):
%v57 = llvm.load %v48 : !llvm.ptr -> i32
%v58 = arith.index_cast %v56 : index to i32
%v59 = arith.addi %v57, %v58 : i32
llvm.store %v59, %v48 : i32, !llvm.ptr
%v60 = arith.addi %v56, %v53 : index
cf.br ^b4(%v60 : index)
^b6(%v61: index):
%v62 = llvm.load %v48 : !llvm.ptr -> i32
%v63 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v64 = llvm.call @printf(%v63, %v62) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v65 = arith.constant 0 : i32
%v66 = arith.constant 4 : i32
%v67 = arith.constant 0 : i32
%v68 = llvm.mlir.constant(1 : i64) : i64
%v69 = llvm.alloca %v68 x i32 : (i64) -> !llvm.ptr
llvm.store %v67, %v69 : i32, !llvm.ptr
%v70 = arith.constant 0 : i32
%v71 = arith.constant 20 : i32
%v72 = arith.index_cast %v70 : i32 to index
%v73 = arith.index_cast %v71 : i32 to index
%v74 = arith.index_cast %v66 : i32 to index
%v75 = arith.constant 0 : index
%v76 = arith.cmpi sgt, %v74, %v75 : index
cf.br ^b7(%v72 : index)
^b7(%v77: index):
%v78 = arith.cmpi slt, %v77, %v73 : index
%v79 = arith.cmpi sgt, %v77, %v73 : index
%v80 = arith.select %v76, %v78, %v79 : i1
cf.cond_br %v80, ^b8(%v77 : index), ^b9(%v77 : index)
^b8(%v81: index):
%v82 = llvm.load %v69 : !llvm.ptr -> i32
%v83 = arith.index_cast %v81 : index to i32
%v84 = arith.addi %v82, %v83 : i32
llvm.store %v84, %v69 : i32, !llvm.ptr
%v85 = arith.addi %v81, %v74 : index
cf.br ^b7(%v85 : index)
^b9(%v86: index):
%v87 = llvm.load %v69 : !llvm.ptr -> i32
%v88 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v89 = llvm.call @printf(%v88, %v87) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v90 = arith.constant 0 : i32
%v91 = arith.constant 0 : i32
%v92 = llvm.mlir.constant(1 : i64) : i64
%v93 = llvm.alloca %v92 x i32 : (i64) -> !llvm.ptr
llvm.store %v91, %v93 : i32, !llvm.ptr
%v94 = arith.constant 5 : i32
%v95 = arith.constant 0 : i32
%v96 = arith.index_cast %v94 : i32 to index
%v97 = arith.index_cast %v95 : i32 to index
%v98 = arith.constant 1 : index
%v99 = arith.constant -1 : index
%v100 = arith.cmpi sle, %v96, %v97 : index
%v101 = arith.select %v100, %v98, %v99 : index
cf.br ^b10(%v96 : index)
^b10(%v102: index):
%v103 = arith.cmpi slt, %v102, %v97 : index
%v104 = arith.cmpi sgt, %v102, %v97 : index
%v105 = arith.select %v100, %v103, %v104 : i1
cf.cond_br %v105, ^b11(%v102 : index), ^b12(%v102 : index)
^b11(%v106: index):
%v107 = llvm.load %v93 : !llvm.ptr -> i32
%v108 = arith.constant 10 : i32
%v109 = arith.muli %v107, %v108 : i32
%v110 = arith.index_cast %v106 : index to i32
%v111 = arith.addi %v109, %v110 : i32
llvm.store %v111, %v93 : i32, !llvm.ptr
%v112 = arith.addi %v106, %v101 : index
cf.br ^b10(%v112 : index)
^b12(%v113: index):
%v114 = llvm.load %v93 : !llvm.ptr -> i32
%v115 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v116 = llvm.call @printf(%v115, %v114) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v117 = arith.constant 0 : i32
%v118 = arith.constant 0 : i32
%v119 = llvm.mlir.constant(1 : i64) : i64
%v120 = llvm.alloca %v119 x i32 : (i64) -> !llvm.ptr
llvm.store %v118, %v120 : i32, !llvm.ptr
%v121 = arith.constant 0 : i32
%v122 = arith.constant 4 : i32
%v123 = arith.index_cast %v121 : i32 to index
%v124 = arith.index_cast %v122 : i32 to index
%v125 = arith.constant 1 : index
%v126 = arith.constant -1 : index
%v127 = arith.cmpi sle, %v123, %v124 : index
%v128 = arith.select %v127, %v125, %v126 : index
cf.br ^b13(%v123 : index)
^b13(%v129: index):
%v130 = arith.cmpi slt, %v129, %v124 : index
%v131 = arith.cmpi sgt, %v129, %v124 : index
%v132 = arith.select %v127, %v130, %v131 : i1
cf.cond_br %v132, ^b14(%v129 : index), ^b15(%v129 : index)
^b14(%v133: index):
%v134 = arith.constant 0 : i32
%v135 = arith.constant 4 : i32
%v136 = arith.index_cast %v134 : i32 to index
%v137 = arith.index_cast %v135 : i32 to index
%v138 = arith.constant 1 : index
%v139 = arith.constant -1 : index
%v140 = arith.cmpi sle, %v136, %v137 : index
%v141 = arith.select %v140, %v138, %v139 : index
cf.br ^b16(%v136 : index)
^b16(%v142: index):
%v143 = arith.cmpi slt, %v142, %v137 : index
%v144 = arith.cmpi sgt, %v142, %v137 : index
%v145 = arith.select %v140, %v143, %v144 : i1
cf.cond_br %v145, ^b17(%v142 : index), ^b18(%v142 : index)
^b17(%v146: index):
%v147 = arith.cmpi sgt, %v146, %v133 : index
cf.cond_br %v147, ^b19, ^b20
^b19:
cf.br ^b18(%v146 : index)
^b20:
cf.br ^b21
^b21:
%v148 = arith.constant 1 : i32
%v149 = arith.index_cast %v146 : index to i32
%v150 = arith.cmpi eq, %v149, %v148 : i32
cf.cond_br %v150, ^b22, ^b23
^b22:
%v151 = arith.addi %v146, %v141 : index
cf.br ^b16(%v151 : index)
^b23:
cf.br ^b24
^b24:
%v152 = llvm.load %v120 : !llvm.ptr -> i32
%v153 = arith.constant 1 : i32
%v154 = arith.addi %v152, %v153 : i32
llvm.store %v154, %v120 : i32, !llvm.ptr
%v155 = arith.addi %v146, %v141 : index
cf.br ^b16(%v155 : index)
^b18(%v156: index):
%v157 = arith.addi %v133, %v128 : index
cf.br ^b13(%v157 : index)
^b15(%v158: index):
%v159 = llvm.load %v120 : !llvm.ptr -> i32
%v160 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v161 = llvm.call @printf(%v160, %v159) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v162 = arith.constant 0 : i32
%v163 = arith.constant 0 : i32
%v164 = arith.constant 1 : i32
%v165 = arith.subi %v163, %v164 : i32
%v166 = llvm.mlir.constant(1 : i64) : i64
%v167 = llvm.alloca %v166 x i32 : (i64) -> !llvm.ptr
llvm.store %v165, %v167 : i32, !llvm.ptr
%v168 = arith.constant 0 : i32
%v169 = arith.constant 100 : i32
%v170 = arith.index_cast %v168 : i32 to index
%v171 = arith.index_cast %v169 : i32 to index
%v172 = arith.constant 1 : index
%v173 = arith.constant -1 : index
%v174 = arith.cmpi sle, %v170, %v171 : index
%v175 = arith.select %v174, %v172, %v173 : index
cf.br ^b25(%v170 : index)
^b25(%v176: index):
%v177 = arith.cmpi slt, %v176, %v171 : index
%v178 = arith.cmpi sgt, %v176, %v171 : index
%v179 = arith.select %v174, %v177, %v178 : i1
cf.cond_br %v179, ^b26(%v176 : index), ^b27(%v176 : index)
^b26(%v180: index):
%v181 = arith.muli %v180, %v180 : index
%v182 = arith.constant 50 : i32
%v183 = arith.index_cast %v181 : index to i32
%v184 = arith.cmpi sgt, %v183, %v182 : i32
cf.cond_br %v184, ^b28, ^b29
^b28:
%v185 = arith.index_cast %v180 : index to i32
llvm.store %v185, %v167 : i32, !llvm.ptr
cf.br ^b27(%v180 : index)
^b29:
cf.br ^b30
^b30:
%v186 = arith.addi %v180, %v175 : index
cf.br ^b25(%v186 : index)
^b27(%v187: index):
%v188 = llvm.load %v167 : !llvm.ptr -> i32
%v189 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v190 = llvm.call @printf(%v189, %v188) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v191 = arith.constant 0 : i32
%v192 = arith.constant 0 : i32
func.return %v192 : i32
}
}
