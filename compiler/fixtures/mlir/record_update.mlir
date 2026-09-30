module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_1("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
// Struct: Point
// Fields:
//   x: i32
//   y: i32
//   w: f64
func.func @moved(%arg0: !llvm.struct<(i32, i32, f64)>, %arg1: i32) -> !llvm.struct<(i32, i32, f64)> {
%v1 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v2 = llvm.extractvalue %arg0[0] : !llvm.struct<(i32, i32, f64)>
%v3 = llvm.insertvalue %v2, %v1[0] : !llvm.struct<(i32, i32, f64)>
%v4 = llvm.extractvalue %arg0[1] : !llvm.struct<(i32, i32, f64)>
%v5 = llvm.insertvalue %v4, %v3[1] : !llvm.struct<(i32, i32, f64)>
%v6 = llvm.extractvalue %arg0[2] : !llvm.struct<(i32, i32, f64)>
%v7 = llvm.insertvalue %v6, %v5[2] : !llvm.struct<(i32, i32, f64)>
%v8 = llvm.mlir.constant(1 : i64) : i64
%v9 = llvm.alloca %v8 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v7, %v9 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v10 = llvm.load %v9 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v11 = llvm.load %v9 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v12 = llvm.getelementptr %v9[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v13 = llvm.load %v12 : !llvm.ptr -> i32
%v14 = arith.addi %v13, %arg1 : i32
%v15 = llvm.insertvalue %v14, %v10[0] : !llvm.struct<(i32, i32, f64)>
%v16 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v17 = llvm.extractvalue %v15[0] : !llvm.struct<(i32, i32, f64)>
%v18 = llvm.insertvalue %v17, %v16[0] : !llvm.struct<(i32, i32, f64)>
%v19 = llvm.extractvalue %v15[1] : !llvm.struct<(i32, i32, f64)>
%v20 = llvm.insertvalue %v19, %v18[1] : !llvm.struct<(i32, i32, f64)>
%v21 = llvm.extractvalue %v15[2] : !llvm.struct<(i32, i32, f64)>
%v22 = llvm.insertvalue %v21, %v20[2] : !llvm.struct<(i32, i32, f64)>
%v23 = llvm.mlir.constant(1 : i64) : i64
%v24 = llvm.alloca %v23 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v22, %v24 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v25 = llvm.load %v24 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
func.return %v25 : !llvm.struct<(i32, i32, f64)>
}
func.func @make() -> !llvm.struct<(i32, i32, f64)> {
%v26 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v27 = arith.constant 1 : i32
%v28 = llvm.insertvalue %v27, %v26[0] : !llvm.struct<(i32, i32, f64)>
%v29 = arith.constant 2 : i32
%v30 = llvm.insertvalue %v29, %v28[1] : !llvm.struct<(i32, i32, f64)>
%v31 = arith.constant 0.5 : f64
%v32 = llvm.insertvalue %v31, %v30[2] : !llvm.struct<(i32, i32, f64)>
%v33 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v34 = llvm.extractvalue %v32[0] : !llvm.struct<(i32, i32, f64)>
%v35 = llvm.insertvalue %v34, %v33[0] : !llvm.struct<(i32, i32, f64)>
%v36 = llvm.extractvalue %v32[1] : !llvm.struct<(i32, i32, f64)>
%v37 = llvm.insertvalue %v36, %v35[1] : !llvm.struct<(i32, i32, f64)>
%v38 = llvm.extractvalue %v32[2] : !llvm.struct<(i32, i32, f64)>
%v39 = llvm.insertvalue %v38, %v37[2] : !llvm.struct<(i32, i32, f64)>
%v40 = llvm.mlir.constant(1 : i64) : i64
%v41 = llvm.alloca %v40 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v39, %v41 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v42 = llvm.load %v41 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
func.return %v42 : !llvm.struct<(i32, i32, f64)>
}
func.func @main() -> i32 {
%v43 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v44 = arith.constant 3 : i32
%v45 = llvm.insertvalue %v44, %v43[0] : !llvm.struct<(i32, i32, f64)>
%v46 = arith.constant 4 : i32
%v47 = llvm.insertvalue %v46, %v45[1] : !llvm.struct<(i32, i32, f64)>
%v48 = arith.constant 1.5 : f64
%v49 = llvm.insertvalue %v48, %v47[2] : !llvm.struct<(i32, i32, f64)>
%v50 = llvm.mlir.constant(1 : i64) : i64
%v51 = llvm.alloca %v50 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v49, %v51 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v52 = llvm.load %v51 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v53 = arith.constant 40 : i32
%v54 = llvm.insertvalue %v53, %v52[1] : !llvm.struct<(i32, i32, f64)>
%v55 = llvm.mlir.constant(1 : i64) : i64
%v56 = llvm.alloca %v55 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v54, %v56 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v57 = llvm.load %v56 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v58 = arith.constant 10 : i32
%v59 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v60 = llvm.extractvalue %v57[0] : !llvm.struct<(i32, i32, f64)>
%v61 = llvm.insertvalue %v60, %v59[0] : !llvm.struct<(i32, i32, f64)>
%v62 = llvm.extractvalue %v57[1] : !llvm.struct<(i32, i32, f64)>
%v63 = llvm.insertvalue %v62, %v61[1] : !llvm.struct<(i32, i32, f64)>
%v64 = llvm.extractvalue %v57[2] : !llvm.struct<(i32, i32, f64)>
%v65 = llvm.insertvalue %v64, %v63[2] : !llvm.struct<(i32, i32, f64)>
%v66 = func.call @moved(%v65, %v58) : (!llvm.struct<(i32, i32, f64)>, i32) -> !llvm.struct<(i32, i32, f64)>
%v67 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v68 = llvm.extractvalue %v66[0] : !llvm.struct<(i32, i32, f64)>
%v69 = llvm.insertvalue %v68, %v67[0] : !llvm.struct<(i32, i32, f64)>
%v70 = llvm.extractvalue %v66[1] : !llvm.struct<(i32, i32, f64)>
%v71 = llvm.insertvalue %v70, %v69[1] : !llvm.struct<(i32, i32, f64)>
%v72 = llvm.extractvalue %v66[2] : !llvm.struct<(i32, i32, f64)>
%v73 = llvm.insertvalue %v72, %v71[2] : !llvm.struct<(i32, i32, f64)>
%v74 = llvm.mlir.constant(1 : i64) : i64
%v75 = llvm.alloca %v74 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v73, %v75 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v76 = llvm.load %v75 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v77 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v78 = llvm.extractvalue %v65[0] : !llvm.struct<(i32, i32, f64)>
%v79 = llvm.insertvalue %v78, %v77[0] : !llvm.struct<(i32, i32, f64)>
%v80 = llvm.extractvalue %v65[1] : !llvm.struct<(i32, i32, f64)>
%v81 = llvm.insertvalue %v80, %v79[1] : !llvm.struct<(i32, i32, f64)>
%v82 = llvm.extractvalue %v65[2] : !llvm.struct<(i32, i32, f64)>
%v83 = llvm.insertvalue %v82, %v81[2] : !llvm.struct<(i32, i32, f64)>
%v84 = llvm.mlir.constant(1 : i64) : i64
%v85 = llvm.alloca %v84 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v83, %v85 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v86 = llvm.load %v85 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
llvm.store %v86, %v56 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v87 = llvm.mlir.constant(1 : i64) : i64
%v88 = llvm.alloca %v87 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v76, %v88 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v89 = func.call @make() : () -> !llvm.struct<(i32, i32, f64)>
%v90 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v91 = llvm.extractvalue %v89[0] : !llvm.struct<(i32, i32, f64)>
%v92 = llvm.insertvalue %v91, %v90[0] : !llvm.struct<(i32, i32, f64)>
%v93 = llvm.extractvalue %v89[1] : !llvm.struct<(i32, i32, f64)>
%v94 = llvm.insertvalue %v93, %v92[1] : !llvm.struct<(i32, i32, f64)>
%v95 = llvm.extractvalue %v89[2] : !llvm.struct<(i32, i32, f64)>
%v96 = llvm.insertvalue %v95, %v94[2] : !llvm.struct<(i32, i32, f64)>
%v97 = llvm.mlir.constant(1 : i64) : i64
%v98 = llvm.alloca %v97 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v96, %v98 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v99 = llvm.load %v98 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v100 = arith.constant 2 : i32
%v101 = arith.sitofp %v100 : i32 to f64
%v102 = llvm.insertvalue %v101, %v99[2] : !llvm.struct<(i32, i32, f64)>
%v103 = llvm.load %v88 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v104 = llvm.getelementptr %v88[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v105 = llvm.load %v104 : !llvm.ptr -> i32
%v106 = arith.constant 1 : i32
%v107 = arith.addi %v105, %v106 : i32
%v108 = llvm.insertvalue %v107, %v102[1] : !llvm.struct<(i32, i32, f64)>
%v109 = llvm.mlir.constant(1 : i64) : i64
%v110 = llvm.alloca %v109 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v108, %v110 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v111 = llvm.load %v56 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v112 = llvm.getelementptr %v56[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v113 = llvm.load %v112 : !llvm.ptr -> i32
%v114 = llvm.load %v56 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v115 = llvm.getelementptr %v56[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v116 = llvm.load %v115 : !llvm.ptr -> i32
%v117 = arith.addi %v113, %v116 : i32
%v118 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v119 = llvm.call @printf(%v118, %v117) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v120 = arith.constant 0 : i32
%v121 = llvm.load %v88 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v122 = llvm.getelementptr %v88[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v123 = llvm.load %v122 : !llvm.ptr -> i32
%v124 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v125 = llvm.call @printf(%v124, %v123) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v126 = arith.constant 0 : i32
%v127 = llvm.load %v110 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v128 = llvm.getelementptr %v110[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v129 = llvm.load %v128 : !llvm.ptr -> f64
%v130 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v131 = llvm.call @printf(%v130, %v129) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v132 = arith.constant 0 : i32
%v133 = llvm.load %v110 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v134 = llvm.getelementptr %v110[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v135 = llvm.load %v134 : !llvm.ptr -> i32
%v136 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v137 = llvm.call @printf(%v136, %v135) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v138 = arith.constant 0 : i32
%v139 = arith.constant 0 : i32
func.return %v139 : i32
}
}
