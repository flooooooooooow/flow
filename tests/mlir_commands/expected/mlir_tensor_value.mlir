module {
func.func @ops(%arg0: tensor<?xf32>, %arg1: tensor<?xf32>) -> tensor<?xf32> {
%v1 = arith.constant 0 : index
%v2 = tensor.dim %arg0, %v1 : tensor<?xf32>
%v3 = tensor.empty(%v2) : tensor<?xf32>
%v4 = linalg.generic {
indexing_maps = [affine_map<(d0) -> (d0)>, affine_map<(d0) -> (d0)>],
iterator_types = ["parallel"]
} ins(%arg1 : tensor<?xf32>) outs(%v3 : tensor<?xf32>) {
^b1(%in: f32, %out: f32):
%v5 = arith.addf %in, %out : f32
linalg.yield %v5 : f32
} -> tensor<?xf32>
%v6 = arith.constant 0 : index
%v7 = tensor.dim %v4, %v6 : tensor<?xf32>
%v8 = tensor.empty(%v7) : tensor<?xf32>
%v9 = linalg.generic {
indexing_maps = [affine_map<(d0) -> (d0)>, affine_map<(d0) -> (d0)>],
iterator_types = ["parallel"]
} ins(%arg1 : tensor<?xf32>) outs(%v8 : tensor<?xf32>) {
^b1(%in: f32, %out: f32):
%v10 = arith.subf %in, %out : f32
linalg.yield %v10 : f32
} -> tensor<?xf32>
%v11 = arith.constant 0 : index
%v12 = tensor.dim %v9, %v11 : tensor<?xf32>
%v13 = tensor.empty(%v12) : tensor<?xf32>
%v14 = linalg.generic {
indexing_maps = [affine_map<(d0) -> (d0)>, affine_map<(d0) -> (d0)>],
iterator_types = ["parallel"]
} ins(%arg1 : tensor<?xf32>) outs(%v13 : tensor<?xf32>) {
^b1(%in: f32, %out: f32):
%v15 = arith.mulf %in, %out : f32
linalg.yield %v15 : f32
} -> tensor<?xf32>
%v16 = arith.constant 0 : index
%v17 = tensor.dim %v14, %v16 : tensor<?xf32>
%v18 = tensor.empty(%v17) : tensor<?xf32>
%v19 = linalg.generic {
indexing_maps = [affine_map<(d0) -> (d0)>, affine_map<(d0) -> (d0)>],
iterator_types = ["parallel"]
} ins(%arg1 : tensor<?xf32>) outs(%v18 : tensor<?xf32>) {
^b1(%in: f32, %out: f32):
%v20 = arith.divf %in, %out : f32
linalg.yield %v20 : f32
} -> tensor<?xf32>
func.return %v19 : tensor<?xf32>
}
}
