#!/usr/bin/env python3
"""Optionally add a paper-spin dispatch to the existing gate script.

The patch is deliberately opt-in. It inserts an early dispatch after the first
shell `set` command and leaves every existing baseline branch untouched.
"""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path

BEGIN = "# BEGIN PAPER-SPIN ADDITIVE DISPATCH"
END = "# END PAPER-SPIN ADDITIVE DISPATCH"
BLOCK = f'''{BEGIN}
if [[ "${{1:-}}" == "paper-spin" ]]; then
  shift
  exec "$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)/run_paper_spin_all.sh" "$@"
fi
{END}
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--undo", action="store_true")
    args = parser.parse_args()
    target = Path(args.repo).resolve() / "scripts/qis/run_next_production_gate.sh"
    text = target.read_text()

    if args.undo:
        if BEGIN not in text:
            print("No paper-spin dispatch is installed")
            return 0
        start = text.index(BEGIN)
        end = text.index(END, start) + len(END)
        while end < len(text) and text[end] == "\n":
            end += 1
        target.write_text(text[:start] + text[end:])
        print(f"Removed dispatch from {target}")
        return 0

    if BEGIN in text:
        print(f"Dispatch already installed in {target}")
        return 0

    lines = text.splitlines(keepends=True)
    insertion = None
    for index, line in enumerate(lines):
        if line.lstrip().startswith("set "):
            insertion = index + 1
            break
    if insertion is None:
        insertion = 1 if lines and lines[0].startswith("#!") else 0

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = target.with_name(target.name + f".pre_paper_spin_{timestamp}.bak")
    shutil.copy2(target, backup)
    lines.insert(insertion, "\n" + BLOCK + "\n")
    target.write_text("".join(lines))
    print(f"Patched {target}")
    print(f"Backup: {backup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
