"""Normalization formulas shared by Phase 6 validators."""
from __future__ import annotations
def weighted_efficiency(selected_sumw: float, denominator_sumw: float) -> float:
    if denominator_sumw <= 0: raise ValueError('denominator_sumw must be positive')
    return selected_sumw / denominator_sumw
def expected_yield(luminosity_fb_inverse: float, cross_section_fb: float, selected_weight_fraction: float) -> float:
    if luminosity_fb_inverse < 0 or cross_section_fb < 0: raise ValueError('luminosity and cross section must be nonnegative')
    if not 0.0 <= selected_weight_fraction <= 1.0: raise ValueError('selected_weight_fraction must be in [0,1]')
    return luminosity_fb_inverse * cross_section_fb * selected_weight_fraction
