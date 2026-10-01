module {
func.func private @malloc(i64) -> !llvm.ptr
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%.1f %.1f\0A\00") {addr_space = 0 : i32} : !llvm.array<11 x i8>
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
%v29 = arith.constant 0.5 : f64
%v30 = arith.addf %v28, %v29 : f64
func.call @put(%v26, %v30) : (!llvm.ptr, f64) -> ()
%v31 = arith.addi %v22, %v17 : index
cf.br ^b1(%v31 : index)
^b3(%v32: index):
func.return
}
func.func @via_data(%arg0: !llvm.struct<(!llvm.ptr, i64)>, %arg1: i32) -> () {
%v33 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v34 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i64)>
%v35 = llvm.insertvalue %v34, %v33[0] : !llvm.struct<(!llvm.ptr, i64)>
%v36 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i64)>
%v37 = llvm.insertvalue %v36, %v35[1] : !llvm.struct<(!llvm.ptr, i64)>
%v38 = llvm.mlir.constant(1 : i64) : i64
%v39 = llvm.alloca %v38 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v37, %v39 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v40 = arith.constant 0 : i32
%v41 = arith.index_cast %v40 : i32 to index
%v42 = arith.index_cast %arg1 : i32 to index
%v43 = arith.constant 1 : index
%v44 = arith.constant -1 : index
%v45 = arith.cmpi sle, %v41, %v42 : index
%v46 = arith.select %v45, %v43, %v44 : index
cf.br ^b4(%v41 : index)
^b4(%v47: index):
%v48 = arith.cmpi slt, %v47, %v42 : index
%v49 = arith.cmpi sgt, %v47, %v42 : index
%v50 = arith.select %v45, %v48, %v49 : i1
cf.cond_br %v50, ^b5(%v47 : index), ^b6(%v47 : index)
^b5(%v51: index):
%v52 = llvm.load %v39 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v53 = llvm.extractvalue %v52[0] : !llvm.struct<(!llvm.ptr, i64)>
%v54 = arith.index_cast %v51 : index to i64
%v55 = llvm.getelementptr %v53[%v54] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v56 = arith.index_cast %v51 : index to i64
%v57 = arith.sitofp %v56 : i64 to f64
%v58 = arith.constant 2.0 : f64
%v59 = arith.mulf %v57, %v58 : f64
func.call @put(%v55, %v59) : (!llvm.ptr, f64) -> ()
%v60 = arith.addi %v51, %v46 : index
cf.br ^b4(%v60 : index)
^b6(%v61: index):
func.return
}
func.func @main() -> i32 {
%v62 = arith.constant 32 : i32
%v63 = arith.extsi %v62 : i32 to i64
%v64 = func.call @malloc(%v63) : (i64) -> !llvm.ptr
%v65 = arith.constant 0 : i32
%v66 = arith.constant 4 : i32
%v67 = arith.extsi %v65 : i32 to i64
%v68 = arith.extsi %v66 : i32 to i64
%v69 = llvm.getelementptr %v64[%v67] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v70 = arith.subi %v68, %v67 : i64
%v71 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v72 = llvm.insertvalue %v69, %v71[0] : !llvm.struct<(!llvm.ptr, i64)>
%v73 = llvm.insertvalue %v70, %v72[1] : !llvm.struct<(!llvm.ptr, i64)>
%v74 = llvm.mlir.constant(1 : i64) : i64
%v75 = llvm.alloca %v74 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v73, %v75 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v76 = llvm.load %v75 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v77 = arith.constant 4 : i32
func.call @via_index(%v76, %v77) : (!llvm.struct<(!llvm.ptr, i64)>, i32) -> ()
%v78 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v79 = llvm.load %v75 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v80 = arith.constant 0 : i32
%v81 = llvm.extractvalue %v79[0] : !llvm.struct<(!llvm.ptr, i64)>
%v82 = arith.extsi %v80 : i32 to i64
%v83 = llvm.getelementptr %v81[%v82] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v84 = llvm.load %v83 : !llvm.ptr -> f64
%v85 = llvm.load %v75 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v86 = arith.constant 3 : i32
%v87 = llvm.extractvalue %v85[0] : !llvm.struct<(!llvm.ptr, i64)>
%v88 = arith.extsi %v86 : i32 to i64
%v89 = llvm.getelementptr %v87[%v88] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v90 = llvm.load %v89 : !llvm.ptr -> f64
%v91 = llvm.call @printf(%v78, %v84, %v90) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v92 = llvm.load %v75 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v93 = arith.constant 4 : i32
func.call @via_data(%v92, %v93) : (!llvm.struct<(!llvm.ptr, i64)>, i32) -> ()
%v94 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v95 = llvm.load %v75 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v96 = arith.constant 1 : i32
%v97 = llvm.extractvalue %v95[0] : !llvm.struct<(!llvm.ptr, i64)>
%v98 = arith.extsi %v96 : i32 to i64
%v99 = llvm.getelementptr %v97[%v98] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v100 = llvm.load %v99 : !llvm.ptr -> f64
%v101 = llvm.load %v75 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v102 = arith.constant 3 : i32
%v103 = llvm.extractvalue %v101[0] : !llvm.struct<(!llvm.ptr, i64)>
%v104 = arith.extsi %v102 : i32 to i64
%v105 = llvm.getelementptr %v103[%v104] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v106 = llvm.load %v105 : !llvm.ptr -> f64
%v107 = llvm.call @printf(%v94, %v100, %v106) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64) -> i32
%v108 = arith.constant 0 : i32
func.return %v108 : i32
}
}
