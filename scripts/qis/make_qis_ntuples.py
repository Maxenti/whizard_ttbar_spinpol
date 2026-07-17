#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from qis_ttbar.cli import make_ntuples_main
raise SystemExit(make_ntuples_main())
