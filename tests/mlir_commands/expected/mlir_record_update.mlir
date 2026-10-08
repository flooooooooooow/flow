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
// flowc.copy_elision record-update
func.return %v15 : !llvm.struct<(i32, i32, f64)>
}
func.func @make() -> !llvm.struct<(i32, i32, f64)> {
%v16 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v17 = arith.constant 1 : i32
%v18 = llvm.insertvalue %v17, %v16[0] : !llvm.struct<(i32, i32, f64)>
%v19 = arith.constant 2 : i32
%v20 = llvm.insertvalue %v19, %v18[1] : !llvm.struct<(i32, i32, f64)>
%v21 = arith.constant 0.5 : f64
%v22 = llvm.insertvalue %v21, %v20[2] : !llvm.struct<(i32, i32, f64)>
%v23 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v24 = llvm.extractvalue %v22[0] : !llvm.struct<(i32, i32, f64)>
%v25 = llvm.insertvalue %v24, %v23[0] : !llvm.struct<(i32, i32, f64)>
%v26 = llvm.extractvalue %v22[1] : !llvm.struct<(i32, i32, f64)>
%v27 = llvm.insertvalue %v26, %v25[1] : !llvm.struct<(i32, i32, f64)>
%v28 = llvm.extractvalue %v22[2] : !llvm.struct<(i32, i32, f64)>
%v29 = llvm.insertvalue %v28, %v27[2] : !llvm.struct<(i32, i32, f64)>
%v30 = llvm.mlir.constant(1 : i64) : i64
%v31 = llvm.alloca %v30 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v29, %v31 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v32 = llvm.load %v31 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
func.return %v32 : !llvm.struct<(i32, i32, f64)>
}
func.func @main() -> i32 {
%v33 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v34 = arith.constant 3 : i32
%v35 = llvm.insertvalue %v34, %v33[0] : !llvm.struct<(i32, i32, f64)>
%v36 = arith.constant 4 : i32
%v37 = llvm.insertvalue %v36, %v35[1] : !llvm.struct<(i32, i32, f64)>
%v38 = arith.constant 1.5 : f64
%v39 = llvm.insertvalue %v38, %v37[2] : !llvm.struct<(i32, i32, f64)>
%v40 = llvm.mlir.constant(1 : i64) : i64
%v41 = llvm.alloca %v40 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v39, %v41 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v42 = llvm.load %v41 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v43 = arith.constant 40 : i32
%v44 = llvm.insertvalue %v43, %v42[1] : !llvm.struct<(i32, i32, f64)>
%v45 = llvm.mlir.constant(1 : i64) : i64
%v46 = llvm.alloca %v45 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v44, %v46 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v47 = llvm.load %v46 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v48 = arith.constant 10 : i32
%v49 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v50 = llvm.extractvalue %v47[0] : !llvm.struct<(i32, i32, f64)>
%v51 = llvm.insertvalue %v50, %v49[0] : !llvm.struct<(i32, i32, f64)>
%v52 = llvm.extractvalue %v47[1] : !llvm.struct<(i32, i32, f64)>
%v53 = llvm.insertvalue %v52, %v51[1] : !llvm.struct<(i32, i32, f64)>
%v54 = llvm.extractvalue %v47[2] : !llvm.struct<(i32, i32, f64)>
%v55 = llvm.insertvalue %v54, %v53[2] : !llvm.struct<(i32, i32, f64)>
%v56 = func.call @moved(%v55, %v48) : (!llvm.struct<(i32, i32, f64)>, i32) -> !llvm.struct<(i32, i32, f64)>
%v57 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v58 = llvm.extractvalue %v56[0] : !llvm.struct<(i32, i32, f64)>
%v59 = llvm.insertvalue %v58, %v57[0] : !llvm.struct<(i32, i32, f64)>
%v60 = llvm.extractvalue %v56[1] : !llvm.struct<(i32, i32, f64)>
%v61 = llvm.insertvalue %v60, %v59[1] : !llvm.struct<(i32, i32, f64)>
%v62 = llvm.extractvalue %v56[2] : !llvm.struct<(i32, i32, f64)>
%v63 = llvm.insertvalue %v62, %v61[2] : !llvm.struct<(i32, i32, f64)>
%v64 = llvm.mlir.constant(1 : i64) : i64
%v65 = llvm.alloca %v64 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v63, %v65 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v66 = llvm.load %v65 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v67 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v68 = llvm.extractvalue %v55[0] : !llvm.struct<(i32, i32, f64)>
%v69 = llvm.insertvalue %v68, %v67[0] : !llvm.struct<(i32, i32, f64)>
%v70 = llvm.extractvalue %v55[1] : !llvm.struct<(i32, i32, f64)>
%v71 = llvm.insertvalue %v70, %v69[1] : !llvm.struct<(i32, i32, f64)>
%v72 = llvm.extractvalue %v55[2] : !llvm.struct<(i32, i32, f64)>
%v73 = llvm.insertvalue %v72, %v71[2] : !llvm.struct<(i32, i32, f64)>
%v74 = llvm.mlir.constant(1 : i64) : i64
%v75 = llvm.alloca %v74 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v73, %v75 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v76 = llvm.load %v75 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
llvm.store %v76, %v46 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v77 = llvm.mlir.constant(1 : i64) : i64
%v78 = llvm.alloca %v77 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v66, %v78 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v79 = func.call @make() : () -> !llvm.struct<(i32, i32, f64)>
%v80 = llvm.mlir.undef : !llvm.struct<(i32, i32, f64)>
%v81 = llvm.extractvalue %v79[0] : !llvm.struct<(i32, i32, f64)>
%v82 = llvm.insertvalue %v81, %v80[0] : !llvm.struct<(i32, i32, f64)>
%v83 = llvm.extractvalue %v79[1] : !llvm.struct<(i32, i32, f64)>
%v84 = llvm.insertvalue %v83, %v82[1] : !llvm.struct<(i32, i32, f64)>
%v85 = llvm.extractvalue %v79[2] : !llvm.struct<(i32, i32, f64)>
%v86 = llvm.insertvalue %v85, %v84[2] : !llvm.struct<(i32, i32, f64)>
%v87 = llvm.mlir.constant(1 : i64) : i64
%v88 = llvm.alloca %v87 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v86, %v88 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v89 = llvm.load %v88 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v90 = arith.constant 2 : i32
%v91 = arith.sitofp %v90 : i32 to f64
%v92 = llvm.insertvalue %v91, %v89[2] : !llvm.struct<(i32, i32, f64)>
%v93 = llvm.load %v78 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v94 = llvm.getelementptr %v78[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v95 = llvm.load %v94 : !llvm.ptr -> i32
%v96 = arith.constant 1 : i32
%v97 = arith.addi %v95, %v96 : i32
%v98 = llvm.insertvalue %v97, %v92[1] : !llvm.struct<(i32, i32, f64)>
%v99 = llvm.mlir.constant(1 : i64) : i64
%v100 = llvm.alloca %v99 x !llvm.struct<(i32, i32, f64)> : (i64) -> !llvm.ptr
llvm.store %v98, %v100 : !llvm.struct<(i32, i32, f64)>, !llvm.ptr
%v101 = llvm.load %v46 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v102 = llvm.getelementptr %v46[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v103 = llvm.load %v102 : !llvm.ptr -> i32
%v104 = llvm.load %v46 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v105 = llvm.getelementptr %v46[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v106 = llvm.load %v105 : !llvm.ptr -> i32
%v107 = arith.addi %v103, %v106 : i32
%v108 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v109 = llvm.call @printf(%v108, %v107) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v110 = arith.constant 0 : i32
%v111 = llvm.load %v78 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v112 = llvm.getelementptr %v78[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v113 = llvm.load %v112 : !llvm.ptr -> i32
%v114 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v115 = llvm.call @printf(%v114, %v113) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v116 = arith.constant 0 : i32
%v117 = llvm.load %v100 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v118 = llvm.getelementptr %v100[0, 2] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v119 = llvm.load %v118 : !llvm.ptr -> f64
%v120 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v121 = llvm.call @printf(%v120, %v119) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v122 = arith.constant 0 : i32
%v123 = llvm.load %v100 : !llvm.ptr -> !llvm.struct<(i32, i32, f64)>
%v124 = llvm.getelementptr %v100[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32, f64)>
%v125 = llvm.load %v124 : !llvm.ptr -> i32
%v126 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v127 = llvm.call @printf(%v126, %v125) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v128 = arith.constant 0 : i32
%v129 = arith.constant 0 : i32
func.return %v129 : i32
}
}
