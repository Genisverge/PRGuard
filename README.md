# PRGuard

PRGuard es una prueba de concepto de un agente de IA que revisa posibles problemas de seguridad en código Python. Combina el análisis estático de Bandit con la lectura e interpretación del código mediante un modelo local ejecutado con Ollama.

Está pensado como un proyecto de aprendizaje y demostración. Los hallazgos del modelo son hipótesis que deben revisarse: PRGuard no garantiza encontrar todas las vulnerabilidades ni demuestra que puedan explotarse.

## Cómo funciona

1. Git consulta los cambios en `demo_repo/` respecto a `HEAD`.
2. Bandit analiza los archivos Python de ese directorio.
3. El agente de LangChain puede leer archivos relevantes y revisar su lógica.
4. Se genera un informe en Markdown que puede consultarse y descargarse desde la interfaz web.

La interfaz está hecha con Streamlit y se comunica con una API de FastAPI. El agente utiliza LangChain y Ollama; las tres herramientas (`get_git_diff`, `run_bandit` y `read_file`) están definidas en `app/tools.py`.

```text
Navegador → Streamlit → FastAPI → LangChain + Ollama
                                      ├── Git diff
                                      ├── Bandit
                                      └── Lectura de archivos Python
```

La revisión se limita al directorio local `demo_repo/` y no ejecuta el código analizado.

## Puesta en marcha con Docker

Es la opción más directa para reproducir la aplicación. Necesitas Git, Docker con Compose y Ollama instalado y en ejecución. En Windows puedes utilizar Docker Desktop; el modelo de Ollama se ejecuta en el ordenador, no dentro de los contenedores.

Primero, clona el repositorio:

```bash
git clone https://github.com/Genisverge/PRGuard.git
cd PRGuard
```

Comprueba el nombre exacto de un modelo que admita llamadas a herramientas (`tool calling`) y descárgalo si hace falta:

```bash
ollama list
ollama pull NOMBRE_DEL_MODELO
```

Sustituye `NOMBRE_DEL_MODELO` por el nombre real, incluido su tag. Configura la variable `PRGUARD_MODEL` en la misma terminal desde la que iniciarás Compose.

En PowerShell (Windows):

```powershell
$env:PRGUARD_MODEL="NOMBRE_DEL_MODELO"
docker compose up --build
```

En Bash (Linux, macOS o WSL):

```bash
export PRGUARD_MODEL="NOMBRE_DEL_MODELO"
docker compose up --build
```

Abre http://localhost:8501 para usar la interfaz. La documentación de la API está en http://localhost:8000/docs. Para detener la aplicación, pulsa `Ctrl+C` y ejecuta `docker compose down`.

La primera construcción necesita conexión a Internet para descargar la imagen base y las dependencias. El modelo también debe descargarse por adelantado. Comprueba que Docker puede comunicarse con Ollama mediante `host.docker.internal:11434` antes de utilizar la demo.

## Ejecución sin Docker

Con Python 3.12 y Ollama disponibles, desde la raíz del proyecto:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PRGUARD_MODEL="NOMBRE_DEL_MODELO"
python -m pytest -q
```

Inicia la API en una terminal:

```bash
python -m uvicorn app.api:app --host 127.0.0.1 --port 8000
```

Y la interfaz en otra terminal, con el mismo entorno virtual:

```bash
python -m streamlit run app/ui.py --server.headless true
```

También puedes ejecutar el agente directamente con `python -m app.agent`.

## Estructura del proyecto

- `app/agent.py`: configura el modelo y el agente de LangChain.
- `app/tools.py`: implementa Git diff, Bandit y la lectura restringida de archivos.
- `app/api.py`: expone `GET /health` y `POST /analyze`.
- `app/ui.py`: interfaz de Streamlit y descarga del informe.
- `demo_repo/`: ejemplos para la demostración, incluido código intencionadamente inseguro.
- `tests/`: pruebas de herramientas y de los endpoints de la API.
- `Dockerfile` y `compose.yaml`: construcción y ejecución de la aplicación en contenedores.

## Pruebas y ejemplos

Ejecuta `python -m pytest -q` en el entorno Python para pasar las pruebas. Se comprueba la API, la lectura permitida y denegada de archivos y la detección de B602 mediante Bandit. La prueba del endpoint de análisis simula la respuesta del agente: no evalúa si el LLM encuentra todas las vulnerabilidades.

En `demo_repo/login.py` hay una llamada a `subprocess` con `shell=True`, identificada por Bandit como B602. En `demo_repo/documents.py` existe una condición de autorización que contradice la regla indicada en su docstring: solo el propietario debería poder editar el documento, incluso si es público. Este segundo caso permite observar las limitaciones del razonamiento del modelo.

Después de clonar el proyecto, `git diff HEAD` normalmente no mostrará cambios. Es el comportamiento esperado de una copia limpia: Bandit seguirá revisando los archivos existentes. Para demostrar el funcionamiento de Git diff, modifica temporalmente un archivo de `demo_repo/` y repite el análisis sin hacer commit.

## Limitaciones

- Solo revisa archivos Python del repositorio de demostración autorizado; no analiza repositorios remotos arbitrarios.
- El modelo utilizado afecta a la calidad y al tiempo de respuesta. Debe admitir `tool calling`.
- Los resultados del LLM pueden contener errores, falsos positivos, falsos negativos o recomendaciones incorrectas.
- No se ejecuta el código del repositorio analizado ni se verifica la explotabilidad de los hallazgos.
- La API no incorpora autenticación y los servicios están configurados para uso local. No deben exponerse directamente a Internet.

GitHub distribuye el código y la documentación, pero no aloja la aplicación en ejecución. Cada persona que lo clone debe disponer de su propio entorno y modelo de Ollama.
