module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("Tensor(\00") {addr_space = 0 : i32} : !llvm.array<8 x i8>
llvm.mlir.global internal constant @str_1("%d\n\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_2(", \00") {addr_space = 0 : i32} : !llvm.array<3 x i8>
llvm.mlir.global internal constant @str_3(")\n\00") {addr_space = 0 : i32} : !llvm.array<3 x i8>
llvm.mlir.global internal constant @str_4("  [\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_5("%f\n\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_6(", ...\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
llvm.mlir.global internal constant @str_7("]\n\00") {addr_space = 0 : i32} : !llvm.array<3 x i8>
llvm.mlir.global internal constant @str_8("MLIR Tensor Benchmark\n\00") {addr_space = 0 : i32} : !llvm.array<23 x i8>
llvm.mlir.global internal constant @str_9("=====================\n\00") {addr_space = 0 : i32} : !llvm.array<23 x i8>
llvm.mlir.global internal constant @str_10("matmul 64x64 sum checkpoint\n\00") {addr_space = 0 : i32} : !llvm.array<29 x i8>
llvm.mlir.global internal constant @str_11("matmul 128x128 sum checkpoint\n\00") {addr_space = 0 : i32} : !llvm.array<31 x i8>
llvm.mlir.global internal constant @str_12("done\n\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
func.func private @malloc(i64) -> !llvm.ptr
func.func private @free(!llvm.ptr) -> ()
func.func private @memset(!llvm.ptr, i32, i64) -> !llvm.ptr
func.func private @sqrt(f64) -> f64
func.func private @exp(f64) -> f64
func.func private @log(f64) -> f64
// Struct: Tensor
// Fields:
//   data: !llvm.ptr
//   size: i32
//   dim0: i32
//   dim1: i32
//   dim2: i32
//   dim3: i32
func.func @tensor_zeros(%arg0: i32, %arg1: i32, %arg2: i32, %arg3: i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1 = arith.muli %arg0, %arg1 : i32
%v2 = arith.muli %v1, %arg2 : i32
%v3 = arith.muli %v2, %arg3 : i32
%v4 = arith.extsi %v3 : i32 to i64
%v5 = arith.constant 4 : i32
%v6 = arith.extsi %v5 : i32 to i64
%v7 = arith.muli %v4, %v6 : i64
%v8 = func.call @malloc(%v7) : (i64) -> !llvm.ptr
%v9 = arith.constant 0 : i32
%v10 = func.call @memset(%v8, %v9, %v7) : (!llvm.ptr, i32, i64) -> !llvm.ptr
%v11 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v12 = llvm.insertvalue %v8, %v11[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v13 = llvm.insertvalue %v3, %v12[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v14 = llvm.insertvalue %arg0, %v13[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v15 = llvm.insertvalue %arg1, %v14[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v16 = llvm.insertvalue %arg2, %v15[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v17 = llvm.insertvalue %arg3, %v16[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v18 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v19 = llvm.extractvalue %v17[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v20 = llvm.insertvalue %v19, %v18[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v21 = llvm.extractvalue %v17[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v22 = llvm.insertvalue %v21, %v20[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v23 = llvm.extractvalue %v17[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v24 = llvm.insertvalue %v23, %v22[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v25 = llvm.extractvalue %v17[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v26 = llvm.insertvalue %v25, %v24[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v27 = llvm.extractvalue %v17[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v28 = llvm.insertvalue %v27, %v26[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v29 = llvm.extractvalue %v17[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v30 = llvm.insertvalue %v29, %v28[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v31 = llvm.mlir.constant(1 : i64) : i64
%v32 = llvm.alloca %v31 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v30, %v32 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v33 = llvm.load %v32 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v33 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_ones(%arg0: i32, %arg1: i32, %arg2: i32, %arg3: i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v34 = func.call @tensor_zeros(%arg0, %arg1, %arg2, %arg3) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v35 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v36 = llvm.extractvalue %v34[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v37 = llvm.insertvalue %v36, %v35[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v38 = llvm.extractvalue %v34[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v39 = llvm.insertvalue %v38, %v37[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v40 = llvm.extractvalue %v34[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v41 = llvm.insertvalue %v40, %v39[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v42 = llvm.extractvalue %v34[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v43 = llvm.insertvalue %v42, %v41[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v44 = llvm.extractvalue %v34[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v45 = llvm.insertvalue %v44, %v43[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v46 = llvm.extractvalue %v34[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v47 = llvm.insertvalue %v46, %v45[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v48 = llvm.mlir.constant(1 : i64) : i64
%v49 = llvm.alloca %v48 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v47, %v49 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v50 = llvm.load %v49 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v51 = llvm.mlir.constant(1 : i64) : i64
%v52 = llvm.alloca %v51 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v50, %v52 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v53 = arith.constant 0 : i32
%v54 = llvm.load %v52 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v55 = llvm.getelementptr %v52[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v56 = llvm.load %v55 : !llvm.ptr -> i32
%v57 = arith.index_cast %v53 : i32 to index
%v58 = arith.index_cast %v56 : i32 to index
%v59 = arith.constant 1 : index
%v60 = arith.constant -1 : index
%v61 = arith.cmpi sle, %v57, %v58 : index
%v62 = arith.select %v61, %v59, %v60 : index
cf.br ^b1(%v57 : index)
^b1(%v63: index):
%v64 = arith.cmpi slt, %v63, %v58 : index
%v65 = arith.cmpi sgt, %v63, %v58 : index
%v66 = arith.select %v61, %v64, %v65 : i1
cf.cond_br %v66, ^b2(%v63 : index), ^b3(%v63 : index)
^b2(%v67: index):
%v68 = arith.constant 1.0 : f32
%v69 = llvm.load %v52 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v70 = llvm.getelementptr %v52[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v71 = llvm.load %v70 : !llvm.ptr -> !llvm.ptr
%v72 = arith.index_cast %v67 : index to i64
%v73 = llvm.getelementptr %v71[%v72] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v68, %v73 : f32, !llvm.ptr
%v74 = arith.addi %v67, %v62 : index
cf.br ^b1(%v74 : index)
^b3(%v75: index):
%v76 = llvm.load %v52 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v77 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v78 = llvm.extractvalue %v76[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v79 = llvm.insertvalue %v78, %v77[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v80 = llvm.extractvalue %v76[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v81 = llvm.insertvalue %v80, %v79[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v82 = llvm.extractvalue %v76[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v83 = llvm.insertvalue %v82, %v81[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v84 = llvm.extractvalue %v76[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v85 = llvm.insertvalue %v84, %v83[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v86 = llvm.extractvalue %v76[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v87 = llvm.insertvalue %v86, %v85[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v88 = llvm.extractvalue %v76[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v89 = llvm.insertvalue %v88, %v87[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v90 = llvm.mlir.constant(1 : i64) : i64
%v91 = llvm.alloca %v90 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v89, %v91 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v92 = llvm.load %v91 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v92 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_fill(%arg0: i32, %arg1: i32, %arg2: i32, %arg3: i32, %arg4: f32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v93 = func.call @tensor_zeros(%arg0, %arg1, %arg2, %arg3) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v94 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v95 = llvm.extractvalue %v93[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v96 = llvm.insertvalue %v95, %v94[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v97 = llvm.extractvalue %v93[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v98 = llvm.insertvalue %v97, %v96[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v99 = llvm.extractvalue %v93[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v100 = llvm.insertvalue %v99, %v98[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v101 = llvm.extractvalue %v93[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v102 = llvm.insertvalue %v101, %v100[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v103 = llvm.extractvalue %v93[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v104 = llvm.insertvalue %v103, %v102[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v105 = llvm.extractvalue %v93[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v106 = llvm.insertvalue %v105, %v104[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v107 = llvm.mlir.constant(1 : i64) : i64
%v108 = llvm.alloca %v107 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v106, %v108 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v109 = llvm.load %v108 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v110 = llvm.mlir.constant(1 : i64) : i64
%v111 = llvm.alloca %v110 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v109, %v111 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v112 = arith.constant 0 : i32
%v113 = llvm.load %v111 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v114 = llvm.getelementptr %v111[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v115 = llvm.load %v114 : !llvm.ptr -> i32
%v116 = arith.index_cast %v112 : i32 to index
%v117 = arith.index_cast %v115 : i32 to index
%v118 = arith.constant 1 : index
%v119 = arith.constant -1 : index
%v120 = arith.cmpi sle, %v116, %v117 : index
%v121 = arith.select %v120, %v118, %v119 : index
cf.br ^b4(%v116 : index)
^b4(%v122: index):
%v123 = arith.cmpi slt, %v122, %v117 : index
%v124 = arith.cmpi sgt, %v122, %v117 : index
%v125 = arith.select %v120, %v123, %v124 : i1
cf.cond_br %v125, ^b5(%v122 : index), ^b6(%v122 : index)
^b5(%v126: index):
%v127 = llvm.load %v111 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v128 = llvm.getelementptr %v111[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v129 = llvm.load %v128 : !llvm.ptr -> !llvm.ptr
%v130 = arith.index_cast %v126 : index to i64
%v131 = llvm.getelementptr %v129[%v130] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %arg4, %v131 : f32, !llvm.ptr
%v132 = arith.addi %v126, %v121 : index
cf.br ^b4(%v132 : index)
^b6(%v133: index):
%v134 = llvm.load %v111 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v135 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v136 = llvm.extractvalue %v134[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v137 = llvm.insertvalue %v136, %v135[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v138 = llvm.extractvalue %v134[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v139 = llvm.insertvalue %v138, %v137[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v140 = llvm.extractvalue %v134[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v141 = llvm.insertvalue %v140, %v139[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v142 = llvm.extractvalue %v134[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v143 = llvm.insertvalue %v142, %v141[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v144 = llvm.extractvalue %v134[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v145 = llvm.insertvalue %v144, %v143[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v146 = llvm.extractvalue %v134[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v147 = llvm.insertvalue %v146, %v145[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v148 = llvm.mlir.constant(1 : i64) : i64
%v149 = llvm.alloca %v148 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v147, %v149 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v150 = llvm.load %v149 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v150 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_rand(%arg0: i32, %arg1: i32, %arg2: i32, %arg3: i32, %arg4: i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v151 = func.call @tensor_zeros(%arg0, %arg1, %arg2, %arg3) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v152 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v153 = llvm.extractvalue %v151[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v154 = llvm.insertvalue %v153, %v152[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v155 = llvm.extractvalue %v151[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v156 = llvm.insertvalue %v155, %v154[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v157 = llvm.extractvalue %v151[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v158 = llvm.insertvalue %v157, %v156[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v159 = llvm.extractvalue %v151[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v160 = llvm.insertvalue %v159, %v158[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v161 = llvm.extractvalue %v151[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v162 = llvm.insertvalue %v161, %v160[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v163 = llvm.extractvalue %v151[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v164 = llvm.insertvalue %v163, %v162[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v165 = llvm.mlir.constant(1 : i64) : i64
%v166 = llvm.alloca %v165 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v164, %v166 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v167 = llvm.load %v166 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v168 = llvm.mlir.constant(1 : i64) : i64
%v169 = llvm.alloca %v168 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v167, %v169 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v170 = llvm.mlir.constant(1 : i64) : i64
%v171 = llvm.alloca %v170 x i32 : (i64) -> !llvm.ptr
llvm.store %arg4, %v171 : i32, !llvm.ptr
%v172 = arith.constant 0 : i32
%v173 = llvm.load %v169 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v174 = llvm.getelementptr %v169[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v175 = llvm.load %v174 : !llvm.ptr -> i32
%v176 = arith.index_cast %v172 : i32 to index
%v177 = arith.index_cast %v175 : i32 to index
%v178 = arith.constant 1 : index
%v179 = arith.constant -1 : index
%v180 = arith.cmpi sle, %v176, %v177 : index
%v181 = arith.select %v180, %v178, %v179 : index
cf.br ^b7(%v176 : index)
^b7(%v182: index):
%v183 = arith.cmpi slt, %v182, %v177 : index
%v184 = arith.cmpi sgt, %v182, %v177 : index
%v185 = arith.select %v180, %v183, %v184 : i1
cf.cond_br %v185, ^b8(%v182 : index), ^b9(%v182 : index)
^b8(%v186: index):
%v187 = llvm.load %v171 : !llvm.ptr -> i32
%v188 = arith.constant 1103515245 : i32
%v189 = arith.muli %v187, %v188 : i32
%v190 = arith.constant 12345 : i32
%v191 = arith.addi %v189, %v190 : i32
%v192 = arith.constant 2147483647 : i32
%v193 = arith.remsi %v191, %v192 : i32
llvm.store %v193, %v171 : i32, !llvm.ptr
%v194 = llvm.load %v171 : !llvm.ptr -> i32
%v195 = arith.constant 0 : i32
%v196 = arith.cmpi slt, %v194, %v195 : i32
cf.cond_br %v196, ^b10, ^b11
^b10:
%v197 = arith.constant 0 : i32
%v198 = llvm.load %v171 : !llvm.ptr -> i32
%v199 = arith.subi %v197, %v198 : i32
llvm.store %v199, %v171 : i32, !llvm.ptr
cf.br ^b12
^b11:
cf.br ^b12
^b12:
%v200 = llvm.load %v171 : !llvm.ptr -> i32
%v201 = arith.constant 10000 : i32
%v202 = arith.remsi %v200, %v201 : i32
%v203 = arith.constant 10000.0 : f32
%v204 = arith.sitofp %v202 : i32 to f32
%v205 = arith.divf %v204, %v203 : f32
%v206 = llvm.load %v169 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v207 = llvm.getelementptr %v169[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v208 = llvm.load %v207 : !llvm.ptr -> !llvm.ptr
%v209 = arith.index_cast %v186 : index to i64
%v210 = llvm.getelementptr %v208[%v209] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v205, %v210 : f32, !llvm.ptr
%v211 = arith.addi %v186, %v181 : index
cf.br ^b7(%v211 : index)
^b9(%v212: index):
%v213 = llvm.load %v169 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v214 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v215 = llvm.extractvalue %v213[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v216 = llvm.insertvalue %v215, %v214[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v217 = llvm.extractvalue %v213[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v218 = llvm.insertvalue %v217, %v216[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v219 = llvm.extractvalue %v213[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v220 = llvm.insertvalue %v219, %v218[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v221 = llvm.extractvalue %v213[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v222 = llvm.insertvalue %v221, %v220[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v223 = llvm.extractvalue %v213[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v224 = llvm.insertvalue %v223, %v222[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v225 = llvm.extractvalue %v213[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v226 = llvm.insertvalue %v225, %v224[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v227 = llvm.mlir.constant(1 : i64) : i64
%v228 = llvm.alloca %v227 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v226, %v228 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v229 = llvm.load %v228 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v229 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_randn(%arg0: i32, %arg1: i32, %arg2: i32, %arg3: i32, %arg4: i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v230 = func.call @tensor_zeros(%arg0, %arg1, %arg2, %arg3) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v231 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v232 = llvm.extractvalue %v230[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v233 = llvm.insertvalue %v232, %v231[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v234 = llvm.extractvalue %v230[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v235 = llvm.insertvalue %v234, %v233[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v236 = llvm.extractvalue %v230[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v237 = llvm.insertvalue %v236, %v235[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v238 = llvm.extractvalue %v230[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v239 = llvm.insertvalue %v238, %v237[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v240 = llvm.extractvalue %v230[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v241 = llvm.insertvalue %v240, %v239[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v242 = llvm.extractvalue %v230[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v243 = llvm.insertvalue %v242, %v241[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v244 = llvm.mlir.constant(1 : i64) : i64
%v245 = llvm.alloca %v244 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v243, %v245 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v246 = llvm.load %v245 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v247 = llvm.mlir.constant(1 : i64) : i64
%v248 = llvm.alloca %v247 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v246, %v248 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v249 = llvm.mlir.constant(1 : i64) : i64
%v250 = llvm.alloca %v249 x i32 : (i64) -> !llvm.ptr
llvm.store %arg4, %v250 : i32, !llvm.ptr
%v251 = arith.constant 0 : i32
%v252 = llvm.load %v248 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v253 = llvm.getelementptr %v248[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v254 = llvm.load %v253 : !llvm.ptr -> i32
%v255 = arith.index_cast %v251 : i32 to index
%v256 = arith.index_cast %v254 : i32 to index
%v257 = arith.constant 1 : index
%v258 = arith.constant -1 : index
%v259 = arith.cmpi sle, %v255, %v256 : index
%v260 = arith.select %v259, %v257, %v258 : index
cf.br ^b13(%v255 : index)
^b13(%v261: index):
%v262 = arith.cmpi slt, %v261, %v256 : index
%v263 = arith.cmpi sgt, %v261, %v256 : index
%v264 = arith.select %v259, %v262, %v263 : i1
cf.cond_br %v264, ^b14(%v261 : index), ^b15(%v261 : index)
^b14(%v265: index):
%v266 = llvm.load %v250 : !llvm.ptr -> i32
%v267 = arith.constant 1103515245 : i32
%v268 = arith.muli %v266, %v267 : i32
%v269 = arith.constant 12345 : i32
%v270 = arith.addi %v268, %v269 : i32
%v271 = arith.constant 2147483647 : i32
%v272 = arith.remsi %v270, %v271 : i32
llvm.store %v272, %v250 : i32, !llvm.ptr
%v273 = llvm.load %v250 : !llvm.ptr -> i32
%v274 = arith.constant 0 : i32
%v275 = arith.cmpi slt, %v273, %v274 : i32
cf.cond_br %v275, ^b16, ^b17
^b16:
%v276 = arith.constant 0 : i32
%v277 = llvm.load %v250 : !llvm.ptr -> i32
%v278 = arith.subi %v276, %v277 : i32
llvm.store %v278, %v250 : i32, !llvm.ptr
cf.br ^b18
^b17:
cf.br ^b18
^b18:
%v279 = llvm.load %v250 : !llvm.ptr -> i32
%v280 = arith.constant 10000 : i32
%v281 = arith.remsi %v279, %v280 : i32
%v282 = arith.constant 1 : i32
%v283 = arith.addi %v281, %v282 : i32
%v284 = arith.constant 10001.0 : f32
%v285 = arith.sitofp %v283 : i32 to f32
%v286 = arith.divf %v285, %v284 : f32
%v287 = arith.extf %v286 : f32 to f64
%v288 = llvm.load %v250 : !llvm.ptr -> i32
%v289 = arith.constant 1103515245 : i32
%v290 = arith.muli %v288, %v289 : i32
%v291 = arith.constant 12345 : i32
%v292 = arith.addi %v290, %v291 : i32
%v293 = arith.constant 2147483647 : i32
%v294 = arith.remsi %v292, %v293 : i32
llvm.store %v294, %v250 : i32, !llvm.ptr
%v295 = llvm.load %v250 : !llvm.ptr -> i32
%v296 = arith.constant 0 : i32
%v297 = arith.cmpi slt, %v295, %v296 : i32
cf.cond_br %v297, ^b19, ^b20
^b19:
%v298 = arith.constant 0 : i32
%v299 = llvm.load %v250 : !llvm.ptr -> i32
%v300 = arith.subi %v298, %v299 : i32
llvm.store %v300, %v250 : i32, !llvm.ptr
cf.br ^b21
^b20:
cf.br ^b21
^b21:
%v301 = llvm.load %v250 : !llvm.ptr -> i32
%v302 = arith.constant 10000 : i32
%v303 = arith.remsi %v301, %v302 : i32
%v304 = arith.constant 10000.0 : f32
%v305 = arith.sitofp %v303 : i32 to f32
%v306 = arith.divf %v305, %v304 : f32
%v307 = arith.extf %v306 : f32 to f64
%v308 = arith.constant 0.0 : f32
%v309 = arith.constant 2.0 : f32
%v310 = func.call @log(%v287) : (f64) -> f64
%v311 = arith.extf %v309 : f32 to f64
%v312 = arith.mulf %v311, %v310 : f64
%v313 = arith.extf %v308 : f32 to f64
%v314 = arith.subf %v313, %v312 : f64
%v315 = func.call @sqrt(%v314) : (f64) -> f64
%v316 = arith.constant 0.5 : f32
%v317 = arith.extf %v316 : f32 to f64
%v318 = arith.mulf %v315, %v317 : f64
%v319 = llvm.load %v248 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v320 = llvm.getelementptr %v248[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v321 = llvm.load %v320 : !llvm.ptr -> !llvm.ptr
%v322 = arith.truncf %v318 : f64 to f32
%v323 = arith.index_cast %v265 : index to i64
%v324 = llvm.getelementptr %v321[%v323] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v322, %v324 : f32, !llvm.ptr
%v325 = arith.addi %v265, %v260 : index
cf.br ^b13(%v325 : index)
^b15(%v326: index):
%v327 = llvm.load %v248 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v328 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v329 = llvm.extractvalue %v327[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v330 = llvm.insertvalue %v329, %v328[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v331 = llvm.extractvalue %v327[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v332 = llvm.insertvalue %v331, %v330[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v333 = llvm.extractvalue %v327[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v334 = llvm.insertvalue %v333, %v332[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v335 = llvm.extractvalue %v327[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v336 = llvm.insertvalue %v335, %v334[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v337 = llvm.extractvalue %v327[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v338 = llvm.insertvalue %v337, %v336[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v339 = llvm.extractvalue %v327[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v340 = llvm.insertvalue %v339, %v338[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v341 = llvm.mlir.constant(1 : i64) : i64
%v342 = llvm.alloca %v341 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v340, %v342 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v343 = llvm.load %v342 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v343 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_free(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> () {
%v344 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v345 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v346 = llvm.insertvalue %v345, %v344[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v347 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v348 = llvm.insertvalue %v347, %v346[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v349 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v350 = llvm.insertvalue %v349, %v348[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v351 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v352 = llvm.insertvalue %v351, %v350[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v353 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v354 = llvm.insertvalue %v353, %v352[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v355 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v356 = llvm.insertvalue %v355, %v354[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v357 = llvm.mlir.constant(1 : i64) : i64
%v358 = llvm.alloca %v357 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v356, %v358 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v359 = llvm.load %v358 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v360 = llvm.getelementptr %v358[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v361 = llvm.load %v360 : !llvm.ptr -> !llvm.ptr
func.call @free(%v361) : (!llvm.ptr) -> ()
func.return
}
func.func @tensor_idx(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: i32, %arg2: i32, %arg3: i32, %arg4: i32) -> i32 {
%v362 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v363 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v364 = llvm.insertvalue %v363, %v362[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v365 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v366 = llvm.insertvalue %v365, %v364[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v367 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v368 = llvm.insertvalue %v367, %v366[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v369 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v370 = llvm.insertvalue %v369, %v368[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v371 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v372 = llvm.insertvalue %v371, %v370[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v373 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v374 = llvm.insertvalue %v373, %v372[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v375 = llvm.mlir.constant(1 : i64) : i64
%v376 = llvm.alloca %v375 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v374, %v376 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v377 = llvm.load %v376 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v378 = llvm.getelementptr %v376[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v379 = llvm.load %v378 : !llvm.ptr -> i32
%v380 = arith.muli %arg1, %v379 : i32
%v381 = arith.addi %v380, %arg2 : i32
%v382 = llvm.load %v376 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v383 = llvm.getelementptr %v376[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v384 = llvm.load %v383 : !llvm.ptr -> i32
%v385 = arith.muli %v381, %v384 : i32
%v386 = arith.addi %v385, %arg3 : i32
%v387 = llvm.load %v376 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v388 = llvm.getelementptr %v376[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v389 = llvm.load %v388 : !llvm.ptr -> i32
%v390 = arith.muli %v386, %v389 : i32
%v391 = arith.addi %v390, %arg4 : i32
func.return %v391 : i32
}
func.func @tensor_get(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: i32, %arg2: i32, %arg3: i32, %arg4: i32) -> f32 {
%v392 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v393 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v394 = llvm.insertvalue %v393, %v392[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v395 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v396 = llvm.insertvalue %v395, %v394[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v397 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v398 = llvm.insertvalue %v397, %v396[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v399 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v400 = llvm.insertvalue %v399, %v398[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v401 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v402 = llvm.insertvalue %v401, %v400[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v403 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v404 = llvm.insertvalue %v403, %v402[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v405 = llvm.mlir.constant(1 : i64) : i64
%v406 = llvm.alloca %v405 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v404, %v406 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v407 = llvm.load %v406 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v408 = llvm.getelementptr %v406[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v409 = llvm.load %v408 : !llvm.ptr -> !llvm.ptr
%v410 = llvm.load %v406 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v411 = func.call @tensor_idx(%v410, %arg1, %arg2, %arg3, %arg4) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, i32, i32, i32, i32) -> i32
%v412 = arith.extsi %v411 : i32 to i64
%v413 = llvm.getelementptr %v409[%v412] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v414 = llvm.load %v413 : !llvm.ptr -> f32
func.return %v414 : f32
}
func.func @tensor_set(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: i32, %arg2: i32, %arg3: i32, %arg4: i32, %arg5: f32) -> () {
%v415 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v416 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v417 = llvm.insertvalue %v416, %v415[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v418 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v419 = llvm.insertvalue %v418, %v417[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v420 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v421 = llvm.insertvalue %v420, %v419[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v422 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v423 = llvm.insertvalue %v422, %v421[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v424 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v425 = llvm.insertvalue %v424, %v423[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v426 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v427 = llvm.insertvalue %v426, %v425[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v428 = llvm.mlir.constant(1 : i64) : i64
%v429 = llvm.alloca %v428 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v427, %v429 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v430 = llvm.load %v429 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v431 = llvm.getelementptr %v429[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v432 = llvm.load %v431 : !llvm.ptr -> !llvm.ptr
%v433 = llvm.load %v429 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v434 = func.call @tensor_idx(%v433, %arg1, %arg2, %arg3, %arg4) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, i32, i32, i32, i32) -> i32
%v435 = arith.extsi %v434 : i32 to i64
%v436 = llvm.getelementptr %v432[%v435] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %arg5, %v436 : f32, !llvm.ptr
func.return
}
func.func @tensor_get2(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: i32, %arg2: i32) -> f32 {
%v437 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v438 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v439 = llvm.insertvalue %v438, %v437[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v440 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v441 = llvm.insertvalue %v440, %v439[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v442 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v443 = llvm.insertvalue %v442, %v441[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v444 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v445 = llvm.insertvalue %v444, %v443[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v446 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v447 = llvm.insertvalue %v446, %v445[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v448 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v449 = llvm.insertvalue %v448, %v447[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v450 = llvm.mlir.constant(1 : i64) : i64
%v451 = llvm.alloca %v450 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v449, %v451 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v452 = llvm.load %v451 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v453 = llvm.getelementptr %v451[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v454 = llvm.load %v453 : !llvm.ptr -> !llvm.ptr
%v455 = llvm.load %v451 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v456 = llvm.getelementptr %v451[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v457 = llvm.load %v456 : !llvm.ptr -> i32
%v458 = arith.muli %arg1, %v457 : i32
%v459 = arith.addi %v458, %arg2 : i32
%v460 = arith.extsi %v459 : i32 to i64
%v461 = llvm.getelementptr %v454[%v460] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v462 = llvm.load %v461 : !llvm.ptr -> f32
func.return %v462 : f32
}
func.func @tensor_set2(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: i32, %arg2: i32, %arg3: f32) -> () {
%v463 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v464 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v465 = llvm.insertvalue %v464, %v463[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v466 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v467 = llvm.insertvalue %v466, %v465[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v468 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v469 = llvm.insertvalue %v468, %v467[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v470 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v471 = llvm.insertvalue %v470, %v469[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v472 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v473 = llvm.insertvalue %v472, %v471[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v474 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v475 = llvm.insertvalue %v474, %v473[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v476 = llvm.mlir.constant(1 : i64) : i64
%v477 = llvm.alloca %v476 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v475, %v477 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v478 = llvm.load %v477 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v479 = llvm.getelementptr %v477[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v480 = llvm.load %v479 : !llvm.ptr -> !llvm.ptr
%v481 = llvm.load %v477 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v482 = llvm.getelementptr %v477[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v483 = llvm.load %v482 : !llvm.ptr -> i32
%v484 = arith.muli %arg1, %v483 : i32
%v485 = arith.addi %v484, %arg2 : i32
%v486 = arith.extsi %v485 : i32 to i64
%v487 = llvm.getelementptr %v480[%v486] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %arg3, %v487 : f32, !llvm.ptr
func.return
}
func.func @tensor_get1(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: i32) -> f32 {
%v488 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v489 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v490 = llvm.insertvalue %v489, %v488[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v491 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v492 = llvm.insertvalue %v491, %v490[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v493 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v494 = llvm.insertvalue %v493, %v492[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v495 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v496 = llvm.insertvalue %v495, %v494[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v497 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v498 = llvm.insertvalue %v497, %v496[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v499 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v500 = llvm.insertvalue %v499, %v498[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v501 = llvm.mlir.constant(1 : i64) : i64
%v502 = llvm.alloca %v501 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v500, %v502 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v503 = llvm.load %v502 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v504 = llvm.getelementptr %v502[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v505 = llvm.load %v504 : !llvm.ptr -> !llvm.ptr
%v506 = arith.extsi %arg1 : i32 to i64
%v507 = llvm.getelementptr %v505[%v506] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v508 = llvm.load %v507 : !llvm.ptr -> f32
func.return %v508 : f32
}
func.func @tensor_set1(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: i32, %arg2: f32) -> () {
%v509 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v510 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v511 = llvm.insertvalue %v510, %v509[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v512 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v513 = llvm.insertvalue %v512, %v511[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v514 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v515 = llvm.insertvalue %v514, %v513[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v516 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v517 = llvm.insertvalue %v516, %v515[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v518 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v519 = llvm.insertvalue %v518, %v517[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v520 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v521 = llvm.insertvalue %v520, %v519[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v522 = llvm.mlir.constant(1 : i64) : i64
%v523 = llvm.alloca %v522 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v521, %v523 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v524 = llvm.load %v523 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v525 = llvm.getelementptr %v523[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v526 = llvm.load %v525 : !llvm.ptr -> !llvm.ptr
%v527 = arith.extsi %arg1 : i32 to i64
%v528 = llvm.getelementptr %v526[%v527] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %arg2, %v528 : f32, !llvm.ptr
func.return
}
func.func @tensor_add(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v529 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v530 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v531 = llvm.insertvalue %v530, %v529[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v532 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v533 = llvm.insertvalue %v532, %v531[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v534 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v535 = llvm.insertvalue %v534, %v533[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v536 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v537 = llvm.insertvalue %v536, %v535[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v538 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v539 = llvm.insertvalue %v538, %v537[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v540 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v541 = llvm.insertvalue %v540, %v539[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v542 = llvm.mlir.constant(1 : i64) : i64
%v543 = llvm.alloca %v542 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v541, %v543 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v544 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v545 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v546 = llvm.insertvalue %v545, %v544[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v547 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v548 = llvm.insertvalue %v547, %v546[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v549 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v550 = llvm.insertvalue %v549, %v548[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v551 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v552 = llvm.insertvalue %v551, %v550[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v553 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v554 = llvm.insertvalue %v553, %v552[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v555 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v556 = llvm.insertvalue %v555, %v554[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v557 = llvm.mlir.constant(1 : i64) : i64
%v558 = llvm.alloca %v557 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v556, %v558 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v559 = llvm.load %v543 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v560 = llvm.getelementptr %v543[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v561 = llvm.load %v560 : !llvm.ptr -> i32
%v562 = llvm.load %v543 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v563 = llvm.getelementptr %v543[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v564 = llvm.load %v563 : !llvm.ptr -> i32
%v565 = llvm.load %v543 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v566 = llvm.getelementptr %v543[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v567 = llvm.load %v566 : !llvm.ptr -> i32
%v568 = llvm.load %v543 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v569 = llvm.getelementptr %v543[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v570 = llvm.load %v569 : !llvm.ptr -> i32
%v571 = func.call @tensor_zeros(%v570, %v567, %v564, %v561) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v572 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v573 = llvm.extractvalue %v571[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v574 = llvm.insertvalue %v573, %v572[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v575 = llvm.extractvalue %v571[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v576 = llvm.insertvalue %v575, %v574[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v577 = llvm.extractvalue %v571[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v578 = llvm.insertvalue %v577, %v576[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v579 = llvm.extractvalue %v571[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v580 = llvm.insertvalue %v579, %v578[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v581 = llvm.extractvalue %v571[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v582 = llvm.insertvalue %v581, %v580[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v583 = llvm.extractvalue %v571[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v584 = llvm.insertvalue %v583, %v582[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v585 = llvm.mlir.constant(1 : i64) : i64
%v586 = llvm.alloca %v585 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v584, %v586 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v587 = llvm.load %v586 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v588 = llvm.mlir.constant(1 : i64) : i64
%v589 = llvm.alloca %v588 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v587, %v589 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v590 = arith.constant 0 : i32
%v591 = llvm.load %v543 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v592 = llvm.getelementptr %v543[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v593 = llvm.load %v592 : !llvm.ptr -> i32
%v594 = arith.index_cast %v590 : i32 to index
%v595 = arith.index_cast %v593 : i32 to index
%v596 = arith.constant 1 : index
%v597 = arith.constant -1 : index
%v598 = arith.cmpi sle, %v594, %v595 : index
%v599 = arith.select %v598, %v596, %v597 : index
cf.br ^b22(%v594 : index)
^b22(%v600: index):
%v601 = arith.cmpi slt, %v600, %v595 : index
%v602 = arith.cmpi sgt, %v600, %v595 : index
%v603 = arith.select %v598, %v601, %v602 : i1
cf.cond_br %v603, ^b23(%v600 : index), ^b24(%v600 : index)
^b23(%v604: index):
%v605 = llvm.load %v543 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v606 = llvm.getelementptr %v543[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v607 = llvm.load %v606 : !llvm.ptr -> !llvm.ptr
%v608 = arith.index_cast %v604 : index to i64
%v609 = llvm.getelementptr %v607[%v608] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v610 = llvm.load %v609 : !llvm.ptr -> f32
%v611 = llvm.load %v558 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v612 = llvm.getelementptr %v558[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v613 = llvm.load %v612 : !llvm.ptr -> !llvm.ptr
%v614 = arith.index_cast %v604 : index to i64
%v615 = llvm.getelementptr %v613[%v614] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v616 = llvm.load %v615 : !llvm.ptr -> f32
%v617 = arith.addf %v610, %v616 : f32
%v618 = llvm.load %v589 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v619 = llvm.getelementptr %v589[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v620 = llvm.load %v619 : !llvm.ptr -> !llvm.ptr
%v621 = arith.index_cast %v604 : index to i64
%v622 = llvm.getelementptr %v620[%v621] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v617, %v622 : f32, !llvm.ptr
%v623 = arith.addi %v604, %v599 : index
cf.br ^b22(%v623 : index)
^b24(%v624: index):
%v625 = llvm.load %v589 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v626 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v627 = llvm.extractvalue %v625[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v628 = llvm.insertvalue %v627, %v626[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v629 = llvm.extractvalue %v625[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v630 = llvm.insertvalue %v629, %v628[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v631 = llvm.extractvalue %v625[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v632 = llvm.insertvalue %v631, %v630[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v633 = llvm.extractvalue %v625[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v634 = llvm.insertvalue %v633, %v632[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v635 = llvm.extractvalue %v625[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v636 = llvm.insertvalue %v635, %v634[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v637 = llvm.extractvalue %v625[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v638 = llvm.insertvalue %v637, %v636[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v639 = llvm.mlir.constant(1 : i64) : i64
%v640 = llvm.alloca %v639 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v638, %v640 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v641 = llvm.load %v640 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v641 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_sub(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v642 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v643 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v644 = llvm.insertvalue %v643, %v642[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v645 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v646 = llvm.insertvalue %v645, %v644[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v647 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v648 = llvm.insertvalue %v647, %v646[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v649 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v650 = llvm.insertvalue %v649, %v648[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v651 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v652 = llvm.insertvalue %v651, %v650[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v653 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v654 = llvm.insertvalue %v653, %v652[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v655 = llvm.mlir.constant(1 : i64) : i64
%v656 = llvm.alloca %v655 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v654, %v656 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v657 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v658 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v659 = llvm.insertvalue %v658, %v657[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v660 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v661 = llvm.insertvalue %v660, %v659[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v662 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v663 = llvm.insertvalue %v662, %v661[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v664 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v665 = llvm.insertvalue %v664, %v663[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v666 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v667 = llvm.insertvalue %v666, %v665[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v668 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v669 = llvm.insertvalue %v668, %v667[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v670 = llvm.mlir.constant(1 : i64) : i64
%v671 = llvm.alloca %v670 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v669, %v671 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v672 = llvm.load %v656 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v673 = llvm.getelementptr %v656[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v674 = llvm.load %v673 : !llvm.ptr -> i32
%v675 = llvm.load %v656 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v676 = llvm.getelementptr %v656[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v677 = llvm.load %v676 : !llvm.ptr -> i32
%v678 = llvm.load %v656 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v679 = llvm.getelementptr %v656[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v680 = llvm.load %v679 : !llvm.ptr -> i32
%v681 = llvm.load %v656 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v682 = llvm.getelementptr %v656[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v683 = llvm.load %v682 : !llvm.ptr -> i32
%v684 = func.call @tensor_zeros(%v683, %v680, %v677, %v674) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v685 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v686 = llvm.extractvalue %v684[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v687 = llvm.insertvalue %v686, %v685[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v688 = llvm.extractvalue %v684[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v689 = llvm.insertvalue %v688, %v687[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v690 = llvm.extractvalue %v684[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v691 = llvm.insertvalue %v690, %v689[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v692 = llvm.extractvalue %v684[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v693 = llvm.insertvalue %v692, %v691[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v694 = llvm.extractvalue %v684[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v695 = llvm.insertvalue %v694, %v693[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v696 = llvm.extractvalue %v684[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v697 = llvm.insertvalue %v696, %v695[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v698 = llvm.mlir.constant(1 : i64) : i64
%v699 = llvm.alloca %v698 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v697, %v699 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v700 = llvm.load %v699 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v701 = llvm.mlir.constant(1 : i64) : i64
%v702 = llvm.alloca %v701 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v700, %v702 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v703 = arith.constant 0 : i32
%v704 = llvm.load %v656 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v705 = llvm.getelementptr %v656[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v706 = llvm.load %v705 : !llvm.ptr -> i32
%v707 = arith.index_cast %v703 : i32 to index
%v708 = arith.index_cast %v706 : i32 to index
%v709 = arith.constant 1 : index
%v710 = arith.constant -1 : index
%v711 = arith.cmpi sle, %v707, %v708 : index
%v712 = arith.select %v711, %v709, %v710 : index
cf.br ^b25(%v707 : index)
^b25(%v713: index):
%v714 = arith.cmpi slt, %v713, %v708 : index
%v715 = arith.cmpi sgt, %v713, %v708 : index
%v716 = arith.select %v711, %v714, %v715 : i1
cf.cond_br %v716, ^b26(%v713 : index), ^b27(%v713 : index)
^b26(%v717: index):
%v718 = llvm.load %v656 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v719 = llvm.getelementptr %v656[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v720 = llvm.load %v719 : !llvm.ptr -> !llvm.ptr
%v721 = arith.index_cast %v717 : index to i64
%v722 = llvm.getelementptr %v720[%v721] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v723 = llvm.load %v722 : !llvm.ptr -> f32
%v724 = llvm.load %v671 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v725 = llvm.getelementptr %v671[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v726 = llvm.load %v725 : !llvm.ptr -> !llvm.ptr
%v727 = arith.index_cast %v717 : index to i64
%v728 = llvm.getelementptr %v726[%v727] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v729 = llvm.load %v728 : !llvm.ptr -> f32
%v730 = arith.subf %v723, %v729 : f32
%v731 = llvm.load %v702 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v732 = llvm.getelementptr %v702[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v733 = llvm.load %v732 : !llvm.ptr -> !llvm.ptr
%v734 = arith.index_cast %v717 : index to i64
%v735 = llvm.getelementptr %v733[%v734] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v730, %v735 : f32, !llvm.ptr
%v736 = arith.addi %v717, %v712 : index
cf.br ^b25(%v736 : index)
^b27(%v737: index):
%v738 = llvm.load %v702 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v739 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v740 = llvm.extractvalue %v738[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v741 = llvm.insertvalue %v740, %v739[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v742 = llvm.extractvalue %v738[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v743 = llvm.insertvalue %v742, %v741[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v744 = llvm.extractvalue %v738[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v745 = llvm.insertvalue %v744, %v743[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v746 = llvm.extractvalue %v738[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v747 = llvm.insertvalue %v746, %v745[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v748 = llvm.extractvalue %v738[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v749 = llvm.insertvalue %v748, %v747[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v750 = llvm.extractvalue %v738[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v751 = llvm.insertvalue %v750, %v749[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v752 = llvm.mlir.constant(1 : i64) : i64
%v753 = llvm.alloca %v752 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v751, %v753 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v754 = llvm.load %v753 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v754 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_mul(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v755 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v756 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v757 = llvm.insertvalue %v756, %v755[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v758 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v759 = llvm.insertvalue %v758, %v757[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v760 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v761 = llvm.insertvalue %v760, %v759[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v762 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v763 = llvm.insertvalue %v762, %v761[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v764 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v765 = llvm.insertvalue %v764, %v763[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v766 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v767 = llvm.insertvalue %v766, %v765[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v768 = llvm.mlir.constant(1 : i64) : i64
%v769 = llvm.alloca %v768 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v767, %v769 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v770 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v771 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v772 = llvm.insertvalue %v771, %v770[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v773 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v774 = llvm.insertvalue %v773, %v772[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v775 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v776 = llvm.insertvalue %v775, %v774[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v777 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v778 = llvm.insertvalue %v777, %v776[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v779 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v780 = llvm.insertvalue %v779, %v778[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v781 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v782 = llvm.insertvalue %v781, %v780[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v783 = llvm.mlir.constant(1 : i64) : i64
%v784 = llvm.alloca %v783 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v782, %v784 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v785 = llvm.load %v769 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v786 = llvm.getelementptr %v769[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v787 = llvm.load %v786 : !llvm.ptr -> i32
%v788 = llvm.load %v769 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v789 = llvm.getelementptr %v769[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v790 = llvm.load %v789 : !llvm.ptr -> i32
%v791 = llvm.load %v769 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v792 = llvm.getelementptr %v769[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v793 = llvm.load %v792 : !llvm.ptr -> i32
%v794 = llvm.load %v769 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v795 = llvm.getelementptr %v769[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v796 = llvm.load %v795 : !llvm.ptr -> i32
%v797 = func.call @tensor_zeros(%v796, %v793, %v790, %v787) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v798 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v799 = llvm.extractvalue %v797[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v800 = llvm.insertvalue %v799, %v798[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v801 = llvm.extractvalue %v797[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v802 = llvm.insertvalue %v801, %v800[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v803 = llvm.extractvalue %v797[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v804 = llvm.insertvalue %v803, %v802[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v805 = llvm.extractvalue %v797[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v806 = llvm.insertvalue %v805, %v804[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v807 = llvm.extractvalue %v797[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v808 = llvm.insertvalue %v807, %v806[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v809 = llvm.extractvalue %v797[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v810 = llvm.insertvalue %v809, %v808[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v811 = llvm.mlir.constant(1 : i64) : i64
%v812 = llvm.alloca %v811 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v810, %v812 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v813 = llvm.load %v812 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v814 = llvm.mlir.constant(1 : i64) : i64
%v815 = llvm.alloca %v814 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v813, %v815 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v816 = arith.constant 0 : i32
%v817 = llvm.load %v769 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v818 = llvm.getelementptr %v769[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v819 = llvm.load %v818 : !llvm.ptr -> i32
%v820 = arith.index_cast %v816 : i32 to index
%v821 = arith.index_cast %v819 : i32 to index
%v822 = arith.constant 1 : index
%v823 = arith.constant -1 : index
%v824 = arith.cmpi sle, %v820, %v821 : index
%v825 = arith.select %v824, %v822, %v823 : index
cf.br ^b28(%v820 : index)
^b28(%v826: index):
%v827 = arith.cmpi slt, %v826, %v821 : index
%v828 = arith.cmpi sgt, %v826, %v821 : index
%v829 = arith.select %v824, %v827, %v828 : i1
cf.cond_br %v829, ^b29(%v826 : index), ^b30(%v826 : index)
^b29(%v830: index):
%v831 = llvm.load %v769 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v832 = llvm.getelementptr %v769[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v833 = llvm.load %v832 : !llvm.ptr -> !llvm.ptr
%v834 = arith.index_cast %v830 : index to i64
%v835 = llvm.getelementptr %v833[%v834] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v836 = llvm.load %v835 : !llvm.ptr -> f32
%v837 = llvm.load %v784 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v838 = llvm.getelementptr %v784[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v839 = llvm.load %v838 : !llvm.ptr -> !llvm.ptr
%v840 = arith.index_cast %v830 : index to i64
%v841 = llvm.getelementptr %v839[%v840] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v842 = llvm.load %v841 : !llvm.ptr -> f32
%v843 = arith.mulf %v836, %v842 : f32
%v844 = llvm.load %v815 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v845 = llvm.getelementptr %v815[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v846 = llvm.load %v845 : !llvm.ptr -> !llvm.ptr
%v847 = arith.index_cast %v830 : index to i64
%v848 = llvm.getelementptr %v846[%v847] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v843, %v848 : f32, !llvm.ptr
%v849 = arith.addi %v830, %v825 : index
cf.br ^b28(%v849 : index)
^b30(%v850: index):
%v851 = llvm.load %v815 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v852 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v853 = llvm.extractvalue %v851[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v854 = llvm.insertvalue %v853, %v852[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v855 = llvm.extractvalue %v851[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v856 = llvm.insertvalue %v855, %v854[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v857 = llvm.extractvalue %v851[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v858 = llvm.insertvalue %v857, %v856[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v859 = llvm.extractvalue %v851[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v860 = llvm.insertvalue %v859, %v858[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v861 = llvm.extractvalue %v851[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v862 = llvm.insertvalue %v861, %v860[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v863 = llvm.extractvalue %v851[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v864 = llvm.insertvalue %v863, %v862[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v865 = llvm.mlir.constant(1 : i64) : i64
%v866 = llvm.alloca %v865 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v864, %v866 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v867 = llvm.load %v866 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v867 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_div(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v868 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v869 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v870 = llvm.insertvalue %v869, %v868[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v871 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v872 = llvm.insertvalue %v871, %v870[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v873 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v874 = llvm.insertvalue %v873, %v872[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v875 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v876 = llvm.insertvalue %v875, %v874[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v877 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v878 = llvm.insertvalue %v877, %v876[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v879 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v880 = llvm.insertvalue %v879, %v878[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v881 = llvm.mlir.constant(1 : i64) : i64
%v882 = llvm.alloca %v881 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v880, %v882 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v883 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v884 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v885 = llvm.insertvalue %v884, %v883[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v886 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v887 = llvm.insertvalue %v886, %v885[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v888 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v889 = llvm.insertvalue %v888, %v887[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v890 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v891 = llvm.insertvalue %v890, %v889[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v892 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v893 = llvm.insertvalue %v892, %v891[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v894 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v895 = llvm.insertvalue %v894, %v893[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v896 = llvm.mlir.constant(1 : i64) : i64
%v897 = llvm.alloca %v896 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v895, %v897 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v898 = llvm.load %v882 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v899 = llvm.getelementptr %v882[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v900 = llvm.load %v899 : !llvm.ptr -> i32
%v901 = llvm.load %v882 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v902 = llvm.getelementptr %v882[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v903 = llvm.load %v902 : !llvm.ptr -> i32
%v904 = llvm.load %v882 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v905 = llvm.getelementptr %v882[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v906 = llvm.load %v905 : !llvm.ptr -> i32
%v907 = llvm.load %v882 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v908 = llvm.getelementptr %v882[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v909 = llvm.load %v908 : !llvm.ptr -> i32
%v910 = func.call @tensor_zeros(%v909, %v906, %v903, %v900) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v911 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v912 = llvm.extractvalue %v910[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v913 = llvm.insertvalue %v912, %v911[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v914 = llvm.extractvalue %v910[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v915 = llvm.insertvalue %v914, %v913[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v916 = llvm.extractvalue %v910[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v917 = llvm.insertvalue %v916, %v915[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v918 = llvm.extractvalue %v910[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v919 = llvm.insertvalue %v918, %v917[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v920 = llvm.extractvalue %v910[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v921 = llvm.insertvalue %v920, %v919[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v922 = llvm.extractvalue %v910[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v923 = llvm.insertvalue %v922, %v921[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v924 = llvm.mlir.constant(1 : i64) : i64
%v925 = llvm.alloca %v924 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v923, %v925 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v926 = llvm.load %v925 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v927 = llvm.mlir.constant(1 : i64) : i64
%v928 = llvm.alloca %v927 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v926, %v928 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v929 = arith.constant 0 : i32
%v930 = llvm.load %v882 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v931 = llvm.getelementptr %v882[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v932 = llvm.load %v931 : !llvm.ptr -> i32
%v933 = arith.index_cast %v929 : i32 to index
%v934 = arith.index_cast %v932 : i32 to index
%v935 = arith.constant 1 : index
%v936 = arith.constant -1 : index
%v937 = arith.cmpi sle, %v933, %v934 : index
%v938 = arith.select %v937, %v935, %v936 : index
cf.br ^b31(%v933 : index)
^b31(%v939: index):
%v940 = arith.cmpi slt, %v939, %v934 : index
%v941 = arith.cmpi sgt, %v939, %v934 : index
%v942 = arith.select %v937, %v940, %v941 : i1
cf.cond_br %v942, ^b32(%v939 : index), ^b33(%v939 : index)
^b32(%v943: index):
%v944 = llvm.load %v882 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v945 = llvm.getelementptr %v882[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v946 = llvm.load %v945 : !llvm.ptr -> !llvm.ptr
%v947 = arith.index_cast %v943 : index to i64
%v948 = llvm.getelementptr %v946[%v947] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v949 = llvm.load %v948 : !llvm.ptr -> f32
%v950 = llvm.load %v897 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v951 = llvm.getelementptr %v897[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v952 = llvm.load %v951 : !llvm.ptr -> !llvm.ptr
%v953 = arith.index_cast %v943 : index to i64
%v954 = llvm.getelementptr %v952[%v953] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v955 = llvm.load %v954 : !llvm.ptr -> f32
%v956 = arith.divf %v949, %v955 : f32
%v957 = llvm.load %v928 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v958 = llvm.getelementptr %v928[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v959 = llvm.load %v958 : !llvm.ptr -> !llvm.ptr
%v960 = arith.index_cast %v943 : index to i64
%v961 = llvm.getelementptr %v959[%v960] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v956, %v961 : f32, !llvm.ptr
%v962 = arith.addi %v943, %v938 : index
cf.br ^b31(%v962 : index)
^b33(%v963: index):
%v964 = llvm.load %v928 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v965 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v966 = llvm.extractvalue %v964[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v967 = llvm.insertvalue %v966, %v965[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v968 = llvm.extractvalue %v964[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v969 = llvm.insertvalue %v968, %v967[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v970 = llvm.extractvalue %v964[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v971 = llvm.insertvalue %v970, %v969[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v972 = llvm.extractvalue %v964[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v973 = llvm.insertvalue %v972, %v971[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v974 = llvm.extractvalue %v964[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v975 = llvm.insertvalue %v974, %v973[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v976 = llvm.extractvalue %v964[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v977 = llvm.insertvalue %v976, %v975[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v978 = llvm.mlir.constant(1 : i64) : i64
%v979 = llvm.alloca %v978 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v977, %v979 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v980 = llvm.load %v979 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v980 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_scale(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: f32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v981 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v982 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v983 = llvm.insertvalue %v982, %v981[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v984 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v985 = llvm.insertvalue %v984, %v983[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v986 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v987 = llvm.insertvalue %v986, %v985[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v988 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v989 = llvm.insertvalue %v988, %v987[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v990 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v991 = llvm.insertvalue %v990, %v989[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v992 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v993 = llvm.insertvalue %v992, %v991[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v994 = llvm.mlir.constant(1 : i64) : i64
%v995 = llvm.alloca %v994 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v993, %v995 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v996 = llvm.load %v995 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v997 = llvm.getelementptr %v995[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v998 = llvm.load %v997 : !llvm.ptr -> i32
%v999 = llvm.load %v995 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1000 = llvm.getelementptr %v995[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1001 = llvm.load %v1000 : !llvm.ptr -> i32
%v1002 = llvm.load %v995 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1003 = llvm.getelementptr %v995[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1004 = llvm.load %v1003 : !llvm.ptr -> i32
%v1005 = llvm.load %v995 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1006 = llvm.getelementptr %v995[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1007 = llvm.load %v1006 : !llvm.ptr -> i32
%v1008 = func.call @tensor_zeros(%v1007, %v1004, %v1001, %v998) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1009 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1010 = llvm.extractvalue %v1008[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1011 = llvm.insertvalue %v1010, %v1009[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1012 = llvm.extractvalue %v1008[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1013 = llvm.insertvalue %v1012, %v1011[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1014 = llvm.extractvalue %v1008[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1015 = llvm.insertvalue %v1014, %v1013[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1016 = llvm.extractvalue %v1008[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1017 = llvm.insertvalue %v1016, %v1015[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1018 = llvm.extractvalue %v1008[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1019 = llvm.insertvalue %v1018, %v1017[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1020 = llvm.extractvalue %v1008[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1021 = llvm.insertvalue %v1020, %v1019[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1022 = llvm.mlir.constant(1 : i64) : i64
%v1023 = llvm.alloca %v1022 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1021, %v1023 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1024 = llvm.load %v1023 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1025 = llvm.mlir.constant(1 : i64) : i64
%v1026 = llvm.alloca %v1025 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1024, %v1026 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1027 = arith.constant 0 : i32
%v1028 = llvm.load %v995 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1029 = llvm.getelementptr %v995[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1030 = llvm.load %v1029 : !llvm.ptr -> i32
%v1031 = arith.index_cast %v1027 : i32 to index
%v1032 = arith.index_cast %v1030 : i32 to index
%v1033 = arith.constant 1 : index
%v1034 = arith.constant -1 : index
%v1035 = arith.cmpi sle, %v1031, %v1032 : index
%v1036 = arith.select %v1035, %v1033, %v1034 : index
cf.br ^b34(%v1031 : index)
^b34(%v1037: index):
%v1038 = arith.cmpi slt, %v1037, %v1032 : index
%v1039 = arith.cmpi sgt, %v1037, %v1032 : index
%v1040 = arith.select %v1035, %v1038, %v1039 : i1
cf.cond_br %v1040, ^b35(%v1037 : index), ^b36(%v1037 : index)
^b35(%v1041: index):
%v1042 = llvm.load %v995 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1043 = llvm.getelementptr %v995[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1044 = llvm.load %v1043 : !llvm.ptr -> !llvm.ptr
%v1045 = arith.index_cast %v1041 : index to i64
%v1046 = llvm.getelementptr %v1044[%v1045] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1047 = llvm.load %v1046 : !llvm.ptr -> f32
%v1048 = arith.mulf %v1047, %arg1 : f32
%v1049 = llvm.load %v1026 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1050 = llvm.getelementptr %v1026[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1051 = llvm.load %v1050 : !llvm.ptr -> !llvm.ptr
%v1052 = arith.index_cast %v1041 : index to i64
%v1053 = llvm.getelementptr %v1051[%v1052] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1048, %v1053 : f32, !llvm.ptr
%v1054 = arith.addi %v1041, %v1036 : index
cf.br ^b34(%v1054 : index)
^b36(%v1055: index):
%v1056 = llvm.load %v1026 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1057 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1058 = llvm.extractvalue %v1056[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1059 = llvm.insertvalue %v1058, %v1057[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1060 = llvm.extractvalue %v1056[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1061 = llvm.insertvalue %v1060, %v1059[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1062 = llvm.extractvalue %v1056[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1063 = llvm.insertvalue %v1062, %v1061[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1064 = llvm.extractvalue %v1056[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1065 = llvm.insertvalue %v1064, %v1063[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1066 = llvm.extractvalue %v1056[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1067 = llvm.insertvalue %v1066, %v1065[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1068 = llvm.extractvalue %v1056[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1069 = llvm.insertvalue %v1068, %v1067[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1070 = llvm.mlir.constant(1 : i64) : i64
%v1071 = llvm.alloca %v1070 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1069, %v1071 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1072 = llvm.load %v1071 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1072 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_add_scalar(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: f32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1073 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1074 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1075 = llvm.insertvalue %v1074, %v1073[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1076 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1077 = llvm.insertvalue %v1076, %v1075[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1078 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1079 = llvm.insertvalue %v1078, %v1077[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1080 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1081 = llvm.insertvalue %v1080, %v1079[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1082 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1083 = llvm.insertvalue %v1082, %v1081[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1084 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1085 = llvm.insertvalue %v1084, %v1083[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1086 = llvm.mlir.constant(1 : i64) : i64
%v1087 = llvm.alloca %v1086 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1085, %v1087 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1088 = llvm.load %v1087 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1089 = llvm.getelementptr %v1087[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1090 = llvm.load %v1089 : !llvm.ptr -> i32
%v1091 = llvm.load %v1087 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1092 = llvm.getelementptr %v1087[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1093 = llvm.load %v1092 : !llvm.ptr -> i32
%v1094 = llvm.load %v1087 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1095 = llvm.getelementptr %v1087[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1096 = llvm.load %v1095 : !llvm.ptr -> i32
%v1097 = llvm.load %v1087 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1098 = llvm.getelementptr %v1087[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1099 = llvm.load %v1098 : !llvm.ptr -> i32
%v1100 = func.call @tensor_zeros(%v1099, %v1096, %v1093, %v1090) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1101 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1102 = llvm.extractvalue %v1100[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1103 = llvm.insertvalue %v1102, %v1101[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1104 = llvm.extractvalue %v1100[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1105 = llvm.insertvalue %v1104, %v1103[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1106 = llvm.extractvalue %v1100[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1107 = llvm.insertvalue %v1106, %v1105[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1108 = llvm.extractvalue %v1100[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1109 = llvm.insertvalue %v1108, %v1107[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1110 = llvm.extractvalue %v1100[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1111 = llvm.insertvalue %v1110, %v1109[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1112 = llvm.extractvalue %v1100[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1113 = llvm.insertvalue %v1112, %v1111[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1114 = llvm.mlir.constant(1 : i64) : i64
%v1115 = llvm.alloca %v1114 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1113, %v1115 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1116 = llvm.load %v1115 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1117 = llvm.mlir.constant(1 : i64) : i64
%v1118 = llvm.alloca %v1117 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1116, %v1118 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1119 = arith.constant 0 : i32
%v1120 = llvm.load %v1087 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1121 = llvm.getelementptr %v1087[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1122 = llvm.load %v1121 : !llvm.ptr -> i32
%v1123 = arith.index_cast %v1119 : i32 to index
%v1124 = arith.index_cast %v1122 : i32 to index
%v1125 = arith.constant 1 : index
%v1126 = arith.constant -1 : index
%v1127 = arith.cmpi sle, %v1123, %v1124 : index
%v1128 = arith.select %v1127, %v1125, %v1126 : index
cf.br ^b37(%v1123 : index)
^b37(%v1129: index):
%v1130 = arith.cmpi slt, %v1129, %v1124 : index
%v1131 = arith.cmpi sgt, %v1129, %v1124 : index
%v1132 = arith.select %v1127, %v1130, %v1131 : i1
cf.cond_br %v1132, ^b38(%v1129 : index), ^b39(%v1129 : index)
^b38(%v1133: index):
%v1134 = llvm.load %v1087 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1135 = llvm.getelementptr %v1087[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1136 = llvm.load %v1135 : !llvm.ptr -> !llvm.ptr
%v1137 = arith.index_cast %v1133 : index to i64
%v1138 = llvm.getelementptr %v1136[%v1137] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1139 = llvm.load %v1138 : !llvm.ptr -> f32
%v1140 = arith.addf %v1139, %arg1 : f32
%v1141 = llvm.load %v1118 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1142 = llvm.getelementptr %v1118[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1143 = llvm.load %v1142 : !llvm.ptr -> !llvm.ptr
%v1144 = arith.index_cast %v1133 : index to i64
%v1145 = llvm.getelementptr %v1143[%v1144] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1140, %v1145 : f32, !llvm.ptr
%v1146 = arith.addi %v1133, %v1128 : index
cf.br ^b37(%v1146 : index)
^b39(%v1147: index):
%v1148 = llvm.load %v1118 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1149 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1150 = llvm.extractvalue %v1148[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1151 = llvm.insertvalue %v1150, %v1149[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1152 = llvm.extractvalue %v1148[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1153 = llvm.insertvalue %v1152, %v1151[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1154 = llvm.extractvalue %v1148[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1155 = llvm.insertvalue %v1154, %v1153[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1156 = llvm.extractvalue %v1148[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1157 = llvm.insertvalue %v1156, %v1155[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1158 = llvm.extractvalue %v1148[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1159 = llvm.insertvalue %v1158, %v1157[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1160 = llvm.extractvalue %v1148[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1161 = llvm.insertvalue %v1160, %v1159[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1162 = llvm.mlir.constant(1 : i64) : i64
%v1163 = llvm.alloca %v1162 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1161, %v1163 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1164 = llvm.load %v1163 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1164 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_neg(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1165 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1166 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1167 = llvm.insertvalue %v1166, %v1165[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1168 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1169 = llvm.insertvalue %v1168, %v1167[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1170 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1171 = llvm.insertvalue %v1170, %v1169[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1172 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1173 = llvm.insertvalue %v1172, %v1171[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1174 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1175 = llvm.insertvalue %v1174, %v1173[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1176 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1177 = llvm.insertvalue %v1176, %v1175[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1178 = llvm.mlir.constant(1 : i64) : i64
%v1179 = llvm.alloca %v1178 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1177, %v1179 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1180 = llvm.load %v1179 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1181 = llvm.getelementptr %v1179[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1182 = llvm.load %v1181 : !llvm.ptr -> i32
%v1183 = llvm.load %v1179 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1184 = llvm.getelementptr %v1179[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1185 = llvm.load %v1184 : !llvm.ptr -> i32
%v1186 = llvm.load %v1179 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1187 = llvm.getelementptr %v1179[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1188 = llvm.load %v1187 : !llvm.ptr -> i32
%v1189 = llvm.load %v1179 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1190 = llvm.getelementptr %v1179[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1191 = llvm.load %v1190 : !llvm.ptr -> i32
%v1192 = func.call @tensor_zeros(%v1191, %v1188, %v1185, %v1182) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1193 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1194 = llvm.extractvalue %v1192[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1195 = llvm.insertvalue %v1194, %v1193[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1196 = llvm.extractvalue %v1192[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1197 = llvm.insertvalue %v1196, %v1195[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1198 = llvm.extractvalue %v1192[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1199 = llvm.insertvalue %v1198, %v1197[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1200 = llvm.extractvalue %v1192[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1201 = llvm.insertvalue %v1200, %v1199[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1202 = llvm.extractvalue %v1192[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1203 = llvm.insertvalue %v1202, %v1201[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1204 = llvm.extractvalue %v1192[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1205 = llvm.insertvalue %v1204, %v1203[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1206 = llvm.mlir.constant(1 : i64) : i64
%v1207 = llvm.alloca %v1206 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1205, %v1207 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1208 = llvm.load %v1207 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1209 = llvm.mlir.constant(1 : i64) : i64
%v1210 = llvm.alloca %v1209 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1208, %v1210 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1211 = arith.constant 0 : i32
%v1212 = llvm.load %v1179 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1213 = llvm.getelementptr %v1179[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1214 = llvm.load %v1213 : !llvm.ptr -> i32
%v1215 = arith.index_cast %v1211 : i32 to index
%v1216 = arith.index_cast %v1214 : i32 to index
%v1217 = arith.constant 1 : index
%v1218 = arith.constant -1 : index
%v1219 = arith.cmpi sle, %v1215, %v1216 : index
%v1220 = arith.select %v1219, %v1217, %v1218 : index
cf.br ^b40(%v1215 : index)
^b40(%v1221: index):
%v1222 = arith.cmpi slt, %v1221, %v1216 : index
%v1223 = arith.cmpi sgt, %v1221, %v1216 : index
%v1224 = arith.select %v1219, %v1222, %v1223 : i1
cf.cond_br %v1224, ^b41(%v1221 : index), ^b42(%v1221 : index)
^b41(%v1225: index):
%v1226 = arith.constant 0.0 : f32
%v1227 = llvm.load %v1179 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1228 = llvm.getelementptr %v1179[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1229 = llvm.load %v1228 : !llvm.ptr -> !llvm.ptr
%v1230 = arith.index_cast %v1225 : index to i64
%v1231 = llvm.getelementptr %v1229[%v1230] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1232 = llvm.load %v1231 : !llvm.ptr -> f32
%v1233 = arith.subf %v1226, %v1232 : f32
%v1234 = llvm.load %v1210 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1235 = llvm.getelementptr %v1210[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1236 = llvm.load %v1235 : !llvm.ptr -> !llvm.ptr
%v1237 = arith.index_cast %v1225 : index to i64
%v1238 = llvm.getelementptr %v1236[%v1237] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1233, %v1238 : f32, !llvm.ptr
%v1239 = arith.addi %v1225, %v1220 : index
cf.br ^b40(%v1239 : index)
^b42(%v1240: index):
%v1241 = llvm.load %v1210 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1242 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1243 = llvm.extractvalue %v1241[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1244 = llvm.insertvalue %v1243, %v1242[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1245 = llvm.extractvalue %v1241[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1246 = llvm.insertvalue %v1245, %v1244[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1247 = llvm.extractvalue %v1241[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1248 = llvm.insertvalue %v1247, %v1246[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1249 = llvm.extractvalue %v1241[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1250 = llvm.insertvalue %v1249, %v1248[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1251 = llvm.extractvalue %v1241[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1252 = llvm.insertvalue %v1251, %v1250[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1253 = llvm.extractvalue %v1241[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1254 = llvm.insertvalue %v1253, %v1252[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1255 = llvm.mlir.constant(1 : i64) : i64
%v1256 = llvm.alloca %v1255 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1254, %v1256 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1257 = llvm.load %v1256 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1257 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_relu(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1258 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1259 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1260 = llvm.insertvalue %v1259, %v1258[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1261 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1262 = llvm.insertvalue %v1261, %v1260[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1263 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1264 = llvm.insertvalue %v1263, %v1262[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1265 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1266 = llvm.insertvalue %v1265, %v1264[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1267 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1268 = llvm.insertvalue %v1267, %v1266[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1269 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1270 = llvm.insertvalue %v1269, %v1268[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1271 = llvm.mlir.constant(1 : i64) : i64
%v1272 = llvm.alloca %v1271 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1270, %v1272 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1273 = llvm.load %v1272 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1274 = llvm.getelementptr %v1272[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1275 = llvm.load %v1274 : !llvm.ptr -> i32
%v1276 = llvm.load %v1272 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1277 = llvm.getelementptr %v1272[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1278 = llvm.load %v1277 : !llvm.ptr -> i32
%v1279 = llvm.load %v1272 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1280 = llvm.getelementptr %v1272[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1281 = llvm.load %v1280 : !llvm.ptr -> i32
%v1282 = llvm.load %v1272 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1283 = llvm.getelementptr %v1272[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1284 = llvm.load %v1283 : !llvm.ptr -> i32
%v1285 = func.call @tensor_zeros(%v1284, %v1281, %v1278, %v1275) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1286 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1287 = llvm.extractvalue %v1285[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1288 = llvm.insertvalue %v1287, %v1286[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1289 = llvm.extractvalue %v1285[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1290 = llvm.insertvalue %v1289, %v1288[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1291 = llvm.extractvalue %v1285[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1292 = llvm.insertvalue %v1291, %v1290[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1293 = llvm.extractvalue %v1285[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1294 = llvm.insertvalue %v1293, %v1292[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1295 = llvm.extractvalue %v1285[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1296 = llvm.insertvalue %v1295, %v1294[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1297 = llvm.extractvalue %v1285[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1298 = llvm.insertvalue %v1297, %v1296[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1299 = llvm.mlir.constant(1 : i64) : i64
%v1300 = llvm.alloca %v1299 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1298, %v1300 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1301 = llvm.load %v1300 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1302 = llvm.mlir.constant(1 : i64) : i64
%v1303 = llvm.alloca %v1302 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1301, %v1303 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1304 = arith.constant 0 : i32
%v1305 = llvm.load %v1272 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1306 = llvm.getelementptr %v1272[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1307 = llvm.load %v1306 : !llvm.ptr -> i32
%v1308 = arith.index_cast %v1304 : i32 to index
%v1309 = arith.index_cast %v1307 : i32 to index
%v1310 = arith.constant 1 : index
%v1311 = arith.constant -1 : index
%v1312 = arith.cmpi sle, %v1308, %v1309 : index
%v1313 = arith.select %v1312, %v1310, %v1311 : index
cf.br ^b43(%v1308 : index)
^b43(%v1314: index):
%v1315 = arith.cmpi slt, %v1314, %v1309 : index
%v1316 = arith.cmpi sgt, %v1314, %v1309 : index
%v1317 = arith.select %v1312, %v1315, %v1316 : i1
cf.cond_br %v1317, ^b44(%v1314 : index), ^b45(%v1314 : index)
^b44(%v1318: index):
%v1319 = llvm.load %v1272 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1320 = llvm.getelementptr %v1272[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1321 = llvm.load %v1320 : !llvm.ptr -> !llvm.ptr
%v1322 = arith.index_cast %v1318 : index to i64
%v1323 = llvm.getelementptr %v1321[%v1322] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1324 = llvm.load %v1323 : !llvm.ptr -> f32
%v1325 = arith.constant 0.0 : f32
%v1326 = arith.cmpf ogt, %v1324, %v1325 : f32
cf.cond_br %v1326, ^b46, ^b47
^b46:
%v1327 = llvm.load %v1272 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1328 = llvm.getelementptr %v1272[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1329 = llvm.load %v1328 : !llvm.ptr -> !llvm.ptr
%v1330 = arith.index_cast %v1318 : index to i64
%v1331 = llvm.getelementptr %v1329[%v1330] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1332 = llvm.load %v1331 : !llvm.ptr -> f32
%v1333 = llvm.load %v1303 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1334 = llvm.getelementptr %v1303[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1335 = llvm.load %v1334 : !llvm.ptr -> !llvm.ptr
%v1336 = arith.index_cast %v1318 : index to i64
%v1337 = llvm.getelementptr %v1335[%v1336] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1332, %v1337 : f32, !llvm.ptr
cf.br ^b48
^b47:
%v1338 = arith.constant 0.0 : f32
%v1339 = llvm.load %v1303 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1340 = llvm.getelementptr %v1303[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1341 = llvm.load %v1340 : !llvm.ptr -> !llvm.ptr
%v1342 = arith.index_cast %v1318 : index to i64
%v1343 = llvm.getelementptr %v1341[%v1342] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1338, %v1343 : f32, !llvm.ptr
cf.br ^b48
^b48:
%v1344 = arith.addi %v1318, %v1313 : index
cf.br ^b43(%v1344 : index)
^b45(%v1345: index):
%v1346 = llvm.load %v1303 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1347 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1348 = llvm.extractvalue %v1346[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1349 = llvm.insertvalue %v1348, %v1347[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1350 = llvm.extractvalue %v1346[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1351 = llvm.insertvalue %v1350, %v1349[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1352 = llvm.extractvalue %v1346[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1353 = llvm.insertvalue %v1352, %v1351[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1354 = llvm.extractvalue %v1346[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1355 = llvm.insertvalue %v1354, %v1353[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1356 = llvm.extractvalue %v1346[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1357 = llvm.insertvalue %v1356, %v1355[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1358 = llvm.extractvalue %v1346[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1359 = llvm.insertvalue %v1358, %v1357[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1360 = llvm.mlir.constant(1 : i64) : i64
%v1361 = llvm.alloca %v1360 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1359, %v1361 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1362 = llvm.load %v1361 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1362 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_sigmoid(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1363 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1364 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1365 = llvm.insertvalue %v1364, %v1363[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1366 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1367 = llvm.insertvalue %v1366, %v1365[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1368 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1369 = llvm.insertvalue %v1368, %v1367[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1370 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1371 = llvm.insertvalue %v1370, %v1369[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1372 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1373 = llvm.insertvalue %v1372, %v1371[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1374 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1375 = llvm.insertvalue %v1374, %v1373[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1376 = llvm.mlir.constant(1 : i64) : i64
%v1377 = llvm.alloca %v1376 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1375, %v1377 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1378 = llvm.load %v1377 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1379 = llvm.getelementptr %v1377[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1380 = llvm.load %v1379 : !llvm.ptr -> i32
%v1381 = llvm.load %v1377 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1382 = llvm.getelementptr %v1377[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1383 = llvm.load %v1382 : !llvm.ptr -> i32
%v1384 = llvm.load %v1377 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1385 = llvm.getelementptr %v1377[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1386 = llvm.load %v1385 : !llvm.ptr -> i32
%v1387 = llvm.load %v1377 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1388 = llvm.getelementptr %v1377[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1389 = llvm.load %v1388 : !llvm.ptr -> i32
%v1390 = func.call @tensor_zeros(%v1389, %v1386, %v1383, %v1380) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1391 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1392 = llvm.extractvalue %v1390[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1393 = llvm.insertvalue %v1392, %v1391[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1394 = llvm.extractvalue %v1390[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1395 = llvm.insertvalue %v1394, %v1393[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1396 = llvm.extractvalue %v1390[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1397 = llvm.insertvalue %v1396, %v1395[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1398 = llvm.extractvalue %v1390[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1399 = llvm.insertvalue %v1398, %v1397[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1400 = llvm.extractvalue %v1390[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1401 = llvm.insertvalue %v1400, %v1399[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1402 = llvm.extractvalue %v1390[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1403 = llvm.insertvalue %v1402, %v1401[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1404 = llvm.mlir.constant(1 : i64) : i64
%v1405 = llvm.alloca %v1404 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1403, %v1405 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1406 = llvm.load %v1405 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1407 = llvm.mlir.constant(1 : i64) : i64
%v1408 = llvm.alloca %v1407 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1406, %v1408 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1409 = arith.constant 0 : i32
%v1410 = llvm.load %v1377 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1411 = llvm.getelementptr %v1377[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1412 = llvm.load %v1411 : !llvm.ptr -> i32
%v1413 = arith.index_cast %v1409 : i32 to index
%v1414 = arith.index_cast %v1412 : i32 to index
%v1415 = arith.constant 1 : index
%v1416 = arith.constant -1 : index
%v1417 = arith.cmpi sle, %v1413, %v1414 : index
%v1418 = arith.select %v1417, %v1415, %v1416 : index
cf.br ^b49(%v1413 : index)
^b49(%v1419: index):
%v1420 = arith.cmpi slt, %v1419, %v1414 : index
%v1421 = arith.cmpi sgt, %v1419, %v1414 : index
%v1422 = arith.select %v1417, %v1420, %v1421 : i1
cf.cond_br %v1422, ^b50(%v1419 : index), ^b51(%v1419 : index)
^b50(%v1423: index):
%v1424 = arith.constant 0.0 : f32
%v1425 = llvm.load %v1377 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1426 = llvm.getelementptr %v1377[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1427 = llvm.load %v1426 : !llvm.ptr -> !llvm.ptr
%v1428 = arith.index_cast %v1423 : index to i64
%v1429 = llvm.getelementptr %v1427[%v1428] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1430 = llvm.load %v1429 : !llvm.ptr -> f32
%v1431 = arith.subf %v1424, %v1430 : f32
%v1432 = arith.extf %v1431 : f32 to f64
%v1433 = func.call @exp(%v1432) : (f64) -> f64
%v1434 = arith.constant 1.0 : f32
%v1435 = arith.constant 1.0 : f32
%v1436 = arith.extf %v1435 : f32 to f64
%v1437 = arith.addf %v1436, %v1433 : f64
%v1438 = arith.extf %v1434 : f32 to f64
%v1439 = arith.divf %v1438, %v1437 : f64
%v1440 = llvm.load %v1408 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1441 = llvm.getelementptr %v1408[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1442 = llvm.load %v1441 : !llvm.ptr -> !llvm.ptr
%v1443 = arith.truncf %v1439 : f64 to f32
%v1444 = arith.index_cast %v1423 : index to i64
%v1445 = llvm.getelementptr %v1442[%v1444] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1443, %v1445 : f32, !llvm.ptr
%v1446 = arith.addi %v1423, %v1418 : index
cf.br ^b49(%v1446 : index)
^b51(%v1447: index):
%v1448 = llvm.load %v1408 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1449 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1450 = llvm.extractvalue %v1448[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1451 = llvm.insertvalue %v1450, %v1449[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1452 = llvm.extractvalue %v1448[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1453 = llvm.insertvalue %v1452, %v1451[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1454 = llvm.extractvalue %v1448[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1455 = llvm.insertvalue %v1454, %v1453[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1456 = llvm.extractvalue %v1448[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1457 = llvm.insertvalue %v1456, %v1455[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1458 = llvm.extractvalue %v1448[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1459 = llvm.insertvalue %v1458, %v1457[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1460 = llvm.extractvalue %v1448[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1461 = llvm.insertvalue %v1460, %v1459[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1462 = llvm.mlir.constant(1 : i64) : i64
%v1463 = llvm.alloca %v1462 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1461, %v1463 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1464 = llvm.load %v1463 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1464 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_tanh(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1465 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1466 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1467 = llvm.insertvalue %v1466, %v1465[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1468 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1469 = llvm.insertvalue %v1468, %v1467[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1470 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1471 = llvm.insertvalue %v1470, %v1469[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1472 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1473 = llvm.insertvalue %v1472, %v1471[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1474 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1475 = llvm.insertvalue %v1474, %v1473[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1476 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1477 = llvm.insertvalue %v1476, %v1475[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1478 = llvm.mlir.constant(1 : i64) : i64
%v1479 = llvm.alloca %v1478 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1477, %v1479 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1480 = llvm.load %v1479 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1481 = llvm.getelementptr %v1479[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1482 = llvm.load %v1481 : !llvm.ptr -> i32
%v1483 = llvm.load %v1479 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1484 = llvm.getelementptr %v1479[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1485 = llvm.load %v1484 : !llvm.ptr -> i32
%v1486 = llvm.load %v1479 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1487 = llvm.getelementptr %v1479[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1488 = llvm.load %v1487 : !llvm.ptr -> i32
%v1489 = llvm.load %v1479 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1490 = llvm.getelementptr %v1479[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1491 = llvm.load %v1490 : !llvm.ptr -> i32
%v1492 = func.call @tensor_zeros(%v1491, %v1488, %v1485, %v1482) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1493 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1494 = llvm.extractvalue %v1492[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1495 = llvm.insertvalue %v1494, %v1493[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1496 = llvm.extractvalue %v1492[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1497 = llvm.insertvalue %v1496, %v1495[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1498 = llvm.extractvalue %v1492[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1499 = llvm.insertvalue %v1498, %v1497[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1500 = llvm.extractvalue %v1492[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1501 = llvm.insertvalue %v1500, %v1499[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1502 = llvm.extractvalue %v1492[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1503 = llvm.insertvalue %v1502, %v1501[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1504 = llvm.extractvalue %v1492[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1505 = llvm.insertvalue %v1504, %v1503[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1506 = llvm.mlir.constant(1 : i64) : i64
%v1507 = llvm.alloca %v1506 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1505, %v1507 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1508 = llvm.load %v1507 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1509 = llvm.mlir.constant(1 : i64) : i64
%v1510 = llvm.alloca %v1509 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1508, %v1510 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1511 = arith.constant 0 : i32
%v1512 = llvm.load %v1479 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1513 = llvm.getelementptr %v1479[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1514 = llvm.load %v1513 : !llvm.ptr -> i32
%v1515 = arith.index_cast %v1511 : i32 to index
%v1516 = arith.index_cast %v1514 : i32 to index
%v1517 = arith.constant 1 : index
%v1518 = arith.constant -1 : index
%v1519 = arith.cmpi sle, %v1515, %v1516 : index
%v1520 = arith.select %v1519, %v1517, %v1518 : index
cf.br ^b52(%v1515 : index)
^b52(%v1521: index):
%v1522 = arith.cmpi slt, %v1521, %v1516 : index
%v1523 = arith.cmpi sgt, %v1521, %v1516 : index
%v1524 = arith.select %v1519, %v1522, %v1523 : i1
cf.cond_br %v1524, ^b53(%v1521 : index), ^b54(%v1521 : index)
^b53(%v1525: index):
%v1526 = llvm.load %v1479 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1527 = llvm.getelementptr %v1479[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1528 = llvm.load %v1527 : !llvm.ptr -> !llvm.ptr
%v1529 = arith.index_cast %v1525 : index to i64
%v1530 = llvm.getelementptr %v1528[%v1529] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1531 = llvm.load %v1530 : !llvm.ptr -> f32
%v1532 = arith.extf %v1531 : f32 to f64
%v1533 = func.call @exp(%v1532) : (f64) -> f64
%v1534 = arith.constant 0.0 : f32
%v1535 = llvm.load %v1479 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1536 = llvm.getelementptr %v1479[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1537 = llvm.load %v1536 : !llvm.ptr -> !llvm.ptr
%v1538 = arith.index_cast %v1525 : index to i64
%v1539 = llvm.getelementptr %v1537[%v1538] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1540 = llvm.load %v1539 : !llvm.ptr -> f32
%v1541 = arith.subf %v1534, %v1540 : f32
%v1542 = arith.extf %v1541 : f32 to f64
%v1543 = func.call @exp(%v1542) : (f64) -> f64
%v1544 = arith.subf %v1533, %v1543 : f64
%v1545 = arith.addf %v1533, %v1543 : f64
%v1546 = arith.divf %v1544, %v1545 : f64
%v1547 = llvm.load %v1510 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1548 = llvm.getelementptr %v1510[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1549 = llvm.load %v1548 : !llvm.ptr -> !llvm.ptr
%v1550 = arith.truncf %v1546 : f64 to f32
%v1551 = arith.index_cast %v1525 : index to i64
%v1552 = llvm.getelementptr %v1549[%v1551] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1550, %v1552 : f32, !llvm.ptr
%v1553 = arith.addi %v1525, %v1520 : index
cf.br ^b52(%v1553 : index)
^b54(%v1554: index):
%v1555 = llvm.load %v1510 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1556 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1557 = llvm.extractvalue %v1555[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1558 = llvm.insertvalue %v1557, %v1556[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1559 = llvm.extractvalue %v1555[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1560 = llvm.insertvalue %v1559, %v1558[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1561 = llvm.extractvalue %v1555[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1562 = llvm.insertvalue %v1561, %v1560[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1563 = llvm.extractvalue %v1555[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1564 = llvm.insertvalue %v1563, %v1562[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1565 = llvm.extractvalue %v1555[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1566 = llvm.insertvalue %v1565, %v1564[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1567 = llvm.extractvalue %v1555[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1568 = llvm.insertvalue %v1567, %v1566[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1569 = llvm.mlir.constant(1 : i64) : i64
%v1570 = llvm.alloca %v1569 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1568, %v1570 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1571 = llvm.load %v1570 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1571 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_softmax(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1572 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1573 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1574 = llvm.insertvalue %v1573, %v1572[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1575 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1576 = llvm.insertvalue %v1575, %v1574[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1577 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1578 = llvm.insertvalue %v1577, %v1576[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1579 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1580 = llvm.insertvalue %v1579, %v1578[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1581 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1582 = llvm.insertvalue %v1581, %v1580[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1583 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1584 = llvm.insertvalue %v1583, %v1582[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1585 = llvm.mlir.constant(1 : i64) : i64
%v1586 = llvm.alloca %v1585 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1584, %v1586 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1587 = arith.constant 1 : i32
%v1588 = arith.constant 1 : i32
%v1589 = llvm.load %v1586 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1590 = llvm.getelementptr %v1586[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1591 = llvm.load %v1590 : !llvm.ptr -> i32
%v1592 = llvm.load %v1586 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1593 = llvm.getelementptr %v1586[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1594 = llvm.load %v1593 : !llvm.ptr -> i32
%v1595 = func.call @tensor_zeros(%v1594, %v1591, %v1588, %v1587) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1596 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1597 = llvm.extractvalue %v1595[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1598 = llvm.insertvalue %v1597, %v1596[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1599 = llvm.extractvalue %v1595[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1600 = llvm.insertvalue %v1599, %v1598[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1601 = llvm.extractvalue %v1595[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1602 = llvm.insertvalue %v1601, %v1600[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1603 = llvm.extractvalue %v1595[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1604 = llvm.insertvalue %v1603, %v1602[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1605 = llvm.extractvalue %v1595[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1606 = llvm.insertvalue %v1605, %v1604[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1607 = llvm.extractvalue %v1595[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1608 = llvm.insertvalue %v1607, %v1606[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1609 = llvm.mlir.constant(1 : i64) : i64
%v1610 = llvm.alloca %v1609 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1608, %v1610 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1611 = llvm.load %v1610 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1612 = llvm.mlir.constant(1 : i64) : i64
%v1613 = llvm.alloca %v1612 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1611, %v1613 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1614 = arith.constant 0 : i32
%v1615 = llvm.load %v1586 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1616 = llvm.getelementptr %v1586[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1617 = llvm.load %v1616 : !llvm.ptr -> i32
%v1618 = arith.index_cast %v1614 : i32 to index
%v1619 = arith.index_cast %v1617 : i32 to index
%v1620 = arith.constant 1 : index
%v1621 = arith.constant -1 : index
%v1622 = arith.cmpi sle, %v1618, %v1619 : index
%v1623 = arith.select %v1622, %v1620, %v1621 : index
cf.br ^b55(%v1618 : index)
^b55(%v1624: index):
%v1625 = arith.cmpi slt, %v1624, %v1619 : index
%v1626 = arith.cmpi sgt, %v1624, %v1619 : index
%v1627 = arith.select %v1622, %v1625, %v1626 : i1
cf.cond_br %v1627, ^b56(%v1624 : index), ^b57(%v1624 : index)
^b56(%v1628: index):
%v1629 = llvm.load %v1586 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1630 = llvm.getelementptr %v1586[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1631 = llvm.load %v1630 : !llvm.ptr -> !llvm.ptr
%v1632 = llvm.load %v1586 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1633 = llvm.getelementptr %v1586[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1634 = llvm.load %v1633 : !llvm.ptr -> i32
%v1635 = arith.index_cast %v1628 : index to i32
%v1636 = arith.muli %v1635, %v1634 : i32
%v1637 = arith.extsi %v1636 : i32 to i64
%v1638 = llvm.getelementptr %v1631[%v1637] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1639 = llvm.load %v1638 : !llvm.ptr -> f32
%v1640 = llvm.mlir.constant(1 : i64) : i64
%v1641 = llvm.alloca %v1640 x f32 : (i64) -> !llvm.ptr
llvm.store %v1639, %v1641 : f32, !llvm.ptr
%v1642 = arith.constant 1 : i32
%v1643 = llvm.load %v1586 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1644 = llvm.getelementptr %v1586[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1645 = llvm.load %v1644 : !llvm.ptr -> i32
%v1646 = arith.index_cast %v1642 : i32 to index
%v1647 = arith.index_cast %v1645 : i32 to index
%v1648 = arith.constant 1 : index
%v1649 = arith.constant -1 : index
%v1650 = arith.cmpi sle, %v1646, %v1647 : index
%v1651 = arith.select %v1650, %v1648, %v1649 : index
cf.br ^b58(%v1646 : index)
^b58(%v1652: index):
%v1653 = arith.cmpi slt, %v1652, %v1647 : index
%v1654 = arith.cmpi sgt, %v1652, %v1647 : index
%v1655 = arith.select %v1650, %v1653, %v1654 : i1
cf.cond_br %v1655, ^b59(%v1652 : index), ^b60(%v1652 : index)
^b59(%v1656: index):
%v1657 = llvm.load %v1586 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1658 = llvm.getelementptr %v1586[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1659 = llvm.load %v1658 : !llvm.ptr -> !llvm.ptr
%v1660 = llvm.load %v1586 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1661 = llvm.getelementptr %v1586[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1662 = llvm.load %v1661 : !llvm.ptr -> i32
%v1663 = arith.index_cast %v1628 : index to i32
%v1664 = arith.muli %v1663, %v1662 : i32
%v1665 = arith.index_cast %v1656 : index to i32
%v1666 = arith.addi %v1664, %v1665 : i32
%v1667 = arith.extsi %v1666 : i32 to i64
%v1668 = llvm.getelementptr %v1659[%v1667] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1669 = llvm.load %v1668 : !llvm.ptr -> f32
%v1670 = llvm.load %v1641 : !llvm.ptr -> f32
%v1671 = arith.cmpf ogt, %v1669, %v1670 : f32
cf.cond_br %v1671, ^b61, ^b62
^b61:
%v1672 = llvm.load %v1586 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1673 = llvm.getelementptr %v1586[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1674 = llvm.load %v1673 : !llvm.ptr -> !llvm.ptr
%v1675 = llvm.load %v1586 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1676 = llvm.getelementptr %v1586[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1677 = llvm.load %v1676 : !llvm.ptr -> i32
%v1678 = arith.index_cast %v1628 : index to i32
%v1679 = arith.muli %v1678, %v1677 : i32
%v1680 = arith.index_cast %v1656 : index to i32
%v1681 = arith.addi %v1679, %v1680 : i32
%v1682 = arith.extsi %v1681 : i32 to i64
%v1683 = llvm.getelementptr %v1674[%v1682] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1684 = llvm.load %v1683 : !llvm.ptr -> f32
llvm.store %v1684, %v1641 : f32, !llvm.ptr
cf.br ^b63
^b62:
cf.br ^b63
^b63:
%v1685 = arith.addi %v1656, %v1651 : index
cf.br ^b58(%v1685 : index)
^b60(%v1686: index):
%v1687 = arith.constant 0.0 : f32
%v1688 = arith.extf %v1687 : f32 to f64
%v1689 = llvm.mlir.constant(1 : i64) : i64
%v1690 = llvm.alloca %v1689 x f64 : (i64) -> !llvm.ptr
llvm.store %v1688, %v1690 : f64, !llvm.ptr
%v1691 = arith.constant 0 : i32
%v1692 = llvm.load %v1586 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1693 = llvm.getelementptr %v1586[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1694 = llvm.load %v1693 : !llvm.ptr -> i32
%v1695 = arith.index_cast %v1691 : i32 to index
%v1696 = arith.index_cast %v1694 : i32 to index
%v1697 = arith.constant 1 : index
%v1698 = arith.constant -1 : index
%v1699 = arith.cmpi sle, %v1695, %v1696 : index
%v1700 = arith.select %v1699, %v1697, %v1698 : index
cf.br ^b64(%v1695 : index)
^b64(%v1701: index):
%v1702 = arith.cmpi slt, %v1701, %v1696 : index
%v1703 = arith.cmpi sgt, %v1701, %v1696 : index
%v1704 = arith.select %v1699, %v1702, %v1703 : i1
cf.cond_br %v1704, ^b65(%v1701 : index), ^b66(%v1701 : index)
^b65(%v1705: index):
%v1706 = llvm.load %v1586 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1707 = llvm.getelementptr %v1586[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1708 = llvm.load %v1707 : !llvm.ptr -> !llvm.ptr
%v1709 = llvm.load %v1586 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1710 = llvm.getelementptr %v1586[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1711 = llvm.load %v1710 : !llvm.ptr -> i32
%v1712 = arith.index_cast %v1628 : index to i32
%v1713 = arith.muli %v1712, %v1711 : i32
%v1714 = arith.index_cast %v1705 : index to i32
%v1715 = arith.addi %v1713, %v1714 : i32
%v1716 = arith.extsi %v1715 : i32 to i64
%v1717 = llvm.getelementptr %v1708[%v1716] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1718 = llvm.load %v1717 : !llvm.ptr -> f32
%v1719 = llvm.load %v1641 : !llvm.ptr -> f32
%v1720 = arith.subf %v1718, %v1719 : f32
%v1721 = arith.extf %v1720 : f32 to f64
%v1722 = func.call @exp(%v1721) : (f64) -> f64
%v1723 = llvm.load %v1613 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1724 = llvm.getelementptr %v1613[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1725 = llvm.load %v1724 : !llvm.ptr -> !llvm.ptr
%v1726 = llvm.load %v1586 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1727 = llvm.getelementptr %v1586[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1728 = llvm.load %v1727 : !llvm.ptr -> i32
%v1729 = arith.index_cast %v1628 : index to i32
%v1730 = arith.muli %v1729, %v1728 : i32
%v1731 = arith.index_cast %v1705 : index to i32
%v1732 = arith.addi %v1730, %v1731 : i32
%v1733 = arith.truncf %v1722 : f64 to f32
%v1734 = arith.extsi %v1732 : i32 to i64
%v1735 = llvm.getelementptr %v1725[%v1734] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1733, %v1735 : f32, !llvm.ptr
%v1736 = llvm.load %v1690 : !llvm.ptr -> f64
%v1737 = arith.addf %v1736, %v1722 : f64
llvm.store %v1737, %v1690 : f64, !llvm.ptr
%v1738 = arith.addi %v1705, %v1700 : index
cf.br ^b64(%v1738 : index)
^b66(%v1739: index):
%v1740 = arith.constant 0 : i32
%v1741 = llvm.load %v1586 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1742 = llvm.getelementptr %v1586[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1743 = llvm.load %v1742 : !llvm.ptr -> i32
%v1744 = arith.index_cast %v1740 : i32 to index
%v1745 = arith.index_cast %v1743 : i32 to index
%v1746 = arith.constant 1 : index
%v1747 = arith.constant -1 : index
%v1748 = arith.cmpi sle, %v1744, %v1745 : index
%v1749 = arith.select %v1748, %v1746, %v1747 : index
cf.br ^b67(%v1744 : index)
^b67(%v1750: index):
%v1751 = arith.cmpi slt, %v1750, %v1745 : index
%v1752 = arith.cmpi sgt, %v1750, %v1745 : index
%v1753 = arith.select %v1748, %v1751, %v1752 : i1
cf.cond_br %v1753, ^b68(%v1750 : index), ^b69(%v1750 : index)
^b68(%v1754: index):
%v1755 = llvm.load %v1613 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1756 = llvm.getelementptr %v1613[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1757 = llvm.load %v1756 : !llvm.ptr -> !llvm.ptr
%v1758 = llvm.load %v1586 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1759 = llvm.getelementptr %v1586[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1760 = llvm.load %v1759 : !llvm.ptr -> i32
%v1761 = arith.index_cast %v1628 : index to i32
%v1762 = arith.muli %v1761, %v1760 : i32
%v1763 = arith.index_cast %v1754 : index to i32
%v1764 = arith.addi %v1762, %v1763 : i32
%v1765 = arith.extsi %v1764 : i32 to i64
%v1766 = llvm.getelementptr %v1757[%v1765] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1767 = llvm.load %v1766 : !llvm.ptr -> f32
%v1768 = llvm.load %v1690 : !llvm.ptr -> f64
%v1769 = arith.extf %v1767 : f32 to f64
%v1770 = arith.divf %v1769, %v1768 : f64
%v1771 = llvm.load %v1613 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1772 = llvm.getelementptr %v1613[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1773 = llvm.load %v1772 : !llvm.ptr -> !llvm.ptr
%v1774 = llvm.load %v1586 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1775 = llvm.getelementptr %v1586[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1776 = llvm.load %v1775 : !llvm.ptr -> i32
%v1777 = arith.index_cast %v1628 : index to i32
%v1778 = arith.muli %v1777, %v1776 : i32
%v1779 = arith.index_cast %v1754 : index to i32
%v1780 = arith.addi %v1778, %v1779 : i32
%v1781 = arith.truncf %v1770 : f64 to f32
%v1782 = arith.extsi %v1780 : i32 to i64
%v1783 = llvm.getelementptr %v1773[%v1782] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1781, %v1783 : f32, !llvm.ptr
%v1784 = arith.addi %v1754, %v1749 : index
cf.br ^b67(%v1784 : index)
^b69(%v1785: index):
%v1786 = arith.addi %v1628, %v1623 : index
cf.br ^b55(%v1786 : index)
^b57(%v1787: index):
%v1788 = llvm.load %v1613 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1789 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1790 = llvm.extractvalue %v1788[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1791 = llvm.insertvalue %v1790, %v1789[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1792 = llvm.extractvalue %v1788[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1793 = llvm.insertvalue %v1792, %v1791[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1794 = llvm.extractvalue %v1788[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1795 = llvm.insertvalue %v1794, %v1793[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1796 = llvm.extractvalue %v1788[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1797 = llvm.insertvalue %v1796, %v1795[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1798 = llvm.extractvalue %v1788[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1799 = llvm.insertvalue %v1798, %v1797[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1800 = llvm.extractvalue %v1788[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1801 = llvm.insertvalue %v1800, %v1799[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1802 = llvm.mlir.constant(1 : i64) : i64
%v1803 = llvm.alloca %v1802 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1801, %v1803 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1804 = llvm.load %v1803 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1804 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_relu_backward(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1805 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1806 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1807 = llvm.insertvalue %v1806, %v1805[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1808 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1809 = llvm.insertvalue %v1808, %v1807[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1810 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1811 = llvm.insertvalue %v1810, %v1809[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1812 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1813 = llvm.insertvalue %v1812, %v1811[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1814 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1815 = llvm.insertvalue %v1814, %v1813[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1816 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1817 = llvm.insertvalue %v1816, %v1815[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1818 = llvm.mlir.constant(1 : i64) : i64
%v1819 = llvm.alloca %v1818 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1817, %v1819 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1820 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1821 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1822 = llvm.insertvalue %v1821, %v1820[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1823 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1824 = llvm.insertvalue %v1823, %v1822[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1825 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1826 = llvm.insertvalue %v1825, %v1824[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1827 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1828 = llvm.insertvalue %v1827, %v1826[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1829 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1830 = llvm.insertvalue %v1829, %v1828[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1831 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1832 = llvm.insertvalue %v1831, %v1830[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1833 = llvm.mlir.constant(1 : i64) : i64
%v1834 = llvm.alloca %v1833 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1832, %v1834 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1835 = llvm.load %v1819 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1836 = llvm.getelementptr %v1819[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1837 = llvm.load %v1836 : !llvm.ptr -> i32
%v1838 = llvm.load %v1819 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1839 = llvm.getelementptr %v1819[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1840 = llvm.load %v1839 : !llvm.ptr -> i32
%v1841 = llvm.load %v1819 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1842 = llvm.getelementptr %v1819[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1843 = llvm.load %v1842 : !llvm.ptr -> i32
%v1844 = llvm.load %v1819 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1845 = llvm.getelementptr %v1819[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1846 = llvm.load %v1845 : !llvm.ptr -> i32
%v1847 = func.call @tensor_zeros(%v1846, %v1843, %v1840, %v1837) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1848 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1849 = llvm.extractvalue %v1847[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1850 = llvm.insertvalue %v1849, %v1848[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1851 = llvm.extractvalue %v1847[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1852 = llvm.insertvalue %v1851, %v1850[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1853 = llvm.extractvalue %v1847[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1854 = llvm.insertvalue %v1853, %v1852[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1855 = llvm.extractvalue %v1847[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1856 = llvm.insertvalue %v1855, %v1854[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1857 = llvm.extractvalue %v1847[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1858 = llvm.insertvalue %v1857, %v1856[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1859 = llvm.extractvalue %v1847[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1860 = llvm.insertvalue %v1859, %v1858[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1861 = llvm.mlir.constant(1 : i64) : i64
%v1862 = llvm.alloca %v1861 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1860, %v1862 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1863 = llvm.load %v1862 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1864 = llvm.mlir.constant(1 : i64) : i64
%v1865 = llvm.alloca %v1864 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1863, %v1865 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1866 = arith.constant 0 : i32
%v1867 = llvm.load %v1819 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1868 = llvm.getelementptr %v1819[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1869 = llvm.load %v1868 : !llvm.ptr -> i32
%v1870 = arith.index_cast %v1866 : i32 to index
%v1871 = arith.index_cast %v1869 : i32 to index
%v1872 = arith.constant 1 : index
%v1873 = arith.constant -1 : index
%v1874 = arith.cmpi sle, %v1870, %v1871 : index
%v1875 = arith.select %v1874, %v1872, %v1873 : index
cf.br ^b70(%v1870 : index)
^b70(%v1876: index):
%v1877 = arith.cmpi slt, %v1876, %v1871 : index
%v1878 = arith.cmpi sgt, %v1876, %v1871 : index
%v1879 = arith.select %v1874, %v1877, %v1878 : i1
cf.cond_br %v1879, ^b71(%v1876 : index), ^b72(%v1876 : index)
^b71(%v1880: index):
%v1881 = llvm.load %v1819 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1882 = llvm.getelementptr %v1819[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1883 = llvm.load %v1882 : !llvm.ptr -> !llvm.ptr
%v1884 = arith.index_cast %v1880 : index to i64
%v1885 = llvm.getelementptr %v1883[%v1884] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1886 = llvm.load %v1885 : !llvm.ptr -> f32
%v1887 = arith.constant 0.0 : f32
%v1888 = arith.cmpf ogt, %v1886, %v1887 : f32
cf.cond_br %v1888, ^b73, ^b74
^b73:
%v1889 = llvm.load %v1834 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1890 = llvm.getelementptr %v1834[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1891 = llvm.load %v1890 : !llvm.ptr -> !llvm.ptr
%v1892 = arith.index_cast %v1880 : index to i64
%v1893 = llvm.getelementptr %v1891[%v1892] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v1894 = llvm.load %v1893 : !llvm.ptr -> f32
%v1895 = llvm.load %v1865 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1896 = llvm.getelementptr %v1865[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1897 = llvm.load %v1896 : !llvm.ptr -> !llvm.ptr
%v1898 = arith.index_cast %v1880 : index to i64
%v1899 = llvm.getelementptr %v1897[%v1898] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1894, %v1899 : f32, !llvm.ptr
cf.br ^b75
^b74:
%v1900 = arith.constant 0.0 : f32
%v1901 = llvm.load %v1865 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1902 = llvm.getelementptr %v1865[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1903 = llvm.load %v1902 : !llvm.ptr -> !llvm.ptr
%v1904 = arith.index_cast %v1880 : index to i64
%v1905 = llvm.getelementptr %v1903[%v1904] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v1900, %v1905 : f32, !llvm.ptr
cf.br ^b75
^b75:
%v1906 = arith.addi %v1880, %v1875 : index
cf.br ^b70(%v1906 : index)
^b72(%v1907: index):
%v1908 = llvm.load %v1865 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1909 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1910 = llvm.extractvalue %v1908[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1911 = llvm.insertvalue %v1910, %v1909[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1912 = llvm.extractvalue %v1908[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1913 = llvm.insertvalue %v1912, %v1911[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1914 = llvm.extractvalue %v1908[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1915 = llvm.insertvalue %v1914, %v1913[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1916 = llvm.extractvalue %v1908[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1917 = llvm.insertvalue %v1916, %v1915[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1918 = llvm.extractvalue %v1908[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1919 = llvm.insertvalue %v1918, %v1917[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1920 = llvm.extractvalue %v1908[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1921 = llvm.insertvalue %v1920, %v1919[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1922 = llvm.mlir.constant(1 : i64) : i64
%v1923 = llvm.alloca %v1922 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1921, %v1923 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1924 = llvm.load %v1923 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v1924 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_sigmoid_backward(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v1925 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1926 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1927 = llvm.insertvalue %v1926, %v1925[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1928 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1929 = llvm.insertvalue %v1928, %v1927[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1930 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1931 = llvm.insertvalue %v1930, %v1929[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1932 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1933 = llvm.insertvalue %v1932, %v1931[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1934 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1935 = llvm.insertvalue %v1934, %v1933[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1936 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1937 = llvm.insertvalue %v1936, %v1935[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1938 = llvm.mlir.constant(1 : i64) : i64
%v1939 = llvm.alloca %v1938 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1937, %v1939 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1940 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1941 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1942 = llvm.insertvalue %v1941, %v1940[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1943 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1944 = llvm.insertvalue %v1943, %v1942[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1945 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1946 = llvm.insertvalue %v1945, %v1944[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1947 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1948 = llvm.insertvalue %v1947, %v1946[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1949 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1950 = llvm.insertvalue %v1949, %v1948[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1951 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1952 = llvm.insertvalue %v1951, %v1950[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1953 = llvm.mlir.constant(1 : i64) : i64
%v1954 = llvm.alloca %v1953 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1952, %v1954 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1955 = llvm.load %v1939 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1956 = llvm.getelementptr %v1939[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1957 = llvm.load %v1956 : !llvm.ptr -> i32
%v1958 = llvm.load %v1939 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1959 = llvm.getelementptr %v1939[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1960 = llvm.load %v1959 : !llvm.ptr -> i32
%v1961 = llvm.load %v1939 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1962 = llvm.getelementptr %v1939[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1963 = llvm.load %v1962 : !llvm.ptr -> i32
%v1964 = llvm.load %v1939 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1965 = llvm.getelementptr %v1939[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1966 = llvm.load %v1965 : !llvm.ptr -> i32
%v1967 = func.call @tensor_zeros(%v1966, %v1963, %v1960, %v1957) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1968 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1969 = llvm.extractvalue %v1967[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1970 = llvm.insertvalue %v1969, %v1968[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1971 = llvm.extractvalue %v1967[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1972 = llvm.insertvalue %v1971, %v1970[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1973 = llvm.extractvalue %v1967[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1974 = llvm.insertvalue %v1973, %v1972[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1975 = llvm.extractvalue %v1967[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1976 = llvm.insertvalue %v1975, %v1974[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1977 = llvm.extractvalue %v1967[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1978 = llvm.insertvalue %v1977, %v1976[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1979 = llvm.extractvalue %v1967[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1980 = llvm.insertvalue %v1979, %v1978[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1981 = llvm.mlir.constant(1 : i64) : i64
%v1982 = llvm.alloca %v1981 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1980, %v1982 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1983 = llvm.load %v1982 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1984 = llvm.mlir.constant(1 : i64) : i64
%v1985 = llvm.alloca %v1984 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v1983, %v1985 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v1986 = arith.constant 0 : i32
%v1987 = llvm.load %v1939 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1988 = llvm.getelementptr %v1939[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v1989 = llvm.load %v1988 : !llvm.ptr -> i32
%v1990 = arith.index_cast %v1986 : i32 to index
%v1991 = arith.index_cast %v1989 : i32 to index
%v1992 = arith.constant 1 : index
%v1993 = arith.constant -1 : index
%v1994 = arith.cmpi sle, %v1990, %v1991 : index
%v1995 = arith.select %v1994, %v1992, %v1993 : index
cf.br ^b76(%v1990 : index)
^b76(%v1996: index):
%v1997 = arith.cmpi slt, %v1996, %v1991 : index
%v1998 = arith.cmpi sgt, %v1996, %v1991 : index
%v1999 = arith.select %v1994, %v1997, %v1998 : i1
cf.cond_br %v1999, ^b77(%v1996 : index), ^b78(%v1996 : index)
^b77(%v2000: index):
%v2001 = llvm.load %v1939 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2002 = llvm.getelementptr %v1939[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2003 = llvm.load %v2002 : !llvm.ptr -> !llvm.ptr
%v2004 = arith.index_cast %v2000 : index to i64
%v2005 = llvm.getelementptr %v2003[%v2004] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2006 = llvm.load %v2005 : !llvm.ptr -> f32
%v2007 = llvm.mlir.constant(1 : i64) : i64
%v2008 = llvm.alloca %v2007 x f32 : (i64) -> !llvm.ptr
llvm.store %v2006, %v2008 : f32, !llvm.ptr
%v2009 = llvm.load %v1954 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2010 = llvm.getelementptr %v1954[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2011 = llvm.load %v2010 : !llvm.ptr -> !llvm.ptr
%v2012 = arith.index_cast %v2000 : index to i64
%v2013 = llvm.getelementptr %v2011[%v2012] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2014 = llvm.load %v2013 : !llvm.ptr -> f32
%v2015 = llvm.load %v2008 : !llvm.ptr -> f32
%v2016 = arith.mulf %v2014, %v2015 : f32
%v2017 = arith.constant 1.0 : f32
%v2018 = llvm.load %v2008 : !llvm.ptr -> f32
%v2019 = arith.subf %v2017, %v2018 : f32
%v2020 = arith.mulf %v2016, %v2019 : f32
%v2021 = llvm.load %v1985 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2022 = llvm.getelementptr %v1985[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2023 = llvm.load %v2022 : !llvm.ptr -> !llvm.ptr
%v2024 = arith.index_cast %v2000 : index to i64
%v2025 = llvm.getelementptr %v2023[%v2024] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v2020, %v2025 : f32, !llvm.ptr
%v2026 = arith.addi %v2000, %v1995 : index
cf.br ^b76(%v2026 : index)
^b78(%v2027: index):
%v2028 = llvm.load %v1985 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2029 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2030 = llvm.extractvalue %v2028[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2031 = llvm.insertvalue %v2030, %v2029[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2032 = llvm.extractvalue %v2028[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2033 = llvm.insertvalue %v2032, %v2031[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2034 = llvm.extractvalue %v2028[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2035 = llvm.insertvalue %v2034, %v2033[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2036 = llvm.extractvalue %v2028[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2037 = llvm.insertvalue %v2036, %v2035[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2038 = llvm.extractvalue %v2028[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2039 = llvm.insertvalue %v2038, %v2037[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2040 = llvm.extractvalue %v2028[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2041 = llvm.insertvalue %v2040, %v2039[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2042 = llvm.mlir.constant(1 : i64) : i64
%v2043 = llvm.alloca %v2042 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2041, %v2043 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2044 = llvm.load %v2043 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v2044 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_tanh_backward(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v2045 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2046 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2047 = llvm.insertvalue %v2046, %v2045[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2048 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2049 = llvm.insertvalue %v2048, %v2047[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2050 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2051 = llvm.insertvalue %v2050, %v2049[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2052 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2053 = llvm.insertvalue %v2052, %v2051[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2054 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2055 = llvm.insertvalue %v2054, %v2053[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2056 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2057 = llvm.insertvalue %v2056, %v2055[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2058 = llvm.mlir.constant(1 : i64) : i64
%v2059 = llvm.alloca %v2058 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2057, %v2059 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2060 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2061 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2062 = llvm.insertvalue %v2061, %v2060[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2063 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2064 = llvm.insertvalue %v2063, %v2062[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2065 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2066 = llvm.insertvalue %v2065, %v2064[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2067 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2068 = llvm.insertvalue %v2067, %v2066[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2069 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2070 = llvm.insertvalue %v2069, %v2068[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2071 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2072 = llvm.insertvalue %v2071, %v2070[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2073 = llvm.mlir.constant(1 : i64) : i64
%v2074 = llvm.alloca %v2073 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2072, %v2074 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2075 = llvm.load %v2059 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2076 = llvm.getelementptr %v2059[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2077 = llvm.load %v2076 : !llvm.ptr -> i32
%v2078 = llvm.load %v2059 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2079 = llvm.getelementptr %v2059[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2080 = llvm.load %v2079 : !llvm.ptr -> i32
%v2081 = llvm.load %v2059 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2082 = llvm.getelementptr %v2059[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2083 = llvm.load %v2082 : !llvm.ptr -> i32
%v2084 = llvm.load %v2059 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2085 = llvm.getelementptr %v2059[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2086 = llvm.load %v2085 : !llvm.ptr -> i32
%v2087 = func.call @tensor_zeros(%v2086, %v2083, %v2080, %v2077) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2088 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2089 = llvm.extractvalue %v2087[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2090 = llvm.insertvalue %v2089, %v2088[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2091 = llvm.extractvalue %v2087[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2092 = llvm.insertvalue %v2091, %v2090[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2093 = llvm.extractvalue %v2087[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2094 = llvm.insertvalue %v2093, %v2092[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2095 = llvm.extractvalue %v2087[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2096 = llvm.insertvalue %v2095, %v2094[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2097 = llvm.extractvalue %v2087[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2098 = llvm.insertvalue %v2097, %v2096[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2099 = llvm.extractvalue %v2087[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2100 = llvm.insertvalue %v2099, %v2098[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2101 = llvm.mlir.constant(1 : i64) : i64
%v2102 = llvm.alloca %v2101 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2100, %v2102 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2103 = llvm.load %v2102 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2104 = llvm.mlir.constant(1 : i64) : i64
%v2105 = llvm.alloca %v2104 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2103, %v2105 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2106 = arith.constant 0 : i32
%v2107 = llvm.load %v2059 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2108 = llvm.getelementptr %v2059[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2109 = llvm.load %v2108 : !llvm.ptr -> i32
%v2110 = arith.index_cast %v2106 : i32 to index
%v2111 = arith.index_cast %v2109 : i32 to index
%v2112 = arith.constant 1 : index
%v2113 = arith.constant -1 : index
%v2114 = arith.cmpi sle, %v2110, %v2111 : index
%v2115 = arith.select %v2114, %v2112, %v2113 : index
cf.br ^b79(%v2110 : index)
^b79(%v2116: index):
%v2117 = arith.cmpi slt, %v2116, %v2111 : index
%v2118 = arith.cmpi sgt, %v2116, %v2111 : index
%v2119 = arith.select %v2114, %v2117, %v2118 : i1
cf.cond_br %v2119, ^b80(%v2116 : index), ^b81(%v2116 : index)
^b80(%v2120: index):
%v2121 = llvm.load %v2059 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2122 = llvm.getelementptr %v2059[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2123 = llvm.load %v2122 : !llvm.ptr -> !llvm.ptr
%v2124 = arith.index_cast %v2120 : index to i64
%v2125 = llvm.getelementptr %v2123[%v2124] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2126 = llvm.load %v2125 : !llvm.ptr -> f32
%v2127 = llvm.load %v2074 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2128 = llvm.getelementptr %v2074[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2129 = llvm.load %v2128 : !llvm.ptr -> !llvm.ptr
%v2130 = arith.index_cast %v2120 : index to i64
%v2131 = llvm.getelementptr %v2129[%v2130] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2132 = llvm.load %v2131 : !llvm.ptr -> f32
%v2133 = arith.constant 1.0 : f32
%v2134 = arith.mulf %v2126, %v2126 : f32
%v2135 = arith.subf %v2133, %v2134 : f32
%v2136 = arith.mulf %v2132, %v2135 : f32
%v2137 = llvm.load %v2105 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2138 = llvm.getelementptr %v2105[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2139 = llvm.load %v2138 : !llvm.ptr -> !llvm.ptr
%v2140 = arith.index_cast %v2120 : index to i64
%v2141 = llvm.getelementptr %v2139[%v2140] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v2136, %v2141 : f32, !llvm.ptr
%v2142 = arith.addi %v2120, %v2115 : index
cf.br ^b79(%v2142 : index)
^b81(%v2143: index):
%v2144 = llvm.load %v2105 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2145 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2146 = llvm.extractvalue %v2144[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2147 = llvm.insertvalue %v2146, %v2145[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2148 = llvm.extractvalue %v2144[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2149 = llvm.insertvalue %v2148, %v2147[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2150 = llvm.extractvalue %v2144[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2151 = llvm.insertvalue %v2150, %v2149[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2152 = llvm.extractvalue %v2144[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2153 = llvm.insertvalue %v2152, %v2151[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2154 = llvm.extractvalue %v2144[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2155 = llvm.insertvalue %v2154, %v2153[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2156 = llvm.extractvalue %v2144[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2157 = llvm.insertvalue %v2156, %v2155[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2158 = llvm.mlir.constant(1 : i64) : i64
%v2159 = llvm.alloca %v2158 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2157, %v2159 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2160 = llvm.load %v2159 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v2160 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_mul_backward_a(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg2: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v2161 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2162 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2163 = llvm.insertvalue %v2162, %v2161[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2164 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2165 = llvm.insertvalue %v2164, %v2163[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2166 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2167 = llvm.insertvalue %v2166, %v2165[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2168 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2169 = llvm.insertvalue %v2168, %v2167[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2170 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2171 = llvm.insertvalue %v2170, %v2169[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2172 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2173 = llvm.insertvalue %v2172, %v2171[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2174 = llvm.mlir.constant(1 : i64) : i64
%v2175 = llvm.alloca %v2174 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2173, %v2175 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2176 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2177 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2178 = llvm.insertvalue %v2177, %v2176[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2179 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2180 = llvm.insertvalue %v2179, %v2178[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2181 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2182 = llvm.insertvalue %v2181, %v2180[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2183 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2184 = llvm.insertvalue %v2183, %v2182[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2185 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2186 = llvm.insertvalue %v2185, %v2184[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2187 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2188 = llvm.insertvalue %v2187, %v2186[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2189 = llvm.mlir.constant(1 : i64) : i64
%v2190 = llvm.alloca %v2189 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2188, %v2190 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2191 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2192 = llvm.extractvalue %arg2[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2193 = llvm.insertvalue %v2192, %v2191[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2194 = llvm.extractvalue %arg2[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2195 = llvm.insertvalue %v2194, %v2193[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2196 = llvm.extractvalue %arg2[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2197 = llvm.insertvalue %v2196, %v2195[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2198 = llvm.extractvalue %arg2[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2199 = llvm.insertvalue %v2198, %v2197[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2200 = llvm.extractvalue %arg2[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2201 = llvm.insertvalue %v2200, %v2199[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2202 = llvm.extractvalue %arg2[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2203 = llvm.insertvalue %v2202, %v2201[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2204 = llvm.mlir.constant(1 : i64) : i64
%v2205 = llvm.alloca %v2204 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2203, %v2205 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2206 = llvm.load %v2175 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2207 = llvm.getelementptr %v2175[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2208 = llvm.load %v2207 : !llvm.ptr -> i32
%v2209 = llvm.load %v2175 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2210 = llvm.getelementptr %v2175[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2211 = llvm.load %v2210 : !llvm.ptr -> i32
%v2212 = llvm.load %v2175 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2213 = llvm.getelementptr %v2175[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2214 = llvm.load %v2213 : !llvm.ptr -> i32
%v2215 = llvm.load %v2175 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2216 = llvm.getelementptr %v2175[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2217 = llvm.load %v2216 : !llvm.ptr -> i32
%v2218 = func.call @tensor_zeros(%v2217, %v2214, %v2211, %v2208) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2219 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2220 = llvm.extractvalue %v2218[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2221 = llvm.insertvalue %v2220, %v2219[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2222 = llvm.extractvalue %v2218[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2223 = llvm.insertvalue %v2222, %v2221[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2224 = llvm.extractvalue %v2218[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2225 = llvm.insertvalue %v2224, %v2223[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2226 = llvm.extractvalue %v2218[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2227 = llvm.insertvalue %v2226, %v2225[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2228 = llvm.extractvalue %v2218[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2229 = llvm.insertvalue %v2228, %v2227[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2230 = llvm.extractvalue %v2218[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2231 = llvm.insertvalue %v2230, %v2229[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2232 = llvm.mlir.constant(1 : i64) : i64
%v2233 = llvm.alloca %v2232 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2231, %v2233 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2234 = llvm.load %v2233 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2235 = llvm.mlir.constant(1 : i64) : i64
%v2236 = llvm.alloca %v2235 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2234, %v2236 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2237 = arith.constant 0 : i32
%v2238 = llvm.load %v2175 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2239 = llvm.getelementptr %v2175[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2240 = llvm.load %v2239 : !llvm.ptr -> i32
%v2241 = arith.index_cast %v2237 : i32 to index
%v2242 = arith.index_cast %v2240 : i32 to index
%v2243 = arith.constant 1 : index
%v2244 = arith.constant -1 : index
%v2245 = arith.cmpi sle, %v2241, %v2242 : index
%v2246 = arith.select %v2245, %v2243, %v2244 : index
cf.br ^b82(%v2241 : index)
^b82(%v2247: index):
%v2248 = arith.cmpi slt, %v2247, %v2242 : index
%v2249 = arith.cmpi sgt, %v2247, %v2242 : index
%v2250 = arith.select %v2245, %v2248, %v2249 : i1
cf.cond_br %v2250, ^b83(%v2247 : index), ^b84(%v2247 : index)
^b83(%v2251: index):
%v2252 = llvm.load %v2205 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2253 = llvm.getelementptr %v2205[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2254 = llvm.load %v2253 : !llvm.ptr -> !llvm.ptr
%v2255 = arith.index_cast %v2251 : index to i64
%v2256 = llvm.getelementptr %v2254[%v2255] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2257 = llvm.load %v2256 : !llvm.ptr -> f32
%v2258 = llvm.load %v2190 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2259 = llvm.getelementptr %v2190[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2260 = llvm.load %v2259 : !llvm.ptr -> !llvm.ptr
%v2261 = arith.index_cast %v2251 : index to i64
%v2262 = llvm.getelementptr %v2260[%v2261] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2263 = llvm.load %v2262 : !llvm.ptr -> f32
%v2264 = arith.mulf %v2257, %v2263 : f32
%v2265 = llvm.load %v2236 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2266 = llvm.getelementptr %v2236[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2267 = llvm.load %v2266 : !llvm.ptr -> !llvm.ptr
%v2268 = arith.index_cast %v2251 : index to i64
%v2269 = llvm.getelementptr %v2267[%v2268] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v2264, %v2269 : f32, !llvm.ptr
%v2270 = arith.addi %v2251, %v2246 : index
cf.br ^b82(%v2270 : index)
^b84(%v2271: index):
%v2272 = llvm.load %v2236 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2273 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2274 = llvm.extractvalue %v2272[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2275 = llvm.insertvalue %v2274, %v2273[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2276 = llvm.extractvalue %v2272[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2277 = llvm.insertvalue %v2276, %v2275[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2278 = llvm.extractvalue %v2272[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2279 = llvm.insertvalue %v2278, %v2277[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2280 = llvm.extractvalue %v2272[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2281 = llvm.insertvalue %v2280, %v2279[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2282 = llvm.extractvalue %v2272[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2283 = llvm.insertvalue %v2282, %v2281[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2284 = llvm.extractvalue %v2272[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2285 = llvm.insertvalue %v2284, %v2283[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2286 = llvm.mlir.constant(1 : i64) : i64
%v2287 = llvm.alloca %v2286 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2285, %v2287 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2288 = llvm.load %v2287 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v2288 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_mul_backward_b(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg2: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v2289 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2290 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2291 = llvm.insertvalue %v2290, %v2289[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2292 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2293 = llvm.insertvalue %v2292, %v2291[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2294 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2295 = llvm.insertvalue %v2294, %v2293[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2296 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2297 = llvm.insertvalue %v2296, %v2295[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2298 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2299 = llvm.insertvalue %v2298, %v2297[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2300 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2301 = llvm.insertvalue %v2300, %v2299[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2302 = llvm.mlir.constant(1 : i64) : i64
%v2303 = llvm.alloca %v2302 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2301, %v2303 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2304 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2305 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2306 = llvm.insertvalue %v2305, %v2304[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2307 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2308 = llvm.insertvalue %v2307, %v2306[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2309 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2310 = llvm.insertvalue %v2309, %v2308[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2311 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2312 = llvm.insertvalue %v2311, %v2310[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2313 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2314 = llvm.insertvalue %v2313, %v2312[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2315 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2316 = llvm.insertvalue %v2315, %v2314[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2317 = llvm.mlir.constant(1 : i64) : i64
%v2318 = llvm.alloca %v2317 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2316, %v2318 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2319 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2320 = llvm.extractvalue %arg2[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2321 = llvm.insertvalue %v2320, %v2319[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2322 = llvm.extractvalue %arg2[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2323 = llvm.insertvalue %v2322, %v2321[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2324 = llvm.extractvalue %arg2[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2325 = llvm.insertvalue %v2324, %v2323[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2326 = llvm.extractvalue %arg2[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2327 = llvm.insertvalue %v2326, %v2325[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2328 = llvm.extractvalue %arg2[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2329 = llvm.insertvalue %v2328, %v2327[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2330 = llvm.extractvalue %arg2[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2331 = llvm.insertvalue %v2330, %v2329[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2332 = llvm.mlir.constant(1 : i64) : i64
%v2333 = llvm.alloca %v2332 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2331, %v2333 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2334 = llvm.load %v2318 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2335 = llvm.getelementptr %v2318[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2336 = llvm.load %v2335 : !llvm.ptr -> i32
%v2337 = llvm.load %v2318 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2338 = llvm.getelementptr %v2318[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2339 = llvm.load %v2338 : !llvm.ptr -> i32
%v2340 = llvm.load %v2318 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2341 = llvm.getelementptr %v2318[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2342 = llvm.load %v2341 : !llvm.ptr -> i32
%v2343 = llvm.load %v2318 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2344 = llvm.getelementptr %v2318[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2345 = llvm.load %v2344 : !llvm.ptr -> i32
%v2346 = func.call @tensor_zeros(%v2345, %v2342, %v2339, %v2336) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2347 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2348 = llvm.extractvalue %v2346[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2349 = llvm.insertvalue %v2348, %v2347[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2350 = llvm.extractvalue %v2346[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2351 = llvm.insertvalue %v2350, %v2349[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2352 = llvm.extractvalue %v2346[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2353 = llvm.insertvalue %v2352, %v2351[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2354 = llvm.extractvalue %v2346[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2355 = llvm.insertvalue %v2354, %v2353[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2356 = llvm.extractvalue %v2346[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2357 = llvm.insertvalue %v2356, %v2355[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2358 = llvm.extractvalue %v2346[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2359 = llvm.insertvalue %v2358, %v2357[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2360 = llvm.mlir.constant(1 : i64) : i64
%v2361 = llvm.alloca %v2360 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2359, %v2361 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2362 = llvm.load %v2361 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2363 = llvm.mlir.constant(1 : i64) : i64
%v2364 = llvm.alloca %v2363 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2362, %v2364 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2365 = arith.constant 0 : i32
%v2366 = llvm.load %v2318 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2367 = llvm.getelementptr %v2318[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2368 = llvm.load %v2367 : !llvm.ptr -> i32
%v2369 = arith.index_cast %v2365 : i32 to index
%v2370 = arith.index_cast %v2368 : i32 to index
%v2371 = arith.constant 1 : index
%v2372 = arith.constant -1 : index
%v2373 = arith.cmpi sle, %v2369, %v2370 : index
%v2374 = arith.select %v2373, %v2371, %v2372 : index
cf.br ^b85(%v2369 : index)
^b85(%v2375: index):
%v2376 = arith.cmpi slt, %v2375, %v2370 : index
%v2377 = arith.cmpi sgt, %v2375, %v2370 : index
%v2378 = arith.select %v2373, %v2376, %v2377 : i1
cf.cond_br %v2378, ^b86(%v2375 : index), ^b87(%v2375 : index)
^b86(%v2379: index):
%v2380 = llvm.load %v2333 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2381 = llvm.getelementptr %v2333[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2382 = llvm.load %v2381 : !llvm.ptr -> !llvm.ptr
%v2383 = arith.index_cast %v2379 : index to i64
%v2384 = llvm.getelementptr %v2382[%v2383] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2385 = llvm.load %v2384 : !llvm.ptr -> f32
%v2386 = llvm.load %v2303 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2387 = llvm.getelementptr %v2303[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2388 = llvm.load %v2387 : !llvm.ptr -> !llvm.ptr
%v2389 = arith.index_cast %v2379 : index to i64
%v2390 = llvm.getelementptr %v2388[%v2389] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2391 = llvm.load %v2390 : !llvm.ptr -> f32
%v2392 = arith.mulf %v2385, %v2391 : f32
%v2393 = llvm.load %v2364 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2394 = llvm.getelementptr %v2364[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2395 = llvm.load %v2394 : !llvm.ptr -> !llvm.ptr
%v2396 = arith.index_cast %v2379 : index to i64
%v2397 = llvm.getelementptr %v2395[%v2396] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v2392, %v2397 : f32, !llvm.ptr
%v2398 = arith.addi %v2379, %v2374 : index
cf.br ^b85(%v2398 : index)
^b87(%v2399: index):
%v2400 = llvm.load %v2364 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2401 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2402 = llvm.extractvalue %v2400[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2403 = llvm.insertvalue %v2402, %v2401[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2404 = llvm.extractvalue %v2400[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2405 = llvm.insertvalue %v2404, %v2403[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2406 = llvm.extractvalue %v2400[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2407 = llvm.insertvalue %v2406, %v2405[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2408 = llvm.extractvalue %v2400[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2409 = llvm.insertvalue %v2408, %v2407[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2410 = llvm.extractvalue %v2400[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2411 = llvm.insertvalue %v2410, %v2409[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2412 = llvm.extractvalue %v2400[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2413 = llvm.insertvalue %v2412, %v2411[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2414 = llvm.mlir.constant(1 : i64) : i64
%v2415 = llvm.alloca %v2414 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2413, %v2415 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2416 = llvm.load %v2415 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v2416 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_broadcast_add(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v2417 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2418 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2419 = llvm.insertvalue %v2418, %v2417[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2420 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2421 = llvm.insertvalue %v2420, %v2419[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2422 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2423 = llvm.insertvalue %v2422, %v2421[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2424 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2425 = llvm.insertvalue %v2424, %v2423[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2426 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2427 = llvm.insertvalue %v2426, %v2425[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2428 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2429 = llvm.insertvalue %v2428, %v2427[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2430 = llvm.mlir.constant(1 : i64) : i64
%v2431 = llvm.alloca %v2430 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2429, %v2431 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2432 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2433 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2434 = llvm.insertvalue %v2433, %v2432[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2435 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2436 = llvm.insertvalue %v2435, %v2434[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2437 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2438 = llvm.insertvalue %v2437, %v2436[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2439 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2440 = llvm.insertvalue %v2439, %v2438[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2441 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2442 = llvm.insertvalue %v2441, %v2440[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2443 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2444 = llvm.insertvalue %v2443, %v2442[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2445 = llvm.mlir.constant(1 : i64) : i64
%v2446 = llvm.alloca %v2445 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2444, %v2446 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2447 = llvm.load %v2431 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2448 = llvm.getelementptr %v2431[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2449 = llvm.load %v2448 : !llvm.ptr -> i32
%v2450 = llvm.load %v2431 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2451 = llvm.getelementptr %v2431[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2452 = llvm.load %v2451 : !llvm.ptr -> i32
%v2453 = llvm.load %v2431 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2454 = llvm.getelementptr %v2431[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2455 = llvm.load %v2454 : !llvm.ptr -> i32
%v2456 = llvm.load %v2431 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2457 = llvm.getelementptr %v2431[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2458 = llvm.load %v2457 : !llvm.ptr -> i32
%v2459 = func.call @tensor_zeros(%v2458, %v2455, %v2452, %v2449) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2460 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2461 = llvm.extractvalue %v2459[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2462 = llvm.insertvalue %v2461, %v2460[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2463 = llvm.extractvalue %v2459[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2464 = llvm.insertvalue %v2463, %v2462[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2465 = llvm.extractvalue %v2459[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2466 = llvm.insertvalue %v2465, %v2464[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2467 = llvm.extractvalue %v2459[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2468 = llvm.insertvalue %v2467, %v2466[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2469 = llvm.extractvalue %v2459[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2470 = llvm.insertvalue %v2469, %v2468[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2471 = llvm.extractvalue %v2459[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2472 = llvm.insertvalue %v2471, %v2470[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2473 = llvm.mlir.constant(1 : i64) : i64
%v2474 = llvm.alloca %v2473 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2472, %v2474 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2475 = llvm.load %v2474 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2476 = llvm.mlir.constant(1 : i64) : i64
%v2477 = llvm.alloca %v2476 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2475, %v2477 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2478 = arith.constant 0 : i32
%v2479 = llvm.load %v2431 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2480 = llvm.getelementptr %v2431[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2481 = llvm.load %v2480 : !llvm.ptr -> i32
%v2482 = arith.index_cast %v2478 : i32 to index
%v2483 = arith.index_cast %v2481 : i32 to index
%v2484 = arith.constant 1 : index
%v2485 = arith.constant -1 : index
%v2486 = arith.cmpi sle, %v2482, %v2483 : index
%v2487 = arith.select %v2486, %v2484, %v2485 : index
cf.br ^b88(%v2482 : index)
^b88(%v2488: index):
%v2489 = arith.cmpi slt, %v2488, %v2483 : index
%v2490 = arith.cmpi sgt, %v2488, %v2483 : index
%v2491 = arith.select %v2486, %v2489, %v2490 : i1
cf.cond_br %v2491, ^b89(%v2488 : index), ^b90(%v2488 : index)
^b89(%v2492: index):
%v2493 = arith.constant 0 : i32
%v2494 = llvm.mlir.constant(1 : i64) : i64
%v2495 = llvm.alloca %v2494 x i32 : (i64) -> !llvm.ptr
llvm.store %v2493, %v2495 : i32, !llvm.ptr
%v2496 = llvm.load %v2446 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2497 = llvm.getelementptr %v2446[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2498 = llvm.load %v2497 : !llvm.ptr -> i32
%v2499 = arith.constant 1 : i32
%v2500 = arith.cmpi sgt, %v2498, %v2499 : i32
cf.cond_br %v2500, ^b91, ^b92
^b91:
%v2501 = arith.index_cast %v2492 : index to i32
llvm.store %v2501, %v2495 : i32, !llvm.ptr
cf.br ^b93
^b92:
cf.br ^b93
^b93:
%v2502 = arith.constant 0 : i32
%v2503 = llvm.load %v2431 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2504 = llvm.getelementptr %v2431[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2505 = llvm.load %v2504 : !llvm.ptr -> i32
%v2506 = arith.index_cast %v2502 : i32 to index
%v2507 = arith.index_cast %v2505 : i32 to index
%v2508 = arith.constant 1 : index
%v2509 = arith.constant -1 : index
%v2510 = arith.cmpi sle, %v2506, %v2507 : index
%v2511 = arith.select %v2510, %v2508, %v2509 : index
cf.br ^b94(%v2506 : index)
^b94(%v2512: index):
%v2513 = arith.cmpi slt, %v2512, %v2507 : index
%v2514 = arith.cmpi sgt, %v2512, %v2507 : index
%v2515 = arith.select %v2510, %v2513, %v2514 : i1
cf.cond_br %v2515, ^b95(%v2512 : index), ^b96(%v2512 : index)
^b95(%v2516: index):
%v2517 = arith.constant 0 : i32
%v2518 = llvm.mlir.constant(1 : i64) : i64
%v2519 = llvm.alloca %v2518 x i32 : (i64) -> !llvm.ptr
llvm.store %v2517, %v2519 : i32, !llvm.ptr
%v2520 = llvm.load %v2446 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2521 = llvm.getelementptr %v2446[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2522 = llvm.load %v2521 : !llvm.ptr -> i32
%v2523 = arith.constant 1 : i32
%v2524 = arith.cmpi sgt, %v2522, %v2523 : i32
cf.cond_br %v2524, ^b97, ^b98
^b97:
%v2525 = arith.index_cast %v2516 : index to i32
llvm.store %v2525, %v2519 : i32, !llvm.ptr
cf.br ^b99
^b98:
cf.br ^b99
^b99:
%v2526 = llvm.load %v2431 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2527 = arith.constant 0 : i32
%v2528 = arith.constant 0 : i32
%v2529 = arith.index_cast %v2492 : index to i32
%v2530 = arith.index_cast %v2516 : index to i32
%v2531 = func.call @tensor_idx(%v2526, %v2529, %v2530, %v2527, %v2528) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, i32, i32, i32, i32) -> i32
%v2532 = llvm.load %v2446 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2533 = llvm.load %v2495 : !llvm.ptr -> i32
%v2534 = llvm.load %v2519 : !llvm.ptr -> i32
%v2535 = arith.constant 0 : i32
%v2536 = arith.constant 0 : i32
%v2537 = func.call @tensor_idx(%v2532, %v2533, %v2534, %v2535, %v2536) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, i32, i32, i32, i32) -> i32
%v2538 = llvm.load %v2431 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2539 = llvm.getelementptr %v2431[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2540 = llvm.load %v2539 : !llvm.ptr -> !llvm.ptr
%v2541 = arith.extsi %v2531 : i32 to i64
%v2542 = llvm.getelementptr %v2540[%v2541] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2543 = llvm.load %v2542 : !llvm.ptr -> f32
%v2544 = llvm.load %v2446 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2545 = llvm.getelementptr %v2446[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2546 = llvm.load %v2545 : !llvm.ptr -> !llvm.ptr
%v2547 = arith.extsi %v2537 : i32 to i64
%v2548 = llvm.getelementptr %v2546[%v2547] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2549 = llvm.load %v2548 : !llvm.ptr -> f32
%v2550 = arith.addf %v2543, %v2549 : f32
%v2551 = llvm.load %v2477 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2552 = llvm.getelementptr %v2477[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2553 = llvm.load %v2552 : !llvm.ptr -> !llvm.ptr
%v2554 = arith.extsi %v2531 : i32 to i64
%v2555 = llvm.getelementptr %v2553[%v2554] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v2550, %v2555 : f32, !llvm.ptr
%v2556 = arith.addi %v2516, %v2511 : index
cf.br ^b94(%v2556 : index)
^b96(%v2557: index):
%v2558 = arith.addi %v2492, %v2487 : index
cf.br ^b88(%v2558 : index)
^b90(%v2559: index):
%v2560 = llvm.load %v2477 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2561 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2562 = llvm.extractvalue %v2560[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2563 = llvm.insertvalue %v2562, %v2561[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2564 = llvm.extractvalue %v2560[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2565 = llvm.insertvalue %v2564, %v2563[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2566 = llvm.extractvalue %v2560[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2567 = llvm.insertvalue %v2566, %v2565[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2568 = llvm.extractvalue %v2560[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2569 = llvm.insertvalue %v2568, %v2567[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2570 = llvm.extractvalue %v2560[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2571 = llvm.insertvalue %v2570, %v2569[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2572 = llvm.extractvalue %v2560[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2573 = llvm.insertvalue %v2572, %v2571[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2574 = llvm.mlir.constant(1 : i64) : i64
%v2575 = llvm.alloca %v2574 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2573, %v2575 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2576 = llvm.load %v2575 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v2576 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_matmul(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v2577 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2578 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2579 = llvm.insertvalue %v2578, %v2577[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2580 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2581 = llvm.insertvalue %v2580, %v2579[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2582 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2583 = llvm.insertvalue %v2582, %v2581[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2584 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2585 = llvm.insertvalue %v2584, %v2583[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2586 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2587 = llvm.insertvalue %v2586, %v2585[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2588 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2589 = llvm.insertvalue %v2588, %v2587[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2590 = llvm.mlir.constant(1 : i64) : i64
%v2591 = llvm.alloca %v2590 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2589, %v2591 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2592 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2593 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2594 = llvm.insertvalue %v2593, %v2592[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2595 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2596 = llvm.insertvalue %v2595, %v2594[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2597 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2598 = llvm.insertvalue %v2597, %v2596[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2599 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2600 = llvm.insertvalue %v2599, %v2598[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2601 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2602 = llvm.insertvalue %v2601, %v2600[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2603 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2604 = llvm.insertvalue %v2603, %v2602[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2605 = llvm.mlir.constant(1 : i64) : i64
%v2606 = llvm.alloca %v2605 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2604, %v2606 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2607 = llvm.load %v2591 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2608 = llvm.getelementptr %v2591[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2609 = llvm.load %v2608 : !llvm.ptr -> i32
%v2610 = llvm.load %v2591 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2611 = llvm.getelementptr %v2591[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2612 = llvm.load %v2611 : !llvm.ptr -> i32
%v2613 = llvm.load %v2606 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2614 = llvm.getelementptr %v2606[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2615 = llvm.load %v2614 : !llvm.ptr -> i32
%v2616 = arith.constant 1 : i32
%v2617 = arith.constant 1 : i32
%v2618 = func.call @tensor_zeros(%v2609, %v2615, %v2617, %v2616) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2619 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2620 = llvm.extractvalue %v2618[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2621 = llvm.insertvalue %v2620, %v2619[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2622 = llvm.extractvalue %v2618[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2623 = llvm.insertvalue %v2622, %v2621[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2624 = llvm.extractvalue %v2618[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2625 = llvm.insertvalue %v2624, %v2623[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2626 = llvm.extractvalue %v2618[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2627 = llvm.insertvalue %v2626, %v2625[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2628 = llvm.extractvalue %v2618[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2629 = llvm.insertvalue %v2628, %v2627[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2630 = llvm.extractvalue %v2618[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2631 = llvm.insertvalue %v2630, %v2629[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2632 = llvm.mlir.constant(1 : i64) : i64
%v2633 = llvm.alloca %v2632 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2631, %v2633 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2634 = llvm.load %v2633 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2635 = llvm.mlir.constant(1 : i64) : i64
%v2636 = llvm.alloca %v2635 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2634, %v2636 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2637 = arith.constant 0 : i32
%v2638 = arith.index_cast %v2637 : i32 to index
%v2639 = arith.index_cast %v2609 : i32 to index
%v2640 = arith.constant 1 : index
%v2641 = arith.constant -1 : index
%v2642 = arith.cmpi sle, %v2638, %v2639 : index
%v2643 = arith.select %v2642, %v2640, %v2641 : index
cf.br ^b100(%v2638 : index)
^b100(%v2644: index):
%v2645 = arith.cmpi slt, %v2644, %v2639 : index
%v2646 = arith.cmpi sgt, %v2644, %v2639 : index
%v2647 = arith.select %v2642, %v2645, %v2646 : i1
cf.cond_br %v2647, ^b101(%v2644 : index), ^b102(%v2644 : index)
^b101(%v2648: index):
%v2649 = arith.constant 0 : i32
%v2650 = arith.index_cast %v2649 : i32 to index
%v2651 = arith.index_cast %v2615 : i32 to index
%v2652 = arith.constant 1 : index
%v2653 = arith.constant -1 : index
%v2654 = arith.cmpi sle, %v2650, %v2651 : index
%v2655 = arith.select %v2654, %v2652, %v2653 : index
cf.br ^b103(%v2650 : index)
^b103(%v2656: index):
%v2657 = arith.cmpi slt, %v2656, %v2651 : index
%v2658 = arith.cmpi sgt, %v2656, %v2651 : index
%v2659 = arith.select %v2654, %v2657, %v2658 : i1
cf.cond_br %v2659, ^b104(%v2656 : index), ^b105(%v2656 : index)
^b104(%v2660: index):
%v2661 = arith.constant 0.0 : f32
%v2662 = llvm.mlir.constant(1 : i64) : i64
%v2663 = llvm.alloca %v2662 x f32 : (i64) -> !llvm.ptr
llvm.store %v2661, %v2663 : f32, !llvm.ptr
%v2664 = arith.constant 0 : i32
%v2665 = arith.index_cast %v2664 : i32 to index
%v2666 = arith.index_cast %v2612 : i32 to index
%v2667 = arith.constant 1 : index
%v2668 = arith.constant -1 : index
%v2669 = arith.cmpi sle, %v2665, %v2666 : index
%v2670 = arith.select %v2669, %v2667, %v2668 : index
cf.br ^b106(%v2665 : index)
^b106(%v2671: index):
%v2672 = arith.cmpi slt, %v2671, %v2666 : index
%v2673 = arith.cmpi sgt, %v2671, %v2666 : index
%v2674 = arith.select %v2669, %v2672, %v2673 : i1
cf.cond_br %v2674, ^b107(%v2671 : index), ^b108(%v2671 : index)
^b107(%v2675: index):
%v2676 = llvm.load %v2663 : !llvm.ptr -> f32
%v2677 = llvm.load %v2591 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2678 = llvm.getelementptr %v2591[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2679 = llvm.load %v2678 : !llvm.ptr -> !llvm.ptr
%v2680 = arith.index_cast %v2648 : index to i32
%v2681 = arith.muli %v2680, %v2612 : i32
%v2682 = arith.index_cast %v2675 : index to i32
%v2683 = arith.addi %v2681, %v2682 : i32
%v2684 = arith.extsi %v2683 : i32 to i64
%v2685 = llvm.getelementptr %v2679[%v2684] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2686 = llvm.load %v2685 : !llvm.ptr -> f32
%v2687 = llvm.load %v2606 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2688 = llvm.getelementptr %v2606[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2689 = llvm.load %v2688 : !llvm.ptr -> !llvm.ptr
%v2690 = arith.index_cast %v2675 : index to i32
%v2691 = arith.muli %v2690, %v2615 : i32
%v2692 = arith.index_cast %v2660 : index to i32
%v2693 = arith.addi %v2691, %v2692 : i32
%v2694 = arith.extsi %v2693 : i32 to i64
%v2695 = llvm.getelementptr %v2689[%v2694] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2696 = llvm.load %v2695 : !llvm.ptr -> f32
%v2697 = arith.mulf %v2686, %v2696 : f32
%v2698 = arith.addf %v2676, %v2697 : f32
llvm.store %v2698, %v2663 : f32, !llvm.ptr
%v2699 = arith.addi %v2675, %v2670 : index
cf.br ^b106(%v2699 : index)
^b108(%v2700: index):
%v2701 = llvm.load %v2663 : !llvm.ptr -> f32
%v2702 = llvm.load %v2636 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2703 = llvm.getelementptr %v2636[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2704 = llvm.load %v2703 : !llvm.ptr -> !llvm.ptr
%v2705 = arith.index_cast %v2648 : index to i32
%v2706 = arith.muli %v2705, %v2615 : i32
%v2707 = arith.index_cast %v2660 : index to i32
%v2708 = arith.addi %v2706, %v2707 : i32
%v2709 = arith.extsi %v2708 : i32 to i64
%v2710 = llvm.getelementptr %v2704[%v2709] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v2701, %v2710 : f32, !llvm.ptr
%v2711 = arith.addi %v2660, %v2655 : index
cf.br ^b103(%v2711 : index)
^b105(%v2712: index):
%v2713 = arith.addi %v2648, %v2643 : index
cf.br ^b100(%v2713 : index)
^b102(%v2714: index):
%v2715 = llvm.load %v2636 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2716 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2717 = llvm.extractvalue %v2715[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2718 = llvm.insertvalue %v2717, %v2716[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2719 = llvm.extractvalue %v2715[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2720 = llvm.insertvalue %v2719, %v2718[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2721 = llvm.extractvalue %v2715[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2722 = llvm.insertvalue %v2721, %v2720[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2723 = llvm.extractvalue %v2715[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2724 = llvm.insertvalue %v2723, %v2722[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2725 = llvm.extractvalue %v2715[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2726 = llvm.insertvalue %v2725, %v2724[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2727 = llvm.extractvalue %v2715[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2728 = llvm.insertvalue %v2727, %v2726[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2729 = llvm.mlir.constant(1 : i64) : i64
%v2730 = llvm.alloca %v2729 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2728, %v2730 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2731 = llvm.load %v2730 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v2731 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_matmul_backward_a(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg2: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v2732 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2733 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2734 = llvm.insertvalue %v2733, %v2732[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2735 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2736 = llvm.insertvalue %v2735, %v2734[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2737 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2738 = llvm.insertvalue %v2737, %v2736[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2739 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2740 = llvm.insertvalue %v2739, %v2738[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2741 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2742 = llvm.insertvalue %v2741, %v2740[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2743 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2744 = llvm.insertvalue %v2743, %v2742[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2745 = llvm.mlir.constant(1 : i64) : i64
%v2746 = llvm.alloca %v2745 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2744, %v2746 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2747 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2748 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2749 = llvm.insertvalue %v2748, %v2747[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2750 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2751 = llvm.insertvalue %v2750, %v2749[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2752 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2753 = llvm.insertvalue %v2752, %v2751[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2754 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2755 = llvm.insertvalue %v2754, %v2753[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2756 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2757 = llvm.insertvalue %v2756, %v2755[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2758 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2759 = llvm.insertvalue %v2758, %v2757[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2760 = llvm.mlir.constant(1 : i64) : i64
%v2761 = llvm.alloca %v2760 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2759, %v2761 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2762 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2763 = llvm.extractvalue %arg2[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2764 = llvm.insertvalue %v2763, %v2762[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2765 = llvm.extractvalue %arg2[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2766 = llvm.insertvalue %v2765, %v2764[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2767 = llvm.extractvalue %arg2[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2768 = llvm.insertvalue %v2767, %v2766[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2769 = llvm.extractvalue %arg2[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2770 = llvm.insertvalue %v2769, %v2768[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2771 = llvm.extractvalue %arg2[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2772 = llvm.insertvalue %v2771, %v2770[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2773 = llvm.extractvalue %arg2[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2774 = llvm.insertvalue %v2773, %v2772[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2775 = llvm.mlir.constant(1 : i64) : i64
%v2776 = llvm.alloca %v2775 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2774, %v2776 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2777 = llvm.load %v2776 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2778 = llvm.getelementptr %v2776[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2779 = llvm.load %v2778 : !llvm.ptr -> i32
%v2780 = llvm.load %v2776 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2781 = llvm.getelementptr %v2776[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2782 = llvm.load %v2781 : !llvm.ptr -> i32
%v2783 = llvm.load %v2746 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2784 = llvm.getelementptr %v2746[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2785 = llvm.load %v2784 : !llvm.ptr -> i32
%v2786 = arith.constant 1 : i32
%v2787 = arith.constant 1 : i32
%v2788 = func.call @tensor_zeros(%v2779, %v2785, %v2787, %v2786) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2789 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2790 = llvm.extractvalue %v2788[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2791 = llvm.insertvalue %v2790, %v2789[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2792 = llvm.extractvalue %v2788[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2793 = llvm.insertvalue %v2792, %v2791[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2794 = llvm.extractvalue %v2788[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2795 = llvm.insertvalue %v2794, %v2793[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2796 = llvm.extractvalue %v2788[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2797 = llvm.insertvalue %v2796, %v2795[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2798 = llvm.extractvalue %v2788[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2799 = llvm.insertvalue %v2798, %v2797[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2800 = llvm.extractvalue %v2788[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2801 = llvm.insertvalue %v2800, %v2799[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2802 = llvm.mlir.constant(1 : i64) : i64
%v2803 = llvm.alloca %v2802 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2801, %v2803 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2804 = llvm.load %v2803 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2805 = llvm.mlir.constant(1 : i64) : i64
%v2806 = llvm.alloca %v2805 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2804, %v2806 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2807 = arith.constant 0 : i32
%v2808 = arith.index_cast %v2807 : i32 to index
%v2809 = arith.index_cast %v2779 : i32 to index
%v2810 = arith.constant 1 : index
%v2811 = arith.constant -1 : index
%v2812 = arith.cmpi sle, %v2808, %v2809 : index
%v2813 = arith.select %v2812, %v2810, %v2811 : index
cf.br ^b109(%v2808 : index)
^b109(%v2814: index):
%v2815 = arith.cmpi slt, %v2814, %v2809 : index
%v2816 = arith.cmpi sgt, %v2814, %v2809 : index
%v2817 = arith.select %v2812, %v2815, %v2816 : i1
cf.cond_br %v2817, ^b110(%v2814 : index), ^b111(%v2814 : index)
^b110(%v2818: index):
%v2819 = arith.constant 0 : i32
%v2820 = arith.index_cast %v2819 : i32 to index
%v2821 = arith.index_cast %v2785 : i32 to index
%v2822 = arith.constant 1 : index
%v2823 = arith.constant -1 : index
%v2824 = arith.cmpi sle, %v2820, %v2821 : index
%v2825 = arith.select %v2824, %v2822, %v2823 : index
cf.br ^b112(%v2820 : index)
^b112(%v2826: index):
%v2827 = arith.cmpi slt, %v2826, %v2821 : index
%v2828 = arith.cmpi sgt, %v2826, %v2821 : index
%v2829 = arith.select %v2824, %v2827, %v2828 : i1
cf.cond_br %v2829, ^b113(%v2826 : index), ^b114(%v2826 : index)
^b113(%v2830: index):
%v2831 = arith.constant 0.0 : f32
%v2832 = llvm.mlir.constant(1 : i64) : i64
%v2833 = llvm.alloca %v2832 x f32 : (i64) -> !llvm.ptr
llvm.store %v2831, %v2833 : f32, !llvm.ptr
%v2834 = arith.constant 0 : i32
%v2835 = arith.index_cast %v2834 : i32 to index
%v2836 = arith.index_cast %v2782 : i32 to index
%v2837 = arith.constant 1 : index
%v2838 = arith.constant -1 : index
%v2839 = arith.cmpi sle, %v2835, %v2836 : index
%v2840 = arith.select %v2839, %v2837, %v2838 : index
cf.br ^b115(%v2835 : index)
^b115(%v2841: index):
%v2842 = arith.cmpi slt, %v2841, %v2836 : index
%v2843 = arith.cmpi sgt, %v2841, %v2836 : index
%v2844 = arith.select %v2839, %v2842, %v2843 : i1
cf.cond_br %v2844, ^b116(%v2841 : index), ^b117(%v2841 : index)
^b116(%v2845: index):
%v2846 = llvm.load %v2833 : !llvm.ptr -> f32
%v2847 = llvm.load %v2776 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2848 = llvm.getelementptr %v2776[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2849 = llvm.load %v2848 : !llvm.ptr -> !llvm.ptr
%v2850 = arith.index_cast %v2818 : index to i32
%v2851 = arith.muli %v2850, %v2782 : i32
%v2852 = arith.index_cast %v2845 : index to i32
%v2853 = arith.addi %v2851, %v2852 : i32
%v2854 = arith.extsi %v2853 : i32 to i64
%v2855 = llvm.getelementptr %v2849[%v2854] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2856 = llvm.load %v2855 : !llvm.ptr -> f32
%v2857 = llvm.load %v2761 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2858 = llvm.getelementptr %v2761[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2859 = llvm.load %v2858 : !llvm.ptr -> !llvm.ptr
%v2860 = arith.index_cast %v2830 : index to i32
%v2861 = arith.muli %v2860, %v2782 : i32
%v2862 = arith.index_cast %v2845 : index to i32
%v2863 = arith.addi %v2861, %v2862 : i32
%v2864 = arith.extsi %v2863 : i32 to i64
%v2865 = llvm.getelementptr %v2859[%v2864] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v2866 = llvm.load %v2865 : !llvm.ptr -> f32
%v2867 = arith.mulf %v2856, %v2866 : f32
%v2868 = arith.addf %v2846, %v2867 : f32
llvm.store %v2868, %v2833 : f32, !llvm.ptr
%v2869 = arith.addi %v2845, %v2840 : index
cf.br ^b115(%v2869 : index)
^b117(%v2870: index):
%v2871 = llvm.load %v2833 : !llvm.ptr -> f32
%v2872 = llvm.load %v2806 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2873 = llvm.getelementptr %v2806[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2874 = llvm.load %v2873 : !llvm.ptr -> !llvm.ptr
%v2875 = arith.index_cast %v2818 : index to i32
%v2876 = arith.muli %v2875, %v2785 : i32
%v2877 = arith.index_cast %v2830 : index to i32
%v2878 = arith.addi %v2876, %v2877 : i32
%v2879 = arith.extsi %v2878 : i32 to i64
%v2880 = llvm.getelementptr %v2874[%v2879] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v2871, %v2880 : f32, !llvm.ptr
%v2881 = arith.addi %v2830, %v2825 : index
cf.br ^b112(%v2881 : index)
^b114(%v2882: index):
%v2883 = arith.addi %v2818, %v2813 : index
cf.br ^b109(%v2883 : index)
^b111(%v2884: index):
%v2885 = llvm.load %v2806 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2886 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2887 = llvm.extractvalue %v2885[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2888 = llvm.insertvalue %v2887, %v2886[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2889 = llvm.extractvalue %v2885[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2890 = llvm.insertvalue %v2889, %v2888[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2891 = llvm.extractvalue %v2885[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2892 = llvm.insertvalue %v2891, %v2890[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2893 = llvm.extractvalue %v2885[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2894 = llvm.insertvalue %v2893, %v2892[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2895 = llvm.extractvalue %v2885[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2896 = llvm.insertvalue %v2895, %v2894[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2897 = llvm.extractvalue %v2885[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2898 = llvm.insertvalue %v2897, %v2896[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2899 = llvm.mlir.constant(1 : i64) : i64
%v2900 = llvm.alloca %v2899 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2898, %v2900 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2901 = llvm.load %v2900 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v2901 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_matmul_backward_b(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg1: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, %arg2: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v2902 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2903 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2904 = llvm.insertvalue %v2903, %v2902[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2905 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2906 = llvm.insertvalue %v2905, %v2904[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2907 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2908 = llvm.insertvalue %v2907, %v2906[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2909 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2910 = llvm.insertvalue %v2909, %v2908[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2911 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2912 = llvm.insertvalue %v2911, %v2910[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2913 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2914 = llvm.insertvalue %v2913, %v2912[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2915 = llvm.mlir.constant(1 : i64) : i64
%v2916 = llvm.alloca %v2915 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2914, %v2916 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2917 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2918 = llvm.extractvalue %arg1[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2919 = llvm.insertvalue %v2918, %v2917[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2920 = llvm.extractvalue %arg1[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2921 = llvm.insertvalue %v2920, %v2919[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2922 = llvm.extractvalue %arg1[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2923 = llvm.insertvalue %v2922, %v2921[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2924 = llvm.extractvalue %arg1[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2925 = llvm.insertvalue %v2924, %v2923[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2926 = llvm.extractvalue %arg1[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2927 = llvm.insertvalue %v2926, %v2925[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2928 = llvm.extractvalue %arg1[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2929 = llvm.insertvalue %v2928, %v2927[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2930 = llvm.mlir.constant(1 : i64) : i64
%v2931 = llvm.alloca %v2930 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2929, %v2931 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2932 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2933 = llvm.extractvalue %arg2[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2934 = llvm.insertvalue %v2933, %v2932[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2935 = llvm.extractvalue %arg2[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2936 = llvm.insertvalue %v2935, %v2934[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2937 = llvm.extractvalue %arg2[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2938 = llvm.insertvalue %v2937, %v2936[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2939 = llvm.extractvalue %arg2[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2940 = llvm.insertvalue %v2939, %v2938[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2941 = llvm.extractvalue %arg2[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2942 = llvm.insertvalue %v2941, %v2940[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2943 = llvm.extractvalue %arg2[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2944 = llvm.insertvalue %v2943, %v2942[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2945 = llvm.mlir.constant(1 : i64) : i64
%v2946 = llvm.alloca %v2945 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2944, %v2946 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2947 = llvm.load %v2916 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2948 = llvm.getelementptr %v2916[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2949 = llvm.load %v2948 : !llvm.ptr -> i32
%v2950 = llvm.load %v2916 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2951 = llvm.getelementptr %v2916[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2952 = llvm.load %v2951 : !llvm.ptr -> i32
%v2953 = llvm.load %v2946 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2954 = llvm.getelementptr %v2946[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2955 = llvm.load %v2954 : !llvm.ptr -> i32
%v2956 = arith.constant 1 : i32
%v2957 = arith.constant 1 : i32
%v2958 = func.call @tensor_zeros(%v2952, %v2955, %v2957, %v2956) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2959 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2960 = llvm.extractvalue %v2958[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2961 = llvm.insertvalue %v2960, %v2959[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2962 = llvm.extractvalue %v2958[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2963 = llvm.insertvalue %v2962, %v2961[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2964 = llvm.extractvalue %v2958[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2965 = llvm.insertvalue %v2964, %v2963[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2966 = llvm.extractvalue %v2958[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2967 = llvm.insertvalue %v2966, %v2965[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2968 = llvm.extractvalue %v2958[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2969 = llvm.insertvalue %v2968, %v2967[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2970 = llvm.extractvalue %v2958[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2971 = llvm.insertvalue %v2970, %v2969[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2972 = llvm.mlir.constant(1 : i64) : i64
%v2973 = llvm.alloca %v2972 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2971, %v2973 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2974 = llvm.load %v2973 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v2975 = llvm.mlir.constant(1 : i64) : i64
%v2976 = llvm.alloca %v2975 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v2974, %v2976 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v2977 = arith.constant 0 : i32
%v2978 = arith.index_cast %v2977 : i32 to index
%v2979 = arith.index_cast %v2952 : i32 to index
%v2980 = arith.constant 1 : index
%v2981 = arith.constant -1 : index
%v2982 = arith.cmpi sle, %v2978, %v2979 : index
%v2983 = arith.select %v2982, %v2980, %v2981 : index
cf.br ^b118(%v2978 : index)
^b118(%v2984: index):
%v2985 = arith.cmpi slt, %v2984, %v2979 : index
%v2986 = arith.cmpi sgt, %v2984, %v2979 : index
%v2987 = arith.select %v2982, %v2985, %v2986 : i1
cf.cond_br %v2987, ^b119(%v2984 : index), ^b120(%v2984 : index)
^b119(%v2988: index):
%v2989 = arith.constant 0 : i32
%v2990 = arith.index_cast %v2989 : i32 to index
%v2991 = arith.index_cast %v2955 : i32 to index
%v2992 = arith.constant 1 : index
%v2993 = arith.constant -1 : index
%v2994 = arith.cmpi sle, %v2990, %v2991 : index
%v2995 = arith.select %v2994, %v2992, %v2993 : index
cf.br ^b121(%v2990 : index)
^b121(%v2996: index):
%v2997 = arith.cmpi slt, %v2996, %v2991 : index
%v2998 = arith.cmpi sgt, %v2996, %v2991 : index
%v2999 = arith.select %v2994, %v2997, %v2998 : i1
cf.cond_br %v2999, ^b122(%v2996 : index), ^b123(%v2996 : index)
^b122(%v3000: index):
%v3001 = arith.constant 0.0 : f32
%v3002 = llvm.mlir.constant(1 : i64) : i64
%v3003 = llvm.alloca %v3002 x f32 : (i64) -> !llvm.ptr
llvm.store %v3001, %v3003 : f32, !llvm.ptr
%v3004 = arith.constant 0 : i32
%v3005 = arith.index_cast %v3004 : i32 to index
%v3006 = arith.index_cast %v2949 : i32 to index
%v3007 = arith.constant 1 : index
%v3008 = arith.constant -1 : index
%v3009 = arith.cmpi sle, %v3005, %v3006 : index
%v3010 = arith.select %v3009, %v3007, %v3008 : index
cf.br ^b124(%v3005 : index)
^b124(%v3011: index):
%v3012 = arith.cmpi slt, %v3011, %v3006 : index
%v3013 = arith.cmpi sgt, %v3011, %v3006 : index
%v3014 = arith.select %v3009, %v3012, %v3013 : i1
cf.cond_br %v3014, ^b125(%v3011 : index), ^b126(%v3011 : index)
^b125(%v3015: index):
%v3016 = llvm.load %v3003 : !llvm.ptr -> f32
%v3017 = llvm.load %v2916 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3018 = llvm.getelementptr %v2916[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3019 = llvm.load %v3018 : !llvm.ptr -> !llvm.ptr
%v3020 = arith.index_cast %v3015 : index to i32
%v3021 = arith.muli %v3020, %v2952 : i32
%v3022 = arith.index_cast %v2988 : index to i32
%v3023 = arith.addi %v3021, %v3022 : i32
%v3024 = arith.extsi %v3023 : i32 to i64
%v3025 = llvm.getelementptr %v3019[%v3024] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3026 = llvm.load %v3025 : !llvm.ptr -> f32
%v3027 = llvm.load %v2946 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3028 = llvm.getelementptr %v2946[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3029 = llvm.load %v3028 : !llvm.ptr -> !llvm.ptr
%v3030 = arith.index_cast %v3015 : index to i32
%v3031 = arith.muli %v3030, %v2955 : i32
%v3032 = arith.index_cast %v3000 : index to i32
%v3033 = arith.addi %v3031, %v3032 : i32
%v3034 = arith.extsi %v3033 : i32 to i64
%v3035 = llvm.getelementptr %v3029[%v3034] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3036 = llvm.load %v3035 : !llvm.ptr -> f32
%v3037 = arith.mulf %v3026, %v3036 : f32
%v3038 = arith.addf %v3016, %v3037 : f32
llvm.store %v3038, %v3003 : f32, !llvm.ptr
%v3039 = arith.addi %v3015, %v3010 : index
cf.br ^b124(%v3039 : index)
^b126(%v3040: index):
%v3041 = llvm.load %v3003 : !llvm.ptr -> f32
%v3042 = llvm.load %v2976 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3043 = llvm.getelementptr %v2976[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3044 = llvm.load %v3043 : !llvm.ptr -> !llvm.ptr
%v3045 = arith.index_cast %v2988 : index to i32
%v3046 = arith.muli %v3045, %v2955 : i32
%v3047 = arith.index_cast %v3000 : index to i32
%v3048 = arith.addi %v3046, %v3047 : i32
%v3049 = arith.extsi %v3048 : i32 to i64
%v3050 = llvm.getelementptr %v3044[%v3049] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v3041, %v3050 : f32, !llvm.ptr
%v3051 = arith.addi %v3000, %v2995 : index
cf.br ^b121(%v3051 : index)
^b123(%v3052: index):
%v3053 = arith.addi %v2988, %v2983 : index
cf.br ^b118(%v3053 : index)
^b120(%v3054: index):
%v3055 = llvm.load %v2976 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3056 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3057 = llvm.extractvalue %v3055[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3058 = llvm.insertvalue %v3057, %v3056[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3059 = llvm.extractvalue %v3055[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3060 = llvm.insertvalue %v3059, %v3058[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3061 = llvm.extractvalue %v3055[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3062 = llvm.insertvalue %v3061, %v3060[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3063 = llvm.extractvalue %v3055[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3064 = llvm.insertvalue %v3063, %v3062[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3065 = llvm.extractvalue %v3055[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3066 = llvm.insertvalue %v3065, %v3064[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3067 = llvm.extractvalue %v3055[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3068 = llvm.insertvalue %v3067, %v3066[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3069 = llvm.mlir.constant(1 : i64) : i64
%v3070 = llvm.alloca %v3069 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3068, %v3070 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3071 = llvm.load %v3070 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v3071 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_transpose(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v3072 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3073 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3074 = llvm.insertvalue %v3073, %v3072[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3075 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3076 = llvm.insertvalue %v3075, %v3074[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3077 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3078 = llvm.insertvalue %v3077, %v3076[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3079 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3080 = llvm.insertvalue %v3079, %v3078[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3081 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3082 = llvm.insertvalue %v3081, %v3080[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3083 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3084 = llvm.insertvalue %v3083, %v3082[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3085 = llvm.mlir.constant(1 : i64) : i64
%v3086 = llvm.alloca %v3085 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3084, %v3086 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3087 = arith.constant 1 : i32
%v3088 = arith.constant 1 : i32
%v3089 = llvm.load %v3086 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3090 = llvm.getelementptr %v3086[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3091 = llvm.load %v3090 : !llvm.ptr -> i32
%v3092 = llvm.load %v3086 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3093 = llvm.getelementptr %v3086[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3094 = llvm.load %v3093 : !llvm.ptr -> i32
%v3095 = func.call @tensor_zeros(%v3094, %v3091, %v3088, %v3087) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3096 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3097 = llvm.extractvalue %v3095[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3098 = llvm.insertvalue %v3097, %v3096[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3099 = llvm.extractvalue %v3095[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3100 = llvm.insertvalue %v3099, %v3098[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3101 = llvm.extractvalue %v3095[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3102 = llvm.insertvalue %v3101, %v3100[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3103 = llvm.extractvalue %v3095[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3104 = llvm.insertvalue %v3103, %v3102[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3105 = llvm.extractvalue %v3095[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3106 = llvm.insertvalue %v3105, %v3104[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3107 = llvm.extractvalue %v3095[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3108 = llvm.insertvalue %v3107, %v3106[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3109 = llvm.mlir.constant(1 : i64) : i64
%v3110 = llvm.alloca %v3109 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3108, %v3110 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3111 = llvm.load %v3110 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3112 = llvm.mlir.constant(1 : i64) : i64
%v3113 = llvm.alloca %v3112 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3111, %v3113 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3114 = arith.constant 0 : i32
%v3115 = llvm.load %v3086 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3116 = llvm.getelementptr %v3086[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3117 = llvm.load %v3116 : !llvm.ptr -> i32
%v3118 = arith.index_cast %v3114 : i32 to index
%v3119 = arith.index_cast %v3117 : i32 to index
%v3120 = arith.constant 1 : index
%v3121 = arith.constant -1 : index
%v3122 = arith.cmpi sle, %v3118, %v3119 : index
%v3123 = arith.select %v3122, %v3120, %v3121 : index
cf.br ^b127(%v3118 : index)
^b127(%v3124: index):
%v3125 = arith.cmpi slt, %v3124, %v3119 : index
%v3126 = arith.cmpi sgt, %v3124, %v3119 : index
%v3127 = arith.select %v3122, %v3125, %v3126 : i1
cf.cond_br %v3127, ^b128(%v3124 : index), ^b129(%v3124 : index)
^b128(%v3128: index):
%v3129 = arith.constant 0 : i32
%v3130 = llvm.load %v3086 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3131 = llvm.getelementptr %v3086[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3132 = llvm.load %v3131 : !llvm.ptr -> i32
%v3133 = arith.index_cast %v3129 : i32 to index
%v3134 = arith.index_cast %v3132 : i32 to index
%v3135 = arith.constant 1 : index
%v3136 = arith.constant -1 : index
%v3137 = arith.cmpi sle, %v3133, %v3134 : index
%v3138 = arith.select %v3137, %v3135, %v3136 : index
cf.br ^b130(%v3133 : index)
^b130(%v3139: index):
%v3140 = arith.cmpi slt, %v3139, %v3134 : index
%v3141 = arith.cmpi sgt, %v3139, %v3134 : index
%v3142 = arith.select %v3137, %v3140, %v3141 : i1
cf.cond_br %v3142, ^b131(%v3139 : index), ^b132(%v3139 : index)
^b131(%v3143: index):
%v3144 = llvm.load %v3086 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3145 = llvm.getelementptr %v3086[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3146 = llvm.load %v3145 : !llvm.ptr -> !llvm.ptr
%v3147 = llvm.load %v3086 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3148 = llvm.getelementptr %v3086[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3149 = llvm.load %v3148 : !llvm.ptr -> i32
%v3150 = arith.index_cast %v3128 : index to i32
%v3151 = arith.muli %v3150, %v3149 : i32
%v3152 = arith.index_cast %v3143 : index to i32
%v3153 = arith.addi %v3151, %v3152 : i32
%v3154 = arith.extsi %v3153 : i32 to i64
%v3155 = llvm.getelementptr %v3146[%v3154] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3156 = llvm.load %v3155 : !llvm.ptr -> f32
%v3157 = llvm.load %v3113 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3158 = llvm.getelementptr %v3113[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3159 = llvm.load %v3158 : !llvm.ptr -> !llvm.ptr
%v3160 = llvm.load %v3086 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3161 = llvm.getelementptr %v3086[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3162 = llvm.load %v3161 : !llvm.ptr -> i32
%v3163 = arith.index_cast %v3143 : index to i32
%v3164 = arith.muli %v3163, %v3162 : i32
%v3165 = arith.index_cast %v3128 : index to i32
%v3166 = arith.addi %v3164, %v3165 : i32
%v3167 = arith.extsi %v3166 : i32 to i64
%v3168 = llvm.getelementptr %v3159[%v3167] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v3156, %v3168 : f32, !llvm.ptr
%v3169 = arith.addi %v3143, %v3138 : index
cf.br ^b130(%v3169 : index)
^b132(%v3170: index):
%v3171 = arith.addi %v3128, %v3123 : index
cf.br ^b127(%v3171 : index)
^b129(%v3172: index):
%v3173 = llvm.load %v3113 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3174 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3175 = llvm.extractvalue %v3173[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3176 = llvm.insertvalue %v3175, %v3174[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3177 = llvm.extractvalue %v3173[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3178 = llvm.insertvalue %v3177, %v3176[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3179 = llvm.extractvalue %v3173[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3180 = llvm.insertvalue %v3179, %v3178[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3181 = llvm.extractvalue %v3173[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3182 = llvm.insertvalue %v3181, %v3180[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3183 = llvm.extractvalue %v3173[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3184 = llvm.insertvalue %v3183, %v3182[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3185 = llvm.extractvalue %v3173[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3186 = llvm.insertvalue %v3185, %v3184[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3187 = llvm.mlir.constant(1 : i64) : i64
%v3188 = llvm.alloca %v3187 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3186, %v3188 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3189 = llvm.load %v3188 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v3189 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_sum(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> f32 {
%v3190 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3191 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3192 = llvm.insertvalue %v3191, %v3190[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3193 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3194 = llvm.insertvalue %v3193, %v3192[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3195 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3196 = llvm.insertvalue %v3195, %v3194[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3197 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3198 = llvm.insertvalue %v3197, %v3196[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3199 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3200 = llvm.insertvalue %v3199, %v3198[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3201 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3202 = llvm.insertvalue %v3201, %v3200[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3203 = llvm.mlir.constant(1 : i64) : i64
%v3204 = llvm.alloca %v3203 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3202, %v3204 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3205 = arith.constant 0.0 : f32
%v3206 = llvm.mlir.constant(1 : i64) : i64
%v3207 = llvm.alloca %v3206 x f32 : (i64) -> !llvm.ptr
llvm.store %v3205, %v3207 : f32, !llvm.ptr
%v3208 = arith.constant 0 : i32
%v3209 = llvm.load %v3204 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3210 = llvm.getelementptr %v3204[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3211 = llvm.load %v3210 : !llvm.ptr -> i32
%v3212 = arith.index_cast %v3208 : i32 to index
%v3213 = arith.index_cast %v3211 : i32 to index
%v3214 = arith.constant 1 : index
%v3215 = arith.constant -1 : index
%v3216 = arith.cmpi sle, %v3212, %v3213 : index
%v3217 = arith.select %v3216, %v3214, %v3215 : index
cf.br ^b133(%v3212 : index)
^b133(%v3218: index):
%v3219 = arith.cmpi slt, %v3218, %v3213 : index
%v3220 = arith.cmpi sgt, %v3218, %v3213 : index
%v3221 = arith.select %v3216, %v3219, %v3220 : i1
cf.cond_br %v3221, ^b134(%v3218 : index), ^b135(%v3218 : index)
^b134(%v3222: index):
%v3223 = llvm.load %v3207 : !llvm.ptr -> f32
%v3224 = llvm.load %v3204 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3225 = llvm.getelementptr %v3204[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3226 = llvm.load %v3225 : !llvm.ptr -> !llvm.ptr
%v3227 = arith.index_cast %v3222 : index to i64
%v3228 = llvm.getelementptr %v3226[%v3227] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3229 = llvm.load %v3228 : !llvm.ptr -> f32
%v3230 = arith.addf %v3223, %v3229 : f32
llvm.store %v3230, %v3207 : f32, !llvm.ptr
%v3231 = arith.addi %v3222, %v3217 : index
cf.br ^b133(%v3231 : index)
^b135(%v3232: index):
%v3233 = llvm.load %v3207 : !llvm.ptr -> f32
func.return %v3233 : f32
}
func.func @tensor_mean(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> f32 {
%v3234 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3235 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3236 = llvm.insertvalue %v3235, %v3234[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3237 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3238 = llvm.insertvalue %v3237, %v3236[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3239 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3240 = llvm.insertvalue %v3239, %v3238[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3241 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3242 = llvm.insertvalue %v3241, %v3240[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3243 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3244 = llvm.insertvalue %v3243, %v3242[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3245 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3246 = llvm.insertvalue %v3245, %v3244[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3247 = llvm.mlir.constant(1 : i64) : i64
%v3248 = llvm.alloca %v3247 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3246, %v3248 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3249 = llvm.load %v3248 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3250 = func.call @tensor_sum(%v3249) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> f32
%v3251 = llvm.load %v3248 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3252 = llvm.getelementptr %v3248[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3253 = llvm.load %v3252 : !llvm.ptr -> i32
%v3254 = arith.sitofp %v3253 : i32 to f32
%v3255 = arith.divf %v3250, %v3254 : f32
func.return %v3255 : f32
}
func.func @tensor_max(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> f32 {
%v3256 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3257 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3258 = llvm.insertvalue %v3257, %v3256[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3259 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3260 = llvm.insertvalue %v3259, %v3258[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3261 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3262 = llvm.insertvalue %v3261, %v3260[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3263 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3264 = llvm.insertvalue %v3263, %v3262[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3265 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3266 = llvm.insertvalue %v3265, %v3264[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3267 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3268 = llvm.insertvalue %v3267, %v3266[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3269 = llvm.mlir.constant(1 : i64) : i64
%v3270 = llvm.alloca %v3269 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3268, %v3270 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3271 = llvm.load %v3270 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3272 = llvm.getelementptr %v3270[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3273 = llvm.load %v3272 : !llvm.ptr -> !llvm.ptr
%v3274 = arith.constant 0 : i32
%v3275 = arith.extsi %v3274 : i32 to i64
%v3276 = llvm.getelementptr %v3273[%v3275] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3277 = llvm.load %v3276 : !llvm.ptr -> f32
%v3278 = llvm.mlir.constant(1 : i64) : i64
%v3279 = llvm.alloca %v3278 x f32 : (i64) -> !llvm.ptr
llvm.store %v3277, %v3279 : f32, !llvm.ptr
%v3280 = arith.constant 1 : i32
%v3281 = llvm.load %v3270 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3282 = llvm.getelementptr %v3270[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3283 = llvm.load %v3282 : !llvm.ptr -> i32
%v3284 = arith.index_cast %v3280 : i32 to index
%v3285 = arith.index_cast %v3283 : i32 to index
%v3286 = arith.constant 1 : index
%v3287 = arith.constant -1 : index
%v3288 = arith.cmpi sle, %v3284, %v3285 : index
%v3289 = arith.select %v3288, %v3286, %v3287 : index
cf.br ^b136(%v3284 : index)
^b136(%v3290: index):
%v3291 = arith.cmpi slt, %v3290, %v3285 : index
%v3292 = arith.cmpi sgt, %v3290, %v3285 : index
%v3293 = arith.select %v3288, %v3291, %v3292 : i1
cf.cond_br %v3293, ^b137(%v3290 : index), ^b138(%v3290 : index)
^b137(%v3294: index):
%v3295 = llvm.load %v3270 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3296 = llvm.getelementptr %v3270[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3297 = llvm.load %v3296 : !llvm.ptr -> !llvm.ptr
%v3298 = arith.index_cast %v3294 : index to i64
%v3299 = llvm.getelementptr %v3297[%v3298] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3300 = llvm.load %v3299 : !llvm.ptr -> f32
%v3301 = llvm.load %v3279 : !llvm.ptr -> f32
%v3302 = arith.cmpf ogt, %v3300, %v3301 : f32
cf.cond_br %v3302, ^b139, ^b140
^b139:
%v3303 = llvm.load %v3270 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3304 = llvm.getelementptr %v3270[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3305 = llvm.load %v3304 : !llvm.ptr -> !llvm.ptr
%v3306 = arith.index_cast %v3294 : index to i64
%v3307 = llvm.getelementptr %v3305[%v3306] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3308 = llvm.load %v3307 : !llvm.ptr -> f32
llvm.store %v3308, %v3279 : f32, !llvm.ptr
cf.br ^b141
^b140:
cf.br ^b141
^b141:
%v3309 = arith.addi %v3294, %v3289 : index
cf.br ^b136(%v3309 : index)
^b138(%v3310: index):
%v3311 = llvm.load %v3279 : !llvm.ptr -> f32
func.return %v3311 : f32
}
func.func @tensor_min(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> f32 {
%v3312 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3313 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3314 = llvm.insertvalue %v3313, %v3312[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3315 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3316 = llvm.insertvalue %v3315, %v3314[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3317 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3318 = llvm.insertvalue %v3317, %v3316[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3319 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3320 = llvm.insertvalue %v3319, %v3318[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3321 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3322 = llvm.insertvalue %v3321, %v3320[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3323 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3324 = llvm.insertvalue %v3323, %v3322[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3325 = llvm.mlir.constant(1 : i64) : i64
%v3326 = llvm.alloca %v3325 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3324, %v3326 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3327 = llvm.load %v3326 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3328 = llvm.getelementptr %v3326[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3329 = llvm.load %v3328 : !llvm.ptr -> !llvm.ptr
%v3330 = arith.constant 0 : i32
%v3331 = arith.extsi %v3330 : i32 to i64
%v3332 = llvm.getelementptr %v3329[%v3331] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3333 = llvm.load %v3332 : !llvm.ptr -> f32
%v3334 = llvm.mlir.constant(1 : i64) : i64
%v3335 = llvm.alloca %v3334 x f32 : (i64) -> !llvm.ptr
llvm.store %v3333, %v3335 : f32, !llvm.ptr
%v3336 = arith.constant 1 : i32
%v3337 = llvm.load %v3326 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3338 = llvm.getelementptr %v3326[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3339 = llvm.load %v3338 : !llvm.ptr -> i32
%v3340 = arith.index_cast %v3336 : i32 to index
%v3341 = arith.index_cast %v3339 : i32 to index
%v3342 = arith.constant 1 : index
%v3343 = arith.constant -1 : index
%v3344 = arith.cmpi sle, %v3340, %v3341 : index
%v3345 = arith.select %v3344, %v3342, %v3343 : index
cf.br ^b142(%v3340 : index)
^b142(%v3346: index):
%v3347 = arith.cmpi slt, %v3346, %v3341 : index
%v3348 = arith.cmpi sgt, %v3346, %v3341 : index
%v3349 = arith.select %v3344, %v3347, %v3348 : i1
cf.cond_br %v3349, ^b143(%v3346 : index), ^b144(%v3346 : index)
^b143(%v3350: index):
%v3351 = llvm.load %v3326 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3352 = llvm.getelementptr %v3326[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3353 = llvm.load %v3352 : !llvm.ptr -> !llvm.ptr
%v3354 = arith.index_cast %v3350 : index to i64
%v3355 = llvm.getelementptr %v3353[%v3354] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3356 = llvm.load %v3355 : !llvm.ptr -> f32
%v3357 = llvm.load %v3335 : !llvm.ptr -> f32
%v3358 = arith.cmpf olt, %v3356, %v3357 : f32
cf.cond_br %v3358, ^b145, ^b146
^b145:
%v3359 = llvm.load %v3326 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3360 = llvm.getelementptr %v3326[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3361 = llvm.load %v3360 : !llvm.ptr -> !llvm.ptr
%v3362 = arith.index_cast %v3350 : index to i64
%v3363 = llvm.getelementptr %v3361[%v3362] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3364 = llvm.load %v3363 : !llvm.ptr -> f32
llvm.store %v3364, %v3335 : f32, !llvm.ptr
cf.br ^b147
^b146:
cf.br ^b147
^b147:
%v3365 = arith.addi %v3350, %v3345 : index
cf.br ^b142(%v3365 : index)
^b144(%v3366: index):
%v3367 = llvm.load %v3335 : !llvm.ptr -> f32
func.return %v3367 : f32
}
func.func @tensor_argmax(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> i32 {
%v3368 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3369 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3370 = llvm.insertvalue %v3369, %v3368[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3371 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3372 = llvm.insertvalue %v3371, %v3370[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3373 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3374 = llvm.insertvalue %v3373, %v3372[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3375 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3376 = llvm.insertvalue %v3375, %v3374[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3377 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3378 = llvm.insertvalue %v3377, %v3376[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3379 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3380 = llvm.insertvalue %v3379, %v3378[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3381 = llvm.mlir.constant(1 : i64) : i64
%v3382 = llvm.alloca %v3381 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3380, %v3382 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3383 = arith.constant 0 : i32
%v3384 = llvm.mlir.constant(1 : i64) : i64
%v3385 = llvm.alloca %v3384 x i32 : (i64) -> !llvm.ptr
llvm.store %v3383, %v3385 : i32, !llvm.ptr
%v3386 = llvm.load %v3382 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3387 = llvm.getelementptr %v3382[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3388 = llvm.load %v3387 : !llvm.ptr -> !llvm.ptr
%v3389 = arith.constant 0 : i32
%v3390 = arith.extsi %v3389 : i32 to i64
%v3391 = llvm.getelementptr %v3388[%v3390] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3392 = llvm.load %v3391 : !llvm.ptr -> f32
%v3393 = llvm.mlir.constant(1 : i64) : i64
%v3394 = llvm.alloca %v3393 x f32 : (i64) -> !llvm.ptr
llvm.store %v3392, %v3394 : f32, !llvm.ptr
%v3395 = arith.constant 1 : i32
%v3396 = llvm.load %v3382 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3397 = llvm.getelementptr %v3382[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3398 = llvm.load %v3397 : !llvm.ptr -> i32
%v3399 = arith.index_cast %v3395 : i32 to index
%v3400 = arith.index_cast %v3398 : i32 to index
%v3401 = arith.constant 1 : index
%v3402 = arith.constant -1 : index
%v3403 = arith.cmpi sle, %v3399, %v3400 : index
%v3404 = arith.select %v3403, %v3401, %v3402 : index
cf.br ^b148(%v3399 : index)
^b148(%v3405: index):
%v3406 = arith.cmpi slt, %v3405, %v3400 : index
%v3407 = arith.cmpi sgt, %v3405, %v3400 : index
%v3408 = arith.select %v3403, %v3406, %v3407 : i1
cf.cond_br %v3408, ^b149(%v3405 : index), ^b150(%v3405 : index)
^b149(%v3409: index):
%v3410 = llvm.load %v3382 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3411 = llvm.getelementptr %v3382[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3412 = llvm.load %v3411 : !llvm.ptr -> !llvm.ptr
%v3413 = arith.index_cast %v3409 : index to i64
%v3414 = llvm.getelementptr %v3412[%v3413] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3415 = llvm.load %v3414 : !llvm.ptr -> f32
%v3416 = llvm.load %v3394 : !llvm.ptr -> f32
%v3417 = arith.cmpf ogt, %v3415, %v3416 : f32
cf.cond_br %v3417, ^b151, ^b152
^b151:
%v3418 = llvm.load %v3382 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3419 = llvm.getelementptr %v3382[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3420 = llvm.load %v3419 : !llvm.ptr -> !llvm.ptr
%v3421 = arith.index_cast %v3409 : index to i64
%v3422 = llvm.getelementptr %v3420[%v3421] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3423 = llvm.load %v3422 : !llvm.ptr -> f32
llvm.store %v3423, %v3394 : f32, !llvm.ptr
%v3424 = arith.index_cast %v3409 : index to i32
llvm.store %v3424, %v3385 : i32, !llvm.ptr
cf.br ^b153
^b152:
cf.br ^b153
^b153:
%v3425 = arith.addi %v3409, %v3404 : index
cf.br ^b148(%v3425 : index)
^b150(%v3426: index):
%v3427 = llvm.load %v3385 : !llvm.ptr -> i32
func.return %v3427 : i32
}
func.func @tensor_copy(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> {
%v3428 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3429 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3430 = llvm.insertvalue %v3429, %v3428[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3431 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3432 = llvm.insertvalue %v3431, %v3430[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3433 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3434 = llvm.insertvalue %v3433, %v3432[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3435 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3436 = llvm.insertvalue %v3435, %v3434[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3437 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3438 = llvm.insertvalue %v3437, %v3436[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3439 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3440 = llvm.insertvalue %v3439, %v3438[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3441 = llvm.mlir.constant(1 : i64) : i64
%v3442 = llvm.alloca %v3441 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3440, %v3442 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3443 = llvm.load %v3442 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3444 = llvm.getelementptr %v3442[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3445 = llvm.load %v3444 : !llvm.ptr -> i32
%v3446 = llvm.load %v3442 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3447 = llvm.getelementptr %v3442[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3448 = llvm.load %v3447 : !llvm.ptr -> i32
%v3449 = llvm.load %v3442 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3450 = llvm.getelementptr %v3442[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3451 = llvm.load %v3450 : !llvm.ptr -> i32
%v3452 = llvm.load %v3442 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3453 = llvm.getelementptr %v3442[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3454 = llvm.load %v3453 : !llvm.ptr -> i32
%v3455 = func.call @tensor_zeros(%v3454, %v3451, %v3448, %v3445) : (i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3456 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3457 = llvm.extractvalue %v3455[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3458 = llvm.insertvalue %v3457, %v3456[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3459 = llvm.extractvalue %v3455[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3460 = llvm.insertvalue %v3459, %v3458[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3461 = llvm.extractvalue %v3455[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3462 = llvm.insertvalue %v3461, %v3460[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3463 = llvm.extractvalue %v3455[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3464 = llvm.insertvalue %v3463, %v3462[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3465 = llvm.extractvalue %v3455[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3466 = llvm.insertvalue %v3465, %v3464[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3467 = llvm.extractvalue %v3455[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3468 = llvm.insertvalue %v3467, %v3466[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3469 = llvm.mlir.constant(1 : i64) : i64
%v3470 = llvm.alloca %v3469 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3468, %v3470 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3471 = llvm.load %v3470 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3472 = llvm.mlir.constant(1 : i64) : i64
%v3473 = llvm.alloca %v3472 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3471, %v3473 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3474 = arith.constant 0 : i32
%v3475 = llvm.load %v3442 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3476 = llvm.getelementptr %v3442[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3477 = llvm.load %v3476 : !llvm.ptr -> i32
%v3478 = arith.index_cast %v3474 : i32 to index
%v3479 = arith.index_cast %v3477 : i32 to index
%v3480 = arith.constant 1 : index
%v3481 = arith.constant -1 : index
%v3482 = arith.cmpi sle, %v3478, %v3479 : index
%v3483 = arith.select %v3482, %v3480, %v3481 : index
cf.br ^b154(%v3478 : index)
^b154(%v3484: index):
%v3485 = arith.cmpi slt, %v3484, %v3479 : index
%v3486 = arith.cmpi sgt, %v3484, %v3479 : index
%v3487 = arith.select %v3482, %v3485, %v3486 : i1
cf.cond_br %v3487, ^b155(%v3484 : index), ^b156(%v3484 : index)
^b155(%v3488: index):
%v3489 = llvm.load %v3442 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3490 = llvm.getelementptr %v3442[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3491 = llvm.load %v3490 : !llvm.ptr -> !llvm.ptr
%v3492 = arith.index_cast %v3488 : index to i64
%v3493 = llvm.getelementptr %v3491[%v3492] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3494 = llvm.load %v3493 : !llvm.ptr -> f32
%v3495 = llvm.load %v3473 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3496 = llvm.getelementptr %v3473[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3497 = llvm.load %v3496 : !llvm.ptr -> !llvm.ptr
%v3498 = arith.index_cast %v3488 : index to i64
%v3499 = llvm.getelementptr %v3497[%v3498] : (!llvm.ptr, i64) -> !llvm.ptr, f32
llvm.store %v3494, %v3499 : f32, !llvm.ptr
%v3500 = arith.addi %v3488, %v3483 : index
cf.br ^b154(%v3500 : index)
^b156(%v3501: index):
%v3502 = llvm.load %v3473 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3503 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3504 = llvm.extractvalue %v3502[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3505 = llvm.insertvalue %v3504, %v3503[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3506 = llvm.extractvalue %v3502[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3507 = llvm.insertvalue %v3506, %v3505[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3508 = llvm.extractvalue %v3502[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3509 = llvm.insertvalue %v3508, %v3507[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3510 = llvm.extractvalue %v3502[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3511 = llvm.insertvalue %v3510, %v3509[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3512 = llvm.extractvalue %v3502[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3513 = llvm.insertvalue %v3512, %v3511[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3514 = llvm.extractvalue %v3502[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3515 = llvm.insertvalue %v3514, %v3513[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3516 = llvm.mlir.constant(1 : i64) : i64
%v3517 = llvm.alloca %v3516 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3515, %v3517 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3518 = llvm.load %v3517 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.return %v3518 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
}
func.func @tensor_print(%arg0: !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> () {
%v3519 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3520 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3521 = llvm.insertvalue %v3520, %v3519[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3522 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3523 = llvm.insertvalue %v3522, %v3521[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3524 = llvm.extractvalue %arg0[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3525 = llvm.insertvalue %v3524, %v3523[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3526 = llvm.extractvalue %arg0[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3527 = llvm.insertvalue %v3526, %v3525[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3528 = llvm.extractvalue %arg0[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3529 = llvm.insertvalue %v3528, %v3527[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3530 = llvm.extractvalue %arg0[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3531 = llvm.insertvalue %v3530, %v3529[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3532 = llvm.mlir.constant(1 : i64) : i64
%v3533 = llvm.alloca %v3532 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3531, %v3533 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3534 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v3535 = llvm.call @printf(%v3534) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3536 = arith.constant 0 : i32
%v3537 = llvm.load %v3533 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3538 = llvm.getelementptr %v3533[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3539 = llvm.load %v3538 : !llvm.ptr -> i32
%v3540 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v3541 = llvm.call @printf(%v3540, %v3539) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v3542 = arith.constant 0 : i32
%v3543 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v3544 = llvm.call @printf(%v3543) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3545 = arith.constant 0 : i32
%v3546 = llvm.load %v3533 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3547 = llvm.getelementptr %v3533[0, 3] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3548 = llvm.load %v3547 : !llvm.ptr -> i32
%v3549 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v3550 = llvm.call @printf(%v3549, %v3548) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v3551 = arith.constant 0 : i32
%v3552 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v3553 = llvm.call @printf(%v3552) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3554 = arith.constant 0 : i32
%v3555 = llvm.load %v3533 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3556 = llvm.getelementptr %v3533[0, 4] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3557 = llvm.load %v3556 : !llvm.ptr -> i32
%v3558 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v3559 = llvm.call @printf(%v3558, %v3557) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v3560 = arith.constant 0 : i32
%v3561 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v3562 = llvm.call @printf(%v3561) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3563 = arith.constant 0 : i32
%v3564 = llvm.load %v3533 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3565 = llvm.getelementptr %v3533[0, 5] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3566 = llvm.load %v3565 : !llvm.ptr -> i32
%v3567 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v3568 = llvm.call @printf(%v3567, %v3566) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v3569 = arith.constant 0 : i32
%v3570 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v3571 = llvm.call @printf(%v3570) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3572 = arith.constant 0 : i32
%v3573 = llvm.load %v3533 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3574 = llvm.getelementptr %v3533[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3575 = llvm.load %v3574 : !llvm.ptr -> i32
%v3576 = llvm.mlir.constant(1 : i64) : i64
%v3577 = llvm.alloca %v3576 x i32 : (i64) -> !llvm.ptr
llvm.store %v3575, %v3577 : i32, !llvm.ptr
%v3578 = llvm.load %v3577 : !llvm.ptr -> i32
%v3579 = arith.constant 10 : i32
%v3580 = arith.cmpi sgt, %v3578, %v3579 : i32
cf.cond_br %v3580, ^b157, ^b158
^b157:
%v3581 = arith.constant 10 : i32
llvm.store %v3581, %v3577 : i32, !llvm.ptr
cf.br ^b159
^b158:
cf.br ^b159
^b159:
%v3582 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v3583 = llvm.call @printf(%v3582) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3584 = arith.constant 0 : i32
%v3585 = arith.constant 0 : i32
%v3586 = llvm.load %v3577 : !llvm.ptr -> i32
%v3587 = arith.index_cast %v3585 : i32 to index
%v3588 = arith.index_cast %v3586 : i32 to index
%v3589 = arith.constant 1 : index
%v3590 = arith.constant -1 : index
%v3591 = arith.cmpi sle, %v3587, %v3588 : index
%v3592 = arith.select %v3591, %v3589, %v3590 : index
cf.br ^b160(%v3587 : index)
^b160(%v3593: index):
%v3594 = arith.cmpi slt, %v3593, %v3588 : index
%v3595 = arith.cmpi sgt, %v3593, %v3588 : index
%v3596 = arith.select %v3591, %v3594, %v3595 : i1
cf.cond_br %v3596, ^b161(%v3593 : index), ^b162(%v3593 : index)
^b161(%v3597: index):
%v3598 = llvm.load %v3533 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3599 = llvm.getelementptr %v3533[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3600 = llvm.load %v3599 : !llvm.ptr -> !llvm.ptr
%v3601 = arith.index_cast %v3597 : index to i64
%v3602 = llvm.getelementptr %v3600[%v3601] : (!llvm.ptr, i64) -> !llvm.ptr, f32
%v3603 = llvm.load %v3602 : !llvm.ptr -> f32
%v3604 = llvm.mlir.addressof @str_5 : !llvm.ptr
%v3605 = arith.extf %v3603 : f32 to f64
%v3606 = llvm.call @printf(%v3604, %v3605) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v3607 = arith.constant 0 : i32
%v3608 = llvm.load %v3577 : !llvm.ptr -> i32
%v3609 = arith.constant 1 : i32
%v3610 = arith.subi %v3608, %v3609 : i32
%v3611 = arith.index_cast %v3597 : index to i32
%v3612 = arith.cmpi slt, %v3611, %v3610 : i32
cf.cond_br %v3612, ^b163, ^b164
^b163:
%v3613 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v3614 = llvm.call @printf(%v3613) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3615 = arith.constant 0 : i32
cf.br ^b165
^b164:
cf.br ^b165
^b165:
%v3616 = arith.addi %v3597, %v3592 : index
cf.br ^b160(%v3616 : index)
^b162(%v3617: index):
%v3618 = llvm.load %v3533 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3619 = llvm.getelementptr %v3533[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3620 = llvm.load %v3619 : !llvm.ptr -> i32
%v3621 = arith.constant 10 : i32
%v3622 = arith.cmpi sgt, %v3620, %v3621 : i32
cf.cond_br %v3622, ^b166, ^b167
^b166:
%v3623 = llvm.mlir.addressof @str_6 : !llvm.ptr
%v3624 = llvm.call @printf(%v3623) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3625 = arith.constant 0 : i32
cf.br ^b168
^b167:
cf.br ^b168
^b168:
%v3626 = llvm.mlir.addressof @str_7 : !llvm.ptr
%v3627 = llvm.call @printf(%v3626) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3628 = arith.constant 0 : i32
func.return
}
func.func @bench_matmul(%arg0: i32, %arg1: i32, %arg2: i32) -> f32 {
%v3629 = arith.constant 42 : i32
%v3630 = arith.constant 1 : i32
%v3631 = arith.constant 1 : i32
%v3632 = func.call @tensor_rand(%arg0, %arg1, %v3631, %v3630, %v3629) : (i32, i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3633 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3634 = llvm.extractvalue %v3632[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3635 = llvm.insertvalue %v3634, %v3633[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3636 = llvm.extractvalue %v3632[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3637 = llvm.insertvalue %v3636, %v3635[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3638 = llvm.extractvalue %v3632[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3639 = llvm.insertvalue %v3638, %v3637[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3640 = llvm.extractvalue %v3632[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3641 = llvm.insertvalue %v3640, %v3639[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3642 = llvm.extractvalue %v3632[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3643 = llvm.insertvalue %v3642, %v3641[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3644 = llvm.extractvalue %v3632[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3645 = llvm.insertvalue %v3644, %v3643[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3646 = llvm.mlir.constant(1 : i64) : i64
%v3647 = llvm.alloca %v3646 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3645, %v3647 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3648 = llvm.load %v3647 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3649 = llvm.mlir.constant(1 : i64) : i64
%v3650 = llvm.alloca %v3649 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3648, %v3650 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3651 = arith.constant 99 : i32
%v3652 = arith.constant 1 : i32
%v3653 = arith.constant 1 : i32
%v3654 = func.call @tensor_rand(%arg1, %arg2, %v3653, %v3652, %v3651) : (i32, i32, i32, i32, i32) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3655 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3656 = llvm.extractvalue %v3654[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3657 = llvm.insertvalue %v3656, %v3655[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3658 = llvm.extractvalue %v3654[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3659 = llvm.insertvalue %v3658, %v3657[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3660 = llvm.extractvalue %v3654[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3661 = llvm.insertvalue %v3660, %v3659[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3662 = llvm.extractvalue %v3654[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3663 = llvm.insertvalue %v3662, %v3661[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3664 = llvm.extractvalue %v3654[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3665 = llvm.insertvalue %v3664, %v3663[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3666 = llvm.extractvalue %v3654[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3667 = llvm.insertvalue %v3666, %v3665[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3668 = llvm.mlir.constant(1 : i64) : i64
%v3669 = llvm.alloca %v3668 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3667, %v3669 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3670 = llvm.load %v3669 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3671 = llvm.mlir.constant(1 : i64) : i64
%v3672 = llvm.alloca %v3671 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3670, %v3672 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3673 = llvm.load %v3672 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3674 = llvm.load %v3650 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3675 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3676 = llvm.extractvalue %v3673[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3677 = llvm.insertvalue %v3676, %v3675[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3678 = llvm.extractvalue %v3673[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3679 = llvm.insertvalue %v3678, %v3677[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3680 = llvm.extractvalue %v3673[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3681 = llvm.insertvalue %v3680, %v3679[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3682 = llvm.extractvalue %v3673[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3683 = llvm.insertvalue %v3682, %v3681[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3684 = llvm.extractvalue %v3673[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3685 = llvm.insertvalue %v3684, %v3683[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3686 = llvm.extractvalue %v3673[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3687 = llvm.insertvalue %v3686, %v3685[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3688 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3689 = llvm.extractvalue %v3674[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3690 = llvm.insertvalue %v3689, %v3688[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3691 = llvm.extractvalue %v3674[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3692 = llvm.insertvalue %v3691, %v3690[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3693 = llvm.extractvalue %v3674[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3694 = llvm.insertvalue %v3693, %v3692[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3695 = llvm.extractvalue %v3674[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3696 = llvm.insertvalue %v3695, %v3694[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3697 = llvm.extractvalue %v3674[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3698 = llvm.insertvalue %v3697, %v3696[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3699 = llvm.extractvalue %v3674[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3700 = llvm.insertvalue %v3699, %v3698[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3701 = func.call @tensor_matmul(%v3700, %v3687) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3702 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3703 = llvm.extractvalue %v3701[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3704 = llvm.insertvalue %v3703, %v3702[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3705 = llvm.extractvalue %v3701[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3706 = llvm.insertvalue %v3705, %v3704[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3707 = llvm.extractvalue %v3701[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3708 = llvm.insertvalue %v3707, %v3706[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3709 = llvm.extractvalue %v3701[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3710 = llvm.insertvalue %v3709, %v3708[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3711 = llvm.mlir.constant(1 : i64) : i64
%v3712 = llvm.alloca %v3711 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3710, %v3712 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3713 = llvm.load %v3712 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3714 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3715 = llvm.extractvalue %v3700[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3716 = llvm.insertvalue %v3715, %v3714[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3717 = llvm.extractvalue %v3700[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3718 = llvm.insertvalue %v3717, %v3716[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3719 = llvm.extractvalue %v3700[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3720 = llvm.insertvalue %v3719, %v3718[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3721 = llvm.extractvalue %v3700[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3722 = llvm.insertvalue %v3721, %v3720[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3723 = llvm.extractvalue %v3700[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3724 = llvm.insertvalue %v3723, %v3722[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3725 = llvm.extractvalue %v3700[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3726 = llvm.insertvalue %v3725, %v3724[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3726, %v3650 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3727 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3728 = llvm.extractvalue %v3687[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3729 = llvm.insertvalue %v3728, %v3727[0] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3730 = llvm.extractvalue %v3687[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3731 = llvm.insertvalue %v3730, %v3729[1] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3732 = llvm.extractvalue %v3687[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3733 = llvm.insertvalue %v3732, %v3731[2] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3734 = llvm.extractvalue %v3687[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3735 = llvm.insertvalue %v3734, %v3733[3] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3736 = llvm.extractvalue %v3687[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3737 = llvm.insertvalue %v3736, %v3735[4] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3738 = llvm.extractvalue %v3687[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3739 = llvm.insertvalue %v3738, %v3737[5] : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
llvm.store %v3739, %v3672 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3740 = llvm.mlir.constant(1 : i64) : i64
%v3741 = llvm.alloca %v3740 x !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v3713, %v3741 : !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>, !llvm.ptr
%v3742 = llvm.load %v3741 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
%v3743 = func.call @tensor_sum(%v3742) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> f32
%v3744 = llvm.load %v3650 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.call @tensor_free(%v3744) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> ()
%v3745 = llvm.load %v3672 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.call @tensor_free(%v3745) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> ()
%v3746 = llvm.load %v3741 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>
func.call @tensor_free(%v3746) : (!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>) -> ()
func.return %v3743 : f32
}
func.func @main() -> i32 {
%v3747 = llvm.mlir.addressof @str_8 : !llvm.ptr
%v3748 = llvm.call @printf(%v3747) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3749 = arith.constant 0 : i32
%v3750 = llvm.mlir.addressof @str_9 : !llvm.ptr
%v3751 = llvm.call @printf(%v3750) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3752 = arith.constant 0 : i32
%v3753 = arith.constant 64 : i32
%v3754 = arith.constant 64 : i32
%v3755 = arith.constant 64 : i32
%v3756 = func.call @bench_matmul(%v3753, %v3754, %v3755) : (i32, i32, i32) -> f32
%v3757 = arith.constant 128 : i32
%v3758 = arith.constant 128 : i32
%v3759 = arith.constant 128 : i32
%v3760 = func.call @bench_matmul(%v3757, %v3758, %v3759) : (i32, i32, i32) -> f32
%v3761 = llvm.mlir.addressof @str_10 : !llvm.ptr
%v3762 = llvm.call @printf(%v3761) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3763 = arith.constant 0 : i32
%v3764 = llvm.mlir.addressof @str_5 : !llvm.ptr
%v3765 = arith.extf %v3756 : f32 to f64
%v3766 = llvm.call @printf(%v3764, %v3765) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v3767 = arith.constant 0 : i32
%v3768 = llvm.mlir.addressof @str_11 : !llvm.ptr
%v3769 = llvm.call @printf(%v3768) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3770 = arith.constant 0 : i32
%v3771 = llvm.mlir.addressof @str_5 : !llvm.ptr
%v3772 = arith.extf %v3760 : f32 to f64
%v3773 = llvm.call @printf(%v3771, %v3772) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v3774 = arith.constant 0 : i32
%v3775 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v3776 = llvm.call @printf(%v3775) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v3777 = arith.constant 0 : i32
%v3778 = arith.constant 0 : i32
func.return %v3778 : i32
}
}
