# UniCesumar - Universidade Cesumar
## Graduação em Engenharia de Software

### MODELO DE DOCUMENTO — ENTREGA 2
**Relatório Técnico de Implementação, Testes e Avaliação do Agente de Software**

---

| Campo | Especificação |
|---|---|
| **Título do Projeto / Ecossistema** | **Ergane** — Plataforma para Pequenos Empreendedores (CNPJ / MEI / ME / EPP) |
| **Curso / Disciplina / Turma** | Engenharia de Software — Arquitetura de Software · Gestão de Projetos · Tecnologias Emergentes |
| **Aluno / Integrante Responsável** | **Caua Cesar da Silva de Oliveira** — Acessibilidade e Documentação |
| **Equipe Integrada (Projeto Ergane)** | Luigi Biagio Antonioli (Coordenação e Arquitetura)<br>Francisco Guilherme Soares dos Santos (Qualidade e Testes)<br>Caua Cesar da Silva de Oliveira (Acessibilidade e Documentação) |
| **Agente Desenvolvido** | **Agente 3 — Agente de Acessibilidade Preditiva 60+ (Núcleo do Ergane)** |
| **ODS Escolhida** | **ODS 10 — Redução das Desigualdades** (Foco em Inclusão Digital da Economia Prateada 60+) |
| **Data da Entrega** | 13/11/2026 |

---

## 1. Contexto, Justificativa da ODS e Papel do Agente 3

### 1.1. Contexto da Plataforma Ergane
O **Ergane** é uma solução de software voltada a micro e pequenos empreendedores com CNPJ (MEI, ME e EPP). A plataforma busca desburocratizar e descomplicar rotinas essenciais como controle financeiro diário, emissão de recibos, geração e conferência de cobranças via PIX e organização de pedidos. 

### 1.2. Justificativa da ODS 10 (Redução das Desigualdades)
O pilar social do projeto é a **inclusão digital de empreendedores com mais de 60 anos (Economia Prateada)**. De acordo com dados do Sebrae e do IBGE, o Brasil possui mais de 4,5 milhões de empreendedores sêniores, muitos dos quais enfrentam barreiras severas ao utilizar sistemas informatizados convencionais devido a declínios visuais graduais (presbiopia, menor sensibilidade ao contraste), declínios motores (menor precisão no clique do mouse ou toque) e sobrecarga cognitiva (ansiedade diante de telas densas, jargões técnicos crípticos e fluxos não lineares).

A escolha da **ODS 10** materializa-se ao tratar a acessibilidade e a clareza de uso não como um adendo cosmético de fim de projeto, mas como **requisito de funcionamento prévio**: a interface é validada antes de chegar ao usuário final.

### 1.3. Papel do Agente 3 no Ecossistema
O **Agente 3 (Acessibilidade Preditiva)** é o núcleo do ecossistema Ergane. Sua premissa inovadora é atuar de forma **preventiva e preditiva**: em vez de esperar que a tela seja desenvolvida, renderizada e colocada em produção para então submetê-la a testes com usuários, o Agente 3 analisa o código-fonte, elementos estruturais de interface e a documentação técnica, cruzando essas informações com um catálogo de regras 60+ para **prever as barreiras de acessibilidade antes da tela ser renderizada**.

```
[Código / Telas do Ergane] ──▶ [Agente 3: Acessibilidade Preditiva] ──▶ [Relatório Preditivo 60+ com Recomendações]
                                            │
                                            ├── Frente 1: Percepção (Contraste, Fontes, Alvos)
                                            ├── Frente 2: Operação (Teclado, Skip links, Complexidade)
                                            ├── Frente 3: Compreensão (Flesch, Jargões, Mensagens de Erro)
                                            └── Frente 4: Fluxo (Breadcrumbs, Passos, Consistência)
```

---

## 2. Especificação do Agente: Regras, Formato e Arquitetura

### 2.1. Entradas, Saídas e Gatilho de Acionamento

