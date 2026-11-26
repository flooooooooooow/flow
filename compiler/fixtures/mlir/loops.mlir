module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_1("%lld\0A\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
func.func @sum_to(%arg0: i32) -> i32 {
%v1 = llvm.mlir.constant(1 : i64) : i64
%v2 = llvm.alloca %v1 x i32 : (i64) -> !llvm.ptr
%v3 = arith.constant 0 : i32
llvm.store %v3, %v2 : i32, !llvm.ptr
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
%v16 = llvm.load %v2 : !llvm.ptr -> i32
%v17 = arith.index_cast %v15 : index to i32
%v18 = arith.addi %v16, %v17 : i32
llvm.store %v18, %v2 : i32, !llvm.ptr
%v19 = arith.addi %v15, %v10 : index
cf.br ^b1(%v19 : index)
^b3(%v20: index):
%v21 = llvm.load %v2 : !llvm.ptr -> i32
func.return %v21 : i32
}
func.func @main() -> i32 {
%v22 = llvm.mlir.constant(1 : i64) : i64
%v23 = llvm.alloca %v22 x i32 : (i64) -> !llvm.ptr
%v24 = llvm.mlir.constant(1 : i64) : i64
%v25 = llvm.alloca %v24 x i32 : (i64) -> !llvm.ptr
%v26 = llvm.mlir.constant(1 : i64) : i64
%v27 = llvm.alloca %v26 x i32 : (i64) -> !llvm.ptr
%v28 = llvm.mlir.constant(1 : i64) : i64
%v29 = llvm.alloca %v28 x i32 : (i64) -> !llvm.ptr
%v30 = llvm.mlir.constant(1 : i64) : i64
%v31 = llvm.alloca %v30 x i32 : (i64) -> !llvm.ptr
%v32 = arith.constant 10 : i32
%v33 = func.call @sum_to(%v32) : (i32) -> i32
%v34 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v35 = llvm.call @printf(%v34, %v33) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v36 = arith.constant 0 : i32
%v37 = arith.constant 0 : i32
%v38 = arith.constant 12 : i32
%v39 = arith.index_cast %v37 : i32 to index
%v40 = arith.index_cast %v38 : i32 to index
%v41 = arith.constant 3 : index
scf.for %v42 = %v39 to %v40 step %v41 {
%v43 = arith.constant 4 : i32
%v44 = arith.index_cast %v42 : index to i32
%v45 = arith.cmpi sgt, %v44, %v43 : i32
scf.if %v45 {
%v46 = arith.index_cast %v42 : index to i64
%v47 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v48 = llvm.call @printf(%v47, %v46) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v49 = arith.constant 0 : i32
} else {
%v50 = arith.constant 0 : i32
%v51 = arith.index_cast %v42 : index to i32
%v52 = arith.subi %v50, %v51 : i32
%v53 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v54 = llvm.call @printf(%v53, %v52) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v55 = arith.constant 0 : i32
}
}
%v56 = arith.constant 0 : i32
llvm.store %v56, %v23 : i32, !llvm.ptr
%v57 = arith.constant 10 : i32
%v58 = arith.constant 0 : i32
%v59 = arith.index_cast %v57 : i32 to index
%v60 = arith.index_cast %v58 : i32 to index
%v61 = arith.constant -2 : index
cf.br ^b4(%v59 : index)
^b4(%v62: index):
%v63 = arith.cmpi sgt, %v62, %v60 : index
cf.cond_br %v63, ^b5(%v62 : index), ^b6(%v62 : index)
^b5(%v64: index):
%v65 = llvm.load %v23 : !llvm.ptr -> i32
%v66 = arith.index_cast %v64 : index to i32
%v67 = arith.addi %v65, %v66 : i32
llvm.store %v67, %v23 : i32, !llvm.ptr
%v68 = arith.addi %v64, %v61 : index
cf.br ^b4(%v68 : index)
^b6(%v69: index):
%v70 = llvm.load %v23 : !llvm.ptr -> i32
%v71 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v72 = llvm.call @printf(%v71, %v70) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v73 = arith.constant 0 : i32
%v74 = arith.constant 4 : i32
%v75 = arith.constant 0 : i32
llvm.store %v75, %v25 : i32, !llvm.ptr
%v76 = arith.constant 0 : i32
%v77 = arith.constant 20 : i32
%v78 = arith.index_cast %v76 : i32 to index
%v79 = arith.index_cast %v77 : i32 to index
%v80 = arith.index_cast %v74 : i32 to index
%v81 = arith.constant 0 : index
%v82 = arith.cmpi sgt, %v80, %v81 : index
cf.br ^b7(%v78 : index)
^b7(%v83: index):
%v84 = arith.cmpi slt, %v83, %v79 : index
%v85 = arith.cmpi sgt, %v83, %v79 : index
%v86 = arith.select %v82, %v84, %v85 : i1
cf.cond_br %v86, ^b8(%v83 : index), ^b9(%v83 : index)
^b8(%v87: index):
%v88 = llvm.load %v25 : !llvm.ptr -> i32
%v89 = arith.index_cast %v87 : index to i32
%v90 = arith.addi %v88, %v89 : i32
llvm.store %v90, %v25 : i32, !llvm.ptr
%v91 = arith.addi %v87, %v80 : index
cf.br ^b7(%v91 : index)
^b9(%v92: index):
%v93 = llvm.load %v25 : !llvm.ptr -> i32
%v94 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v95 = llvm.call @printf(%v94, %v93) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v96 = arith.constant 0 : i32
%v97 = arith.constant 0 : i32
llvm.store %v97, %v27 : i32, !llvm.ptr
%v98 = arith.constant 5 : i32
%v99 = arith.constant 0 : i32
%v100 = arith.index_cast %v98 : i32 to index
%v101 = arith.index_cast %v99 : i32 to index
%v102 = arith.constant 1 : index
%v103 = arith.constant -1 : index
%v104 = arith.cmpi sle, %v100, %v101 : index
%v105 = arith.select %v104, %v102, %v103 : index
cf.br ^b10(%v100 : index)
^b10(%v106: index):
%v107 = arith.cmpi slt, %v106, %v101 : index
%v108 = arith.cmpi sgt, %v106, %v101 : index
%v109 = arith.select %v104, %v107, %v108 : i1
cf.cond_br %v109, ^b11(%v106 : index), ^b12(%v106 : index)
^b11(%v110: index):
%v111 = llvm.load %v27 : !llvm.ptr -> i32
%v112 = arith.constant 10 : i32
%v113 = arith.muli %v111, %v112 : i32
%v114 = arith.index_cast %v110 : index to i32
%v115 = arith.addi %v113, %v114 : i32
llvm.store %v115, %v27 : i32, !llvm.ptr
%v116 = arith.addi %v110, %v105 : index
cf.br ^b10(%v116 : index)
^b12(%v117: index):
%v118 = llvm.load %v27 : !llvm.ptr -> i32
%v119 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v120 = llvm.call @printf(%v119, %v118) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v121 = arith.constant 0 : i32
%v122 = arith.constant 0 : i32
llvm.store %v122, %v29 : i32, !llvm.ptr
%v123 = arith.constant 0 : i32
%v124 = arith.constant 4 : i32
%v125 = arith.index_cast %v123 : i32 to index
%v126 = arith.index_cast %v124 : i32 to index
%v127 = arith.constant 1 : index
%v128 = arith.constant -1 : index
%v129 = arith.cmpi sle, %v125, %v126 : index
%v130 = arith.select %v129, %v127, %v128 : index
cf.br ^b13(%v125 : index)
^b13(%v131: index):
%v132 = arith.cmpi slt, %v131, %v126 : index
%v133 = arith.cmpi sgt, %v131, %v126 : index
%v134 = arith.select %v129, %v132, %v133 : i1
cf.cond_br %v134, ^b14(%v131 : index), ^b15(%v131 : index)
^b14(%v135: index):
%v136 = arith.constant 0 : i32
%v137 = arith.constant 4 : i32
%v138 = arith.index_cast %v136 : i32 to index
%v139 = arith.index_cast %v137 : i32 to index
%v140 = arith.constant 1 : index
%v141 = arith.constant -1 : index
%v142 = arith.cmpi sle, %v138, %v139 : index
%v143 = arith.select %v142, %v140, %v141 : index
cf.br ^b16(%v138 : index)
^b16(%v144: index):
%v145 = arith.cmpi slt, %v144, %v139 : index
%v146 = arith.cmpi sgt, %v144, %v139 : index
%v147 = arith.select %v142, %v145, %v146 : i1
cf.cond_br %v147, ^b17(%v144 : index), ^b18(%v144 : index)
^b17(%v148: index):
%v149 = arith.cmpi sgt, %v148, %v135 : index
cf.cond_br %v149, ^b19, ^b20
^b19:
cf.br ^b18(%v148 : index)
^b20:
cf.br ^b21
^b21:
%v150 = arith.constant 1 : i32
%v151 = arith.index_cast %v148 : index to i32
%v152 = arith.cmpi eq, %v151, %v150 : i32
cf.cond_br %v152, ^b22, ^b23
^b22:
%v153 = arith.addi %v148, %v143 : index
cf.br ^b16(%v153 : index)
^b23:
cf.br ^b24
^b24:
%v154 = llvm.load %v29 : !llvm.ptr -> i32
%v155 = arith.constant 1 : i32
%v156 = arith.addi %v154, %v155 : i32
llvm.store %v156, %v29 : i32, !llvm.ptr
%v157 = arith.addi %v148, %v143 : index
cf.br ^b16(%v157 : index)
^b18(%v158: index):
%v159 = arith.addi %v135, %v130 : index
cf.br ^b13(%v159 : index)
^b15(%v160: index):
%v161 = llvm.load %v29 : !llvm.ptr -> i32
%v162 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v163 = llvm.call @printf(%v162, %v161) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v164 = arith.constant 0 : i32
%v165 = arith.constant 0 : i32
%v166 = arith.constant 1 : i32
%v167 = arith.subi %v165, %v166 : i32
llvm.store %v167, %v31 : i32, !llvm.ptr
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
llvm.store %v185, %v31 : i32, !llvm.ptr
cf.br ^b27(%v180 : index)
^b29:
cf.br ^b30
^b30:
%v186 = arith.addi %v180, %v175 : index
cf.br ^b25(%v186 : index)
^b27(%v187: index):
%v188 = llvm.load %v31 : !llvm.ptr -> i32
%v189 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v190 = llvm.call @printf(%v189, %v188) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v191 = arith.constant 0 : i32
%v192 = arith.constant 0 : i32
func.return %v192 : i32
}
}
