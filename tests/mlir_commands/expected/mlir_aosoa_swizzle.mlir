module {
func.func private @strlen(!llvm.ptr) -> i64
func.func private @write(i32, !llvm.ptr, i64) -> i64
func.func private @abort() -> ()
llvm.mlir.global internal constant @str_0("flow: \00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
llvm.mlir.global internal constant @str_1("\0A\00") {addr_space = 0 : i32} : !llvm.array<2 x i8>
llvm.mlir.global internal constant @str_2("invalid shift (amount out of range or left-shift of negative)\00") {addr_space = 0 : i32} : !llvm.array<62 x i8>
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
// Struct: Particle_SoA_4
// Fields:
//   x: memref<4xf32>
//   y: memref<4xf32>
// Struct: Particle
// Fields:
//   x: f32
//   y: f32
func.func @update() -> i32 {
%v1 = llvm.mlir.undef : !llvm.struct<(!llvm.array<4 x f32>, !llvm.array<4 x f32>)>
%v2 = arith.constant 0 : i32
%v3 = llvm.mlir.constant(1 : i64) : i64
%v4 = llvm.alloca %v3 x i32 : (i64) -> !llvm.ptr
llvm.store %v2, %v4 : i32, !llvm.ptr
cf.br ^b1
^b1:
%v5 = llvm.load %v4 : !llvm.ptr -> i32
%v6 = arith.constant 4 : i32
%v7 = arith.cmpi slt, %v5, %v6 : i32
cf.cond_br %v7, ^b2, ^b3
^b2:
%v8 = arith.constant 1.0 : f64
%v9 = llvm.extractvalue %v1[0] : !llvm.struct<(!llvm.array<4 x f32>, !llvm.array<4 x f32>)>
%v10 = llvm.load %v4 : !llvm.ptr -> i32
%v11 = llvm.load %v4 : !llvm.ptr -> i32
%v12 = arith.constant 0 : i32
%v13 = arith.constant 32 : i32
%v14 = arith.cmpi uge, %v12, %v13 : i32
scf.if %v14 {
%v15 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v15) : (!llvm.ptr) -> ()
}
%v16 = arith.shrsi %v11, %v12 : i32
%v17 = arith.xori %v10, %v16 : i32
%v18 = arith.index_cast %v17 : i32 to index
%v19 = arith.truncf %v8 : f64 to f32
memref.store %v19, %v9[%v18] : memref<4xf32>
%v20 = arith.constant 2.0 : f64
%v21 = llvm.extractvalue %v1[1] : !llvm.struct<(!llvm.array<4 x f32>, !llvm.array<4 x f32>)>
%v22 = llvm.load %v4 : !llvm.ptr -> i32
%v23 = llvm.load %v4 : !llvm.ptr -> i32
%v24 = arith.constant 0 : i32
%v25 = arith.constant 32 : i32
%v26 = arith.cmpi uge, %v24, %v25 : i32
scf.if %v26 {
%v27 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v27) : (!llvm.ptr) -> ()
}
%v28 = arith.shrsi %v23, %v24 : i32
%v29 = arith.xori %v22, %v28 : i32
%v30 = arith.index_cast %v29 : i32 to index
%v31 = arith.truncf %v20 : f64 to f32
memref.store %v31, %v21[%v30] : memref<4xf32>
%v32 = llvm.load %v4 : !llvm.ptr -> i32
%v33 = arith.constant 1 : i32
%v34 = arith.addi %v32, %v33 : i32
llvm.store %v34, %v4 : i32, !llvm.ptr
cf.br ^b1
^b3:
%v35 = llvm.load %v4 : !llvm.ptr -> i32
func.return %v35 : i32
}
}
