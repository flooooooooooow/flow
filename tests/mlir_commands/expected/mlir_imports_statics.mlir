module {
func.func private @strlen(!llvm.ptr) -> i64
func.func private @write(i32, !llvm.ptr, i64) -> i64
func.func private @abort() -> ()
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("statics\00") {addr_space = 0 : i32} : !llvm.array<8 x i8>
llvm.mlir.global internal constant @str_1("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_2("flow: \00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
llvm.mlir.global internal constant @str_3("\0A\00") {addr_space = 0 : i32} : !llvm.array<2 x i8>
llvm.mlir.global internal constant @str_4("array index out of bounds\00") {addr_space = 0 : i32} : !llvm.array<26 x i8>
llvm.mlir.global internal constant @str_5("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_6("%s\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
func.func private @__flow_fault(%arg0: !llvm.ptr) {
%fd = arith.constant 2 : i32
%pre = llvm.mlir.addressof @str_2 : !llvm.ptr
%n6 = arith.constant 6 : i64
%w0 = func.call @write(%fd, %pre, %n6) : (i32, !llvm.ptr, i64) -> i64
%n = func.call @strlen(%arg0) : (!llvm.ptr) -> i64
%w1 = func.call @write(%fd, %arg0, %n) : (i32, !llvm.ptr, i64) -> i64
%nl = llvm.mlir.addressof @str_3 : !llvm.ptr
%n1 = arith.constant 1 : i64
%w2 = func.call @write(%fd, %nl, %n1) : (i32, !llvm.ptr, i64) -> i64
func.call @abort() : () -> ()
func.return
}
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
%v57 = arith.index_cast %v54 : index to i32
%v58 = arith.constant 4 : i32
%v59 = arith.cmpi uge, %v57, %v58 : i32
scf.if %v59 {
%v60 = llvm.mlir.addressof @str_4 : !llvm.ptr
func.call @__flow_fault(%v60) : (!llvm.ptr) -> ()
}
%v61 = arith.index_cast %v54 : index to i64
%v62 = llvm.getelementptr %v56[0, %v61] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x i32>
%v63 = llvm.load %v62 : !llvm.ptr -> i32
%v64 = arith.addi %v55, %v63 : i32
llvm.store %v64, %v41 : i32, !llvm.ptr
%v65 = arith.addi %v54, %v49 : index
cf.br ^b1(%v65 : index)
^b3(%v66: index):
%v67 = llvm.load %v41 : !llvm.ptr -> i32
%v68 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v69 = llvm.call @printf(%v68, %v67) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v70 = arith.constant 0 : i32
%v71 = llvm.mlir.addressof @scale : !llvm.ptr
%v72 = llvm.load %v71 : !llvm.ptr -> f64
%v73 = llvm.mlir.addressof @str_5 : !llvm.ptr
%v74 = llvm.call @printf(%v73, %v72) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v75 = arith.constant 0 : i32
%v76 = llvm.mlir.addressof @label : !llvm.ptr
%v77 = llvm.load %v76 : !llvm.ptr -> !llvm.ptr
%v78 = llvm.mlir.addressof @str_6 : !llvm.ptr
%v79 = llvm.call @printf(%v78, %v77) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, !llvm.ptr) -> i32
%v80 = arith.constant 0 : i32
%v81 = arith.constant 7 : i32
%v82 = func.call @dep_scale(%v81) : (i32) -> i32
%v83 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v84 = llvm.call @printf(%v83, %v82) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v85 = arith.constant 0 : i32
%v86 = llvm.mlir.addressof @dep_calls : !llvm.ptr
%v87 = llvm.load %v86 : !llvm.ptr -> i32
%v88 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v89 = llvm.call @printf(%v88, %v87) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v90 = arith.constant 0 : i32
%v91 = arith.constant 0 : i32
func.return %v91 : i32
}
}
