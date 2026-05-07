from pathlib import Path


REPORTS_DIR = Path("reports_salvos")


def ensure_reports_dir() -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    return REPORTS_DIR


def sanitize_report_name(name: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in " _-" else "_" for char in str(name))
    cleaned = "_".join(part for part in cleaned.strip().split())
    return cleaned or "relatorio"


def save_report_file(file_name: str, content: bytes) -> Path:
    reports_dir = ensure_reports_dir()
    target = reports_dir / file_name
    target.write_bytes(content)
    return target


def list_saved_reports() -> list[Path]:
    reports_dir = ensure_reports_dir()
    return sorted(reports_dir.glob("*.png"), key=lambda path: path.stat().st_mtime, reverse=True)


def delete_report_file(file_name: str) -> bool:
    target = ensure_reports_dir() / Path(file_name).name
    if not target.exists() or target.parent != ensure_reports_dir():
        return False
    target.unlink()
    return True