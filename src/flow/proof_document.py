#!/usr/bin/env python3
"""
Generate English proof prose and numbered LaTeX from Flow verification files.
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from flow.claim_address import (
    address_phrase,
    tier_opening_plain,
    try_parse_claim_address,
)
from flow.claim_path import assume_premise, tier_label
from flow.math_prose import (
    addr_coordinate_display,
    addr_coordinate_latex,
    claim_path_latex,
    flow_expr_to_latex,
    flow_expr_to_mathematical_english,
    mathematical_case_condition,
)
from flow.proof_substitution import (
    SubstitutionBox,
    instantiate_premise_latex,
    substitution_boxes_for_refs,
)


# Most basic proofs, in teaching order.
BASIC_PROOF_BUNDLE: List[str] = [
    "lib/verify/Eq.flow",
    "examples/verify/math/derived/Eq-symmetric.flow",
    "examples/verify/math/derived/Eq-transitive.flow",
    "examples/verify/math/derived/Eq-subst-add-right.flow",
    "examples/verify/math/derived/Eq-subst-add-left.flow",
    "examples/verify/math/derived/Eq-subst-mul-right.flow",
    "examples/verify/math/derived/Eq-subst-mul-left.flow",
    "examples/verify/math/derived/Eq-trans-subst-add.flow",
    "examples/verify/math/derived/Eq-trans-subst-mul.flow",
    "examples/verify/math/derived/Eq-trans-subst-add-left.flow",
    "examples/verify/math/derived/Eq-trans-subst-mul-left.flow",
    "examples/verify/math/derived/Eq-reflexive-zero.flow",
    "examples/verify/math/derived/Eq-reflexive-one.flow",
    "lib/verify/Bool.flow",
    "examples/verify/math/derived/Bool-or-assoc.flow",
    "examples/verify/math/derived/Bool-and-assoc.flow",
    "examples/verify/math/derived/Bool-not-involution.flow",
    "examples/verify/math/derived/Bool-de-morgan.flow",
    "examples/verify/math/derived/Bool-or-false-left.flow",
    "examples/verify/math/derived/Bool-and-true-left.flow",
    "examples/verify/math/derived/Bool-or-true-absorb.flow",
    "examples/verify/math/derived/Bool-and-false-absorb.flow",
    "examples/verify/math/derived/Bool-de-morgan-disj.flow",
    "examples/verify/math/derived/Bool-or-true-right.flow",
    "examples/verify/math/derived/Bool-and-false-right.flow",
    "examples/verify/math/derived/Bool-or-false-right.flow",
    "examples/verify/math/derived/Bool-and-true-right.flow",
    "examples/verify/math/derived/Bool-and-false-twice.flow",
    "examples/verify/math/derived/Bool-or-true-twice.flow",
    "lib/verify/Nat.flow",
    "lib/verify/Nat-core.flow",
    "examples/verify/math/derived/Nat-plus-zero-right.flow",
    "examples/verify/math/derived/Nat-plus-zero-left-derived.flow",
    "examples/verify/math/derived/Nat-plus-succ-left.flow",
    "examples/verify/math/derived/Nat-plus-assoc.flow",
    "examples/verify/math/derived/Nat-plus-commutes.flow",
    "examples/verify/math/derived/Nat-plus-cancel-left.flow",
    "examples/verify/math/derived/Nat-plus-cancel-right.flow",
    "lib/verify/Nat-mul.flow",
    "examples/verify/math/derived/Nat-mul-one-left.flow",
    "examples/verify/math/derived/Nat-mul-commutes.flow",
    "examples/verify/math/derived/Nat-mul-one-right.flow",
    "examples/verify/math/derived/Nat-mul-one-squared.flow",
    "examples/verify/math/derived/Nat-mul-distrib-left.flow",
    "examples/verify/math/derived/Nat-mul-distrib-right.flow",
    "examples/verify/math/derived/Nat-mul-assoc.flow",
    "lib/verify/Nat-order.flow",
    "examples/verify/math/derived/Nat-plus-mono-right.flow",
    "examples/verify/math/derived/Nat-order-plus-characterization.flow",
    "lib/verify/Nat-sq.flow",
    "examples/verify/math/derived/Nat-sq-nonneg.flow",
    "examples/verify/math/derived/Nat-sq-one.flow",
    "examples/verify/math/derived/Nat-sq-zero.flow",
    "examples/verify/math/derived/Nat-zero-times-one.flow",
    "examples/verify/math/derived/Nat-one-times-zero.flow",
    "examples/verify/math/derived/Nat-add-zero-zero.flow",
    "examples/verify/math/derived/Nat-zero-times-zero.flow",
    "examples/verify/math/derived/Nat-mul-two-one.flow",
    "examples/verify/math/derived/Nat-plus-one-zero.flow",
    "examples/verify/math/derived/Nat-plus-zero-one.flow",
    "examples/verify/math/derived/Nat-mul-two-zero.flow",
    "examples/verify/math/derived/Nat-mul-zero-two.flow",
    "examples/verify/math/derived/Nat-mul-one-two.flow",
    "examples/verify/math/derived/Nat-sq-two.flow",
    "examples/verify/math/derived/Nat-plus-two-zero.flow",
    "examples/verify/math/derived/Nat-plus-zero-two.flow",
    "examples/verify/math/derived/Nat-mul-equals-sq-two.flow",
    "examples/verify/math/derived/Nat-mul-three-one.flow",
    "examples/verify/math/derived/Nat-mul-one-three.flow",
    "examples/verify/math/derived/Nat-mul-three-zero.flow",
    "examples/verify/math/derived/Nat-mul-zero-three.flow",
    "examples/verify/math/derived/Nat-plus-three-zero.flow",
    "examples/verify/math/derived/Nat-plus-zero-three.flow",
    "examples/verify/math/derived/Nat-plus-one-one-two.flow",
    "examples/verify/math/derived/Nat-sq-three.flow",
    "examples/verify/math/derived/Nat-mul-four-zero.flow",
    "examples/verify/math/derived/Nat-mul-zero-four.flow",
    "examples/verify/math/derived/Nat-plus-four-zero.flow",
    "examples/verify/math/derived/Nat-plus-zero-four.flow",
    "examples/verify/math/derived/Nat-mul-five-zero.flow",
    "examples/verify/math/derived/Nat-mul-zero-five.flow",
    "examples/verify/math/derived/Nat-plus-two-one.flow",
    "examples/verify/math/derived/Nat-plus-one-two.flow",
    "examples/verify/math/derived/Nat-plus-two-two.flow",
    "examples/verify/math/derived/Nat-mul-one-one.flow",
    "examples/verify/math/derived/Nat-order-reflexive-zero.flow",
    "examples/verify/math/derived/Nat-order-reflexive-one.flow",
    "examples/verify/math/derived/Nat-plus-three-one.flow",
    "examples/verify/math/derived/Nat-plus-one-three.flow",
    "examples/verify/math/derived/Nat-mul-three-sq.flow",
    "examples/verify/math/derived/Nat-order-reflexive-two.flow",
    "examples/verify/math/derived/Nat-plus-four-one.flow",
    "examples/verify/math/derived/Nat-mul-four-one.flow",
    "examples/verify/math/derived/Nat-plus-five-one.flow",
    "examples/verify/math/derived/Nat-mul-five-one.flow",
    "examples/verify/math/derived/Nat-plus-six-one.flow",
    "examples/verify/math/derived/Nat-mul-six-one.flow",
    "examples/verify/math/derived/Nat-mul-mono-right.flow",
    "examples/verify/math/derived/Nat-order-trichotomy.flow",
    "examples/verify/math/derived/Nat-order-lt-succ.flow",
    "examples/verify/math/derived/Nat-induction-meta.flow",
    "lib/verify/Int.flow",
    "examples/verify/math/derived/Int-add-comm.flow",
    "examples/verify/math/derived/Int-add-assoc.flow",
    "examples/verify/math/derived/Int-neg-add.flow",
    "examples/verify/math/derived/Int-mul-one-right.flow",
    "examples/verify/math/derived/Int-mul-comm.flow",
    "examples/verify/math/derived/Int-mul-one-left.flow",
    "examples/verify/math/derived/Int-mul-one-squared.flow",
    "lib/verify/Rat.flow",
    "examples/verify/math/derived/Rat-add-comm.flow",
    "examples/verify/math/derived/Rat-add-assoc.flow",
    "examples/verify/math/derived/Rat-mul-one-right.flow",
    "examples/verify/math/derived/Rat-mul-comm.flow",
    "lib/verify/Real.flow",
    "examples/verify/math/derived/Real-add-comm.flow",
    "examples/verify/math/derived/Real-add-assoc.flow",
    "examples/verify/math/derived/Real-mul-one-right.flow",
    "examples/verify/math/derived/Real-mul-comm.flow",
    "examples/verify/math/derived/Rat-mul-assoc.flow",
    "examples/verify/math/derived/Real-mul-assoc.flow",
    "examples/verify/math/derived/Int-mul-assoc.flow",
    "examples/verify/math/derived/Int-add-cancel.flow",
    "lib/verify/Ratio.flow",
    "examples/verify/math/derived/Ratio-alternando.flow",
    "examples/verify/math/derived/Real-mul-distrib-left.flow",
    "examples/verify/math/derived/Rat-add-cancel.flow",
    "examples/verify/math/derived/Int-add-cancel-left.flow",
    "examples/verify/math/derived/Real-mul-distrib-right.flow",
    "examples/verify/math/derived/Rat-mul-distrib-left.flow",
    "examples/verify/math/derived/Int-mul-distrib-left.flow",
    "examples/verify/math/derived/Ratio-invertendo.flow",
    "examples/verify/math/derived/Ratio-componendo.flow",
    "examples/verify/math/derived/Nat-plus-succ-right.flow",
    "examples/verify/math/derived/Nat-mul-zero-left.flow",
    "examples/verify/math/derived/Ratio-dividendo.flow",
    "examples/verify/math/derived/Int-mul-distrib-right.flow",
    "examples/verify/math/derived/Rat-mul-distrib-right.flow",
    "examples/verify/math/derived/Real-add-cancel.flow",
    "examples/verify/math/derived/Nat-plus-mono-left.flow",
    "examples/verify/math/derived/Ratio-componendo-dividendo.flow",
    "examples/verify/math/derived/Real-add-cancel-left.flow",
    "examples/verify/math/derived/Rat-add-cancel-left.flow",
    "examples/verify/math/derived/Nat-sq-succ.flow",
    "examples/verify/math/derived/Nat-order-lt-implies-le.flow",
    "examples/verify/math/derived/Int-neg-self.flow",
    "examples/verify/math/Int-square-nonneg.flow",
    "examples/verify/math/derived/Int-neg-zero.flow",
    "examples/verify/math/derived/Int-mul-zero-left.flow",
    "examples/verify/math/derived/Int-mul-zero-right.flow",
    "examples/verify/math/derived/Int-add-zero-right-derived.flow",
    "examples/verify/math/derived/Int-add-zero-left-derived.flow",
    "examples/verify/math/derived/Int-add-zero-zero.flow",
    "examples/verify/math/derived/Int-add-one-zero.flow",
    "examples/verify/math/derived/Int-zero-plus-one.flow",
    "examples/verify/math/derived/Int-one-times-one.flow",
    "examples/verify/math/derived/Nat-mul-zero-right.flow",
    "examples/verify/math/derived/Real-add-zero-right-derived.flow",
    "examples/verify/math/derived/Real-add-zero-left-derived.flow",
    "examples/verify/math/derived/Real-add-zero-zero.flow",
    "examples/verify/math/derived/Real-one-times-zero.flow",
    "examples/verify/math/derived/Rat-add-zero-right-derived.flow",
    "examples/verify/math/derived/Rat-add-zero-left-derived.flow",
    "examples/verify/math/derived/Rat-add-zero-zero.flow",
    "examples/verify/math/derived/Rat-one-times-zero.flow",
    "examples/verify/math/derived/Rat-add-one-zero.flow",
    "examples/verify/math/derived/Rat-one-times-one.flow",
    "examples/verify/math/derived/Rat-mul-zero-times-one.flow",
    "examples/verify/math/derived/Real-one-times-one.flow",
    "examples/verify/math/derived/Real-mul-zero-times-one.flow",
    "examples/verify/math/derived/Real-mul-zero-left.flow",
    "examples/verify/math/derived/Real-mul-zero-right.flow",
    "examples/verify/math/derived/Rat-mul-zero-left.flow",
    "examples/verify/math/derived/Rat-mul-zero-right.flow",
    "examples/verify/math/derived/Rat-mul-one-left-derived.flow",
    "examples/verify/math/derived/Real-mul-one-left-derived.flow",
    "examples/verify/math/derived/Rat-mul-one-squared.flow",
    "examples/verify/math/derived/Real-mul-one-squared.flow",
    "examples/verify/math/derived/Int-zero-times-one.flow",
    "examples/verify/math/derived/Int-one-times-zero.flow",
    "examples/verify/math/derived/Int-zero-times-zero.flow",
    "examples/verify/math/derived/Rat-zero-plus-one.flow",
    "examples/verify/math/derived/Real-zero-plus-one.flow",
    "examples/verify/math/derived/Real-add-one-zero.flow",
    "examples/verify/math/derived/Rat-zero-times-one.flow",
    "examples/verify/math/derived/Rat-zero-times-zero.flow",
    "examples/verify/math/derived/Real-zero-times-one.flow",
    "examples/verify/math/derived/Real-zero-times-zero.flow",
    "examples/verify/math/derived/Real-zero-plus-zero.flow",
    "examples/verify/math/derived/Nat-plus-seven-one.flow",
    "examples/verify/math/derived/Nat-mul-seven-one.flow",
    "examples/verify/math/derived/Nat-plus-eight-one.flow",
    "examples/verify/math/derived/Nat-mul-eight-one.flow",
    "examples/verify/math/derived/Nat-plus-nine-one.flow",
    "examples/verify/math/derived/Nat-mul-nine-one.flow",
    "examples/verify/math/derived/Nat-plus-ten-one.flow",
    "examples/verify/math/derived/Nat-mul-ten-one.flow",
    "examples/verify/math/derived/Nat-plus-eleven-one.flow",
    "examples/verify/math/derived/Nat-mul-eleven-one.flow",
    "examples/verify/math/derived/Nat-plus-twelve-one.flow",
    "examples/verify/math/derived/Nat-mul-twelve-one.flow",
    "examples/verify/math/derived/Nat-plus-thirteen-one.flow",
    "examples/verify/math/derived/Nat-mul-thirteen-one.flow",
    "examples/verify/math/derived/Nat-plus-fourteen-one.flow",
    "examples/verify/math/derived/Nat-mul-fourteen-one.flow",
    "examples/verify/math/derived/Nat-plus-fifteen-one.flow",
    "examples/verify/math/derived/Nat-mul-fifteen-one.flow",
    "examples/verify/math/derived/Nat-plus-sixteen-one.flow",
    "examples/verify/math/derived/Nat-mul-sixteen-one.flow",
    "examples/verify/math/derived/Nat-plus-seventeen-one.flow",
    "examples/verify/math/derived/Nat-mul-seventeen-one.flow",
    "examples/verify/math/derived/Nat-plus-eighteen-one.flow",
    "examples/verify/math/derived/Nat-mul-eighteen-one.flow",
    "examples/verify/math/derived/Nat-plus-nineteen-one.flow",
    "examples/verify/math/derived/Nat-mul-nineteen-one.flow",
    "examples/verify/math/derived/Nat-plus-twenty-one.flow",
    "examples/verify/math/derived/Nat-mul-twenty-one.flow",
    "examples/verify/math/derived/Nat-plus-twenty-two.flow",
    "examples/verify/math/derived/Nat-mul-twenty-two.flow",
    "examples/verify/math/derived/Nat-plus-twenty-three.flow",
    "examples/verify/math/derived/Nat-mul-twenty-three.flow",
    "examples/verify/math/derived/Nat-plus-twenty-four.flow",
    "examples/verify/math/derived/Nat-mul-twenty-four.flow",
    "examples/verify/math/derived/Nat-plus-twenty-five.flow",
    "examples/verify/math/derived/Nat-mul-twenty-five.flow",
    "examples/verify/math/derived/Nat-plus-twenty-six.flow",
    "examples/verify/math/derived/Nat-mul-twenty-six.flow",
    "examples/verify/math/derived/Nat-plus-twenty-seven.flow",
    "examples/verify/math/derived/Nat-mul-twenty-seven.flow",
    "examples/verify/math/derived/Nat-plus-twenty-eight.flow",
    "examples/verify/math/derived/Nat-mul-twenty-eight.flow",
    "examples/verify/math/derived/Nat-plus-twenty-nine.flow",
    "examples/verify/math/derived/Nat-mul-twenty-nine.flow",
    "examples/verify/math/derived/Nat-plus-thirty.flow",
    "examples/verify/math/derived/Nat-mul-thirty.flow",
    "examples/verify/math/derived/Nat-plus-thirty-one.flow",
    "examples/verify/math/derived/Nat-mul-thirty-one.flow",
    "examples/verify/math/derived/Nat-plus-thirty-two.flow",
    "examples/verify/math/derived/Nat-mul-thirty-two.flow",
    "examples/verify/math/derived/Nat-plus-thirty-three.flow",
    "examples/verify/math/derived/Nat-mul-thirty-three.flow",
    "examples/verify/math/derived/Nat-plus-thirty-four.flow",
    "examples/verify/math/derived/Nat-mul-thirty-four.flow",
]

DATA_PROOF_BUNDLE: List[str] = [
    "lib/verify/Pair.flow",
    "examples/verify/math/derived/Pair-swap-roundtrip.flow",
    "lib/verify/List.flow",
    "examples/verify/math/derived/List-append-assoc.flow",
    "examples/verify/math/derived/List-len-append.flow",
    "examples/verify/math/derived/List-append-empty-right.flow",
    "lib/verify/Comb.flow",
    "examples/verify/math/derived/Comb-choose-sym.flow",
    "examples/verify/math/derived/Comb-choose-n-n.flow",
    "examples/verify/math/derived/Comb-choose-one.flow",
    "lib/verify/Finset.flow",
    "examples/verify/math/derived/Finset-union-assoc.flow",
    "examples/verify/math/derived/Finset-inter-comm.flow",
    "examples/verify/math/derived/Finset-inter-assoc.flow",
    "lib/verify/Order.flow",
    "examples/verify/math/derived/Order-join-assoc.flow",
    "examples/verify/math/derived/Order-meet-idempotent.flow",
    "examples/verify/math/derived/Order-join-idempotent.flow",
    "examples/verify/math/derived/Finset-card-union.flow",
    "examples/verify/math/derived/List-len-nil.flow",
    "examples/verify/math/derived/List-rev-nil.flow",
    "examples/verify/math/derived/Finset-union-idem.flow",
    "examples/verify/math/derived/Order-absorption-meet.flow",
    "examples/verify/math/derived/Order-absorption-join.flow",
    "examples/verify/math/derived/List-rev-append.flow",
    "examples/verify/math/derived/Comb-choose-zero-n.flow",
    "examples/verify/math/derived/Finset-inter-idem.flow",
    "examples/verify/math/derived/List-len-cons.flow",
    "examples/verify/math/derived/Finset-card-inter.flow",
    "examples/verify/math/derived/Comb-pascal-base.flow",
    "examples/verify/math/derived/List-rev-rev.flow",
    "examples/verify/math/derived/Finset-card-inter-right.flow",
    "examples/verify/math/derived/Comb-choose-succ.flow",
    "examples/verify/math/derived/List-append-comm.flow",
    "examples/verify/math/derived/Finset-inter-union.flow",
    "examples/verify/math/derived/Comb-choose-two.flow",
    "examples/verify/math/derived/List-len-rev.flow",
    "examples/verify/math/derived/Finset-card-monotone.flow",
    "examples/verify/math/derived/Pair-compose-snd.flow",
    "examples/verify/math/derived/Pair-compose-fst.flow",
    "examples/verify/math/derived/Order-join-meet.flow",
    "examples/verify/math/derived/List-rev-cons.flow",
    "examples/verify/math/derived/Comb-choose-succ-one.flow",
    "examples/verify/math/derived/Comb-choose-succ-zero.flow",
    "examples/verify/math/derived/List-rev-singleton.flow",
    "examples/verify/math/derived/Finset-card-inter-monotone.flow",
    "examples/verify/math/derived/Pair-projection-roundtrip.flow",
    "examples/verify/math/derived/Comb-choose-succ-n-n.flow",
    "examples/verify/math/derived/List-append-cons-distributes.flow",
    "examples/verify/math/derived/Order-meet-leq-left.flow",
    "examples/verify/math/derived/Finset-inter-union-right.flow",
    "examples/verify/math/derived/Comb-choose-succ-two.flow",
    "examples/verify/math/derived/Order-meet-leq-right.flow",
    "examples/verify/math/derived/Order-join-geq-left.flow",
    "examples/verify/math/derived/Finset-card-union-monotone-right.flow",
    "examples/verify/math/derived/Pair-swap-fst.flow",
    "examples/verify/math/derived/List-rev-nil-append.flow",
    "examples/verify/math/derived/Comb-choose-sym-succ.flow",
    "examples/verify/math/derived/Order-join-geq-right.flow",
    "examples/verify/math/derived/Pair-swap-snd.flow",
    "examples/verify/math/derived/Comb-choose-succ-three.flow",
    "examples/verify/math/derived/List-len-singleton.flow",
    "examples/verify/math/derived/Finset-union-empty-right.flow",
    "examples/verify/math/derived/Order-meet-self-leq.flow",
    "examples/verify/math/derived/Finset-union-empty-left.flow",
    "examples/verify/math/derived/Finset-inter-empty-left.flow",
    "examples/verify/math/derived/Order-join-self-geq.flow",
    "examples/verify/math/derived/Comb-choose-succ-four.flow",
    "examples/verify/math/derived/List-len-empty-append.flow",
    "examples/verify/math/derived/Finset-inter-empty-right.flow",
    "examples/verify/math/derived/Comb-choose-succ-five.flow",
    "examples/verify/math/derived/List-len-append-nil-right.flow",
    "examples/verify/math/derived/Finset-card-inter-empty.flow",
    "examples/verify/math/derived/List-rev-append-nil-right.flow",
    "examples/verify/math/derived/Comb-choose-succ-six.flow",
    "examples/verify/math/derived/Finset-card-union-empty-right.flow",
    "examples/verify/math/derived/List-len-rev-singleton.flow",
    "examples/verify/math/derived/Order-meet-trans-join.flow",
    "examples/verify/math/derived/Pair-pairing-recover.flow",
    "examples/verify/math/derived/Comb-choose-succ-seven.flow",
    "examples/verify/math/derived/Finset-card-union-empty-left.flow",
    "examples/verify/math/derived/List-rev-rev-singleton.flow",
    "examples/verify/math/derived/Order-join-trans-meet.flow",
    "examples/verify/math/derived/Finset-card-empty-union.flow",
    "examples/verify/math/derived/Comb-choose-succ-eight.flow",
    "examples/verify/math/derived/List-len-cons-cons.flow",
    "examples/verify/math/derived/Finset-card-inter-self.flow",
    "examples/verify/math/derived/Order-meet-self-eq.flow",
    "examples/verify/math/derived/Comb-choose-succ-nine.flow",
    "examples/verify/math/derived/List-len-rev-cons-cons.flow",
    "examples/verify/math/derived/Pair-fst-from-pairing.flow",
    "examples/verify/math/derived/Pair-snd-from-pairing.flow",
    "examples/verify/math/derived/Finset-card-union-self.flow",
    "examples/verify/math/derived/List-len-rev-nil.flow",
    "examples/verify/math/derived/Order-join-self-eq.flow",
    "examples/verify/math/derived/List-append-nil-nil.flow",
    "examples/verify/math/derived/Finset-inter-comm-derived.flow",
    "examples/verify/math/derived/Comb-choose-succ-zero-k.flow",
    "examples/verify/math/derived/List-rev-singleton-fixed.flow",
    "examples/verify/math/derived/Order-meet-leq-join-via-both.flow",
    "examples/verify/math/derived/Comb-choose-succ-ten.flow",
    "examples/verify/math/derived/Finset-union-comm-derived.flow",
    "examples/verify/math/derived/List-len-rev-rev.flow",
    "examples/verify/math/derived/Order-meet-leq-join-via-left.flow",
    "examples/verify/math/derived/Finset-union-inter-empty.flow",
    "examples/verify/math/derived/List-len-append-singleton.flow",
    "examples/verify/math/derived/Comb-choose-succ-one-n.flow",
    "examples/verify/math/derived/List-append-empty-left-derived.flow",
    "examples/verify/math/derived/Finset-card-union-inter-empty.flow",
    "examples/verify/math/derived/Pair-swap-compose-fst.flow",
    "examples/verify/math/derived/Pair-swap-compose-snd.flow",
    "examples/verify/math/derived/Order-join-absorption-derived.flow",
    "examples/verify/math/derived/Comb-choose-succ-eleven.flow",
    "examples/verify/math/derived/Order-meet-absorption-derived.flow",
    "examples/verify/math/derived/List-len-rev-cons.flow",
    "examples/verify/math/derived/Finset-inter-union-empty.flow",
    "examples/verify/math/derived/List-rev-double-cons.flow",
    "examples/verify/math/derived/Comb-choose-succ-two-n.flow",
    "examples/verify/math/derived/Finset-card-inter-empty-left.flow",
    "examples/verify/math/derived/List-append-singleton-right.flow",
    "examples/verify/math/derived/Finset-union-empty-inter.flow",
    "examples/verify/math/derived/Pair-pairing-determines.flow",
    "examples/verify/math/derived/List-len-rev-double-cons.flow",
    "examples/verify/math/derived/Order-meet-leq-join-absorption.flow",
    "examples/verify/math/derived/Comb-choose-succ-twelve.flow",
    "examples/verify/math/derived/List-len-rev-append-nil.flow",
    "examples/verify/math/derived/Finset-card-union-empty-left.flow",
    "examples/verify/math/derived/Order-join-meet-absorption.flow",
    "examples/verify/math/derived/Pair-fst-snd-determine.flow",
    "examples/verify/math/derived/List-rev-rev-cons-cons.flow",
    "examples/verify/math/derived/Comb-choose-succ-three-n.flow",
    "examples/verify/math/derived/Finset-inter-self-card-bound.flow",
    "examples/verify/math/derived/Order-meet-leq-self.flow",
    "examples/verify/math/derived/List-append-assoc-derived.flow",
    "examples/verify/math/derived/Finset-union-inter-empty-self.flow",
    "examples/verify/math/derived/List-len-nil-append-both.flow",
    "examples/verify/math/derived/Comb-choose-succ-thirteen.flow",
    "examples/verify/math/derived/List-len-rev-empty-left.flow",
    "examples/verify/math/derived/Pair-snd-determine.flow",
    "examples/verify/math/derived/Comb-choose-succ-four-n.flow",
    "examples/verify/math/derived/Order-join-leq-self.flow",
    "examples/verify/math/derived/List-rev-cons-len.flow",
    "examples/verify/math/derived/Finset-union-self-inter-empty.flow",
    "examples/verify/math/derived/Order-meet-join-idem.flow",
    "examples/verify/math/derived/List-len-cons-nil-derived.flow",
    "examples/verify/math/derived/Finset-card-empty-inter-right.flow",
    "examples/verify/math/derived/List-rev-append-singleton.flow",
    "examples/verify/math/derived/Finset-union-self-card-bound-derived.flow",
    "examples/verify/math/derived/Comb-choose-succ-fourteen.flow",
    "examples/verify/math/derived/Comb-choose-succ-five-n.flow",
    "examples/verify/math/derived/List-len-rev-double-nil.flow",
    "examples/verify/math/derived/List-rev-cons-double.flow",
    "examples/verify/math/derived/Pair-fst-determines.flow",
    "examples/verify/math/derived/Finset-inter-self-empty-derived.flow",
    "examples/verify/math/derived/Finset-card-diff-empty.flow",
    "examples/verify/math/derived/Order-join-geq-self.flow",
    "examples/verify/math/derived/Order-meet-leq-join-via-right.flow",
    "examples/verify/math/derived/List-len-append-double-singleton.flow",
    "examples/verify/math/derived/Finset-union-empty-card.flow",
    "examples/verify/math/derived/List-rev-rev-double-cons.flow",
    "examples/verify/math/derived/Comb-choose-succ-fifteen.flow",
    "examples/verify/math/derived/Comb-choose-succ-six-n.flow",
    "examples/verify/math/derived/List-rev-cons-triple.flow",
    "examples/verify/math/derived/List-len-rev-triple-cons.flow",
    "examples/verify/math/derived/Pair-swap-fst-snd.flow",
    "examples/verify/math/derived/Finset-inter-union-self.flow",
    "examples/verify/math/derived/Finset-card-union-inter-self.flow",
    "examples/verify/math/derived/Order-meet-geq-self.flow",
    "examples/verify/math/derived/Order-join-leq-join-self.flow",
    "examples/verify/math/derived/List-len-cons-triple-nil.flow",
    "examples/verify/math/derived/Finset-diff-self-empty.flow",
    "examples/verify/math/derived/List-rev-rev-triple-cons.flow",
    "examples/verify/math/derived/Comb-choose-succ-sixteen.flow",
    "examples/verify/math/derived/Comb-choose-succ-seven-n.flow",
    "examples/verify/math/derived/List-rev-cons-quad.flow",
    "examples/verify/math/derived/List-len-cons-quad-nil.flow",
    "examples/verify/math/derived/Pair-swap-snd-recovers.flow",
    "examples/verify/math/derived/Finset-union-inter-empty-derived.flow",
    "examples/verify/math/derived/Finset-card-inter-union-bound.flow",
    "examples/verify/math/derived/Order-meet-join-dual.flow",
    "examples/verify/math/derived/Order-join-meet-dual.flow",
    "examples/verify/math/derived/List-len-append-triple-singleton.flow",
    "examples/verify/math/derived/Finset-diff-empty-card-zero.flow",
    "examples/verify/math/derived/List-rev-rev-quad-cons.flow",
    "examples/verify/math/derived/Comb-choose-succ-seventeen.flow",
    "examples/verify/math/derived/Comb-choose-succ-eight-n.flow",
    "examples/verify/math/derived/List-rev-cons-quint.flow",
    "examples/verify/math/derived/List-len-cons-quint-nil.flow",
    "examples/verify/math/derived/Pair-swap-compose-roundtrip.flow",
    "examples/verify/math/derived/Finset-union-self-card.flow",
    "examples/verify/math/derived/Finset-inter-empty-card-zero.flow",
    "examples/verify/math/derived/Order-meet-leq-join-trans.flow",
    "examples/verify/math/derived/Order-join-geq-meet-trans.flow",
    "examples/verify/math/derived/List-len-rev-quad-cons.flow",
    "examples/verify/math/derived/Finset-card-union-inter-bound.flow",
    "examples/verify/math/derived/List-rev-rev-quint-cons.flow",
    "examples/verify/math/derived/Comb-choose-succ-eighteen.flow",
    "examples/verify/math/derived/Comb-choose-succ-nine-n.flow",
    "examples/verify/math/derived/List-rev-cons-sext.flow",
    "examples/verify/math/derived/List-len-cons-sext-nil.flow",
    "examples/verify/math/derived/Pair-swap-triple-roundtrip.flow",
    "examples/verify/math/derived/Finset-union-inter-self-card.flow",
    "examples/verify/math/derived/Finset-diff-union-empty.flow",
    "examples/verify/math/derived/Order-meet-join-trans-right.flow",
    "examples/verify/math/derived/Order-join-meet-trans-left.flow",
    "examples/verify/math/derived/List-len-rev-quint-cons.flow",
    "examples/verify/math/derived/Finset-card-inter-self-bound.flow",
    "examples/verify/math/derived/List-rev-rev-sext-cons.flow",
    "examples/verify/math/derived/Comb-choose-succ-nineteen.flow",
    "examples/verify/math/derived/Comb-choose-succ-ten-n.flow",
    "examples/verify/math/derived/List-rev-cons-sept.flow",
    "examples/verify/math/derived/List-len-cons-sept-nil.flow",
    "examples/verify/math/derived/Pair-swap-quad-roundtrip.flow",
    "examples/verify/math/derived/Finset-inter-union-card-bound.flow",
    "examples/verify/math/derived/Finset-union-diff-empty.flow",
    "examples/verify/math/derived/Order-meet-trans-both.flow",
    "examples/verify/math/derived/Order-join-trans-both.flow",
    "examples/verify/math/derived/List-len-append-quad-singleton.flow",
    "examples/verify/math/derived/Finset-card-diff-self-zero.flow",
    "examples/verify/math/derived/List-rev-rev-sept-cons.flow",
    "examples/verify/math/derived/Comb-choose-succ-twenty.flow",
    "examples/verify/math/derived/Comb-choose-succ-eleven-n.flow",
    "examples/verify/math/derived/List-rev-cons-oct.flow",
    "examples/verify/math/derived/List-len-cons-oct-nil.flow",
    "examples/verify/math/derived/Pair-swap-quint-roundtrip.flow",
    "examples/verify/math/derived/Finset-inter-diff-empty.flow",
    "examples/verify/math/derived/Finset-card-union-self-derived.flow",
    "examples/verify/math/derived/Order-meet-absorb-join-derived.flow",
    "examples/verify/math/derived/Order-join-absorb-meet-derived.flow",
    "examples/verify/math/derived/List-len-rev-sext-cons.flow",
    "examples/verify/math/derived/List-len-append-quint-singleton.flow",
    "examples/verify/math/derived/List-rev-rev-oct-cons.flow",
    "examples/verify/math/derived/Comb-choose-succ-twenty-one.flow",
    "examples/verify/math/derived/Comb-choose-succ-twelve-n.flow",
    "examples/verify/math/derived/List-rev-cons-non.flow",
    "examples/verify/math/derived/List-len-cons-non-nil.flow",
    "examples/verify/math/derived/Pair-swap-sext-roundtrip.flow",
    "examples/verify/math/derived/Finset-inter-self-card-zero.flow",
    "examples/verify/math/derived/Finset-union-inter-diff-empty.flow",
    "examples/verify/math/derived/Order-meet-idem-join.flow",
    "examples/verify/math/derived/Order-join-idem-meet.flow",
    "examples/verify/math/derived/List-len-rev-sept-cons.flow",
    "examples/verify/math/derived/List-len-append-sext-singleton.flow",
    "examples/verify/math/derived/List-rev-rev-non-cons.flow",
    "examples/verify/math/derived/Comb-choose-succ-twenty-two.flow",
    "examples/verify/math/derived/Comb-choose-succ-thirteen-n.flow",
    "examples/verify/math/derived/List-rev-cons-decem.flow",
    "examples/verify/math/derived/List-len-cons-decem-nil.flow",
    "examples/verify/math/derived/Pair-swap-sept-roundtrip.flow",
    "examples/verify/math/derived/Finset-union-diff-self.flow",
    "examples/verify/math/derived/Finset-inter-union-card-zero.flow",
    "examples/verify/math/derived/Order-meet-join-symm.flow",
    "examples/verify/math/derived/Order-join-meet-symm.flow",
    "examples/verify/math/derived/List-len-rev-oct-cons.flow",
    "examples/verify/math/derived/List-len-append-sept-singleton.flow",
    "examples/verify/math/derived/List-rev-rev-decem-cons.flow",
    "examples/verify/math/derived/Comb-choose-succ-twenty-three.flow",
    "examples/verify/math/derived/Comb-choose-succ-fourteen-n.flow",
    "examples/verify/math/derived/List-rev-cons-undec.flow",
    "examples/verify/math/derived/List-len-cons-undec-nil.flow",
    "examples/verify/math/derived/Pair-swap-oct-roundtrip.flow",
    "examples/verify/math/derived/Finset-diff-inter-empty.flow",
    "examples/verify/math/derived/Finset-card-union-diff-empty.flow",
    "examples/verify/math/derived/Order-meet-join-comm.flow",
    "examples/verify/math/derived/Order-join-meet-comm.flow",
    "examples/verify/math/derived/List-len-rev-non-cons.flow",
    "examples/verify/math/derived/List-len-append-oct-singleton.flow",
    "examples/verify/math/derived/List-rev-rev-undec-cons.flow",
    "examples/verify/math/derived/Comb-choose-succ-twenty-four.flow",
    "examples/verify/math/derived/Comb-choose-succ-fifteen-n.flow",
    "examples/verify/math/derived/List-rev-cons-duodec.flow",
    "examples/verify/math/derived/List-len-cons-duodec-nil.flow",
    "examples/verify/math/derived/Pair-swap-non-roundtrip.flow",
    "examples/verify/math/derived/Finset-diff-union-self.flow",
    "examples/verify/math/derived/Finset-card-inter-diff-empty.flow",
    "examples/verify/math/derived/Order-meet-join-dual-comm.flow",
    "examples/verify/math/derived/Order-join-meet-dual-comm.flow",
    "examples/verify/math/derived/List-len-rev-decem-cons.flow",
    "examples/verify/math/derived/List-len-append-non-singleton.flow",
    "examples/verify/math/derived/List-rev-rev-duodec-cons.flow",
    "examples/verify/math/derived/Comb-choose-succ-twenty-five.flow",
    "examples/verify/math/derived/Comb-choose-succ-sixteen-n.flow",
    "examples/verify/math/derived/List-rev-cons-tredec.flow",
    "examples/verify/math/derived/List-len-cons-tredec-nil.flow",
    "examples/verify/math/derived/Pair-swap-decem-roundtrip.flow",
    "examples/verify/math/derived/Finset-inter-diff-self.flow",
    "examples/verify/math/derived/Finset-card-diff-union-empty.flow",
    "examples/verify/math/derived/Order-meet-join-reflex.flow",
    "examples/verify/math/derived/Order-join-meet-reflex.flow",
    "examples/verify/math/derived/List-len-rev-undec-cons.flow",
    "examples/verify/math/derived/List-len-append-decem-singleton.flow",
    "examples/verify/math/derived/List-rev-rev-tredec-cons.flow",
    "examples/verify/math/derived/Comb-choose-succ-twenty-six.flow",
    "examples/verify/math/derived/Comb-choose-succ-seventeen-n.flow",
    "examples/verify/math/derived/List-rev-cons-quattuordec.flow",
    "examples/verify/math/derived/List-len-cons-quattuordec-nil.flow",
    "examples/verify/math/derived/Pair-swap-undec-roundtrip.flow",
    "examples/verify/math/derived/Finset-union-inter-diff-self.flow",
    "examples/verify/math/derived/Finset-card-diff-inter-empty.flow",
    "examples/verify/math/derived/Order-meet-join-antim.flow",
    "examples/verify/math/derived/Order-join-meet-antim.flow",
    "examples/verify/math/derived/List-len-rev-duodec-cons.flow",
    "examples/verify/math/derived/List-len-append-undec-singleton.flow",
    "examples/verify/math/derived/List-rev-rev-quattuordec-cons.flow",
    "examples/verify/math/derived/Comb-choose-succ-twenty-seven.flow",
    "examples/verify/math/derived/Comb-choose-succ-eighteen-n.flow",
    "examples/verify/math/derived/List-rev-cons-quindec.flow",
    "examples/verify/math/derived/List-len-cons-quindec-nil.flow",
    "examples/verify/math/derived/Pair-swap-duodec-roundtrip.flow",
    "examples/verify/math/derived/Finset-inter-union-diff-self.flow",
    "examples/verify/math/derived/Finset-card-union-diff-inter-empty.flow",
    "examples/verify/math/derived/Order-meet-join-trans-left.flow",
    "examples/verify/math/derived/Order-join-meet-trans-right.flow",
    "examples/verify/math/derived/List-len-rev-tredec-cons.flow",
    "examples/verify/math/derived/List-len-append-duodec-singleton.flow",
    "examples/verify/math/derived/List-rev-rev-quindec-cons.flow",
    "examples/verify/math/derived/Comb-choose-succ-twenty-eight.flow",
    "examples/verify/math/derived/Comb-choose-succ-nineteen-n.flow",
    "examples/verify/math/derived/List-rev-cons-sedec.flow",
    "examples/verify/math/derived/List-len-cons-sedec-nil.flow",
    "examples/verify/math/derived/Pair-swap-tredec-roundtrip.flow",
    "examples/verify/math/derived/Finset-diff-union-inter-self.flow",
    "examples/verify/math/derived/Finset-card-inter-union-diff-empty.flow",
    "examples/verify/math/derived/Order-meet-join-dual-antim.flow",
    "examples/verify/math/derived/Order-join-meet-dual-antim.flow",
    "examples/verify/math/derived/List-len-rev-quattuordec-cons.flow",
    "examples/verify/math/derived/List-len-append-tredec-singleton.flow",
    "examples/verify/math/derived/List-rev-rev-sedec-cons.flow",
    "examples/verify/math/derived/Comb-choose-succ-twenty-nine.flow",
    "examples/verify/math/derived/Comb-choose-succ-twenty-n.flow",
    "examples/verify/math/derived/List-rev-cons-septendec.flow",
    "examples/verify/math/derived/List-len-cons-septendec-nil.flow",
    "examples/verify/math/derived/Pair-swap-quattuordec-roundtrip.flow",
    "examples/verify/math/derived/Finset-union-diff-inter-self.flow",
    "examples/verify/math/derived/List-len-rev-quindec-cons.flow",
    "examples/verify/math/derived/List-len-append-quattuordec-singleton.flow",
    "examples/verify/math/derived/List-rev-rev-septendec-cons.flow",
    "examples/verify/math/derived/Order-meet-join-absorb-dual.flow",
    "examples/verify/math/derived/Order-join-meet-absorb-dual.flow",
]

ALGEBRA_PROOF_BUNDLE: List[str] = [
    "lib/verify/Monoid.flow",
    "lib/verify/Group.flow",
    "examples/verify/math/derived/Group-inv-right.flow",
    "examples/verify/math/derived/Group-inv-unique.flow",
    "examples/verify/math/derived/Group-inv-inv.flow",
    "examples/verify/math/derived/Group-identity-unique.flow",
    "lib/verify/Ring.flow",
    "examples/verify/math/derived/Ring-add-assoc.flow",
    "examples/verify/math/derived/Ring-mul-assoc.flow",
    "examples/verify/math/derived/Ring-zero-right.flow",
    "examples/verify/math/derived/Ring-mul-one-right.flow",
    "examples/verify/math/derived/Ring-mul-distrib-right.flow",
    "lib/verify/Ideal.flow",
    "examples/verify/math/derived/Ideal-absorb.flow",
    "lib/verify/Subgroup.flow",
    "examples/verify/math/derived/Subgroup-inv-closed.flow",
    "lib/verify/GroupHom.flow",
    "examples/verify/math/derived/GroupHom-preserves-inverse.flow",
    "examples/verify/math/derived/Group-cancel-left.flow",
    "examples/verify/math/derived/Group-product-inverses.flow",
    "lib/verify/RingHom.flow",
    "examples/verify/math/derived/Ring-add-cancel.flow",
    "examples/verify/math/derived/RingHom-preserves-zero.flow",
    "examples/verify/math/derived/Ideal-absorb-right.flow",
    "examples/verify/math/derived/Group-cancel-right.flow",
    "examples/verify/math/derived/Monoid-identity-unique.flow",
    "examples/verify/math/derived/RingHom-preserves-one.flow",
    "examples/verify/math/derived/Subgroup-mul-closed.flow",
    "examples/verify/math/derived/Ideal-add-closed.flow",
    "examples/verify/math/derived/Ring-add-cancel-left.flow",
    "examples/verify/math/derived/Group-inverse-of-identity.flow",
    "examples/verify/math/derived/Subgroup-identity-membership.flow",
    "examples/verify/math/derived/Ideal-zero-membership.flow",
    "examples/verify/math/derived/Ring-mul-zero-left.flow",
    "examples/verify/math/derived/Ring-mul-zero-right.flow",
    "examples/verify/math/derived/Group-inverse-agreement.flow",
    "examples/verify/math/derived/Ring-zero-plus-zero.flow",
    "examples/verify/math/derived/Ring-one-times-one.flow",
    "examples/verify/math/derived/Monoid-one-times-one.flow",
    "examples/verify/math/derived/Ideal-zero-sum-closed.flow",
    "examples/verify/math/derived/RingHom-one-squared.flow",
    "examples/verify/math/derived/Ring-zero-times-one.flow",
    "examples/verify/math/derived/Ring-one-times-zero.flow",
    "examples/verify/math/derived/Ideal-zero-product.flow",
    "examples/verify/math/derived/GroupHom-inverse-product.flow",
    "examples/verify/math/derived/Subgroup-identity-squared.flow",
    "examples/verify/math/derived/GroupHom-identity-idempotent.flow",
    "examples/verify/math/derived/Ring-one-plus-zero.flow",
    "examples/verify/math/derived/Ring-zero-plus-one.flow",
    "examples/verify/math/derived/Ring-zero-times-zero.flow",
    "examples/verify/math/derived/Subgroup-inv-identity.flow",
    "examples/verify/math/derived/RingHom-zero-times-one.flow",
    "examples/verify/math/derived/RingHom-zero-squared.flow",
    "examples/verify/math/derived/Ideal-zero-self-product.flow",
    "examples/verify/math/derived/Subgroup-inv-times-identity.flow",
    "examples/verify/math/derived/Group-inv-left-product.flow",
    "examples/verify/math/derived/RingHom-one-times-zero.flow",
    "examples/verify/math/derived/Subgroup-identity-times-inv.flow",
    "examples/verify/math/derived/Group-identity-self-product.flow",
    "examples/verify/math/derived/Ideal-one-times-zero.flow",
    "examples/verify/math/derived/Subgroup-inv-squared.flow",
    "examples/verify/math/derived/GroupHom-one-self-product.flow",
    "examples/verify/math/derived/Ideal-add-zero-zero.flow",
    "examples/verify/math/derived/Group-inv-right-equals-one.flow",
    "examples/verify/math/derived/Subgroup-identity-cubed.flow",
    "examples/verify/math/derived/Group-identity-left-multiplies.flow",
    "examples/verify/math/derived/Monoid-identity-right-multiplies.flow",
    "examples/verify/math/derived/Ring-zero-left-identity.flow",
    "examples/verify/math/derived/Subgroup-identity-quad.flow",
    "examples/verify/math/derived/Group-identity-right-multiplies.flow",
    "examples/verify/math/derived/Ring-one-left-identity.flow",
    "examples/verify/math/derived/Ideal-one-plus-zero.flow",
    "examples/verify/math/derived/Subgroup-identity-pent.flow",
    "examples/verify/math/derived/Ring-zero-right-identity.flow",
    "examples/verify/math/derived/Ideal-zero-plus-one-derived.flow",
    "examples/verify/math/derived/Subgroup-identity-hex.flow",
    "examples/verify/math/derived/GroupHom-one-right-multiplies.flow",
    "examples/verify/math/derived/Ring-one-right-identity.flow",
    "examples/verify/math/derived/Monoid-identity-left.flow",
    "examples/verify/math/derived/Subgroup-identity-hept.flow",
    "examples/verify/math/derived/Ideal-one-times-one.flow",
    "examples/verify/math/derived/Group-inv-times-inv.flow",
    "examples/verify/math/derived/Ideal-add-one-zero-derived.flow",
    "examples/verify/math/derived/RingHom-zero-plus-zero.flow",
    "examples/verify/math/derived/Subgroup-identity-sept.flow",
    "examples/verify/math/derived/Subgroup-identity-oct.flow",
    "examples/verify/math/derived/GroupHom-zero-plus-zero.flow",
    "examples/verify/math/derived/Ideal-zero-plus-zero-derived.flow",
    "examples/verify/math/derived/Ring-add-zero-zero-derived.flow",
    "examples/verify/math/derived/Subgroup-identity-nona.flow",
    "examples/verify/math/derived/GroupHom-one-times-one.flow",
    "examples/verify/math/derived/Ideal-one-plus-one.flow",
    "examples/verify/math/derived/Ring-mul-one-left-derived.flow",
    "examples/verify/math/derived/Subgroup-identity-deca.flow",
    "examples/verify/math/derived/GroupHom-zero-times-one.flow",
    "examples/verify/math/derived/Ideal-zero-times-zero-derived.flow",
    "examples/verify/math/derived/Ring-zero-times-zero-derived.flow",
    "examples/verify/math/derived/Subgroup-identity-undeca.flow",
    "examples/verify/math/derived/GroupHom-zero-times-zero.flow",
    "examples/verify/math/derived/Ideal-one-times-zero-derived.flow",
    "examples/verify/math/derived/Ring-one-plus-one-derived.flow",
    "examples/verify/math/derived/Subgroup-identity-duodec.flow",
    "examples/verify/math/derived/RingHom-one-plus-one.flow",
    "examples/verify/math/derived/Monoid-zero-times-one.flow",
    "examples/verify/math/derived/Ideal-two-plus-zero.flow",
    "examples/verify/math/derived/Subgroup-identity-tredec.flow",
    "examples/verify/math/derived/RingHom-one-times-one-derived.flow",
    "examples/verify/math/derived/Monoid-one-plus-zero.flow",
    "examples/verify/math/derived/Ideal-three-plus-zero.flow",
    "examples/verify/math/derived/Subgroup-identity-quattuordec.flow",
    "examples/verify/math/derived/RingHom-zero-plus-one.flow",
    "examples/verify/math/derived/Monoid-zero-plus-zero.flow",
    "examples/verify/math/derived/Ideal-four-plus-zero.flow",
    "examples/verify/math/derived/Subgroup-identity-quindec.flow",
    "examples/verify/math/derived/RingHom-one-plus-zero.flow",
    "examples/verify/math/derived/Monoid-two-plus-zero.flow",
    "examples/verify/math/derived/Ideal-five-plus-zero.flow",
    "examples/verify/math/derived/Subgroup-identity-sedec.flow",
    "examples/verify/math/derived/RingHom-two-plus-zero.flow",
    "examples/verify/math/derived/Monoid-three-plus-zero.flow",
    "examples/verify/math/derived/Ideal-six-plus-zero.flow",
    "examples/verify/math/derived/Subgroup-identity-septendec.flow",
    "examples/verify/math/derived/RingHom-three-plus-zero.flow",
    "examples/verify/math/derived/Monoid-four-plus-zero.flow",
    "examples/verify/math/derived/Ideal-seven-plus-zero.flow",
    "examples/verify/math/derived/Subgroup-identity-octodec.flow",
    "examples/verify/math/derived/RingHom-four-plus-zero.flow",
    "examples/verify/math/derived/Monoid-five-plus-zero.flow",
    "examples/verify/math/derived/Ideal-eight-plus-zero.flow",
    "examples/verify/math/derived/Subgroup-identity-novemdec.flow",
    "examples/verify/math/derived/RingHom-five-plus-zero.flow",
    "examples/verify/math/derived/Monoid-six-plus-zero.flow",
    "examples/verify/math/derived/Ideal-nine-plus-zero.flow",
    "examples/verify/math/derived/Subgroup-identity-vigesim.flow",
    "examples/verify/math/derived/RingHom-six-plus-zero.flow",
    "examples/verify/math/derived/Monoid-seven-plus-zero.flow",
    "examples/verify/math/derived/Ideal-ten-plus-zero.flow",
    "examples/verify/math/derived/Subgroup-identity-unvigesim.flow",
    "examples/verify/math/derived/RingHom-seven-plus-zero.flow",
    "examples/verify/math/derived/Monoid-eight-plus-zero.flow",
    "examples/verify/math/derived/Ideal-eleven-plus-zero.flow",
    "examples/verify/math/derived/Subgroup-identity-duovigesim.flow",
    "examples/verify/math/derived/RingHom-eight-plus-zero.flow",
    "examples/verify/math/derived/Monoid-nine-plus-zero.flow",
    "examples/verify/math/derived/Ideal-twelve-plus-zero.flow",
    "examples/verify/math/derived/Subgroup-identity-tresvigesim.flow",
    "examples/verify/math/derived/RingHom-nine-plus-zero.flow",
    "examples/verify/math/derived/Monoid-ten-plus-zero.flow",
    "examples/verify/math/derived/Ideal-thirteen-plus-zero.flow",
    "examples/verify/math/derived/Subgroup-identity-quattuorvigesim.flow",
    "examples/verify/math/derived/RingHom-ten-plus-zero.flow",
    "examples/verify/math/derived/Monoid-eleven-plus-zero.flow",
    "examples/verify/math/derived/Ideal-fourteen-plus-zero.flow",
    "examples/verify/math/derived/Subgroup-identity-quinvigesim.flow",
    "examples/verify/math/derived/RingHom-eleven-plus-zero.flow",
    "examples/verify/math/derived/Monoid-twelve-plus-zero.flow",
    "examples/verify/math/derived/Ideal-fifteen-plus-zero.flow",
    "examples/verify/math/derived/Subgroup-identity-sexvigesim.flow",
    "examples/verify/math/derived/RingHom-twelve-plus-zero.flow",
    "examples/verify/math/derived/Monoid-thirteen-plus-zero.flow",
    "examples/verify/math/derived/Ideal-sixteen-plus-zero.flow",
    "examples/verify/math/derived/Subgroup-identity-septenvigesim.flow",
    "examples/verify/math/derived/RingHom-thirteen-plus-zero.flow",
    "examples/verify/math/derived/Monoid-fourteen-plus-zero.flow",
    "examples/verify/math/derived/Ideal-seventeen-plus-zero.flow",
    "examples/verify/math/derived/Subgroup-identity-octovigesim.flow",
    "examples/verify/math/derived/RingHom-fourteen-plus-zero.flow",
    "examples/verify/math/derived/Monoid-fifteen-plus-zero.flow",
    "examples/verify/math/derived/Ideal-eighteen-plus-zero.flow",
    "examples/verify/math/derived/Subgroup-identity-novemvigesim.flow",
    "examples/verify/math/derived/RingHom-fifteen-plus-zero.flow",
    "examples/verify/math/derived/Monoid-sixteen-plus-zero.flow",
    "examples/verify/math/derived/Ideal-nineteen-plus-zero.flow",
    "examples/verify/math/derived/Subgroup-identity-trigesim.flow",
    "examples/verify/math/derived/RingHom-sixteen-plus-zero.flow",
    "examples/verify/math/derived/Monoid-seventeen-plus-zero.flow",
    "examples/verify/math/derived/Ideal-twenty-plus-zero.flow",
    "examples/verify/math/derived/Subgroup-identity-untrigesim.flow",
    "examples/verify/math/derived/RingHom-seventeen-plus-zero.flow",
    "examples/verify/math/derived/Monoid-eighteen-plus-zero.flow",
    "examples/verify/math/derived/Ideal-twenty-one-plus-zero.flow",
    "examples/verify/math/derived/Subgroup-identity-duotrigesim.flow",
    "examples/verify/math/derived/RingHom-eighteen-plus-zero.flow",
    "examples/verify/math/derived/Monoid-nineteen-plus-zero.flow",
    "examples/verify/math/derived/Ideal-twenty-two-plus-zero.flow",
]

GEOMETRY_DERIVED_BUNDLE: List[str] = [
    "examples/verify/geometry/circle-radii-equal.flow",
    "examples/verify/geometry/parallel-lines-alternate.flow",
    "examples/verify/geometry/triangle-congruence-sas.flow",
    "examples/verify/geometry/vertical-angles.flow",
    "examples/verify/geometry/isosceles-base-angles.flow",
    "examples/verify/geometry/triangle-angle-sum.flow",
    "examples/verify/geometry/pythagoras.flow",
    "examples/verify/geometry/inscribed-angle-half-central.flow",
    "examples/verify/geometry/thales-right-angle.flow",
    "examples/verify/geometry/exterior-angle-remote-sum.flow",
    "examples/verify/geometry/vertical-angles-supplementary.flow",
    "examples/verify/geometry/inscribed-thales-witness.flow",
    "examples/verify/geometry/right-triangle-legs-shorter.flow",
    "examples/verify/geometry/triangle-two-angles-determine-third.flow",
    "examples/verify/geometry/triangle-exterior-plus-adjacent-two-right.flow",
    "examples/verify/geometry/isosceles-equal-angles-imply-equal-sides.flow",
    "examples/verify/geometry/parallel-corresponding-equal.flow",
    "examples/verify/geometry/right-triangle-acute-angles-sum.flow",
    "examples/verify/geometry/right-triangle-both-legs-shorter.flow",
    "examples/verify/geometry/inscribed-same-arc-equal.flow",
    "examples/verify/geometry/circle-chord-centre-isosceles.flow",
    "examples/verify/geometry/vertical-angles-form-pair.flow",
    "examples/verify/geometry/pythagoras-345-witness.flow",
    "examples/verify/geometry/thales-central-angle-double.flow",
    "examples/verify/geometry/isosceles-base-median-perpendicular.flow",
    "examples/verify/geometry/triangle-each-angle-less-two-right.flow",
    "examples/verify/geometry/parallel-co-interior-sum-two-right.flow",
    "examples/verify/geometry/isosceles-apex-bisects-base.flow",
    "examples/verify/geometry/isosceles-equal-sides-imply-base-angles.flow",
    "examples/verify/geometry/right-triangle-leg-squared-less-hypotenuse.flow",
    "examples/verify/geometry/inscribed-angle-less-one-right.flow",
    "examples/verify/geometry/thales-inscribed-half-central.flow",
    "examples/verify/geometry/triangle-exterior-greater-remote.flow",
    "examples/verify/geometry/circle-radii-to-same-point-equal.flow",
    "examples/verify/geometry/parallel-alternate-implies-corresponding.flow",
    "examples/verify/geometry/pythagoras-512-witness.flow",
    "examples/verify/geometry/vertical-supplementary-implies-equal.flow",
    "examples/verify/geometry/triangle-angle-sum-minus-one.flow",
    "examples/verify/geometry/parallel-z-angles-equal.flow",
    "examples/verify/geometry/isosceles-reflection-symmetric.flow",
    "examples/verify/geometry/right-triangle-both-acute.flow",
    "examples/verify/geometry/inscribed-half-central-positive.flow",
    "examples/verify/geometry/thales-unique-right-on-diameter.flow",
    "examples/verify/geometry/triangle-exterior-not-less-remote-sum.flow",
    "examples/verify/geometry/circle-diameter-twice-radius.flow",
    "examples/verify/geometry/parallel-co-interior-less-two-right.flow",
    "examples/verify/geometry/pythagoras-6810-witness.flow",
    "examples/verify/geometry/vertical-four-angle-cycle.flow",
    "examples/verify/geometry/triangle-interior-sum-positive.flow",
    "examples/verify/geometry/triangle-third-angle-positive.flow",
    "examples/verify/geometry/parallel-f-angles-equal.flow",
    "examples/verify/geometry/isosceles-apex-median-bisects.flow",
    "examples/verify/geometry/right-triangle-squares-positive.flow",
    "examples/verify/geometry/inscribed-semicircle-right-witness.flow",
    "examples/verify/geometry/thales-central-half-inscribed.flow",
    "examples/verify/geometry/triangle-exterior-strictly-greater.flow",
    "examples/verify/geometry/circle-radius-positive.flow",
    "examples/verify/geometry/parallel-transversal-angle-cycle.flow",
    "examples/verify/geometry/pythagoras-91215-witness.flow",
    "examples/verify/geometry/vertical-opposite-equal-pair.flow",
    "examples/verify/geometry/triangle-exterior-equals-remote-plus-adjacent.flow",
    "examples/verify/geometry/triangle-first-angle-positive.flow",
    "examples/verify/geometry/parallel-alternate-z-chain.flow",
    "examples/verify/geometry/isosceles-sides-symmetric.flow",
    "examples/verify/geometry/right-triangle-hypotenuse-square-positive.flow",
    "examples/verify/geometry/inscribed-less-than-central.flow",
    "examples/verify/geometry/thales-right-implies-diameter.flow",
    "examples/verify/geometry/triangle-exterior-remote-strict.flow",
    "examples/verify/geometry/circle-diameter-positive.flow",
    "examples/verify/geometry/parallel-corresponding-f-chain.flow",
    "examples/verify/geometry/pythagoras-81517-witness.flow",
    "examples/verify/geometry/vertical-adjacent-supplement-pair.flow",
    "examples/verify/geometry/triangle-angle-difference-positive.flow",
    "examples/verify/geometry/triangle-second-angle-positive.flow",
    "examples/verify/geometry/parallel-interior-alternate-chain.flow",
    "examples/verify/geometry/isosceles-base-angles-symmetric.flow",
    "examples/verify/geometry/right-triangle-sum-squares-hypotenuse.flow",
    "examples/verify/geometry/inscribed-on-minor-arc-acute.flow",
    "examples/verify/geometry/thales-diameter-central-two-right.flow",
    "examples/verify/geometry/triangle-exterior-sum-strict.flow",
    "examples/verify/geometry/circle-two-radii-sum-diameter.flow",
    "examples/verify/geometry/parallel-full-transversal-chain.flow",
    "examples/verify/geometry/pythagoras-72425-witness.flow",
    "examples/verify/geometry/vertical-four-supplement-cycle.flow",
    "examples/verify/geometry/triangle-angles-less-one-full-turn.flow",
    "examples/verify/geometry/triangle-all-angles-positive.flow",
    "examples/verify/geometry/parallel-co-interior-chain.flow",
    "examples/verify/geometry/isosceles-apex-perpendicular-base.flow",
    "examples/verify/geometry/right-triangle-leg-sum-less-hypotenuse.flow",
    "examples/verify/geometry/inscribed-major-arc-obtuse.flow",
    "examples/verify/geometry/thales-semicircle-unique-right.flow",
    "examples/verify/geometry/triangle-exterior-transitive-greater.flow",
    "examples/verify/geometry/circle-radius-half-diameter.flow",
    "examples/verify/geometry/parallel-transversal-complete-chain.flow",
    "examples/verify/geometry/pythagoras-202121-witness.flow",
    "examples/verify/geometry/vertical-opposite-supplement.flow",
    "examples/verify/geometry/triangle-sum-equals-half-turn.flow",
    "examples/verify/geometry/triangle-angle-b-positive.flow",
    "examples/verify/geometry/parallel-supplement-co-interior.flow",
    "examples/verify/geometry/isosceles-reflection-fixes-apex.flow",
    "examples/verify/geometry/right-triangle-c-squared-equals-sum.flow",
    "examples/verify/geometry/inscribed-central-ratio-half.flow",
    "examples/verify/geometry/thales-inscribed-on-semicircle.flow",
    "examples/verify/geometry/triangle-exterior-min-remote.flow",
    "examples/verify/geometry/circle-diameter-twice-radius-alt.flow",
    "examples/verify/geometry/parallel-angle-chain-closure.flow",
    "examples/verify/geometry/pythagoras-91240-witness.flow",
    "examples/verify/geometry/vertical-equal-opposite-pair-alt.flow",
    "examples/verify/geometry/triangle-half-turn-witness.flow",
    "examples/verify/geometry/triangle-angle-c-positive.flow",
    "examples/verify/geometry/parallel-f-z-chain.flow",
    "examples/verify/geometry/isosceles-median-equals-bisector.flow",
    "examples/verify/geometry/right-triangle-b-squared-positive.flow",
    "examples/verify/geometry/inscribed-on-diameter-right-alt.flow",
    "examples/verify/geometry/thales-central-inscribed-witness.flow",
    "examples/verify/geometry/triangle-exterior-max-remote.flow",
    "examples/verify/geometry/circle-radius-half-diameter-alt.flow",
    "examples/verify/geometry/parallel-chain-alternate-f-equal.flow",
    "examples/verify/geometry/pythagoras-121635-witness.flow",
    "examples/verify/geometry/vertical-alpha-beta-supplement.flow",
    "examples/verify/geometry/triangle-three-angles-half-turn.flow",
    "examples/verify/geometry/triangle-all-angles-positive-chain.flow",
    "examples/verify/geometry/parallel-corresponding-z-chain.flow",
    "examples/verify/geometry/isosceles-bisector-perpendicular-base.flow",
    "examples/verify/geometry/right-triangle-a-squared-positive.flow",
    "examples/verify/geometry/inscribed-on-semicircle-acute-alt.flow",
    "examples/verify/geometry/thales-inscribed-central-chain.flow",
    "examples/verify/geometry/triangle-exterior-strict-remote.flow",
    "examples/verify/geometry/circle-chord-equal-radii.flow",
    "examples/verify/geometry/parallel-alternate-corresponding-equal.flow",
    "examples/verify/geometry/pythagoras-123537-witness.flow",
    "examples/verify/geometry/vertical-gamma-delta-supplement.flow",
    "examples/verify/geometry/triangle-pair-angles-less-half-turn.flow",
]

ANALYSIS_APPENDIX: List[str] = [
    "examples/verify/analysis/sine-derivatives-at-zero.flow",
    "examples/verify/geometry/taylor-sin-maclaurin.flow",
]


def _euclid_book_i_bundle() -> List[str]:
    manifest = Path(__file__).resolve().parents[2] / "examples" / "verify" / "euclid" / "book-i" / "MANIFEST.txt"
    if manifest.is_file():
        return [line.strip() for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    book_i = Path(__file__).resolve().parents[2] / "examples" / "verify" / "euclid" / "book-i"
    return sorted(
        f"examples/verify/euclid/book-i/{p.name}"
        for p in book_i.glob("prop-*.flow")
    )


EUCLID_BOOK_I_BUNDLE: List[str] = _euclid_book_i_bundle()


def _euclid_book_ii_bundle() -> List[str]:
    manifest = Path(__file__).resolve().parents[2] / "examples" / "verify" / "euclid" / "book-ii" / "MANIFEST.txt"
    if manifest.is_file():
        return [line.strip() for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    book_ii = Path(__file__).resolve().parents[2] / "examples" / "verify" / "euclid" / "book-ii"
    return sorted(
        f"examples/verify/euclid/book-ii/{p.name}"
        for p in book_ii.glob("prop-*.flow")
    )


EUCLID_BOOK_II_BUNDLE: List[str] = _euclid_book_ii_bundle()


def _euclid_book_iii_bundle() -> List[str]:
    manifest = Path(__file__).resolve().parents[2] / "examples" / "verify" / "euclid" / "book-iii" / "MANIFEST.txt"
    if manifest.is_file():
        return [line.strip() for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    book_iii = Path(__file__).resolve().parents[2] / "examples" / "verify" / "euclid" / "book-iii"
    return sorted(
        f"examples/verify/euclid/book-iii/{p.name}"
        for p in book_iii.glob("prop-*.flow")
    )


EUCLID_BOOK_III_BUNDLE: List[str] = _euclid_book_iii_bundle()


def _euclid_book_iv_bundle() -> List[str]:
    manifest = Path(__file__).resolve().parents[2] / "examples" / "verify" / "euclid" / "book-iv" / "MANIFEST.txt"
    if manifest.is_file():
        return [line.strip() for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    book_iv = Path(__file__).resolve().parents[2] / "examples" / "verify" / "euclid" / "book-iv"
    return sorted(
        f"examples/verify/euclid/book-iv/{p.name}"
        for p in book_iv.glob("prop-*.flow")
    )


EUCLID_BOOK_IV_BUNDLE: List[str] = _euclid_book_iv_bundle()


def _euclid_book_v_bundle() -> List[str]:
    manifest = Path(__file__).resolve().parents[2] / "examples" / "verify" / "euclid" / "book-v" / "MANIFEST.txt"
    if manifest.is_file():
        return [line.strip() for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    book_v = Path(__file__).resolve().parents[2] / "examples" / "verify" / "euclid" / "book-v"
    return sorted(
        f"examples/verify/euclid/book-v/{p.name}"
        for p in book_v.glob("prop-*.flow")
    )


EUCLID_BOOK_V_BUNDLE: List[str] = _euclid_book_v_bundle()


def _euclid_book_vi_bundle() -> List[str]:
    manifest = Path(__file__).resolve().parents[2] / "examples" / "verify" / "euclid" / "book-vi" / "MANIFEST.txt"
    if manifest.is_file():
        return [line.strip() for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    book_vi = Path(__file__).resolve().parents[2] / "examples" / "verify" / "euclid" / "book-vi"
    return sorted(
        f"examples/verify/euclid/book-vi/{p.name}"
        for p in book_vi.glob("prop-*.flow")
    )


EUCLID_BOOK_VI_BUNDLE: List[str] = _euclid_book_vi_bundle()

# Unified proof book — continuous numbering.
BOOK_PARTS: List[Tuple[str, List[str]]] = [
    ("Part I — Logic and Arithmetic", BASIC_PROOF_BUNDLE),
    ("Part II — Data Structures", DATA_PROOF_BUNDLE),
    ("Book I — Euclid's Elements", EUCLID_BOOK_I_BUNDLE),
    ("Book II — Euclid's Elements", EUCLID_BOOK_II_BUNDLE),
    ("Book III — Euclid's Elements", EUCLID_BOOK_III_BUNDLE),
    ("Book IV — Euclid's Elements", EUCLID_BOOK_IV_BUNDLE),
    ("Book V — Euclid's Elements", EUCLID_BOOK_V_BUNDLE),
    ("Book VI — Euclid's Elements", EUCLID_BOOK_VI_BUNDLE),
    ("Geometry — Derived Lemmas", GEOMETRY_DERIVED_BUNDLE),
    ("Part III — Algebra", ALGEBRA_PROOF_BUNDLE),
    ("Appendix — Analysis", ANALYSIS_APPENDIX),
]

FLOW_PROOF_BOOK: List[str] = (
    BASIC_PROOF_BUNDLE
    + DATA_PROOF_BUNDLE
    + EUCLID_BOOK_I_BUNDLE
    + EUCLID_BOOK_II_BUNDLE
    + EUCLID_BOOK_III_BUNDLE
    + EUCLID_BOOK_IV_BUNDLE
    + EUCLID_BOOK_V_BUNDLE
    + EUCLID_BOOK_VI_BUNDLE
    + GEOMETRY_DERIVED_BUNDLE
    + ALGEBRA_PROOF_BUNDLE
    + ANALYSIS_APPENDIX
)

# Backward-compatible alias for geometry bundle loaders/tests.
GEOMETRY_PROOF_BUNDLE: List[str] = EUCLID_BOOK_I_BUNDLE


META_LINE = re.compile(r"^\s*#\s*@(?P<key>[a-z-]+)\s+(?P<value>.+?)\s*$", re.I)
THEOREM_HEADER = re.compile(
    r"theorem\s+"
    r"(?P<path>«[^»]+»\s*«[^»]+»\s*«[^»]+»|[^\s(]+)"
    r"\s*\((?P<params>[^)]*)\)\s*\{",
    re.MULTILINE,
)
ASSUME_LINE = re.compile(r"assume\s+(.+)")
THEREFORE_LINE = re.compile(r"therefore\s+(.+)")
LET_LINE = re.compile(r"let\s+(?:mut\s+)?(\w+)\s*=\s*(.+)")
IF_LINE = re.compile(r"^\s*\}?\s*if\s+(.+?)\s*\{")
ELIF_LINE = re.compile(r"^\s*\}?\s*elif\s+(.+?)\s*\{")
ELSE_LINE = re.compile(r"^\s*\}?\s*else\s*\{")


@dataclass
class TheoremMeta:
    means: str = ""
    from_source: str = ""
    tier: str = ""
    needs: List[str] = field(default_factory=list)
    used_by: List[str] = field(default_factory=list)
    diagram: str = ""
    diagram_script: str = ""


@dataclass
class ProofStep:
    kind: str
    text: str
    detail: str = ""


@dataclass
class TheoremDoc:
    claim_path: str
    params: str
    meta: TheoremMeta
    steps: List[ProofStep]
    claim_expr: str = ""
    file_path: str = ""
    number: int = 0
    diagram_svg: str = ""
    diagram_tex: str = ""


@dataclass
class ModuleDoc:
    module: str = ""
    means: str = ""
    from_source: str = ""
    tier: str = ""
    theorems: List[TheoremDoc] = field(default_factory=list)
    file_path: str = ""


@dataclass
class BookPart:
    """One division of the unified proof book."""

    title: str
    docs: List[ModuleDoc] = field(default_factory=list)


@dataclass
class TheoremCatalogEntry:
    """Global index entry for cross-theorem references."""

    number: int
    tier: str
    title: str
    claim_path: str
    label: str


@dataclass
class TutorialLine:
    """One numbered line in a textbook-style proof."""

    number: int
    english: str
    math_latex: Optional[str] = None
    is_goal: bool = False
    refs: List[int] = field(default_factory=list)
    substitutions: List[SubstitutionBox] = field(default_factory=list)
    is_premise: bool = False


_CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"


def _circled(n: int) -> str:
    if 1 <= n <= len(_CIRCLED):
        return _CIRCLED[n - 1]
    return f"({n})"


def _step_label_latex(n: int) -> str:
    return rf"\textbf{{{n}.}}"


def _fmt_refs(nums: List[int]) -> str:
    """Format step numbers for cross-reference."""
    unique = sorted(set(nums))
    if not unique:
        return ""
    labels = [f"step {n}" for n in unique]
    if len(labels) == 1:
        return labels[0]
    if len(labels) == 2:
        return f"{labels[0]} and {labels[1]}"
    return ", ".join(labels[:-1]) + f", and {labels[-1]}"


def _theorem_ref_plain(entry: TheoremCatalogEntry) -> str:
    return f"{tier_label(entry.tier)} {entry.number}"


def _theorem_ref_latex(entry: TheoremCatalogEntry) -> str:
    return (
        rf"\hyperref[thm:{entry.label}]{{{tier_label(entry.tier)} {entry.number}}}"
    )


def build_theorem_catalog_from_docs(docs: List[ModuleDoc]) -> Dict[str, TheoremCatalogEntry]:
    catalog: Dict[str, TheoremCatalogEntry] = {}
    for doc in docs:
        for thm in doc.theorems:
            catalog[thm.claim_path] = TheoremCatalogEntry(
                number=thm.number,
                tier=thm.meta.tier or "derived",
                title=_facet_title(thm.claim_path, thm.meta),
                claim_path=thm.claim_path,
                label=_slug_label(thm.claim_path),
            )
    return catalog


def build_theorem_catalog_from_parts(parts: List[BookPart]) -> Dict[str, TheoremCatalogEntry]:
    docs: List[ModuleDoc] = []
    for part in parts:
        docs.extend(part.docs)
    return build_theorem_catalog_from_docs(docs)


def _lookup_theorem_ref(
    ref_path: str,
    catalog: Optional[Dict[str, TheoremCatalogEntry]],
) -> str:
    if catalog and ref_path in catalog:
        return _theorem_ref_plain(catalog[ref_path])
    return ""


def _format_premise_refs(
    nums: List[int],
    assume_meta: Dict[int, Tuple[str, str]],
    catalog: Optional[Dict[str, TheoremCatalogEntry]],
    *,
    current_claim: str = "",
) -> str:
    """Prefer prerequisite theorem numbers over in-proof step circles."""
    labels: List[str] = []
    for n in sorted(set(nums)):
        if n in assume_meta:
            ref_path, _ = assume_meta[n]
            if ref_path != current_claim:
                thm_ref = _lookup_theorem_ref(ref_path, catalog)
                if thm_ref:
                    labels.append(thm_ref)
                    continue
        labels.append(f"step {n}")
    if not labels:
        return ""
    if len(labels) == 1:
        return labels[0]
    if len(labels) == 2:
        return f"{labels[0]} and {labels[1]}"
    return ", ".join(labels[:-1]) + f", and {labels[-1]}"


def _from_refs(nums: List[int]) -> str:
    if not nums:
        return ""
    return f"From {_fmt_refs(nums)}, "


def _under_refs(nums: List[int]) -> str:
    if not nums:
        return ""
    if len(nums) == 1:
        return f"Under the supposition in step {nums[0]}, "
    return f"Under the suppositions in {_fmt_refs(nums)}, "


def diagram_markdown_embed(svg_filename: str) -> List[str]:
    return [
        "**Figure.**",
        "",
        f"![{svg_filename}]({svg_filename})",
        "",
    ]


def _slug_label(path: str) -> str:
    addr = try_parse_claim_address(path)
    if addr:
        return addr.slug.replace(".", "-")
    return (
        path.replace("/", "-")
        .replace("+", "plus")
        .replace("*", "star")
        .replace("|", "or")
        .replace(".", "-")
        .replace("=", "eq")
        .replace("«", "")
        .replace("»", "")
        .replace(" ", "-")
    )


def _parse_meta_block(lines: List[str]) -> Tuple[Dict[str, str], int]:
    meta: Dict[str, str] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        m = META_LINE.match(line)
        if not m:
            break
        key = m.group("key").lower().replace("-", "_")
        if key == "from":
            key = "from_source"
        meta[key] = m.group("value").strip()
        i += 1
    return meta, i


def _meta_from_dict(d: Dict[str, str]) -> TheoremMeta:
    needs = [s.strip() for s in d.get("needs", "").split(",") if s.strip()]
    used_by = [s.strip() for s in d.get("used_by", "").split(",") if s.strip()]
    return TheoremMeta(
        means=d.get("means", ""),
        from_source=d.get("from_source", ""),
        tier=d.get("tier", ""),
        needs=needs,
        used_by=used_by,
        diagram=d.get("diagram", ""),
        diagram_script=d.get("diagram_script", ""),
    )


def _extract_brace_body(text: str, open_index: int) -> Tuple[str, int]:
    depth = 0
    i = open_index
    while i < len(text):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[open_index + 1 : i], i + 1
        i += 1
    return text[open_index + 1 :], len(text)


def _parse_steps(body: str) -> Tuple[List[ProofStep], str]:
    steps: List[ProofStep] = []
    claim = ""
    lines = [ln.strip() for ln in body.splitlines() if ln.strip() and not ln.strip().startswith("#")]

    i = 0
    while i < len(lines):
        line = lines[i]

        m = IF_LINE.match(line)
        if m:
            steps.append(ProofStep("if", m.group(1).strip(), m.group(1)))
            i += 1
            continue

        m = ELIF_LINE.match(line)
        if m:
            steps.append(ProofStep("case", f"case {m.group(1).strip()}", m.group(1)))
            i += 1
            continue

        if ELSE_LINE.match(line):
            steps.append(ProofStep("case", "inductive step", "else"))
            i += 1
            continue

        m = ASSUME_LINE.match(line)
        if m:
            steps.append(ProofStep("assume", m.group(1).strip()))
            i += 1
            continue

        m = THEREFORE_LINE.match(line)
        if m:
            expr = m.group(1).strip()
            steps.append(ProofStep("therefore", expr))
            claim = expr.split(" by ")[0].strip()
            i += 1
            continue

        m = LET_LINE.match(line)
        if m:
            steps.append(ProofStep("let", f"{m.group(1)} = {m.group(2).strip()}"))
            i += 1
            continue

        i += 1

    return steps, claim


def flow_expr_to_english(expr: str) -> str:
    """Readable mathematics — no type abbreviations or code syntax."""
    return flow_expr_to_mathematical_english(expr)


def _claim_path_phrase(path: str) -> str:
    addr = try_parse_claim_address(path)
    if addr:
        return address_phrase(addr)
    return path


def _natural_claim_sentence(thm: TheoremDoc) -> str:
    if thm.meta.means:
        return thm.meta.means.rstrip(".")
    if thm.claim_expr:
        gloss = {
            "0 + m = m": "Adding zero on the left gives you the same number.",
            "n + succ(m) = succ(n + m)": "Adding one more on the right just steps the sum by one.",
            "n + 0 = n": "Adding zero on the right gives you the same number.",
            "a + b = b + a": "You can swap the order when you add.",
            "x = x": "Anything is always equal to itself.",
            "a or b = b or a": "Order doesn't matter for or — either way you get the same truth.",
            "sq >= 0": "Squaring never gives you a negative number.",
        }
        key = flow_expr_to_english(thm.claim_expr)
        key = re.sub(r"\s+", " ", key)
        return gloss.get(key, f"We're showing that {key}.")
    return "We're showing this claim holds."


def _build_tier_index(theorems: List[TheoremDoc]) -> Dict[str, str]:
    return {thm.claim_path: thm.meta.tier for thm in theorems if thm.meta.tier}


def _global_tier_index() -> Dict[str, str]:
    """Cross-file tiers so assumes respect definitional vs derived boundaries."""
    try:
        from flow.know import _default_search_roots, scan_claim_index

        root = Path(__file__).resolve().parents[2]
        entries = scan_claim_index(_default_search_roots(str(root)))
        return {
            entry.theorem.claim_path: entry.theorem.meta.tier
            for entry in entries.values()
            if entry.theorem.meta.tier
        }
    except Exception:
        return {}


def _merged_tier_index(doc: ModuleDoc) -> Dict[str, str]:
    merged = _global_tier_index()
    merged.update(_build_tier_index(doc.theorems))
    return merged


def _natural_assume(
    step_text: str,
    thm: TheoremDoc,
    *,
    tier_index: Optional[Dict[str, str]] = None,
    theorem_catalog: Optional[Dict[str, TheoremCatalogEntry]] = None,
    context_refs: Optional[List[int]] = None,
) -> str:
    ref = step_text.split("(")[0].strip()
    phrase = _claim_path_phrase(ref)
    args = ""
    if "(" in step_text:
        args = step_text[step_text.index("(") + 1 : step_text.rindex(")")].strip()

    if ref == thm.claim_path:
        var = args.split(",")[0].strip() if args else (
            thm.params.split(":")[0].strip() if thm.params else "n"
        )
        lead = _under_refs(context_refs or [])
        body = assume_premise(
            ref,
            phrase=phrase,
            is_induction_hypothesis=True,
            hyp_var=var,
        )
        if lead:
            return lead + body[0].lower() + body[1:]
        return body

    ref_tier = (tier_index or {}).get(ref, "derived")
    return assume_premise(
        ref,
        phrase=phrase,
        args=args,
        ref_tier=ref_tier,
        theorem_ref=_lookup_theorem_ref(ref, theorem_catalog),
    )


def _natural_let(step_text: str, *, context_refs: Optional[List[int]] = None) -> str:
    m = re.match(r"(\w+)\s*=\s*pred\((\w+)\)", step_text.strip())
    lead = _under_refs(context_refs or [])
    if m:
        body = f"let {m.group(1)} denote the predecessor of {m.group(2)}."
    elif "pred(n)" in step_text:
        body = "let k denote the predecessor of n."
    else:
        body = f"let {step_text}."
    if lead:
        return lead + body
    return body[0].upper() + body[1:]


GEOMETRY_DIRECT: Dict[str, str] = {
    "«Geometry» «intersecting lines» «vertical angles are equal»": (
        "α and β form a straight angle, and so do β and α′, hence α equals α′"
    ),
    "«Geometry» «right triangle» «the Pythagorean relation holds»": (
        "the square on the hypotenuse decomposes into the two squares on the legs"
    ),
}


GEOMETRY_DEDUCTION: Dict[Tuple[str, str], str] = {
    (
        "«Geometry» «isosceles triangle» «base angles are equal»",
        "«Geometry» «triangle congruence» «side-angle-side implies congruence»",
    ): "the two halves of the isosceles triangle are congruent by SAS, so the base angles match",
    (
        "«Geometry» «triangle» «interior angles sum to two right angles»",
        "«Geometry» «parallel lines» «alternate angles are equal»",
    ): "a line through the apex parallel to the base makes alternate angles with the sides, so the three interior angles line up on a straight line",
    (
        "«Geometry» «circle» «Thales right angle in semicircle»",
        "«Geometry» «triangle» «interior angles sum to two right angles»",
    ): "triangle ABC has two equal base angles at A and B because OA = OB, so the angle at C is the remaining half of two right angles",
    (
        "«Geometry» «circle» «inscribed angle is half the central angle»",
        "«Geometry» «circle» «radii from the centre are equal»",
    ): "the two radii OA and OB form an isosceles triangle, so the inscribed angle at P is half the central angle at O",
    (
        "«Analysis» «Taylor series» «sin equals its Maclaurin series near zero»",
        "«Analysis» «smooth functions» «derivatives of sine are known»",
    ): "the Maclaurin coefficients match the known derivatives of sine at zero, so each partial sum agrees with sin(x) to the next order",
}


def _natural_therefore(
    step_text: str,
    *,
    is_base: bool,
    is_final: bool,
    premise_nums: List[int],
    premise_ref_str: str = "",
    tier: str = "",
    in_case: bool = False,
    case_close_nums: Optional[List[int]] = None,
    claim_path: str = "",
    premise_claims: Optional[List[str]] = None,
) -> str:
    plain = flow_expr_to_english(step_text)
    from_phrase = f"From {premise_ref_str}, " if premise_ref_str else ""

    if not premise_nums:
        if tier == "definition":
            body = f"This follows directly from the definition: {plain}."
        elif tier == "axiom":
            body = f"This holds immediately by the stated axiom: {plain}."
        elif in_case and not is_final:
            body = f"In this case, we can deduce that {plain}."
        elif in_case and is_final:
            body = f"In this case, this implies {plain}."
        elif is_final and claim_path in GEOMETRY_DIRECT:
            body = f"{GEOMETRY_DIRECT[claim_path]}, so {plain}."
        else:
            body = f"We can deduce that {plain}."
        return body + (" Hence proven." if is_final else "")

    if premise_claims and claim_path:
        for prem in premise_claims:
            bridge = GEOMETRY_DEDUCTION.get((claim_path, prem))
            if bridge and is_final and not in_case:
                return f"{from_phrase}{bridge}, so {plain}. Hence proven."
        if (
            is_final
            and not in_case
            and "«Euclid Book I»" in claim_path
            and premise_ref_str
        ):
            return (
                f"{from_phrase}by the chain of results established in Book I "
                f"({premise_ref_str}), we obtain {plain}. Hence proven."
            )

    if is_base:
        base_refs = premise_ref_str or _fmt_refs(premise_nums)
        return (
            f"{from_phrase}we can deduce that {plain}. "
            f"This establishes the base case (see {base_refs}). Hence proven."
        )
    if is_final and in_case and case_close_nums:
        cases = _fmt_refs(case_close_nums)
        return (
            f"{from_phrase}this implies {plain}. "
            f"Together with the other cases ({cases}), the goal is discharged. Hence proven."
        )
    if is_final:
        return f"{from_phrase}this implies {plain}. Hence proven."
    if in_case:
        return f"{from_phrase}this implies {plain} in this case."
    return f"{from_phrase}we can deduce that {plain}."


def _claim_math_latex(thm: TheoremDoc) -> str:
    claim = flow_expr_to_latex(thm.claim_expr or thm.meta.means)
    if thm.params:
        from flow.math_prose import TYPE_LATEX

        quants: List[str] = []
        for chunk in thm.params.split(","):
            chunk = chunk.strip()
            if not chunk or ":" not in chunk:
                continue
            var, dom = chunk.split(":", 1)
            var = var.strip()
            dom = dom.strip()
            dom_tex = TYPE_LATEX.get(dom, _latex_escape(dom))
            quants.append(rf"\forall {var} \in {dom_tex}")
        if quants:
            return " ".join(quants) + r"\quad " + claim
    return claim


def build_tutorial_lines(
    thm: TheoremDoc,
    *,
    tier_index: Optional[Dict[str, str]] = None,
    theorem_catalog: Optional[Dict[str, TheoremCatalogEntry]] = None,
) -> List[TutorialLine]:
    """Line-by-line textbook proof with circled step numbers."""
    lines: List[TutorialLine] = []
    step_num = 1

    lines.append(
        TutorialLine(
            number=0,
            english=_natural_claim_sentence(thm),
            math_latex=_claim_math_latex(thm),
            is_goal=True,
        )
    )

    claim = try_parse_claim_address(thm.claim_path)
    if claim and thm.meta.tier:
        lines.append(
            TutorialLine(step_num, tier_opening_plain(thm.meta.tier, claim))
        )
        step_num += 1

    induction = _is_induction_proof(thm)
    case_analysis = _is_case_analysis(thm)
    if case_analysis:
        lines.append(
            TutorialLine(
                step_num,
                "We split into exhaustive cases — the claim must hold in each one.",
            )
        )
        step_num += 1

    case_num = 0
    if induction:
        var = thm.params.split(":")[0].strip() if thm.params else "n"
        lines.append(
            TutorialLine(
                step_num,
                f"We proceed by induction on {var}: first the base case, "
                f"then the inductive step.",
            )
        )
        step_num += 1

    in_base = induction
    seen_else = False
    pending_premise_nums: List[int] = []
    therefore_count = 0
    total_therefore = sum(1 for s in thm.steps if s.kind == "therefore")
    current_case_step: Optional[int] = None
    case_open_steps: List[int] = []
    case_close_steps: List[int] = []
    inductive_step_num: Optional[int] = None
    base_case_step_num: Optional[int] = None
    split_step_num: Optional[int] = None
    assume_meta: Dict[int, Tuple[str, str]] = {}

    if case_analysis and lines and not lines[-1].is_goal:
        split_step_num = lines[-1].number

    for pstep in thm.steps:
        if pstep.kind == "if" and case_analysis:
            case_num += 1
            cond = mathematical_case_condition(pstep.detail)
            refs = [split_step_num] if split_step_num else []
            lines.append(
                TutorialLine(
                    step_num,
                    f"Case {case_num} (see {_fmt_refs(refs)}): suppose {cond}."
                    if refs
                    else f"Case {case_num}: suppose {cond}.",
                    refs=refs,
                )
            )
            current_case_step = step_num
            case_open_steps.append(step_num)
            pending_premise_nums = []
            step_num += 1
        elif pstep.kind == "if" and induction:
            case = mathematical_case_condition(pstep.detail)
            lines.append(
                TutorialLine(
                    step_num,
                    f"Consider the base case in which {case}.",
                )
            )
            base_case_step_num = step_num
            current_case_step = step_num
            pending_premise_nums = []
            step_num += 1
            in_base = True
        elif pstep.kind == "case" and case_analysis and not induction:
            pending_premise_nums = []
            if pstep.detail == "else":
                case_num += 1
                refs = [split_step_num] if split_step_num else []
                lines.append(
                    TutorialLine(
                        step_num,
                        f"Case {case_num} (see {_fmt_refs(refs)}): neither disjunct holds.",
                        refs=refs,
                    )
                )
            else:
                case_num += 1
                cond = mathematical_case_condition(
                    pstep.detail.replace("case ", "")
                )
                refs = [split_step_num] if split_step_num else []
                lines.append(
                    TutorialLine(
                        step_num,
                        f"Case {case_num} (see {_fmt_refs(refs)}): suppose {cond}.",
                        refs=refs,
                    )
                )
            current_case_step = step_num
            case_open_steps.append(step_num)
            step_num += 1
        elif pstep.kind == "case" and pstep.detail == "else" and induction:
            if not seen_else:
                lines.append(
                    TutorialLine(
                        step_num,
                        "For the inductive step, suppose the claim holds for all smaller values.",
                    )
                )
                inductive_step_num = step_num
                current_case_step = step_num
                pending_premise_nums = []
                step_num += 1
                seen_else = True
                in_base = False
        elif pstep.kind == "assume":
            ref = pstep.text.split("(")[0].strip()
            args = ""
            if "(" in pstep.text:
                args = pstep.text[pstep.text.index("(") + 1 : pstep.text.rindex(")")].strip()
            ctx = (
                [inductive_step_num]
                if ref == thm.claim_path and inductive_step_num
                else (
                    [base_case_step_num]
                    if in_base and base_case_step_num and ref != thm.claim_path
                    else []
                )
            )
            premise_latex = instantiate_premise_latex(
                ref,
                args,
                claim_expr=thm.claim_expr if ref == thm.claim_path else "",
                params=thm.params if ref == thm.claim_path else "",
            )
            lines.append(
                TutorialLine(
                    step_num,
                    _natural_assume(
                        pstep.text,
                        thm,
                        tier_index=tier_index,
                        theorem_catalog=theorem_catalog,
                        context_refs=ctx,
                    ),
                    math_latex=premise_latex,
                    refs=ctx,
                    is_premise=True,
                )
            )
            assume_meta[step_num] = (ref, args)
            pending_premise_nums.append(step_num)
            step_num += 1
        elif pstep.kind == "let":
            ctx = [inductive_step_num] if inductive_step_num and not in_base else []
            lines.append(
                TutorialLine(
                    step_num,
                    _natural_let(pstep.text, context_refs=ctx),
                    refs=ctx,
                )
            )
            pending_premise_nums.append(step_num)
            step_num += 1
        elif pstep.kind == "therefore":
            therefore_count += 1
            premise_nums: List[int] = []
            if current_case_step is not None:
                premise_nums.append(current_case_step)
            premise_nums.extend(pending_premise_nums)
            is_final = therefore_count == total_therefore
            premise_ref_str = _format_premise_refs(
                premise_nums,
                assume_meta,
                theorem_catalog,
                current_claim=thm.claim_path,
            )
            premise_claims = [
                assume_meta[pn][0]
                for pn in premise_nums
                if pn in assume_meta and assume_meta[pn][0] != thm.claim_path
            ]
            english = _natural_therefore(
                pstep.text,
                is_base=in_base and induction,
                is_final=is_final,
                premise_nums=premise_nums,
                premise_ref_str=premise_ref_str,
                tier=thm.meta.tier,
                in_case=case_analysis,
                case_close_nums=case_open_steps if is_final and case_analysis else None,
                claim_path=thm.claim_path,
                premise_claims=premise_claims,
            )
            ref_steps = [
                (pn, assume_meta[pn][0], assume_meta[pn][1])
                for pn in premise_nums
                if pn in assume_meta
            ]
            source_labels = {
                pn: _lookup_theorem_ref(assume_meta[pn][0], theorem_catalog)
                for pn in premise_nums
                if pn in assume_meta
                and assume_meta[pn][0] != thm.claim_path
                and _lookup_theorem_ref(assume_meta[pn][0], theorem_catalog)
            }
            subs = substitution_boxes_for_refs(
                ref_steps,
                claim_expr=thm.claim_expr,
                params=thm.params,
                source_labels=source_labels,
            )
            lines.append(
                TutorialLine(
                    step_num,
                    english,
                    math_latex=flow_expr_to_latex(pstep.text),
                    refs=premise_nums,
                    substitutions=subs,
                )
            )
            if case_analysis:
                case_close_steps.append(step_num)
            step_num += 1
            pending_premise_nums = []

    if step_num == 1 and thm.claim_expr:
        plain = flow_expr_to_english(thm.claim_expr)
        lines.append(
            TutorialLine(
                1,
                f"The claim follows immediately: {plain}. Hence proven.",
                math_latex=flow_expr_to_latex(thm.claim_expr),
            )
        )

    return lines


def _natural_proof_narrative(thm: TheoremDoc) -> List[str]:
    """Legacy string list — one entry per tutorial line."""
    out: List[str] = []
    for tl in build_tutorial_lines(thm):
        if tl.is_goal:
            continue
        out.append(tl.english)
        out.append("")
    return out


def _facet_title(claim_path: str, meta: TheoremMeta) -> str:
    if meta.means:
        first = meta.means.split(".")[0].strip()
        if first.lower().startswith("adding"):
            return first[0].upper() + first[1:]
        return first
    facet = claim_path.split(".")[-1] if "." in claim_path else claim_path
    return facet.replace("-", " ").capitalize()


def parse_proof_file(path: str) -> ModuleDoc:
    text = Path(path).read_text(encoding="utf-8")
    lines = text.splitlines()

    file_meta, _ = _parse_meta_block(lines)
    module_doc = ModuleDoc(
        module=file_meta.get("module", ""),
        means=file_meta.get("means", ""),
        from_source=file_meta.get("from_source", ""),
        tier=file_meta.get("tier", ""),
        file_path=os.path.abspath(path),
    )

    pos = 0
    while pos < len(text):
        m = THEOREM_HEADER.search(text, pos)
        if not m:
            break

        header_start = m.start()
        pre = text[:header_start]
        block_meta_lines: List[str] = []
        for ln in reversed(pre.splitlines()):
            stripped = ln.strip()
            if META_LINE.match(ln):
                block_meta_lines.insert(0, ln)
            elif stripped == "" or stripped.startswith("import "):
                continue
            elif stripped.startswith("#"):
                continue
            else:
                break

        block_meta, _ = _parse_meta_block(block_meta_lines)
        meta = _meta_from_dict(block_meta)

        body_start = m.end() - 1
        body, end_pos = _extract_brace_body(text, body_start)
        steps, claim = _parse_steps(body)

        module_doc.theorems.append(
            TheoremDoc(
                claim_path=m.group("path").strip(),
                params=m.group("params").strip(),
                meta=meta,
                steps=steps,
                claim_expr=claim,
                file_path=os.path.abspath(path),
            )
        )
        pos = end_pos

    return module_doc


def assign_numbers(docs: List[ModuleDoc], start: int = 1) -> int:
    n = start
    for doc in docs:
        for thm in doc.theorems:
            thm.number = n
            n += 1
    return n


def render_english(doc: ModuleDoc) -> str:
    parts: List[str] = []
    title = doc.module or Path(doc.file_path).stem
    parts.append(f"# {title}")
    parts.append("")

    if doc.means:
        parts.append(f"*{doc.means}*")
        parts.append("")
    if doc.from_source:
        parts.append(f"**Source.** {doc.from_source}")
        parts.append("")

    tier_index = _merged_tier_index(doc)
    for thm in doc.theorems:
        title = _facet_title(thm.claim_path, thm.meta)
        label = tier_label(thm.meta.tier or "derived")
        parts.append(f"## {label} {thm.number} — {title}")
        parts.append("")
        parts.extend(_render_theorem_markdown(thm, tier_index=tier_index))
        parts.append("")

    return "\n".join(parts).rstrip() + "\n"


def _render_theorem_markdown(
    thm: TheoremDoc,
    *,
    tier_index: Optional[Dict[str, str]] = None,
) -> List[str]:
    parts: List[str] = []
    claim = try_parse_claim_address(thm.claim_path)
    if claim:
        parts.append(
            f"**Coordinate.** {addr_coordinate_display(claim)} · "
            f"**{tier_label(thm.meta.tier or 'derived')}**"
        )
        parts.append("")
    if thm.meta.from_source:
        parts.append(f"*Source: {thm.meta.from_source}*")
        parts.append("")
    if thm.meta.needs:
        needs = ", ".join(_claim_path_phrase(n) for n in thm.meta.needs)
        parts.append(f"*Built on: {needs}*")
        parts.append("")

    tutorial = build_tutorial_lines(thm, tier_index=tier_index)
    goal = tutorial[0] if tutorial and tutorial[0].is_goal else None
    if goal:
        parts.append(f"> **Goal.** {goal.english}")
        if goal.math_latex:
            parts.append(">")
            parts.append(f"> $${goal.math_latex}$$")
        parts.append("")

    if thm.diagram_svg:
        parts.extend(diagram_markdown_embed(thm.diagram_svg))

    parts.append("| | **Proof** | | **Math** |")
    parts.append("|:---:|:---|:---:|:---|")

    for tl in tutorial:
        if tl.is_goal:
            continue
        math_cell = f"${tl.math_latex}$" if tl.math_latex else ""
        parts.append(
            f"| {_circled(tl.number)} | {tl.english} | "
            f"{_circled(tl.number) if tl.math_latex else ''} | {math_cell} |"
        )

    trace = _render_trace_legend(tutorial)
    if trace:
        parts.append("")
        parts.extend(trace)

    parts.append("")
    addr = try_parse_claim_address(thm.claim_path)
    parts.append(
        f"`{addr_coordinate_display(addr) if addr else thm.claim_path}`"
    )
    return parts


def _render_trace_legend(tutorial: List[TutorialLine]) -> List[str]:
    """Audit table: each numbered step maps back to the steps it uses."""
    traced = [tl for tl in tutorial if tl.refs and not tl.is_goal]
    if not traced:
        return []
    lines = ["**Trace.** Each step lists the earlier steps it depends on.", ""]
    lines.append("| Step | Uses |")
    lines.append("|:---:|:---|")
    for tl in traced:
        lines.append(f"| {_circled(tl.number)} | {_fmt_refs(tl.refs)} |")
    return lines


def _is_induction_proof(thm: TheoremDoc) -> bool:
    has_if_else = any(s.kind == "if" for s in thm.steps) and any(
        s.kind == "case" and s.detail == "else" for s in thm.steps
    )
    recursive = any(
        s.kind == "assume" and thm.claim_path.split("(")[0] in s.text
        for s in thm.steps
    )
    return has_if_else and recursive


def _is_case_analysis(thm: TheoremDoc) -> bool:
    return any(s.kind == "if" for s in thm.steps) and not _is_induction_proof(thm)


def _english_proof_steps(thm: TheoremDoc) -> List[str]:
    return _natural_proof_narrative(thm)


def _render_math_cell_latex(tl: TutorialLine) -> str:
    """Mathematics column — plain display math only."""
    if not tl.math_latex:
        return "&"
    return rf"& $\displaystyle {tl.math_latex}$"


def _latex_preamble(stem: str, *, title_prefix: str = "Flow Proof Artifact") -> List[str]:
    return [
        r"\documentclass[11pt]{article}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage{textcomp}",
        r"\usepackage[margin=0.75in]{geometry}",
        r"\usepackage{amsmath,amssymb,amsthm}",
        r"\usepackage{array,booktabs}",
        r"\usepackage{hyperref}",
        r"\setlength{\parindent}{0pt}",
        r"\newtheorem{theorem}{Theorem}",
        r"\theoremstyle{definition}",
        r"\newtheorem{definition}{Definition}",
        r"\title{" + _latex_escape(f"{title_prefix}: {stem}") + "}",
        r"\author{Generated by \texttt{flow doc proof}}",
        r"\date{Flow Proof Book}",
        r"\begin{document}",
        r"\maketitle",
    ]


def _needs_lines_latex(thm: TheoremDoc, catalog: Dict[str, TheoremCatalogEntry]) -> List[str]:
    if not thm.meta.needs:
        return []
    parts: List[str] = []
    for need in thm.meta.needs:
        entry = catalog.get(need)
        if entry:
            parts.append(_theorem_ref_latex(entry))
        else:
            parts.append(_latex_escape(_claim_path_phrase(need)))
    return [
        r"\smallskip\noindent\textit{Built on: " + ", ".join(parts) + r"}\par"
    ]


def _render_theorem_latex_block(
    thm: TheoremDoc,
    *,
    tier_index: Optional[Dict[str, str]] = None,
    theorem_catalog: Optional[Dict[str, TheoremCatalogEntry]] = None,
    book_mode: bool = False,
) -> List[str]:
    label = _slug_label(thm.claim_path)
    title = _facet_title(thm.claim_path, thm.meta)
    tier = tier_label(thm.meta.tier or "derived")
    parts: List[str] = []

    parts.append(r"\bigskip")
    header = (
        rf"\noindent{{\large \textbf{{{tier} {thm.number}.}} "
        rf"\textit{{{_latex_escape(title)}}} "
        rf"\hfill {claim_path_latex(thm.claim_path)}}}\par"
    )
    parts.append(header)
    if book_mode:
        parts.append(
            r"\addcontentsline{toc}{subsection}{"
            + _latex_escape(f"{tier} {thm.number} — {title}")
            + "}"
        )
    claim = try_parse_claim_address(thm.claim_path)
    if claim:
        parts.append(
            r"\smallskip\noindent\textit{Coordinate: "
            + addr_coordinate_latex(claim)
            + r"}\par"
        )
    if thm.meta.from_source:
        parts.append(
            r"\smallskip\noindent\textit{Source: "
            + _latex_escape(thm.meta.from_source)
            + r"}\par"
        )
    if theorem_catalog and thm.meta.needs:
        parts.extend(_needs_lines_latex(thm, theorem_catalog))

    tutorial = build_tutorial_lines(
        thm,
        tier_index=tier_index,
        theorem_catalog=theorem_catalog,
    )
    goal = tutorial[0] if tutorial and tutorial[0].is_goal else None

    if goal:
        parts.append(r"\medskip")
        parts.append(
            r"\noindent\textbf{Goal.} " + _latex_escape(goal.english) + r"\par"
        )
        if goal.math_latex:
            parts.append(
                r"\noindent$\displaystyle " + goal.math_latex + r"$\par"
            )

    parts.append(r"\medskip")
    parts.append(r"\noindent")
    parts.append(
        r"\begin{tabular}{@{} >{\raggedright\arraybackslash}p{0.06\textwidth} "
        r">{\raggedright\arraybackslash}p{0.47\textwidth} "
        r">{\raggedleft\arraybackslash}p{0.41\textwidth} @{}}"
    )
    parts.append(r"\textbf{\#} & \textbf{Proof} & \textbf{Mathematics} \\")
    parts.append(r"\midrule")

    for tl in tutorial:
        if tl.is_goal:
            continue
        eng = _latex_escape(tl.english)
        left = _step_label_latex(tl.number) + " & " + eng
        right = _render_math_cell_latex(tl)
        parts.append(left + " " + right + r" \\[0.45em]")

    parts.append(r"\bottomrule")
    parts.append(r"\end{tabular}")
    parts.append(rf"\label{{thm:{label}}}")
    parts.append(r"\par\medskip\hrule")
    return parts


def render_latex(doc: ModuleDoc, *, document_class: str = "article") -> str:
    stem = Path(doc.file_path).stem
    parts = _latex_preamble(stem)

    if doc.means:
        parts.append(_latex_escape(doc.means) + r"\\[0.5em]")
    if doc.from_source:
        parts.append(
            r"\textbf{Source.} " + _latex_escape(doc.from_source) + r"\\[0.5em]"
        )

    tier_index = _merged_tier_index(doc)
    catalog = build_theorem_catalog_from_docs([doc])
    for thm in doc.theorems:
        parts.extend(
            _render_theorem_latex_block(
                thm,
                tier_index=tier_index,
                theorem_catalog=catalog,
            )
        )

    parts.append(r"\end{document}")
    return "\n".join(parts) + "\n"


def _latex_escape(text: str) -> str:
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "·": r"\textperiodcentered{}",
        "«": r"\guillemotleft{}",
        "»": r"\guillemotright{}",
        "α": r"$\alpha$",
        "β": r"$\beta$",
        "γ": r"$\gamma$",
        "′": r"$'$",
    }
    out = text
    for a, b in repl.items():
        out = out.replace(a, b)
    return out


def _latex_escape_params(params: str) -> str:
    return _latex_escape(params).replace(",", r",\;")


def _attach_geometry_diagrams(
    doc: ModuleDoc,
    out_dir: Path,
    stem: str,
    *,
    flow_file_dir: Optional[str] = None,
) -> List[str]:
    from flow.geometry_diagram import write_diagram_artifacts

    written: List[str] = []
    total = len(doc.theorems)
    script_dir = flow_file_dir
    if not script_dir and doc.file_path:
        script_dir = str(Path(doc.file_path).parent)
    for i, thm in enumerate(doc.theorems):
        svg, tex = write_diagram_artifacts(
            thm,
            out_dir,
            stem,
            index=i,
            total=total,
            flow_file_dir=script_dir,
        )
        if svg:
            thm.diagram_svg = Path(svg).name
            thm.diagram_tex = Path(tex).name if tex else ""
            written.append(svg)
            if tex:
                written.append(tex)
    return written


def write_proof_artifacts(
    path: str,
    *,
    output_dir: Optional[str] = None,
    number_offset: int = 1,
) -> Tuple[str, str, List[str]]:
    """Parse a .flow file and write .proof.md, .proof.tex, and diagram files."""
    doc = parse_proof_file(path)
    assign_numbers([doc], start=number_offset)

    src = Path(path)
    out_dir = Path(output_dir) if output_dir else src.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    diagram_files = _attach_geometry_diagrams(
        doc, out_dir, src.stem, flow_file_dir=str(src.parent)
    )

    md_path = out_dir / (src.stem + ".proof.md")
    tex_path = out_dir / (src.stem + ".proof.tex")

    md_path.write_text(render_english(doc), encoding="utf-8")
    tex_path.write_text(render_latex(doc), encoding="utf-8")

    return str(md_path), str(tex_path), diagram_files


def write_proof_artifacts_tree(
    root: str,
    *,
    recursive: bool = True,
) -> List[Tuple[str, str, str]]:
    """Generate artifacts for all verification-shaped .flow files under root."""
    root_path = Path(root)
    files: List[Path] = []
    if root_path.is_file():
        files = [root_path]
    elif recursive:
        files = sorted(root_path.rglob("*.flow"))
    else:
        files = sorted(root_path.glob("*.flow"))

    results: List[Tuple[str, str, str]] = []
    counter = 1
    for fp in files:
        text = fp.read_text(encoding="utf-8", errors="ignore")
        if "theorem " not in text:
            continue
        doc = parse_proof_file(str(fp))
        if not doc.theorems:
            continue
        assign_numbers([doc], start=counter)
        counter += len(doc.theorems)

        _attach_geometry_diagrams(doc, fp.parent, fp.stem, flow_file_dir=str(fp.parent))

        md = fp.parent / (fp.stem + ".proof.md")
        tex = fp.parent / (fp.stem + ".proof.tex")
        md.write_text(render_english(doc), encoding="utf-8")
        tex.write_text(render_latex(doc), encoding="utf-8")
        results.append((str(fp), str(md), str(tex)))

    return results


def _render_book_docs(
    docs: List[ModuleDoc],
    parts: List[str],
    *,
    theorem_catalog: Dict[str, TheoremCatalogEntry],
) -> None:
    for doc in docs:
        tier_index = _merged_tier_index(doc)
        for thm in doc.theorems:
            parts.extend(
                _render_theorem_latex_block(
                    thm,
                    tier_index=tier_index,
                    theorem_catalog=theorem_catalog,
                    book_mode=True,
                )
            )


def render_side_by_side_bundle(
    docs: Optional[List[ModuleDoc]] = None,
    *,
    book_parts: Optional[List[BookPart]] = None,
    title: str = "Flow Proof Book",
) -> str:
    """LaTeX textbook tutorial — circled steps, proof | math columns."""
    preamble = _latex_preamble(title, title_prefix=title)
    for i, line in enumerate(preamble):
        if line.startswith(r"\title{"):
            preamble[i] = r"\title{" + _latex_escape(title) + "}"
            break

    body: List[str] = []
    if book_parts:
        body.append(r"\tableofcontents")
        body.append(r"\bigskip\par")
    body.extend([
        r"\noindent\textit{Each proof step is numbered. "
        r"English reasoning is on the left; the matching equation is on the right. "
        r"Prerequisite facts are cited by number (e.g.\ Definition 2, Axiom 9).}\par",
        r"\medskip",
        r"\noindent\textbf{Labels.} "
        r"\textit{Axiom} = accepted without proof; "
        r"\textit{Definition} = stipulation; "
        r"\textit{Derived fact} = proved from prior claims.\par",
    ])
    body.append(r"\bigskip\par")

    catalog: Dict[str, TheoremCatalogEntry] = {}
    if book_parts:
        catalog = build_theorem_catalog_from_parts(book_parts)
    elif docs:
        catalog = build_theorem_catalog_from_docs(docs)

    if book_parts:
        for i, part in enumerate(book_parts):
            if i:
                body.append(r"\clearpage")
            body.append(
                rf"\section*{{{_latex_escape(part.title)}}}"
            )
            body.append(r"\addcontentsline{toc}{section}{" + _latex_escape(part.title) + "}")
            body.append(r"\medskip\par")
            _render_book_docs(part.docs, body, theorem_catalog=catalog)
    elif docs:
        _render_book_docs(docs, body, theorem_catalog=catalog)

    body.append(r"\end{document}")
    return "\n".join(preamble + body) + "\n"


def load_basic_proof_bundle(project_root: str) -> List[ModuleDoc]:
    root = Path(project_root)
    docs: List[ModuleDoc] = []
    counter = 1
    for rel in BASIC_PROOF_BUNDLE:
        path = root / rel
        if not path.is_file():
            raise FileNotFoundError(f"Basic proof file missing: {path}")
        doc = parse_proof_file(str(path))
        assign_numbers([doc], start=counter)
        counter += len(doc.theorems)
        docs.append(doc)
    return docs


def load_geometry_proof_bundle(
    project_root: str,
    *,
    diagram_dir: Optional[Path] = None,
    number_offset: int = 1,
) -> List[ModuleDoc]:
    """Load Euclidean geometry proofs and attach diagram artifacts."""
    docs, _ = _load_bundle_files(
        project_root,
        GEOMETRY_PROOF_BUNDLE,
        number_offset=number_offset,
        diagram_dir=diagram_dir,
    )
    return docs


def _load_bundle_files(
    project_root: str,
    rel_paths: List[str],
    *,
    number_offset: int = 1,
    diagram_dir: Optional[Path] = None,
) -> Tuple[List[ModuleDoc], int]:
    root = Path(project_root)
    docs: List[ModuleDoc] = []
    counter = number_offset
    for rel in rel_paths:
        path = root / rel
        if not path.is_file():
            raise FileNotFoundError(f"Proof file missing: {path}")
        doc = parse_proof_file(str(path))
        assign_numbers([doc], start=counter)
        counter += len(doc.theorems)
        docs.append(doc)
    return docs, counter


def load_proof_book(
    project_root: str,
    *,
    diagram_dir: Optional[Path] = None,
) -> List[BookPart]:
    """Load the full proof book with continuous theorem numbering."""
    parts: List[BookPart] = []
    counter = 1
    for title, rels in BOOK_PARTS:
        docs, counter = _load_bundle_files(
            project_root,
            rels,
            number_offset=counter,
            diagram_dir=diagram_dir,
        )
        parts.append(BookPart(title=title, docs=docs))
    return parts


def _compile_proof_bundle_pdf(
    tex_path: Path,
    pdf_path: Path,
    out_dir: Path,
) -> Tuple[str, str]:
    for cmd in ("pdflatex", "xelatex", "tectonic"):
        exe = _find_latex_compiler(cmd)
        if not exe:
            continue
        try:
            _compile_latex(exe, tex_path, out_dir)
            built = out_dir / f"{tex_path.stem}.pdf"
            if built.is_file():
                if built != pdf_path:
                    built.replace(pdf_path)
                return str(tex_path), str(pdf_path)
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    raise RuntimeError(
        "Could not compile PDF. Install pdflatex, xelatex, or tectonic."
    )


def write_proof_book_pdf(
    project_root: str,
    *,
    output_dir: Optional[str] = None,
    tex_name: str = "flow-proof-book.tex",
    pdf_name: str = "flow-proof-book.pdf",
) -> Tuple[str, str]:
    """
    Generate the unified Flow proof book (algebra + geometry + analysis)
    with continuous numbering, diagrams, and substitution boxes.
    Returns (tex_path, pdf_path).
    """
    out_dir = Path(output_dir or Path(project_root) / "build" / "proofs")
    out_dir.mkdir(parents=True, exist_ok=True)

    parts = load_proof_book(project_root, diagram_dir=out_dir)

    tex_path = out_dir / tex_name
    pdf_path = out_dir / pdf_name

    tex_path.write_text(
        render_side_by_side_bundle(
            book_parts=parts,
            title="Flow Proof Book",
        ),
        encoding="utf-8",
    )

    for rel in FLOW_PROOF_BOOK:
        write_proof_artifacts(str(Path(project_root) / rel))

    return _compile_proof_bundle_pdf(tex_path, pdf_path, out_dir)


def write_basic_proof_bundle_pdf(
    project_root: str,
    *,
    output_dir: Optional[str] = None,
    pdf_name: str = "basic-proofs-side-by-side.pdf",
) -> Tuple[str, str]:
    """
    Generate side-by-side LaTeX for basic proofs and compile to PDF.
    Returns (tex_path, pdf_path).
    """
    docs = load_basic_proof_bundle(project_root)

    out_dir = Path(output_dir or Path(project_root) / "build" / "proofs")
    out_dir.mkdir(parents=True, exist_ok=True)

    tex_path = out_dir / "basic-proofs-side-by-side.tex"
    pdf_path = out_dir / pdf_name

    tex_path.write_text(
        render_side_by_side_bundle(docs, title="Flow Basic Proofs"),
        encoding="utf-8",
    )

    for rel in BASIC_PROOF_BUNDLE:
        write_proof_artifacts(str(Path(project_root) / rel))

    return _compile_proof_bundle_pdf(tex_path, pdf_path, out_dir)


def write_geometry_proof_bundle_pdf(
    project_root: str,
    *,
    output_dir: Optional[str] = None,
    pdf_name: str = "geometry-proofs-side-by-side.pdf",
) -> Tuple[str, str]:
    """
    Generate side-by-side LaTeX for Euclidean geometry proofs (with diagrams)
    and compile to PDF. Returns (tex_path, pdf_path).
    """
    out_dir = Path(output_dir or Path(project_root) / "build" / "proofs")
    out_dir.mkdir(parents=True, exist_ok=True)

    docs = load_geometry_proof_bundle(project_root, diagram_dir=out_dir)

    tex_path = out_dir / "geometry-proofs-side-by-side.tex"
    pdf_path = out_dir / pdf_name

    tex_path.write_text(
        render_side_by_side_bundle(docs, title="Flow Euclidean Geometry"),
        encoding="utf-8",
    )

    for rel in GEOMETRY_PROOF_BUNDLE:
        write_proof_artifacts(str(Path(project_root) / rel))

    return _compile_proof_bundle_pdf(tex_path, pdf_path, out_dir)


def _find_latex_compiler(name: str) -> Optional[str]:
    from shutil import which

    path = which(name)
    if path:
        return path
    mac_tex = f"/Library/TeX/texbin/{name}"
    if os.path.isfile(mac_tex):
        return mac_tex
    return None


def _compile_latex(compiler: str, tex_path: Path, out_dir: Path) -> None:
    stem = tex_path.stem
    if "tectonic" in compiler:
        subprocess.run(
            [compiler, "--outdir", str(out_dir), str(tex_path)],
            check=True,
            cwd=str(out_dir),
            capture_output=True,
        )
        return

    tex_name = tex_path.name
    for _ in range(2):
        result = subprocess.run(
            [
                compiler,
                "-interaction=nonstopmode",
                tex_name,
            ],
            cwd=str(out_dir),
            capture_output=True,
        )
        if not (out_dir / f"{stem}.pdf").is_file():
            err = result.stderr.decode("utf-8", errors="replace")[-2000:]
            raise subprocess.CalledProcessError(
                result.returncode, compiler, output=err
            )