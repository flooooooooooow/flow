module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
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
func.func @main() -> i32 {
%v10 = arith.constant 2 : i32
%v11 = func.call @dep_scale(%v10) : (i32) -> i32
%v12 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v13 = llvm.call @printf(%v12, %v11) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v14 = arith.constant 0 : i32
%v15 = arith.constant 0 : i32
func.return %v15 : i32
}
}
