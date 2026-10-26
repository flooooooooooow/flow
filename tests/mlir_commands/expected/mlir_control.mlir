module {
func.func private @strlen(!llvm.ptr) -> i64
func.func private @write(i32, !llvm.ptr, i64) -> i64
func.func private @abort() -> ()
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("flow: \00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
llvm.mlir.global internal constant @str_1("\0A\00") {addr_space = 0 : i32} : !llvm.array<2 x i8>
llvm.mlir.global internal constant @str_2("division by zero\00") {addr_space = 0 : i32} : !llvm.array<17 x i8>
llvm.mlir.global internal constant @str_3("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_4("large\0A\00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
llvm.mlir.global internal constant @str_5("small\0A\00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
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
%v13 = arith.constant 1 : i32
%v14 = llvm.mlir.constant(1 : i64) : i64
%v15 = llvm.alloca %v14 x i32 : (i64) -> !llvm.ptr
llvm.store %v13, %v15 : i32, !llvm.ptr
cf.br ^b7
^b7:
%v16 = llvm.load %v15 : !llvm.ptr -> i32
%v17 = arith.cmpi slt, %v16, %arg0 : i32
cf.cond_br %v17, ^b8, ^b9
^b8:
%v18 = llvm.load %v15 : !llvm.ptr -> i32
%v19 = arith.constant 0 : i32
%v20 = arith.cmpi eq, %arg1, %v19 : i32
scf.if %v20 {
%v21 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v21) : (!llvm.ptr) -> ()
}
%v22 = arith.remsi %v18, %arg1 : i32
%v23 = arith.constant 0 : i32
%v24 = arith.cmpi eq, %v22, %v23 : i32
cf.cond_br %v24, ^b10, ^b11
^b10:
%v25 = llvm.load %v15 : !llvm.ptr -> i32
func.return %v25 : i32
^b11:
cf.br ^b12
^b12:
%v26 = llvm.load %v15 : !llvm.ptr -> i32
%v27 = arith.constant 1 : i32
%v28 = arith.addi %v26, %v27 : i32
llvm.store %v28, %v15 : i32, !llvm.ptr
cf.br ^b7
^b9:
%v29 = arith.constant 0 : i32
%v30 = arith.constant 1 : i32
%v31 = arith.subi %v29, %v30 : i32
func.return %v31 : i32
}
func.func @collatz(%arg0: i32) -> i32 {
%v32 = llvm.mlir.constant(1 : i64) : i64
%v33 = llvm.alloca %v32 x i32 : (i64) -> !llvm.ptr
llvm.store %arg0, %v33 : i32, !llvm.ptr
%v34 = arith.constant 0 : i32
%v35 = llvm.mlir.constant(1 : i64) : i64
%v36 = llvm.alloca %v35 x i32 : (i64) -> !llvm.ptr
llvm.store %v34, %v36 : i32, !llvm.ptr
cf.br ^b13
^b13:
%v37 = llvm.load %v33 : !llvm.ptr -> i32
%v38 = arith.constant 1 : i32
%v39 = arith.cmpi ne, %v37, %v38 : i32
cf.cond_br %v39, ^b14, ^b15
^b14:
%v40 = llvm.load %v33 : !llvm.ptr -> i32
%v41 = arith.constant 2 : i32
%v42 = arith.constant 0 : i32
%v43 = arith.cmpi eq, %v41, %v42 : i32
scf.if %v43 {
%v44 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v44) : (!llvm.ptr) -> ()
}
%v45 = arith.remsi %v40, %v41 : i32
%v46 = arith.constant 0 : i32
%v47 = arith.cmpi eq, %v45, %v46 : i32
cf.cond_br %v47, ^b16, ^b17
^b16:
%v48 = llvm.load %v33 : !llvm.ptr -> i32
%v49 = arith.constant 2 : i32
%v50 = arith.constant 0 : i32
%v51 = arith.cmpi eq, %v49, %v50 : i32
scf.if %v51 {
%v52 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v52) : (!llvm.ptr) -> ()
}
%v53 = arith.divsi %v48, %v49 : i32
llvm.store %v53, %v33 : i32, !llvm.ptr
cf.br ^b18
^b17:
%v54 = arith.constant 3 : i32
%v55 = llvm.load %v33 : !llvm.ptr -> i32
%v56 = arith.muli %v54, %v55 : i32
%v57 = arith.constant 1 : i32
%v58 = arith.addi %v56, %v57 : i32
llvm.store %v58, %v33 : i32, !llvm.ptr
cf.br ^b18
^b18:
%v59 = llvm.load %v36 : !llvm.ptr -> i32
%v60 = arith.constant 1 : i32
%v61 = arith.addi %v59, %v60 : i32
llvm.store %v61, %v36 : i32, !llvm.ptr
cf.br ^b13
^b15:
%v62 = llvm.load %v36 : !llvm.ptr -> i32
func.return %v62 : i32
}
func.func @main() -> i32 {
%v63 = arith.constant 0 : i32
%v64 = arith.constant 5 : i32
%v65 = arith.subi %v63, %v64 : i32
%v66 = func.call @classify(%v65) : (i32) -> i32
%v67 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v68 = llvm.call @printf(%v67, %v66) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v69 = arith.constant 0 : i32
%v70 = arith.constant 0 : i32
%v71 = func.call @classify(%v70) : (i32) -> i32
%v72 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v73 = llvm.call @printf(%v72, %v71) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v74 = arith.constant 0 : i32
%v75 = arith.constant 7 : i32
%v76 = func.call @classify(%v75) : (i32) -> i32
%v77 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v78 = llvm.call @printf(%v77, %v76) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v79 = arith.constant 0 : i32
%v80 = arith.constant 70 : i32
%v81 = func.call @classify(%v80) : (i32) -> i32
%v82 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v83 = llvm.call @printf(%v82, %v81) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v84 = arith.constant 0 : i32
%v85 = arith.constant 50 : i32
%v86 = arith.constant 13 : i32
%v87 = func.call @first_multiple(%v85, %v86) : (i32, i32) -> i32
%v88 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v89 = llvm.call @printf(%v88, %v87) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v90 = arith.constant 0 : i32
%v91 = arith.constant 5 : i32
%v92 = arith.constant 13 : i32
%v93 = func.call @first_multiple(%v91, %v92) : (i32, i32) -> i32
%v94 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v95 = llvm.call @printf(%v94, %v93) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v96 = arith.constant 0 : i32
%v97 = arith.constant 27 : i32
%v98 = func.call @collatz(%v97) : (i32) -> i32
%v99 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v100 = llvm.call @printf(%v99, %v98) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v101 = arith.constant 0 : i32
%v102 = arith.constant 0 : i32
%v103 = llvm.mlir.constant(1 : i64) : i64
%v104 = llvm.alloca %v103 x i32 : (i64) -> !llvm.ptr
llvm.store %v102, %v104 : i32, !llvm.ptr
%v105 = arith.constant 0 : i32
%v106 = llvm.mlir.constant(1 : i64) : i64
%v107 = llvm.alloca %v106 x i32 : (i64) -> !llvm.ptr
llvm.store %v105, %v107 : i32, !llvm.ptr
cf.br ^b19
^b19:
%v108 = llvm.load %v104 : !llvm.ptr -> i32
%v109 = arith.constant 20 : i32
%v110 = arith.cmpi slt, %v108, %v109 : i32
cf.cond_br %v110, ^b20, ^b21
^b20:
%v111 = llvm.load %v104 : !llvm.ptr -> i32
%v112 = arith.constant 1 : i32
%v113 = arith.addi %v111, %v112 : i32
llvm.store %v113, %v104 : i32, !llvm.ptr
%v114 = llvm.load %v104 : !llvm.ptr -> i32
%v115 = arith.constant 2 : i32
%v116 = arith.constant 0 : i32
%v117 = arith.cmpi eq, %v115, %v116 : i32
scf.if %v117 {
%v118 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v118) : (!llvm.ptr) -> ()
}
%v119 = arith.remsi %v114, %v115 : i32
%v120 = arith.constant 0 : i32
%v121 = arith.cmpi eq, %v119, %v120 : i32
cf.cond_br %v121, ^b22, ^b23
^b22:
cf.br ^b19
^b23:
cf.br ^b24
^b24:
%v122 = llvm.load %v104 : !llvm.ptr -> i32
%v123 = arith.constant 15 : i32
%v124 = arith.cmpi sgt, %v122, %v123 : i32
cf.cond_br %v124, ^b25, ^b26
^b25:
cf.br ^b21
^b26:
cf.br ^b27
^b27:
%v125 = llvm.load %v107 : !llvm.ptr -> i32
%v126 = llvm.load %v104 : !llvm.ptr -> i32
%v127 = arith.addi %v125, %v126 : i32
llvm.store %v127, %v107 : i32, !llvm.ptr
cf.br ^b19
^b21:
%v128 = llvm.load %v107 : !llvm.ptr -> i32
%v129 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v130 = llvm.call @printf(%v129, %v128) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v131 = arith.constant 0 : i32
%v132 = arith.constant 0 : i32
%v133 = llvm.mlir.constant(1 : i64) : i64
%v134 = llvm.alloca %v133 x i32 : (i64) -> !llvm.ptr
llvm.store %v132, %v134 : i32, !llvm.ptr
%v135 = arith.constant 0 : i32
%v136 = llvm.mlir.constant(1 : i64) : i64
%v137 = llvm.alloca %v136 x i32 : (i64) -> !llvm.ptr
llvm.store %v135, %v137 : i32, !llvm.ptr
cf.br ^b28
^b28:
%v138 = llvm.load %v134 : !llvm.ptr -> i32
%v139 = arith.constant 4 : i32
%v140 = arith.cmpi slt, %v138, %v139 : i32
cf.cond_br %v140, ^b29, ^b30
^b29:
%v141 = arith.constant 0 : i32
%v142 = llvm.mlir.constant(1 : i64) : i64
%v143 = llvm.alloca %v142 x i32 : (i64) -> !llvm.ptr
llvm.store %v141, %v143 : i32, !llvm.ptr
cf.br ^b31
^b31:
%v144 = llvm.load %v143 : !llvm.ptr -> i32
%v145 = llvm.load %v134 : !llvm.ptr -> i32
%v146 = arith.cmpi slt, %v144, %v145 : i32
cf.cond_br %v146, ^b32, ^b33
^b32:
%v147 = llvm.load %v137 : !llvm.ptr -> i32
%v148 = llvm.load %v134 : !llvm.ptr -> i32
%v149 = llvm.load %v143 : !llvm.ptr -> i32
%v150 = arith.muli %v148, %v149 : i32
%v151 = arith.addi %v147, %v150 : i32
llvm.store %v151, %v137 : i32, !llvm.ptr
%v152 = llvm.load %v143 : !llvm.ptr -> i32
%v153 = arith.constant 1 : i32
%v154 = arith.addi %v152, %v153 : i32
llvm.store %v154, %v143 : i32, !llvm.ptr
cf.br ^b31
^b33:
%v155 = llvm.load %v134 : !llvm.ptr -> i32
%v156 = arith.constant 1 : i32
%v157 = arith.addi %v155, %v156 : i32
llvm.store %v157, %v134 : i32, !llvm.ptr
cf.br ^b28
^b30:
%v158 = llvm.load %v137 : !llvm.ptr -> i32
%v159 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v160 = llvm.call @printf(%v159, %v158) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v161 = arith.constant 0 : i32
%v162 = llvm.load %v137 : !llvm.ptr -> i32
%v163 = arith.constant 10 : i32
%v164 = arith.cmpi sgt, %v162, %v163 : i32
cf.cond_br %v164, ^b34, ^b35
^b34:
%v165 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v166 = llvm.call @printf(%v165) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v167 = arith.constant 0 : i32
cf.br ^b36
^b35:
%v168 = llvm.mlir.addressof @str_5 : !llvm.ptr
%v169 = llvm.call @printf(%v168) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v170 = arith.constant 0 : i32
cf.br ^b36
^b36:
%v171 = arith.constant 0 : i32
func.return %v171 : i32
}
}
