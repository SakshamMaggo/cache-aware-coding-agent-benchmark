from src.agent_backend import NoFixer, RuleFixer


def test_no_fixer_returns_same_code():
    fixer = NoFixer()
    code = "def add_numbers(a, b):\n    return a - b\n"

    fixed = fixer.fix(
        task_id="task_001",
        task_text="Fix addition.",
        buggy_code=code,
    )

    assert fixed == code
    assert fixer.last_call["model"] == "none"


def test_rule_fixer_fixes_known_task():
    fixer = RuleFixer()
    code = "def add_numbers(a, b):\n    return a - b\n"

    fixed = fixer.fix(
        task_id="task_001",
        task_text="Fix addition.",
        buggy_code=code,
    )

    assert "return a + b" in fixed
    assert fixer.last_call["model"] == "rule_based"

def test_get_backend_type_detects_hosted_backend():
    from src.model_client import get_backend_type

    assert get_backend_type(None) == "hosted"


def test_get_backend_type_detects_local_backend(monkeypatch):
    from src.model_client import get_backend_type

    monkeypatch.delenv("MODEL_BACKEND", raising=False)

    assert (
        get_backend_type("http://localhost:8000/v1")
        == "local_openai_compatible"
    )
