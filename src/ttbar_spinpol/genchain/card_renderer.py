"""SINDARIN template renderer with fatal unresolved placeholders."""
from __future__ import annotations
import re, string
from pathlib import Path
PLACEHOLDER_RE=re.compile(r'\$\{[A-Z0-9_]+\}')
def render_text(template: str, context: dict[str, object]) -> str:
    text=string.Template(template).safe_substitute({k:str(v) for k,v in context.items()}); unresolved=sorted(set(PLACEHOLDER_RE.findall(text)))
    if unresolved: raise ValueError(f'unresolved placeholders: {unresolved}')
    return text
def render_file(template: Path, output: Path, context: dict[str, object]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True); output.write_text(render_text(template.read_text(), context), encoding='utf-8')
