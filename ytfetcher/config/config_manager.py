import json
from pathlib import Path

CONFIG_FILE = Path.home() / ".ytfetcher" / "config" / "config_cli.json"

def save_api_key(api_key: str):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

    data = {"api_key": api_key}
    with open(CONFIG_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file)
    print(f"API key saved to {CONFIG_FILE}")

def load_api_key() -> str | None:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("api_key")
    return None