module {
func.func @accumulate(%arg0: tensor<?xf32>, %arg1: tensor<?xf32>, %arg2: i32) -> tensor<?xf32> {
%v1 = arith.constant 0 : i32
%v2 = arith.index_cast %v1 : i32 to index
%v3 = arith.index_cast %arg2 : i32 to index
%v4 = arith.constant 1 : index
%v5 = scf.for %v6 = %v2 to %v3 step %v4 iter_args(%v7 = %arg0) -> (tensor<?xf32>) {
%v8 = linalg.generic {
indexing_maps = [affine_map<(d0) -> (d0)>, affine_map<(d0) -> (d0)>],
iterator_types = ["parallel"]
} ins(%arg1 : tensor<?xf32>) outs(%v7 : tensor<?xf32>) {
^b1(%in: f32, %out: f32):
%v9 = arith.addf %in, %out : f32
linalg.yield %v9 : f32
} -> tensor<?xf32>
scf.yield %v8 : tensor<?xf32>
}
func.return %v5 : tensor<?xf32>
}
func.func @scale_loop(%arg0: tensor<?xf32>, %arg1: f32, %arg2: i32) -> tensor<?xf32> {
%v10 = arith.constant 0 : i32
%v11 = arith.index_cast %v10 : i32 to index
%v12 = arith.index_cast %arg2 : i32 to index
%v13 = arith.constant 1 : index
%v14 = scf.for %v15 = %v11 to %v12 step %v13 iter_args(%v16 = %arg0) -> (tensor<?xf32>) {
%v17 = linalg.generic {
indexing_maps = [affine_map<(d0) -> ()>, affine_map<(d0) -> (d0)>],
iterator_types = ["parallel"]
} ins(%arg1 : f32) outs(%v16 : tensor<?xf32>) {
^b1(%scalar: f32, %out: f32):
%v18 = arith.addf %out, %scalar : f32
linalg.yield %v18 : f32
} -> tensor<?xf32>
scf.yield %v17 : tensor<?xf32>
}
func.return %v14 : tensor<?xf32>
}
}
