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
%v1 = llvm.mlir.constant(1 : i64) : i64
%v2 = llvm.alloca %v1 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
%v3 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v4 = llvm.extractvalue %arg0[0] : !llvm.struct<(i32, i32, f64)>
%v5 = llvm.insertvalue %v4, %v3[0] : !llvm.struct<(i32, i32, f64)>
%v6 = llvm.extractvalue %arg0[1] : !llvm.struct<(i32, i32, f64)>
%v7 = llvm.insertvalue %v6, %v5[1] : !llvm.struct<(i32, i32, f64)>
%v8 = llvm.extractvalue %arg0[2] : !llvm.struct<(i32, i32, f64)>
%v9 = llvm.insertvalue %v8, %v7[2] : !llvm.struct<(i32, i32, f64)>
llvm.store %v9, %v2 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v10 = llvm.load %v2 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v11 = llvm.load %v2 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v12 = llvm.getelementptr %v2[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v13 = llvm.load %v12 : !llvm.ptr -> i32
%v14 = arith.addi %v13, %arg1 : i32
%v15 = llvm.insertvalue %v14, %v10[0] : !llvm.struct<(i32, i32, f64)>
// flowc.copy_elision record-update
func.return %v15 : !llvm.struct<(i32, i32, f64)>
}
func.func @make() -> !llvm.struct<(i32, i32, f64)> {
%v16 = llvm.mlir.constant(1 : i64) : i64
%v17 = llvm.alloca %v16 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
%v18 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v19 = arith.constant 1 : i32
%v20 = llvm.insertvalue %v19, %v18[0] : !llvm.struct<(i32, i32, f64)>
%v21 = arith.constant 2 : i32
%v22 = llvm.insertvalue %v21, %v20[1] : !llvm.struct<(i32, i32, f64)>
%v23 = arith.constant 0.5 : f64
%v24 = llvm.insertvalue %v23, %v22[2] : !llvm.struct<(i32, i32, f64)>
%v25 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v26 = llvm.extractvalue %v24[0] : !llvm.struct<(i32, i32, f64)>
%v27 = llvm.insertvalue %v26, %v25[0] : !llvm.struct<(i32, i32, f64)>
%v28 = llvm.extractvalue %v24[1] : !llvm.struct<(i32, i32, f64)>
%v29 = llvm.insertvalue %v28, %v27[1] : !llvm.struct<(i32, i32, f64)>
%v30 = llvm.extractvalue %v24[2] : !llvm.struct<(i32, i32, f64)>
%v31 = llvm.insertvalue %v30, %v29[2] : !llvm.struct<(i32, i32, f64)>
llvm.store %v31, %v17 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v32 = llvm.load %v17 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
func.return %v32 : !llvm.struct<(i32, i32, f64)>
}
func.func @main() -> i32 {
%v33 = llvm.mlir.constant(1 : i64) : i64
%v34 = llvm.alloca %v33 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
%v35 = llvm.mlir.constant(1 : i64) : i64
%v36 = llvm.alloca %v35 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
%v37 = llvm.mlir.constant(1 : i64) : i64
%v38 = llvm.alloca %v37 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
%v39 = llvm.mlir.constant(1 : i64) : i64
%v40 = llvm.alloca %v39 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
%v41 = llvm.mlir.constant(1 : i64) : i64
%v42 = llvm.alloca %v41 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
%v43 = llvm.mlir.constant(1 : i64) : i64
%v44 = llvm.alloca %v43 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
%v45 = llvm.mlir.constant(1 : i64) : i64
%v46 = llvm.alloca %v45 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
%v47 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v48 = arith.constant 3 : i32
%v49 = llvm.insertvalue %v48, %v47[0] : !llvm.struct<(i32, i32, f64)>
%v50 = arith.constant 4 : i32
%v51 = llvm.insertvalue %v50, %v49[1] : !llvm.struct<(i32, i32, f64)>
%v52 = arith.constant 1.5 : f64
%v53 = llvm.insertvalue %v52, %v51[2] : !llvm.struct<(i32, i32, f64)>
llvm.store %v53, %v34 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v54 = llvm.load %v34 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v55 = arith.constant 40 : i32
%v56 = llvm.insertvalue %v55, %v54[1] : !llvm.struct<(i32, i32, f64)>
llvm.store %v56, %v36 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v57 = llvm.load %v36 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
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
llvm.store %v73, %v38 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v74 = llvm.load %v38 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v75 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v76 = llvm.extractvalue %v65[0] : !llvm.struct<(i32, i32, f64)>
%v77 = llvm.insertvalue %v76, %v75[0] : !llvm.struct<(i32, i32, f64)>
%v78 = llvm.extractvalue %v65[1] : !llvm.struct<(i32, i32, f64)>
%v79 = llvm.insertvalue %v78, %v77[1] : !llvm.struct<(i32, i32, f64)>
%v80 = llvm.extractvalue %v65[2] : !llvm.struct<(i32, i32, f64)>
%v81 = llvm.insertvalue %v80, %v79[2] : !llvm.struct<(i32, i32, f64)>
llvm.store %v81, %v40 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v82 = llvm.load %v40 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
llvm.store %v82, %v36 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
llvm.store %v74, %v42 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v83 = func.call @make() : () -> !llvm.struct<(i32, i32, f64)>
%v84 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v85 = llvm.extractvalue %v83[0] : !llvm.struct<(i32, i32, f64)>
%v86 = llvm.insertvalue %v85, %v84[0] : !llvm.struct<(i32, i32, f64)>
%v87 = llvm.extractvalue %v83[1] : !llvm.struct<(i32, i32, f64)>
%v88 = llvm.insertvalue %v87, %v86[1] : !llvm.struct<(i32, i32, f64)>
%v89 = llvm.extractvalue %v83[2] : !llvm.struct<(i32, i32, f64)>
%v90 = llvm.insertvalue %v89, %v88[2] : !llvm.struct<(i32, i32, f64)>
llvm.store %v90, %v44 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v91 = llvm.load %v44 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v92 = arith.constant 2 : i32
%v93 = arith.sitofp %v92 : i32 to f64
%v94 = llvm.insertvalue %v93, %v91[2] : !llvm.struct<(i32, i32, f64)>
%v95 = llvm.load %v42 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v96 = llvm.getelementptr %v42[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v97 = llvm.load %v96 : !llvm.ptr -> i32
%v98 = arith.constant 1 : i32
%v99 = arith.addi %v97, %v98 : i32
%v100 = llvm.insertvalue %v99, %v94[1] : !llvm.struct<(i32, i32, f64)>
llvm.store %v100, %v46 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v101 = llvm.load %v36 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v102 = llvm.getelementptr %v36[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v103 = llvm.load %v102 : !llvm.ptr -> i32
%v104 = llvm.load %v36 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v105 = llvm.getelementptr %v36[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v106 = llvm.load %v105 : !llvm.ptr -> i32
%v107 = arith.addi %v103, %v106 : i32
%v108 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v109 = llvm.call @printf(%v108, %v107) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v110 = arith.constant 0 : i32
%v111 = llvm.load %v42 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v112 = llvm.getelementptr %v42[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v113 = llvm.load %v112 : !llvm.ptr -> i32
%v114 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v115 = llvm.call @printf(%v114, %v113) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v116 = arith.constant 0 : i32
%v117 = llvm.load %v46 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v118 = llvm.getelementptr %v46[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v119 = llvm.load %v118 : !llvm.ptr -> f64
%v120 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v121 = llvm.call @printf(%v120, %v119) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v122 = arith.constant 0 : i32
%v123 = llvm.load %v46 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v124 = llvm.getelementptr %v46[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v125 = llvm.load %v124 : !llvm.ptr -> i32
%v126 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v127 = llvm.call @printf(%v126, %v125) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v128 = arith.constant 0 : i32
%v129 = arith.constant 0 : i32
func.return %v129 : i32
}
}
