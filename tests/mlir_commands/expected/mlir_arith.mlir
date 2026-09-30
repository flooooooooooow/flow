module {
func.func private @strlen(!llvm.ptr) -> i64
func.func private @write(i32, !llvm.ptr, i64) -> i64
func.func private @abort() -> ()
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("flow: \00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
llvm.mlir.global internal constant @str_1("\0A\00") {addr_space = 0 : i32} : !llvm.array<2 x i8>
llvm.mlir.global internal constant @str_2("division by zero\00") {addr_space = 0 : i32} : !llvm.array<17 x i8>
llvm.mlir.global internal constant @str_3("invalid shift (amount out of range or left-shift of negative)\00") {addr_space = 0 : i32} : !llvm.array<62 x i8>
llvm.mlir.global internal constant @str_4("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_5("%lld\0A\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
llvm.mlir.global internal constant @str_6("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_7("unsigned compare\0A\00") {addr_space = 0 : i32} : !llvm.array<18 x i8>
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
func.func @mix(%arg0: i32, %arg1: i64) -> i64 {
%v1 = arith.extsi %arg0 : i32 to i64
%v2 = arith.muli %v1, %arg1 : i64
%v3 = arith.constant 7 : i32
%v4 = arith.extsi %v3 : i32 to i64
%v5 = arith.addi %v2, %v4 : i64
func.return %v5 : i64
}
func.func @udiv(%arg0: i32, %arg1: i32) -> i32 {
%v6 = arith.constant 0 : i32
%v7 = arith.cmpi eq, %arg1, %v6 : i32
scf.if %v7 {
%v8 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v8) : (!llvm.ptr) -> ()
}
%v9 = arith.divui %arg0, %arg1 : i32
func.return %v9 : i32
}
func.func @umod(%arg0: i8, %arg1: i8) -> i8 {
%v10 = arith.extui %arg0 : i8 to i32
%v11 = arith.extui %arg1 : i8 to i32
%v12 = arith.constant 0 : i32
%v13 = arith.cmpi eq, %v11, %v12 : i32
scf.if %v13 {
%v14 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v14) : (!llvm.ptr) -> ()
}
%v15 = arith.remui %v10, %v11 : i32
%v16 = arith.trunci %v15 : i32 to i8
func.return %v16 : i8
}
func.func @shifts(%arg0: i32) -> i32 {
%v17 = arith.constant 3 : i32
%v18 = arith.constant 32 : i32
%v19 = arith.cmpi uge, %v17, %v18 : i32
%v20 = arith.constant 0 : i32
%v21 = arith.cmpi slt, %arg0, %v20 : i32
%v22 = arith.ori %v19, %v21 : i1
scf.if %v22 {
%v23 = llvm.mlir.addressof @str_3 : !llvm.ptr
func.call @__flow_fault(%v23) : (!llvm.ptr) -> ()
}
%v24 = arith.shli %arg0, %v17 : i32
%v25 = arith.constant 1 : i32
%v26 = arith.constant 32 : i32
%v27 = arith.cmpi uge, %v25, %v26 : i32
scf.if %v27 {
%v28 = llvm.mlir.addressof @str_3 : !llvm.ptr
func.call @__flow_fault(%v28) : (!llvm.ptr) -> ()
}
%v29 = arith.shrsi %v24, %v25 : i32
%v30 = arith.constant 12 : i32
%v31 = arith.andi %arg0, %v30 : i32
%v32 = arith.xori %v29, %v31 : i32
%v33 = arith.constant 1 : i32
%v34 = arith.ori %v32, %v33 : i32
func.return %v34 : i32
}
func.func @ushift(%arg0: i32) -> i32 {
%v35 = arith.constant 4 : i32
%v36 = arith.constant 32 : i32
%v37 = arith.cmpi uge, %v35, %v36 : i32
scf.if %v37 {
%v38 = llvm.mlir.addressof @str_3 : !llvm.ptr
func.call @__flow_fault(%v38) : (!llvm.ptr) -> ()
}
%v39 = arith.shrui %arg0, %v35 : i32
func.return %v39 : i32
}
func.func @fmix(%arg0: f64, %arg1: f32) -> f64 {
%v40 = arith.constant 2.5 : f64
%v41 = arith.extf %arg1 : f32 to f64
%v42 = llvm.intr.fmuladd(%arg0, %v40, %v41) : (f64, f64, f64) -> f64
%v43 = arith.constant 0.25 : f64
%v44 = arith.subf %v42, %v43 : f64
func.return %v44 : f64
}
func.func @main() -> i32 {
%v45 = arith.constant 40 : i32
%v46 = arith.constant 3 : i32
%v47 = arith.constant 0 : i32
%v48 = arith.subi %v47, %v46 : i32
%v49 = arith.addi %v45, %v48 : i32
%v50 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v51 = llvm.call @printf(%v50, %v49) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v52 = arith.constant 0 : i32
%v53 = arith.constant 2 : i32
%v54 = arith.muli %v48, %v53 : i32
%v55 = arith.subi %v45, %v54 : i32
%v56 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v57 = llvm.call @printf(%v56, %v55) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v58 = arith.constant 0 : i32
%v59 = arith.constant 0 : i32
%v60 = arith.cmpi eq, %v48, %v59 : i32
scf.if %v60 {
%v61 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v61) : (!llvm.ptr) -> ()
}
%v62 = arith.divsi %v45, %v48 : i32
%v63 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v64 = llvm.call @printf(%v63, %v62) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v65 = arith.constant 0 : i32
%v66 = arith.constant 7 : i32
%v67 = arith.constant 0 : i32
%v68 = arith.cmpi eq, %v66, %v67 : i32
scf.if %v68 {
%v69 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v69) : (!llvm.ptr) -> ()
}
%v70 = arith.remsi %v45, %v66 : i32
%v71 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v72 = llvm.call @printf(%v71, %v70) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v73 = arith.constant 0 : i32
%v74 = arith.constant 100000 : i32
%v75 = arith.extsi %v74 : i32 to i64
%v76 = func.call @mix(%v45, %v75) : (i32, i64) -> i64
%v77 = llvm.mlir.addressof @str_5 : !llvm.ptr
%v78 = llvm.call @printf(%v77, %v76) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v79 = arith.constant 0 : i32
%v80 = arith.constant 4000000000 : i64
%v81 = arith.trunci %v80 : i64 to i32
%v82 = arith.constant 3 : i32
%v83 = func.call @udiv(%v81, %v82) : (i32, i32) -> i32
%v84 = arith.extui %v83 : i32 to i64
%v85 = llvm.mlir.addressof @str_5 : !llvm.ptr
%v86 = llvm.call @printf(%v85, %v84) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v87 = arith.constant 0 : i32
%v88 = arith.constant 250 : i32
%v89 = arith.trunci %v88 : i32 to i8
%v90 = arith.constant 7 : i32
%v91 = arith.trunci %v90 : i32 to i8
%v92 = func.call @umod(%v89, %v91) : (i8, i8) -> i8
%v93 = arith.extui %v92 : i8 to i32
%v94 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v95 = llvm.call @printf(%v94, %v93) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v96 = arith.constant 0 : i32
%v97 = arith.constant 9 : i32
%v98 = func.call @shifts(%v97) : (i32) -> i32
%v99 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v100 = llvm.call @printf(%v99, %v98) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v101 = arith.constant 0 : i32
%v102 = func.call @ushift(%v81) : (i32) -> i32
%v103 = arith.extui %v102 : i32 to i64
%v104 = llvm.mlir.addressof @str_5 : !llvm.ptr
%v105 = llvm.call @printf(%v104, %v103) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v106 = arith.constant 0 : i32
%v107 = arith.constant 300 : i32
%v108 = arith.trunci %v107 : i32 to i16
%v109 = arith.extsi %v108 : i16 to i64
%v110 = arith.constant 1000 : i32
%v111 = arith.extsi %v110 : i32 to i64
%v112 = arith.muli %v109, %v111 : i64
%v113 = llvm.mlir.addressof @str_5 : !llvm.ptr
%v114 = llvm.call @printf(%v113, %v112) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v115 = arith.constant 0 : i32
%v116 = arith.constant 1.5 : f64
%v117 = arith.constant 0.5 : f64
%v118 = arith.truncf %v117 : f64 to f32
%v119 = func.call @fmix(%v116, %v118) : (f64, f32) -> f64
%v120 = llvm.mlir.addressof @str_6 : !llvm.ptr
%v121 = llvm.call @printf(%v120, %v119) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v122 = arith.constant 0 : i32
%v123 = arith.constant 3.0 : f64
%v124 = arith.truncf %v123 : f64 to f32
%v125 = arith.constant 2.0 : f64
%v126 = arith.extf %v124 : f32 to f64
%v127 = arith.mulf %v126, %v125 : f64
%v128 = llvm.mlir.addressof @str_6 : !llvm.ptr
%v129 = llvm.call @printf(%v128, %v127) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v130 = arith.constant 0 : i32
%v131 = arith.fptosi %v119 : f64 to i32
%v132 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v133 = llvm.call @printf(%v132, %v131) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v134 = arith.constant 0 : i32
%v135 = arith.negf %v119 : f64
%v136 = llvm.mlir.addressof @str_6 : !llvm.ptr
%v137 = llvm.call @printf(%v136, %v135) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v138 = arith.constant 0 : i32
%v139 = arith.constant -1 : i32
%v140 = arith.xori %v45, %v139 : i32
%v141 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v142 = llvm.call @printf(%v141, %v140) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v143 = arith.constant 0 : i32
%v144 = arith.constant 3000000000 : i64
%v145 = arith.extui %v81 : i32 to i64
%v146 = arith.cmpi ugt, %v145, %v144 : i64
cf.cond_br %v146, ^b1, ^b2
^b1:
%v147 = llvm.mlir.addressof @str_7 : !llvm.ptr
%v148 = llvm.call @printf(%v147) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v149 = arith.constant 0 : i32
cf.br ^b3
^b2:
cf.br ^b3
^b3:
%v150 = arith.constant 0 : i32
func.return %v150 : i32
}
}
