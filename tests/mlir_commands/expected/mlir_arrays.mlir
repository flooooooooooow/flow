module {
func.func private @strlen(!llvm.ptr) -> i64
func.func private @write(i32, !llvm.ptr, i64) -> i64
func.func private @abort() -> ()
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("flow: \00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
llvm.mlir.global internal constant @str_1("\0A\00") {addr_space = 0 : i32} : !llvm.array<2 x i8>
llvm.mlir.global internal constant @str_2("array index out of bounds\00") {addr_space = 0 : i32} : !llvm.array<26 x i8>
llvm.mlir.global internal constant @str_3("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_4("%lld\0A\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
llvm.mlir.global internal constant @str_5("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_6("first\0A\00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
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
%v12 = arith.constant 5 : i32
%v13 = arith.cmpi uge, %v11, %v12 : i32
scf.if %v13 {
%v14 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v14) : (!llvm.ptr) -> ()
}
%v15 = arith.extsi %v11 : i32 to i64
%v16 = llvm.getelementptr %arg0[0, %v15] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
%v17 = llvm.load %v16 : !llvm.ptr -> i32
%v18 = arith.addi %v10, %v17 : i32
llvm.store %v18, %v3 : i32, !llvm.ptr
%v19 = llvm.load %v6 : !llvm.ptr -> i32
%v20 = arith.constant 1 : i32
%v21 = arith.addi %v19, %v20 : i32
llvm.store %v21, %v6 : i32, !llvm.ptr
cf.br ^b1
^b3:
%v22 = llvm.load %v3 : !llvm.ptr -> i32
func.return %v22 : i32
}
func.func @scale(%arg0: !llvm.ptr, %arg1: i32, %arg2: f64) -> f64 {
%v23 = arith.constant 0.0 : f64
%v24 = llvm.mlir.constant(1 : i64) : i64
%v25 = llvm.alloca %v24 x f64 : (i64) -> !llvm.ptr
llvm.store %v23, %v25 : f64, !llvm.ptr
%v26 = arith.constant 0 : i32
%v27 = arith.index_cast %v26 : i32 to index
%v28 = arith.index_cast %arg1 : i32 to index
%v29 = arith.constant 1 : index
%v30 = arith.constant -1 : index
%v31 = arith.cmpi sle, %v27, %v28 : index
%v32 = arith.select %v31, %v29, %v30 : index
cf.br ^b4(%v27 : index)
^b4(%v33: index):
%v34 = arith.cmpi slt, %v33, %v28 : index
%v35 = arith.cmpi sgt, %v33, %v28 : index
%v36 = arith.select %v31, %v34, %v35 : i1
cf.cond_br %v36, ^b5(%v33 : index), ^b6(%v33 : index)
^b5(%v37: index):
%v38 = llvm.load %v25 : !llvm.ptr -> f64
%v39 = arith.index_cast %v37 : index to i64
%v40 = llvm.getelementptr %arg0[%v39] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v41 = llvm.load %v40 : !llvm.ptr -> f64
%v42 = llvm.intr.fma(%v41, %arg2, %v38) : (f64, f64, f64) -> f64
llvm.store %v42, %v25 : f64, !llvm.ptr
%v43 = arith.addi %v37, %v32 : index
cf.br ^b4(%v43 : index)
^b6(%v44: index):
%v45 = llvm.load %v25 : !llvm.ptr -> f64
func.return %v45 : f64
}
func.func @main() -> i32 {
%v46 = arith.constant 3 : i32
%v47 = arith.constant 1 : i32
%v48 = arith.constant 4 : i32
%v49 = arith.constant 1 : i32
%v50 = arith.constant 5 : i32
%v51 = llvm.mlir.constant(1 : i64) : i64
%v52 = llvm.alloca %v51 x !llvm.array<5 x i32> : (i64) -> !llvm.ptr
%v53 = llvm.mlir.zero : !llvm.array<5 x i32>
llvm.store %v53, %v52 : !llvm.array<5 x i32>, !llvm.ptr
%v54 = llvm.mlir.constant(0 : i64) : i64
%v55 = llvm.getelementptr %v52[0, %v54] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v46, %v55 : i32, !llvm.ptr
%v56 = llvm.mlir.constant(1 : i64) : i64
%v57 = llvm.getelementptr %v52[0, %v56] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v47, %v57 : i32, !llvm.ptr
%v58 = llvm.mlir.constant(2 : i64) : i64
%v59 = llvm.getelementptr %v52[0, %v58] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v48, %v59 : i32, !llvm.ptr
%v60 = llvm.mlir.constant(3 : i64) : i64
%v61 = llvm.getelementptr %v52[0, %v60] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v49, %v61 : i32, !llvm.ptr
%v62 = llvm.mlir.constant(4 : i64) : i64
%v63 = llvm.getelementptr %v52[0, %v62] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v50, %v63 : i32, !llvm.ptr
%v64 = func.call @total(%v52) : (!llvm.ptr) -> i32
%v65 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v66 = llvm.call @printf(%v65, %v64) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v67 = arith.constant 0 : i32
%v68 = arith.constant 40 : i32
%v69 = arith.constant 2 : i32
%v70 = arith.extsi %v69 : i32 to i64
%v71 = llvm.getelementptr %v52[0, %v70] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v68, %v71 : i32, !llvm.ptr
%v72 = arith.constant 4 : i32
%v73 = arith.constant 5 : i32
%v74 = arith.cmpi uge, %v72, %v73 : i32
scf.if %v74 {
%v75 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v75) : (!llvm.ptr) -> ()
}
%v76 = arith.extsi %v72 : i32 to i64
%v77 = llvm.getelementptr %v52[0, %v76] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
%v78 = llvm.load %v77 : !llvm.ptr -> i32
%v79 = arith.constant 100 : i32
%v80 = arith.addi %v78, %v79 : i32
%v81 = arith.extsi %v72 : i32 to i64
%v82 = llvm.getelementptr %v52[0, %v81] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
llvm.store %v80, %v82 : i32, !llvm.ptr
%v83 = func.call @total(%v52) : (!llvm.ptr) -> i32
%v84 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v85 = llvm.call @printf(%v84, %v83) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v86 = arith.constant 0 : i32
%v87 = arith.constant 2 : i32
%v88 = arith.constant 5 : i32
%v89 = arith.cmpi uge, %v87, %v88 : i32
scf.if %v89 {
%v90 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v90) : (!llvm.ptr) -> ()
}
%v91 = arith.extsi %v87 : i32 to i64
%v92 = llvm.getelementptr %v52[0, %v91] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
%v93 = llvm.load %v92 : !llvm.ptr -> i32
%v94 = arith.constant 4 : i32
%v95 = arith.constant 5 : i32
%v96 = arith.cmpi uge, %v94, %v95 : i32
scf.if %v96 {
%v97 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v97) : (!llvm.ptr) -> ()
}
%v98 = arith.extsi %v94 : i32 to i64
%v99 = llvm.getelementptr %v52[0, %v98] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<5 x i32>
%v100 = llvm.load %v99 : !llvm.ptr -> i32
%v101 = arith.addi %v93, %v100 : i32
%v102 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v103 = llvm.call @printf(%v102, %v101) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v104 = arith.constant 0 : i32
%v105 = arith.constant 1 : i32
%v106 = arith.constant 2 : i32
%v107 = arith.constant 3 : i32
%v108 = llvm.mlir.constant(1 : i64) : i64
%v109 = llvm.alloca %v108 x !llvm.array<3 x i64> : (i64) -> !llvm.ptr
%v110 = llvm.mlir.zero : !llvm.array<3 x i64>
llvm.store %v110, %v109 : !llvm.array<3 x i64>, !llvm.ptr
%v111 = arith.extsi %v105 : i32 to i64
%v112 = arith.extsi %v106 : i32 to i64
%v113 = arith.extsi %v107 : i32 to i64
%v114 = llvm.mlir.constant(0 : i64) : i64
%v115 = llvm.getelementptr %v109[0, %v114] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
llvm.store %v111, %v115 : i64, !llvm.ptr
%v116 = llvm.mlir.constant(1 : i64) : i64
%v117 = llvm.getelementptr %v109[0, %v116] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
llvm.store %v112, %v117 : i64, !llvm.ptr
%v118 = llvm.mlir.constant(2 : i64) : i64
%v119 = llvm.getelementptr %v109[0, %v118] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
llvm.store %v113, %v119 : i64, !llvm.ptr
%v120 = arith.constant 0 : i32
%v121 = arith.extsi %v120 : i32 to i64
%v122 = llvm.mlir.constant(1 : i64) : i64
%v123 = llvm.alloca %v122 x i64 : (i64) -> !llvm.ptr
llvm.store %v121, %v123 : i64, !llvm.ptr
%v124 = arith.constant 0 : i32
%v125 = arith.constant 3 : i32
%v126 = arith.index_cast %v124 : i32 to index
%v127 = arith.index_cast %v125 : i32 to index
%v128 = arith.constant 1 : index
%v129 = arith.constant -1 : index
%v130 = arith.cmpi sle, %v126, %v127 : index
%v131 = arith.select %v130, %v128, %v129 : index
cf.br ^b7(%v126 : index)
^b7(%v132: index):
%v133 = arith.cmpi slt, %v132, %v127 : index
%v134 = arith.cmpi sgt, %v132, %v127 : index
%v135 = arith.select %v130, %v133, %v134 : i1
cf.cond_br %v135, ^b8(%v132 : index), ^b9(%v132 : index)
^b8(%v136: index):
%v137 = llvm.load %v123 : !llvm.ptr -> i64
%v138 = arith.index_cast %v136 : index to i32
%v139 = arith.constant 3 : i32
%v140 = arith.cmpi uge, %v138, %v139 : i32
scf.if %v140 {
%v141 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v141) : (!llvm.ptr) -> ()
}
%v142 = arith.index_cast %v136 : index to i64
%v143 = llvm.getelementptr %v109[0, %v142] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i64>
%v144 = llvm.load %v143 : !llvm.ptr -> i64
%v145 = arith.constant 1000000 : i32
%v146 = arith.extsi %v145 : i32 to i64
%v147 = arith.muli %v144, %v146 : i64
%v148 = arith.addi %v137, %v147 : i64
llvm.store %v148, %v123 : i64, !llvm.ptr
%v149 = arith.addi %v136, %v131 : index
cf.br ^b7(%v149 : index)
^b9(%v150: index):
%v151 = llvm.load %v123 : !llvm.ptr -> i64
%v152 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v153 = llvm.call @printf(%v152, %v151) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v154 = arith.constant 0 : i32
%v155 = arith.constant 0.5 : f64
%v156 = arith.constant 1.5 : f64
%v157 = arith.constant 2.5 : f64
%v158 = arith.constant 3.5 : f64
%v159 = llvm.mlir.constant(1 : i64) : i64
%v160 = llvm.alloca %v159 x !llvm.array<4 x f64> : (i64) -> !llvm.ptr
%v161 = llvm.mlir.zero : !llvm.array<4 x f64>
llvm.store %v161, %v160 : !llvm.array<4 x f64>, !llvm.ptr
%v162 = llvm.mlir.constant(0 : i64) : i64
%v163 = llvm.getelementptr %v160[0, %v162] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v155, %v163 : f64, !llvm.ptr
%v164 = llvm.mlir.constant(1 : i64) : i64
%v165 = llvm.getelementptr %v160[0, %v164] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v156, %v165 : f64, !llvm.ptr
%v166 = llvm.mlir.constant(2 : i64) : i64
%v167 = llvm.getelementptr %v160[0, %v166] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v157, %v167 : f64, !llvm.ptr
%v168 = llvm.mlir.constant(3 : i64) : i64
%v169 = llvm.getelementptr %v160[0, %v168] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f64>
llvm.store %v158, %v169 : f64, !llvm.ptr
%v170 = arith.constant 4 : i32
%v171 = arith.constant 2.0 : f64
%v172 = func.call @scale(%v160, %v170, %v171) : (!llvm.ptr, i32, f64) -> f64
%v173 = llvm.mlir.addressof @str_5 : !llvm.ptr
%v174 = llvm.call @printf(%v173, %v172) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v175 = arith.constant 0 : i32
%v176 = arith.constant 1 : i1
%v177 = arith.constant 0 : i1
%v178 = llvm.mlir.constant(1 : i64) : i64
%v179 = llvm.alloca %v178 x !llvm.array<2 x i1> : (i64) -> !llvm.ptr
%v180 = llvm.mlir.zero : !llvm.array<2 x i1>
llvm.store %v180, %v179 : !llvm.array<2 x i1>, !llvm.ptr
%v181 = llvm.mlir.constant(0 : i64) : i64
%v182 = llvm.getelementptr %v179[0, %v181] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x i1>
llvm.store %v176, %v182 : i1, !llvm.ptr
%v183 = llvm.mlir.constant(1 : i64) : i64
%v184 = llvm.getelementptr %v179[0, %v183] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x i1>
llvm.store %v177, %v184 : i1, !llvm.ptr
%v185 = arith.constant 0 : i32
%v186 = arith.constant 2 : i32
%v187 = arith.cmpi uge, %v185, %v186 : i32
scf.if %v187 {
%v188 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v188) : (!llvm.ptr) -> ()
}
%v189 = arith.extsi %v185 : i32 to i64
%v190 = llvm.getelementptr %v179[0, %v189] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<2 x i1>
%v191 = llvm.load %v190 : !llvm.ptr -> i1
cf.cond_br %v191, ^b10, ^b11
^b10:
%v192 = llvm.mlir.addressof @str_6 : !llvm.ptr
%v193 = llvm.call @printf(%v192) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v194 = arith.constant 0 : i32
cf.br ^b12
^b11:
cf.br ^b12
^b12:
%v195 = arith.constant 0 : i32
func.return %v195 : i32
}
}
