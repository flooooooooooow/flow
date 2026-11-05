module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("vectors built\0A\00") {addr_space = 0 : i32} : !llvm.array<15 x i8>
func.func @lit_f32() -> vector<4xf32> {
%v1 = arith.constant 1.0 : f64
%v2 = arith.constant 2.0 : f64
%v3 = arith.constant 3.0 : f64
%v4 = arith.constant 4.0 : f64
%v5 = vector.from_elements %v1, %v2, %v3, %v4 : vector<4xf64>
%v6 = arith.truncf %v5 : vector<4xf64> to vector<4xf32>
func.return %v6 : vector<4xf32>
}
func.func @ops_f32() -> vector<4xf32> {
%v7 = arith.constant 1.0 : f64
%v8 = arith.constant 2.0 : f64
%v9 = arith.constant 3.0 : f64
%v10 = arith.constant 4.0 : f64
%v11 = vector.from_elements %v7, %v8, %v9, %v10 : vector<4xf64>
%v12 = arith.truncf %v11 : vector<4xf64> to vector<4xf32>
%v13 = arith.constant 0.5 : f64
%v14 = arith.constant 0.5 : f64
%v15 = arith.constant 0.5 : f64
%v16 = arith.constant 0.5 : f64
%v17 = vector.from_elements %v13, %v14, %v15, %v16 : vector<4xf64>
%v18 = arith.truncf %v17 : vector<4xf64> to vector<4xf32>
%v19 = arith.mulf %v12, %v18 : vector<4xf32>
%v20 = arith.constant 1.0 : f64
%v21 = arith.constant 1.0 : f64
%v22 = arith.constant 1.0 : f64
%v23 = arith.constant 1.0 : f64
%v24 = vector.from_elements %v20, %v21, %v22, %v23 : vector<4xf64>
%v25 = arith.truncf %v24 : vector<4xf64> to vector<4xf32>
%v26 = arith.addf %v25, %v19 : vector<4xf32>
%v27 = arith.subf %v26, %v12 : vector<4xf32>
func.return %v27 : vector<4xf32>
}
func.func @ops_i64() -> vector<2xi64> {
%v28 = arith.constant 1 : i32
%v29 = arith.constant 2 : i32
%v30 = vector.from_elements %v28, %v29 : vector<2xi32>
%v31 = arith.extsi %v30 : vector<2xi32> to vector<2xi64>
%v32 = arith.constant 10 : i32
%v33 = arith.constant 20 : i32
%v34 = vector.from_elements %v32, %v33 : vector<2xi32>
%v35 = arith.extsi %v34 : vector<2xi32> to vector<2xi64>
%v36 = arith.addi %v31, %v35 : vector<2xi64>
func.return %v36 : vector<2xi64>
}
func.func @main() -> i32 {
%v37 = func.call @lit_f32() : () -> vector<4xf32>
%v38 = func.call @ops_f32() : () -> vector<4xf32>
%v39 = func.call @ops_i64() : () -> vector<2xi64>
%v40 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v41 = llvm.call @printf(%v40) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32
%v42 = arith.constant 0 : i32
func.return %v42 : i32
}
}
