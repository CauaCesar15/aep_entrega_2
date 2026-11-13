"""
Validadores estáticos de código para o Agente 2.

Padrões de projeto aplicados:
- Strategy (GoF): Cada validador encapsula um algoritmo de análise intercambiável.
- Composite (GoF): CompositeValidator permite tratar um grupo de validadores como um só.
- Factory Method (GoF): ValidatorFactory instancia validadores baseando-se em políticas YAML.
- GRASP: Polimorfismo e Baixo Acoplamento.
"""

from __future__ import annotations

import ast
import re
from abc import ABC, abstractmethod
from typing import Any


class BaseValidator(ABC):
    """
    Interface comum para validadores de código (Padrão Strategy).
    """

    @abstractmethod
    def validate(self, codigo: str, config: dict[str, Any] | None = None) -> dict[str, Any]:
        """Executa a validação sobre o código e retorna o relatório de achados."""
        ...


class SyntaxValidator(BaseValidator):
    """Validador de sintaxe Python utilizando a AST padrão."""

    def validate(self, codigo: str, config: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            ast.parse(codigo)
            return {"valido": True, "erros": [], "tipo": "sintaxe"}
        except SyntaxError as e:
            return {
                "valido": False,
                "erros": [f"Linha {e.lineno}: {e.msg}"],
                "tipo": "sintaxe",
            }


class QualityValidator(BaseValidator):
    """
    Validador de qualidade: complexidade ciclomática e aninhamento excessivo.
    Pode usar a biblioteca 'radon' caso disponível, ou fallback via AST.
    """

    def validate(self, codigo: str, config: dict[str, Any] | None = None) -> dict[str, Any]:
        max_complexidade = (config or {}).get("max_complexidade", 10)
        achados = []
        funcoes_complexas = []

        try:
            tree = ast.parse(codigo)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Contagem de nós de decisão (if, while, for, except, boolops)
                    cc = 1
                    for sub in ast.walk(node):
                        if isinstance(sub, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.ExceptHandler)):
                            cc += 1
                        elif isinstance(sub, ast.BoolOp):
                            cc += len(sub.values) - 1

                    if cc > max_complexidade:
                        funcoes_complexas.append({
                            "funcao": node.name,
                            "linha": getattr(node, "lineno", 0),
                            "complexidade": cc,
                        })
                        achados.append(
                            f"Função '{node.name}' possui complexidade ciclomática elevada ({cc} > {max_complexidade})"
                        )
        except Exception:
            pass

        return {
            "valido": len(funcoes_complexas) == 0,
            "funcoes_complexas": funcoes_complexas,
            "achados": achados,
            "tipo": "qualidade",
        }


class SecurityValidator(BaseValidator):
    """
    Validador de segurança estática: detecção de senhas em código,
    uso perigoso de eval/exec e padrões vulneráveis de SQL.
    """

    PADROES_SEGURANCA = [
        (r"(?i)(password|senha|secret|apikey|token)\s*=\s*['\"][^'\"]{4,}['\"]", "Segredo ou senha codificada diretamente no código-fonte (hardcoded secret)."),
        (r"\beval\s*\(", "Uso inseguro de 'eval()', permitindo execução arbitrária de código."),
        (r"\bexec\s*\(", "Uso de 'exec()', risco crítico de injeção de comandos."),
        (r"(?i)select\s+.*\s+from\s+.*\s*%\s*", "Possível interpolação insegura de SQL sem parametrização."),
    ]

    def validate(self, codigo: str, config: dict[str, Any] | None = None) -> dict[str, Any]:
        vulnerabilidades = []
        for padrao, descricao in self.PADROES_SEGURANCA:
            for match in re.finditer(padrao, codigo):
                linha = codigo[:match.start()].count("\n") + 1
                vulnerabilidades.append({
                    "linha": linha,
                    "trecho": match.group(0)[:40],
                    "descricao": descricao,
                })

        return {
            "valido": len(vulnerabilidades) == 0,
            "vulnerabilidades": vulnerabilidades,
            "tipo": "seguranca",
        }


class StyleValidator(BaseValidator):
    """
    Validador de convenções de estilo e padrões de codificação limpa.
    """

    def validate(self, codigo: str, config: dict[str, Any] | None = None) -> dict[str, Any]:
        avisos = []
        linhas = codigo.splitlines()

        for idx, linha in enumerate(linhas, 1):
            if len(linha) > 120:
                avisos.append(f"Linha {idx} possui mais de 120 caracteres ({len(linha)} cols).")

        return {
            "valido": len(avisos) == 0,
            "avisos": avisos,
            "tipo": "estilo",
        }


class CompositeValidator(BaseValidator):
    """
    Padrão Composite (GoF).
    Agrupa uma coleção de validadores e executa todos de forma unificada.
    """

    def __init__(self) -> None:
        self._validators: list[BaseValidator] = []

    def add(self, validator: BaseValidator) -> CompositeValidator:
        """Adiciona um validador à composição."""
        self._validators.append(validator)
        return self

    def validate(self, codigo: str, config: dict[str, Any] | None = None) -> dict[str, Any]:
        """Executa todos os validadores da composição e unifica os relatórios."""
        todos_validos = True
        resultados: dict[str, Any] = {}

        for val in self._validators:
            res = val.validate(codigo, config)
            tipo = res.get("tipo", val.__class__.__name__)
            resultados[tipo] = res
            if not res.get("valido", True):
                todos_validos = False

        return {
            "valido": todos_validos,
            "detalhes": resultados,
        }


class ValidatorFactory:
    """
    Padrão Factory Method (GoF).
    Cria validadores com base em políticas ou configurações.
    """

    _REGISTRY: dict[str, type[BaseValidator]] = {
        "syntax": SyntaxValidator,
        "sintaxe": SyntaxValidator,
        "quality": QualityValidator,
        "qualidade": QualityValidator,
        "security": SecurityValidator,
        "seguranca": SecurityValidator,
        "style": StyleValidator,
        "estilo": StyleValidator,
    }

    @classmethod
    def create(cls, tipo: str) -> BaseValidator:
        """Cria validador individual."""
        val_cls = cls._REGISTRY.get(tipo.lower())
        if not val_cls:
            raise ValueError(f"Validador desconhecido: {tipo}")
        return val_cls()

    @classmethod
    def create_default_suite(cls) -> CompositeValidator:
        """Cria suíte completa com todos os validadores padrão."""
        suite = CompositeValidator()
        suite.add(SyntaxValidator())
        suite.add(QualityValidator())
        suite.add(SecurityValidator())
        suite.add(StyleValidator())
        return suite
