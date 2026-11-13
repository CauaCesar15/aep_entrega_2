"""
Módulo de Exemplo — Ergane Checkout e Faturamento MEI.

Este arquivo simula uma tela e rotina de processamento da plataforma Ergane,
voltada a pequenos empreendedores e testada sob a ótica da ODS 10 (Inclusão 60+).
"""

import sys


def emitir_recibo_rapido(cliente_nome, cpf_cnpj, valor_total):
    """
    Emite um recibo simplificado para o cliente do pequeno empreendedor MEI.
    Envia os dados via payload para a API de faturamento no backend.
    """
    if not cliente_nome or not cpf_cnpj:
        # Mensagem problemática para testar o Agente 2
        raise ValueError("Dados inválidos: campo obrigatório não preenchido")

    if valor_total <= 0:
        return "operation failed: valor não pode ser zero"

    taxa = calcular_imposto_simples(valor_total)
    return {"status": "ok", "recibo_id": 9921, "liquido": valor_total - taxa}


def calcular_imposto_simples(valor):
    """Calcula taxa estimada sobre o faturamento."""
    # Simulação de regra de negócio
    if valor > 5000:
        return valor * 0.05
    return 0.0


def verificar_conexao_gateway_pix():
    # Propositalmente sem docstring para testar métrica de cobertura de docstrings
    try:
        # Padrão de erro inesperado para testar detecção de erros problemáticos
        pass
    except Exception:
        return "Internal Server Error: falha no banco de dados"
    return "Conexão ativa"


def render_tela_recibo():
    """
    Renderiza o componente visual de recibo do Ergane.
    """
    html = """
    <div class="container">
      <header>
        <h1>Ergane — Emissão de Recibo MEI</h1>
      </header>
      <main>
        <section class="dados-cliente">
          <label>Nome do Cliente:</label>
          <input type="text" name="nome" placeholder="Ex: Maria Pereira" />
          <label>Documento (CPF ou CNPJ):</label>
          <input type="text" name="doc" placeholder="Apenas números" />
        </section>
        <section class="valores">
          <label>Valor do Serviço (R$):</label>
          <input type="text" name="valor" placeholder="0,00" />
          <button type="submit">Emitir e Imprimir Recibo</button>
        </section>
      </main>
      <footer>
        <p>Ergane Plataforma Acessível — Apoio ao Empreendedor Sênior</p>
      </footer>
    </div>
    """
    return html
