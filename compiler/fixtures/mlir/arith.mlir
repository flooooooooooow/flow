module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_1("%lld\0A\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
llvm.mlir.global internal constant @str_2("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_3("unsigned compare\0A\00") {addr_space = 0 : i32} : !llvm.array<18 x i8>
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
%v22 = arith.constant 2.5 : f64
%v23 = arith.extf %arg1 : f32 to f64
%v24 = math.fma %arg0, %v22, %v23 : f64
%v25 = arith.constant 0.25 : f64
%v26 = arith.subf %v24, %v25 : f64
func.return %v26 : f64
}
func.func @main() -> i32 {
%v27 = arith.constant 40 : i32
%v28 = arith.constant 3 : i32
%v29 = arith.constant 0 : i32
%v30 = arith.subi %v29, %v28 : i32
%v31 = arith.addi %v27, %v30 : i32
%v32 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v33 = llvm.call @printf(%v32, %v31) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v34 = arith.constant 0 : i32
%v35 = arith.constant 2 : i32
%v36 = arith.muli %v30, %v35 : i32
%v37 = arith.subi %v27, %v36 : i32
%v38 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v39 = llvm.call @printf(%v38, %v37) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v40 = arith.constant 0 : i32
%v41 = arith.divsi %v27, %v30 : i32
%v42 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v43 = llvm.call @printf(%v42, %v41) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v44 = arith.constant 0 : i32
%v45 = arith.constant 7 : i32
%v46 = arith.remsi %v27, %v45 : i32
%v47 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v48 = llvm.call @printf(%v47, %v46) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v49 = arith.constant 0 : i32
%v50 = arith.constant 100000 : i32
%v51 = arith.extsi %v50 : i32 to i64
%v52 = func.call @mix(%v27, %v51) : (i32, i64) -> i64
%v53 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v54 = llvm.call @printf(%v53, %v52) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v55 = arith.constant 0 : i32
%v56 = arith.constant 4000000000 : i64
%v57 = arith.trunci %v56 : i64 to i32
%v58 = arith.constant 3 : i32
%v59 = func.call @udiv(%v57, %v58) : (i32, i32) -> i32
%v60 = arith.extui %v59 : i32 to i64
%v61 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v62 = llvm.call @printf(%v61, %v60) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v63 = arith.constant 0 : i32
%v64 = arith.constant 250 : i32
%v65 = arith.trunci %v64 : i32 to i8
%v66 = arith.constant 7 : i32
%v67 = arith.trunci %v66 : i32 to i8
%v68 = func.call @umod(%v65, %v67) : (i8, i8) -> i8
%v69 = arith.extui %v68 : i8 to i32
%v70 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v71 = llvm.call @printf(%v70, %v69) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v72 = arith.constant 0 : i32
%v73 = arith.constant 9 : i32
%v74 = func.call @shifts(%v73) : (i32) -> i32
%v75 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v76 = llvm.call @printf(%v75, %v74) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v77 = arith.constant 0 : i32
%v78 = func.call @ushift(%v57) : (i32) -> i32
%v79 = arith.extui %v78 : i32 to i64
%v80 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v81 = llvm.call @printf(%v80, %v79) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v82 = arith.constant 0 : i32
%v83 = arith.constant 300 : i32
%v84 = arith.trunci %v83 : i32 to i16
%v85 = arith.extsi %v84 : i16 to i64
%v86 = arith.constant 1000 : i32
%v87 = arith.extsi %v86 : i32 to i64
%v88 = arith.muli %v85, %v87 : i64
%v89 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v90 = llvm.call @printf(%v89, %v88) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v91 = arith.constant 0 : i32
%v92 = arith.constant 1.5 : f64
%v93 = arith.constant 0.5 : f64
%v94 = arith.truncf %v93 : f64 to f32
%v95 = func.call @fmix(%v92, %v94) : (f64, f32) -> f64
%v96 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v97 = llvm.call @printf(%v96, %v95) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v98 = arith.constant 0 : i32
%v99 = arith.constant 3.0 : f64
%v100 = arith.truncf %v99 : f64 to f32
%v101 = arith.constant 2.0 : f64
%v102 = arith.extf %v100 : f32 to f64
%v103 = arith.mulf %v102, %v101 : f64
%v104 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v105 = llvm.call @printf(%v104, %v103) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v106 = arith.constant 0 : i32
%v107 = arith.fptosi %v95 : f64 to i32
%v108 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v109 = llvm.call @printf(%v108, %v107) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v110 = arith.constant 0 : i32
%v111 = arith.negf %v95 : f64
%v112 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v113 = llvm.call @printf(%v112, %v111) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v114 = arith.constant 0 : i32
%v115 = arith.constant -1 : i32
%v116 = arith.xori %v27, %v115 : i32
%v117 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v118 = llvm.call @printf(%v117, %v116) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v119 = arith.constant 0 : i32
%v120 = arith.constant 3000000000 : i64
%v121 = arith.extui %v57 : i32 to i64
%v122 = arith.cmpi ugt, %v121, %v120 : i64
cf.cond_br %v122, ^b1, ^b2
^b1:
%v123 = llvm.mlir.addressof @str_3 : !llvm.ptr
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
