"""
Construção e catálogo de cenários de teste simulados para o Agente 4.

Padrões aplicados:
- Builder (GoF): ScenarioBuilder permite construir cenários passo a passo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScenarioStep:
    """Passo individual de um cenário de teste."""

    acao: str
    alvo: str
    espera_segundos: float
    sucesso_esperado: bool = True


@dataclass
class TestScenario:
    """Cenário de teste completo simulando recuperação de erro."""

    id: str
    nome: str
    tipo: str  # "tecnico" ou "financeiro"
    descricao: str
    barreira_relacionada: str
    passos: list[ScenarioStep] = field(default_factory=list)
    tempo_base_s: float = 10.0


class ScenarioBuilder:
    """
    Padrão Builder (GoF).
    Constrói incrementalmente cenários de teste com múltiplos passos.
    """

    def __init__(self, id_cenario: str, tipo: str) -> None:
        self._scenario = TestScenario(
            id=id_cenario,
            nome="",
            tipo=tipo,
            descricao="",
            barreira_relacionada="",
            passos=[],
            tempo_base_s=10.0,
        )

    def set_nome(self, nome: str) -> ScenarioBuilder:
        self._scenario.nome = nome
        return self

    def set_descricao(self, descricao: str) -> ScenarioBuilder:
        self._scenario.descricao = descricao
        return self

    def set_barreira(self, barreira: str) -> ScenarioBuilder:
        self._scenario.barreira_relacionada = barreira
        return self

    def set_tempo_base(self, segundos: float) -> ScenarioBuilder:
        self._scenario.tempo_base_s = segundos
        return self

    def add_passo(self, acao: str, alvo: str, espera: float = 2.0) -> ScenarioBuilder:
        self._scenario.passos.append(ScenarioStep(acao=acao, alvo=alvo, espera_segundos=espera))
        return self

    def build(self) -> TestScenario:
        return self._scenario


# ---------------------------------------------------------------------------
# Catálogo Canônico: 5 Casos Técnicos e 5 Casos Financeiros
# ---------------------------------------------------------------------------

def criar_cenarios_padrao() -> list[TestScenario]:
    """
    Cria a suíte oficial de cenários atendendo aos critérios da Entrega 2:
    - 5 casos de erro técnico
    - 5 casos de erro financeiro
    """
    cenarios: list[TestScenario] = []

    # --- 5 Casos Técnicos ---
    cenarios.append(
        ScenarioBuilder("TEC-01", "tecnico")
        .set_nome("Falha de Conexão na Emissão de Recibo")
        .set_descricao("Queda temporária de Wi-Fi no momento em que o Sr. José clica para gerar o recibo.")
        .set_barreira("Queda no Soquete TCP / Sem Resposta HTTP")
        .set_tempo_base(18.0)
        .add_passo("Observar tela de aviso", "Modal de alerta amigável", 5.0)
        .add_passo("Ler instrução de reconexão", "Guia 60+", 8.0)
        .add_passo("Clicar no botão verde", "Botão 'Tentar novamente'", 5.0)
        .build()
    )

    cenarios.append(
        ScenarioBuilder("TEC-02", "tecnico")
        .set_nome("Erro de Senha Incorreta / Caps Lock")
        .set_descricao("Tentativa de login com letras maiúsculas acidentais ativadas.")
        .set_barreira("AUTH_FAILED_401")
        .set_tempo_base(22.0)
        .add_passo("Perceber mensagem de erro", "Texto abaixo do campo senha", 6.0)
        .add_passo("Desligar Caps Lock no teclado", "Teclado físico", 7.0)
        .add_passo("Digitar senha novamente e confirmar", "Campo de senha", 9.0)
        .build()
    )

    cenarios.append(
        ScenarioBuilder("TEC-03", "tecnico")
        .set_nome("Sessão Expirada por Inatividade")
        .set_descricao("Sr. José atendeu um cliente na oficina e ao voltar a tela estava bloqueada.")
        .set_barreira("SESSION_TIMEOUT_440")
        .set_tempo_base(25.0)
        .add_passo("Ler aviso de segurança da sessão", "Aviso em tela cheia", 10.0)
        .add_passo("Clicar em 'Entrar novamente'", "Botão azul destacado", 5.0)
        .add_passo("Reconfirmar senha de acesso", "Formulário rápido", 10.0)
        .build()
    )

    cenarios.append(
        ScenarioBuilder("TEC-04", "tecnico")
        .set_nome("Campo Obrigatório Não Preenchido")
        .set_descricao("Tentativa de salvar cliente sem colocar o telefone de contato.")
        .set_barreira("MISSING_REQUIRED_FIELD")
        .set_tempo_base(15.0)
        .add_passo("Localizar campo destacado em amarelo", "Campo Telefone", 5.0)
        .add_passo("Digitar o DDD e número", "Input com máscara", 6.0)
        .add_passo("Salvar novamente", "Botão Salvar", 4.0)
        .build()
    )

    cenarios.append(
        ScenarioBuilder("TEC-05", "tecnico")
        .set_nome("Timeout de Resposta do Servidor")
        .set_descricao("Demora excessiva na resposta da API de consulta de CEP.")
        .set_barreira("timeout")
        .set_tempo_base(28.0)
        .add_passo("Aguardar mensagem de tempo esgotado", "Alerta na tela", 10.0)
        .add_passo("Optar por digitar o endereço manualmente", "Link 'Preencher à mão'", 10.0)
        .add_passo("Completar nome da rua e bairro", "Campos de endereço", 8.0)
        .build()
    )

    # --- 5 Casos Financeiros ---
    cenarios.append(
        ScenarioBuilder("FIN-01", "financeiro")
        .set_nome("Recusa de Transação PIX no Gateway")
        .set_descricao("Cliente escaneou o QR Code PIX mas a transação falhou no banco.")
        .set_barreira("PAYMENT_GATEWAY_REJECTED")
        .set_tempo_base(35.0)
        .add_passo("Identificar aviso sonoro e visual de não recebido", "Alerta na tela", 8.0)
        .add_passo("Ler orientação para gerar novo QR Code", "Instrução clara", 12.0)
        .add_passo("Gerar novo código e mostrar ao cliente", "Botão Novo PIX", 15.0)
        .build()
    )

    cenarios.append(
        ScenarioBuilder("FIN-02", "financeiro")
        .set_nome("CNPJ do Tomador Inválido na NF-e")
        .set_descricao("Tentativa de emissão de recibo com 13 dígitos em vez de 14 no CNPJ.")
        .set_barreira("INVALID_FORMAT_REGEX")
        .set_tempo_base(30.0)
        .add_passo("Ler mensagem indicando que faltou 1 dígito", "Mensagem amigável", 10.0)
        .add_passo("Conferir documento impresso do cliente", "Cartão CNPJ", 12.0)
        .add_passo("Corrigir o número e emitir", "Botão Emitir", 8.0)
        .build()
    )

    cenarios.append(
        ScenarioBuilder("FIN-03", "financeiro")
        .set_nome("Aviso de Proximidade do Teto MEI")
        .set_descricao("Sr. José ultrapassou 80% do faturamento anual permitido para MEI.")
        .set_barreira("MEI_REVENUE_THRESHOLD_ALERT")
        .set_tempo_base(40.0)
        .add_passo("Ler explicação preventiva sem pânico", "Banner informativo", 15.0)
        .add_passo("Acessar resumo de faturamento anual", "Aba Meu Negócio", 15.0)
        .add_passo("Clicar no link de orientação do SEBRAE", "Botão de apoio", 10.0)
        .build()
    )

    cenarios.append(
        ScenarioBuilder("FIN-04", "financeiro")
        .set_nome("Valor com Formatação de Moeda Incorreta")
        .set_descricao("Inserção de ponto em vez de vírgula no valor do serviço (ex: R$ 150.00).")
        .set_barreira("INVALID_FORMAT_REGEX")
        .set_tempo_base(20.0)
        .add_passo("Ver máscara automática ajustando o valor", "Campo Valor", 6.0)
        .add_passo("Confirmar se o valor exibido em reais está correto", "Leitura de confirmação", 8.0)
        .add_passo("Avançar para geração do recibo", "Botão Confirmar", 6.0)
        .build()
    )

    cenarios.append(
        ScenarioBuilder("FIN-05", "financeiro")
        .set_nome("Estorno de Pagamento Duplicado")
        .set_descricao("Cliente passou o cartão duas vezes por engano e solicita cancelamento.")
        .set_barreira("Lógica operacional complexa")
        .set_tempo_base(45.0)
        .add_passo("Acessar aba 'Últimos Recebimentos'", "Menu Financeiro", 12.0)
        .add_passo("Localizar transação repetida com horário idêntico", "Lista de cartões", 15.0)
        .add_passo("Clicar em 'Pedir estorno' com confirmação em 1 clique", "Botão Estornar", 18.0)
        .build()
    )

    return cenarios
