"""
Extratores de metadados de documentação e código.

Aplica os padrões de projeto:
- Factory Method (GoF): ExtractorFactory cria instâncias adequadas de extratores.
- Adapter (GoF): SourceAdapter normaliza diferentes origens (arquivos, strings, commits).
- Especialista (GRASP): cada extrator é especialista em uma fonte de metadados.
"""

from __future__ import annotations

import ast
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseExtractor(ABC):
    """Classe base abstrata para todos os extratores de metadados."""

    @abstractmethod
    def extract(self, source: Any) -> dict[str, Any]:
        """Extrai metadados da fonte fornecida."""
        ...


class DocstringExtractor(BaseExtractor):
    """
    Extrator especialista em analisar código Python usando AST
    para extrair docstrings, nomes de funções, classes e métodos.
    """

    def extract(self, source: str) -> dict[str, Any]:
        """
        Analisa código Python via AST e extrai:
        - docstrings do módulo, funções e classes
        - contagem de elementos documentados vs totais
        - lista de nomes de variáveis, funções e parâmetros
        """
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            return {
                "erro_sintaxe": str(e),
                "total_funcoes": 0,
                "funcoes_documentadas": 0,
                "total_classes": 0,
                "classes_documentadas": 0,
                "docstrings": [],
                "nomes": [],
            }

        docstrings: list[str] = []
        nomes: list[str] = []
        total_funcoes = 0
        funcoes_com_doc = 0
        total_classes = 0
        classes_com_doc = 0

        # Docstring do módulo
        mod_doc = ast.get_docstring(tree)
        if mod_doc:
            docstrings.append(mod_doc)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                total_funcoes += 1
                nomes.append(node.name)
                for arg in node.args.args:
                    nomes.append(arg.arg)
                doc = ast.get_docstring(node)
                if doc:
                    funcoes_com_doc += 1
                    docstrings.append(doc)

            elif isinstance(node, ast.ClassDef):
                total_classes += 1
                nomes.append(node.name)
                doc = ast.get_docstring(node)
                if doc:
                    classes_com_doc += 1
                    docstrings.append(doc)

            elif isinstance(node, ast.Name):
                nomes.append(node.id)

        # Deduplicar nomes preservando ordem
        nomes_unicos = list(dict.fromkeys(nomes))

        return {
            "total_funcoes": total_funcoes,
            "funcoes_documentadas": funcoes_com_doc,
            "total_classes": total_classes,
            "classes_documentadas": classes_com_doc,
            "total_elementos": total_funcoes + total_classes,
            "total_documentados": funcoes_com_doc + classes_com_doc,
            "docstrings": docstrings,
            "nomes": nomes_unicos,
        }


class CommitExtractor(BaseExtractor):
    """
    Extrator de mensagens de commits do repositório Git.
    """

    def extract(self, source: Any) -> dict[str, Any]:
        """
        Processa mensagens de commits passadas como lista ou string.
        """
        if isinstance(source, list):
            commits = source
        elif isinstance(source, str):
            commits = [line.strip() for line in source.splitlines() if line.strip()]
        else:
            commits = []

        return {
            "total_commits": len(commits),
            "mensagens": commits,
        }


class SourceAdapter:
    """
    Padrão Adapter (GoF).
    Adapta diferentes formatos de entrada (caminho de arquivo, código bruto,
    ou payload estruturado) em um formato interno padrão para os extratores.
    """

    @staticmethod
    def adapt(input_data: str | Path | dict[str, Any]) -> tuple[str, str]:
        """
        Retorna uma tupla (nome_arquivo_ou_origem, conteudo_texto).
        """
        if isinstance(input_data, (str, Path)):
            path = Path(input_data)
            if path.exists() and path.is_file():
                try:
                    conteudo = path.read_text(encoding="utf-8")
                    return str(path.name), conteudo
                except Exception:
                    conteudo = path.read_text(encoding="latin-1", errors="ignore")
                    return str(path.name), conteudo
            # Se for string de código puro
            return "inline_code.py", str(input_data)

        if isinstance(input_data, dict):
            origem = input_data.get("arquivo", input_data.get("filename", "desconhecido.py"))
            conteudo = input_data.get("codigo", input_data.get("content", ""))
            return origem, conteudo

        return "unknown.py", str(input_data)


class ExtractorFactory:
    """
    Padrão Factory Method (GoF).
    Cria extratores específicos com base no tipo solicitado.
    """

    _EXTRACTORS = {
        "docstring": DocstringExtractor,
        "ast": DocstringExtractor,
        "commit": CommitExtractor,
    }

    @classmethod
    def create(cls, extractor_type: str) -> BaseExtractor:
        """Cria e retorna o extrator correspondente."""
        extractor_cls = cls._EXTRACTORS.get(extractor_type.lower())
        if not extractor_cls:
            raise ValueError(f"Tipo de extrator não suportado: {extractor_type}")
        return extractor_cls()
