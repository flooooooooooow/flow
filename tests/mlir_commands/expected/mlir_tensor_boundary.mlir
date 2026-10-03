module {
func.func @add_once(%arg0: tensor<?xf32>, %arg1: tensor<?xf32>) -> tensor<?xf32> {
%v1 = arith.constant 0 : index
%v2 = tensor.dim %arg0, %v1 : tensor<?xf32>
%v3 = tensor.empty(%v2) : tensor<?xf32>
%v4 = linalg.generic {
indexing_maps = [affine_map<(d0) -> (d0)>, affine_map<(d0) -> (d0)>, affine_map<(d0) -> (d0)>],
iterator_types = ["parallel"]
} ins(%arg0 : tensor<?xf32>, %arg1 : tensor<?xf32>) outs(%v3 : tensor<?xf32>) {
^b1(%lhs: f32, %rhs: f32, %out: f32):
%v5 = arith.addf %lhs, %rhs : f32
linalg.yield %v5 : f32
} -> tensor<?xf32>
func.return %v4 : tensor<?xf32>
}
func.func @pipeline(%arg0: tensor<?xf32>, %arg1: tensor<?xf32>) -> tensor<?xf32> {
%v6 = func.call @add_once(%arg0, %arg1) : (tensor<?xf32>, tensor<?xf32>) -> tensor<?xf32>
%v7 = func.call @add_once(%v6, %arg1) : (tensor<?xf32>, tensor<?xf32>) -> tensor<?xf32>
func.return %v7 : tensor<?xf32>
}
}
