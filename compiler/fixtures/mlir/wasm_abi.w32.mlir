module attributes {llvm.data_layout = "e-m:e-p:32:32-i64:64-n32:64-S128", llvm.target_triple = "wasm32-unknown-emscripten"} {
llvm.mlir.global internal constant @str_0("hello\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
func.func private @lambda_1(%env: !llvm.ptr, %arg0: i32) -> i32 {
%v1 = llvm.getelementptr %env[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32)>
%v2 = llvm.load %v1 : !llvm.ptr -> i32
%v3 = llvm.load %v1 : !llvm.ptr -> i32
%v4 = arith.addi %arg0, %v3 : i32
func.return %v4 : i32
}
func.func private @malloc(i32) -> !llvm.ptr
func.func private @strlen(!llvm.ptr) -> i32
func.func private @memset(!llvm.ptr, i32, i32) -> !llvm.ptr
// Struct: Point
// Fields:
//   x: i32
//   y: i32
func.func @mid(%arg0: !llvm.struct<(i32, i32)>, %arg1: !llvm.struct<(i32, i32)>) -> !llvm.struct<(i32, i32)> {
%v5 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v6 = llvm.extractvalue %arg0[0] : !llvm.struct<(i32, i32)>
%v7 = llvm.insertvalue %v6, %v5[0] : !llvm.struct<(i32, i32)>
%v8 = llvm.extractvalue %arg0[1] : !llvm.struct<(i32, i32)>
%v9 = llvm.insertvalue %v8, %v7[1] : !llvm.struct<(i32, i32)>
%v10 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v11 = llvm.extractvalue %arg1[0] : !llvm.struct<(i32, i32)>
%v12 = llvm.insertvalue %v11, %v10[0] : !llvm.struct<(i32, i32)>
%v13 = llvm.extractvalue %arg1[1] : !llvm.struct<(i32, i32)>
%v14 = llvm.insertvalue %v13, %v12[1] : !llvm.struct<(i32, i32)>
%v15 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v16 = llvm.extractvalue %v9[0] : !llvm.struct<(i32, i32)>
%v17 = llvm.extractvalue %v14[0] : !llvm.struct<(i32, i32)>
%v18 = arith.addi %v16, %v17 : i32
%v19 = arith.constant 2 : i32
%v20 = arith.divsi %v18, %v19 : i32
%v21 = llvm.insertvalue %v20, %v15[0] : !llvm.struct<(i32, i32)>
%v22 = llvm.extractvalue %v9[1] : !llvm.struct<(i32, i32)>
%v23 = llvm.extractvalue %v14[1] : !llvm.struct<(i32, i32)>
%v24 = arith.addi %v22, %v23 : i32
%v25 = arith.constant 2 : i32
%v26 = arith.divsi %v24, %v25 : i32
%v27 = llvm.insertvalue %v26, %v21[1] : !llvm.struct<(i32, i32)>
%v28 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v29 = llvm.extractvalue %v27[0] : !llvm.struct<(i32, i32)>
%v30 = llvm.insertvalue %v29, %v28[0] : !llvm.struct<(i32, i32)>
%v31 = llvm.extractvalue %v27[1] : !llvm.struct<(i32, i32)>
%v32 = llvm.insertvalue %v31, %v30[1] : !llvm.struct<(i32, i32)>
func.return %v32 : !llvm.struct<(i32, i32)>
}
func.func @apply(%arg0: !llvm.struct<(!llvm.ptr, !llvm.ptr)>, %arg1: i32) -> i32 {
%v33 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v34 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v35 = llvm.insertvalue %v34, %v33[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v36 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v37 = llvm.insertvalue %v36, %v35[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v38 = llvm.extractvalue %v37[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v39 = llvm.extractvalue %v37[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v40 = llvm.call %v38(%v39, %arg1) : !llvm.ptr, (!llvm.ptr, i32) -> i32
func.return %v40 : i32
}
func.func @main() -> i32 {
%v41 = arith.constant 16 : i32
%v42 = func.call @malloc(%v41) : (i32) -> !llvm.ptr
%v43 = arith.constant 0 : i32
%v44 = arith.constant 16 : i32
%v45 = func.call @memset(%v42, %v43, %v44) : (!llvm.ptr, i32, i32) -> !llvm.ptr
%v46 = llvm.mlir.addressof @str_0 : !llvm.ptr
%v47 = func.call @strlen(%v46) : (!llvm.ptr) -> i32
%v48 = arith.extsi %v47 : i32 to i64
%v49 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v50 = arith.constant 4 : i32
%v51 = llvm.insertvalue %v50, %v49[0] : !llvm.struct<(i32, i32)>
%v52 = arith.constant 6 : i32
%v53 = llvm.insertvalue %v52, %v51[1] : !llvm.struct<(i32, i32)>
%v54 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v55 = arith.constant 0 : i32
%v56 = llvm.insertvalue %v55, %v54[0] : !llvm.struct<(i32, i32)>
%v57 = arith.constant 0 : i32
%v58 = llvm.insertvalue %v57, %v56[1] : !llvm.struct<(i32, i32)>
%v59 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v60 = llvm.extractvalue %v58[0] : !llvm.struct<(i32, i32)>
%v61 = llvm.insertvalue %v60, %v59[0] : !llvm.struct<(i32, i32)>
%v62 = llvm.extractvalue %v58[1] : !llvm.struct<(i32, i32)>
%v63 = llvm.insertvalue %v62, %v61[1] : !llvm.struct<(i32, i32)>
%v64 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v65 = llvm.extractvalue %v53[0] : !llvm.struct<(i32, i32)>
%v66 = llvm.insertvalue %v65, %v64[0] : !llvm.struct<(i32, i32)>
%v67 = llvm.extractvalue %v53[1] : !llvm.struct<(i32, i32)>
%v68 = llvm.insertvalue %v67, %v66[1] : !llvm.struct<(i32, i32)>
%v69 = func.call @mid(%v63, %v68) : (!llvm.struct<(i32, i32)>, !llvm.struct<(i32, i32)>) -> !llvm.struct<(i32, i32)>
%v70 = llvm.mlir.undef : !llvm.struct<(i32, i32)>
%v71 = llvm.extractvalue %v69[0] : !llvm.struct<(i32, i32)>
%v72 = llvm.insertvalue %v71, %v70[0] : !llvm.struct<(i32, i32)>
%v73 = llvm.extractvalue %v69[1] : !llvm.struct<(i32, i32)>
%v74 = llvm.insertvalue %v73, %v72[1] : !llvm.struct<(i32, i32)>
%v75 = arith.constant 5 : i32
%v76 = llvm.mlir.zero : !llvm.ptr
%v77 = llvm.getelementptr %v76[1] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32)>
%v78 = llvm.ptrtoint %v77 : !llvm.ptr to i32
%v79 = func.call @malloc(%v78) : (i32) -> !llvm.ptr
%v80 = llvm.getelementptr %v79[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.struct<(i32)>
llvm.store %v75, %v80 : i32, !llvm.ptr
%v81 = func.constant @lambda_1 : (!llvm.ptr, i32) -> i32
%v82 = builtin.unrealized_conversion_cast %v81 : (!llvm.ptr, i32) -> i32 to !llvm.ptr
%v83 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v84 = llvm.insertvalue %v82, %v83[0] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v85 = llvm.insertvalue %v79, %v84[1] : !llvm.struct<(!llvm.ptr, !llvm.ptr)>
%v86 = arith.constant 2 : i32
%v87 = func.call @apply(%v85, %v86) : (!llvm.struct<(!llvm.ptr, !llvm.ptr)>, i32) -> i32
%v88 = arith.trunci %v48 : i64 to i32
%v89 = llvm.extractvalue %v74[0] : !llvm.struct<(i32, i32)>
%v90 = arith.addi %v88, %v89 : i32
%v91 = llvm.extractvalue %v74[1] : !llvm.struct<(i32, i32)>
%v92 = arith.addi %v90, %v91 : i32
%v93 = arith.addi %v92, %v87 : i32
func.return %v93 : i32
}
}