| Elemento | Especificação Técnica |
|---|---|
| **Entradas** | **Modo Autônomo:** Arquivo de código Python, HTML ou tela do Ergane (`sample_ergane_module.py`).<br>**Modo Ecossistema:** JSON de métricas de documentação (Agente 1) + JSON de métricas estruturais de código (Agente 2). |
| **Saídas** | 1. Relatório executivo em Markdown (`output/relatorio_acessibilidade_*.md`).<br>2. Estrutura consolidada em JSON com severidades e planos de ação (`output/predicoes_acessibilidade_*.json`). |
| **Gatilho de Acionamento** | Evento de integração contínua (push/pull request no repositório) ou execução sob demanda via linha de comando (`agente3_cli.py`). |

### 2.2. Catálogo de Regras Formais de Acessibilidade 60+
O agente utiliza regras declarativas parametrizadas no arquivo `config/rules_60plus.yaml`, alinhadas às diretrizes internacionais da **WCAG 2.2** e à literatura de usabilidade para a terceira idade (Nielsen, 2002; W3C, 2021; Recchia, 2026), divididas em **4 frentes especializadas**:

1. **Frente de Percepção (Visual e Sensorial):**
   - `PERC-001`: Tamanho de fonte inferior a 16px (corpo) ou 18px (destaques). Severidade: Alta.
   - `PERC-002`: Contraste de cor texto/fundo inferior a 4.5:1 (WCAG AA). Severidade: Alta.
   - `PERC-003`: Alvos de clique/toque inferiores a 44x44px. Severidade: Alta.
   - `PERC-004`: Excesso de `divs` genéricas em detrimento de marcos semânticos (`<header>`, `<main>`, `<nav>`). Severidade: Média.

2. **Frente de Operação (Interação e Controle):**
   - `OPER-001`: Ausência de suporte à navegação completa por teclado (Tab, Enter, Esc). Severidade: Alta.
   - `OPER-002`: Ausência de link de salto (*skip link* — "Pular para o conteúdo principal"). Severidade: Média.
   - `OPER-003`: Lógica operacional de alta complexidade ciclomática (CC > 4.0) nos manipuladores de interface, impondo múltiplos passos rápidos ou timeouts que geram perda de sessão. Severidade: Alta.

3. **Frente de Compreensão (Linguagem e Cognição):**
   - `COMP-001`: Uso de jargões técnicos crípticos no vocabulário (`payload`, `backend`, `token`, `endpoint`, `null`). Severidade: Alta.
   - `COMP-002`: Índice de legibilidade Flesch-Kincaid abaixo de 50.0 (textos difíceis que demandam escolaridade superior para compreensão). Severidade: Alta.
   - `COMP-003`: Mensagens de erro sem orientação de correção (ex: *"Erro inesperado"*, *"Falha 500"*, *"Dados inválidos"*). Severidade: Alta.

4. **Frente de Fluxo (Orientação e Navegação):**
   - `FLUX-001`: Navegação profunda com mais de 3 níveis hierárquicos a partir da tela inicial. Severidade: Média.
   - `FLUX-002`: Ausência de indicadores visuais de progresso (*breadcrumbs* ou "Etapa 1 de 3"). Severidade: Média.
   - `FLUX-003`: Inconsistência na taxonomia e nomenclatura de botões e ações da interface. Severidade: Média.

### 2.3. Padrões de Projeto Aplicados (GoF e GRASP)

