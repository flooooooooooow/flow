module {
func.func @matmul_naive(%arg0: !llvm.ptr, %arg1: !llvm.ptr, %arg2: !llvm.ptr) -> i32 {
%v1 = arith.constant 0 : i32
%v2 = arith.constant 2 : i32
%v3 = arith.index_cast %v1 : i32 to index
%v4 = arith.index_cast %v2 : i32 to index
%v5 = arith.constant 1 : index
%v6 = arith.constant -1 : index
%v7 = arith.cmpi sle, %v3, %v4 : index
%v8 = arith.select %v7, %v5, %v6 : index
cf.br ^b1(%v3 : index)
^b1(%v9: index):
%v10 = arith.cmpi slt, %v9, %v4 : index
%v11 = arith.cmpi sgt, %v9, %v4 : index
%v12 = arith.select %v7, %v10, %v11 : i1
cf.cond_br %v12, ^b2(%v9 : index), ^b3(%v9 : index)
^b2(%v13: index):
%v14 = arith.constant 0 : i32
%v15 = arith.constant 2 : i32
%v16 = arith.index_cast %v14 : i32 to index
%v17 = arith.index_cast %v15 : i32 to index
%v18 = arith.constant 1 : index
%v19 = arith.constant -1 : index
%v20 = arith.cmpi sle, %v16, %v17 : index
%v21 = arith.select %v20, %v18, %v19 : index
cf.br ^b4(%v16 : index)
^b4(%v22: index):
%v23 = arith.cmpi slt, %v22, %v17 : index
%v24 = arith.cmpi sgt, %v22, %v17 : index
%v25 = arith.select %v20, %v23, %v24 : i1
cf.cond_br %v25, ^b5(%v22 : index), ^b6(%v22 : index)
^b5(%v26: index):
%v27 = arith.constant 0.0 : f32
%v28 = llvm.mlir.constant(1 : i64) : i64
%v29 = llvm.alloca %v28 x f32 : (i64) -> !llvm.ptr
llvm.store %v27, %v29 : f32, !llvm.ptr
%v30 = arith.constant 0 : i32
%v31 = arith.constant 2 : i32
%v32 = arith.index_cast %v30 : i32 to index
%v33 = arith.index_cast %v31 : i32 to index
%v34 = arith.constant 1 : index
%v35 = arith.constant -1 : index
%v36 = arith.cmpi sle, %v32, %v33 : index
%v37 = arith.select %v36, %v34, %v35 : index
cf.br ^b7(%v32 : index)
^b7(%v38: index):
%v39 = arith.cmpi slt, %v38, %v33 : index
%v40 = arith.cmpi sgt, %v38, %v33 : index
%v41 = arith.select %v36, %v39, %v40 : i1
cf.cond_br %v41, ^b8(%v38 : index), ^b9(%v38 : index)
^b8(%v42: index):
%v43 = llvm.load %v29 : !llvm.ptr -> f32
%v44 = arith.constant 2 : i32
%v45 = arith.index_cast %v13 : index to i32
%v46 = arith.muli %v45, %v44 : i32
%v47 = arith.index_cast %v42 : index to i32
%v48 = arith.addi %v46, %v47 : i32
%v49 = arith.extsi %v48 : i32 to i64
%v50 = llvm.getelementptr %arg1[0, %v49] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f32>
%v51 = llvm.load %v50 : !llvm.ptr -> f32
%v52 = arith.constant 2 : i32
%v53 = arith.index_cast %v42 : index to i32
%v54 = arith.muli %v53, %v52 : i32
%v55 = arith.index_cast %v26 : index to i32
%v56 = arith.addi %v54, %v55 : i32
%v57 = arith.extsi %v56 : i32 to i64
%v58 = llvm.getelementptr %arg2[0, %v57] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f32>
%v59 = llvm.load %v58 : !llvm.ptr -> f32
%v60 = arith.mulf %v51, %v59 : f32
%v61 = arith.addf %v43, %v60 : f32
llvm.store %v61, %v29 : f32, !llvm.ptr
%v62 = arith.addi %v42, %v37 : index
cf.br ^b7(%v62 : index)
^b9(%v63: index):
%v64 = llvm.load %v29 : !llvm.ptr -> f32
%v65 = arith.constant 2 : i32
%v66 = arith.index_cast %v13 : index to i32
%v67 = arith.muli %v66, %v65 : i32
%v68 = arith.index_cast %v26 : index to i32
%v69 = arith.addi %v67, %v68 : i32
%v70 = arith.extsi %v69 : i32 to i64
%v71 = llvm.getelementptr %arg0[0, %v70] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f32>
llvm.store %v64, %v71 : f32, !llvm.ptr
%v72 = arith.addi %v26, %v21 : index
cf.br ^b4(%v72 : index)
^b6(%v73: index):
%v74 = arith.addi %v13, %v8 : index
cf.br ^b1(%v74 : index)
^b3(%v75: index):
%v76 = arith.constant 0 : i32
func.return %v76 : i32
}
func.func @main() -> i32 {
%v77 = arith.constant 0 : i32
func.return %v77 : i32
}
}
