"""Small YAML compatibility layer used by package static validators.

The lxplus/Key4HEP Python environment used for this project may not provide
PyYAML. Production code uses PyYAML when available, but package installation and
static validation must not fail just because that optional module is absent.
This module tries PyYAML first and falls back to a strict, small parser for the
subset used by the project contracts:

* indentation-based mappings and lists;
* scalar strings, booleans, integers, floats, and nulls;
* quoted strings;
* inline lists and simple inline mappings;
* folded/literal block scalars introduced with ``>`` or ``|``.

The fallback is not a general YAML implementation. It is intentionally limited
so unsupported syntax fails clearly instead of being interpreted differently on
different machines.
"""

from __future__ import annotations

from dataclasses import dataclass
import ast
import re
from pathlib import Path
from typing import Any

try:
    import yaml as _pyyaml  # type: ignore
except Exception:  # pragma: no cover - depends on external environment.
    _pyyaml = None


class YamlCompatError(ValueError):
    """Raised when a YAML document cannot be loaded reproducibly."""


@dataclass(frozen=True)
class _Token:
    indent: int
    text: str
    line_number: int


def load_text(text: str, *, source: str = "<string>") -> Any:
    """Load YAML text using PyYAML if available, otherwise the fallback parser."""

    if _pyyaml is not None:
        try:
            return _pyyaml.safe_load(text)
        except Exception as exc:  # pragma: no cover - PyYAML-specific path.
            raise YamlCompatError(f"invalid YAML in {source}: {exc}") from exc
    return _FallbackYamlParser(text, source).parse()


def load_path(path: Path) -> Any:
    """Load a YAML document from ``path``."""

    return load_text(path.read_text(encoding="utf-8"), source=str(path))


def load_mapping(path: Path) -> dict[str, Any]:
    """Load a YAML document and require a top-level mapping."""

    value = load_path(path)
    if not isinstance(value, dict):
        raise YamlCompatError(f"top-level YAML object must be a mapping: {path}")
    return value


