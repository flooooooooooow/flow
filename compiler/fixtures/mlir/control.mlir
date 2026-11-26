module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_1("large\0A\00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
llvm.mlir.global internal constant @str_2("small\0A\00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
func.func @classify(%arg0: i32) -> i32 {
%v1 = arith.constant 0 : i32
%v2 = arith.cmpi slt, %arg0, %v1 : i32
cf.cond_br %v2, ^b1, ^b2
^b1:
%v3 = arith.constant 0 : i32
%v4 = arith.constant 1 : i32
%v5 = arith.subi %v3, %v4 : i32
func.return %v5 : i32
^b2:
%v6 = arith.constant 0 : i32
%v7 = arith.cmpi eq, %arg0, %v6 : i32
cf.cond_br %v7, ^b3, ^b4
^b3:
%v8 = arith.constant 0 : i32
func.return %v8 : i32
^b4:
%v9 = arith.constant 10 : i32
%v10 = arith.cmpi slt, %arg0, %v9 : i32
cf.cond_br %v10, ^b5, ^b6
^b5:
%v11 = arith.constant 1 : i32
func.return %v11 : i32
^b6:
%v12 = arith.constant 2 : i32
func.return %v12 : i32
}
func.func @first_multiple(%arg0: i32, %arg1: i32) -> i32 {
%v13 = llvm.mlir.constant(1 : i64) : i64
%v14 = llvm.alloca %v13 x i32 : (i64) -> !llvm.ptr
%v15 = arith.constant 1 : i32
llvm.store %v15, %v14 : i32, !llvm.ptr
cf.br ^b7
^b7:
%v16 = llvm.load %v14 : !llvm.ptr -> i32
%v17 = arith.cmpi slt, %v16, %arg0 : i32
cf.cond_br %v17, ^b8, ^b9
^b8:
%v18 = llvm.load %v14 : !llvm.ptr -> i32
%v19 = arith.remsi %v18, %arg1 : i32
%v20 = arith.constant 0 : i32
%v21 = arith.cmpi eq, %v19, %v20 : i32
cf.cond_br %v21, ^b10, ^b11
^b10:
%v22 = llvm.load %v14 : !llvm.ptr -> i32
func.return %v22 : i32
^b11:
cf.br ^b12
^b12:
%v23 = llvm.load %v14 : !llvm.ptr -> i32
%v24 = arith.constant 1 : i32
%v25 = arith.addi %v23, %v24 : i32
llvm.store %v25, %v14 : i32, !llvm.ptr
cf.br ^b7
^b9:
%v26 = arith.constant 0 : i32
%v27 = arith.constant 1 : i32
%v28 = arith.subi %v26, %v27 : i32
func.return %v28 : i32
}
func.func @collatz(%arg0: i32) -> i32 {
%v29 = llvm.mlir.constant(1 : i64) : i64
%v30 = llvm.alloca %v29 x i32 : (i64) -> !llvm.ptr
%v31 = llvm.mlir.constant(1 : i64) : i64
%v32 = llvm.alloca %v31 x i32 : (i64) -> !llvm.ptr
llvm.store %arg0, %v30 : i32, !llvm.ptr
%v33 = arith.constant 0 : i32
llvm.store %v33, %v32 : i32, !llvm.ptr
cf.br ^b13
^b13:
%v34 = llvm.load %v30 : !llvm.ptr -> i32
%v35 = arith.constant 1 : i32
%v36 = arith.cmpi ne, %v34, %v35 : i32
cf.cond_br %v36, ^b14, ^b15
^b14:
%v37 = llvm.load %v30 : !llvm.ptr -> i32
%v38 = arith.constant 2 : i32
%v39 = arith.remsi %v37, %v38 : i32
%v40 = arith.constant 0 : i32
%v41 = arith.cmpi eq, %v39, %v40 : i32
cf.cond_br %v41, ^b16, ^b17
^b16:
%v42 = llvm.load %v30 : !llvm.ptr -> i32
%v43 = arith.constant 2 : i32
%v44 = arith.divsi %v42, %v43 : i32
llvm.store %v44, %v30 : i32, !llvm.ptr
cf.br ^b18
^b17:
%v45 = arith.constant 3 : i32
%v46 = llvm.load %v30 : !llvm.ptr -> i32
%v47 = arith.muli %v45, %v46 : i32
%v48 = arith.constant 1 : i32
%v49 = arith.addi %v47, %v48 : i32
llvm.store %v49, %v30 : i32, !llvm.ptr
cf.br ^b18
^b18:
%v50 = llvm.load %v32 : !llvm.ptr -> i32
%v51 = arith.constant 1 : i32
%v52 = arith.addi %v50, %v51 : i32
llvm.store %v52, %v32 : i32, !llvm.ptr
cf.br ^b13
^b15:
%v53 = llvm.load %v32 : !llvm.ptr -> i32
func.return %v53 : i32
}
func.func @main() -> i32 {
%v54 = llvm.mlir.constant(1 : i64) : i64
%v55 = llvm.alloca %v54 x i32 : (i64) -> !llvm.ptr
%v56 = llvm.mlir.constant(1 : i64) : i64
%v57 = llvm.alloca %v56 x i32 : (i64) -> !llvm.ptr
%v58 = llvm.mlir.constant(1 : i64) : i64
%v59 = llvm.alloca %v58 x i32 : (i64) -> !llvm.ptr
%v60 = llvm.mlir.constant(1 : i64) : i64
%v61 = llvm.alloca %v60 x i32 : (i64) -> !llvm.ptr
%v62 = llvm.mlir.constant(1 : i64) : i64
%v63 = llvm.alloca %v62 x i32 : (i64) -> !llvm.ptr
%v64 = arith.constant 0 : i32
%v65 = arith.constant 5 : i32
%v66 = arith.subi %v64, %v65 : i32
%v67 = func.call @classify(%v66) : (i32) -> i32
%v68 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v69 = llvm.call @printf(%v68, %v67) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v70 = arith.constant 0 : i32
%v71 = arith.constant 0 : i32
%v72 = func.call @classify(%v71) : (i32) -> i32
%v73 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v74 = llvm.call @printf(%v73, %v72) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v75 = arith.constant 0 : i32
%v76 = arith.constant 7 : i32
%v77 = func.call @classify(%v76) : (i32) -> i32
%v78 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v79 = llvm.call @printf(%v78, %v77) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v80 = arith.constant 0 : i32
%v81 = arith.constant 70 : i32
%v82 = func.call @classify(%v81) : (i32) -> i32
%v83 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v84 = llvm.call @printf(%v83, %v82) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v85 = arith.constant 0 : i32
%v86 = arith.constant 50 : i32
%v87 = arith.constant 13 : i32
%v88 = func.call @first_multiple(%v86, %v87) : (i32, i32) -> i32
%v89 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v90 = llvm.call @printf(%v89, %v88) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v91 = arith.constant 0 : i32
%v92 = arith.constant 5 : i32
%v93 = arith.constant 13 : i32
%v94 = func.call @first_multiple(%v92, %v93) : (i32, i32) -> i32
%v95 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v96 = llvm.call @printf(%v95, %v94) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v97 = arith.constant 0 : i32
%v98 = arith.constant 27 : i32
%v99 = func.call @collatz(%v98) : (i32) -> i32
%v100 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v101 = llvm.call @printf(%v100, %v99) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v102 = arith.constant 0 : i32
%v103 = arith.constant 0 : i32
llvm.store %v103, %v55 : i32, !llvm.ptr
%v104 = arith.constant 0 : i32
llvm.store %v104, %v57 : i32, !llvm.ptr
cf.br ^b19
^b19:
%v105 = llvm.load %v55 : !llvm.ptr -> i32
%v106 = arith.constant 20 : i32
%v107 = arith.cmpi slt, %v105, %v106 : i32
cf.cond_br %v107, ^b20, ^b21
^b20:
%v108 = llvm.load %v55 : !llvm.ptr -> i32
%v109 = arith.constant 1 : i32
%v110 = arith.addi %v108, %v109 : i32
llvm.store %v110, %v55 : i32, !llvm.ptr
%v111 = llvm.load %v55 : !llvm.ptr -> i32
%v112 = arith.constant 2 : i32
%v113 = arith.remsi %v111, %v112 : i32
%v114 = arith.constant 0 : i32
%v115 = arith.cmpi eq, %v113, %v114 : i32
cf.cond_br %v115, ^b22, ^b23
^b22:
cf.br ^b19
^b23:
cf.br ^b24
^b24:
%v116 = llvm.load %v55 : !llvm.ptr -> i32
%v117 = arith.constant 15 : i32
%v118 = arith.cmpi sgt, %v116, %v117 : i32
cf.cond_br %v118, ^b25, ^b26
^b25:
cf.br ^b21
^b26:
cf.br ^b27
^b27:
%v119 = llvm.load %v57 : !llvm.ptr -> i32
%v120 = llvm.load %v55 : !llvm.ptr -> i32
%v121 = arith.addi %v119, %v120 : i32
llvm.store %v121, %v57 : i32, !llvm.ptr
cf.br ^b19
^b21:
%v122 = llvm.load %v57 : !llvm.ptr -> i32
%v123 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v124 = llvm.call @printf(%v123, %v122) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v125 = arith.constant 0 : i32
%v126 = arith.constant 0 : i32
llvm.store %v126, %v59 : i32, !llvm.ptr
%v127 = arith.constant 0 : i32
llvm.store %v127, %v61 : i32, !llvm.ptr
cf.br ^b28
^b28:
%v128 = llvm.load %v59 : !llvm.ptr -> i32
%v129 = arith.constant 4 : i32
%v130 = arith.cmpi slt, %v128, %v129 : i32
cf.cond_br %v130, ^b29, ^b30
^b29:
%v131 = arith.constant 0 : i32
llvm.store %v131, %v63 : i32, !llvm.ptr
cf.br ^b31
^b31:
%v132 = llvm.load %v63 : !llvm.ptr -> i32
%v133 = llvm.load %v59 : !llvm.ptr -> i32
%v134 = arith.cmpi slt, %v132, %v133 : i32
cf.cond_br %v134, ^b32, ^b33
^b32:
%v135 = llvm.load %v61 : !llvm.ptr -> i32
%v136 = llvm.load %v59 : !llvm.ptr -> i32
%v137 = llvm.load %v63 : !llvm.ptr -> i32
%v138 = arith.muli %v136, %v137 : i32
%v139 = arith.addi %v135, %v138 : i32
llvm.store %v139, %v61 : i32, !llvm.ptr
%v140 = llvm.load %v63 : !llvm.ptr -> i32
%v141 = arith.constant 1 : i32
%v142 = arith.addi %v140, %v141 : i32
llvm.store %v142, %v63 : i32, !llvm.ptr
cf.br ^b31
^b33:
%v143 = llvm.load %v59 : !llvm.ptr -> i32
%v144 = arith.constant 1 : i32
%v145 = arith.addi %v143, %v144 : i32
llvm.store %v145, %v59 : i32, !llvm.ptr
cf.br ^b28
^b30:
%v146 = llvm.load %v61 : !llvm.ptr -> i32
%v147 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v148 = llvm.call @printf(%v147, %v146) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v149 = arith.constant 0 : i32
%v150 = llvm.load %v61 : !llvm.ptr -> i32
%v151 = arith.constant 10 : i32
%v152 = arith.cmpi sgt, %v150, %v151 : i32
cf.cond_br %v152, ^b34, ^b35
^b34:
%v153 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v154 = llvm.call @printf(%v153) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v155 = arith.constant 0 : i32
cf.br ^b36
^b35:
%v156 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v157 = llvm.call @printf(%v156) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v158 = arith.constant 0 : i32
cf.br ^b36
^b36:
%v159 = arith.constant 0 : i32
func.return %v159 : i32
}
}
