import hashlib
from pathlib import Path


def tree_hash(root: Path) -> str:
    hasher = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file():
            hasher.update(str(path.relative_to(root)).encode())
            hasher.update(path.read_bytes())
    return hasher.hexdigest()


def test_additive_package_does_not_require_baseline_mutation(tmp_path):
    baseline = tmp_path / "baseline"
    baseline.mkdir()
    (baseline / "gate.json").write_text('{"status":"pass"}\n')
    before = tree_hash(baseline)
    output = tmp_path / "paper_spin"
    output.mkdir()
    (output / "manifest.json").write_text('{"baseline_modified":false}\n')
    assert tree_hash(baseline) == before
