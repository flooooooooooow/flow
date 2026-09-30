module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\n\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_1("%f\n\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_2("unsigned compare\n\00") {addr_space = 0 : i32} : !llvm.array<18 x i8>
func.func @mix(%arg0: i32, %arg1: i64) -> i64 {
%v1 = arith.extsi %arg0 : i32 to i64
%v2 = arith.muli %v1, %arg1 : i64
%v3 = arith.constant 7 : i32
%v4 = arith.extsi %v3 : i32 to i64
%v5 = arith.addi %v2, %v4 : i64
func.return %v5 : i64
}
func.func @udiv(%arg0: i32, %arg1: i32) -> i32 {
%v6 = arith.divui %arg0, %arg1 : i32
func.return %v6 : i32
}
func.func @umod(%arg0: i8, %arg1: i8) -> i8 {
%v7 = arith.extui %arg0 : i8 to i32
%v8 = arith.extui %arg1 : i8 to i32
%v9 = arith.remui %v7, %v8 : i32
%v10 = arith.trunci %v9 : i32 to i8
func.return %v10 : i8
}
func.func @shifts(%arg0: i32) -> i32 {
%v11 = arith.constant 3 : i32
%v12 = arith.shli %arg0, %v11 : i32
%v13 = arith.constant 1 : i32
%v14 = arith.shrsi %v12, %v13 : i32
%v15 = arith.constant 12 : i32
%v16 = arith.andi %arg0, %v15 : i32
%v17 = arith.xori %v14, %v16 : i32
%v18 = arith.constant 1 : i32
%v19 = arith.ori %v17, %v18 : i32
func.return %v19 : i32
}
func.func @ushift(%arg0: i32) -> i32 {
%v20 = arith.constant 4 : i32
%v21 = arith.shrui %arg0, %v20 : i32
func.return %v21 : i32
}
func.func @fmix(%arg0: f64, %arg1: f32) -> f64 {
%v22 = arith.constant 2.5 : f32
%v23 = arith.extf %v22 : f32 to f64
%v24 = arith.mulf %arg0, %v23 : f64
%v25 = arith.extf %arg1 : f32 to f64
%v26 = arith.addf %v24, %v25 : f64
%v27 = arith.constant 0.25 : f32
%v28 = arith.extf %v27 : f32 to f64
%v29 = arith.subf %v26, %v28 : f64
func.return %v29 : f64
}
func.func @main() -> i32 {
%v30 = arith.constant 40 : i32
%v31 = arith.constant 3 : i32
%v32 = arith.constant 0 : i32
%v33 = arith.subi %v32, %v31 : i32
%v34 = arith.addi %v30, %v33 : i32
%v35 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v36 = llvm.call @printf(%v35, %v34) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v37 = arith.constant 0 : i32
%v38 = arith.constant 2 : i32
%v39 = arith.muli %v33, %v38 : i32
%v40 = arith.subi %v30, %v39 : i32
%v41 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v42 = llvm.call @printf(%v41, %v40) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v43 = arith.constant 0 : i32
%v44 = arith.divsi %v30, %v33 : i32
%v45 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v46 = llvm.call @printf(%v45, %v44) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v47 = arith.constant 0 : i32
%v48 = arith.constant 7 : i32
%v49 = arith.remsi %v30, %v48 : i32
%v50 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v51 = llvm.call @printf(%v50, %v49) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v52 = arith.constant 0 : i32
%v53 = arith.constant 100000 : i32
%v54 = arith.extsi %v53 : i32 to i64
%v55 = func.call @mix(%v30, %v54) : (i32, i64) -> i64
%v56 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v57 = llvm.call @printf(%v56, %v55) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v58 = arith.constant 0 : i32
%v59 = arith.constant -294967296 : i32
%v60 = arith.constant 3 : i32
%v61 = func.call @udiv(%v59, %v60) : (i32, i32) -> i32
%v62 = arith.extui %v61 : i32 to i64
%v63 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v64 = llvm.call @printf(%v63, %v62) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v65 = arith.constant 0 : i32
%v66 = arith.constant 250 : i32
%v67 = arith.trunci %v66 : i32 to i8
%v68 = arith.constant 7 : i32
%v69 = arith.trunci %v68 : i32 to i8
%v70 = func.call @umod(%v67, %v69) : (i8, i8) -> i8
%v71 = arith.extui %v70 : i8 to i32
%v72 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v73 = llvm.call @printf(%v72, %v71) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v74 = arith.constant 0 : i32
%v75 = arith.constant 9 : i32
%v76 = func.call @shifts(%v75) : (i32) -> i32
%v77 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v78 = llvm.call @printf(%v77, %v76) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v79 = arith.constant 0 : i32
%v80 = func.call @ushift(%v59) : (i32) -> i32
%v81 = arith.extui %v80 : i32 to i64
%v82 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v83 = llvm.call @printf(%v82, %v81) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v84 = arith.constant 0 : i32
%v85 = arith.constant 300 : i32
%v86 = arith.trunci %v85 : i32 to i16
%v87 = arith.extsi %v86 : i16 to i64
%v88 = arith.constant 1000 : i32
%v89 = arith.extsi %v88 : i32 to i64
%v90 = arith.muli %v87, %v89 : i64
%v91 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v92 = llvm.call @printf(%v91, %v90) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v93 = arith.constant 0 : i32
%v94 = arith.constant 1.5 : f32
%v95 = arith.constant 0.5 : f32
%v96 = arith.extf %v94 : f32 to f64
%v97 = func.call @fmix(%v96, %v95) : (f64, f32) -> f64
%v98 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v99 = llvm.call @printf(%v98, %v97) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v100 = arith.constant 0 : i32
%v101 = arith.constant 3.0 : f32
%v102 = arith.constant 2.0 : f32
%v103 = arith.mulf %v101, %v102 : f32
%v104 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v105 = arith.extf %v103 : f32 to f64
%v106 = llvm.call @printf(%v104, %v105) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v107 = arith.constant 0 : i32
%v108 = arith.fptosi %v97 : f64 to i32
%v109 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v110 = llvm.call @printf(%v109, %v108) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v111 = arith.constant 0 : i32
%v112 = arith.negf %v97 : f64
%v113 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v114 = llvm.call @printf(%v113, %v112) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v115 = arith.constant 0 : i32
%v116 = arith.constant -1 : i32
%v117 = arith.xori %v30, %v116 : i32
%v118 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v119 = llvm.call @printf(%v118, %v117) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v120 = arith.constant 0 : i32
%v121 = arith.constant -1294967296 : i32
%v122 = arith.cmpi ugt, %v59, %v121 : i32
cf.cond_br %v122, ^b1, ^b2
^b1:
%v123 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v124 = llvm.call @printf(%v123) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v125 = arith.constant 0 : i32
cf.br ^b3
^b2:
cf.br ^b3
^b3:
%v126 = arith.constant 0 : i32
func.return %v126 : i32
}
}
