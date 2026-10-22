module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("no newline, \00") {addr_space = 0 : i32} : !llvm.array<13 x i8>
llvm.mlir.global internal constant @str_1("with newline\0A\00") {addr_space = 0 : i32} : !llvm.array<14 x i8>
llvm.mlir.global internal constant @str_2("tab\09quote\22 backslash\5C end\0A\00") {addr_space = 0 : i32} : !llvm.array<27 x i8>
llvm.mlir.global internal constant @str_3("flow\00") {addr_space = 0 : i32} : !llvm.array<5 x i8>
llvm.mlir.global internal constant @str_4("%s\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_5("%s has %d letters and pi is %.3f\0A\00") {addr_space = 0 : i32} : !llvm.array<34 x i8>
llvm.mlir.global internal constant @str_6("plain\0A\00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
llvm.mlir.global internal constant @str_7("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_8("even and big\0A\00") {addr_space = 0 : i32} : !llvm.array<14 x i8>
llvm.mlir.global internal constant @str_9("odd or six\0A\00") {addr_space = 0 : i32} : !llvm.array<12 x i8>
llvm.mlir.global internal constant @str_10("non-negative\0A\00") {addr_space = 0 : i32} : !llvm.array<14 x i8>
func.func @is_even(%arg0: i32) -> i1 {
%v1 = arith.constant 2 : i32
%v2 = arith.remsi %arg0, %v1 : i32
%v3 = arith.constant 0 : i32
%v4 = arith.cmpi eq, %v2, %v3 : i32
func.return %v4 : i1
}
func.func @pick(%arg0: i1, %arg1: i32, %arg2: i32) -> i32 {
%v5 = scf.if %arg0 -> (i32) {
scf.yield %arg1 : i32
} else {
scf.yield %arg2 : i32
}
func.return %v5 : i32
}
func.func @main() -> i32 {
%v6 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v7 = llvm.call @printf(%v6) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v8 = arith.constant 0 : i32
%v9 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v10 = llvm.call @printf(%v9) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v11 = arith.constant 0 : i32
%v12 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v13 = llvm.call @printf(%v12) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v14 = arith.constant 0 : i32
%v15 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v16 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v17 = llvm.call @printf(%v16, %v15) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, !llvm.ptr) -> i32
%v18 = arith.constant 0 : i32
%v19 = llvm.mlir.addressof @str_5 : !llvm.ptr
%v20 = arith.constant 4 : i32
%v21 = arith.constant 3.14159 : f64
%v22 = llvm.call @printf(%v19, %v15, %v20, %v21) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, !llvm.ptr, i32, f64) -> i32
%v23 = llvm.mlir.addressof @str_6 : !llvm.ptr
%v24 = llvm.call @printf(%v23) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v25 = arith.constant 1 : i1
%v26 = arith.extui %v25 : i1 to i32
%v27 = llvm.mlir.addressof @str_7 : !llvm.ptr
%v28 = llvm.call @printf(%v27, %v26) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v29 = arith.constant 0 : i32
%v30 = arith.constant 6 : i32
%v31 = func.call @is_even(%v30) : (i32) -> i1
%v32 = scf.if %v31 -> (i1) {
%v33 = arith.constant 4 : i32
%v34 = arith.cmpi sgt, %v30, %v33 : i32
scf.yield %v34 : i1
} else {
%v35 = arith.constant false
scf.yield %v35 : i1
}
cf.cond_br %v32, ^b1, ^b2
^b1:
%v36 = llvm.mlir.addressof @str_8 : !llvm.ptr
%v37 = llvm.call @printf(%v36) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v38 = arith.constant 0 : i32
cf.br ^b3
^b2:
cf.br ^b3
^b3:
%v39 = func.call @is_even(%v30) : (i32) -> i1
%v40 = arith.constant 1 : i1
%v41 = arith.xori %v39, %v40 : i1
%v42 = scf.if %v41 -> (i1) {
%v43 = arith.constant true
scf.yield %v43 : i1
} else {
%v44 = arith.constant 6 : i32
%v45 = arith.cmpi eq, %v30, %v44 : i32
scf.yield %v45 : i1
}
cf.cond_br %v42, ^b4, ^b5
^b4:
%v46 = llvm.mlir.addressof @str_9 : !llvm.ptr
%v47 = llvm.call @printf(%v46) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v48 = arith.constant 0 : i32
cf.br ^b6
^b5:
cf.br ^b6
^b6:
%v49 = arith.constant 0 : i32
%v50 = arith.cmpi slt, %v30, %v49 : i32
%v51 = arith.constant 1 : i1
%v52 = arith.xori %v50, %v51 : i1
cf.cond_br %v52, ^b7, ^b8
^b7:
%v53 = llvm.mlir.addressof @str_10 : !llvm.ptr
%v54 = llvm.call @printf(%v53) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v55 = arith.constant 0 : i32
cf.br ^b9
^b8:
cf.br ^b9
^b9:
%v56 = arith.constant 3 : i32
%v57 = arith.cmpi sgt, %v30, %v56 : i32
%v58 = arith.constant 10 : i32
%v59 = arith.constant 20 : i32
%v60 = func.call @pick(%v57, %v58, %v59) : (i1, i32, i32) -> i32
%v61 = llvm.mlir.addressof @str_7 : !llvm.ptr
%v62 = llvm.call @printf(%v61, %v60) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v63 = arith.constant 0 : i32
%v64 = arith.constant 7 : i32
%v65 = func.call @is_even(%v64) : (i32) -> i1
%v66 = arith.constant 10 : i32
%v67 = arith.constant 20 : i32
%v68 = func.call @pick(%v65, %v66, %v67) : (i1, i32, i32) -> i32
%v69 = llvm.mlir.addressof @str_7 : !llvm.ptr
%v70 = llvm.call @printf(%v69, %v68) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v71 = arith.constant 0 : i32
%v72 = arith.constant 2 : i32
%v73 = func.call @is_even(%v72) : (i32) -> i1
%v74 = scf.if %v73 -> (i1) {
%v75 = arith.constant 4 : i32
%v76 = func.call @is_even(%v75) : (i32) -> i1
scf.yield %v76 : i1
} else {
%v77 = arith.constant false
scf.yield %v77 : i1
}
%v78 = arith.extui %v74 : i1 to i32
%v79 = llvm.mlir.addressof @str_7 : !llvm.ptr
%v80 = llvm.call @printf(%v79, %v78) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v81 = arith.constant 0 : i32
%v82 = arith.constant 0 : i32
func.return %v82 : i32
}
}