| Categoria | Padrão Adotado | Justificativa e Implementação no Agente 3 |
|---|---|---|
| **Criação (GoF)** | **Factory Method** | A classe `PredictorFactory` instancia dinamicamente o preditor especialista adequado (`PercepcaoPredictor`, `OperacaoPredictor`, `CompreensaoPredictor`, `FluxoPredictor`) sem acoplar o cliente às classes concretas. |
| **Estrutural (GoF)** | **Decorator** | A classe `RuleDecorator` decora qualquer preditor em tempo de execução, injetando regras dinâmicas vindas de arquivos YAML sem modificar o código-fonte das classes base. |
| **Comportamental (GoF)** | **Observer** | O agente integra-se ao `EventBus`, assinando notificações de novos códigos e publicando alertas automáticos caso identifique barreiras de severidade alta. |
| **Arquitetura** | **MVC Adaptado** | **Model:** Regras 60+ (`rules_60plus.yaml`) e dataclasses tipadas (`BarreiraPreditiva`).<br>**View:** Gerador de relatórios executivos em Markdown (`AccessibilityEngine.gerar_relatorio_markdown`).<br>**Controller:** `AccessibilityEngine`, coordenador do fluxo de predição. |
| **GRASP** | **Especialista na Informação + Controlador** | Cada frente preditiva é especialista nos seus próprios limiares de acessibilidade; o `AccessibilityEngine` atua como controlador central de consolidação. |

---

## 3. Metodologia de Teste e Cenários de Entrada

### 3.1. Como o Agente foi Testado (Metodologia)
A validação do Agente 3 foi conduzida por meio de uma abordagem dupla:
1. **Bateria de Testes Unitários Automatizados (`unittest`):** Implementada no arquivo `tests/test_agente3_standalone.py`, validando o isolamento de cada preditor, a instanciação via Factory, a decoração dinâmica via Decorator e o cumprimento de 100% dos critérios de aceitação.
2. **Execução no Test Harness Formal:** Executado via `python3 agente3_cli.py test`, submetendo o agente a cenários estressantes de código e aferindo a taxa de conformidade e tempos de resposta com precisão de milissegundos.

### 3.2. Cenários e Entradas Utilizadas nos Testes
Foram formulados dois conjuntos de dados de entrada:

- **Entrada 1 — Código Real da Plataforma Ergane (`sample_ergane_module.py`):**
  Representa uma tela típica de checkout para MEI, contendo formulário de cobrança PIX, campos de entrada (`<input>`), botões (`<button>`), divs aninhadas, mensagens de tratamento de erro e docstrings técnicas.
- **Entrada 2 — Contexto Sintético com Violações Severas (Caso de Estresse):**
  - Legibilidade Flesch forçada para **30.0** (linguagem excessivamente densa e técnica).
  - Presença explícita de jargões técnicos: `["payload", "backend", "token"]`.
  - Complexidade ciclomática elevada em **5.5** (fluxo confuso com múltiplos desvios condicionais).
  - Mensagens de erro vagas: `["Erro inesperado", "Internal server error"]`.
  - Ausência de tags de orientação (`<nav>`, links de salto e indicadores de progresso).

---

## 4. Resultados e Análise de Desempenho

### 4.1. Scorecard dos Critérios de Aceitação (Entrega 2)
A tabela a seguir consolida os resultados da verificação formal dos critérios de aceitação estipulados para a Entrega 2:

| # | Critério de Aceitação | Meta Estipulada | Resultado Obtido | Status |
|---|---|---|---|:---:|
| **3.1** | Cruzar métricas de documentação e estruturais com regras 60+ | Pelo menos 1 barreira prevista | **10 barreiras identificadas** | ✅ **APROVADO** |
| **3.2** | Prever pelo menos 4 categorias/tipos de barreira | Abranger as 4 frentes | **4/4 frentes cobertas** (Percepção, Operação, Compreensão, Fluxo) | ✅ **APROVADO** |
| **3.3** | Gerar relatório por arquivo e por tela | Markdown e JSON estruturados | **Relatório Markdown (4.058 caracteres) + JSON gerados** | ✅ **APROVADO** |
| **3.4** | Emitir sugestão de correção para cada barreira | 100% com sugestão | **100% das barreiras possuem plano de correção acionável** | ✅ **APROVADO** |
| **3.5** | Tempo de análise por arquivo | ≤ 30,0 segundos | **0,0001s nos testes / 0,0029s no módulo completo** | ✅ **APROVADO** |

> **Resultado Geral do Test Harness:** **5/5 critérios aprovados (100% de conformidade).**

