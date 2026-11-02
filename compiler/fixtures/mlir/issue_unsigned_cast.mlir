module {
func.func private @puts(!llvm.ptr) -> i32
llvm.mlir.global internal constant @str_0("ok\00") {addr_space = 0 : i32} : !llvm.array<3 x i8>
llvm.mlir.global internal constant @str_1("fail\00") {addr_space = 0 : i32} : !llvm.array<5 x i8>
func.func @main() -> i32 {
%v1 = arith.constant 1 : i32
%v2 = arith.constant 0 : i32
%v3 = arith.subi %v2, %v1 : i32
%v4 = arith.extsi %v3 : i32 to i64
%v5 = arith.ori %v4, %v4 : i64
%v6 = arith.constant 0 : i32
%v7 = arith.extsi %v6 : i32 to i64
%v8 = arith.cmpi slt, %v4, %v7 : i64
cf.cond_br %v8, ^b1, ^b2
^b1:
%v9 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v10 = func.call @puts(%v9) : (!llvm.ptr) -> i32
%v11 = arith.constant 0 : i32
func.return %v11 : i32
^b2:
cf.br ^b3
^b3:
%v12 = llvm.mlir.addressof @str_1 : !llvm.ptr
%v13 = func.call @puts(%v12) : (!llvm.ptr) -> i32
%v14 = arith.constant 1 : i32
func.return %v14 : i32
}
}
