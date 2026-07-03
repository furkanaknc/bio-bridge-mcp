from pathlib import Path

from dotenv import load_dotenv


def load_project_env() -> None:
    project_root = Path(__file__).resolve().parents[2]
    dotenv_path = project_root / ".env"
    load_dotenv(dotenv_path=dotenv_path, override=False)
