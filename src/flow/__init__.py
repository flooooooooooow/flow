"""
FLOW Language Compiler Package
"""

from .version import __version__ as __version__
from ._dynamics_dsl_fixes import install as _install_dynamics_dsl_fixes
from .monomorphize import monomorphize as monomorphize, Monomorphizer as Monomorphizer

_install_dynamics_dsl_fixes()
del _install_dynamics_dsl_fixes
