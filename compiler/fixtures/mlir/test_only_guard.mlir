module {
func.func @pick() -> i32 {
%v1 = arith.constant 2 : i32
func.return %v1 : i32
}
func.func @mode_name() -> i32 {
%v2 = arith.constant 20 : i32
func.return %v2 : i32
}
func.func @shape() -> i32 {
%v3 = arith.constant 200 : i32
func.return %v3 : i32
}
func.func @tag() -> i32 {
%v4 = arith.constant 3 : i32
func.return %v4 : i32
}
func.func @main() -> i32 {
%v5 = func.call @pick() : () -> i32
%v6 = arith.constant 2 : i32
%v7 = arith.cmpi ne, %v5, %v6 : i32
cf.cond_br %v7, ^b1, ^b2
^b1:
%v8 = arith.constant 1 : i32
func.return %v8 : i32
^b2:
cf.br ^b3
^b3:
%v9 = func.call @mode_name() : () -> i32
%v10 = arith.constant 20 : i32
%v11 = arith.cmpi ne, %v9, %v10 : i32
cf.cond_br %v11, ^b4, ^b5
^b4:
%v12 = arith.constant 2 : i32
func.return %v12 : i32
^b5:
cf.br ^b6
^b6:
%v13 = func.call @shape() : () -> i32
%v14 = arith.constant 200 : i32
%v15 = arith.cmpi ne, %v13, %v14 : i32
cf.cond_br %v15, ^b7, ^b8
^b7:
%v16 = arith.constant 3 : i32
func.return %v16 : i32
^b8:
cf.br ^b9
^b9:
%v17 = func.call @tag() : () -> i32
%v18 = arith.constant 3 : i32
%v19 = arith.cmpi ne, %v17, %v18 : i32
cf.cond_br %v19, ^b10, ^b11
^b10:
%v20 = arith.constant 4 : i32
func.return %v20 : i32
^b11:
cf.br ^b12
^b12:
%v21 = arith.constant 0 : i32
func.return %v21 : i32
}
}
