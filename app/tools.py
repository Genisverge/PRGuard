from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ALLOWED_DIR = PROJECT_ROOT / "demo_repo"

def read_file(path: str) -> str:
    file_path = (ALLOWED_DIR / path).resolve()

    if not file_path.is_relative_to(ALLOWED_DIR.resolve()):
        return "Error: archivo fuera del directorio permitido."

    if not file_path.is_file():
        return "Error: el archivo no existe."

    if file_path.suffix != ".py":
        return "Error: solo se permiten archivos Python."

    if file_path.stat().st_size > 20_000:
        return "Error: archivo demasiado grande."

    return file_path.read_text(encoding="utf-8")