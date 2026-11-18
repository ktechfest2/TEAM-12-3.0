"""Writes the OpenAPI document so the web app can generate typed clients."""

import json
import sys
from pathlib import Path

from clarion_api.config import AppEnv, Settings
from clarion_api.main import create_app


def main() -> None:
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "openapi.json")
    app = create_app(Settings(app_env=AppEnv.TEST, _env_file=None))  # type: ignore[call-arg]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
