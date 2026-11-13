"""
Preditores especializados de barreiras de acessibilidade 60+ para o Agente 3.

Padrões de projeto aplicados:
- Factory Method (GoF): PredictorFactory instancia preditores para cada categoria.
- Decorator (GoF): RuleDecorator adiciona regras contextuais 60+ dinamicamente.
- Especialista (GRASP): Cada preditor cuida de uma frente (Percepção, Operação, Compreensão, Fluxo).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ergane_agents.shared.models import BarreiraPreditiva, Severidade, TipoBarreira


class BasePredictor(ABC):
    """Classe base abstrata para preditores de acessibilidade."""

    def __init__(self, tipo: TipoBarreira) -> None:
        self.tipo = tipo

    @abstractmethod
    def predict(
        self,
        doc_metrics: dict[str, Any],
        struct_metrics: dict[str, Any],
        regras: list[dict[str, Any]] | None = None,
    ) -> list[BarreiraPreditiva]:
        """Prevê barreiras cruzando métricas e regras."""
        ...


class PercepcaoPredictor(BasePredictor):
    """
    Especialista em barreiras de Percepção:
    - Textos com fontes pequenas (< 16px / 18px)
    - Baixo contraste (< 4.5:1)
    - Alvos de clique pequenos (< 44px)
    - Ausência de tags semânticas visuais claras
    """

    def __init__(self) -> None:
        super().__init__(TipoBarreira.PERCEPCAO)

    def predict(
        self,
        doc_metrics: dict[str, Any],
        struct_metrics: dict[str, Any],
        regras: list[dict[str, Any]] | None = None,
    ) -> list[BarreiraPreditiva]:
        barreiras: list[BarreiraPreditiva] = []
        arquivo = struct_metrics.get("arquivo", "tela_front.html")
        tags = [t.lower() for t in struct_metrics.get("tags_semanticas", [])]
        total_tags = struct_metrics.get("total_tags", 0)
        total_divs = struct_metrics.get("total_divs", 0)

        # 1. Alvos de clique e contraste em botões / inputs
        if "button" in tags or "input" in tags or total_tags > 0:
            barreiras.append(
                BarreiraPreditiva(
                    tipo=self.tipo,
                    severidade=Severidade.ALTA,
                    arquivo=arquivo,
                    descricao=(
                        "Elementos interativos (botões/campos) identificados sem especificação explícita "
                        "de tamanho mínimo de alvo (44x44px) ou contraste de cores (mínimo 4.5:1)."
                    ),
                    sugestao_correcao=(
                        "Definir padding amplo para garantir alvos de clique ≥ 44x44px e aplicar contraste "
                        "mínimo de 4.5:1 no texto contra o fundo (WCAG 2.2 nível AA)."
                    ),
                )
            )

        # 2. Ausência de tags semânticas visuais
        indice_semantico = struct_metrics.get("indice_semantico", 1.0)
        if indice_semantico < 0.5 or total_divs > 3:
            barreiras.append(
                BarreiraPreditiva(
                    tipo=self.tipo,
                    severidade=Severidade.MEDIA,
                    arquivo=arquivo,
                    descricao="Estrutura com excesso de divs genéricas em relação a blocos semânticos visuais.",
                    sugestao_correcao="Adotar <header>, <main>, <section> e <footer> para orientar visualmente o idoso.",
                )
            )

        return barreiras


class OperacaoPredictor(BasePredictor):
    """
    Especialista em barreiras de Operação:
    - Navegação via teclado
    - Ausência de links de salto (skip links)
    - Falta de foco visual em inputs
    """

    def __init__(self) -> None:
        super().__init__(TipoBarreira.OPERACAO)

    def predict(
        self,
        doc_metrics: dict[str, Any],
        struct_metrics: dict[str, Any],
        regras: list[dict[str, Any]] | None = None,
    ) -> list[BarreiraPreditiva]:
        barreiras: list[BarreiraPreditiva] = []
        arquivo = struct_metrics.get("arquivo", "modulo.py")
        tags = [t.lower() for t in struct_metrics.get("tags_semanticas", [])]

        # 1. Ausência de skip link / nav explícito
        if "nav" not in tags:
            barreiras.append(
                BarreiraPreditiva(
                    tipo=self.tipo,
                    severidade=Severidade.MEDIA,
                    arquivo=arquivo,
                    descricao=(
                        "Ausência de link de salto ('Pular para o conteúdo principal') e de tag <nav>. "
                        "Usuários que navegam por teclado precisam pressionar Tab repetidamente até o conteúdo."
                    ),
                    sugestao_correcao="Adicionar link de salto no início da tela e estruturar menus dentro da tag <nav>.",
                )
            )

        # 2. Complexidade ciclomática elevada em manipuladores de evento
        cc_media = struct_metrics.get("complexidade_media", 1.0)
        if cc_media > 4.0:
            barreiras.append(
                BarreiraPreditiva(
                    tipo=self.tipo,
                    severidade=Severidade.ALTA,
                    arquivo=arquivo,
                    descricao=f"Lógica operacional complexa nos componentes (CC média={cc_media}). Pode exigir múltiplos passos rápidos.",
                    sugestao_correcao="Simplificar o fluxo operacional, removendo timeouts curtos e permitindo confirmações em etapa única.",
                )
            )

        return barreiras


class CompreensaoPredictor(BasePredictor):
    """
    Especialista em barreiras de Compreensão:
    - Jargões técnicos excessivos
    - Índice Flesch baixo (< 50)
    - Mensagens de erro crípticas ou sem orientação
    """

    def __init__(self) -> None:
        super().__init__(TipoBarreira.COMPREENSAO)

    def predict(
        self,
        doc_metrics: dict[str, Any],
        struct_metrics: dict[str, Any],
        regras: list[dict[str, Any]] | None = None,
    ) -> list[BarreiraPreditiva]:
        barreiras: list[BarreiraPreditiva] = []
        arquivo = doc_metrics.get("arquivo", struct_metrics.get("arquivo", "app.py"))

        # 1. Cruzamento com Flesch
        flesch = doc_metrics.get("indice_flesch", 70.0)
        if flesch < 50.0:
            barreiras.append(
                BarreiraPreditiva(
                    tipo=self.tipo,
                    severidade=Severidade.ALTA,
                    arquivo=arquivo,
                    descricao=(
                        f"Índice de legibilidade Flesch ({flesch}) abaixo do limite seguro (50.0). "
                        "Textos de ajuda e documentação estão excessivamente densos para o público 60+."
                    ),
                    sugestao_correcao="Reescrever os textos com frases curtas (máximo 15 palavras) e vocabulário direto do dia a dia.",
                )
            )

        # 2. Jargões técnicos
        jargoes = doc_metrics.get("jargoes_detectados", [])
        if jargoes:
            lista_str = ", ".join(jargoes[:5])
            barreiras.append(
                BarreiraPreditiva(
                    tipo=self.tipo,
                    severidade=Severidade.ALTA,
                    arquivo=arquivo,
                    descricao=f"Presença de termos técnicos prejudiciais na interface/documentação: [{lista_str}].",
                    sugestao_correcao="Substituir termos como 'payload', 'backend', 'timeout' por palavras como 'dados', 'sistema' e 'tempo de espera'.",
                )
            )

        # 3. Mensagens de erro problemáticas do código
        erros_prob = struct_metrics.get("mensagens_erro_problematicas", [])
        if erros_prob:
            barreiras.append(
                BarreiraPreditiva(
                    tipo=self.tipo,
                    severidade=Severidade.ALTA,
                    arquivo=arquivo,
                    descricao=f"Foram detectadas {len(erros_prob)} mensagens de erro inadequadas (técnicas ou vagas).",
                    sugestao_correcao="Adotar o catálogo de erros simplificados do Agente 1, com título amigável e passos de solução.",
                )
            )

        return barreiras


class FluxoPredictor(BasePredictor):
    """
    Especialista em barreiras de Fluxo:
    - Ausência de breadcrumbs / trilha de etapas
    - Navegação profunda sem retorno simples
    - Inconsistência de layout e nomenclatura
    - Telas sobrecarregadas com excesso de passos
    """

    def __init__(self) -> None:
        super().__init__(TipoBarreira.FLUXO)

    def predict(
        self,
        doc_metrics: dict[str, Any],
        struct_metrics: dict[str, Any],
        regras: list[dict[str, Any]] | None = None,
    ) -> list[BarreiraPreditiva]:
        barreiras: list[BarreiraPreditiva] = []
        arquivo = struct_metrics.get("arquivo", "modulo.py")

        # 1. Ausência de indicador de fluxo ou trilha de migalhas (breadcrumbs)
        tags = [t.lower() for t in struct_metrics.get("tags_semanticas", [])]
        barreiras.append(
            BarreiraPreditiva(
                tipo=self.tipo,
                severidade=Severidade.MEDIA,
                arquivo=arquivo,
                descricao=(
                    "Fluxo de formulário/transação sem indicador visual de progresso (breadcrumbs ou etapas 1 de 3). "
                    "Usuários 60+ perdem o senso de orientação sem saber quanto falta para concluir."
                ),
                sugestao_correcao=(
                    "Adicionar barra de progresso simples com passos numerados e botão explícito 'Voltar para a etapa anterior'."
                ),
            )
        )

        consistencia = struct_metrics.get("consistencia_nomes", 1.0)
        if consistencia < 0.8:
            barreiras.append(
                BarreiraPreditiva(
                    tipo=self.tipo,
                    severidade=Severidade.MEDIA,
                    arquivo=arquivo,
                    descricao=f"Variação no padrão de nomenclatura ({consistencia * 100}%). Gera termos desiguais nas ações da tela.",
                    sugestao_correcao="Padronizar a taxonomia de ações ('Salvar', 'Voltar', 'Confirmar') em todo o fluxo da plataforma.",
                )
            )

        # 3. Alta densidade de código
        loc = struct_metrics.get("loc", 0)
        if loc > 300:
            barreiras.append(
                BarreiraPreditiva(
                    tipo=self.tipo,
                    severidade=Severidade.MEDIA,
                    arquivo=arquivo,
                    descricao=f"Arquivo de interface com alta densidade ({loc} linhas), sugerindo tela sobrecarregada.",
                    sugestao_correcao="Dividir o processo em um assistente passo a passo (wizard) com no máximo 3 campos por tela.",
                )
            )

        return barreiras


# ---------------------------------------------------------------------------
# Padrão Decorator (GoF) para adicionar regras customizadas dinamicamente
# ---------------------------------------------------------------------------

class RuleDecorator(BasePredictor):
    """
    Padrão Decorator (GoF).
    Decora um preditor existente para aplicar regras adicionais vindas de arquivos YAML
    sem alterar a implementação original.
    """

    def __init__(self, wrapped_predictor: BasePredictor, regras_extras: list[dict[str, Any]]) -> None:
        super().__init__(wrapped_predictor.tipo)
        self.wrapped = wrapped_predictor
        self.regras_extras = regras_extras

    def predict(
        self,
        doc_metrics: dict[str, Any],
        struct_metrics: dict[str, Any],
        regras: list[dict[str, Any]] | None = None,
    ) -> list[BarreiraPreditiva]:
        # Executa as predições da base
        barreiras = self.wrapped.predict(doc_metrics, struct_metrics, regras)

        arquivo = struct_metrics.get("arquivo", "app.py")
        # Aplica as regras extras decoradas
        for regra in self.regras_extras:
            regra_id = regra.get("id", "")
            descricao = regra.get("descricao", "")
            sugestao = regra.get("sugestao", "")
            sev_str = regra.get("severidade", "media").lower()
            severidade = Severidade.ALTA if sev_str == "alta" else (Severidade.BAIXA if sev_str == "baixa" else Severidade.MEDIA)

            # Avalia regra se houver flag no contexto
            if regra_id in struct_metrics.get("regras_violadas", []):
                barreiras.append(
                    BarreiraPreditiva(
                        tipo=self.tipo,
                        severidade=severidade,
                        arquivo=arquivo,
                        descricao=f"[{regra_id}] {descricao}",
                        sugestao_correcao=sugestao,
                    )
                )

        return barreiras


# ---------------------------------------------------------------------------
# Padrão Factory Method (GoF)
# ---------------------------------------------------------------------------

class PredictorFactory:
    """
    Padrão Factory Method (GoF).
    Instancia o preditor especialista adequado para a frente informada.
    """

    _REGISTRY: dict[TipoBarreira, type[BasePredictor]] = {
        TipoBarreira.PERCEPCAO: PercepcaoPredictor,
        TipoBarreira.OPERACAO: OperacaoPredictor,
        TipoBarreira.COMPREENSAO: CompreensaoPredictor,
        TipoBarreira.FLUXO: FluxoPredictor,
    }

    @classmethod
    def create(cls, tipo: TipoBarreira | str) -> BasePredictor:
        if isinstance(tipo, str):
            tipo = TipoBarreira(tipo.lower())
        predictor_cls = cls._REGISTRY.get(tipo)
        if not predictor_cls:
            raise ValueError(f"Tipo de barreira não suportado: {tipo}")
        return predictor_cls()

    @classmethod
    def create_all(cls) -> list[BasePredictor]:
        """Retorna instâncias para as quatro frentes."""
        return [
            PercepcaoPredictor(),
            OperacaoPredictor(),
            CompreensaoPredictor(),
            FluxoPredictor(),
        ]
