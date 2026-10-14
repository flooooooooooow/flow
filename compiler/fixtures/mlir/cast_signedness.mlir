module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d %u %llu %llu\0A\00") {addr_space = 0 : i32} : !llvm.array<17 x i8>
func.func @magnitude(%arg0: i64) -> i64 {
%v1 = arith.constant 0 : i32
%v2 = arith.extsi %v1 : i32 to i64
%v3 = arith.cmpi sge, %arg0, %v2 : i64
cf.cond_br %v3, ^b1, ^b2
^b1:
%v4 = arith.bitcast %arg0 : i64 to i64
func.return %v4 : i64
^b2:
cf.br ^b3
^b3:
%v5 = arith.constant 0 : i32
%v6 = arith.extsi %v5 : i32 to i64
%v7 = arith.bitcast %arg0 : i64 to i64
%v8 = arith.subi %v6, %v7 : i64
func.return %v8 : i64
}
func.func @distance(%arg0: i64, %arg1: i64) -> i64 {
%v9 = arith.constant 0 : i32
%v10 = arith.extsi %v9 : i32 to i64
%v11 = arith.cmpi sge, %arg0, %v10 : i64
%v12 = scf.if %v11 -> (i1) {
%v13 = arith.constant 0 : i32
%v14 = arith.extsi %v13 : i32 to i64
%v15 = arith.cmpi slt, %arg1, %v14 : i64
scf.yield %v15 : i1
} else {
%v16 = arith.constant false
scf.yield %v16 : i1
}
cf.cond_br %v12, ^b4, ^b5
^b4:
%v17 = arith.bitcast %arg0 : i64 to i64
%v18 = func.call @magnitude(%arg1) : (i64) -> i64
%v19 = arith.addi %v17, %v18 : i64
func.return %v19 : i64
^b5:
cf.br ^b6
^b6:
%v20 = arith.constant 0 : i32
%v21 = arith.extsi %v20 : i32 to i64
%v22 = arith.cmpi slt, %arg0, %v21 : i64
%v23 = scf.if %v22 -> (i1) {
%v24 = arith.constant 0 : i32
%v25 = arith.extsi %v24 : i32 to i64
%v26 = arith.cmpi sge, %arg1, %v25 : i64
scf.yield %v26 : i1
} else {
%v27 = arith.constant false
scf.yield %v27 : i1
}
cf.cond_br %v23, ^b7, ^b8
^b7:
%v28 = func.call @magnitude(%arg0) : (i64) -> i64
%v29 = arith.bitcast %arg1 : i64 to i64
%v30 = arith.addi %v28, %v29 : i64
func.return %v30 : i64
^b8:
cf.br ^b9
^b9:
%v31 = arith.cmpi sge, %arg0, %arg1 : i64
cf.cond_br %v31, ^b10, ^b11
^b10:
%v32 = arith.subi %arg0, %arg1 : i64
func.return %v32 : i64
^b11:
cf.br ^b12
^b12:
%v33 = arith.subi %arg1, %arg0 : i64
func.return %v33 : i64
}
func.func @main() -> i32 {
%v34 = arith.constant 5 : i32
%v35 = arith.constant 0 : i32
%v36 = arith.subi %v35, %v34 : i32
%v37 = llvm.mlir.constant(1 : i64) : i64
%v38 = llvm.alloca %v37 x i32 : (i64) -> !llvm.ptr
llvm.store %v36, %v38 : i32, !llvm.ptr
%v39 = llvm.load %v38 : !llvm.ptr -> i32
%v40 = llvm.load %v38 : !llvm.ptr -> i32
%v41 = arith.constant 0 : i32
%v42 = arith.cmpi slt, %v40, %v41 : i32
%v43 = arith.constant 3 : i32
%v44 = arith.constant 0 : i32
%v45 = arith.subi %v44, %v43 : i32
%v46 = arith.constant 4 : i32
%v47 = arith.extsi %v45 : i32 to i64
%v48 = arith.extsi %v46 : i32 to i64
%v49 = func.call @distance(%v47, %v48) : (i64, i64) -> i64
%v50 = arith.constant 2 : i32
%v51 = arith.constant 9 : i32
%v52 = arith.extsi %v50 : i32 to i64
%v53 = arith.extsi %v51 : i32 to i64
%v54 = func.call @distance(%v52, %v53) : (i64, i64) -> i64
%v55 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v56 = scf.if %v42 -> (i32) {
%v57 = arith.constant 1 : i32
scf.yield %v57 : i32
} else {
%v58 = arith.constant 0 : i32
scf.yield %v58 : i32
}
%v59 = llvm.call @printf(%v55, %v56, %v39, %v49, %v54) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32, i32, i64, i64) -> i32
%v60 = arith.constant 1 : i1
%v61 = arith.xori %v42, %v60 : i1
%v62 = scf.if %v61 -> (i1) {
%v63 = arith.constant true
scf.yield %v63 : i1
} else {
%v64 = arith.constant 7 : i32
%v65 = arith.extsi %v64 : i32 to i64
%v66 = arith.cmpi ne, %v49, %v65 : i64
scf.yield %v66 : i1
}
%v67 = scf.if %v62 -> (i1) {
%v68 = arith.constant true
scf.yield %v68 : i1
} else {
%v69 = arith.constant 7 : i32
%v70 = arith.extsi %v69 : i32 to i64
%v71 = arith.cmpi ne, %v54, %v70 : i64
scf.yield %v71 : i1
}
cf.cond_br %v67, ^b13, ^b14
^b13:
%v72 = arith.constant 1 : i32
func.return %v72 : i32
^b14:
cf.br ^b15
^b15:
%v73 = arith.constant 0 : i32
func.return %v73 : i32
}
}
