module {
func.func @add(%arg0: i32, %arg1: i32) -> i32 {
%v1 = arith.addi %arg0, %arg1 : i32
func.return %v1 : i32
}
func.func @multiply(%arg0: i32, %arg1: i32) -> i32 {
%v2 = arith.muli %arg0, %arg1 : i32
func.return %v2 : i32
}
func.func @compute() -> i32 {
%v3 = arith.constant 10 : i32
%v4 = arith.constant 20 : i32
%v5 = func.call @add(%v3, %v4) : (i32, i32) -> i32
%v6 = func.call @multiply(%v3, %v4) : (i32, i32) -> i32
%v7 = arith.addi %v5, %v6 : i32
func.return %v7 : i32
}
func.func @main() -> i32 {
%v8 = func.call @compute() : () -> i32
func.return %v8 : i32
}
}
