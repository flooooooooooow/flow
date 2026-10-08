module {
func.func @ops(%arg0: tensor<?xf32>, %arg1: f32) -> tensor<?xf32> {
%v1 = arith.constant 0 : index
%v2 = tensor.dim %arg0, %v1 : tensor<?xf32>
%v3 = tensor.empty(%v2) : tensor<?xf32>
%v4 = linalg.generic {
indexing_maps = [affine_map<(d0) -> (d0)>, affine_map<(d0) -> ()>, affine_map<(d0) -> (d0)>],
iterator_types = ["parallel"]
} ins(%arg0, %arg1 : tensor<?xf32>, f32) outs(%v3 : tensor<?xf32>) {
^b1(%in: f32, %scalar: f32, %out: f32):
%v5 = arith.mulf %in, %scalar : f32
linalg.yield %v5 : f32
} -> tensor<?xf32>
%v6 = arith.constant 0 : index
%v7 = tensor.dim %v4, %v6 : tensor<?xf32>
%v8 = tensor.empty(%v7) : tensor<?xf32>
%v9 = linalg.generic {
indexing_maps = [affine_map<(d0) -> (d0)>, affine_map<(d0) -> ()>, affine_map<(d0) -> (d0)>],
iterator_types = ["parallel"]
} ins(%v4, %arg1 : tensor<?xf32>, f32) outs(%v8 : tensor<?xf32>) {
^b1(%in: f32, %scalar: f32, %out: f32):
%v10 = arith.addf %in, %scalar : f32
linalg.yield %v10 : f32
} -> tensor<?xf32>
func.return %v9 : tensor<?xf32>
}
}
