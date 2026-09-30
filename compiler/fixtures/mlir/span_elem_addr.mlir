module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%.1f %.1f\n\00") {addr_space = 0 : i32} : !llvm.array<11 x i8>
func.func private @malloc(i64) -> !llvm.ptr
func.func @put(%arg0: !llvm.ptr, %arg1: f64) -> () {
%v1 = arith.constant 0 : i32
%v2 = arith.extsi %v1 : i32 to i64
%v3 = llvm.getelementptr %arg0[%v2] : (!llvm.ptr, i64) -> !llvm.ptr, f64
llvm.store %arg1, %v3 : f64, !llvm.ptr
func.return
}
func.func @via_index(%arg0: !llvm.struct<(!llvm.ptr, i64)>, %arg1: i32) -> () {
%v4 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v5 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i64)>
%v6 = llvm.insertvalue %v5, %v4[0] : !llvm.struct<(!llvm.ptr, i64)>
%v7 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i64)>
%v8 = llvm.insertvalue %v7, %v6[1] : !llvm.struct<(!llvm.ptr, i64)>
%v9 = llvm.mlir.constant(1 : i64) : i64
%v10 = llvm.alloca %v9 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v8, %v10 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v11 = arith.constant 0 : i32
%v12 = arith.index_cast %v11 : i32 to index
%v13 = arith.index_cast %arg1 : i32 to index
%v14 = arith.constant 1 : index
%v15 = arith.constant -1 : index
%v16 = arith.cmpi sle, %v12, %v13 : index
%v17 = arith.select %v16, %v14, %v15 : index
cf.br ^b1(%v12 : index)
^b1(%v18: index):
%v19 = arith.cmpi slt, %v18, %v13 : index
%v20 = arith.cmpi sgt, %v18, %v13 : index
%v21 = arith.select %v16, %v19, %v20 : i1
cf.cond_br %v21, ^b2(%v18 : index), ^b3(%v18 : index)
^b2(%v22: index):
%v23 = llvm.load %v10 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v24 = llvm.extractvalue %v23[0] : !llvm.struct<(!llvm.ptr, i64)>
%v25 = arith.index_cast %v22 : index to i64
%v26 = llvm.getelementptr %v24[%v25] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v27 = arith.index_cast %v22 : index to i64
%v28 = arith.sitofp %v27 : i64 to f64
%v29 = arith.constant 0.5 : f32
%v30 = arith.extf %v29 : f32 to f64
%v31 = arith.addf %v28, %v30 : f64
func.call @put(%v26, %v31) : (!llvm.ptr, f64) -> ()
%v32 = arith.addi %v22, %v17 : index
cf.br ^b1(%v32 : index)
^b3(%v33: index):
func.return
}
func.func @via_data(%arg0: !llvm.struct<(!llvm.ptr, i64)>, %arg1: i32) -> () {
%v34 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v35 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i64)>
%v36 = llvm.insertvalue %v35, %v34[0] : !llvm.struct<(!llvm.ptr, i64)>
%v37 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i64)>
%v38 = llvm.insertvalue %v37, %v36[1] : !llvm.struct<(!llvm.ptr, i64)>
%v39 = llvm.mlir.constant(1 : i64) : i64
%v40 = llvm.alloca %v39 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v38, %v40 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v41 = arith.constant 0 : i32
%v42 = arith.index_cast %v41 : i32 to index
%v43 = arith.index_cast %arg1 : i32 to index
%v44 = arith.constant 1 : index
%v45 = arith.constant -1 : index
%v46 = arith.cmpi sle, %v42, %v43 : index
%v47 = arith.select %v46, %v44, %v45 : index
cf.br ^b4(%v42 : index)
^b4(%v48: index):
%v49 = arith.cmpi slt, %v48, %v43 : index
%v50 = arith.cmpi sgt, %v48, %v43 : index
%v51 = arith.select %v46, %v49, %v50 : i1
cf.cond_br %v51, ^b5(%v48 : index), ^b6(%v48 : index)
^b5(%v52: index):
%v53 = llvm.load %v40 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v54 = llvm.extractvalue %v53[0] : !llvm.struct<(!llvm.ptr, i64)>
%v55 = arith.index_cast %v52 : index to i64
%v56 = llvm.getelementptr %v54[%v55] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v57 = arith.index_cast %v52 : index to i64
%v58 = arith.sitofp %v57 : i64 to f64
%v59 = arith.constant 2.0 : f32
%v60 = arith.extf %v59 : f32 to f64
%v61 = arith.mulf %v58, %v60 : f64
func.call @put(%v56, %v61) : (!llvm.ptr, f64) -> ()
%v62 = arith.addi %v52, %v47 : index
cf.br ^b4(%v62 : index)
^b6(%v63: index):
func.return
}
func.func @main() -> i32 {
%v64 = arith.constant 32 : i32
%v65 = arith.extsi %v64 : i32 to i64
%v66 = func.call @malloc(%v65) : (i64) -> !llvm.ptr
%v67 = arith.constant 0 : i32
%v68 = arith.constant 4 : i32
%v69 = arith.extsi %v67 : i32 to i64
%v70 = arith.extsi %v68 : i32 to i64
%v71 = llvm.getelementptr %v66[%v69] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v72 = arith.subi %v70, %v69 : i64
%v73 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v74 = llvm.insertvalue %v71, %v73[0] : !llvm.struct<(!llvm.ptr, i64)>
%v75 = llvm.insertvalue %v72, %v74[1] : !llvm.struct<(!llvm.ptr, i64)>
%v76 = llvm.mlir.constant(1 : i64) : i64
%v77 = llvm.alloca %v76 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v75, %v77 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v78 = llvm.load %v77 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v79 = arith.constant 4 : i32
func.call @via_index(%v78, %v79) : (!llvm.struct<(!llvm.ptr, i64)>, i32) -> ()
%v80 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v81 = llvm.load %v77 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v82 = arith.constant 0 : i32
%v83 = llvm.extractvalue %v81[0] : !llvm.struct<(!llvm.ptr, i64)>
%v84 = arith.extsi %v82 : i32 to i64
%v85 = llvm.getelementptr %v83[%v84] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v86 = llvm.load %v85 : !llvm.ptr -> f64
%v87 = llvm.load %v77 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v88 = arith.constant 3 : i32
%v89 = llvm.extractvalue %v87[0] : !llvm.struct<(!llvm.ptr, i64)>
%v90 = arith.extsi %v88 : i32 to i64
%v91 = llvm.getelementptr %v89[%v90] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v92 = llvm.load %v91 : !llvm.ptr -> f64
%v93 = llvm.call @printf(%v80, %v86, %v92) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v94 = llvm.load %v77 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v95 = arith.constant 4 : i32
func.call @via_data(%v94, %v95) : (!llvm.struct<(!llvm.ptr, i64)>, i32) -> ()
%v96 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v97 = llvm.load %v77 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v98 = arith.constant 1 : i32
%v99 = llvm.extractvalue %v97[0] : !llvm.struct<(!llvm.ptr, i64)>
%v100 = arith.extsi %v98 : i32 to i64
%v101 = llvm.getelementptr %v99[%v100] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v102 = llvm.load %v101 : !llvm.ptr -> f64
%v103 = llvm.load %v77 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v104 = arith.constant 3 : i32
%v105 = llvm.extractvalue %v103[0] : !llvm.struct<(!llvm.ptr, i64)>
%v106 = arith.extsi %v104 : i32 to i64
%v107 = llvm.getelementptr %v105[%v106] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v108 = llvm.load %v107 : !llvm.ptr -> f64
%v109 = llvm.call @printf(%v96, %v102, %v108) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v110 = arith.constant 0 : i32
func.return %v110 : i32
}
}
