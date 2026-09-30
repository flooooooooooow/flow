module {
func.func private @strlen(!llvm.ptr) -> i64
func.func private @write(i32, !llvm.ptr, i64) -> i64
func.func private @abort() -> ()
func.func private @malloc(i64) -> !llvm.ptr
llvm.func @printf(!llvm.ptr, ...) -> i32
llvm.mlir.global internal constant @str_0("flow: \00") {addr_space = 0 : i32} : !llvm.array<7 x i8>
llvm.mlir.global internal constant @str_1("\0A\00") {addr_space = 0 : i32} : !llvm.array<2 x i8>
llvm.mlir.global internal constant @str_2("span index out of bounds\00") {addr_space = 0 : i32} : !llvm.array<25 x i8>
llvm.mlir.global internal constant @str_3("%f\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
llvm.mlir.global internal constant @str_4("%lld\0A\00") {addr_space = 0 : i32} : !llvm.array<6 x i8>
llvm.mlir.global internal constant @str_5("array index out of bounds\00") {addr_space = 0 : i32} : !llvm.array<26 x i8>
llvm.mlir.global internal constant @str_6("%d\0A\00") {addr_space = 0 : i32} : !llvm.array<4 x i8>
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
// Constant: K
llvm.mlir.global internal constant @K(3 : i32) : i32
// Constant: MASK
llvm.mlir.global internal constant @MASK(16 : i32) : i32
// Constant: NEG
llvm.mlir.global internal constant @NEG(-5 : i64) : i64
// Constant: ZERO_F
// Module static: counter
llvm.mlir.global internal @counter(42 : i32) : i32
func.func @total(%arg0: !llvm.struct<(!llvm.ptr, i64)>) -> f64 {
%v1 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v2 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i64)>
%v3 = llvm.insertvalue %v2, %v1[0] : !llvm.struct<(!llvm.ptr, i64)>
%v4 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i64)>
%v5 = llvm.insertvalue %v4, %v3[1] : !llvm.struct<(!llvm.ptr, i64)>
%v6 = llvm.mlir.constant(1 : i64) : i64
%v7 = llvm.alloca %v6 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v5, %v7 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v8 = arith.constant 0.0 : f64
%v9 = llvm.mlir.constant(1 : i64) : i64
%v10 = llvm.alloca %v9 x f64 : (i64) -> !llvm.ptr
llvm.store %v8, %v10 : f64, !llvm.ptr
%v11 = arith.constant 0 : i32
%v12 = llvm.mlir.constant(1 : i64) : i64
%v13 = llvm.alloca %v12 x i32 : (i64) -> !llvm.ptr
llvm.store %v11, %v13 : i32, !llvm.ptr
cf.br ^b1
^b1:
%v14 = llvm.load %v13 : !llvm.ptr -> i32
%v15 = llvm.load %v7 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v16 = llvm.extractvalue %v15[1] : !llvm.struct<(!llvm.ptr, i64)>
%v17 = arith.extsi %v14 : i32 to i64
%v18 = arith.cmpi slt, %v17, %v16 : i64
cf.cond_br %v18, ^b2, ^b3
^b2:
%v19 = llvm.load %v10 : !llvm.ptr -> f64
%v20 = llvm.load %v7 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v21 = llvm.load %v13 : !llvm.ptr -> i32
%v22 = llvm.extractvalue %v20[1] : !llvm.struct<(!llvm.ptr, i64)>
%v23 = arith.extsi %v21 : i32 to i64
%v24 = arith.cmpi sge, %v23, %v22 : i64
scf.if %v24 {
%v25 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v25) : (!llvm.ptr) -> ()
}
%v26 = llvm.extractvalue %v20[0] : !llvm.struct<(!llvm.ptr, i64)>
%v27 = arith.extsi %v21 : i32 to i64
%v28 = llvm.getelementptr %v26[%v27] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v29 = llvm.load %v28 : !llvm.ptr -> f64
%v30 = arith.addf %v19, %v29 : f64
llvm.store %v30, %v10 : f64, !llvm.ptr
%v31 = llvm.load %v13 : !llvm.ptr -> i32
%v32 = arith.constant 1 : i32
%v33 = arith.addi %v31, %v32 : i32
llvm.store %v33, %v13 : i32, !llvm.ptr
cf.br ^b1
^b3:
%v34 = llvm.load %v10 : !llvm.ptr -> f64
func.return %v34 : f64
}
func.func @fill(%arg0: !llvm.struct<(!llvm.ptr, i64)>, %arg1: f64) -> () {
%v35 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v36 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i64)>
%v37 = llvm.insertvalue %v36, %v35[0] : !llvm.struct<(!llvm.ptr, i64)>
%v38 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i64)>
%v39 = llvm.insertvalue %v38, %v37[1] : !llvm.struct<(!llvm.ptr, i64)>
%v40 = llvm.mlir.constant(1 : i64) : i64
%v41 = llvm.alloca %v40 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v39, %v41 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v42 = arith.constant 0 : i32
%v43 = arith.extsi %v42 : i32 to i64
%v44 = llvm.mlir.constant(1 : i64) : i64
%v45 = llvm.alloca %v44 x i64 : (i64) -> !llvm.ptr
llvm.store %v43, %v45 : i64, !llvm.ptr
cf.br ^b4
^b4:
%v46 = llvm.load %v45 : !llvm.ptr -> i64
%v47 = llvm.load %v41 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v48 = llvm.extractvalue %v47[1] : !llvm.struct<(!llvm.ptr, i64)>
%v49 = arith.cmpi slt, %v46, %v48 : i64
cf.cond_br %v49, ^b5, ^b6
^b5:
%v50 = llvm.load %v41 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v51 = llvm.load %v45 : !llvm.ptr -> i64
%v52 = llvm.extractvalue %v50[0] : !llvm.struct<(!llvm.ptr, i64)>
%v53 = llvm.getelementptr %v52[%v51] : (!llvm.ptr, i64) -> !llvm.ptr, f64
llvm.store %arg1, %v53 : f64, !llvm.ptr
%v54 = llvm.load %v45 : !llvm.ptr -> i64
%v55 = arith.constant 1 : i32
%v56 = arith.extsi %v55 : i32 to i64
%v57 = arith.addi %v54, %v56 : i64
llvm.store %v57, %v45 : i64, !llvm.ptr
cf.br ^b4
^b6:
func.return
}
func.func @make(%arg0: i32) -> !llvm.struct<(!llvm.ptr, i64)> {
%v58 = arith.extsi %arg0 : i32 to i64
%v59 = arith.constant 8 : i32
%v60 = arith.extsi %v59 : i32 to i64
%v61 = arith.muli %v58, %v60 : i64
%v62 = func.call @malloc(%v61) : (i64) -> !llvm.ptr
%v63 = arith.constant 0 : i32
%v64 = arith.extsi %v63 : i32 to i64
%v65 = arith.extsi %arg0 : i32 to i64
%v66 = llvm.getelementptr %v62[%v64] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v67 = arith.subi %v65, %v64 : i64
%v68 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v69 = llvm.insertvalue %v66, %v68[0] : !llvm.struct<(!llvm.ptr, i64)>
%v70 = llvm.insertvalue %v67, %v69[1] : !llvm.struct<(!llvm.ptr, i64)>
%v71 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v72 = llvm.extractvalue %v70[0] : !llvm.struct<(!llvm.ptr, i64)>
%v73 = llvm.insertvalue %v72, %v71[0] : !llvm.struct<(!llvm.ptr, i64)>
%v74 = llvm.extractvalue %v70[1] : !llvm.struct<(!llvm.ptr, i64)>
%v75 = llvm.insertvalue %v74, %v73[1] : !llvm.struct<(!llvm.ptr, i64)>
%v76 = llvm.mlir.constant(1 : i64) : i64
%v77 = llvm.alloca %v76 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v75, %v77 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v78 = llvm.load %v77 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
func.return %v78 : !llvm.struct<(!llvm.ptr, i64)>
}
func.func @first4(%arg0: !llvm.struct<(!llvm.ptr, i64)>) -> i32 {
%v79 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v80 = llvm.extractvalue %arg0[0] : !llvm.struct<(!llvm.ptr, i64)>
%v81 = llvm.insertvalue %v80, %v79[0] : !llvm.struct<(!llvm.ptr, i64)>
%v82 = llvm.extractvalue %arg0[1] : !llvm.struct<(!llvm.ptr, i64)>
%v83 = llvm.insertvalue %v82, %v81[1] : !llvm.struct<(!llvm.ptr, i64)>
%v84 = llvm.mlir.constant(1 : i64) : i64
%v85 = llvm.alloca %v84 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v83, %v85 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v86 = llvm.load %v85 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v87 = arith.constant 0 : i32
%v88 = llvm.extractvalue %v86[1] : !llvm.struct<(!llvm.ptr, i64)>
%v89 = arith.extsi %v87 : i32 to i64
%v90 = arith.cmpi sge, %v89, %v88 : i64
scf.if %v90 {
%v91 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v91) : (!llvm.ptr) -> ()
}
%v92 = llvm.extractvalue %v86[0] : !llvm.struct<(!llvm.ptr, i64)>
%v93 = arith.extsi %v87 : i32 to i64
%v94 = llvm.getelementptr %v92[%v93] : (!llvm.ptr, i64) -> !llvm.ptr, i32
%v95 = llvm.load %v94 : !llvm.ptr -> i32
%v96 = llvm.load %v85 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v97 = arith.constant 3 : i32
%v98 = llvm.extractvalue %v96[1] : !llvm.struct<(!llvm.ptr, i64)>
%v99 = arith.extsi %v97 : i32 to i64
%v100 = arith.cmpi sge, %v99, %v98 : i64
scf.if %v100 {
%v101 = llvm.mlir.addressof @str_2 : !llvm.ptr
func.call @__flow_fault(%v101) : (!llvm.ptr) -> ()
}
%v102 = llvm.extractvalue %v96[0] : !llvm.struct<(!llvm.ptr, i64)>
%v103 = arith.extsi %v97 : i32 to i64
%v104 = llvm.getelementptr %v102[%v103] : (!llvm.ptr, i64) -> !llvm.ptr, i32
%v105 = llvm.load %v104 : !llvm.ptr -> i32
%v106 = arith.addi %v95, %v105 : i32
func.return %v106 : i32
}
func.func @scale(%arg0: memref<?xf32>, %arg1: memref<?xf32>, %arg2: i32, %arg3: f32) -> () {
// flow: vectorized elementwise f32 loop (VF=4)
%v107 = arith.constant 0 : i32
%v108 = arith.index_cast %v107 : i32 to index
%v109 = arith.index_cast %arg2 : i32 to index
%v110 = arith.constant 1 : index
%v111 = arith.constant 4 : index
%v112 = arith.subi %v109, %v108 : index
%v113 = arith.remsi %v112, %v111 : index
%v114 = arith.subi %v112, %v113 : index
%v115 = arith.addi %v108, %v114 : index
scf.for %v116 = %v108 to %v115 step %v111 {
%v117 = arith.constant 0.0 : f32
%v118 = vector.transfer_read %arg1[%v116], %v117 {in_bounds = [true]} : memref<?xf32>, vector<4xf32>
%v119 = arith.negf %v118 : vector<4xf32>
%v120 = vector.broadcast %arg3 : f32 to vector<4xf32>
%v121 = arith.mulf %v119, %v120 : vector<4xf32>
%v122 = arith.constant 2.0 : f32
%v123 = vector.broadcast %v122 : f32 to vector<4xf32>
%v124 = arith.addf %v121, %v123 : vector<4xf32>
%v125 = arith.constant 0.0 : f32
%v126 = vector.transfer_read %arg0[%v116], %v125 {in_bounds = [true]} : memref<?xf32>, vector<4xf32>
%v127 = arith.constant 4.0 : f32
%v128 = vector.broadcast %v127 : f32 to vector<4xf32>
%v129 = arith.divf %v126, %v128 : vector<4xf32>
%v130 = arith.subf %v124, %v129 : vector<4xf32>
vector.transfer_write %v130, %arg0[%v116] {in_bounds = [true]} : vector<4xf32>, memref<?xf32>
}
scf.for %v131 = %v115 to %v109 step %v110 {
%v132 = memref.load %arg1[%v131] : memref<?xf32>
%v133 = arith.negf %v132 : f32
%v134 = arith.mulf %v133, %arg3 : f32
%v135 = arith.constant 2.0 : f64
%v136 = arith.extf %v134 : f32 to f64
%v137 = arith.addf %v136, %v135 : f64
%v138 = memref.load %arg0[%v131] : memref<?xf32>
%v139 = arith.constant 4.0 : f64
%v140 = arith.extf %v138 : f32 to f64
%v141 = arith.divf %v140, %v139 : f64
%v142 = arith.subf %v137, %v141 : f64
%v143 = arith.truncf %v142 : f64 to f32
memref.store %v143, %arg0[%v131] : memref<?xf32>
}
func.return
}
func.func @dot(%arg0: memref<?xf32>, %arg1: memref<?xf32>, %arg2: i32) -> f32 {
%v144 = arith.constant 0.0 : f64
%v145 = arith.truncf %v144 : f64 to f32
%v146 = llvm.mlir.constant(1 : i64) : i64
%v147 = llvm.alloca %v146 x f32 : (i64) -> !llvm.ptr
llvm.store %v145, %v147 : f32, !llvm.ptr
%v148 = arith.constant 0 : i32
%v149 = arith.index_cast %v148 : i32 to index
%v150 = arith.index_cast %arg2 : i32 to index
%v151 = arith.constant 1 : index
%v152 = arith.constant -1 : index
%v153 = arith.cmpi sle, %v149, %v150 : index
%v154 = arith.select %v153, %v151, %v152 : index
cf.br ^b7(%v149 : index)
^b7(%v155: index):
%v156 = arith.cmpi slt, %v155, %v150 : index
%v157 = arith.cmpi sgt, %v155, %v150 : index
%v158 = arith.select %v153, %v156, %v157 : i1
cf.cond_br %v158, ^b8(%v155 : index), ^b9(%v155 : index)
^b8(%v159: index):
%v160 = llvm.load %v147 : !llvm.ptr -> f32
%v161 = memref.load %arg0[%v159] : memref<?xf32>
%v162 = memref.load %arg1[%v159] : memref<?xf32>
%v163 = llvm.intr.fma(%v161, %v162, %v160) : (f32, f32, f32) -> f32
llvm.store %v163, %v147 : f32, !llvm.ptr
%v164 = arith.addi %v159, %v154 : index
cf.br ^b7(%v164 : index)
^b9(%v165: index):
%v166 = llvm.load %v147 : !llvm.ptr -> f32
func.return %v166 : f32
}
func.func @main() -> i32 {
%v167 = arith.constant 4 : i32
%v168 = func.call @make(%v167) : (i32) -> !llvm.struct<(!llvm.ptr, i64)>
%v169 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v170 = llvm.extractvalue %v168[0] : !llvm.struct<(!llvm.ptr, i64)>
%v171 = llvm.insertvalue %v170, %v169[0] : !llvm.struct<(!llvm.ptr, i64)>
%v172 = llvm.extractvalue %v168[1] : !llvm.struct<(!llvm.ptr, i64)>
%v173 = llvm.insertvalue %v172, %v171[1] : !llvm.struct<(!llvm.ptr, i64)>
%v174 = llvm.mlir.constant(1 : i64) : i64
%v175 = llvm.alloca %v174 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v173, %v175 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v176 = llvm.load %v175 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v177 = llvm.mlir.constant(1 : i64) : i64
%v178 = llvm.alloca %v177 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v176, %v178 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v179 = llvm.load %v178 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v180 = arith.constant 2.5 : f64
func.call @fill(%v179, %v180) : (!llvm.struct<(!llvm.ptr, i64)>, f64) -> ()
%v181 = llvm.load %v178 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v182 = llvm.extractvalue %v181[0] : !llvm.struct<(!llvm.ptr, i64)>
%v183 = arith.constant 1 : i32
%v184 = arith.constant 3 : i32
%v185 = arith.extsi %v183 : i32 to i64
%v186 = arith.extsi %v184 : i32 to i64
%v187 = llvm.getelementptr %v182[%v185] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v188 = arith.subi %v186, %v185 : i64
%v189 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v190 = llvm.insertvalue %v187, %v189[0] : !llvm.struct<(!llvm.ptr, i64)>
%v191 = llvm.insertvalue %v188, %v190[1] : !llvm.struct<(!llvm.ptr, i64)>
%v192 = llvm.mlir.constant(1 : i64) : i64
%v193 = llvm.alloca %v192 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v191, %v193 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v194 = arith.constant 2 : i32
%v195 = func.call @make(%v194) : (i32) -> !llvm.struct<(!llvm.ptr, i64)>
%v196 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v197 = llvm.extractvalue %v195[0] : !llvm.struct<(!llvm.ptr, i64)>
%v198 = llvm.insertvalue %v197, %v196[0] : !llvm.struct<(!llvm.ptr, i64)>
%v199 = llvm.extractvalue %v195[1] : !llvm.struct<(!llvm.ptr, i64)>
%v200 = llvm.insertvalue %v199, %v198[1] : !llvm.struct<(!llvm.ptr, i64)>
%v201 = llvm.mlir.constant(1 : i64) : i64
%v202 = llvm.alloca %v201 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v200, %v202 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v203 = llvm.load %v202 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v204 = llvm.mlir.constant(1 : i64) : i64
%v205 = llvm.alloca %v204 x !llvm.struct<(!llvm.ptr, i64)> : (i64) -> !llvm.ptr
llvm.store %v203, %v205 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v206 = llvm.load %v178 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
llvm.store %v206, %v205 : !llvm.struct<(!llvm.ptr, i64)>, !llvm.ptr
%v207 = llvm.load %v193 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v208 = func.call @total(%v207) : (!llvm.struct<(!llvm.ptr, i64)>) -> f64
%v209 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v210 = llvm.call @printf(%v209, %v208) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v211 = arith.constant 0 : i32
%v212 = llvm.load %v205 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v213 = llvm.extractvalue %v212[1] : !llvm.struct<(!llvm.ptr, i64)>
%v214 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v215 = llvm.call @printf(%v214, %v213) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v216 = arith.constant 0 : i32
%v217 = llvm.load %v178 : !llvm.ptr -> !llvm.struct<(!llvm.ptr, i64)>
%v218 = llvm.extractvalue %v217[0] : !llvm.struct<(!llvm.ptr, i64)>
%v219 = arith.constant 0 : i32
%v220 = arith.constant 2 : i32
%v221 = arith.extsi %v219 : i32 to i64
%v222 = arith.extsi %v220 : i32 to i64
%v223 = llvm.getelementptr %v218[%v221] : (!llvm.ptr, i64) -> !llvm.ptr, f64
%v224 = arith.subi %v222, %v221 : i64
%v225 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v226 = llvm.insertvalue %v223, %v225[0] : !llvm.struct<(!llvm.ptr, i64)>
%v227 = llvm.insertvalue %v224, %v226[1] : !llvm.struct<(!llvm.ptr, i64)>
%v228 = func.call @total(%v227) : (!llvm.struct<(!llvm.ptr, i64)>) -> f64
%v229 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v230 = llvm.call @printf(%v229, %v228) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v231 = arith.constant 0 : i32
%v232 = arith.constant 7 : i32
%v233 = arith.constant 0 : index
%v234 = arith.constant 4 : index
%v235 = arith.constant 1 : index
%v236 = llvm.mlir.constant(1 : i64) : i64
%v237 = llvm.alloca %v236 x !llvm.array<4 x i32> : (i64) -> !llvm.ptr
scf.for %v238 = %v233 to %v234 step %v235 {
%v239 = arith.index_cast %v238 : index to i64
%v240 = llvm.getelementptr %v237[0, %v239] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x i32>
llvm.store %v232, %v240 : i32, !llvm.ptr
}
%v241 = arith.constant 2 : i32
%v242 = arith.constant 4 : i32
%v243 = arith.cmpi uge, %v241, %v242 : i32
scf.if %v243 {
%v244 = llvm.mlir.addressof @str_5 : !llvm.ptr
func.call @__flow_fault(%v244) : (!llvm.ptr) -> ()
}
%v245 = arith.extsi %v241 : i32 to i64
%v246 = llvm.getelementptr %v237[0, %v245] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<4 x i32>
%v247 = llvm.load %v246 : !llvm.ptr -> i32
%v248 = arith.constant 7 : i32
%v249 = arith.constant 0 : index
%v250 = arith.constant 4 : index
%v251 = arith.constant 1 : index
%v252 = memref.alloca() : memref<4xi32>
scf.for %v253 = %v249 to %v250 step %v251 {
memref.store %v248, %v252[%v253] : memref<4xi32>
}
%v254 = memref.extract_aligned_pointer_as_index %v252 : memref<4xi32> -> index
%v255 = arith.index_cast %v254 : index to i64
%v256 = llvm.inttoptr %v255 : i64 to !llvm.ptr
%v257 = arith.constant 0 : index
%v258 = memref.dim %v252, %v257 : memref<4xi32>
%v259 = arith.index_cast %v258 : index to i64
%v260 = llvm.mlir.undef : !llvm.struct<(!llvm.ptr, i64)>
%v261 = llvm.insertvalue %v256, %v260[0] : !llvm.struct<(!llvm.ptr, i64)>
%v262 = llvm.insertvalue %v259, %v261[1] : !llvm.struct<(!llvm.ptr, i64)>
%v263 = func.call @first4(%v262) : (!llvm.struct<(!llvm.ptr, i64)>) -> i32
%v264 = arith.addi %v247, %v263 : i32
%v265 = llvm.mlir.addressof @str_6 : !llvm.ptr
%v266 = llvm.call @printf(%v265, %v264) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v267 = arith.constant 0 : i32
%v268 = arith.constant 8 : i32
%v269 = arith.index_cast %v268 : i32 to index
%v270 = memref.alloc(%v269) : memref<?xf32>
%v271 = arith.constant 0.0 : f32
%v272 = arith.constant 0 : index
%v273 = arith.constant 1 : index
scf.for %v274 = %v272 to %v269 step %v273 {
memref.store %v271, %v270[%v274] : memref<?xf32>
}
%v275 = arith.constant 8 : i32
%v276 = arith.index_cast %v275 : i32 to index
%v277 = memref.alloc(%v276) : memref<?xf32>
%v278 = arith.constant 0.0 : f32
%v279 = arith.constant 0 : index
%v280 = arith.constant 1 : index
scf.for %v281 = %v279 to %v276 step %v280 {
memref.store %v278, %v277[%v281] : memref<?xf32>
}
%v282 = arith.constant 0 : i32
%v283 = arith.constant 8 : i32
%v284 = arith.index_cast %v282 : i32 to index
%v285 = arith.index_cast %v283 : i32 to index
%v286 = arith.constant 1 : index
%v287 = arith.constant -1 : index
%v288 = arith.cmpi sle, %v284, %v285 : index
%v289 = arith.select %v288, %v286, %v287 : index
cf.br ^b10(%v284 : index)
^b10(%v290: index):
%v291 = arith.cmpi slt, %v290, %v285 : index
%v292 = arith.cmpi sgt, %v290, %v285 : index
%v293 = arith.select %v288, %v291, %v292 : i1
cf.cond_br %v293, ^b11(%v290 : index), ^b12(%v290 : index)
^b11(%v294: index):
%v295 = arith.constant 1.5 : f64
%v296 = arith.truncf %v295 : f64 to f32
memref.store %v296, %v277[%v294] : memref<?xf32>
%v297 = arith.constant 2.0 : f64
%v298 = arith.truncf %v297 : f64 to f32
memref.store %v298, %v270[%v294] : memref<?xf32>
%v299 = arith.addi %v294, %v289 : index
cf.br ^b10(%v299 : index)
^b12(%v300: index):
%v301 = arith.constant 8 : i32
%v302 = arith.constant 0.5 : f64
%v303 = arith.truncf %v302 : f64 to f32
func.call @scale(%v270, %v277, %v301, %v303) : (memref<?xf32>, memref<?xf32>, i32, f32) -> ()
%v304 = arith.constant 3 : i32
%v305 = arith.index_cast %v304 : i32 to index
%v306 = memref.load %v270[%v305] : memref<?xf32>
%v307 = arith.extf %v306 : f32 to f64
%v308 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v309 = llvm.call @printf(%v308, %v307) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v310 = arith.constant 0 : i32
%v311 = arith.constant 1.0 : f64
%v312 = arith.constant 2.0 : f64
%v313 = arith.constant 3.0 : f64
%v314 = arith.truncf %v311 : f64 to f32
%v315 = arith.truncf %v312 : f64 to f32
%v316 = arith.truncf %v313 : f64 to f32
%v317 = memref.alloca() : memref<3xf32>
%v318 = arith.constant 0 : index
memref.store %v314, %v317[%v318] : memref<3xf32>
%v319 = arith.constant 1 : index
memref.store %v315, %v317[%v319] : memref<3xf32>
%v320 = arith.constant 2 : index
memref.store %v316, %v317[%v320] : memref<3xf32>
%v321 = arith.constant 4.0 : f64
%v322 = arith.constant 5.0 : f64
%v323 = arith.constant 6.0 : f64
%v324 = arith.truncf %v321 : f64 to f32
%v325 = arith.truncf %v322 : f64 to f32
%v326 = arith.truncf %v323 : f64 to f32
%v327 = memref.alloca() : memref<3xf32>
%v328 = arith.constant 0 : index
memref.store %v324, %v327[%v328] : memref<3xf32>
%v329 = arith.constant 1 : index
memref.store %v325, %v327[%v329] : memref<3xf32>
%v330 = arith.constant 2 : index
memref.store %v326, %v327[%v330] : memref<3xf32>
%v331 = arith.constant 3 : i32
%v332 = memref.cast %v317 : memref<3xf32> to memref<?xf32>
%v333 = memref.cast %v327 : memref<3xf32> to memref<?xf32>
%v334 = func.call @dot(%v332, %v333, %v331) : (memref<?xf32>, memref<?xf32>, i32) -> f32
%v335 = arith.extf %v334 : f32 to f64
%v336 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v337 = llvm.call @printf(%v336, %v335) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v338 = arith.constant 0 : i32
%v339 = arith.constant 1 : i32
%v340 = arith.constant 2 : i32
%v341 = arith.constant 3 : i32
%v342 = llvm.mlir.constant(1 : i64) : i64
%v343 = llvm.alloca %v342 x !llvm.array<3 x i32> : (i64) -> !llvm.ptr
%v344 = llvm.mlir.zero : !llvm.array<3 x i32>
llvm.store %v344, %v343 : !llvm.array<3 x i32>, !llvm.ptr
%v345 = llvm.mlir.constant(0 : i64) : i64
%v346 = llvm.getelementptr %v343[0, %v345] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v339, %v346 : i32, !llvm.ptr
%v347 = llvm.mlir.constant(1 : i64) : i64
%v348 = llvm.getelementptr %v343[0, %v347] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v340, %v348 : i32, !llvm.ptr
%v349 = llvm.mlir.constant(2 : i64) : i64
%v350 = llvm.getelementptr %v343[0, %v349] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
llvm.store %v341, %v350 : i32, !llvm.ptr
%v351 = arith.constant 0 : i32
%v352 = llvm.mlir.constant(1 : i64) : i64
%v353 = llvm.alloca %v352 x i32 : (i64) -> !llvm.ptr
llvm.store %v351, %v353 : i32, !llvm.ptr
%v354 = arith.constant 0 : i32
%v355 = arith.constant 3 : i32
%v356 = arith.cmpi uge, %v354, %v355 : i32
scf.if %v356 {
%v357 = llvm.mlir.addressof @str_5 : !llvm.ptr
func.call @__flow_fault(%v357) : (!llvm.ptr) -> ()
}
%v358 = arith.extsi %v354 : i32 to i64
%v359 = llvm.getelementptr %v343[0, %v358] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
%v360 = llvm.load %v359 : !llvm.ptr -> i32
%v361 = arith.constant 1 : i32
%v362 = arith.cmpi eq, %v360, %v361 : i32
%v363 = arith.constant 1 : i32
%v364 = arith.constant 3 : i32
%v365 = arith.cmpi uge, %v363, %v364 : i32
scf.if %v365 {
%v366 = llvm.mlir.addressof @str_5 : !llvm.ptr
func.call @__flow_fault(%v366) : (!llvm.ptr) -> ()
}
%v367 = arith.extsi %v363 : i32 to i64
%v368 = llvm.getelementptr %v343[0, %v367] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
%v369 = llvm.load %v368 : !llvm.ptr -> i32
%v370 = arith.constant 2 : i32
%v371 = arith.constant 3 : i32
%v372 = arith.cmpi uge, %v370, %v371 : i32
scf.if %v372 {
%v373 = llvm.mlir.addressof @str_5 : !llvm.ptr
func.call @__flow_fault(%v373) : (!llvm.ptr) -> ()
}
%v374 = arith.extsi %v370 : i32 to i64
%v375 = llvm.getelementptr %v343[0, %v374] : (!llvm.ptr, i64) -> !llvm.ptr, !llvm.array<3 x i32>
%v376 = llvm.load %v375 : !llvm.ptr -> i32
cf.cond_br %v362, ^b13, ^b14
^b13:
%v377 = arith.addi %v369, %v376 : i32
llvm.store %v377, %v353 : i32, !llvm.ptr
cf.br ^b15
^b14:
%v378 = arith.constant 99 : i32
llvm.store %v378, %v353 : i32, !llvm.ptr
cf.br ^b15
^b15:
%v379 = llvm.load %v353 : !llvm.ptr -> i32
%v380 = llvm.mlir.addressof @str_6 : !llvm.ptr
%v381 = llvm.call @printf(%v380, %v379) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v382 = arith.constant 0 : i32
%v383 = llvm.mlir.addressof @K : !llvm.ptr
%v384 = llvm.load %v383 : !llvm.ptr -> i32
%v385 = llvm.mlir.addressof @MASK : !llvm.ptr
%v386 = llvm.load %v385 : !llvm.ptr -> i32
%v387 = arith.addi %v384, %v386 : i32
%v388 = llvm.mlir.addressof @counter : !llvm.ptr
%v389 = llvm.load %v388 : !llvm.ptr -> i32
%v390 = arith.addi %v387, %v389 : i32
%v391 = llvm.mlir.addressof @str_6 : !llvm.ptr
%v392 = llvm.call @printf(%v391, %v390) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i32) -> i32
%v393 = arith.constant 0 : i32
%v394 = llvm.mlir.addressof @NEG : !llvm.ptr
%v395 = llvm.load %v394 : !llvm.ptr -> i64
%v396 = llvm.mlir.addressof @str_4 : !llvm.ptr
%v397 = llvm.call @printf(%v396, %v395) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, i64) -> i32
%v398 = arith.constant 0 : i32
%v399 = arith.constant 1.5 : f64
%v400 = arith.constant 2.0 : f64
%v401 = arith.mulf %v399, %v400 : f64
%v402 = llvm.mlir.addressof @str_3 : !llvm.ptr
%v403 = llvm.call @printf(%v402, %v401) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, f64) -> i32
%v404 = arith.constant 0 : i32
%v405 = arith.constant 0 : i32
func.return %v405 : i32
}
}
