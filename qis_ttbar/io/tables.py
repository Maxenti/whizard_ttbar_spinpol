from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def write_table(frame: pd.DataFrame, base: str | Path, *, parquet: bool = True, root: bool = True, csv: bool = True) -> dict[str, str]:
    base = Path(base)
    base.parent.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, str] = {}
    if csv:
        path = base.with_suffix(".csv")
        frame.to_csv(path, index=False)
        outputs["csv"] = str(path)
    if parquet:
        path = base.with_suffix(".parquet")
        try:
            frame.to_parquet(path, index=False)
            outputs["parquet"] = str(path)
        except (ImportError, ModuleNotFoundError) as exc:
            outputs["parquet_error"] = str(exc)
    if root:
        path = base.with_suffix(".root")
        try:
            import uproot
            arrays = {name: frame[name].to_numpy() for name in frame.columns}
            with uproot.recreate(path) as file:
                file["events"] = arrays
            outputs["root"] = str(path)
        except (ImportError, ModuleNotFoundError) as exc:
            outputs["root_error"] = str(exc)
    manifest = base.with_suffix(".outputs.json")
    manifest.write_text(json.dumps(outputs, indent=2, sort_keys=True) + "\n")
    return outputs


def read_table(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if path.suffix == ".csv":
        return pd.read_csv(path)
    if path.suffix in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    if path.suffix == ".root":
        import uproot
        with uproot.open(path) as file:
            return file["events"].arrays(library="pd")
    raise ValueError(f"unsupported table format: {path}")
