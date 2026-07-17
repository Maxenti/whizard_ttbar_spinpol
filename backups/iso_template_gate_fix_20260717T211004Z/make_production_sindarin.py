#!/usr/bin/env python3
"""Generate shard-renderable WHIZARD SINDARIN templates for production-v1."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from production_common import (
    SampleConfig,
    filter_configs,
    read_configs,
    repo_root_from_script,
    write_csv,
)

TOKENS = ("__SHARD_LABEL__", "__OUTPUT_SAMPLE__", "__SEED__", "__N_EVENTS__")


def parse_args() -> argparse.Namespace:
    root = repo_root_from_script(__file__)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=root / "configs/production/production_500GeV_ISR_sc_v1.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "sindarin/production",
    )
    parser.add_argument(
        "--sample",
        action="append",
        default=[],
        help="fnmatch pattern; may be repeated",
    )
    parser.add_argument("--check", action="store_true", help="validate without writing")
    parser.add_argument("--force", action="store_true", help="replace existing templates")
    return parser.parse_args()


def decay_lines(cfg: SampleConfig) -> tuple[str, str, str, str]:
    if cfg.decay_channel == "epmum":
        return (
            "process t_decay    = t    => b,    E1, n1",
            "process tbar_decay = tbar => bbar, e2, N2",
            "t -> b e+ nu_e",
            "tbar -> bbar mu- anti-nu_mu",
        )
    if cfg.decay_channel == "mupem":
        return (
            "process t_decay    = t    => b,    E2, n2",
            "process tbar_decay = tbar => bbar, e1, N1",
            "t -> b mu+ nu_mu",
            "tbar -> bbar e- anti-nu_e",
        )
    raise ValueError(cfg.decay_channel)


def percent(value: float) -> str:
    return f"{100.0 * value:g}%"


def render_template(cfg: SampleConfig) -> str:
    t_process, tbar_process, t_text, tbar_text = decay_lines(cfg)
    isotropic = "false" if cfg.spin_correlated else "true"
    diagonal = "false"
    beam_line = f"beams = {cfg.beam1}, {cfg.beam2} => isr" if cfg.isr_enabled else f"beams = {cfg.beam1}, {cfg.beam2}"
    isr_block = f"""
?isr_handler = true
$isr_handler_mode = "recoil"
?keep_beams = true
?keep_remnants = true
isr_mass = {cfg.isr_mass_GeV:.12g} GeV
isr_alpha = {cfg.isr_alpha:.12g}
""".strip() if cfg.isr_enabled else ""

    return f"""! ======================================================================
! WHIZARD polarized ttbar production template with configurable decay spin treatment
! ======================================================================
! META campaign_id={cfg.campaign_id}
! META sample_id={cfg.sample_id}
! META initial_state={cfg.initial_state}
! META sqrt_s_GeV={cfg.sqrt_s_GeV:g}
! META decay_channel={cfg.decay_channel}
! META polarization={cfg.polarization}
! META beam1_helicity={cfg.beam1_helicity}
! META beam2_helicity={cfg.beam2_helicity}
! META beam1_pol_fraction={cfg.beam1_pol_fraction:g}
! META beam2_pol_fraction={cfg.beam2_pol_fraction:g}
! META spin_mode={"sc" if cfg.spin_correlated else "iso"}
! META isr_enabled={str(cfg.isr_enabled).lower()}
! META isr_mass_GeV={cfg.isr_mass_GeV:.12g}
! META isr_alpha={cfg.isr_alpha:.12g}
! META beam_spectrum={cfg.beam_spectrum}
! META model=SM
! META seed=__SEED__
! META requested_events=__N_EVENTS__
! META shard_label=__SHARD_LABEL__
!
! Production:
!   {cfg.beam1} {cfg.beam2} -> t tbar
!
! Forced decay assignment:
!   {t_text}
!   {tbar_text}
!
! The raw LHE header contains the inclusive polarized ttbar production
! cross section because each forced decay table has one configured channel.
! The workflow preserves raw LHE and creates separately normalized final LHE.
! ======================================================================

model = SM

process tt_prod = {cfg.beam1}, {cfg.beam2} => t, tbar
{t_process}
{tbar_process}

! Integrate decay processes before defining collider beams.  This ordering is
! required by the validated WHIZARD 3.1.5 workflow for separate decay grids.
integrate (t_decay) {{
  iterations = 3:5000, 3:20000
}}

integrate (tbar_decay) {{
  iterations = 3:5000, 3:20000
}}

sqrts = {cfg.sqrt_s_GeV:g} GeV
{beam_line}
{isr_block}

beams_pol_density  = @({cfg.beam1_helicity:+d}), @({cfg.beam2_helicity:+d})
beams_pol_fraction = {percent(cfg.beam1_pol_fraction)}, {percent(cfg.beam2_pol_fraction)}

?diagonal_decay = {diagonal}
?isotropic_decay = {isotropic}

integrate (tt_prod) {{
  iterations = 5:20000, 5:50000
  ?polarized_events = true
}}

unstable t    (t_decay)
unstable tbar (tbar_decay)

seed = __SEED__
n_events = __N_EVENTS__
sample_format = lhef
$sample = "__OUTPUT_SAMPLE__"

simulate (tt_prod) {{
  ?polarized_events = true
}}
"""


def validate_template(text: str, cfg: SampleConfig) -> None:
    for token in TOKENS:
        if token not in text:
            raise ValueError(f"template for {cfg.sample_id} is missing token {token}")
    required = [
        "=> isr",
        "?isr_handler = true",
        "isr_mass =",
        "isr_alpha =",
        f"?isotropic_decay = {'false' if cfg.spin_correlated else 'true'}",
        "?diagonal_decay = false",
        "?polarized_events = true",
        f"@({cfg.beam1_helicity:+d})",
        f"@({cfg.beam2_helicity:+d})",
        "sample_format = lhef",
    ]
    missing = [entry for entry in required if entry not in text]
    if missing:
        raise ValueError(f"template for {cfg.sample_id} is missing: {missing}")


def main() -> int:
    args = parse_args()
    repo = repo_root_from_script(__file__)
    configs = filter_configs(read_configs(args.config), args.sample)
    rows: list[dict[str, object]] = []
    for cfg in configs:
        text = render_template(cfg)
        validate_template(text, cfg)
        path = args.output_dir / cfg.template_name
        if not args.check:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists() and not args.force:
                existing = path.read_text()
                if existing != text:
                    raise FileExistsError(
                        f"template exists with different content: {path}; use --force"
                    )
            else:
                path.write_text(text)
        rows.append(
            {
                "campaign_id": cfg.campaign_id,
                "sample_id": cfg.sample_id,
                "template_path": str(path.resolve().relative_to(repo.resolve()))
                if path.resolve().is_relative_to(repo.resolve()) else str(path.resolve()),
                "initial_state": cfg.initial_state,
                "decay_channel": cfg.decay_channel,
                "polarization": cfg.polarization,
                "sqrt_s_GeV": cfg.sqrt_s_GeV,
                "isr_enabled": cfg.isr_enabled,
                "spin_correlated": cfg.spin_correlated,
            }
        )
        print(f"{'CHECK' if args.check else 'WROTE'} {path}")

    if not args.check:
        manifest = args.output_dir / "generated_templates.csv"
        write_csv(
            manifest,
            [
                "campaign_id",
                "sample_id",
                "template_path",
                "initial_state",
                "decay_channel",
                "polarization",
                "sqrt_s_GeV",
                "isr_enabled",
                "spin_correlated",
            ],
            rows,
        )
        print(f"Wrote {manifest}")
    print(f"Validated {len(configs)} production template(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
