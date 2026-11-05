# PRGuard

**PRGuard** es una prueba de concepto de un agente de IA para revisar la seguridad de código Python. Combina **LangChain**, un modelo local mediante **Ollama**, **Git**, **Bandit**, **FastAPI**, **Streamlit** y **Docker Compose**.

El agente revisa código de un repositorio de demostración autorizado, utiliza herramientas de solo lectura y genera un informe en Markdown. **No ejecuta el código vulnerable**. Los hallazgos del LLM son hipótesis, no vulnerabilidades confirmadas; una revisión humana sigue siendo necesaria.

## Arquitectura

```text
Navegador → Streamlit (8501) → FastAPI (8000) → LangChain + Ollama
                                                    ├── Git diff
                                                    ├── Bandit
                                                    └── Lectura de archivos Python
```

- `app/agent.py`: crea el agente y gestiona su ejecución con LangChain.
- `app/tools.py`: implementa las tres herramientas restringidas a `demo_repo/`.
- `app/api.py`: expone `GET /health` y `POST /analyze` mediante FastAPI.
- `app/ui.py`: muestra la interfaz de Streamlit y permite descargar el informe.
- `demo_repo/`: archivos de ejemplo para evaluar el agente; contienen código intencionadamente vulnerable.
- `tests/`: pruebas de herramientas y de los endpoints de la API.

## Requisitos

- Python 3.12 (recomendado para reproducir el entorno de desarrollo).
- Ollama activo, con un modelo **compatible con tool calling** instalado.
- Git y Bandit (Bandit se instala mediante `requirements.txt`).
- Docker Desktop, **solo** si se quiere ejecutar con Compose.

Consulta el nombre exacto del modelo con `ollama list`.

## Ejecución local (WSL/Linux)

Desde la raíz del repositorio:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PRGUARD_MODEL="NOMBRE_EXACTO_DEL_MODELO"
python -m pytest -q
```

En una terminal, inicia el backend:

```bash
source .venv/bin/activate
export PRGUARD_MODEL="NOMBRE_EXACTO_DEL_MODELO"
python -m uvicorn app.api:app --host 127.0.0.1 --port 8000
```

En otra terminal, inicia la interfaz:

```bash
source .venv/bin/activate
python -m streamlit run app/ui.py --server.headless true
```

Abre <http://localhost:8501> y pulsa **Analizar repositorio**. También puedes consultar la documentación interactiva de la API en <http://localhost:8000/docs>.

## Ejecución con Docker Compose

Con Docker Desktop y Ollama arrancados, desde la raíz del repositorio:

```bash
export PRGUARD_MODEL="NOMBRE_EXACTO_DEL_MODELO"
docker compose up --build
```

Abre <http://localhost:8501>. Detén los servicios con `Ctrl+C` y `docker compose down`.

Compose monta el repositorio local en modo solo lectura para que Git pueda consultar `.git`. La API y la interfaz se publican únicamente en `127.0.0.1`. Ollama se ejecuta **fuera** de los contenedores: la API intenta alcanzarlo mediante `host.docker.internal:11434`. Si falla esa conexión, revisa la configuración de red de Docker Desktop y Ollama.

No publiques estos endpoints directamente en Internet: esta prueba de concepto no incorpora autenticación.

## Pruebas

```bash
python -m pytest -q
```

Las pruebas actuales verifican lectura permitida y denegada, detección del ejemplo B602 por Bandit, `/health` y la estructura de la respuesta de `/analyze`. La prueba de la API sustituye el análisis real por un resultado simulado: **no evalúa la precisión del modelo**.

## Escenarios y limitaciones

- `demo_repo/login.py`: usa `subprocess.run(..., shell=True)` y Bandit lo marca como B602.
- `demo_repo/documents.py`: incluye una función que contradice su regla de negocio de edición exclusiva por propietarios. Permite evaluar si el LLM detecta problemas de autorización no cubiertos por las reglas de Bandit.
- `git diff HEAD` solo muestra cambios locales no confirmados en archivos rastreados (o marcados con `git add -N`). Después de confirmar los archivos, es normal que no muestre cambios. Bandit puede seguir detectando problemas en el código existente.
- El resultado depende del modelo local y de sus capacidades: puede omitir problemas, inventar detalles o proponer correcciones incorrectas.
- La salida no demuestra explotabilidad y no sustituye una auditoría profesional.

**Nota:** GitHub almacena el código y su historial; no ejecuta automáticamente la aplicación. Quien clone el proyecto debe instalar y configurar Ollama y el modelo, además de las dependencias indicadas.
