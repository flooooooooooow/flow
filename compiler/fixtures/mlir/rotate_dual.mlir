module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\n\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_1("%f\n\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
// Struct: Dual
// Fields:
//   val: f32
//   grad: f32
func.func @countdown(%arg0: i32) -> i32 {
%v1 = arith.constant 0 : i32
%v2 = llvm.mlir.constant(1 : i64) : i64
%v3 = llvm.alloca %v2 x i32 : (i64) -> !llvm.ptr
llvm.store %v1, %v3 : i32, !llvm.ptr
%v4 = llvm.mlir.constant(1 : i64) : i64
%v5 = llvm.alloca %v4 x i32 : (i64) -> !llvm.ptr
llvm.store %arg0, %v5 : i32, !llvm.ptr
%v6 = llvm.load %v3 : !llvm.ptr -> i32
%v7 = llvm.load %v5 : !llvm.ptr -> i32
%v8 = arith.addi %v6, %v7 : i32
llvm.store %v8, %v3 : i32, !llvm.ptr
cf.br ^b1
^b1:
%v9 = llvm.load %v5 : !llvm.ptr -> i32
%v10 = arith.constant 0 : i32
%v11 = arith.cmpi ne, %v9, %v10 : i32
cf.cond_br %v11, ^b2, ^b3
^b2:
%v12 = llvm.load %v5 : !llvm.ptr -> i32
%v13 = arith.constant 1 : i32
%v14 = arith.subi %v12, %v13 : i32
llvm.store %v14, %v5 : i32, !llvm.ptr
%v15 = llvm.load %v3 : !llvm.ptr -> i32
%v16 = llvm.load %v5 : !llvm.ptr -> i32
%v17 = arith.addi %v15, %v16 : i32
llvm.store %v17, %v3 : i32, !llvm.ptr
cf.br ^b1
^b3:
%v18 = llvm.load %v3 : !llvm.ptr -> i32
func.return %v18 : i32
}
func.func @first_over(%arg0: i32) -> i32 {
%v19 = arith.constant 0 : i32
%v20 = llvm.mlir.constant(1 : i64) : i64
%v21 = llvm.alloca %v20 x i32 : (i64) -> !llvm.ptr
llvm.store %v19, %v21 : i32, !llvm.ptr
cf.br ^b4
^b4:
%v22 = arith.constant 1 : i1
cf.cond_br %v22, ^b5, ^b6
^b5:
%v23 = llvm.load %v21 : !llvm.ptr -> i32
%v24 = llvm.load %v21 : !llvm.ptr -> i32
%v25 = arith.muli %v23, %v24 : i32
%v26 = arith.cmpi sgt, %v25, %arg0 : i32
cf.cond_br %v26, ^b7, ^b8
^b7:
cf.br ^b6
^b8:
cf.br ^b9
^b9:
%v27 = llvm.load %v21 : !llvm.ptr -> i32
%v28 = arith.constant 1 : i32
%v29 = arith.addi %v27, %v28 : i32
llvm.store %v29, %v21 : i32, !llvm.ptr
cf.br ^b4
^b6:
%v30 = llvm.load %v21 : !llvm.ptr -> i32
func.return %v30 : i32
}
func.func @scale(%arg0: !llvm.struct<(f32, f32)>, %arg1: f32) -> !llvm.struct<(f32, f32)> {
%v31 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v32 = llvm.extractvalue %arg0[0] : !llvm.struct<(f32, f32)>
%v33 = llvm.insertvalue %v32, %v31[0] : !llvm.struct<(f32, f32)>
%v34 = llvm.extractvalue %arg0[1] : !llvm.struct<(f32, f32)>
%v35 = llvm.insertvalue %v34, %v33[1] : !llvm.struct<(f32, f32)>
%v36 = llvm.mlir.constant(1 : i64) : i64
%v37 = llvm.alloca %v36 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
llvm.store %v35, %v37 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v38 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v39 = llvm.load %v37 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v40 = llvm.getelementptr %v37[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f32, f32)>
%v41 = llvm.load %v40 : !llvm.ptr -> f32
%v42 = arith.mulf %v41, %arg1 : f32
%v43 = llvm.insertvalue %v42, %v38[0] : !llvm.struct<(f32, f32)>
%v44 = llvm.load %v37 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v45 = llvm.getelementptr %v37[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f32, f32)>
%v46 = llvm.load %v45 : !llvm.ptr -> f32
%v47 = arith.mulf %v46, %arg1 : f32
%v48 = llvm.insertvalue %v47, %v43[1] : !llvm.struct<(f32, f32)>
%v49 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v50 = llvm.extractvalue %v48[0] : !llvm.struct<(f32, f32)>
%v51 = llvm.insertvalue %v50, %v49[0] : !llvm.struct<(f32, f32)>
%v52 = llvm.extractvalue %v48[1] : !llvm.struct<(f32, f32)>
%v53 = llvm.insertvalue %v52, %v51[1] : !llvm.struct<(f32, f32)>
%v54 = llvm.mlir.constant(1 : i64) : i64
%v55 = llvm.alloca %v54 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
llvm.store %v53, %v55 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v56 = llvm.load %v55 : !llvm.ptr -> !llvm.struct<(f32, f32)>
func.return %v56 : !llvm.struct<(f32, f32)>
}
func.func @main() -> i32 {
%v57 = arith.constant 10 : i32
%v58 = func.call @countdown(%v57) : (i32) -> i32
%v59 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v60 = llvm.call @printf(%v59, %v58) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v61 = arith.constant 0 : i32
%v62 = arith.constant 50 : i32
%v63 = func.call @first_over(%v62) : (i32) -> i32
%v64 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v65 = llvm.call @printf(%v64, %v63) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v66 = arith.constant 0 : i32
%v67 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v68 = arith.constant 2.0 : f32
%v69 = llvm.insertvalue %v68, %v67[0] : !llvm.struct<(f32, f32)>
%v70 = arith.constant 1.0 : f32
%v71 = llvm.insertvalue %v70, %v69[1] : !llvm.struct<(f32, f32)>
%v72 = llvm.mlir.constant(1 : i64) : i64
%v73 = llvm.alloca %v72 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
llvm.store %v71, %v73 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v74 = arith.constant 3.0 : f32
%v75 = llvm.load %v73 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v76 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v77 = llvm.extractvalue %v75[0] : !llvm.struct<(f32, f32)>
%v78 = llvm.insertvalue %v77, %v76[0] : !llvm.struct<(f32, f32)>
%v79 = llvm.extractvalue %v75[1] : !llvm.struct<(f32, f32)>
%v80 = llvm.insertvalue %v79, %v78[1] : !llvm.struct<(f32, f32)>
%v81 = func.call @scale(%v80, %v74) : (!llvm.struct<(f32, f32)>, f32) -> !llvm.struct<(f32, f32)>
%v82 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v83 = llvm.extractvalue %v81[0] : !llvm.struct<(f32, f32)>
%v84 = llvm.insertvalue %v83, %v82[0] : !llvm.struct<(f32, f32)>
%v85 = llvm.extractvalue %v81[1] : !llvm.struct<(f32, f32)>
%v86 = llvm.insertvalue %v85, %v84[1] : !llvm.struct<(f32, f32)>
%v87 = llvm.mlir.constant(1 : i64) : i64
%v88 = llvm.alloca %v87 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
llvm.store %v86, %v88 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v89 = llvm.load %v88 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v90 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v91 = llvm.extractvalue %v80[0] : !llvm.struct<(f32, f32)>
%v92 = llvm.insertvalue %v91, %v90[0] : !llvm.struct<(f32, f32)>
%v93 = llvm.extractvalue %v80[1] : !llvm.struct<(f32, f32)>
%v94 = llvm.insertvalue %v93, %v92[1] : !llvm.struct<(f32, f32)>
%v95 = llvm.mlir.constant(1 : i64) : i64
%v96 = llvm.alloca %v95 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
llvm.store %v94, %v96 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v97 = llvm.load %v96 : !llvm.ptr -> !llvm.struct<(f32, f32)>
llvm.store %v97, %v73 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v98 = llvm.mlir.constant(1 : i64) : i64
%v99 = llvm.alloca %v98 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
llvm.store %v89, %v99 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v100 = llvm.load %v99 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v101 = llvm.getelementptr %v99[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f32, f32)>
%v102 = llvm.load %v101 : !llvm.ptr -> f32
%v103 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v104 = arith.extf %v102 : f32 to f64
%v105 = llvm.call @printf(%v103, %v104) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v106 = arith.constant 0 : i32
%v107 = arith.constant 0 : i32
func.return %v107 : i32
}
}
