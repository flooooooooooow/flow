module {
func.func private @register_tile_outer_product(vector<4xf32>, vector<4xf32>) -> vector<4xvector<4xf32>>
func.func @probe(%arg0: vector<4xf32>, %arg1: vector<4xf32>) -> vector<4xvector<4xf32>> {
// flow.register_tile_target = "generic"
// flow.register_tile_lowering = "vector.outerproduct"
// flow.register_tile_lanes = 16
// flow.register_tile_max_lanes = 256
%v1 = vector.outerproduct %arg0, %arg1 : vector<4xf32>, vector<4xf32>
func.return %v1 : vector<4xvector<4xf32>>
}
}
