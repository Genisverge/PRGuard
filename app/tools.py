from pathlib import Path
import subprocess
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ALLOWED_DIR = PROJECT_ROOT / "demo_repo"

def read_file(path: str) -> str:
    file_path = (PROJECT_ROOT / path).resolve()

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

def run_bandit() -> str:
    command = [
        "bandit",
        "-r",
        "demo_repo",
        "-f", 
        "json"
    ]

    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=15,
        )
    
    except subprocess.TimeoutExpired:
        return "Error: bandit tardó demasiado."

    except FileNotFoundError:
        return "Error: Bandit no está instalado o no se encuentra en el PATH."

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return "Error: Bandit no devolvió un JSON válido."

    if result.returncode not in (0, 1):
        return f"Error: Bandit terminó con código {result.returncode}."

    if not isinstance(data, dict):
        return "Error: el informe de Bandit no es un objeto JSON."

    errors = data.get("errors", [])

    if not isinstance(errors, list):
        return "Error: formato inesperado en los errores de Bandit."

    if errors:
        return f"Error: Bandit no pudo analizar correctamente todos los archivos: {errors[:3]}"

    findings = data.get("results")

    if not isinstance(findings, list):
        return "Error: el informe de Bandit no contiene una lista de resultados."

    MAX_FINDINGS = 20
    MAX_CODE_CHARS = 500
    summaries = []

    for finding in findings[:MAX_FINDINGS]:
        test_id = finding.get("test_id", "UNKNOWN")
        severity = finding.get("issue_severity", "UNKNOWN")
        confidence = finding.get("issue_confidence", "UNKNOWN")
        text = finding.get("issue_text", "UNKNOWN")
        code = finding.get("code", "UNKNOWN")
        code = str(code)[:MAX_CODE_CHARS]       
        line = finding.get("line_number", "UNKNOWN")
        filename = finding.get("filename", "UNKNOWN")
        summary = (
            f"ID: {test_id}\n"
            f"Severidad: {severity}\n"
            f"Confianza: {confidence}\n"
            f"Descripción: {text}\n"
            f"Código: {code}\n"
            f"Línea: {line}\n"
            f"Archivo: {filename}"
        )
        summaries.append(summary)
    
    header = f"Bandit ha detectado {len(findings)} posibles problemas de seguridad."

    if len(findings) > MAX_FINDINGS:
        header += f"\n[AVISO: solo se muestran los primeros {MAX_FINDINGS} hallazgos.]"

    return header + "\n\n" + "\n\n".join(summaries)

