module {
func.func private @malloc(i64) -> !llvm.ptr
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("note %d\0A\00") {addr_space = 0 : i32} : !llvm.array<9 x i8>
llvm.mlir.global internal constant @str_1("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_2("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
func.func @__flow_callback_square(%env: !llvm.ptr, %arg1: i32) -> i32 {
%result = func.call @square(%arg1) : (i32) -> i32
func.return %result : i32
}
func.func private @lambda_1(%env: !llvm.ptr, %arg0: i32) -> i32 {
%v1 = arith.constant 2 : i32
%v2 = arith.muli %arg0, %v1 : i32
func.return %v2 : i32
}
func.func private @lambda_2(%env: !llvm.ptr, %arg0: i32) -> i32 {
%v3 = llvm.getelementptr %env[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32)>
%v4 = llvm.load %v3 : !llvm.ptr -> i32
%v5 = llvm.load %v3 : !llvm.ptr -> i32
%v6 = arith.addi %arg0, %v5 : i32
%v7 = llvm.mlir.addressof @BIAS : !llvm.ptr
%v8 = llvm.load %v7 : !llvm.ptr -> i32
%v9 = arith.addi %v6, %v8 : i32
func.return %v9 : i32
}
func.func private @lambda_3(%env: !llvm.ptr, %arg0: i32) -> i32 {
%v10 = llvm.getelementptr %env[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.struct<(!llvm.ptr, !llvm.ptr)>)>
%v11 = llvm.load %v10 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v12 = llvm.getelementptr %env[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.struct<(!llvm.ptr, !llvm.ptr)>)>
%v13 = llvm.load %v12 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v14 = llvm.load %v12 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v15 = llvm.extractvalue %v14[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v16 = llvm.extractvalue %v14[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v17 = llvm.call %v15(%v16, %arg0) : !llvm.ptr, (!llvm.ptr, i32) -> i32
%v18 = llvm.load %v10 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v19 = llvm.extractvalue %v18[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v20 = llvm.extractvalue %v18[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v21 = llvm.call %v19(%v20, %v17) : !llvm.ptr, (!llvm.ptr, i32) -> i32
func.return %v21 : i32
}
func.func private @lambda_4(%env: !llvm.ptr, %arg0: f64, %arg1: f64) -> f64 {
%v22 = arith.constant 0.5 : f64
%v23 = llvm.intr.fmuladd(%arg1, %v22, %arg0) : (f64, f64, f64) -> f64
func.return %v23 : f64
}
// Constant: BIAS
llvm.mlir.global internal constant @BIAS(1 : i32) : i32
func.func @apply(%arg0: !llvm.struct<(!llvm.ptr, !llvm.ptr)>, %arg1: i32) -> i32 {
%v24 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v25 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v26 = llvm.insertvalue %v25, %v24[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v27 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v28 = llvm.insertvalue %v27, %v26[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v29 = llvm.mlir.constant(1 : i64) : i64
%v30 = llvm.alloca %v29 x !llvm.struct<(!llvm.ptr, !llvm.ptr)> : (i64) -> !llvm.ptr
llvm.store %v28, %v30 : !llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.ptr
%v31 = llvm.load %v30 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v32 = llvm.extractvalue %v31[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v33 = llvm.extractvalue %v31[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v34 = llvm.call %v32(%v33, %arg1) : !llvm.ptr, (!llvm.ptr, i32) -> i32
func.return %v34 : i32
}
func.func @twice(%arg0: !llvm.struct<(!llvm.ptr, !llvm.ptr)>, %arg1: i32) -> i32 {
%v35 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v36 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v37 = llvm.insertvalue %v36, %v35[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v38 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v39 = llvm.insertvalue %v38, %v37[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v40 = llvm.mlir.constant(1 : i64) : i64
%v41 = llvm.alloca %v40 x !llvm.struct<(!llvm.ptr, !llvm.ptr)> : (i64) -> !llvm.ptr
llvm.store %v39, %v41 : !llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.ptr
%v42 = llvm.load %v41 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v43 = llvm.mlir.constant(1 : i64) : i64
%v44 = llvm.alloca %v43 x !llvm.struct<(!llvm.ptr, !llvm.ptr)> : (i64) -> !llvm.ptr
llvm.store %v42, %v44 : !llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.ptr
%v45 = llvm.load %v44 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v46 = llvm.extractvalue %v45[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v47 = llvm.extractvalue %v45[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v48 = llvm.load %v44 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v49 = llvm.extractvalue %v48[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v50 = llvm.extractvalue %v48[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v51 = llvm.call %v49(%v50, %arg1) : !llvm.ptr, (!llvm.ptr, i32) -> i32
%v52 = llvm.call %v46(%v47, %v51) : !llvm.ptr, (!llvm.ptr, i32) -> i32
func.return %v52 : i32
}
func.func @square(%arg0: i32) -> i32 {
%v53 = arith.muli %arg0, %arg0 : i32
func.return %v53 : i32
}
func.func @fold(%arg0: !llvm.struct<(!llvm.ptr, !llvm.ptr)>, %arg1: i32) -> f64 {
%v54 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v55 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v56 = llvm.insertvalue %v55, %v54[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v57 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v58 = llvm.insertvalue %v57, %v56[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v59 = llvm.mlir.constant(1 : i64) : i64
%v60 = llvm.alloca %v59 x !llvm.struct<(!llvm.ptr, !llvm.ptr)> : (i64) -> !llvm.ptr
llvm.store %v58, %v60 : !llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.ptr
%v61 = arith.constant 0.0 : f64
%v62 = llvm.mlir.constant(1 : i64) : i64
%v63 = llvm.alloca %v62 x f64 : (i64) -> !llvm.ptr
llvm.store %v61, %v63 : f64, !llvm.ptr
%v64 = arith.constant 0 : i32
%v65 = arith.index_cast %v64 : i32 to index
%v66 = arith.index_cast %arg1 : i32 to index
%v67 = arith.constant 1 : index
%v68 = arith.constant -1 : index
%v69 = arith.cmpi sle, %v65, %v66 : index
%v70 = arith.select %v69, %v67, %v68 : index
cf.br ^b1(%v65 : index)
^b1(%v71: index):
%v72 = arith.cmpi slt, %v71, %v66 : index
%v73 = arith.cmpi sgt, %v71, %v66 : index
%v74 = arith.select %v69, %v72, %v73 : i1
cf.cond_br %v74, ^b2(%v71 : index), ^b3(%v71 : index)
^b2(%v75: index):
%v76 = llvm.load %v60 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v77 = llvm.extractvalue %v76[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v78 = llvm.extractvalue %v76[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v79 = llvm.load %v63 : !llvm.ptr -> f64
%v80 = arith.index_cast %v75 : index to i64
%v81 = arith.sitofp %v80 : i64 to f64
%v82 = llvm.call %v77(%v78, %v79, %v81) : !llvm.ptr, (!llvm.ptr, f64, f64) -> f64
llvm.store %v82, %v63 : f64, !llvm.ptr
%v83 = arith.addi %v75, %v70 : index
cf.br ^b1(%v83 : index)
^b3(%v84: index):
%v85 = llvm.load %v63 : !llvm.ptr -> f64
func.return %v85 : f64
}
func.func @note(%arg0: i32) -> () {
%v86 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v87 = llvm.call @printf(%v86, %arg0) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
func.return
}
func.func @main() -> i32 {
%v88 = llvm.mlir.zero : !llvm.ptr
%v89 = func.constant @lambda_1 : (!llvm.ptr, i32) -> i32
%v90 = builtin.unrealized_conversion_cast %v89 : (!llvm.ptr, i32) -> i32 to !llvm.ptr
%v91 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v92 = llvm.insertvalue %v90, %v91[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v93 = llvm.insertvalue %v88, %v92[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v94 = arith.constant 10 : i32
%v95 = llvm.mlir.constant(1 : i64) : i64
%v96 = llvm.alloca %v95 x i32 : (i64) -> !llvm.ptr
llvm.store %v94, %v96 : i32, !llvm.ptr
%v97 = llvm.mlir.zero : !llvm.ptr
%v98 = llvm.getelementptr %v97[1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32)>
%v99 = llvm.ptrtoint %v98 : !llvm.ptr to i64
%v100 = func.call @malloc(%v99) : (i64) -> !llvm.ptr
%v101 = llvm.load %v96 : !llvm.ptr -> i32
%v102 = llvm.getelementptr %v100[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32)>
llvm.store %v101, %v102 : i32, !llvm.ptr
%v103 = func.constant @lambda_2 : (!llvm.ptr, i32) -> i32
%v104 = builtin.unrealized_conversion_cast %v103 : (!llvm.ptr, i32) -> i32 to !llvm.ptr
%v105 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v106 = llvm.insertvalue %v104, %v105[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v107 = llvm.insertvalue %v100, %v106[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v108 = arith.constant 100 : i32
llvm.store %v108, %v96 : i32, !llvm.ptr
%v109 = llvm.mlir.zero : !llvm.ptr
%v110 = llvm.getelementptr %v109[1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.struct<(!llvm.ptr, !llvm.ptr)>)>
%v111 = llvm.ptrtoint %v110 : !llvm.ptr to i64
%v112 = func.call @malloc(%v111) : (i64) -> !llvm.ptr
%v113 = llvm.getelementptr %v112[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.struct<(!llvm.ptr, !llvm.ptr)>)>
llvm.store %v107, %v113 : !llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.ptr
%v114 = llvm.getelementptr %v112[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.struct<(!llvm.ptr, !llvm.ptr)>)>
llvm.store %v93, %v114 : !llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.ptr
%v115 = func.constant @lambda_3 : (!llvm.ptr, i32) -> i32
%v116 = builtin.unrealized_conversion_cast %v115 : (!llvm.ptr, i32) -> i32 to !llvm.ptr
%v117 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v118 = llvm.insertvalue %v116, %v117[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v119 = llvm.insertvalue %v112, %v118[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v120 = llvm.mlir.zero : !llvm.ptr
%v121 = func.constant @lambda_4 : (!llvm.ptr, f64, f64) -> f64
%v122 = builtin.unrealized_conversion_cast %v121 : (!llvm.ptr, f64, f64) -> f64 to !llvm.ptr
%v123 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v124 = llvm.insertvalue %v122, %v123[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v125 = llvm.insertvalue %v120, %v124[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v126 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v127 = arith.constant 21 : i32
%v128 = func.call @apply(%v93, %v127) : (!llvm.struct<(!llvm.ptr, !llvm.ptr)>, i32) -> i32
%v129 = llvm.call @printf(%v126, %v128) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v130 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v131 = arith.constant 5 : i32
%v132 = func.call @apply(%v107, %v131) : (!llvm.struct<(!llvm.ptr, !llvm.ptr)>, i32) -> i32
%v133 = llvm.call @printf(%v130, %v132) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v134 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v135 = llvm.extractvalue %v119[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v136 = llvm.extractvalue %v119[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v137 = arith.constant 4 : i32
%v138 = llvm.call %v135(%v136, %v137) : !llvm.ptr, (!llvm.ptr, i32) -> i32
%v139 = llvm.call @printf(%v134, %v138) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v140 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v141 = arith.constant 3 : i32
%v142 = func.call @twice(%v93, %v141) : (!llvm.struct<(!llvm.ptr, !llvm.ptr)>, i32) -> i32
%v143 = llvm.call @printf(%v140, %v142) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v144 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v145 = func.constant @__flow_callback_square : (!llvm.ptr, i32) -> i32
%v146 = builtin.unrealized_conversion_cast %v145 : (!llvm.ptr, i32) -> i32 to !llvm.ptr
%v147 = llvm.mlir.zero : !llvm.ptr
%v148 = llvm.mlir.zero : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v149 = llvm.insertvalue %v146, %v148[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v150 = llvm.insertvalue %v147, %v149[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v151 = arith.constant 7 : i32
%v152 = func.call @apply(%v150, %v151) : (!llvm.struct<(!llvm.ptr, !llvm.ptr)>, i32) -> i32
%v153 = llvm.call @printf(%v144, %v152) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v154 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v155 = arith.constant 5 : i32
%v156 = func.call @fold(%v125, %v155) : (!llvm.struct<(!llvm.ptr, !llvm.ptr)>, i32) -> f64
%v157 = llvm.call @printf(%v154, %v156) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v158 = arith.constant 3 : i32
func.call @note(%v158) : (i32) -> ()
%v159 = arith.constant 0 : i32
func.return %v159 : i32
}
}
