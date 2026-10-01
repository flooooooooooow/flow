module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @Shape_Circle(0 : i32) : i32
llvm.mlir.global internal constant @Shape_Square(1 : i32) : i32
llvm.mlir.global internal constant @Shape_Line(2 : i32) : i32
// Struct: Pair
// Fields:
//   a: i32
//   b: i32
// Enum: Shape (lowered as tagged struct + variant constants)
func.func @classify(%arg0: i32) -> i32 {
%v1 = arith.constant 0 : i32
%v2 = arith.cmpi eq, %arg0, %v1 : i32
cf.cond_br %v2, ^b1, ^b2
^b1:
%v3 = arith.constant 10 : i32
func.return %v3 : i32
^b2:
%v4 = arith.constant 1 : i32
%v5 = arith.constant 0 : i32
%v6 = arith.subi %v5, %v4 : i32
%v7 = arith.cmpi eq, %arg0, %v6 : i32
cf.cond_br %v7, ^b3, ^b4
^b3:
%v8 = arith.constant 11 : i32
func.return %v8 : i32
^b4:
%v9 = arith.constant 1 : i32
%v10 = arith.cmpi eq, %arg0, %v9 : i32
cf.cond_br %v10, ^b5, ^b6
^b5:
%v11 = arith.constant 12 : i32
func.return %v11 : i32
^b6:
%v12 = arith.constant 2 : i32
%v13 = arith.cmpi eq, %arg0, %v12 : i32
cf.cond_br %v13, ^b7, ^b8
^b7:
%v14 = arith.constant 12 : i32
func.return %v14 : i32
^b8:
%v15 = arith.constant 3 : i32
%v16 = arith.cmpi eq, %arg0, %v15 : i32
cf.cond_br %v16, ^b9, ^b10
^b9:
%v17 = arith.constant 12 : i32
func.return %v17 : i32
^b10:
%v18 = arith.constant 1 : i1
%v19 = arith.constant 100 : i32
%v20 = arith.cmpi sgt, %arg0, %v19 : i32
%v21 = arith.andi %v18, %v20 : i1
cf.cond_br %v21, ^b11, ^b12
^b11:
%v22 = arith.constant 13 : i32
func.return %v22 : i32
^b12:
%v23 = arith.constant 14 : i32
func.return %v23 : i32
^b13:
llvm.unreachable
}
func.func @truth(%arg0: i1) -> i32 {
%v24 = arith.constant 1 : i1
%v25 = arith.cmpi eq, %arg0, %v24 : i1
cf.cond_br %v25, ^b14, ^b15
^b14:
%v26 = arith.constant 1 : i32
func.return %v26 : i32
^b15:
%v27 = arith.constant 0 : i1
%v28 = arith.cmpi eq, %arg0, %v27 : i1
cf.cond_br %v28, ^b16, ^b17
^b16:
%v29 = arith.constant 0 : i32
func.return %v29 : i32
^b17:
cf.br ^b18
^b18:
%v30 = arith.constant 7 : i32
func.return %v30 : i32
}
func.func @pair_sum(%arg0: !llvm.struct<(i32, i32)>) -> i32 {
%v31 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v32 = llvm.extractvalue %arg0[0] : !llvm.struct<(i32, i32)>
%v33 = llvm.insertvalue %v32, %v31[0] : !llvm.struct<(i32, i32)>
%v34 = llvm.extractvalue %arg0[1] : !llvm.struct<(i32, i32)>
%v35 = llvm.insertvalue %v34, %v33[1] : !llvm.struct<(i32, i32)>
%v36 = llvm.mlir.constant(1 : i64) : i64
%v37 = llvm.alloca %v36 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v35, %v37 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v38 = arith.constant 0 : i32
%v39 = llvm.mlir.constant(1 : i64) : i64
%v40 = llvm.alloca %v39 x i32 : (i64) -> !llvm.ptr
llvm.store %v38, %v40 : i32, !llvm.ptr
%v41 = llvm.load %v37 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v42 = arith.constant 1 : i1
%v43 = llvm.extractvalue %v41[0] : !llvm.struct<(i32, i32)>
%v44 = llvm.extractvalue %v41[1] : !llvm.struct<(i32, i32)>
cf.cond_br %v42, ^b19, ^b20
^b19:
%v45 = arith.addi %v43, %v44 : i32
llvm.store %v45, %v40 : i32, !llvm.ptr
cf.br ^b21
^b20:
cf.br ^b21
^b21:
%v46 = llvm.load %v40 : !llvm.ptr -> i32
func.return %v46 : i32
}
func.func @shape_code(%arg0: !llvm.struct<(i32, i32)>) -> i32 {
%v47 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v48 = llvm.extractvalue %arg0[0] : !llvm.struct<(i32, i32)>
%v49 = llvm.insertvalue %v48, %v47[0] : !llvm.struct<(i32, i32)>
%v50 = llvm.extractvalue %arg0[1] : !llvm.struct<(i32, i32)>
%v51 = llvm.insertvalue %v50, %v49[1] : !llvm.struct<(i32, i32)>
%v52 = llvm.mlir.constant(1 : i64) : i64
%v53 = llvm.alloca %v52 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v51, %v53 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v54 = llvm.load %v53 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v55 = llvm.load %v53 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v56 = llvm.getelementptr %v53[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v57 = llvm.load %v56 : !llvm.ptr -> i32
%v58 = arith.constant 0 : i32
%v59 = arith.cmpi eq, %v57, %v58 : i32
cf.cond_br %v59, ^b22, ^b23
^b22:
%v60 = arith.constant 1 : i32
func.return %v60 : i32
^b23:
%v61 = llvm.load %v53 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v62 = llvm.getelementptr %v53[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v63 = llvm.load %v62 : !llvm.ptr -> i32
%v64 = arith.constant 1 : i32
%v65 = arith.cmpi eq, %v63, %v64 : i32
cf.cond_br %v65, ^b24, ^b25
^b24:
%v66 = arith.constant 2 : i32
func.return %v66 : i32
^b25:
%v67 = arith.constant 1 : i1
cf.cond_br %v67, ^b26, ^b27
^b26:
%v68 = arith.constant 3 : i32
func.return %v68 : i32
^b27:
cf.br ^b28
^b28:
llvm.unreachable
}
func.func @tag_of(%arg0: i32) -> i32 {
%v69 = arith.constant 0 : i32
%v70 = llvm.mlir.constant(1 : i64) : i64
%v71 = llvm.alloca %v70 x i32 : (i64) -> !llvm.ptr
llvm.store %v69, %v71 : i32, !llvm.ptr
%v72 = arith.constant 2 : i32
%v73 = arith.cmpi eq, %arg0, %v72 : i32
cf.cond_br %v73, ^b29, ^b30
^b29:
%v74 = arith.constant 30 : i32
llvm.store %v74, %v71 : i32, !llvm.ptr
cf.br ^b31
^b30:
%v75 = arith.constant 1 : i1
cf.cond_br %v75, ^b32, ^b33
^b32:
llvm.store %arg0, %v71 : i32, !llvm.ptr
cf.br ^b31
^b33:
cf.br ^b31
^b31:
%v76 = llvm.load %v71 : !llvm.ptr -> i32
func.return %v76 : i32
}
func.func @main() -> i32 {
%v77 = arith.constant 0 : i32
%v78 = func.call @classify(%v77) : (i32) -> i32
%v79 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v80 = llvm.call @printf(%v79, %v78) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v81 = arith.constant 0 : i32
%v82 = arith.constant 0 : i32
%v83 = arith.constant 1 : i32
%v84 = arith.subi %v82, %v83 : i32
%v85 = func.call @classify(%v84) : (i32) -> i32
%v86 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v87 = llvm.call @printf(%v86, %v85) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v88 = arith.constant 0 : i32
%v89 = arith.constant 2 : i32
%v90 = func.call @classify(%v89) : (i32) -> i32
%v91 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v92 = llvm.call @printf(%v91, %v90) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v93 = arith.constant 0 : i32
%v94 = arith.constant 500 : i32
%v95 = func.call @classify(%v94) : (i32) -> i32
%v96 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v97 = llvm.call @printf(%v96, %v95) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v98 = arith.constant 0 : i32
%v99 = arith.constant 50 : i32
%v100 = func.call @classify(%v99) : (i32) -> i32
%v101 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v102 = llvm.call @printf(%v101, %v100) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v103 = arith.constant 0 : i32
%v104 = arith.constant 1 : i1
%v105 = func.call @truth(%v104) : (i1) -> i32
%v106 = arith.constant 0 : i1
%v107 = func.call @truth(%v106) : (i1) -> i32
%v108 = arith.addi %v105, %v107 : i32
%v109 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v110 = llvm.call @printf(%v109, %v108) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v111 = arith.constant 0 : i32
%v112 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v113 = arith.constant 3 : i32
%v114 = llvm.insertvalue %v113, %v112[0] : !llvm.struct<(i32, i32)>
%v115 = arith.constant 4 : i32
%v116 = llvm.insertvalue %v115, %v114[1] : !llvm.struct<(i32, i32)>
%v117 = llvm.mlir.constant(1 : i64) : i64
%v118 = llvm.alloca %v117 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v116, %v118 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v119 = llvm.load %v118 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v120 = func.call @pair_sum(%v119) : (!llvm.struct<(i32, i32)>) -> i32
%v121 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v122 = llvm.call @printf(%v121, %v120) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v123 = arith.constant 0 : i32
%v124 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v125 = arith.constant 0 : i32
%v126 = llvm.insertvalue %v125, %v124[0] : !llvm.struct<(i32, i32)>
%v127 = arith.constant 5 : i32
%v128 = llvm.insertvalue %v127, %v126[1] : !llvm.struct<(i32, i32)>
%v129 = llvm.mlir.constant(1 : i64) : i64
%v130 = llvm.alloca %v129 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v128, %v130 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v131 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v132 = arith.constant 1 : i32
%v133 = llvm.insertvalue %v132, %v131[0] : !llvm.struct<(i32, i32)>
%v134 = arith.constant 0 : i32
%v135 = llvm.insertvalue %v134, %v133[1] : !llvm.struct<(i32, i32)>
%v136 = llvm.mlir.constant(1 : i64) : i64
%v137 = llvm.alloca %v136 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v135, %v137 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v138 = llvm.load %v130 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v139 = func.call @shape_code(%v138) : (!llvm.struct<(i32, i32)>) -> i32
%v140 = arith.constant 10 : i32
%v141 = arith.muli %v139, %v140 : i32
%v142 = llvm.load %v137 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v143 = func.call @shape_code(%v142) : (!llvm.struct<(i32, i32)>) -> i32
%v144 = arith.addi %v141, %v143 : i32
%v145 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v146 = llvm.call @printf(%v145, %v144) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v147 = arith.constant 0 : i32
%v148 = arith.constant 2 : i32
%v149 = func.call @tag_of(%v148) : (i32) -> i32
%v150 = arith.constant 4 : i32
%v151 = func.call @tag_of(%v150) : (i32) -> i32
%v152 = arith.addi %v149, %v151 : i32
%v153 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v154 = llvm.call @printf(%v153, %v152) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v155 = arith.constant 0 : i32
%v156 = arith.constant 0 : i32
func.return %v156 : i32
}
}
