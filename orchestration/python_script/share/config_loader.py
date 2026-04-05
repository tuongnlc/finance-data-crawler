from pathlib import Path
from typing import Any

from src.shared.utils.load_yaml_config import load_config


def resolve_config_path(url: str, project_root: Path) -> Path:
    config_path = Path(url)
    if config_path.exists():
        return config_path

    potential_path = project_root / "configs" / url
    if potential_path.exists():
        return potential_path

    return config_path


def load_yaml_config(url: str, project_root: Path) -> dict[str, Any]:
    config_path = resolve_config_path(url, project_root)
    print(f"Loading config from: {config_path}")
    config = load_config(config_path)
    return config
