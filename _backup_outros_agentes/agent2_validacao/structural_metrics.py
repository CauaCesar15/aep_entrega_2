"""
Extração de métricas estruturais relacionadas à acessibilidade para o Agente 2.

Critérios da Entrega 2:
- Extrair complexidade ciclomática por função.
- Extrair consistência de nomes de componentes front-end.
- Detectar mensagens de erro problemáticas.
- Extrair tags semânticas e linhas de código (LOC).
"""

from __future__ import annotations

import ast
import re
from typing import Any

# Padrões de mensagens de erro consideradas problemáticas para o usuário 60+
# (crípticas, genéricas, técnicas ou sem instrução de recuperação)
PADROES_ERRO_PROBLEMATICO: list[tuple[str, str]] = [
    (r"(?i)\berro\s+inesperado\b", "Mensagem excessivamente genérica ('Erro inesperado') sem orientação de recuperação."),
    (r"(?i)\binternal\s+server\s+error\b", "Jargão técnico em inglês ('Internal Server Error') que assusta usuários idosos."),
    (r"(?i)\bfalha\s+no\s+banco\b", "Erro técnico de infraestrutura ('Falha no banco') exposto ao usuário."),
    (r"(?i)\bnull\s*pointer\b", "Exceção técnica de programação ('Null pointer') exposta diretamente."),
    (r"(?i)\berro\s+500\b", "Código de status HTTP puro ('Erro 500') sem explicação em linguagem humana."),
    (r"(?i)\bexception\b", "Termo de exceção técnica ('Exception') presente na mensagem."),
    (r"(?i)\bundefined\b", "Mensagem contendo valor 'undefined' sem tratamento."),
    (r"(?i)\boperation\s+failed\b", "Mensagem em inglês sem tradução ou dica de ação."),
    (r"(?i)\bdados\s+inv[aá]lidos\b", "Mensagem vaga ('Dados inválidos') que não indica qual campo está incorreto."),
]

TAGS_SEMANTICAS_HTML = {
    "header", "nav", "main", "footer", "section", "article", "aside",
    "h1", "h2", "h3", "h4", "h5", "h6", "button", "label", "form", "output"
}


def extrair_complexidade_ciclomatica(codigo: str) -> dict[str, Any]:
    """
    Calcula a complexidade ciclomática por função via AST.
    Retorna métricas detalhadas por função e a média geral.
    """
    try:
        tree = ast.parse(codigo)
    except Exception:
        return {
            "media": 1.0,
            "maxima": 1.0,
            "funcoes": [],
            "total_funcoes": 0,
        }

    funcoes_cc: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            cc = 1
            for sub in ast.walk(node):
                if isinstance(sub, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.ExceptHandler)):
                    cc += 1
                elif isinstance(sub, ast.BoolOp):
                    cc += len(sub.values) - 1

            funcoes_cc.append({
                "nome": node.name,
                "linha": getattr(node, "lineno", 1),
                "complexidade": cc,
            })

    if not funcoes_cc:
        return {
            "media": 1.0,
            "maxima": 1.0,
            "funcoes": [],
            "total_funcoes": 0,
        }

    ccs = [f["complexidade"] for f in funcoes_cc]
    return {
        "media": round(sum(ccs) / len(ccs), 2),
        "maxima": max(ccs),
        "funcoes": funcoes_cc,
        "total_funcoes": len(funcoes_cc),
    }


def verificar_tags_semanticas(conteudo: str) -> dict[str, Any]:
    """
    Analisa tags semânticas em templates HTML, JSX ou strings de código.
    Verifica se há uso de tags estruturais acessíveis versus divs excessivas.
    """
    # Procura tags HTML: <tag ou <tag ...>
    encontradas = re.findall(r"<([a-zA-Z0-9]+)[\s>/]", conteudo)
    tags_lower = [t.lower() for t in encontradas]

    semanticas_presentes = list(set(tags_lower).intersection(TAGS_SEMANTICAS_HTML))
    total_tags = len(tags_lower)
    total_divs = tags_lower.count("div")

    # Razão de tags semânticas sobre divs (evita div soup)
    indice_semantico = 0.0
    if total_tags > 0:
        indice_semantico = round(len(semanticas_presentes) / max(1, len(semanticas_presentes) + total_divs), 2)

    return {
        "tags_semanticas_encontradas": sorted(semanticas_presentes),
        "total_tags": total_tags,
        "total_divs": total_divs,
        "indice_semantico": indice_semantico,
        "tem_main": "main" in semanticas_presentes,
        "tem_nav": "nav" in semanticas_presentes,
    }


def avaliar_consistencia_nomes(codigo: str) -> float:
    """
    Avalia a consistência no padrão de nomenclatura (snake_case vs camelCase).
    No ecossistema Ergane, inconsistência gera confusão na equipe e no mapeamento de componentes.
    Retorna score de 0.0 a 1.0 (ou 0 a 100%).
    """
    try:
        tree = ast.parse(codigo)
        nomes = [node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.ClassDef))]
    except Exception:
        nomes = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", codigo)

    if not nomes:
        return 1.0

    snake_count = sum(1 for n in nomes if re.match(r"^[a-z]+(_[a-z0-9]+)+$", n))
    camel_count = sum(1 for n in nomes if re.match(r"^[a-z]+[A-Z][a-zA-Z0-9]*$", n))
    pascal_count = sum(1 for n in nomes if re.match(r"^[A-Z][a-zA-Z0-9]*$", n))

    maior_grupo = max(snake_count, camel_count, pascal_count, 1)
    total_relevantes = max(1, snake_count + camel_count + pascal_count)

    consistencia = round(maior_grupo / total_relevantes, 2)
    return consistencia


def detectar_mensagens_erro_problematicas(codigo: str) -> list[str]:
    """
    Identifica mensagens de erro técnicas, vagas ou inadequadas para idosos
    presentes em literais de strings ou exceções no código.
    """
    problemas: list[str] = []

    # Extrai todas as strings literais do código
    try:
        tree = ast.parse(codigo)
        strings = [
            node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        ]
    except Exception:
        # Fallback via regex de aspas
        strings = re.findall(r"['\"]([^'\"]{3,100})['\"]", codigo)

    for texto in strings:
        for padrao, motivo in PADROES_ERRO_PROBLEMATICO:
            if re.search(padrao, texto):
                problemas.append(f"Trecho '{texto}': {motivo}")

    return sorted(list(set(problemas)))


def contar_loc(codigo: str) -> int:
    """
    Conta linhas efetivas de código (excluindo linhas vazias e comentários).
    """
    linhas = codigo.splitlines()
    loc = 0
    for linha in linhas:
        l = linha.strip()
        if l and not l.startswith("#"):
            loc += 1
    return loc
