module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
func.func @main() -> i32 {
%v1 = arith.constant 3 : i32
%v2 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v3 = llvm.call @printf(%v2, %v1) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v4 = arith.constant 0 : i32
%v5 = arith.constant 0 : i32
func.return %v5 : i32
}
}
