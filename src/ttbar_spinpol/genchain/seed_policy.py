"""Deterministic positive 31-bit seed derivation."""
from __future__ import annotations
import hashlib
MAX_SEED=2_147_483_646
def derive_seed(*fields: object) -> int:
    digest=hashlib.sha256('::'.join(str(f) for f in fields).encode()).digest()
    return 1 + (int.from_bytes(digest[:8], 'big') % MAX_SEED)
