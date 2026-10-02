module {
// Struct: Particle_SoA_4
// Fields:
//   x: memref<5xf32>
//   y: memref<5xf32>
// Struct: Particle
// Fields:
//   x: f32
//   y: f32
func.func @update() -> i32 {
%v1 = llvm.mlir.undef : !llvm.struct<(!llvm.array<5 x f32>, !llvm.array<5 x f32>)>
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
%v9 = llvm.extractvalue %v1[0] : !llvm.struct<(!llvm.array<5 x f32>, !llvm.array<5 x f32>)>
%v10 = llvm.load %v4 : !llvm.ptr -> i32
%v11 = arith.index_cast %v10 : i32 to index
%v12 = arith.truncf %v8 : f64 to f32
memref.store %v12, %v9[%v11] : memref<5xf32>
%v13 = arith.constant 2.0 : f64
%v14 = llvm.extractvalue %v1[1] : !llvm.struct<(!llvm.array<5 x f32>, !llvm.array<5 x f32>)>
%v15 = llvm.load %v4 : !llvm.ptr -> i32
%v16 = arith.index_cast %v15 : i32 to index
%v17 = arith.truncf %v13 : f64 to f32
memref.store %v17, %v14[%v16] : memref<5xf32>
%v18 = llvm.load %v4 : !llvm.ptr -> i32
%v19 = arith.constant 1 : i32
%v20 = arith.addi %v18, %v19 : i32
llvm.store %v20, %v4 : i32, !llvm.ptr
cf.br ^b1
^b3:
%v21 = llvm.load %v4 : !llvm.ptr -> i32
func.return %v21 : i32
}
}
