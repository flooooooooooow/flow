module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_1("%lld\0A\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
llvm.mlir.global internal constant @str_2("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_3("first\0A\00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
func.func @total(%arg0: !llvm.ptr) -> i32 {
%v1 = arith.constant 0 : i32
%v2 = llvm.mlir.constant(1 : i64) : i64
%v3 = llvm.alloca %v2 x i32 : (i64) -> !llvm.ptr
llvm.store %v1, %v3 : i32, !llvm.ptr
%v4 = arith.constant 0 : i32
%v5 = llvm.mlir.constant(1 : i64) : i64
%v6 = llvm.alloca %v5 x i32 : (i64) -> !llvm.ptr
llvm.store %v4, %v6 : i32, !llvm.ptr
cf.br ^b1
^b1:
%v7 = llvm.load %v6 : !llvm.ptr -> i32
%v8 = arith.constant 5 : i32
%v9 = arith.cmpi slt, %v7, %v8 : i32
cf.cond_br %v9, ^b2, ^b3
^b2:
%v10 = llvm.load %v3 : !llvm.ptr -> i32
%v11 = llvm.load %v6 : !llvm.ptr -> i32
%v12 = arith.extsi %v11 : i32 to i64
%v13 = llvm.getelementptr %arg0[0, %v12] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
%v14 = llvm.load %v13 : !llvm.ptr -> i32
%v15 = arith.addi %v10, %v14 : i32
llvm.store %v15, %v3 : i32, !llvm.ptr
%v16 = llvm.load %v6 : !llvm.ptr -> i32
%v17 = arith.constant 1 : i32
%v18 = arith.addi %v16, %v17 : i32
llvm.store %v18, %v6 : i32, !llvm.ptr
cf.br ^b1
^b3:
%v19 = llvm.load %v3 : !llvm.ptr -> i32
func.return %v19 : i32
}
func.func @scale(%arg0: !llvm.ptr, %arg1: i32, %arg2: f64) -> f64 {
%v20 = arith.constant 0.0 : f64
%v21 = llvm.mlir.constant(1 : i64) : i64
%v22 = llvm.alloca %v21 x f64 : (i64) -> !llvm.ptr
llvm.store %v20, %v22 : f64, !llvm.ptr
%v23 = arith.constant 0 : i32
%v24 = arith.index_cast %v23 : i32 to index
%v25 = arith.index_cast %arg1 : i32 to index
%v26 = arith.constant 1 : index
%v27 = arith.constant -1 : index
%v28 = arith.cmpi sle, %v24, %v25 : index
%v29 = arith.select %v28, %v26, %v27 : index
cf.br ^b4(%v24 : index)
^b4(%v30: index):
%v31 = arith.cmpi slt, %v30, %v25 : index
%v32 = arith.cmpi sgt, %v30, %v25 : index
%v33 = arith.select %v28, %v31, %v32 : i1
cf.cond_br %v33, ^b5(%v30 : index), ^b6(%v30 : index)
^b5(%v34: index):
%v35 = llvm.load %v22 : !llvm.ptr -> f64
%v36 = arith.index_cast %v34 : index to i64
%v37 = llvm.getelementptr %arg0[%v36] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v38 = llvm.load %v37 : !llvm.ptr -> f64
%v39 = llvm.intr.fma(%v38, %arg2, %v35) : (f64, f64, f64) -> f64
llvm.store %v39, %v22 : f64, !llvm.ptr
%v40 = arith.addi %v34, %v29 : index
cf.br ^b4(%v40 : index)
^b6(%v41: index):
%v42 = llvm.load %v22 : !llvm.ptr -> f64
func.return %v42 : f64
}
func.func @main() -> i32 {
%v43 = arith.constant 3 : i32
%v44 = arith.constant 1 : i32
%v45 = arith.constant 4 : i32
%v46 = arith.constant 1 : i32
%v47 = arith.constant 5 : i32
%v48 = llvm.mlir.constant(1 : i64) : i64
%v49 = llvm.alloca %v48 x !llvm.array<5 x i32> : (i64) -> !llvm.ptr
%v50 = llvm.mlir.zero : !llvm.array<5 x i32>
llvm.store %v50, %v49 : !llvm.array<5 x i32>, !llvm.ptr
%v51 = llvm.mlir.constant(0 : i64) : i64
%v52 = llvm.getelementptr %v49[0, %v51] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v43, %v52 : i32, !llvm.ptr
%v53 = llvm.mlir.constant(1 : i64) : i64
%v54 = llvm.getelementptr %v49[0, %v53] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v44, %v54 : i32, !llvm.ptr
%v55 = llvm.mlir.constant(2 : i64) : i64
%v56 = llvm.getelementptr %v49[0, %v55] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v45, %v56 : i32, !llvm.ptr
%v57 = llvm.mlir.constant(3 : i64) : i64
%v58 = llvm.getelementptr %v49[0, %v57] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v46, %v58 : i32, !llvm.ptr
%v59 = llvm.mlir.constant(4 : i64) : i64
%v60 = llvm.getelementptr %v49[0, %v59] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v47, %v60 : i32, !llvm.ptr
%v61 = func.call @total(%v49) : (!llvm.ptr) -> i32
%v62 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v63 = llvm.call @printf(%v62, %v61) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v64 = arith.constant 0 : i32
%v65 = arith.constant 40 : i32
%v66 = arith.constant 2 : i32
%v67 = arith.extsi %v66 : i32 to i64
%v68 = llvm.getelementptr %v49[0, %v67] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v65, %v68 : i32, !llvm.ptr
%v69 = arith.constant 4 : i32
%v70 = arith.extsi %v69 : i32 to i64
%v71 = llvm.getelementptr %v49[0, %v70] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
%v72 = llvm.load %v71 : !llvm.ptr -> i32
%v73 = arith.constant 100 : i32
%v74 = arith.addi %v72, %v73 : i32
%v75 = arith.extsi %v69 : i32 to i64
%v76 = llvm.getelementptr %v49[0, %v75] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v74, %v76 : i32, !llvm.ptr
%v77 = func.call @total(%v49) : (!llvm.ptr) -> i32
%v78 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v79 = llvm.call @printf(%v78, %v77) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v80 = arith.constant 0 : i32
%v81 = arith.constant 2 : i32
%v82 = arith.extsi %v81 : i32 to i64
%v83 = llvm.getelementptr %v49[0, %v82] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
%v84 = llvm.load %v83 : !llvm.ptr -> i32
%v85 = arith.constant 4 : i32
%v86 = arith.extsi %v85 : i32 to i64
%v87 = llvm.getelementptr %v49[0, %v86] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
%v88 = llvm.load %v87 : !llvm.ptr -> i32
%v89 = arith.addi %v84, %v88 : i32
%v90 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v91 = llvm.call @printf(%v90, %v89) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v92 = arith.constant 0 : i32
%v93 = arith.constant 1 : i32
%v94 = arith.constant 2 : i32
%v95 = arith.constant 3 : i32
%v96 = llvm.mlir.constant(1 : i64) : i64
%v97 = llvm.alloca %v96 x !llvm.array<3 x i64> : (i64) -> !llvm.ptr
%v98 = llvm.mlir.zero : !llvm.array<3 x i64>
llvm.store %v98, %v97 : !llvm.array<3 x i64>, !llvm.ptr
%v99 = arith.extsi %v93 : i32 to i64
%v100 = arith.extsi %v94 : i32 to i64
%v101 = arith.extsi %v95 : i32 to i64
%v102 = llvm.mlir.constant(0 : i64) : i64
%v103 = llvm.getelementptr %v97[0, %v102] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
llvm.store %v99, %v103 : i64, !llvm.ptr
%v104 = llvm.mlir.constant(1 : i64) : i64
%v105 = llvm.getelementptr %v97[0, %v104] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
llvm.store %v100, %v105 : i64, !llvm.ptr
%v106 = llvm.mlir.constant(2 : i64) : i64
%v107 = llvm.getelementptr %v97[0, %v106] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
llvm.store %v101, %v107 : i64, !llvm.ptr
%v108 = arith.constant 0 : i32
%v109 = arith.extsi %v108 : i32 to i64
%v110 = llvm.mlir.constant(1 : i64) : i64
%v111 = llvm.alloca %v110 x i64 : (i64) -> !llvm.ptr
llvm.store %v109, %v111 : i64, !llvm.ptr
%v112 = arith.constant 0 : i32
%v113 = arith.constant 3 : i32
%v114 = arith.index_cast %v112 : i32 to index
%v115 = arith.index_cast %v113 : i32 to index
%v116 = arith.constant 1 : index
%v117 = arith.constant -1 : index
%v118 = arith.cmpi sle, %v114, %v115 : index
%v119 = arith.select %v118, %v116, %v117 : index
cf.br ^b7(%v114 : index)
^b7(%v120: index):
%v121 = arith.cmpi slt, %v120, %v115 : index
%v122 = arith.cmpi sgt, %v120, %v115 : index
%v123 = arith.select %v118, %v121, %v122 : i1
cf.cond_br %v123, ^b8(%v120 : index), ^b9(%v120 : index)
^b8(%v124: index):
%v125 = llvm.load %v111 : !llvm.ptr -> i64
%v126 = arith.index_cast %v124 : index to i64
%v127 = llvm.getelementptr %v97[0, %v126] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
%v128 = llvm.load %v127 : !llvm.ptr -> i64
%v129 = arith.constant 1000000 : i32
%v130 = arith.extsi %v129 : i32 to i64
%v131 = arith.muli %v128, %v130 : i64
%v132 = arith.addi %v125, %v131 : i64
llvm.store %v132, %v111 : i64, !llvm.ptr
%v133 = arith.addi %v124, %v119 : index
cf.br ^b7(%v133 : index)
^b9(%v134: index):
%v135 = llvm.load %v111 : !llvm.ptr -> i64
%v136 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v137 = llvm.call @printf(%v136, %v135) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v138 = arith.constant 0 : i32
%v139 = arith.constant 0.5 : f64
%v140 = arith.constant 1.5 : f64
%v141 = arith.constant 2.5 : f64
%v142 = arith.constant 3.5 : f64
%v143 = llvm.mlir.constant(1 : i64) : i64
%v144 = llvm.alloca %v143 x !llvm.array<4 x f64> : (i64) -> !llvm.ptr
%v145 = llvm.mlir.zero : !llvm.array<4 x f64>
llvm.store %v145, %v144 : !llvm.array<4 x f64>, !llvm.ptr
%v146 = llvm.mlir.constant(0 : i64) : i64
%v147 = llvm.getelementptr %v144[0, %v146] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v139, %v147 : f64, !llvm.ptr
%v148 = llvm.mlir.constant(1 : i64) : i64
%v149 = llvm.getelementptr %v144[0, %v148] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v140, %v149 : f64, !llvm.ptr
%v150 = llvm.mlir.constant(2 : i64) : i64
%v151 = llvm.getelementptr %v144[0, %v150] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v141, %v151 : f64, !llvm.ptr
%v152 = llvm.mlir.constant(3 : i64) : i64
%v153 = llvm.getelementptr %v144[0, %v152] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v142, %v153 : f64, !llvm.ptr
%v154 = arith.constant 4 : i32
%v155 = arith.constant 2.0 : f64
%v156 = func.call @scale(%v144, %v154, %v155) : (!llvm.ptr, i32, f64) -> f64
%v157 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v158 = llvm.call @printf(%v157, %v156) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v159 = arith.constant 0 : i32
%v160 = arith.constant 1 : i1
%v161 = arith.constant 0 : i1
%v162 = llvm.mlir.constant(1 : i64) : i64
%v163 = llvm.alloca %v162 x !llvm.array<2 x i1> : (i64) -> !llvm.ptr
%v164 = llvm.mlir.zero : !llvm.array<2 x i1>
llvm.store %v164, %v163 : !llvm.array<2 x i1>, !llvm.ptr
%v165 = llvm.mlir.constant(0 : i64) : i64
%v166 = llvm.getelementptr %v163[0, %v165] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x i1>
llvm.store %v160, %v166 : i1, !llvm.ptr
%v167 = llvm.mlir.constant(1 : i64) : i64
%v168 = llvm.getelementptr %v163[0, %v167] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x i1>
llvm.store %v161, %v168 : i1, !llvm.ptr
%v169 = arith.constant 0 : i32
%v170 = arith.extsi %v169 : i32 to i64
%v171 = llvm.getelementptr %v163[0, %v170] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x i1>
%v172 = llvm.load %v171 : !llvm.ptr -> i1
cf.cond_br %v172, ^b10, ^b11
^b10:
%v173 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v174 = llvm.call @printf(%v173) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v175 = arith.constant 0 : i32
cf.br ^b12
^b11:
cf.br ^b12
^b12:
%v176 = arith.constant 0 : i32
func.return %v176 : i32
}
}
