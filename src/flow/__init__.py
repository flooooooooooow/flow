"""
FLOW Language Compiler Package
"""

from .version import __version__ as __version__
from ._dynamics_dsl_fixes import install as _install_dynamics_dsl_fixes
from .monomorphize import monomorphize as monomorphize, Monomorphizer as Monomorphizer

# Keep cross-backend semantic fixes isolated while the legacy MLIR generator
# converges with the C backend. Importing the package installs the extensions
# before callers obtain MLIRGenerator from flow.mlir_generator.
from .mlir_parity import install as _install_mlir_parity
from .mlir_match_termination import install as _install_mlir_match_termination
from .mlir_closure_parity import install as _install_mlir_closure_parity
from .mlir_nested_closure_parity import install as _install_mlir_nested_closure_parity

_install_dynamics_dsl_fixes()
_install_mlir_parity()
_install_mlir_match_termination()
_install_mlir_closure_parity()
_install_mlir_nested_closure_parity()
del _install_dynamics_dsl_fixes
del _install_mlir_parity
del _install_mlir_match_termination
del _install_mlir_closure_parity
del _install_mlir_nested_closure_parity
