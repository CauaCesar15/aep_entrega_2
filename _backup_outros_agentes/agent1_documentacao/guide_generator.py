"""
Gerador do Guia de Erros em Linguagem Simples para Idosos (60+).

Padrões aplicados:
- Template Method (GoF): BaseGuideGenerator define o esqueleto do algoritmo de geração.
- Especialista (GRASP): GuiaErrosIdoso especializa a tradução de jargões para linguagem clara.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseGuideGenerator(ABC):
    """
    Padrão Template Method (GoF).
    Define o esqueleto do processo de geração do guia de suporte.
    """

    def gerar_guia(self, contexto: dict[str, Any] | None = None) -> str:
        """
        Método gabarito (Template Method).
        Executa os passos na ordem definida:
        1. coletar_erros
        2. formatar_erros
        3. simplificar_linguagem
        4. montar_documento
        """
        erros_brutos = self.coletar_erros(contexto or {})
        erros_formatados = self.formatar_erros(erros_brutos)
        erros_simplificados = self.simplificar_linguagem(erros_formatados)
        return self.montar_documento(erros_simplificados)

    @abstractmethod
    def coletar_erros(self, contexto: dict[str, Any]) -> list[dict[str, Any]]:
        """Passo 1: Coleta os erros catalogados."""
        ...

    @abstractmethod
    def formatar_erros(self, erros: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Passo 2: Formata os dados de erro."""
        ...

    @abstractmethod
    def simplificar_linguagem(self, erros: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Passo 3: Aplica simplificação de linguagem para o público-alvo."""
        ...

    @abstractmethod
    def montar_documento(self, erros: list[dict[str, Any]]) -> str:
        """Passo 4: Monta o documento final em Markdown/texto."""
        ...


class GuiaErrosIdoso(BaseGuideGenerator):
    """
    Gera o Guia de Resolução de Erros do Ergane voltado para empreendedores 60+.
    Atende ao critério de pelo menos 8 tipos de erros com passos claros e ilustrados.
    """

    CATALOGO_ERROS_60PLUS: list[dict[str, Any]] = [
        {
            "id": "ERR_01_LOGIN",
            "categoria": "Autenticação",
            "codigo_tecnico": "AUTH_FAILED_401",
            "titulo_original": "Falha na Autenticação de Usuário",
            "titulo_simples": "Não conseguimos entrar na sua conta",
            "icone": "🔑",
            "o_que_aconteceu": "O e-mail ou a senha digitados podem ter alguma letra ou número fora do lugar.",
            "passos_solucao": [
                "Verifique se a tecla de letras maiúsculas (Caps Lock) está ligada no seu teclado.",
                "Apague o que escreveu e digite novamente com calma.",
                "Se esqueceu a senha, clique no botão azul 'Esqueci minha senha' para receber um código no seu celular.",
            ],
            "dica_tranquilidade": "Fique tranquilo: seu dinheiro e suas informações continuam 100% seguros.",
        },
        {
            "id": "ERR_02_SENHA_EXPIRADA",
            "categoria": "Autenticação",
            "codigo_tecnico": "PASSWORD_EXPIRED",
            "titulo_original": "Credencial Expirada por Política de Segurança",
            "titulo_simples": "Chegou a hora de criar uma nova senha",
            "icone": "🛡️",
            "o_que_aconteceu": "Por segurança do seu CNPJ, o sistema pede para renovar a senha de tempos em tempos.",
            "passos_solucao": [
                "Digite sua senha antiga no primeiro campo.",
                "Crie uma nova senha de fácil lembrança para você (com pelo menos 8 números ou letras).",
                "Anote a nova senha em um caderninho seguro em sua casa ou escritório.",
                "Clique em 'Salvar nova senha'.",
            ],
            "dica_tranquilidade": "Essa troca protege suas emissões de notas fiscais contra fraudes.",
        },
        {
            "id": "ERR_03_SESSAO_EXPIRADA",
            "categoria": "Sessão",
            "codigo_tecnico": "SESSION_TIMEOUT_440",
            "titulo_original": "Tempo Limite de Sessão Excedido",
            "titulo_simples": "Sua tela pausou por segurança após algum tempo sem uso",
            "icone": "⏳",
            "o_que_aconteceu": "Você ficou alguns minutos sem mexer no sistema e a tela foi bloqueada para que ninguém mexa nos seus dados.",
            "passos_solucao": [
                "Clique no botão 'Entrar novamente'.",
                "Digite seu e-mail e senha de acesso.",
                "O sistema voltará exatamente na tela onde você estava.",
            ],
            "dica_tranquilidade": "Nenhum dado cadastrado foi perdido.",
        },
        {
            "id": "ERR_04_CAMPO_OBRIGATORIO",
            "categoria": "Formulário",
            "codigo_tecnico": "MISSING_REQUIRED_FIELD",
            "titulo_original": "Campos Mandatórios Não Fornecidos",
            "titulo_simples": "Faltou preencher uma informação importante",
            "icone": "📝",
            "o_que_aconteceu": "Para emitir seu recibo ou cadastrar seu cliente, um dado essencial ficou em branco.",
            "passos_solucao": [
                "Olhe para a tela e procure o campo destacado com a cor amarela ou vermelha.",
                "Preencha o campo que está pedindo a informação (como Nome do Cliente ou Valor).",
                "Clique novamente no botão 'Salvar'.",
            ],
            "dica_tranquilidade": "O sistema só avança quando tudo estiver certinho para você não ter problemas com a Receita.",
        },
        {
            "id": "ERR_05_FORMATO_INVALIDO",
            "categoria": "Validação",
            "codigo_tecnico": "INVALID_FORMAT_REGEX",
            "titulo_original": "Falha de Máscara de Formato de Entrada",
            "titulo_simples": "Número de CPF ou CNPJ com quantidade errada de dígitos",
            "icone": "🔢",
            "o_que_aconteceu": "Faltou ou sobrou algum número no documento digitado.",
            "passos_solucao": [
                "Lembre-se: CPF possui 11 números e CNPJ possui 14 números.",
                "Não precisa digitar pontos ou barras; o sistema coloca automaticamente.",
                "Confira os números no cartão do cliente e digite de novo.",
            ],
            "dica_tranquilidade": "Se tiver dúvidas, você pode consultar o cartão de CNPJ do cliente antes de confirmar.",
        },
        {
            "id": "ERR_06_CONEXAO_PERDIDA",
            "categoria": "Rede",
            "codigo_tecnico": "NETWORK_DISCONNECTED_ERR",
            "titulo_original": "Queda no Soquete TCP / Sem Resposta HTTP",
            "titulo_simples": "Sua internet oscilou ou caiu por um instante",
            "icone": "📡",
            "o_que_aconteceu": "O computador ou celular perdeu contato com a internet enquanto enviava sua solicitação.",
            "passos_solucao": [
                "Dê uma olhadinha no modem ou no ícone do Wi-Fi no canto da tela.",
                "Aguarde cerca de 20 a 30 segundos para o sinal voltar.",
                "Clique no botão verde 'Tentar novamente' na tela.",
            ],
            "dica_tranquilidade": "O Ergane guarda o que você digitou para não ter que recomeçar do zero.",
        },
        {
            "id": "ERR_07_PAGAMENTO_RECUSADO",
            "categoria": "Financeiro",
            "codigo_tecnico": "PAYMENT_GATEWAY_REJECTED",
            "titulo_original": "Recusa na Liquidação de Transação no Gateway",
            "titulo_simples": "O recebimento do PIX ou Cartão não foi concluído",
            "icone": "💳",
            "o_que_aconteceu": "O banco do cliente ou a maquininha não autorizou este valor neste momento.",
            "passos_solucao": [
                "Pergunte ao cliente se o aplicativo do banco dele exibiu algum aviso de limite ou horário.",
                "Se for PIX, gere um novo QR Code clicando em 'Gerar novo código PIX'.",
                "Se for cartão, tente inserir ou aproximar novamente após 1 minuto.",
            ],
            "dica_tranquilidade": "Nenhum valor foi debitado indevidamente do seu cliente.",
        },
        {
            "id": "ERR_08_LIMITE_MEI",
            "categoria": "Fiscal / MEI",
            "codigo_tecnico": "MEI_REVENUE_THRESHOLD_ALERT",
            "titulo_original": "Alerta de Limite Operacional Anual MEI",
            "titulo_simples": "Atenção ao faturamento total do seu MEI este ano",
            "icone": "📊",
            "o_que_aconteceu": "Parabéns pelas vendas! O total acumulado está se aproximando do teto permitido para MEI.",
            "passos_solucao": [
                "Acesse a aba 'Meu Negócio' para ver o gráfico simples de faturamento anual.",
                "Se as vendas continuarem crescendo, procure seu contador ou o SEBRAE para fazer a transição para Microempresa (ME).",
                "Você pode continuar emitindo seus recibos normalmente este mês.",
            ],
            "dica_tranquilidade": "Crescer é uma excelente notícia! O Ergane avisa com antecedência para evitar multas.",
        },
    ]

    def coletar_erros(self, contexto: dict[str, Any]) -> list[dict[str, Any]]:
        """Retorna o catálogo de erros 60+, permitindo adições contextuais."""
        erros_extras = contexto.get("erros_adicionais", [])
        return list(self.CATALOGO_ERROS_60PLUS) + list(erros_extras)

    def formatar_erros(self, erros: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Garante que todos os campos obrigatórios estejam preenchidos."""
        formatados = []
        for e in erros:
            formatados.append({
                "id": e.get("id", "ERR_GENERIC"),
                "categoria": e.get("categoria", "Geral"),
                "titulo_simples": e.get("titulo_simples", "Aconteceu um pequeno imprevisto"),
                "icone": e.get("icone", "ℹ️"),
                "o_que_aconteceu": e.get("o_que_aconteceu", "O sistema precisa de sua confirmação."),
                "passos_solucao": e.get("passos_solucao", ["Tente novamente em instantes."]),
                "dica_tranquilidade": e.get("dica_tranquilidade", "Suas informações estão seguras."),
            })
        return formatados

    def simplificar_linguagem(self, erros: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Reforça que a linguagem esteja acessível (elimina jargões remanescentes)."""
        # Garante substituições comuns
        substituicoes = {
            "timeout": "tempo esgotado",
            "bug": "pequeno erro",
            "login": "entrada na conta",
            "link": "botão ou endereço",
            "download": "baixar arquivo",
            "upload": "enviar arquivo",
        }
        for item in erros:
            for eng, pt in substituicoes.items():
                item["o_que_aconteceu"] = item["o_que_aconteceu"].replace(eng, pt)
        return erros

    def montar_documento(self, erros: list[dict[str, Any]]) -> str:
        """Monta o Guia em formato Markdown com alta legibilidade."""
        linhas = [
            "# Guia de Resolução Fácil — Ergane 60+",
            "## Como resolver os avisos e imprevistos mais comuns no seu dia a dia",
            "",
            "> **Prezado(a) Empreendedor(a):** Este guia foi feito especialmente com letras claras e ",
            "> explicações passo a passo para que você resolva qualquer aviso do sistema com segurança e autonomia.",
            "",
            "---",
            "",
        ]

        for i, erro in enumerate(erros, 1):
            linhas.append(f"### {erro['icone']} {i}. {erro['titulo_simples']}")
            linhas.append(f"**Categoria:** {erro['categoria']}")
            linhas.append("")
            linhas.append(f"**O que aconteceu:** {erro['o_que_aconteceu']}")
            linhas.append("")
            linhas.append("**O que você deve fazer (Passo a passo):**")
            for step_idx, passo in enumerate(erro["passos_solucao"], 1):
                linhas.append(f"{step_idx}. {passo}")
            linhas.append("")
            linhas.append(f"💡 *Dica de Segurança:* {erro['dica_tranquilidade']}")
            linhas.append("")
            linhas.append("---")
            linhas.append("")

        linhas.append("### Precisa de mais ajuda?")
        linhas.append("Se o aviso continuar, ligue ou mande mensagem para o nosso suporte acolhedor pelo telefone / WhatsApp indicado na tela inicial.")
        return "\n".join(linhas)
