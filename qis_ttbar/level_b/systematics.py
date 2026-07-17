from __future__ import annotations

import dataclasses
from collections.abc import Callable, Iterable
from typing import Any


@dataclasses.dataclass(frozen=True)
class SystematicVariation:
    name: str
    parameter: str
    value: Any
    correlation_group: str | None = None


def run_variations(base_configuration: dict[str, Any], variations: Iterable[SystematicVariation], evaluator: Callable[[dict[str, Any]], Any]) -> dict[str, Any]:
    output = {"nominal": evaluator(dict(base_configuration))}
    for variation in variations:
        varied = dict(base_configuration)
        varied[variation.parameter] = variation.value
        output[variation.name] = evaluator(varied)
    return output
