module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
func.func @merges(%arg0: i32) -> i32 {
%v1 = llvm.mlir.undef : i32
%v2 = arith.constant 0 : i32
%v3 = llvm.mlir.undef : i32
%v4 = arith.constant 0 : i32
cf.br ^b1(%v2, %v4 : i32, i32)
^b1(%v5: i32, %v6: i32):
%v7 = arith.cmpi slt, %v6, %arg0 : i32
cf.cond_br %v7, ^b2(%v5, %v6 : i32, i32), ^b3(%v5, %v6 : i32, i32)
^b2(%v8: i32, %v9: i32):
%v10 = arith.constant 3 : i32
%v11 = arith.cmpi sgt, %v9, %v10 : i32
%v12 = scf.if %v11 -> (i32) {
%v13 = arith.addi %v8, %v9 : i32
scf.yield %v13 : i32
} else {
%v14 = arith.constant 1 : i32
%v15 = arith.subi %v8, %v14 : i32
scf.yield %v15 : i32
}
%v16 = arith.constant 1 : i32
%v17 = arith.addi %v9, %v16 : i32
cf.br ^b1(%v12, %v17 : i32, i32)
^b3(%v18: i32, %v19: i32):
%v20 = arith.constant 0 : i32
%v21 = arith.index_cast %v20 : i32 to index
%v22 = arith.index_cast %arg0 : i32 to index
%v23 = arith.constant 1 : index
%v24 = arith.constant -1 : index
%v25 = arith.cmpi sle, %v21, %v22 : index
%v26 = arith.select %v25, %v23, %v24 : index
cf.br ^b4(%v21, %v18 : index, i32)
^b4(%v27: index, %v28: i32):
%v29 = arith.cmpi slt, %v27, %v22 : index
%v30 = arith.cmpi sgt, %v27, %v22 : index
%v31 = arith.select %v25, %v29, %v30 : i1
cf.cond_br %v31, ^b5(%v27, %v28 : index, i32), ^b6(%v27, %v28 : index, i32)
^b5(%v32: index, %v33: i32):
%v34 = arith.index_cast %v32 : index to i32
%v35 = arith.addi %v33, %v34 : i32
%v36 = arith.addi %v32, %v26 : index
cf.br ^b4(%v36, %v35 : index, i32)
^b6(%v37: index, %v38: i32):
%v39 = arith.constant 0 : i32
%v40 = arith.index_cast %v39 : i32 to index
%v41 = arith.index_cast %arg0 : i32 to index
%v42 = arith.constant 1 : index
%v43 = arith.constant -1 : index
%v44 = arith.cmpi sle, %v40, %v41 : index
%v45 = arith.select %v44, %v42, %v43 : index
cf.br ^b7(%v40, %v38 : index, i32)
^b7(%v46: index, %v47: i32):
%v48 = arith.cmpi slt, %v46, %v41 : index
%v49 = arith.cmpi sgt, %v46, %v41 : index
%v50 = arith.select %v44, %v48, %v49 : i1
cf.cond_br %v50, ^b8(%v46, %v47 : index, i32), ^b9(%v46, %v47 : index, i32)
^b8(%v51: index, %v52: i32):
%v53 = arith.constant 2 : i32
%v54 = arith.index_cast %v51 : index to i32
%v55 = arith.cmpi eq, %v54, %v53 : i32
cf.cond_br %v55, ^b10, ^b11
^b10:
%v56 = arith.addi %v51, %v45 : index
cf.br ^b7(%v56, %v52 : index, i32)
^b11:
cf.br ^b12
^b12:
%v57 = arith.constant 7 : i32
%v58 = arith.index_cast %v51 : index to i32
%v59 = arith.cmpi eq, %v58, %v57 : i32
cf.cond_br %v59, ^b13, ^b14
^b13:
cf.br ^b9(%v51, %v52 : index, i32)
^b14:
cf.br ^b15
^b15:
%v60 = arith.constant 1 : i32
%v61 = arith.addi %v52, %v60 : i32
%v62 = arith.addi %v51, %v45 : index
cf.br ^b7(%v62, %v61 : index, i32)
^b9(%v63: index, %v64: i32):
%v65 = arith.constant 100 : i32
%v66 = arith.cmpi sgt, %v64, %v65 : i32
cf.cond_br %v66, ^b16, ^b17
^b16:
%v67 = arith.constant 100 : i32
cf.br ^b18(%v67 : i32)
^b17:
%v68 = arith.constant 50 : i32
%v69 = arith.cmpi sgt, %v64, %v68 : i32
cf.cond_br %v69, ^b19, ^b20
^b19:
%v70 = arith.constant 50 : i32
cf.br ^b18(%v70 : i32)
^b20:
%v71 = arith.constant 2 : i32
%v72 = arith.muli %v64, %v71 : i32
cf.br ^b18(%v72 : i32)
^b18(%v73: i32):
func.return %v73 : i32
}
func.func @pick(%arg0: i32) -> i32 {
%v74 = llvm.mlir.undef : i32
%v75 = arith.constant 2 : i32
%v76 = arith.cmpi sgt, %arg0, %v75 : i32
%v77 = scf.if %v76 -> (i32) {
%v78 = arith.constant 5 : i32
scf.yield %v78 : i32
} else {
scf.yield %arg0 : i32
}
func.return %v77 : i32
}
func.func @params(%arg0: i32, %arg1: i32) -> i32 {
%v79 = arith.addi %arg0, %arg1 : i32
%v80 = arith.constant 10 : i32
%v81 = arith.cmpi sgt, %v79, %v80 : i32
%v82 = scf.if %v81 -> (i32) {
%v83 = arith.constant 1 : i32
scf.yield %v83 : i32
} else {
scf.yield %arg1 : i32
}
%v84 = arith.constant 100 : i32
%v85 = arith.muli %v79, %v84 : i32
%v86 = arith.addi %v85, %v82 : i32
func.return %v86 : i32
}
func.func @main() -> i32 {
%v87 = arith.constant 10 : i32
%v88 = func.call @merges(%v87) : (i32) -> i32
%v89 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v90 = llvm.call @printf(%v89, %v88) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v91 = arith.constant 0 : i32
%v92 = arith.constant 3 : i32
%v93 = func.call @merges(%v92) : (i32) -> i32
%v94 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v95 = llvm.call @printf(%v94, %v93) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v96 = arith.constant 0 : i32
%v97 = arith.constant 3 : i32
%v98 = func.call @pick(%v97) : (i32) -> i32
%v99 = arith.constant 1 : i32
%v100 = func.call @pick(%v99) : (i32) -> i32
%v101 = arith.addi %v98, %v100 : i32
%v102 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v103 = llvm.call @printf(%v102, %v101) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v104 = arith.constant 0 : i32
%v105 = arith.constant 4 : i32
%v106 = arith.constant 9 : i32
%v107 = func.call @params(%v105, %v106) : (i32, i32) -> i32
%v108 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v109 = llvm.call @printf(%v108, %v107) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v110 = arith.constant 0 : i32
%v111 = arith.constant 0 : i32
func.return %v111 : i32
}
}
