module {
func.func private @strlen(!llvm.ptr) -> i64
func.func private @write(i32, !llvm.ptr, i64) -> i64
func.func private @abort() -> ()
llvm.mlir.global internal constant @str_0("flow: \00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
llvm.mlir.global internal constant @str_1("\0A\00") {addr_space = 0 : i32} : !llvm.array<2 x i8>
llvm.mlir.global internal constant @str_2("array index out of bounds\00") {addr_space = 0 : i32} : !llvm.array<26 x i8>
func.func private @__flow_fault(%arg0: !llvm.ptr) {
%fd = arith.constant 2 : i32
%pre = llvm.mlir.addressof @str_0 : !llvm.ptr
%n6 = arith.constant 6 : i64
%w0 = func.call @write(%fd, %pre, %n6) : (i32, !llvm.ptr, i64) -> i64
%n = func.call @strlen(%arg0) : (!llvm.ptr) -> i64
%w1 = func.call @write(%fd, %arg0, %n) : (i32, !llvm.ptr, i64) -> i64
%nl = llvm.mlir.addressof @str_1 : !llvm.ptr
%n1 = arith.constant 1 : i64
%w2 = func.call @write(%fd, %nl, %n1) : (i32, !llvm.ptr, i64) -> i64
func.call @abort() : () -> ()
func.return
}
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
%v27 = arith.constant 0.0 : f64
%v28 = arith.truncf %v27 : f64 to f32
%v29 = llvm.mlir.constant(1 : i64) : i64
%v30 = llvm.alloca %v29 x f32 : (i64) -> !llvm.ptr
llvm.store %v28, %v30 : f32, !llvm.ptr
%v31 = arith.constant 0 : i32
%v32 = arith.constant 2 : i32
%v33 = arith.index_cast %v31 : i32 to index
%v34 = arith.index_cast %v32 : i32 to index
%v35 = arith.constant 1 : index
%v36 = arith.constant -1 : index
%v37 = arith.cmpi sle, %v33, %v34 : index
%v38 = arith.select %v37, %v35, %v36 : index
cf.br ^b7(%v33 : index)
^b7(%v39: index):
%v40 = arith.cmpi slt, %v39, %v34 : index
%v41 = arith.cmpi sgt, %v39, %v34 : index
%v42 = arith.select %v37, %v40, %v41 : i1
cf.cond_br %v42, ^b8(%v39 : index), ^b9(%v39 : index)
^b8(%v43: index):
%v44 = llvm.load %v30 : !llvm.ptr -> f32
%v45 = arith.constant 2 : i32
%v46 = arith.index_cast %v13 : index to i32
%v47 = arith.muli %v46, %v45 : i32
%v48 = arith.index_cast %v43 : index to i32
%v49 = arith.addi %v47, %v48 : i32
%v50 = arith.constant 4 : i32
%v51 = arith.cmpi uge, %v49, %v50 : i32
scf.if %v51 {
%v52 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v52) : (!llvm.ptr) -> ()
}
%v53 = arith.extsi %v49 : i32 to i64
%v54 = llvm.getelementptr %arg1[0, %v53] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f32>
%v55 = llvm.load %v54 : !llvm.ptr -> f32
%v56 = arith.constant 2 : i32
%v57 = arith.index_cast %v43 : index to i32
%v58 = arith.muli %v57, %v56 : i32
%v59 = arith.index_cast %v26 : index to i32
%v60 = arith.addi %v58, %v59 : i32
%v61 = arith.constant 4 : i32
%v62 = arith.cmpi uge, %v60, %v61 : i32
scf.if %v62 {
%v63 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v63) : (!llvm.ptr) -> ()
}
%v64 = arith.extsi %v60 : i32 to i64
%v65 = llvm.getelementptr %arg2[0, %v64] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f32>
%v66 = llvm.load %v65 : !llvm.ptr -> f32
%v67 = llvm.intr.fmuladd(%v55, %v66, %v44) : (f32, f32, f32) -> f32
llvm.store %v67, %v30 : f32, !llvm.ptr
%v68 = arith.addi %v43, %v38 : index
cf.br ^b7(%v68 : index)
^b9(%v69: index):
%v70 = llvm.load %v30 : !llvm.ptr -> f32
%v71 = arith.constant 2 : i32
%v72 = arith.index_cast %v13 : index to i32
%v73 = arith.muli %v72, %v71 : i32
%v74 = arith.index_cast %v26 : index to i32
%v75 = arith.addi %v73, %v74 : i32
%v76 = arith.extsi %v75 : i32 to i64
%v77 = llvm.getelementptr %arg0[0, %v76] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x f32>
llvm.store %v70, %v77 : f32, !llvm.ptr
%v78 = arith.addi %v26, %v21 : index
cf.br ^b4(%v78 : index)
^b6(%v79: index):
%v80 = arith.addi %v13, %v8 : index
cf.br ^b1(%v80 : index)
^b3(%v81: index):
%v82 = arith.constant 0 : i32
func.return %v82 : i32
}
func.func @main() -> i32 {
%v83 = arith.constant 0 : i32
func.return %v83 : i32
}
}
