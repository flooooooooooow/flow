module {
func.func private @strlen(!llvm.ptr) -> i64
func.func private @write(i32, !llvm.ptr, i64) -> i64
func.func private @abort() -> ()
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("flow: \00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
llvm.mlir.global internal constant @str_1("\0A\00") {addr_space = 0 : i32} : !llvm.array<2 x i8>
llvm.mlir.global internal constant @str_2("division by zero\00") {addr_space = 0 : i32} : !llvm.array<17 x i8>
llvm.mlir.global internal constant @str_3("no newline, \00") {addr_space = 0 : i32} : !llvm.array<13 x i8>
llvm.mlir.global internal constant @str_4("with newline\0A\00") {addr_space = 0 : i32} : !llvm.array<14 x i8>
llvm.mlir.global internal constant @str_5("tab\09quote\22 backslash\5C end\0A\00") {addr_space = 0 : i32} : !llvm.array<27 x i8>
llvm.mlir.global internal constant @str_6("flow\00") {addr_space = 0 : i32} : !llvm.array<5 x i8>
llvm.mlir.global internal constant @str_7("%s\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_8("%s has %d letters and pi is %.3f\0A\00") {addr_space = 0 : i32} : !llvm.array<34 x i8>
llvm.mlir.global internal constant @str_9("plain\0A\00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
llvm.mlir.global internal constant @str_10("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_11("even and big\0A\00") {addr_space = 0 : i32} : !llvm.array<14 x i8>
llvm.mlir.global internal constant @str_12("odd or six\0A\00") {addr_space = 0 : i32} : !llvm.array<12 x i8>
llvm.mlir.global internal constant @str_13("non-negative\0A\00") {addr_space = 0 : i32} : !llvm.array<14 x i8>
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
func.func @is_even(%arg0: i32) -> i1 {
%v1 = arith.constant 2 : i32
%v2 = arith.constant 0 : i32
%v3 = arith.cmpi eq, %v1, %v2 : i32
scf.if %v3 {
%v4 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v4) : (!llvm.ptr) -> ()
}
%v5 = arith.remsi %arg0, %v1 : i32
%v6 = arith.constant 0 : i32
%v7 = arith.cmpi eq, %v5, %v6 : i32
func.return %v7 : i1
}
func.func @pick(%arg0: i1, %arg1: i32, %arg2: i32) -> i32 {
%v8 = scf.if %arg0 -> (i32) {
scf.yield %arg1 : i32
} else {
scf.yield %arg2 : i32
}
func.return %v8 : i32
}
func.func @main() -> i32 {
%v9 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v10 = llvm.call @printf(%v9) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v11 = arith.constant 0 : i32
%v12 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v13 = llvm.call @printf(%v12) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v14 = arith.constant 0 : i32
%v15 = llvm.mlir.addressof @str_5 : !llvm.ptr
%v16 = llvm.call @printf(%v15) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v17 = arith.constant 0 : i32
%v18 = llvm.mlir.addressof @str_6 : !llvm.ptr
%v19 = llvm.mlir.addressof @str_7 : !llvm.ptr
%v20 = llvm.call @printf(%v19, %v18) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, !llvm.ptr) -> i32
%v21 = arith.constant 0 : i32
%v22 = llvm.mlir.addressof @str_8 : !llvm.ptr
%v23 = arith.constant 4 : i32
%v24 = arith.constant 3.14159 : f64
%v25 = llvm.call @printf(%v22, %v18, %v23, %v24) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, !llvm.ptr, i32, f64) -> i32
%v26 = llvm.mlir.addressof @str_9 : !llvm.ptr
%v27 = llvm.call @printf(%v26) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v28 = arith.constant 1 : i1
%v29 = arith.extui %v28 : i1 to i32
%v30 = llvm.mlir.addressof @str_10 : !llvm.ptr
%v31 = llvm.call @printf(%v30, %v29) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v32 = arith.constant 0 : i32
%v33 = arith.constant 6 : i32
%v34 = func.call @is_even(%v33) : (i32) -> i1
%v35 = scf.if %v34 -> (i1) {
%v36 = arith.constant 4 : i32
%v37 = arith.cmpi sgt, %v33, %v36 : i32
scf.yield %v37 : i1
} else {
%v38 = arith.constant false
scf.yield %v38 : i1
}
cf.cond_br %v35, ^b1, ^b2
^b1:
%v39 = llvm.mlir.addressof @str_11 : !llvm.ptr
%v40 = llvm.call @printf(%v39) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v41 = arith.constant 0 : i32
cf.br ^b3
^b2:
cf.br ^b3
^b3:
%v42 = func.call @is_even(%v33) : (i32) -> i1
%v43 = arith.constant 1 : i1
%v44 = arith.xori %v42, %v43 : i1
%v45 = scf.if %v44 -> (i1) {
%v46 = arith.constant true
scf.yield %v46 : i1
} else {
%v47 = arith.constant 6 : i32
%v48 = arith.cmpi eq, %v33, %v47 : i32
scf.yield %v48 : i1
}
cf.cond_br %v45, ^b4, ^b5
^b4:
%v49 = llvm.mlir.addressof @str_12 : !llvm.ptr
%v50 = llvm.call @printf(%v49) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v51 = arith.constant 0 : i32
cf.br ^b6
^b5:
cf.br ^b6
^b6:
%v52 = arith.constant 0 : i32
%v53 = arith.cmpi slt, %v33, %v52 : i32
%v54 = arith.constant 1 : i1
%v55 = arith.xori %v53, %v54 : i1
cf.cond_br %v55, ^b7, ^b8
^b7:
%v56 = llvm.mlir.addressof @str_13 : !llvm.ptr
%v57 = llvm.call @printf(%v56) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v58 = arith.constant 0 : i32
cf.br ^b9
^b8:
cf.br ^b9
^b9:
%v59 = arith.constant 3 : i32
%v60 = arith.cmpi sgt, %v33, %v59 : i32
%v61 = arith.constant 10 : i32
%v62 = arith.constant 20 : i32
%v63 = func.call @pick(%v60, %v61, %v62) : (i1, i32, i32) -> i32
%v64 = llvm.mlir.addressof @str_10 : !llvm.ptr
%v65 = llvm.call @printf(%v64, %v63) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v66 = arith.constant 0 : i32
%v67 = arith.constant 7 : i32
%v68 = func.call @is_even(%v67) : (i32) -> i1
%v69 = arith.constant 10 : i32
%v70 = arith.constant 20 : i32
%v71 = func.call @pick(%v68, %v69, %v70) : (i1, i32, i32) -> i32
%v72 = llvm.mlir.addressof @str_10 : !llvm.ptr
%v73 = llvm.call @printf(%v72, %v71) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v74 = arith.constant 0 : i32
%v75 = arith.constant 2 : i32
%v76 = func.call @is_even(%v75) : (i32) -> i1
%v77 = scf.if %v76 -> (i1) {
%v78 = arith.constant 4 : i32
%v79 = func.call @is_even(%v78) : (i32) -> i1
scf.yield %v79 : i1
} else {
%v80 = arith.constant false
scf.yield %v80 : i1
}
%v81 = arith.extui %v77 : i1 to i32
%v82 = llvm.mlir.addressof @str_10 : !llvm.ptr
%v83 = llvm.call @printf(%v82, %v81) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v84 = arith.constant 0 : i32
%v85 = arith.constant 0 : i32
func.return %v85 : i32
}
}
