from pathlib import Path


BASE_PATH = Path(__file__).parent


def load_prompt(relative_path: str) -> str:

    prompt_path = BASE_PATH / relative_path

    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()