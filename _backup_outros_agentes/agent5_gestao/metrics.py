"""
Cálculo de métricas ágeis e lógica de priorização para o Agente 5.

Critérios da Entrega 2:
- Calcular velocity e burndown com precisão.
- Emitir alerta para tarefas de acessibilidade 60+ em risco.
- Priorizar automaticamente issues de erro financeiro.
"""

from __future__ import annotations

from typing import Any

from ergane_agents.agent5_gestao.adapters import ProjectTask


def calcular_velocity(sprints_concluidas: list[dict[str, Any]]) -> float:
    """
    Calcula a velocidade média da equipe em story points por sprint.
    """
    if not sprints_concluidas:
        return 20.0  # Velocidade nominal inicial estimada para equipe de 3

    pontos_totais = sum(s.get("pontos_entregues", 0) for s in sprints_concluidas)
    return round(pontos_totais / len(sprints_concluidas), 2)


def calcular_burndown(
    pontos_totais: int,
    dias_sprint: int,
    pontos_queimados_por_dia: list[int],
) -> list[dict[str, Any]]:
    """
    Gera a série temporal de burndown (ideal vs real).
    """
    burndown: list[dict[str, Any]] = []
    decremento_ideal = pontos_totais / max(1, dias_sprint)
    saldo_real = pontos_totais

    for dia in range(dias_sprint + 1):
        ideal = max(0.0, round(pontos_totais - (dia * decremento_ideal), 1))

        if dia == 0:
            saldo_real = pontos_totais
        elif dia <= len(pontos_queimados_por_dia):
            saldo_real = max(0, saldo_real - pontos_queimados_por_dia[dia - 1])
        else:
            saldo_real = saldo_real  # Projeção mantida

        burndown.append({
            "dia": dia,
            "ideal_restante": ideal,
            "real_restante": saldo_real,
        })

    return burndown


def priorizar_backlog(
    tarefas: list[ProjectTask],
    barreiras_agente3: list[dict[str, Any]] | None = None,
) -> list[ProjectTask]:
    """
    Aplica regra de negócio do Ergane:
    1. Erros financeiros têm prioridade máxima absoluta (P1)
    2. Barreiras de acessibilidade 60+ têm prioridade alta (P2)
    3. Documentação de suporte para idosos (P3)
    4. Funcionalidades comuns (P4)
    """
    def calcular_peso(task: ProjectTask) -> int:
        peso = 100
        titulo_lower = task.titulo.lower()

        # Critério: Priorização automática de erro financeiro
        if task.categoria == "financeiro" or any(k in titulo_lower for k in ["pix", "pagamento", "recibo", "nota fiscal", "nf-e", "mei"]):
            peso = 10  # P1

        # Barreiras de acessibilidade 60+
        elif task.categoria == "acessibilidade_60+" or any(k in titulo_lower for k in ["60+", "idoso", "fonte", "contraste", "teclado"]):
            peso = 20  # P2

        # Documentação e guias
        elif task.categoria == "documentacao" or "guia" in titulo_lower:
            peso = 30  # P3

        else:
            peso = 50  # P4

        # Tarefas bloqueadas ou em progresso ganham urgência
        if task.status == "in_progress":
            peso -= 2
        elif task.status == "blocked":
            peso -= 5

        return peso

    # Ordena pelo peso calculado
    tarefas_ordenadas = sorted(tarefas, key=calcular_peso)

    # Atribui prioridade sequencial de 1 a N
    for idx, t in enumerate(tarefas_ordenadas, 1):
        t.prioridade_calculada = idx

    return tarefas_ordenadas


def identificar_alertas_risco(tarefas: list[ProjectTask]) -> list[str]:
    """
    Emite alertas para tarefas de acessibilidade 60+ ou financeiras em risco de atraso.
    """
    alertas: list[str] = []

    for t in tarefas:
        if t.status in ("todo", "in_progress", "blocked"):
            if t.categoria == "acessibilidade_60+":
                if t.status == "blocked":
                    alertas.append(f"🚨 ALERTA CRÍTICO: Tarefa 60+ [{t.id}] '{t.titulo}' está BLOQUEADA!")
                elif t.status == "todo" and t.pontos >= 5:
                    alertas.append(f"⚠️ RISCO DE ATRASO: Tarefa 60+ [{t.id}] '{t.titulo}' possui alta pontuação ({t.pontos} pts) e ainda não foi iniciada.")

            elif t.categoria == "financeiro" and t.status in ("blocked", "todo"):
                alertas.append(f"💳 ATENÇÃO FINANCEIRA: Correção financeira [{t.id}] '{t.titulo}' requer prioridade imediata na sprint.")

    return alertas
