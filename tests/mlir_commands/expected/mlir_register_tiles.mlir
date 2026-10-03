module {
func.func private @register_tile_outer_product(vector<4xf32>, vector<4xf32>) -> vector<4xf32>
func.func @probe(%arg0: vector<4xf32>, %arg1: vector<4xf32>) -> i32 {
// flow.register_tile_target = "generic"
// flow.register_tile_lowering = "vector.outerproduct"
%v1 = vector.outerproduct %arg0, %arg1 : vector<4xf32>, vector<4xf32>
%v2 = arith.constant 0 : i32
func.return %v2 : i32
}
func.func @main() -> i32 {
%v3 = arith.constant 0 : i32
func.return %v3 : i32
}
}
