"""
Cálculo de métricas de documentação para o Agente 1.

Métricas calculadas:
- Cobertura de docstrings por arquivo (0 a 100%)
- Índice de legibilidade Flesch Reading Ease (com fallback determinístico em português)
- Tamanho médio de frases (palavras por frase)
- Detecção de jargão técnico prejudicial ao público 60+
- Avaliação de clareza de nomes de variáveis/funções
"""

from __future__ import annotations

import re
from typing import Any

# Lista canônica de jargões técnicos que confundem usuários idosos (60+)
JARGOES_TECNICOS_COMUNS: list[str] = [
    "api",
    "backend",
    "frontend",
    "token",
    "payload",
    "endpoint",
    "deploy",
    "commit",
    "stack trace",
    "middleware",
    "callback",
    "nullpointer",
    "depreciado",
    "deprecated",
    "parse",
    "parsing",
    "timeout",
    "buffer",
    "thread",
    "rollback",
    "cache",
    "jwt",
    "oauth",
    "webhook",
    "crud",
    "rest",
    "graphql",
    "payload",
    "regex",
    "hash",
    "cors",
    "async",
    "await",
    "socket",
    "dns",
    "gateway",
]


def calcular_cobertura_docstrings(ast_data: dict[str, Any]) -> float:
    """
    Calcula a porcentagem de elementos (funções e classes) que possuem docstring.
    Retorna valor de 0.0 a 100.0.
    """
    total = ast_data.get("total_elementos", 0)
    if total == 0:
        # Se não há funções nem classes, verifica se o módulo tem docstring
        if ast_data.get("docstrings"):
            return 100.0
        return 0.0

    documentados = ast_data.get("total_documentados", 0)
    return round((documentados / total) * 100.0, 2)


def _contar_silabas_pt(palavra: str) -> int:
    """
    Heurística simples para contagem de sílabas em português baseada em núcleos vocálicos.
    """
    palavra = palavra.lower().strip()
    if not palavra:
        return 0
    # Agrupa vogais e encontros
    vogais = re.findall(r"[aeiouáéíóúâêîôûãõàü]+", palavra)
    return max(1, len(vogais))


def calcular_indice_flesch(texto: str) -> float:
    """
    Calcula o índice de facilidade de leitura Flesch (Reading Ease).
    Tenta usar a biblioteca textstat; caso indisponível, usa fórmula determinística adaptada:
    Flesch = 206.835 - (1.015 * ASL) - (84.6 * ASW)
    Onde:
      ASL = Média de palavras por sentença
      ASW = Média de sílabas por palavra
    Escala:
      75-100: Muito fácil / Fácil (Ideal para idosos)
      50-74: Médio / Razoável
      < 50: Difícil / Confuso (Barreira para idosos)
    """
    texto = texto.strip()
    if not texto:
        return 0.0

    try:
        import textstat  # type: ignore
        return float(textstat.flesch_reading_ease(texto))
    except Exception:
        # Fallback determinístico próprio
        frases = [f.strip() for f in re.split(r"[.!?]+", texto) if f.strip()]
        if not frases:
            frases = [texto]

        palavras = [p.strip() for p in re.findall(r"\b\w+\b", texto) if p.strip()]
        if not palavras:
            return 0.0

        total_frases = len(frases)
        total_palavras = len(palavras)
        total_silabas = sum(_contar_silabas_pt(p) for p in palavras)

        asl = total_palavras / max(1, total_frases)
        asw = total_silabas / max(1, total_palavras)

        score = 206.835 - (1.015 * asl) - (84.6 * asw)
        # Limitar entre 0.0 e 100.0
        score = max(0.0, min(100.0, score))
        return round(score, 2)


def calcular_tamanho_medio_frases(texto: str) -> float:
    """
    Calcula a média de palavras por frase.
    Frases acima de 20 palavras costumam ser barreiras cognitivas para o público sênior.
    """
    texto = texto.strip()
    if not texto:
        return 0.0

    frases = [f.strip() for f in re.split(r"[.!?]+", texto) if f.strip()]
    if not frases:
        return 0.0

    palavras = re.findall(r"\b\w+\b", texto)
    if not palavras:
        return 0.0

    return round(len(palavras) / len(frases), 2)


def detectar_jargao(texto: str, lista_jargoes: list[str] | None = None) -> list[str]:
    """
    Identifica termos técnicos presentes no texto que geram atrito cognitivo.
    Retorna lista de termos únicos detectados.
    """
    if not texto:
        return []

    jargoes_alvo = lista_jargoes or JARGOES_TECNICOS_COMUNS
    texto_lower = texto.lower()
    detectados: list[str] = []

    for jargao in jargoes_alvo:
        padrao = rf"\b{re.escape(jargao.lower())}\b"
        if re.search(padrao, texto_lower):
            detectados.append(jargao)

    return sorted(list(set(detectados)))


def avaliar_clareza_nomes(nomes: list[str]) -> float:
    """
    Avalia a clareza de uma lista de nomes de variáveis/funções.
    Critérios:
    - Nomes muito curtos (1 ou 2 letras como 'x', 'i', 'cb') perdem pontos.
    - Abreviações crípticas perdem pontos.
    - Nomes descritivos (snake_case ou camelCase claros) ganham pontos.
    Retorna uma nota de 0.0 a 100.0.
    """
    if not nomes:
        return 100.0

    pontos = 0.0
    for nome in nomes:
        nome_limpo = nome.strip("_")
        # Nomes de 1 caractere são crípticos
        if len(nome_limpo) <= 1:
            pontos += 10.0
        elif len(nome_limpo) == 2 and nome_limpo not in ("id", "ok", "me"):
            pontos += 30.0
        elif len(nome_limpo) < 4:
            pontos += 50.0
        elif re.match(r"^[a-z]+(_[a-z0-9]+)+$", nome_limpo) or re.match(r"^[a-z]+[A-Z][a-zA-Z0-9]*$", nome_limpo):
            pontos += 100.0
        else:
            pontos += 80.0

    return round(pontos / len(nomes), 2)
