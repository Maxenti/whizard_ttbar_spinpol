from pathlib import Path


def test_upgrade_files_exist() -> None:
    root = Path(__file__).resolve().parents[2]
    assert (root / "scripts/qis/build_paper_spin_v3p1.py").is_file()
    assert (root / "scripts/qis/run_paper_spin_v3p1.sh").is_file()
    assert (root / "scripts/qis/verify_paper_spin_bundle.py").is_file()
