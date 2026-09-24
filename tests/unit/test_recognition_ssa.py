from flow.recognition_ssa import (
    AttractorSignature, RecognitionContract, RecognitionRefinementError,
    assert_recognition_refinement, check_recognition_refinement,
)

def discrete_yes(before, after):
    return True

def test_empty_contracts_are_conservative_extension():
    cert = check_recognition_refinement("a", "b", discrete_refines=discrete_yes)
    assert cert.preserved
    assert cert.witnesses == ()

def test_continuous_drift_within_epsilon_is_accepted():
    states = {
        ("a", "numerical"): AttractorSignature(fixed_points=((0.0,),), stability=(-1.0,), invariants=(2.0,)),
        ("b", "numerical"): AttractorSignature(fixed_points=((0.01,),), stability=(-0.99,), invariants=(2.0,)),
    }
    cert = check_recognition_refinement("a", "b", discrete_refines=discrete_yes, contracts=(RecognitionContract("numerical", epsilon=0.02),), observe=lambda p, q: states[(p, q)])
    assert cert.preserved

def test_basin_change_is_rejected():
    states = {
        ("a", "safety"): AttractorSignature(basin_labels=(0, 1)),
        ("b", "safety"): AttractorSignature(basin_labels=(0, 0)),
    }
    try:
        assert_recognition_refinement("a", "b", discrete_refines=discrete_yes, contracts=(RecognitionContract("safety", epsilon=100.0),), observe=lambda p, q: states[(p, q)])
    except RecognitionRefinementError as exc:
        assert "safety" in str(exc)
    else:
        raise AssertionError("basin topology drift must be rejected")

def test_discrete_refinement_remains_mandatory():
    cert = check_recognition_refinement("a", "b", discrete_refines=lambda a, b: False)
    assert not cert.preserved
