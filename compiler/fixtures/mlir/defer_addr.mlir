module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("defer %d\0A\00") {addr_space = 0 : i32} : !llvm.array<10 x i8>
llvm.mlir.global internal constant @str_1("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
// Struct: Counter
// Fields:
//   hits: i32
//   last: i32
func.func @note(%arg0: i32) -> () {
%v1 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v2 = llvm.call @printf(%v1, %arg0) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
func.return
}
func.func @bump(%arg0: !llvm.ptr) -> () {
%v3 = arith.constant 0 : i32
%v4 = arith.extsi %v3 : i32 to i64
%v5 = llvm.getelementptr %arg0[%v4] : (!llvm.ptr, i64) -> !llvm.ptr, i32
%v6 = llvm.load %v5 : !llvm.ptr -> i32
%v7 = arith.constant 1 : i32
%v8 = arith.addi %v6, %v7 : i32
%v9 = arith.constant 0 : i32
%v10 = arith.extsi %v9 : i32 to i64
%v11 = llvm.getelementptr %arg0[%v10] : (!llvm.ptr, i64) -> !llvm.ptr, i32
llvm.store %v8, %v11 : i32, !llvm.ptr
func.return
}
func.func @deferred(%arg0: i32) -> i32 {
%v12 = arith.constant 0 : i32
%v13 = llvm.mlir.constant(1 : i64) : i64
%v14 = llvm.alloca %v13 x i32 : (i64) -> !llvm.ptr
llvm.store %v12, %v14 : i32, !llvm.ptr
cf.br ^b1
^b1:
%v15 = llvm.load %v14 : !llvm.ptr -> i32
%v16 = arith.cmpi slt, %v15, %arg0 : i32
cf.cond_br %v16, ^b2, ^b3
^b2:
%v17 = llvm.load %v14 : !llvm.ptr -> i32
%v18 = arith.constant 2 : i32
%v19 = arith.cmpi eq, %v17, %v18 : i32
cf.cond_br %v19, ^b4, ^b5
^b4:
%v20 = arith.constant 2 : i32
func.call @note(%v20) : (i32) -> ()
cf.br ^b3
^b5:
cf.br ^b6
^b6:
%v21 = llvm.load %v14 : !llvm.ptr -> i32
%v22 = arith.constant 1 : i32
%v23 = arith.addi %v21, %v22 : i32
llvm.store %v23, %v14 : i32, !llvm.ptr
%v24 = arith.constant 2 : i32
func.call @note(%v24) : (i32) -> ()
cf.br ^b1
^b3:
%v25 = llvm.load %v14 : !llvm.ptr -> i32
%v26 = arith.constant 10 : i32
%v27 = arith.muli %v25, %v26 : i32
%v28 = arith.constant 3 : i32
func.call @note(%v28) : (i32) -> ()
%v29 = arith.constant 1 : i32
func.call @note(%v29) : (i32) -> ()
func.return %v27 : i32
}
func.func @main() -> i32 {
%v30 = arith.constant 5 : i32
%v31 = func.call @deferred(%v30) : (i32) -> i32
%v32 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v33 = llvm.call @printf(%v32, %v31) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v34 = arith.constant 0 : i32
%v35 = arith.constant 41 : i32
%v36 = llvm.mlir.constant(1 : i64) : i64
%v37 = llvm.alloca %v36 x i32 : (i64) -> !llvm.ptr
llvm.store %v35, %v37 : i32, !llvm.ptr
func.call @bump(%v37) : (!llvm.ptr) -> ()
%v38 = llvm.load %v37 : !llvm.ptr -> i32
%v39 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v40 = llvm.call @printf(%v39, %v38) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v41 = arith.constant 0 : i32
%v42 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v43 = arith.constant 0 : i32
%v44 = llvm.insertvalue %v43, %v42[0] : !llvm.struct<(i32, i32)>
%v45 = arith.constant 0 : i32
%v46 = llvm.insertvalue %v45, %v44[1] : !llvm.struct<(i32, i32)>
%v47 = llvm.mlir.constant(1 : i64) : i64
%v48 = llvm.alloca %v47 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v46, %v48 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v49 = llvm.getelementptr %v48[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
func.call @bump(%v49) : (!llvm.ptr) -> ()
%v50 = llvm.getelementptr %v48[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
func.call @bump(%v50) : (!llvm.ptr) -> ()
%v51 = llvm.load %v48 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v52 = llvm.getelementptr %v48[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v53 = llvm.load %v52 : !llvm.ptr -> i32
%v54 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v55 = llvm.call @printf(%v54, %v53) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v56 = arith.constant 0 : i32
%v57 = arith.constant 1 : i32
%v58 = arith.constant 2 : i32
%v59 = arith.constant 3 : i32
%v60 = llvm.mlir.constant(1 : i64) : i64
%v61 = llvm.alloca %v60 x !llvm.array<3 x i32> : (i64) -> !llvm.ptr
%v62 = llvm.mlir.zero : !llvm.array<3 x i32>
llvm.store %v62, %v61 : !llvm.array<3 x i32>, !llvm.ptr
%v63 = llvm.mlir.constant(0 : i64) : i64
%v64 = llvm.getelementptr %v61[0, %v63] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v57, %v64 : i32, !llvm.ptr
%v65 = llvm.mlir.constant(1 : i64) : i64
%v66 = llvm.getelementptr %v61[0, %v65] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v58, %v66 : i32, !llvm.ptr
%v67 = llvm.mlir.constant(2 : i64) : i64
%v68 = llvm.getelementptr %v61[0, %v67] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v59, %v68 : i32, !llvm.ptr
%v69 = arith.constant 1 : i32
%v70 = arith.extsi %v69 : i32 to i64
%v71 = llvm.getelementptr %v61[0, %v70] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
func.call @bump(%v71) : (!llvm.ptr) -> ()
%v72 = arith.constant 1 : i32
%v73 = arith.extsi %v72 : i32 to i64
%v74 = llvm.getelementptr %v61[0, %v73] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
%v75 = llvm.load %v74 : !llvm.ptr -> i32
%v76 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v77 = llvm.call @printf(%v76, %v75) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v78 = arith.constant 0 : i32
%v79 = arith.constant 5 : i32
%v80 = llvm.mlir.constant(1 : i64) : i64
%v81 = llvm.alloca %v80 x i32 : (i64) -> !llvm.ptr
llvm.store %v79, %v81 : i32, !llvm.ptr
%v82 = arith.constant 0 : i32
%v83 = arith.extsi %v82 : i32 to i64
%v84 = llvm.getelementptr %v81[%v83] : (!llvm.ptr, i64) -> !llvm.ptr, i32
%v85 = llvm.load %v84 : !llvm.ptr -> i32
%v86 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v87 = llvm.call @printf(%v86, %v85) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v88 = arith.constant 0 : i32
%v89 = arith.constant 0 : i32
func.return %v89 : i32
}
}
