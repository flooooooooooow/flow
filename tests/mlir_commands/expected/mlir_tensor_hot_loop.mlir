module {
func.func @accumulate(%arg0: tensor<?xf32>, %arg1: tensor<?xf32>, %arg2: i32) -> tensor<?xf32> {
%v1 = arith.constant 0 : i32
%v2 = arith.index_cast %v1 : i32 to index
%v3 = arith.index_cast %arg2 : i32 to index
%v4 = arith.constant 1 : index
%v5 = scf.for %v6 = %v2 to %v3 step %v4 iter_args(%v7 = %arg0) -> (tensor<?xf32>) {
%v8 = arith.constant 0 : index
%v9 = tensor.dim %v7, %v8 : tensor<?xf32>
%v10 = tensor.empty(%v9) : tensor<?xf32>
%v11 = linalg.generic {
indexing_maps = [affine_map<(d0) -> (d0)>, affine_map<(d0) -> (d0)>, affine_map<(d0) -> (d0)>],
iterator_types = ["parallel"]
} ins(%v7, %arg1 : tensor<?xf32>, tensor<?xf32>) outs(%v10 : tensor<?xf32>) {
^b1(%lhs: f32, %rhs: f32, %out: f32):
%v12 = arith.addf %lhs, %rhs : f32
linalg.yield %v12 : f32
} -> tensor<?xf32>
scf.yield %v11 : tensor<?xf32>
}
func.return %v5 : tensor<?xf32>
}
func.func @scale_loop(%arg0: tensor<?xf32>, %arg1: f32, %arg2: i32) -> tensor<?xf32> {
%v13 = arith.constant 0 : i32
%v14 = arith.index_cast %v13 : i32 to index
%v15 = arith.index_cast %arg2 : i32 to index
%v16 = arith.constant 1 : index
%v17 = scf.for %v18 = %v14 to %v15 step %v16 iter_args(%v19 = %arg0) -> (tensor<?xf32>) {
%v20 = arith.constant 0 : index
%v21 = tensor.dim %v19, %v20 : tensor<?xf32>
%v22 = tensor.empty(%v21) : tensor<?xf32>
%v23 = linalg.generic {
indexing_maps = [affine_map<(d0) -> (d0)>, affine_map<(d0) -> ()>, affine_map<(d0) -> (d0)>],
iterator_types = ["parallel"]
} ins(%v19, %arg1 : tensor<?xf32>, f32) outs(%v22 : tensor<?xf32>) {
^b1(%in: f32, %scalar: f32, %out: f32):
%v24 = arith.addf %in, %scalar : f32
linalg.yield %v24 : f32
} -> tensor<?xf32>
scf.yield %v23 : tensor<?xf32>
}
func.return %v17 : tensor<?xf32>
}
}
