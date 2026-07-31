#!/usr/bin/env python3
"""Build JSONL manifests for Phase 7 canonical-v2 bridge runs."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


CAMPAIGN_ID = "full6f_365gev_ee_ttbar_spinpol_v1"
GENERATED_SUBDIR = "sindarin/generated/full6f_365gev_ee_ttbar_spinpol_v1"

REPRESENTATIVE_RELATIVE_CARDS = [
    "f6f365_ee_unpol_epmum/epmum/process.sin",
    "f6f365_ee_LR100_epmum/epmum/process.sin",
    "f6f365_ee_unpol_epjets/epjets__Wminus_ubar_d/process.sin",
]


def derive_label(card: Path, generated_root: Path) -> str:
    rel = card.relative_to(generated_root)
    family = rel.parts[0]
    channel_dir = rel.parts[1]

    prefix = "f6f365_ee_"
    family_tail = family[len(prefix):] if family.startswith(prefix) else family

    if "_" in family_tail:
        pol, family_channel = family_tail.split("_", 1)
    else:
        pol, family_channel = "unknown", family_tail

    clean_channel = channel_dir.replace("__", "_")

    if channel_dir == family_channel:
        return family_tail

    if channel_dir.startswith(family_channel + "__"):
        return f"{pol}_{clean_channel}"

    return f"{family_tail}_{clean_channel}"


def derive_category(label: str) -> str:
    pol = "polarized" if label.startswith(("LR100", "RL100")) else "unpolarized"
    topology = "semileptonic" if "jets" in label else "dilepton"
    return f"{topology}_{pol}"


def discover_cards(generated_root: Path, mode: str) -> list[Path]:
    if mode == "representative":
        cards = [generated_root / rel for rel in REPRESENTATIVE_RELATIVE_CARDS]
        missing = [str(card) for card in cards if not card.is_file()]
        if missing:
            raise FileNotFoundError("missing representative cards:\n" + "\n".join(missing))
        return cards

    cards = sorted(generated_root.glob("**/process.sin"))
    cards = [card for card in cards if "/common/" not in card.as_posix()]
    if not cards:
        raise FileNotFoundError(f"no process.sin cards found under {generated_root}")
    return cards


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(os.environ.get("REPO", ".")).resolve())
    parser.add_argument("--campaign-id", default=CAMPAIGN_ID)
    parser.add_argument("--generated-root", type=Path, default=None)
    parser.add_argument("--mode", choices=["representative", "all"], default="representative")
    parser.add_argument("--base-seed", type=int, default=24682000)
    parser.add_argument("--events", type=int, default=100)
    parser.add_argument("--iterations", default="3:5000")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    repo = args.repo.resolve()
    generated_root = args.generated_root or (repo / GENERATED_SUBDIR)
    generated_root = generated_root.resolve()

    if args.output is None:
        out_dir = repo / "campaigns" / args.campaign_id / "showering"
        out_dir.mkdir(parents=True, exist_ok=True)
        output = out_dir / f"phase7_bridge_manifest_{args.mode}.jsonl"
    else:
        output = args.output
        output.parent.mkdir(parents=True, exist_ok=True)

    cards = discover_cards(generated_root, args.mode)

    records = []
    for i, card in enumerate(cards):
        label = derive_label(card, generated_root)
        category = derive_category(label)
        seed = args.base_seed + i

        records.append(
            {
                "schema_version": 1,
                "campaign_id": args.campaign_id,
                "bridge_policy": "canonical_v2",
                "label": label,
                "category": category,
                "card": str(card),
                "sample_id": f"{label}_canonical_v2",
                "shard_id": f"bridge_{args.events}ev_{label}",
                "seed": seed,
                "events": args.events,
                "iterations": args.iterations,
            }
        )

    with output.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, sort_keys=True) + "\n")

    print(f"PHASE7_BRIDGE_MANIFEST={output}")
    print(f"MODE={args.mode}")
    print(f"RECORDS={len(records)}")
    for record in records:
        print(f"{record['label']}  {record['category']}  seed={record['seed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
