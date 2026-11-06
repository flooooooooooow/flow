module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("/nonexistent/flow-extern-type\00") {addr_space = 0 : i32} : !llvm.array<30 x i8>
llvm.mlir.global internal constant @str_1("r\00") {addr_space = 0 : i32} : !llvm.array<2 x i8>
llvm.mlir.global internal constant @str_2("missing open %d\0A\00") {addr_space = 0 : i32} : !llvm.array<17 x i8>
llvm.mlir.global internal constant @str_3("no dir\0A\00") {addr_space = 0 : i32} : !llvm.array<8 x i8>
llvm.mlir.global internal constant @str_4("/\00") {addr_space = 0 : i32} : !llvm.array<2 x i8>
llvm.mlir.global internal constant @str_5("root dir %d\0A\00") {addr_space = 0 : i32} : !llvm.array<13 x i8>
func.func private @fopen(!llvm.ptr, !llvm.ptr) -> !llvm.ptr
func.func private @fclose(!llvm.ptr) -> i32
func.func private @opendir(!llvm.ptr) -> !llvm.ptr
func.func private @closedir(!llvm.ptr) -> i32
func.func @is_open(%arg0: !llvm.ptr) -> i32 {
%v1 = llvm.mlir.zero : !llvm.ptr
%v2 = llvm.icmp "eq" %arg0, %v1 : !llvm.ptr
cf.cond_br %v2, ^b1, ^b2
^b1:
%v3 = arith.constant 0 : i32
func.return %v3 : i32
^b2:
cf.br ^b3
^b3:
%v4 = arith.constant 1 : i32
func.return %v4 : i32
}
func.func @main() -> i32 {
%v5 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v6 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v7 = func.call @fopen(%v5, %v6) : (!llvm.ptr, !llvm.ptr) -> !llvm.ptr
%v8 = llvm.mlir.addressof @str_2 : !llvm.ptr
%v9 = func.call @is_open(%v7) : (!llvm.ptr) -> i32
%v10 = llvm.call @printf(%v8, %v9) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v11 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v12 = func.call @opendir(%v11) : (!llvm.ptr) -> !llvm.ptr
%v13 = llvm.mlir.zero : !llvm.ptr
%v14 = llvm.icmp "eq" %v12, %v13 : !llvm.ptr
cf.cond_br %v14, ^b4, ^b5
^b4:
%v15 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v16 = llvm.call @printf(%v15) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
cf.br ^b6
^b5:
cf.br ^b6
^b6:
%v17 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v18 = func.call @opendir(%v17) : (!llvm.ptr) -> !llvm.ptr
%v19 = llvm.mlir.zero : !llvm.ptr
%v20 = llvm.icmp "ne" %v18, %v19 : !llvm.ptr
cf.cond_br %v20, ^b7, ^b8
^b7:
%v21 = llvm.mlir.addressof @str_5 : !llvm.ptr
%v22 = func.call @closedir(%v18) : (!llvm.ptr) -> i32
%v23 = llvm.call @printf(%v21, %v22) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
cf.br ^b9
^b8:
cf.br ^b9
^b9:
%v24 = arith.constant 0 : i32
func.return %v24 : i32
}
}
