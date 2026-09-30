module {
llvm.func @malloc(i64) -> !llvm.ptr
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("note %d\n\00") {addr_space = 0 : i32} : !llvm.array<9 x i8>
llvm.mlir.global internal constant @str_1("%d\n\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_2("%f\n\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
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
%v3 = llvm.getelementptr %env[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v4 = llvm.load %v3 : !llvm.ptr -> i32
%v5 = llvm.getelementptr %env[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v6 = llvm.load %v5 : !llvm.ptr -> i32
%v7 = llvm.load %v5 : !llvm.ptr -> i32
%v8 = arith.addi %arg0, %v7 : i32
%v9 = llvm.load %v3 : !llvm.ptr -> i32
%v10 = arith.addi %v8, %v9 : i32
func.return %v10 : i32
}
func.func private @lambda_3(%env: !llvm.ptr, %arg0: i32) -> i32 {
%v11 = llvm.getelementptr %env[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.struct<(!llvm.ptr, !llvm.ptr)>)>
%v12 = llvm.load %v11 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v13 = llvm.getelementptr %env[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.struct<(!llvm.ptr, !llvm.ptr)>)>
%v14 = llvm.load %v13 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v15 = llvm.load %v13 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v16 = llvm.extractvalue %v15[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v17 = llvm.extractvalue %v15[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v18 = llvm.call %v16(%v17, %arg0) : !llvm.ptr, (!llvm.ptr, i32) -> i32
%v19 = llvm.load %v11 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v20 = llvm.extractvalue %v19[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v21 = llvm.extractvalue %v19[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v22 = llvm.call %v20(%v21, %v18) : !llvm.ptr, (!llvm.ptr, i32) -> i32
func.return %v22 : i32
}
func.func private @lambda_4(%env: !llvm.ptr, %arg0: f64, %arg1: f64) -> f64 {
%v23 = arith.constant 0.5 : f32
%v24 = arith.extf %v23 : f32 to f64
%v25 = arith.mulf %arg1, %v24 : f64
%v26 = arith.addf %arg0, %v25 : f64
func.return %v26 : f64
}
// Constant: BIAS
llvm.mlir.global internal constant @BIAS(1 : i32) : i32
func.func @apply(%arg0: !llvm.struct<(!llvm.ptr, !llvm.ptr)>, %arg1: i32) -> i32 {
%v27 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v28 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v29 = llvm.insertvalue %v28, %v27[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v30 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v31 = llvm.insertvalue %v30, %v29[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v32 = llvm.mlir.constant(1 : i64) : i64
%v33 = llvm.alloca %v32 x !llvm.struct<(!llvm.ptr, !llvm.ptr)> : (i64) -> !llvm.ptr
llvm.store %v31, %v33 : !llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.ptr
%v34 = llvm.load %v33 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v35 = llvm.extractvalue %v34[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v36 = llvm.extractvalue %v34[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v37 = llvm.call %v35(%v36, %arg1) : !llvm.ptr, (!llvm.ptr, i32) -> i32
func.return %v37 : i32
}
func.func @twice(%arg0: !llvm.struct<(!llvm.ptr, !llvm.ptr)>, %arg1: i32) -> i32 {
%v38 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v39 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v40 = llvm.insertvalue %v39, %v38[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v41 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v42 = llvm.insertvalue %v41, %v40[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v43 = llvm.mlir.constant(1 : i64) : i64
%v44 = llvm.alloca %v43 x !llvm.struct<(!llvm.ptr, !llvm.ptr)> : (i64) -> !llvm.ptr
llvm.store %v42, %v44 : !llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.ptr
%v45 = llvm.load %v44 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v46 = llvm.mlir.constant(1 : i64) : i64
%v47 = llvm.alloca %v46 x !llvm.struct<(!llvm.ptr, !llvm.ptr)> : (i64) -> !llvm.ptr
llvm.store %v45, %v47 : !llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.ptr
%v48 = llvm.load %v47 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v49 = llvm.extractvalue %v48[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v50 = llvm.extractvalue %v48[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v51 = llvm.load %v47 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v52 = llvm.extractvalue %v51[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v53 = llvm.extractvalue %v51[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v54 = llvm.call %v52(%v53, %arg1) : !llvm.ptr, (!llvm.ptr, i32) -> i32
%v55 = llvm.call %v49(%v50, %v54) : !llvm.ptr, (!llvm.ptr, i32) -> i32
func.return %v55 : i32
}
func.func @square(%arg0: i32) -> i32 {
%v56 = arith.muli %arg0, %arg0 : i32
func.return %v56 : i32
}
func.func @fold(%arg0: !llvm.struct<(!llvm.ptr, !llvm.ptr)>, %arg1: i32) -> f64 {
%v57 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v58 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v59 = llvm.insertvalue %v58, %v57[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v60 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v61 = llvm.insertvalue %v60, %v59[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v62 = llvm.mlir.constant(1 : i64) : i64
%v63 = llvm.alloca %v62 x !llvm.struct<(!llvm.ptr, !llvm.ptr)> : (i64) -> !llvm.ptr
llvm.store %v61, %v63 : !llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.ptr
%v64 = arith.constant 0.0 : f32
%v65 = arith.extf %v64 : f32 to f64
%v66 = llvm.mlir.constant(1 : i64) : i64
%v67 = llvm.alloca %v66 x f64 : (i64) -> !llvm.ptr
llvm.store %v65, %v67 : f64, !llvm.ptr
%v68 = arith.constant 0 : i32
%v69 = arith.index_cast %v68 : i32 to index
%v70 = arith.index_cast %arg1 : i32 to index
%v71 = arith.constant 1 : index
%v72 = arith.constant -1 : index
%v73 = arith.cmpi sle, %v69, %v70 : index
%v74 = arith.select %v73, %v71, %v72 : index
cf.br ^b1(%v69 : index)
^b1(%v75: index):
%v76 = arith.cmpi slt, %v75, %v70 : index
%v77 = arith.cmpi sgt, %v75, %v70 : index
%v78 = arith.select %v73, %v76, %v77 : i1
cf.cond_br %v78, ^b2(%v75 : index), ^b3(%v75 : index)
^b2(%v79: index):
%v80 = llvm.load %v63 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v81 = llvm.extractvalue %v80[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v82 = llvm.extractvalue %v80[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v83 = llvm.load %v67 : !llvm.ptr -> f64
%v84 = arith.index_cast %v79 : index to i64
%v85 = arith.sitofp %v84 : i64 to f64
%v86 = llvm.call %v81(%v82, %v83, %v85) : !llvm.ptr, (!llvm.ptr, f64, f64) -> f64
llvm.store %v86, %v67 : f64, !llvm.ptr
%v87 = arith.addi %v79, %v74 : index
cf.br ^b1(%v87 : index)
^b3(%v88: index):
%v89 = llvm.load %v67 : !llvm.ptr -> f64
func.return %v89 : f64
}
func.func @note(%arg0: i32) -> () {
%v90 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v91 = llvm.call @printf(%v90, %arg0) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
func.return
}
func.func @main() -> i32 {
%v92 = llvm.mlir.zero : !llvm.ptr
%v93 = func.constant @lambda_1 : (!llvm.ptr, i32) -> i32
%v94 = builtin.unrealized_conversion_cast %v93 : (!llvm.ptr, i32) -> i32 to !llvm.ptr
%v95 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v96 = llvm.insertvalue %v94, %v95[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v97 = llvm.insertvalue %v92, %v96[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v98 = arith.constant 10 : i32
%v99 = llvm.mlir.constant(1 : i64) : i64
%v100 = llvm.alloca %v99 x i32 : (i64) -> !llvm.ptr
llvm.store %v98, %v100 : i32, !llvm.ptr
%v101 = llvm.mlir.zero : !llvm.ptr
%v102 = llvm.getelementptr %v101[1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v103 = llvm.ptrtoint %v102 : !llvm.ptr to i64
%v104 = llvm.call @malloc(%v103) : (i64) -> !llvm.ptr
%v105 = llvm.mlir.addressof @BIAS : !llvm.ptr
%v106 = llvm.load %v105 : !llvm.ptr -> i32
%v107 = llvm.getelementptr %v104[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
llvm.store %v106, %v107 : i32, !llvm.ptr
%v108 = llvm.load %v100 : !llvm.ptr -> i32
%v109 = llvm.getelementptr %v104[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
llvm.store %v108, %v109 : i32, !llvm.ptr
%v110 = func.constant @lambda_2 : (!llvm.ptr, i32) -> i32
%v111 = builtin.unrealized_conversion_cast %v110 : (!llvm.ptr, i32) -> i32 to !llvm.ptr
%v112 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v113 = llvm.insertvalue %v111, %v112[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v114 = llvm.insertvalue %v104, %v113[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v115 = arith.constant 100 : i32
llvm.store %v115, %v100 : i32, !llvm.ptr
%v116 = llvm.mlir.zero : !llvm.ptr
%v117 = llvm.getelementptr %v116[1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.struct<(!llvm.ptr, !llvm.ptr)>)>
%v118 = llvm.ptrtoint %v117 : !llvm.ptr to i64
%v119 = llvm.call @malloc(%v118) : (i64) -> !llvm.ptr
%v120 = llvm.getelementptr %v119[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.struct<(!llvm.ptr, !llvm.ptr)>)>
llvm.store %v114, %v120 : !llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.ptr
%v121 = llvm.getelementptr %v119[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.struct<(!llvm.ptr, !llvm.ptr)>)>
llvm.store %v97, %v121 : !llvm.struct<(!llvm.ptr, !llvm.ptr)>, !llvm.ptr
%v122 = func.constant @lambda_3 : (!llvm.ptr, i32) -> i32
%v123 = builtin.unrealized_conversion_cast %v122 : (!llvm.ptr, i32) -> i32 to !llvm.ptr
%v124 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v125 = llvm.insertvalue %v123, %v124[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v126 = llvm.insertvalue %v119, %v125[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v127 = llvm.mlir.zero : !llvm.ptr
%v128 = func.constant @lambda_4 : (!llvm.ptr, f64, f64) -> f64
%v129 = builtin.unrealized_conversion_cast %v128 : (!llvm.ptr, f64, f64) -> f64 to !llvm.ptr
%v130 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v131 = llvm.insertvalue %v129, %v130[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v132 = llvm.insertvalue %v127, %v131[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v133 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v134 = arith.constant 21 : i32
%v135 = func.call @apply(%v97, %v134) : (!llvm.struct<(!llvm.ptr, !llvm.ptr)>, i32) -> i32
%v136 = llvm.call @printf(%v133, %v135) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v137 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v138 = arith.constant 5 : i32
%v139 = func.call @apply(%v114, %v138) : (!llvm.struct<(!llvm.ptr, !llvm.ptr)>, i32) -> i32
%v140 = llvm.call @printf(%v137, %v139) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v141 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v142 = llvm.extractvalue %v126[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v143 = llvm.extractvalue %v126[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v144 = arith.constant 4 : i32
%v145 = llvm.call %v142(%v143, %v144) : !llvm.ptr, (!llvm.ptr, i32) -> i32
%v146 = llvm.call @printf(%v141, %v145) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v147 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v148 = arith.constant 3 : i32
%v149 = func.call @twice(%v97, %v148) : (!llvm.struct<(!llvm.ptr, !llvm.ptr)>, i32) -> i32
%v150 = llvm.call @printf(%v147, %v149) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v151 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v152 = func.constant @__flow_callback_square : (!llvm.ptr, i32) -> i32
%v153 = builtin.unrealized_conversion_cast %v152 : (!llvm.ptr, i32) -> i32 to !llvm.ptr
%v154 = llvm.mlir.zero : !llvm.ptr
%v155 = llvm.mlir.zero : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v156 = llvm.insertvalue %v153, %v155[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v157 = llvm.insertvalue %v154, %v156[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v158 = arith.constant 7 : i32
%v159 = func.call @apply(%v157, %v158) : (!llvm.struct<(!llvm.ptr, !llvm.ptr)>, i32) -> i32
%v160 = llvm.call @printf(%v151, %v159) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v161 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v162 = arith.constant 5 : i32
%v163 = func.call @fold(%v132, %v162) : (!llvm.struct<(!llvm.ptr, !llvm.ptr)>, i32) -> f64
%v164 = llvm.call @printf(%v161, %v163) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v165 = arith.constant 3 : i32
func.call @note(%v165) : (i32) -> ()
%v166 = arith.constant 0 : i32
func.return %v166 : i32
}
}
