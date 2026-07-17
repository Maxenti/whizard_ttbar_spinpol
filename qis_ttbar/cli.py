from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .config import load_config
from .io.manifest import load_sample_manifest, select_records
from .io.tables import read_table
from .level_b.detector import DetectorResponse, ResponseConfig
from .level_b.reconstruction import DileptonReconstructor
from .level_c.cp import cp_observables
from .level_c.optimized_bases import optimize_correlation_basis
from .validation import validate_synthetic_states, write_validation
from .workflow.ntuples import build_ntuple_for_sample
from .workflow.tomography import run_tomography_for_frame


def make_ntuples_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build truth-level QIS ntuples from LHE or HepMC3")
    parser.add_argument("--config", default="configs/qis/level_a_500GeV_ISR_sc_v1.yaml")
    parser.add_argument("--manifest")
    parser.add_argument("--sample", action="append", default=[])
    parser.add_argument("--input-format", choices=("lhe", "hepmc3"), default="lhe")
    parser.add_argument("--input-root")
    parser.add_argument("--output-dir")
    parser.add_argument("--max-events", type=int)
    parser.add_argument("--no-root", action="store_true")
    parser.add_argument("--no-parquet", action="store_true")
    args = parser.parse_args(argv)
    config = load_config(args.config)
    campaign = config.section("campaign")
    manifest = Path(args.manifest or campaign["source_manifest"])
    output = Path(args.output_dir or config.output_root / "ntuples" / args.input_format)
    physics = config.section("physics")
    records = select_records(load_sample_manifest(manifest), args.sample)
    for record in records:
        input_path = None
        if args.input_root:
            extension = ".lhe" if args.input_format == "lhe" else ".hepmc3"
            input_path = Path(args.input_root) / f"{record.sample_id}{extension}"
        summary = build_ntuple_for_sample(
            record, input_path=input_path, input_format=args.input_format,
            output_base=output / record.sample_id, max_events=args.max_events,
            basis_order=tuple(physics.get("basis_order", ["k", "r", "n"])),
            antitop_analyzer_sign=float(physics.get("antitop_analyzer_sign", -1.0)),
            alpha_plus=float(physics.get("analyzing_power", {}).get("lepton_plus", 1.0)),
            alpha_minus=float(physics.get("analyzing_power", {}).get("lepton_minus", 1.0)),
            write_root=not args.no_root, write_parquet=not args.no_parquet,
        )
        print(json.dumps(summary, sort_keys=True))
    return 0


def tomography_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run spin-density-matrix tomography and QIS observables")
    parser.add_argument("input_table")
    parser.add_argument("--config", default="configs/qis/level_a_500GeV_ISR_sc_v1.yaml")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--replicas", type=int)
    parser.add_argument("--minimum-events", type=int, default=100)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    physics, stats, bins = config.section("physics"), config.section("statistics"), config.section("binning")
    frame = read_table(args.input_table)
    run_tomography_for_frame(
        frame, output_dir=args.output_dir,
        basis_order=tuple(physics.get("basis_order", ["k", "r", "n"])),
        replicas=args.replicas or int(stats.get("bootstrap_replicas_production", 1000)),
        seed=int(stats.get("bootstrap_seed", 730001)),
        confidence_level=float(stats.get("confidence_level", 0.68)),
        alpha_plus=float(physics.get("analyzing_power", {}).get("lepton_plus", 1.0)),
        alpha_minus=float(physics.get("analyzing_power", {}).get("lepton_minus", 1.0)),
        mtt_edges=bins.get("mtt_GeV"), cos_theta_edges=bins.get("cos_theta_t"),
        minimum_events=args.minimum_events,
    )
    return 0


def validate_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate QIS mathematics and framework contracts")
    parser.add_argument("--output", default="validation/qis_framework_validation")
    args = parser.parse_args(argv)
    return write_validation(validate_synthetic_states(), args.output)


def level_b_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run parametric Level-B detector/reconstruction closure")
    parser.add_argument("input_table")
    parser.add_argument("--config", default="configs/qis/level_b_detector.yaml")
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-events", type=int)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    response_cfg = ResponseConfig(**{k: v for k, v in config.section("response").items() if k != "seed"})
    response = DetectorResponse(response_cfg, seed=int(config.section("response").get("seed", 810001)))
    reco_cfg = config.section("reconstruction")
    reconstructor = DileptonReconstructor(
        top_mass_GeV=float(reco_cfg.get("top_mass_GeV", 173.1)), w_mass_GeV=float(reco_cfg.get("w_mass_GeV", 80.379)),
        top_width_GeV=float(reco_cfg.get("top_width_GeV", 1.523)), w_width_GeV=float(reco_cfg.get("w_width_GeV", 2.085)),
        solver_starts=int(reco_cfg.get("solver_starts", 32)),
    )
    frame = read_table(args.input_table)
    if args.max_events:
        frame = frame.head(args.max_events)
    rows = []
    from .models import FourVector
    def p4(row, prefix):
        return FourVector(float(row[f"{prefix}_e"]), float(row[f"{prefix}_px"]), float(row[f"{prefix}_py"]), float(row[f"{prefix}_pz"]))
    for _, row in frame.iterrows():
        lp, lm = response.smear_lepton(p4(row, "lepton_plus")), response.smear_lepton(p4(row, "lepton_minus"))
        b, bb = response.smear_jet(p4(row, "b")), response.smear_jet(p4(row, "bbar"))
        accepted = lp.accepted and lm.accepted and b.accepted and bb.accepted
        output = {"event_index": int(row["event_index"]), "accepted": accepted}
        if accepted:
            initial = p4(row, "beam_minus") + p4(row, "beam_plus")
            try:
                solution = reconstructor.reconstruct(initial, lp.p4, lm.p4, (b.p4, bb.p4), max_chi2=float(reco_cfg.get("max_chi2", 100.0)))
                output.update({"reco_success": True, "reco_chi2": solution.chi2, "reco_top_mass": solution.top.mass, "reco_antitop_mass": solution.antitop.mass})
            except Exception as exc:
                output.update({"reco_success": False, "reco_error": str(exc)})
        rows.append(output)
    pd.DataFrame(rows).to_csv(args.output, index=False)
    return 0


def level_c_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run advanced Level-C CP/optimized-basis summary")
    parser.add_argument("tomography_json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    payload = json.loads(Path(args.tomography_json).read_text())
    correlation = payload["tomography"]["C"]
    optimized = optimize_correlation_basis(correlation)
    output = {
        "cp": cp_observables(correlation),
        "optimized_basis": {
            "top_rotation": optimized.top_rotation.tolist(),
            "antitop_rotation": optimized.antitop_rotation.tolist(),
            "diagonal_correlation": optimized.diagonal_correlation.tolist(),
            "singular_values": optimized.singular_values.tolist(),
        },
    }
    Path(args.output).write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    return 0
