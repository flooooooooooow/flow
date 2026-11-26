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
%v25 = llvm.load %v14 : !llvm.ptr -> i32
func.return %v25 : i32
^b11:
cf.br ^b12
^b12:
%v26 = llvm.load %v14 : !llvm.ptr -> i32
%v27 = arith.constant 1 : i32
%v28 = arith.addi %v26, %v27 : i32
llvm.store %v28, %v14 : i32, !llvm.ptr
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
%v34 = llvm.mlir.constant(1 : i64) : i64
%v35 = llvm.alloca %v34 x i32 : (i64) -> !llvm.ptr
llvm.store %arg0, %v33 : i32, !llvm.ptr
%v36 = arith.constant 0 : i32
llvm.store %v36, %v35 : i32, !llvm.ptr
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
%v59 = llvm.load %v35 : !llvm.ptr -> i32
%v60 = arith.constant 1 : i32
%v61 = arith.addi %v59, %v60 : i32
llvm.store %v61, %v35 : i32, !llvm.ptr
cf.br ^b13
^b15:
%v62 = llvm.load %v35 : !llvm.ptr -> i32
func.return %v62 : i32
}
func.func @main() -> i32 {
%v63 = llvm.mlir.constant(1 : i64) : i64
%v64 = llvm.alloca %v63 x i32 : (i64) -> !llvm.ptr
%v65 = llvm.mlir.constant(1 : i64) : i64
%v66 = llvm.alloca %v65 x i32 : (i64) -> !llvm.ptr
%v67 = llvm.mlir.constant(1 : i64) : i64
%v68 = llvm.alloca %v67 x i32 : (i64) -> !llvm.ptr
%v69 = llvm.mlir.constant(1 : i64) : i64
%v70 = llvm.alloca %v69 x i32 : (i64) -> !llvm.ptr
%v71 = llvm.mlir.constant(1 : i64) : i64
%v72 = llvm.alloca %v71 x i32 : (i64) -> !llvm.ptr
%v73 = arith.constant 0 : i32
%v74 = arith.constant 5 : i32
%v75 = arith.subi %v73, %v74 : i32
%v76 = func.call @classify(%v75) : (i32) -> i32
%v77 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v78 = llvm.call @printf(%v77, %v76) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v79 = arith.constant 0 : i32
%v80 = arith.constant 0 : i32
%v81 = func.call @classify(%v80) : (i32) -> i32
%v82 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v83 = llvm.call @printf(%v82, %v81) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v84 = arith.constant 0 : i32
%v85 = arith.constant 7 : i32
%v86 = func.call @classify(%v85) : (i32) -> i32
%v87 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v88 = llvm.call @printf(%v87, %v86) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v89 = arith.constant 0 : i32
%v90 = arith.constant 70 : i32
%v91 = func.call @classify(%v90) : (i32) -> i32
%v92 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v93 = llvm.call @printf(%v92, %v91) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v94 = arith.constant 0 : i32
%v95 = arith.constant 50 : i32
%v96 = arith.constant 13 : i32
%v97 = func.call @first_multiple(%v95, %v96) : (i32, i32) -> i32
%v98 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v99 = llvm.call @printf(%v98, %v97) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v100 = arith.constant 0 : i32
%v101 = arith.constant 5 : i32
%v102 = arith.constant 13 : i32
%v103 = func.call @first_multiple(%v101, %v102) : (i32, i32) -> i32
%v104 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v105 = llvm.call @printf(%v104, %v103) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v106 = arith.constant 0 : i32
%v107 = arith.constant 27 : i32
%v108 = func.call @collatz(%v107) : (i32) -> i32
%v109 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v110 = llvm.call @printf(%v109, %v108) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v111 = arith.constant 0 : i32
%v112 = arith.constant 0 : i32
llvm.store %v112, %v64 : i32, !llvm.ptr
%v113 = arith.constant 0 : i32
llvm.store %v113, %v66 : i32, !llvm.ptr
cf.br ^b19
^b19:
%v114 = llvm.load %v64 : !llvm.ptr -> i32
%v115 = arith.constant 20 : i32
%v116 = arith.cmpi slt, %v114, %v115 : i32
cf.cond_br %v116, ^b20, ^b21
^b20:
%v117 = llvm.load %v64 : !llvm.ptr -> i32
%v118 = arith.constant 1 : i32
%v119 = arith.addi %v117, %v118 : i32
llvm.store %v119, %v64 : i32, !llvm.ptr
%v120 = llvm.load %v64 : !llvm.ptr -> i32
%v121 = arith.constant 2 : i32
%v122 = arith.constant 0 : i32
%v123 = arith.cmpi eq, %v121, %v122 : i32
scf.if %v123 {
%v124 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v124) : (!llvm.ptr) -> ()
}
%v125 = arith.remsi %v120, %v121 : i32
%v126 = arith.constant 0 : i32
%v127 = arith.cmpi eq, %v125, %v126 : i32
cf.cond_br %v127, ^b22, ^b23
^b22:
cf.br ^b19
^b23:
cf.br ^b24
^b24:
%v128 = llvm.load %v64 : !llvm.ptr -> i32
%v129 = arith.constant 15 : i32
%v130 = arith.cmpi sgt, %v128, %v129 : i32
cf.cond_br %v130, ^b25, ^b26
^b25:
cf.br ^b21
^b26:
cf.br ^b27
^b27:
%v131 = llvm.load %v66 : !llvm.ptr -> i32
%v132 = llvm.load %v64 : !llvm.ptr -> i32
%v133 = arith.addi %v131, %v132 : i32
llvm.store %v133, %v66 : i32, !llvm.ptr
cf.br ^b19
^b21:
%v134 = llvm.load %v66 : !llvm.ptr -> i32
%v135 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v136 = llvm.call @printf(%v135, %v134) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v137 = arith.constant 0 : i32
%v138 = arith.constant 0 : i32
llvm.store %v138, %v68 : i32, !llvm.ptr
%v139 = arith.constant 0 : i32
llvm.store %v139, %v70 : i32, !llvm.ptr
cf.br ^b28
^b28:
%v140 = llvm.load %v68 : !llvm.ptr -> i32
%v141 = arith.constant 4 : i32
%v142 = arith.cmpi slt, %v140, %v141 : i32
cf.cond_br %v142, ^b29, ^b30
^b29:
%v143 = arith.constant 0 : i32
llvm.store %v143, %v72 : i32, !llvm.ptr
cf.br ^b31
^b31:
%v144 = llvm.load %v72 : !llvm.ptr -> i32
%v145 = llvm.load %v68 : !llvm.ptr -> i32
%v146 = arith.cmpi slt, %v144, %v145 : i32
cf.cond_br %v146, ^b32, ^b33
^b32:
%v147 = llvm.load %v70 : !llvm.ptr -> i32
%v148 = llvm.load %v68 : !llvm.ptr -> i32
%v149 = llvm.load %v72 : !llvm.ptr -> i32
%v150 = arith.muli %v148, %v149 : i32
%v151 = arith.addi %v147, %v150 : i32
llvm.store %v151, %v70 : i32, !llvm.ptr
%v152 = llvm.load %v72 : !llvm.ptr -> i32
%v153 = arith.constant 1 : i32
%v154 = arith.addi %v152, %v153 : i32
llvm.store %v154, %v72 : i32, !llvm.ptr
cf.br ^b31
^b33:
%v155 = llvm.load %v68 : !llvm.ptr -> i32
%v156 = arith.constant 1 : i32
%v157 = arith.addi %v155, %v156 : i32
llvm.store %v157, %v68 : i32, !llvm.ptr
cf.br ^b28
^b30:
%v158 = llvm.load %v70 : !llvm.ptr -> i32
%v159 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v160 = llvm.call @printf(%v159, %v158) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v161 = arith.constant 0 : i32
%v162 = llvm.load %v70 : !llvm.ptr -> i32
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
