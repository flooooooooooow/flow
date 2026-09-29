module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("defer %d\n\00") {addr_space = 0 : i32} : !llvm.array<10 x i8>
llvm.mlir.global internal constant @str_1("%d\n\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
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
cf.br ^b3
^b5:
cf.br ^b6
^b6:
%v20 = llvm.load %v14 : !llvm.ptr -> i32
%v21 = arith.constant 1 : i32
%v22 = arith.addi %v20, %v21 : i32
llvm.store %v22, %v14 : i32, !llvm.ptr
%v23 = arith.constant 2 : i32
func.call @note(%v23) : (i32) -> ()
cf.br ^b1
^b3:
%v24 = llvm.load %v14 : !llvm.ptr -> i32
%v25 = arith.constant 10 : i32
%v26 = arith.muli %v24, %v25 : i32
%v27 = arith.constant 3 : i32
func.call @note(%v27) : (i32) -> ()
%v28 = arith.constant 1 : i32
func.call @note(%v28) : (i32) -> ()
func.return %v26 : i32
}
func.func @main() -> i32 {
%v29 = arith.constant 5 : i32
%v30 = func.call @deferred(%v29) : (i32) -> i32
%v31 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v32 = llvm.call @printf(%v31, %v30) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v33 = arith.constant 0 : i32
%v34 = arith.constant 41 : i32
%v35 = llvm.mlir.constant(1 : i64) : i64
%v36 = llvm.alloca %v35 x i32 : (i64) -> !llvm.ptr
llvm.store %v34, %v36 : i32, !llvm.ptr
func.call @bump(%v36) : (!llvm.ptr) -> ()
%v37 = llvm.load %v36 : !llvm.ptr -> i32
%v38 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v39 = llvm.call @printf(%v38, %v37) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v40 = arith.constant 0 : i32
%v41 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v42 = arith.constant 0 : i32
%v43 = llvm.insertvalue %v42, %v41[0] : !llvm.struct<(i32, i32)>
%v44 = arith.constant 0 : i32
%v45 = llvm.insertvalue %v44, %v43[1] : !llvm.struct<(i32, i32)>
%v46 = llvm.mlir.constant(1 : i64) : i64
%v47 = llvm.alloca %v46 x !llvm.struct<(i32, i32)> : (i64) -> !llvm.ptr
llvm.store %v45, %v47 : !llvm.struct<(i32, i32)>, !llvm.ptr
%v48 = llvm.getelementptr %v47[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
func.call @bump(%v48) : (!llvm.ptr) -> ()
%v49 = llvm.getelementptr %v47[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
func.call @bump(%v49) : (!llvm.ptr) -> ()
%v50 = llvm.load %v47 : !llvm.ptr -> !llvm.struct<(i32, i32)>
%v51 = llvm.getelementptr %v47[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32, i32)>
%v52 = llvm.load %v51 : !llvm.ptr -> i32
%v53 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v54 = llvm.call @printf(%v53, %v52) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v55 = arith.constant 0 : i32
%v56 = arith.constant 1 : i32
%v57 = arith.constant 2 : i32
%v58 = arith.constant 3 : i32
%v59 = llvm.mlir.constant(1 : i64) : i64
%v60 = llvm.alloca %v59 x !llvm.array<3 x i32> : (i64) -> !llvm.ptr
%v61 = llvm.mlir.zero : !llvm.array<3 x i32>
llvm.store %v61, %v60 : !llvm.array<3 x i32>, !llvm.ptr
%v62 = llvm.mlir.constant(0 : i64) : i64
%v63 = llvm.getelementptr %v60[0, %v62] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v56, %v63 : i32, !llvm.ptr
%v64 = llvm.mlir.constant(1 : i64) : i64
%v65 = llvm.getelementptr %v60[0, %v64] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v57, %v65 : i32, !llvm.ptr
%v66 = llvm.mlir.constant(2 : i64) : i64
%v67 = llvm.getelementptr %v60[0, %v66] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v58, %v67 : i32, !llvm.ptr
%v68 = arith.constant 1 : i32
%v69 = arith.extsi %v68 : i32 to i64
%v70 = llvm.getelementptr %v60[0, %v69] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
func.call @bump(%v70) : (!llvm.ptr) -> ()
%v71 = arith.constant 1 : i32
%v72 = arith.extsi %v71 : i32 to i64
%v73 = llvm.getelementptr %v60[0, %v72] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
%v74 = llvm.load %v73 : !llvm.ptr -> i32
%v75 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v76 = llvm.call @printf(%v75, %v74) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v77 = arith.constant 0 : i32
%v78 = arith.constant 5 : i32
%v79 = llvm.mlir.constant(1 : i64) : i64
%v80 = llvm.alloca %v79 x i32 : (i64) -> !llvm.ptr
llvm.store %v78, %v80 : i32, !llvm.ptr
%v81 = arith.constant 0 : i32
%v82 = arith.extsi %v81 : i32 to i64
%v83 = llvm.getelementptr %v80[%v82] : (!llvm.ptr, i64) -> !llvm.ptr, i32
%v84 = llvm.load %v83 : !llvm.ptr -> i32
%v85 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v86 = llvm.call @printf(%v85, %v84) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v87 = arith.constant 0 : i32
%v88 = arith.constant 0 : i32
func.return %v88 : i32
}
}
