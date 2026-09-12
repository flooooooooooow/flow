import unittest
from flow.mlir_optimizer import specialize_shapes

class TestShapeSpecialization(unittest.TestCase):
    def test_specialize_shapes_basic(self):
        mlir = """
        module {
          func.func @compute(%arg0: memref<?xf32>) {
            %0 = memref.load %arg0[%c0] : memref<?xf32>
          }
        }
        """
        specialized = specialize_shapes(mlir, "compute", {"memref<?xf32>": "memref<1024xf32>"})
        
        self.assertNotIn("memref<?xf32>", specialized)
        self.assertIn("memref<1024xf32>", specialized)
        self.assertIn("@compute(%arg0: memref<1024xf32>)", specialized)

    def test_specialize_shapes_does_not_affect_other_functions(self):
        mlir = """
        module {
          func.func @compute(%arg0: memref<?xf32>) {
            %0 = memref.load %arg0[%c0] : memref<?xf32>
          }
          func.func @other(%arg0: memref<?xf32>) {
            %0 = memref.load %arg0[%c0] : memref<?xf32>
          }
        }
        """
        specialized = specialize_shapes(mlir, "compute", {"memref<?xf32>": "memref<1024xf32>"})
        
        self.assertIn("@compute(%arg0: memref<1024xf32>)", specialized)
        self.assertIn("@other(%arg0: memref<?xf32>)", specialized)

    def test_specialize_shapes_handles_multiple_types(self):
        mlir = """
        module {
          func.func @compute(%arg0: memref<?xf32>, %arg1: memref<?xi32>) {
            %0 = memref.load %arg0[%c0] : memref<?xf32>
            %1 = memref.load %arg1[%c0] : memref<?xi32>
          }
        }
        """
        specialized = specialize_shapes(mlir, "compute", {
            "memref<?xf32>": "memref<1024xf32>",
            "memref<?xi32>": "memref<2048xi32>"
        })
        
        self.assertIn("@compute(%arg0: memref<1024xf32>, %arg1: memref<2048xi32>)", specialized)
        self.assertIn("memref.load %arg1[%c0] : memref<2048xi32>", specialized)

if __name__ == '__main__':
    unittest.main()
