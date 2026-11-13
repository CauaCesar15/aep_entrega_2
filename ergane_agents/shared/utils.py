"""
Funções utilitárias compartilhadas pelo sistema Ergane.

Inclui operações com YAML, JSON, timestamps e sistema de arquivos.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Carrega e retorna o conteúdo de um arquivo YAML."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    logger.debug("YAML carregado: %s", path)
    return data if isinstance(data, dict) else {}


def save_json(data: Any, path: str | Path) -> None:
    """Serializa *data* em JSON e grava no caminho especificado."""
    path = Path(path)
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    logger.debug("JSON salvo: %s", path)


def load_json(path: str | Path) -> Any:
    """Carrega e retorna o conteúdo de um arquivo JSON."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    logger.debug("JSON carregado: %s", path)
    return data


def timestamp_now() -> str:
    """Retorna o timestamp atual em formato ISO 8601."""
    return datetime.now().isoformat()


def ensure_dir(path: str | Path) -> Path:
    """Cria o diretório (e pais) se não existir e retorna o ``Path``."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path
