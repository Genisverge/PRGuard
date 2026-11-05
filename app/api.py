from fastapi import FastAPI

app = FastAPI(title="PRGuard", description="Local Python security review")


def run_analysis():
    from app.agent import analyze
    return analyze()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
def analyze_repository():
    return {"report": run_analysis()}