### 4.2. Barreiras Identificadas no Módulo de Exemplo (`sample_ergane_module.py`)
Ao executar o comando `python3 agente3_cli.py analyze sample_ergane_module.py`, o agente identificou **7 barreiras preventivas**, distribuídas conforme a tabela abaixo:

| # | Frente | Severidade | Barreira Identificada | Sugestão de Correção Emitida pelo Agente |
|---|---|:---:|---|---|
| **1** | Percepção | 🔴 Alta | Botões e campos sem especificação explícita de tamanho mínimo de alvo (44x44px) ou contraste de cores (4.5:1). | Definir padding amplo para garantir alvos ≥ 44x44px e aplicar contraste mínimo de 4.5:1 no texto contra o fundo (WCAG 2.2 AA). |
| **2** | Percepção | 🟡 Média | Estrutura com excesso de `divs` genéricas em relação a blocos semânticos. | Adotar `<header>`, `<main>`, `<section>` e `<footer>` para orientar visualmente o idoso. |
| **3** | Operação | 🟡 Média | Ausência de link de salto (*skip link*) e de tag `<nav>`. Usuários de teclado pressionam Tab repetidamente. | Adicionar link de salto no início da tela e estruturar menus dentro da tag `<nav>`. |
| **4** | Compreensão | 🔴 Alta | Índice de legibilidade Flesch (42.0) abaixo do limite seguro (50.0). | Reescrever textos com frases curtas (máximo 15 palavras) e vocabulário do dia a dia. |
| **5** | Compreensão | 🔴 Alta | Presença de jargões técnicos na interface/documentação: `payload`, `backend`. | Substituir termos por palavras amigáveis: *"dados"*, *"sistema"* e *"tempo de espera"*. |
| **6** | Compreensão | 🔴 Alta | Presença de mensagens de erro inadequadas e vagas. | Adotar catálogo de erros simplificados, com título amigável e passos claros de solução. |
| **7** | Fluxo | 🟡 Média | Fluxo de checkout sem indicador de etapas (*breadcrumbs* ou progresso "1 de 3"). | Adicionar barra de progresso simples com passos numerados e botão explícito "Voltar". |

### 4.3. Desempenho e Performance
A métrica de tempo exigida pela disciplina era de **≤ 30 segundos por arquivo de até 500 linhas**.
O tempo medido de processamento do Agente 3 foi de **0,0029 segundos** para o arquivo completo de checkout (e 0,0001 segundos no teste sintético). O agente operou mais de **10.000 vezes mais rápido que o teto regulamentar**, demonstrando que a arquitetura híbrida com parsing estático determinístico não adiciona *overhead* aos pipelines de integração contínua (CI/CD).

---

## 5. Crítica Reflexiva sobre os Resultados ("O Agente Não É Perfeito")

A maturidade de um projeto de Engenharia de Software fundamenta-se no reconhecimento transparente dos limites e pontos cegos da ferramenta desenvolvida. O Agente 3 atende rigorosamente a todos os critérios de aceitação da Entrega 2, porém possui limitações inerentes à sua abordagem arquitetural:

### 5.1. Limitações da Análise Estática vs. Renderização Dinâmica
O Agente 3 analisa o código-fonte estático e a estrutura da árvore sintética (AST/HTML). No entanto, o agente **não executa uma renderização gráfica completa (Headless Browser / DOM computado)**. Isso gera duas limitações práticas:
- Se uma folha de estilos CSS externa ou uma biblioteca de componentes (como Tailwind CSS ou Bootstrap) aplicar estilos dinâmicos de cor e espaçamento em tempo de execução, o agente pode emitir um aviso de "tamanho de botão não identificado", caracterizando um falso positivo de percepção.
- O agente não consegue validar contrastes que dependem de imagens de fundo dinâmicas ou gradientes renderizados no cliente.

