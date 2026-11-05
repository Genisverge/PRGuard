from pathlib import Path
import subprocess

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

def get_git_diff() -> str:
    command = [
        "git",
        "diff",
        "--no-ext-diff",
        "--no-textconv",
        "HEAD",
        "--",
        "demo_repo/"
    ]

    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    
    except subprocess.TimeoutExpired:
        return "Error: git diff tardó demasiado."

    except FileNotFoundError:
        return "Error: Git no está instalado o no se encuentra en el PATH."
    
    if result.returncode != 0:
        return "Error: git diff falló."

    if not result.stdout:
        return "No hay cambios en el repositorio."

    MAX_DIFF_CHARS = 15_000

    if len(result.stdout) > MAX_DIFF_CHARS:
        truncated_diff = result.stdout[:MAX_DIFF_CHARS]
        return truncated_diff + "\n[AVISO: diff truncado]."

    return result.stdout