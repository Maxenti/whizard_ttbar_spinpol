"""Stable global event identity helpers."""
from __future__ import annotations
import hashlib
def global_event_id(campaign_id: str, sample_id: str, exact_subprocess_id: str, polarization_id: str, shard_id: str, generator_event_number: int) -> str:
    if generator_event_number < 0: raise ValueError('generator_event_number must be nonnegative')
    return hashlib.sha256('::'.join([campaign_id,sample_id,exact_subprocess_id,polarization_id,shard_id,str(generator_event_number)]).encode()).hexdigest()
