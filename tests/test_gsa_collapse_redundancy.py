"""Tests for geotech_references.gsa_collapse.redundancy (Section 3.4).

Section 3.4 is entirely NEW content with no UFC 4-023-03 analog (confirmed:
no cross-check import from ufc_collapse in this file). Anchors are the
PRINTED WORKED-EXAMPLE values from Appendix D's redundancy example (an
8-story reinforced-concrete building, Column Removal 1, printed
pp. D48-D54).
"""

import pytest

from geotech_references.gsa_collapse.redundancy import (
    minimum_load_redistribution_systems,
    load_redistribution_system_strength,
    load_redistribution_average_strength,
    load_redistribution_strength_ratio,
    load_redistribution_system_stiffness,
    load_redistribution_average_stiffness,
    load_redistribution_stiffness_ratio,
    fixed_fixed_flexural_stiffness,
)


class TestMinimumLoadRedistributionSystems:
    def test_eight_story_building(self):
        # PRINTED WORKED-EXAMPLE VALUE (p. D48): n >= 8/3 = 2.67 -> n=3.
        r = minimum_load_redistribution_systems(8)
        assert r["n"] == 3
        assert r["max_spacing_floors"] == 3

    def test_exact_multiple_of_three(self):
        r = minimum_load_redistribution_systems(9)
        assert r["n"] == 3

    def test_one_over_a_multiple_of_three(self):
        r = minimum_load_redistribution_systems(10)
        assert r["n"] == 4

    def test_single_floor(self):
        assert minimum_load_redistribution_systems(1)["n"] == 1


class TestLoadRedistributionStrength:
    def test_system_strength_worked_example_level_3(self):
        # PRINTED WORKED-EXAMPLE VALUE (p. D51): QC1=839.8, QC2=604.6
        # kip-in (Phi already applied in the printed QC values), Phi=1.0
        # (pass-through) since the source already folds Phi into each QC.
        r = load_redistribution_system_strength(
            component_strengths=[839.8, 604.6], phi_factors=[1.0, 1.0])
        assert r["qr"] == pytest.approx(1444.4, abs=0.05)

    def test_average_strength_worked_example(self):
        # PRINTED WORKED-EXAMPLE VALUE (p. D51): QR3=QR5=QR7=1444.4 kip-in.
        r = load_redistribution_average_strength([1444.4, 1444.4, 1444.4])
        assert r["qr_bar"] == pytest.approx(1444.4)
        assert r["n"] == 3

    def test_strength_ratio_worked_example_all_levels_ok(self):
        # PRINTED WORKED-EXAMPLE VALUE (p. D51-D52): ratio=0.0 <= 0.3 at
        # Levels 3, 5, and 7 (all identical, since the same two upgraded
        # beam sections repeat at every load-redistribution level).
        for qr_i in (1444.4, 1444.4, 1444.4):
            r = load_redistribution_strength_ratio(qr_i, qr_bar=1444.4)
            assert r["ratio"] == pytest.approx(0.0)
            assert r["adequate"] is True

    def test_strength_ratio_at_30_pct_boundary(self):
        r = load_redistribution_strength_ratio(qr_i=130.0, qr_bar=100.0)
        assert r["ratio"] == pytest.approx(0.3)
        assert r["adequate"] is True

    def test_strength_ratio_exceeding_30_pct(self):
        r = load_redistribution_strength_ratio(qr_i=131.0, qr_bar=100.0)
        assert r["adequate"] is False


class TestLoadRedistributionStiffness:
    def test_fixed_fixed_flexural_stiffness_beam_b1u(self):
        # PRINTED WORKED-EXAMPLE VALUE (p. D53/D54, Levels 5 and 7 --
        # both printed instances agree): Ec=4031 ksi, Icr.B1U=16423 in4,
        # L=450 in (37.5 ft) -> KC=279 kip/in, reproduced exactly.
        #
        # FLAGGED PRINTED DISCREPANCY: the Level 3 instance of this SAME
        # calculation (printed p. D52) instead states Icr.B1U=19160 in4
        # -- page-verified against the rendered PDF -- yet still claims
        # the identical answer KC=279 kip/in. Substituting 19160 into the
        # document's own printed formula gives KC=325.46 kip/in (via
        # fixed_fixed_flexural_stiffness(ec=4031, icr=19160, length=450)),
        # NOT 279 -- confirmed by direct execution. Since two of the
        # three printed instances (Levels 5 and 7) agree on Icr=16423 and
        # that value is the one that actually reproduces the stated
        # KC=279 answer, 16423 is used here as the validated anchor; the
        # Level 3 "19160" is reported as a one-off source-document
        # transcription error, not silently corrected in the source.
        r = fixed_fixed_flexural_stiffness(ec=4031.0, icr=16423.0, length=450.0)
        assert r["kc"] == pytest.approx(279.0, rel=2e-3)

    def test_fixed_fixed_flexural_stiffness_beam_b1u_level_3_printed_input_does_not_reproduce(self):
        # Confirms the flagged discrepancy noted above: the Level-3
        # printed input (Icr=19160) does NOT reproduce the printed
        # KC=279 kip/in answer under the document's own formula.
        r = fixed_fixed_flexural_stiffness(ec=4031.0, icr=19160.0, length=450.0)
        assert r["kc"] == pytest.approx(325.46, rel=1e-3)
        assert r["kc"] != pytest.approx(279.0, rel=0.05)

    def test_fixed_fixed_flexural_stiffness_beam_b3u(self):
        # PRINTED WORKED-EXAMPLE VALUE (p. D53): Icr=14631 in4 -> KC=249 kip/in.
        r = fixed_fixed_flexural_stiffness(ec=4031.0, icr=14631.0, length=450.0)
        assert r["kc"] == pytest.approx(249.0, rel=2e-3)

    def test_system_stiffness_worked_example_level_3(self):
        # PRINTED WORKED-EXAMPLE VALUE (p. D52): KCE1=279, KCE2=249
        # kip/in -> KR3=528 kip/in (KC summed directly, no explicit Phi
        # multiplier in the worked example).
        r = load_redistribution_system_stiffness([279.0, 249.0])
        assert r["kr"] == pytest.approx(528.0)

    def test_average_stiffness_worked_example(self):
        # PRINTED WORKED-EXAMPLE VALUE (p. D54): KR3=KR5=KR7=528 kip/in.
        r = load_redistribution_average_stiffness([528.0, 528.0, 528.0])
        assert r["kr_bar"] == pytest.approx(528.0)
        assert r["n"] == 3

    def test_stiffness_ratio_worked_example_all_levels_ok(self):
        # PRINTED WORKED-EXAMPLE VALUE (p. D54): ratio=0.0 <= 0.3 at
        # every level.
        r = load_redistribution_stiffness_ratio(kr_i=528.0, kr_bar=528.0)
        assert r["ratio"] == pytest.approx(0.0)
        assert r["adequate"] is True

    def test_stiffness_ratio_exceeding_30_pct(self):
        r = load_redistribution_stiffness_ratio(kr_i=69.0, kr_bar=100.0)
        assert r["adequate"] is False

    def test_system_stiffness_with_explicit_phi(self):
        r = load_redistribution_system_stiffness([279.0, 249.0], phi_factors=[0.9, 0.9])
        assert r["kr"] == pytest.approx(0.9 * (279.0 + 249.0))
