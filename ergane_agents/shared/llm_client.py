"""
Cliente wrapper para a API REST do Ollama.

Fornece geração de texto via modelo local com fallback gracioso
quando o serviço não está disponível.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

_DEFAULT_MODEL = "llama3.2:3b"
_DEFAULT_BASE_URL = "http://localhost:11434"
_GENERATE_PATH = "/api/generate"
_TIMEOUT_SECONDS = 120


class LLMClient:
    """
    Wrapper leve para a API de geração do Ollama.

    Parâmetros
    ----------
    base_url : str
        URL base do serviço Ollama (padrão ``http://localhost:11434``).
    model : str
        Modelo padrão a ser utilizado nas chamadas de geração.
    """

    def __init__(
        self,
        base_url: str = _DEFAULT_BASE_URL,
        model: str = _DEFAULT_MODEL,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Verifica se o serviço Ollama está acessível."""
        try:
            resp = requests.get(self.base_url, timeout=5)
            return resp.status_code == 200
        except requests.ConnectionError:
            logger.warning("Ollama indisponível em %s.", self.base_url)
            return False
        except Exception:
            logger.exception("Erro inesperado ao verificar disponibilidade do Ollama.")
            return False

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        **kwargs: Any,
    ) -> str | None:
        """
        Gera texto a partir de *prompt* usando o modelo especificado.

        Retorna ``None`` e registra um aviso caso o Ollama não esteja
        disponível ou ocorra qualquer erro na chamada.

        Parâmetros
        ----------
        prompt : str
            Texto de entrada para o modelo.
        model : str, opcional
            Modelo a utilizar; se omitido, usa o padrão da instância.
        **kwargs
            Parâmetros adicionais repassados ao payload da API.
        """
        url = f"{self.base_url}{_GENERATE_PATH}"
        payload: dict[str, Any] = {
            "model": model or self.model,
            "prompt": prompt,
            "stream": False,
            **kwargs,
        }

        try:
            resp = requests.post(url, json=payload, timeout=_TIMEOUT_SECONDS)
            resp.raise_for_status()
            body = resp.json()
            return body.get("response", "")
        except requests.ConnectionError:
            logger.warning(
                "Ollama indisponível em %s. Retornando None.", self.base_url
            )
            return None
        except requests.Timeout:
            logger.warning("Timeout ao chamar Ollama (%ss).", _TIMEOUT_SECONDS)
            return None
        except Exception:
            logger.exception("Erro inesperado ao gerar texto via Ollama.")
            return None
