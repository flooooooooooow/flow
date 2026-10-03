import unittest
import os
import subprocess
import shutil

class TestShapeSpecializer(unittest.TestCase):
    def test_shape_specialization_execution(self):
        # Test just the toolchain flag integration
        self.assertTrue(os.path.exists("tools/flow_cli/shape_specializer.flow"))

        with open("test_dummy.flow", "w") as f:
            f.write("function main() -> i32 { return 0 }\n")

        env = os.environ.copy()

        # Determine paths
        flow_exec = "./flow"

        # Use a shell command to exactly replicate the bash context
        result_spec = subprocess.run(f"{flow_exec} jit test_dummy.flow --shape-spec='memref<?xf32>=memref<1024xf32>'", shell=True, env=env)

        os.remove("test_dummy.flow")
        self.assertEqual(result_spec.returncode, 0)

if __name__ == '__main__':
    unittest.main()
