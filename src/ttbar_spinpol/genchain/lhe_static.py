"""Tiny LHE static checks without external HEP packages."""
from __future__ import annotations
from pathlib import Path
def count_lhe_events(path: Path) -> int:
    return sum(1 for line in path.read_text(errors='replace').splitlines() if line.strip()=='<event>')
def has_lhe_init(path: Path) -> bool:
    text=path.read_text(errors='replace'); return '<init>' in text and '</init>' in text