### 5.2. Risco de Falsos Positivos Semânticos em Jargões
O detector de jargões varre símbolos e docstrings procurando termos como `payload` ou `backend`. Embora isso seja benéfico para manter a documentação simples, pode ocorrer de um desenvolvedor utilizar a palavra `payload` apenas no nome de uma variável interna de backend sem que esse termo jamais seja exposto ao usuário idoso na tela. O agente trata preventivamente a ocorrência como barreira, demandando refinamento futuro para distinguir contexto interno de strings de interface gráfica.

### 5.3. A Predição Não Substitui o Teste Empírico Humano
A inferência preditiva é uma ferramenta de aceleração para a equipe de desenvolvimento, mas **não substitui a validação humana com usuários 60+ reais**. Variáveis subjetivas como o nível de ansiedade digital do empreendedor sênior, a fadiga ocular acumulada ao longo do dia de trabalho e a hesitação diante de interfaces financeiras só podem ser plenamente medidas através de testes com usuários reais ou simulações comportamentais mais profundas (como as propostas pelo Agente 4 do ecossistema).

### 5.4. Dependência do Modelo LLM Local
A arquitetura híbrida do agente foi concebida com *fallback* gracioso determinístico: caso o servidor local Ollama (Llama 3.2 3B) não esteja ativo, o agente utiliza geradores determinísticos baseados em regras e templates. Se por um lado isso assegura robustez e taxa de falha zero, por outro reduz a flexibilidade criativa das sugestões de correção, que passam a ser padronizadas em vez de contextualizadas em linguagem natural empática.

---

## 6. Considerações Finais

O desenvolvimento do **Agente 3 (Acessibilidade Preditiva 60+)** comprova a viabilidade técnica de utilizar padrões de projeto clássicos (**Factory Method**, **Decorator**, **Observer** e **MVC**) para resolver um problema social concreto: a **inclusão digital de pequenos empreendedores da Economia Prateada (ODS 10)**.

O agente conseguiu prever com precisão barreiras reais no código do checkout Ergane antes que qualquer tela chegasse ao usuário final, cumprindo 100% dos critérios de aceitação e operando com alta velocidade (0,0029s). As limitações identificadas apontam um caminho claro de evolução para as próximas etapas: integração com renderizadores de DOM dinâmico e refinamento de contexto de UI.

---

## 7. Referências Utilizadas (Normas ABNT)

- **AGÊNCIA BRASIL.** *Brasil já tem 4,5 milhões de empreendedores da Economia Prateada.* Brasília, DF, 2026.
- **BASS, L.; CLEMENTS, P.; KAZMAN, R.** *Software Architecture in Practice.* 4. ed. Boston: Addison-Wesley, 2021.
- **BRASIL.** *Lei Complementar nº 123, de 14 de dezembro de 2006.* Estatuto Nacional da Microempresa e da Empresa de Pequeno Porte.
- **BRASIL.** *Lei nº 10.741, de 1º de outubro de 2003.* Estatuto da Pessoa Idosa.
- **BRASIL.** *Lei nº 13.146, de 6 de julho de 2015.* Lei Brasileira de Inclusão da Pessoa com Deficiência.
- **GAMMA, E.; HELM, R.; JOHNSON, R.; VLISSIDES, J.** *Design Patterns: Elements of Reusable Object-Oriented Software.* Boston: Addison-Wesley, 1994.
- **LARMAN, C.** *Utilizando UML e Padrões: uma introdução à análise e ao projeto orientados a objetos e ao desenvolvimento iterativo.* 3. ed. Porto Alegre: Bookman, 2007.
- **NIELSEN, J.** *Usability for Senior Citizens: design guidelines based on usability studies with people age 65 and older.* Nielsen Norman Group, 2002.
- **RECCHIA, R. M.** *Guia Visual WCAG 2.2: apoio ao desenvolvimento de aplicativos acessíveis para pessoas com baixa visão.* 2026. Dissertação — Escola Paulista de Medicina, Universidade Federal de São Paulo.
- **W3C.** *Making Content Usable for People with Cognitive and Learning Disabilities.* W3C Working Group Note, 2021.
- **W3C.** *Web Content Accessibility Guidelines (WCAG) 2.2.* W3C Recommendation, 2023.
