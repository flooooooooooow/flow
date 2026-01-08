"""
Basic test to verify the test infrastructure works.
"""


def test_basic_setup():
    """Test that basic Python functionality works."""
    assert 1 + 1 == 2


def test_imports():
    """Test that we can import flow modules."""
    import sys
    import os

    # Add src to path if not already there
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_path = os.path.join(project_root, "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    # Test basic import
    from flow.parser import TokenType

    assert TokenType.FUNCTION.value == "FUNCTION"
