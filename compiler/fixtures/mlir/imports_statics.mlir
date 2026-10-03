module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("statics\00") {addr_space = 0 : i32} : !llvm.array<8 x i8>
llvm.mlir.global internal constant @str_1("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_2("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_3("%s\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
// Module static: dep_calls
llvm.mlir.global internal @dep_calls(0 : i32) : i32
func.func @dep_scale(%arg0: i32) -> i32 {
%v1 = llvm.mlir.addressof @dep_calls : !llvm.ptr
%v2 = llvm.load %v1 : !llvm.ptr -> i32
%v3 = arith.constant 1 : i32
%v4 = arith.addi %v2, %v3 : i32
%v5 = llvm.mlir.addressof @dep_calls : !llvm.ptr
llvm.store %v4, %v5 : i32, !llvm.ptr
%v6 = arith.constant 3 : i32
%v7 = arith.muli %arg0, %v6 : i32
func.return %v7 : i32
}
func.func @dep_total() -> i32 {
%v8 = llvm.mlir.addressof @dep_calls : !llvm.ptr
%v9 = llvm.load %v8 : !llvm.ptr -> i32
func.return %v9 : i32
}
// Module static: counter
llvm.mlir.global internal @counter(0 : i32) : i32
// Module static: table
llvm.mlir.global internal @table() : !llvm.array<4 x i32> {
%v10 = llvm.mlir.zero : !llvm.array<4 x i32>
%v11 = llvm.mlir.constant(3 : i32) : i32
%v12 = llvm.insertvalue %v11, %v10[0] : !llvm.array<4 x i32>
%v13 = llvm.mlir.constant(1 : i32) : i32
%v14 = llvm.insertvalue %v13, %v12[1] : !llvm.array<4 x i32>
%v15 = llvm.mlir.constant(4 : i32) : i32
%v16 = llvm.insertvalue %v15, %v14[2] : !llvm.array<4 x i32>
%v17 = llvm.mlir.constant(1 : i32) : i32
%v18 = llvm.insertvalue %v17, %v16[3] : !llvm.array<4 x i32>
llvm.return %v18 : !llvm.array<4 x i32>
}
// Module static: scale
llvm.mlir.global internal @scale(2.50000000000000000e+00 : f64) : f64
// Module static (string): label
llvm.mlir.global internal @label() {addr_space = 0 : i32} : !llvm.ptr {
%v19 = llvm.mlir.addressof @str_0 : !llvm.ptr
llvm.return %v19 : !llvm.ptr
}
func.func @next_id() -> i32 {
%v20 = llvm.mlir.addressof @counter : !llvm.ptr
%v21 = llvm.load %v20 : !llvm.ptr -> i32
%v22 = arith.constant 1 : i32
%v23 = arith.addi %v21, %v22 : i32
%v24 = llvm.mlir.addressof @counter : !llvm.ptr
llvm.store %v23, %v24 : i32, !llvm.ptr
%v25 = llvm.mlir.addressof @counter : !llvm.ptr
%v26 = llvm.load %v25 : !llvm.ptr -> i32
func.return %v26 : i32
}
func.func @main() -> i32 {
%v27 = func.call @next_id() : () -> i32
%v28 = func.call @next_id() : () -> i32
%v29 = llvm.mlir.addressof @counter : !llvm.ptr
%v30 = llvm.load %v29 : !llvm.ptr -> i32
%v31 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v32 = llvm.call @printf(%v31, %v30) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v33 = arith.constant 0 : i32
%v34 = arith.constant 9 : i32
%v35 = llvm.mlir.addressof @table : !llvm.ptr
%v36 = arith.constant 2 : i32
%v37 = arith.extsi %v36 : i32 to i64
%v38 = llvm.getelementptr %v35[0, %v37] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x i32>
llvm.store %v34, %v38 : i32, !llvm.ptr
%v39 = arith.constant 0 : i32
%v40 = llvm.mlir.constant(1 : i64) : i64
%v41 = llvm.alloca %v40 x i32 : (i64) -> !llvm.ptr
llvm.store %v39, %v41 : i32, !llvm.ptr
%v42 = arith.constant 0 : i32
%v43 = arith.constant 4 : i32
%v44 = arith.index_cast %v42 : i32 to index
%v45 = arith.index_cast %v43 : i32 to index
%v46 = arith.constant 1 : index
%v47 = arith.constant -1 : index
%v48 = arith.cmpi sle, %v44, %v45 : index
%v49 = arith.select %v48, %v46, %v47 : index
cf.br ^b1(%v44 : index)
^b1(%v50: index):
%v51 = arith.cmpi slt, %v50, %v45 : index
%v52 = arith.cmpi sgt, %v50, %v45 : index
%v53 = arith.select %v48, %v51, %v52 : i1
cf.cond_br %v53, ^b2(%v50 : index), ^b3(%v50 : index)
^b2(%v54: index):
%v55 = llvm.load %v41 : !llvm.ptr -> i32
%v56 = llvm.mlir.addressof @table : !llvm.ptr
%v57 = arith.index_cast %v54 : index to i64
%v58 = llvm.getelementptr %v56[0, %v57] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x i32>
%v59 = llvm.load %v58 : !llvm.ptr -> i32
%v60 = arith.addi %v55, %v59 : i32
llvm.store %v60, %v41 : i32, !llvm.ptr
%v61 = arith.addi %v54, %v49 : index
cf.br ^b1(%v61 : index)
^b3(%v62: index):
%v63 = llvm.load %v41 : !llvm.ptr -> i32
%v64 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v65 = llvm.call @printf(%v64, %v63) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v66 = arith.constant 0 : i32
%v67 = llvm.mlir.addressof @scale : !llvm.ptr
%v68 = llvm.load %v67 : !llvm.ptr -> f64
%v69 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v70 = llvm.call @printf(%v69, %v68) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v71 = arith.constant 0 : i32
%v72 = llvm.mlir.addressof @label : !llvm.ptr
%v73 = llvm.load %v72 : !llvm.ptr -> !llvm.ptr
%v74 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v75 = llvm.call @printf(%v74, %v73) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, !llvm.ptr) -> i32
%v76 = arith.constant 0 : i32
%v77 = arith.constant 7 : i32
%v78 = func.call @dep_scale(%v77) : (i32) -> i32
%v79 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v80 = llvm.call @printf(%v79, %v78) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v81 = arith.constant 0 : i32
%v82 = llvm.mlir.addressof @dep_calls : !llvm.ptr
%v83 = llvm.load %v82 : !llvm.ptr -> i32
%v84 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v85 = llvm.call @printf(%v84, %v83) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v86 = arith.constant 0 : i32
%v87 = arith.constant 0 : i32
func.return %v87 : i32
}
}
