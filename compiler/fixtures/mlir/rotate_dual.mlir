module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_1("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
// Struct: Dual
// Fields:
//   val: f32
//   grad: f32
func.func @countdown(%arg0: i32) -> i32 {
%v1 = llvm.mlir.constant(1 : i64) : i64
%v2 = llvm.alloca %v1 x i32 : (i64) -> !llvm.ptr
%v3 = llvm.mlir.constant(1 : i64) : i64
%v4 = llvm.alloca %v3 x i32 : (i64) -> !llvm.ptr
%v5 = arith.constant 0 : i32
llvm.store %v5, %v2 : i32, !llvm.ptr
llvm.store %arg0, %v4 : i32, !llvm.ptr
%v6 = llvm.load %v2 : !llvm.ptr -> i32
%v7 = llvm.load %v4 : !llvm.ptr -> i32
%v8 = arith.addi %v6, %v7 : i32
llvm.store %v8, %v2 : i32, !llvm.ptr
cf.br ^b1
^b1:
%v9 = llvm.load %v4 : !llvm.ptr -> i32
%v10 = arith.constant 0 : i32
%v11 = arith.cmpi ne, %v9, %v10 : i32
cf.cond_br %v11, ^b2, ^b3
^b2:
%v12 = llvm.load %v4 : !llvm.ptr -> i32
%v13 = arith.constant 1 : i32
%v14 = arith.subi %v12, %v13 : i32
llvm.store %v14, %v4 : i32, !llvm.ptr
%v15 = llvm.load %v2 : !llvm.ptr -> i32
%v16 = llvm.load %v4 : !llvm.ptr -> i32
%v17 = arith.addi %v15, %v16 : i32
llvm.store %v17, %v2 : i32, !llvm.ptr
cf.br ^b1
^b3:
%v18 = llvm.load %v2 : !llvm.ptr -> i32
func.return %v18 : i32
}
func.func @first_over(%arg0: i32) -> i32 {
%v19 = llvm.mlir.constant(1 : i64) : i64
%v20 = llvm.alloca %v19 x i32 : (i64) -> !llvm.ptr
%v21 = arith.constant 0 : i32
llvm.store %v21, %v20 : i32, !llvm.ptr
cf.br ^b4
^b4:
%v22 = arith.constant 1 : i1
cf.cond_br %v22, ^b5, ^b6
^b5:
%v23 = llvm.load %v20 : !llvm.ptr -> i32
%v24 = llvm.load %v20 : !llvm.ptr -> i32
%v25 = arith.muli %v23, %v24 : i32
%v26 = arith.cmpi sgt, %v25, %arg0 : i32
cf.cond_br %v26, ^b7, ^b8
^b7:
cf.br ^b6
^b8:
cf.br ^b9
^b9:
%v27 = llvm.load %v20 : !llvm.ptr -> i32
%v28 = arith.constant 1 : i32
%v29 = arith.addi %v27, %v28 : i32
llvm.store %v29, %v20 : i32, !llvm.ptr
cf.br ^b4
^b6:
%v30 = llvm.load %v20 : !llvm.ptr -> i32
func.return %v30 : i32
}
func.func @scale(%arg0: !llvm.struct<(f32, f32)>, %arg1: f32) -> !llvm.struct<(f32, f32)> {
%v31 = llvm.mlir.constant(1 : i64) : i64
%v32 = llvm.alloca %v31 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
%v33 = llvm.mlir.constant(1 : i64) : i64
%v34 = llvm.alloca %v33 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
%v35 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v36 = llvm.extractvalue %arg0[0] : !llvm.struct<(f32, f32)>
%v37 = llvm.insertvalue %v36, %v35[0] : !llvm.struct<(f32, f32)>
%v38 = llvm.extractvalue %arg0[1] : !llvm.struct<(f32, f32)>
%v39 = llvm.insertvalue %v38, %v37[1] : !llvm.struct<(f32, f32)>
llvm.store %v39, %v32 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v40 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v41 = llvm.load %v32 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v42 = llvm.getelementptr %v32[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f32, f32)>
%v43 = llvm.load %v42 : !llvm.ptr -> f32
%v44 = arith.mulf %v43, %arg1 : f32
%v45 = llvm.insertvalue %v44, %v40[0] : !llvm.struct<(f32, f32)>
%v46 = llvm.load %v32 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v47 = llvm.getelementptr %v32[0, 1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f32, f32)>
%v48 = llvm.load %v47 : !llvm.ptr -> f32
%v49 = arith.mulf %v48, %arg1 : f32
%v50 = llvm.insertvalue %v49, %v45[1] : !llvm.struct<(f32, f32)>
%v51 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v52 = llvm.extractvalue %v50[0] : !llvm.struct<(f32, f32)>
%v53 = llvm.insertvalue %v52, %v51[0] : !llvm.struct<(f32, f32)>
%v54 = llvm.extractvalue %v50[1] : !llvm.struct<(f32, f32)>
%v55 = llvm.insertvalue %v54, %v53[1] : !llvm.struct<(f32, f32)>
llvm.store %v55, %v34 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v56 = llvm.load %v34 : !llvm.ptr -> !llvm.struct<(f32, f32)>
func.return %v56 : !llvm.struct<(f32, f32)>
}
func.func @main() -> i32 {
%v57 = llvm.mlir.constant(1 : i64) : i64
%v58 = llvm.alloca %v57 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
%v59 = llvm.mlir.constant(1 : i64) : i64
%v60 = llvm.alloca %v59 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
%v61 = llvm.mlir.constant(1 : i64) : i64
%v62 = llvm.alloca %v61 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
%v63 = llvm.mlir.constant(1 : i64) : i64
%v64 = llvm.alloca %v63 x !llvm.struct<(f32, f32)> : (i64) -> !llvm.ptr
%v65 = arith.constant 10 : i32
%v66 = func.call @countdown(%v65) : (i32) -> i32
%v67 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v68 = llvm.call @printf(%v67, %v66) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v69 = arith.constant 0 : i32
%v70 = arith.constant 50 : i32
%v71 = func.call @first_over(%v70) : (i32) -> i32
%v72 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v73 = llvm.call @printf(%v72, %v71) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v74 = arith.constant 0 : i32
%v75 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v76 = arith.constant 2.0 : f64
%v77 = arith.truncf %v76 : f64 to f32
%v78 = llvm.insertvalue %v77, %v75[0] : !llvm.struct<(f32, f32)>
%v79 = arith.constant 1.0 : f64
%v80 = arith.truncf %v79 : f64 to f32
%v81 = llvm.insertvalue %v80, %v78[1] : !llvm.struct<(f32, f32)>
llvm.store %v81, %v58 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v82 = llvm.load %v58 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v83 = arith.constant 3.0 : f64
%v84 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v85 = llvm.extractvalue %v82[0] : !llvm.struct<(f32, f32)>
%v86 = llvm.insertvalue %v85, %v84[0] : !llvm.struct<(f32, f32)>
%v87 = llvm.extractvalue %v82[1] : !llvm.struct<(f32, f32)>
%v88 = llvm.insertvalue %v87, %v86[1] : !llvm.struct<(f32, f32)>
%v89 = arith.truncf %v83 : f64 to f32
%v90 = func.call @scale(%v88, %v89) : (!llvm.struct<(f32, f32)>, f32) -> !llvm.struct<(f32, f32)>
%v91 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v92 = llvm.extractvalue %v90[0] : !llvm.struct<(f32, f32)>
%v93 = llvm.insertvalue %v92, %v91[0] : !llvm.struct<(f32, f32)>
%v94 = llvm.extractvalue %v90[1] : !llvm.struct<(f32, f32)>
%v95 = llvm.insertvalue %v94, %v93[1] : !llvm.struct<(f32, f32)>
llvm.store %v95, %v60 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v96 = llvm.load %v60 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v97 = llvm.mlir.undef : !llvm.struct<(f32, f32)>
%v98 = llvm.extractvalue %v88[0] : !llvm.struct<(f32, f32)>
%v99 = llvm.insertvalue %v98, %v97[0] : !llvm.struct<(f32, f32)>
%v100 = llvm.extractvalue %v88[1] : !llvm.struct<(f32, f32)>
%v101 = llvm.insertvalue %v100, %v99[1] : !llvm.struct<(f32, f32)>
llvm.store %v101, %v62 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v102 = llvm.load %v62 : !llvm.ptr -> !llvm.struct<(f32, f32)>
llvm.store %v102, %v58 : !llvm.struct<(f32, f32)>, !llvm.ptr
llvm.store %v96, %v64 : !llvm.struct<(f32, f32)>, !llvm.ptr
%v103 = llvm.load %v64 : !llvm.ptr -> !llvm.struct<(f32, f32)>
%v104 = llvm.getelementptr %v64[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(f32, f32)>
%v105 = llvm.load %v104 : !llvm.ptr -> f32
%v106 = arith.extf %v105 : f32 to f64
%v107 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v108 = llvm.call @printf(%v107, %v106) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v109 = arith.constant 0 : i32
%v110 = arith.constant 0 : i32
func.return %v110 : i32
}
}
