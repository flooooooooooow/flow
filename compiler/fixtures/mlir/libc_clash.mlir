module {
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("%f %f %d\0A\00") {addr_space = 0 : i32} : !llvm.array<10 x i8>
func.func @__flowc_libc_abs(%arg0: f32) -> f32 {
%v1 = arith.constant 0.0 : f64
%v2 = arith.extf %arg0 : f32 to f64
%v3 = arith.cmpf olt, %v2, %v1 : f64
cf.cond_br %v3, ^b1, ^b2
^b1:
%v4 = arith.negf %arg0 : f32
func.return %v4 : f32
^b2:
cf.br ^b3
^b3:
func.return %arg0 : f32
}
func.func @random() -> i32 {
%v5 = arith.constant 4 : i32
func.return %v5 : i32
}
func.func @main() -> i32 {
%v6 = arith.constant 0.25 : f64
%v7 = arith.negf %v6 : f64
%v8 = arith.truncf %v7 : f64 to f32
%v9 = func.call @__flowc_libc_abs(%v8) : (f32) -> f32
%v10 = arith.constant 1.5 : f64
%v11 = arith.truncf %v10 : f64 to f32
%v12 = func.call @__flowc_libc_abs(%v11) : (f32) -> f32
%v13 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v14 = arith.extf %v9 : f32 to f64
%v15 = arith.extf %v12 : f32 to f64
%v16 = func.call @random() : () -> i32
%v17 = llvm.call @printf(%v13, %v14, %v15, %v16) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64, f64, i32) -> i32
%v18 = arith.constant 0.25 : f64
%v19 = arith.extf %v9 : f32 to f64
%v20 = arith.cmpf une, %v19, %v18 : f64
%v21 = scf.if %v20 -> (i1) {
%v22 = arith.constant true
scf.yield %v22 : i1
} else {
%v23 = func.call @random() : () -> i32
%v24 = arith.constant 4 : i32
%v25 = arith.cmpi ne, %v23, %v24 : i32
scf.yield %v25 : i1
}
cf.cond_br %v21, ^b4, ^b5
^b4:
%v26 = arith.constant 1 : i32
func.return %v26 : i32
^b5:
cf.br ^b6
^b6:
%v27 = arith.constant 0 : i32
func.return %v27 : i32
}
}