class _FallbackYamlParser:
    """Small indentation parser for the package contract YAML subset."""

    _key_value = re.compile(r"^([^:#][^:]*):(.*)$")

    def __init__(self, text: str, source: str) -> None:
        self.source = source
        self.tokens = self._tokenize(text)

    def parse(self) -> Any:
        if not self.tokens:
            return None
        value, index = self._parse_block(0, self.tokens[0].indent)
        if index != len(self.tokens):
            token = self.tokens[index]
            raise YamlCompatError(
                f"unexpected trailing content at {self.source}:{token.line_number}: {token.text}"
            )
        return value

    def _tokenize(self, text: str) -> list[_Token]:
        tokens: list[_Token] = []
        raw_lines = text.splitlines()
        i = 0
        while i < len(raw_lines):
            original = raw_lines[i]
            line_number = i + 1
            stripped = original.strip()
            if not stripped or stripped.startswith("#") or stripped in {"---", "..."}:
                i += 1
                continue

            indent = len(original) - len(original.lstrip(" "))
            content = self._strip_comment(original[indent:]).rstrip()

            match = self._key_value.match(content)
            if match is not None and match.group(2).strip() in {">", "|", ">-", "|-", ">+", "|+"}:
                style = match.group(2).strip()[0]
                key = match.group(1).strip()
                block_indent: int | None = None
                block_lines: list[str] = []
                i += 1
                while i < len(raw_lines):
                    candidate = raw_lines[i]
                    cstrip = candidate.strip()
                    if not cstrip:
                        block_lines.append("")
                        i += 1
                        continue
                    cindent = len(candidate) - len(candidate.lstrip(" "))
                    if cindent <= indent:
                        break
                    if block_indent is None:
                        block_indent = cindent
                    block_lines.append(candidate[min(block_indent, len(candidate)):])
                    i += 1
                if style == ">":
                    block_value = " ".join(line.strip() for line in block_lines).strip()
                else:
                    block_value = "\n".join(block_lines).rstrip("\n")
                tokens.append(_Token(indent, f"{key}: {block_value!r}", line_number))
                continue

            tokens.append(_Token(indent, content, line_number))
            i += 1
        return tokens

    def _strip_comment(self, text: str) -> str:
        in_single = False
        in_double = False
        for idx, char in enumerate(text):
            if char == "'" and not in_double:
                in_single = not in_single
            elif char == '"' and not in_single:
                in_double = not in_double
            elif char == "#" and not in_single and not in_double:
                if idx == 0 or text[idx - 1].isspace():
                    return text[:idx]
        return text

    def _parse_block(self, index: int, indent: int) -> tuple[Any, int]:
        if index >= len(self.tokens):
            return {}, index
        token = self.tokens[index]
        if token.indent < indent:
            return {}, index
        if token.indent != indent:
            raise YamlCompatError(
                f"unexpected indentation at {self.source}:{token.line_number}: {token.text}"
            )
        if token.text.startswith("- "):
            return self._parse_list(index, indent)
        return self._parse_map(index, indent)

    def _parse_map(self, index: int, indent: int) -> tuple[dict[str, Any], int]:
        result: dict[str, Any] = {}
        while index < len(self.tokens):
            token = self.tokens[index]
            if token.indent < indent:
                break
            if token.indent > indent:
                raise YamlCompatError(
                    f"unexpected nested mapping content at {self.source}:{token.line_number}: {token.text}"
                )
            if token.text.startswith("- "):
                break
            match = self._key_value.match(token.text)
            if match is None:
                raise YamlCompatError(f"expected key/value at {self.source}:{token.line_number}: {token.text}")
            key = match.group(1).strip()
            remainder = match.group(2).strip()
            index += 1
            if remainder:
                result[key] = self._parse_scalar(remainder)
            elif index < len(self.tokens) and self.tokens[index].indent > indent:
                result[key], index = self._parse_block(index, self.tokens[index].indent)
            else:
                result[key] = None
        return result, index

    def _parse_list(self, index: int, indent: int) -> tuple[list[Any], int]:
        result: list[Any] = []
        while index < len(self.tokens):
            token = self.tokens[index]
            if token.indent < indent:
                break
            if token.indent > indent:
                raise YamlCompatError(
                    f"unexpected nested list content at {self.source}:{token.line_number}: {token.text}"
                )
            if not token.text.startswith("- "):
                break
            item = token.text[2:].strip()
            index += 1
            if not item:
                if index < len(self.tokens) and self.tokens[index].indent > indent:
                    value, index = self._parse_block(index, self.tokens[index].indent)
                else:
                    value = None
            elif self._key_value.match(item) is not None:
                synthetic = _Token(indent + 2, item, token.line_number)
                old = self.tokens
                self.tokens = old[: index - 1] + [synthetic] + old[index:]
                value, index = self._parse_map(index - 1, indent + 2)
                self.tokens = old
                index -= 1
            else:
                value = self._parse_scalar(item)
            result.append(value)
        return result, index

    def _parse_scalar(self, value: str) -> Any:
        lower = value.lower()
        if lower in {"true", "false"}:
            return lower == "true"
        if lower in {"null", "none", "~"}:
            return None
        if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
            try:
                return ast.literal_eval(value)
            except Exception:
                return value[1:-1]
        if value.startswith("[") and value.endswith("]"):
            return [self._parse_scalar(part.strip()) for part in self._split_inline(value[1:-1]) if part.strip()]
        if value.startswith("{") and value.endswith("}"):
            mapping: dict[str, Any] = {}
            for part in self._split_inline(value[1:-1]):
                if not part.strip():
                    continue
                if ":" not in part:
                    raise YamlCompatError(f"invalid inline mapping item: {part}")
                key, raw = part.split(":", 1)
                mapping[key.strip().strip("'\"")] = self._parse_scalar(raw.strip())
            return mapping
        if re.fullmatch(r"[-+]?\d+", value):
            try:
                return int(value)
            except ValueError:
                pass
        if re.fullmatch(r"[-+]?(?:\d+\.\d*|\d*\.\d+)(?:[eE][-+]?\d+)?", value) or re.fullmatch(r"[-+]?\d+[eE][-+]?\d+", value):
            try:
                return float(value)
            except ValueError:
                pass
        return value

    def _split_inline(self, text: str) -> list[str]:
        parts: list[str] = []
        start = 0
        depth = 0
        in_single = False
        in_double = False
        for idx, char in enumerate(text):
            if char == "'" and not in_double:
                in_single = not in_single
            elif char == '"' and not in_single:
                in_double = not in_double
            elif not in_single and not in_double:
                if char in "[{":
                    depth += 1
                elif char in "]}":
                    depth -= 1
                elif char == "," and depth == 0:
                    parts.append(text[start:idx])
                    start = idx + 1
        parts.append(text[start:])
        return parts
