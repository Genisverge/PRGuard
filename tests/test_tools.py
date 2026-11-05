from app.tools import read_file, run_bandit


def test_can_read_demo_file():
    assert "def check_host" in read_file("demo_repo/login.py")


def test_cannot_read_outside_demo_repo():
    assert "fuera del directorio permitido" in read_file("app/agent.py")


def test_bandit_finds_demo_vulnerability():
    report = run_bandit()
    assert "ID: B602" in report
    assert "Severidad: HIGH" in report
