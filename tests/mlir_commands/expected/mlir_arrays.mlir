module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\n\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_1("%f\n\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_2("first\n\00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
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
%v20 = arith.constant 0.0 : f32
%v21 = arith.extf %v20 : f32 to f64
%v22 = llvm.mlir.constant(1 : i64) : i64
%v23 = llvm.alloca %v22 x f64 : (i64) -> !llvm.ptr
llvm.store %v21, %v23 : f64, !llvm.ptr
%v24 = arith.constant 0 : i32
%v25 = arith.index_cast %v24 : i32 to index
%v26 = arith.index_cast %arg1 : i32 to index
%v27 = arith.constant 1 : index
%v28 = arith.constant -1 : index
%v29 = arith.cmpi sle, %v25, %v26 : index
%v30 = arith.select %v29, %v27, %v28 : index
cf.br ^b4(%v25 : index)
^b4(%v31: index):
%v32 = arith.cmpi slt, %v31, %v26 : index
%v33 = arith.cmpi sgt, %v31, %v26 : index
%v34 = arith.select %v29, %v32, %v33 : i1
cf.cond_br %v34, ^b5(%v31 : index), ^b6(%v31 : index)
^b5(%v35: index):
%v36 = llvm.load %v23 : !llvm.ptr -> f64
%v37 = arith.index_cast %v35 : index to i64
%v38 = llvm.getelementptr %arg0[%v37] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v39 = llvm.load %v38 : !llvm.ptr -> f64
%v40 = arith.mulf %v39, %arg2 : f64
%v41 = arith.addf %v36, %v40 : f64
llvm.store %v41, %v23 : f64, !llvm.ptr
%v42 = arith.addi %v35, %v30 : index
cf.br ^b4(%v42 : index)
^b6(%v43: index):
%v44 = llvm.load %v23 : !llvm.ptr -> f64
func.return %v44 : f64
}
func.func @main() -> i32 {
%v45 = arith.constant 3 : i32
%v46 = arith.constant 1 : i32
%v47 = arith.constant 4 : i32
%v48 = arith.constant 1 : i32
%v49 = arith.constant 5 : i32
%v50 = llvm.mlir.constant(1 : i64) : i64
%v51 = llvm.alloca %v50 x !llvm.array<5 x i32> : (i64) -> !llvm.ptr
%v52 = llvm.mlir.zero : !llvm.array<5 x i32>
llvm.store %v52, %v51 : !llvm.array<5 x i32>, !llvm.ptr
%v53 = llvm.mlir.constant(0 : i64) : i64
%v54 = llvm.getelementptr %v51[0, %v53] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v45, %v54 : i32, !llvm.ptr
%v55 = llvm.mlir.constant(1 : i64) : i64
%v56 = llvm.getelementptr %v51[0, %v55] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v46, %v56 : i32, !llvm.ptr
%v57 = llvm.mlir.constant(2 : i64) : i64
%v58 = llvm.getelementptr %v51[0, %v57] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v47, %v58 : i32, !llvm.ptr
%v59 = llvm.mlir.constant(3 : i64) : i64
%v60 = llvm.getelementptr %v51[0, %v59] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v48, %v60 : i32, !llvm.ptr
%v61 = llvm.mlir.constant(4 : i64) : i64
%v62 = llvm.getelementptr %v51[0, %v61] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v49, %v62 : i32, !llvm.ptr
%v63 = func.call @total(%v51) : (!llvm.ptr) -> i32
%v64 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v65 = llvm.call @printf(%v64, %v63) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v66 = arith.constant 0 : i32
%v67 = arith.constant 40 : i32
%v68 = arith.constant 2 : i32
%v69 = arith.extsi %v68 : i32 to i64
%v70 = llvm.getelementptr %v51[0, %v69] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v67, %v70 : i32, !llvm.ptr
%v71 = arith.constant 4 : i32
%v72 = arith.extsi %v71 : i32 to i64
%v73 = llvm.getelementptr %v51[0, %v72] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
%v74 = llvm.load %v73 : !llvm.ptr -> i32
%v75 = arith.constant 100 : i32
%v76 = arith.addi %v74, %v75 : i32
%v77 = arith.extsi %v71 : i32 to i64
%v78 = llvm.getelementptr %v51[0, %v77] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v76, %v78 : i32, !llvm.ptr
%v79 = func.call @total(%v51) : (!llvm.ptr) -> i32
%v80 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v81 = llvm.call @printf(%v80, %v79) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v82 = arith.constant 0 : i32
%v83 = arith.constant 2 : i32
%v84 = arith.extsi %v83 : i32 to i64
%v85 = llvm.getelementptr %v51[0, %v84] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
%v86 = llvm.load %v85 : !llvm.ptr -> i32
%v87 = arith.constant 4 : i32
%v88 = arith.extsi %v87 : i32 to i64
%v89 = llvm.getelementptr %v51[0, %v88] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
%v90 = llvm.load %v89 : !llvm.ptr -> i32
%v91 = arith.addi %v86, %v90 : i32
%v92 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v93 = llvm.call @printf(%v92, %v91) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v94 = arith.constant 0 : i32
%v95 = arith.constant 1 : i32
%v96 = arith.constant 2 : i32
%v97 = arith.constant 3 : i32
%v98 = llvm.mlir.constant(1 : i64) : i64
%v99 = llvm.alloca %v98 x !llvm.array<3 x i64> : (i64) -> !llvm.ptr
%v100 = llvm.mlir.zero : !llvm.array<3 x i64>
llvm.store %v100, %v99 : !llvm.array<3 x i64>, !llvm.ptr
%v101 = arith.extsi %v95 : i32 to i64
%v102 = arith.extsi %v96 : i32 to i64
%v103 = arith.extsi %v97 : i32 to i64
%v104 = llvm.mlir.constant(0 : i64) : i64
%v105 = llvm.getelementptr %v99[0, %v104] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
llvm.store %v101, %v105 : i64, !llvm.ptr
%v106 = llvm.mlir.constant(1 : i64) : i64
%v107 = llvm.getelementptr %v99[0, %v106] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
llvm.store %v102, %v107 : i64, !llvm.ptr
%v108 = llvm.mlir.constant(2 : i64) : i64
%v109 = llvm.getelementptr %v99[0, %v108] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
llvm.store %v103, %v109 : i64, !llvm.ptr
%v110 = arith.constant 0 : i32
%v111 = arith.extsi %v110 : i32 to i64
%v112 = llvm.mlir.constant(1 : i64) : i64
%v113 = llvm.alloca %v112 x i64 : (i64) -> !llvm.ptr
llvm.store %v111, %v113 : i64, !llvm.ptr
%v114 = arith.constant 0 : i32
%v115 = arith.constant 3 : i32
%v116 = arith.index_cast %v114 : i32 to index
%v117 = arith.index_cast %v115 : i32 to index
%v118 = arith.constant 1 : index
%v119 = arith.constant -1 : index
%v120 = arith.cmpi sle, %v116, %v117 : index
%v121 = arith.select %v120, %v118, %v119 : index
cf.br ^b7(%v116 : index)
^b7(%v122: index):
%v123 = arith.cmpi slt, %v122, %v117 : index
%v124 = arith.cmpi sgt, %v122, %v117 : index
%v125 = arith.select %v120, %v123, %v124 : i1
cf.cond_br %v125, ^b8(%v122 : index), ^b9(%v122 : index)
^b8(%v126: index):
%v127 = llvm.load %v113 : !llvm.ptr -> i64
%v128 = arith.index_cast %v126 : index to i64
%v129 = llvm.getelementptr %v99[0, %v128] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
%v130 = llvm.load %v129 : !llvm.ptr -> i64
%v131 = arith.constant 1000000 : i32
%v132 = arith.extsi %v131 : i32 to i64
%v133 = arith.muli %v130, %v132 : i64
%v134 = arith.addi %v127, %v133 : i64
llvm.store %v134, %v113 : i64, !llvm.ptr
%v135 = arith.addi %v126, %v121 : index
cf.br ^b7(%v135 : index)
^b9(%v136: index):
%v137 = llvm.load %v113 : !llvm.ptr -> i64
%v138 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v139 = llvm.call @printf(%v138, %v137) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v140 = arith.constant 0 : i32
%v141 = arith.constant 0.5 : f32
%v142 = arith.constant 1.5 : f32
%v143 = arith.constant 2.5 : f32
%v144 = arith.constant 3.5 : f32
%v145 = llvm.mlir.constant(1 : i64) : i64
%v146 = llvm.alloca %v145 x !llvm.array<4 x f64> : (i64) -> !llvm.ptr
%v147 = llvm.mlir.zero : !llvm.array<4 x f64>
llvm.store %v147, %v146 : !llvm.array<4 x f64>, !llvm.ptr
%v148 = arith.extf %v141 : f32 to f64
%v149 = arith.extf %v142 : f32 to f64
%v150 = arith.extf %v143 : f32 to f64
%v151 = arith.extf %v144 : f32 to f64
%v152 = llvm.mlir.constant(0 : i64) : i64
%v153 = llvm.getelementptr %v146[0, %v152] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v148, %v153 : f64, !llvm.ptr
%v154 = llvm.mlir.constant(1 : i64) : i64
%v155 = llvm.getelementptr %v146[0, %v154] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v149, %v155 : f64, !llvm.ptr
%v156 = llvm.mlir.constant(2 : i64) : i64
%v157 = llvm.getelementptr %v146[0, %v156] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v150, %v157 : f64, !llvm.ptr
%v158 = llvm.mlir.constant(3 : i64) : i64
%v159 = llvm.getelementptr %v146[0, %v158] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v151, %v159 : f64, !llvm.ptr
%v160 = arith.constant 4 : i32
%v161 = arith.constant 2.0 : f32
%v162 = arith.extf %v161 : f32 to f64
%v163 = func.call @scale(%v146, %v160, %v162) : (!llvm.ptr, i32, f64) -> f64
%v164 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v165 = llvm.call @printf(%v164, %v163) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v166 = arith.constant 0 : i32
%v167 = arith.constant 1 : i1
%v168 = arith.constant 0 : i1
%v169 = llvm.mlir.constant(1 : i64) : i64
%v170 = llvm.alloca %v169 x !llvm.array<2 x i1> : (i64) -> !llvm.ptr
%v171 = llvm.mlir.zero : !llvm.array<2 x i1>
llvm.store %v171, %v170 : !llvm.array<2 x i1>, !llvm.ptr
%v172 = llvm.mlir.constant(0 : i64) : i64
%v173 = llvm.getelementptr %v170[0, %v172] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x i1>
llvm.store %v167, %v173 : i1, !llvm.ptr
%v174 = llvm.mlir.constant(1 : i64) : i64
%v175 = llvm.getelementptr %v170[0, %v174] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x i1>
llvm.store %v168, %v175 : i1, !llvm.ptr
%v176 = arith.constant 0 : i32
%v177 = arith.extsi %v176 : i32 to i64
%v178 = llvm.getelementptr %v170[0, %v177] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x i1>
%v179 = llvm.load %v178 : !llvm.ptr -> i1
cf.cond_br %v179, ^b10, ^b11
^b10:
%v180 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v181 = llvm.call @printf(%v180) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v182 = arith.constant 0 : i32
cf.br ^b12
^b11:
cf.br ^b12
^b12:
%v183 = arith.constant 0 : i32
func.return %v183 : i32
}
}
