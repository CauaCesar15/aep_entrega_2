# Agente 3 — Agente de Acessibilidade Preditiva 60+ (Núcleo Ergane)

> **Projeto:** Plataforma Ergane para Pequenos Empreendedores (CNPJ / MEI / ME / EPP)  
> **ODS 10:** Redução das Desigualdades (Foco em Inclusão Digital da Economia Prateada 60+)  
> **Curso:** Graduação em Engenharia de Software — UniCesumar  
> **Disciplina:** Arquitetura de Software · Gestão de Projetos · Tecnologias Emergentes  
> **Entrega 2 — Agente Individual:** Caua Cesar da Silva de Oliveira  
> **Papel:** Acessibilidade e Documentação  

---

## 1. Visão Geral e Propósito (ODS 10)

O **Agente 3** é o núcleo do ecossistema Ergane. Sua função é **prever preventivamente barreiras de acessibilidade front-end para empreendedores idosos (60+)** antes mesmo da tela chegar ao usuário final ou ser renderizada no navegador.

Ele analisa o código-fonte, elementos de interface e documentação, cruzando essas informações com um catálogo formal de regras de usabilidade sênior (baseadas na **WCAG 2.2** e na **Economia Prateada**) divididas em 4 frentes:
1. 👁️ **Percepção:** Contraste mínimo 4.5:1, fontes ≥ 16px/18px, alvos de toque ≥ 44x44px e blocos semânticos.
2. ⌨️ **Operação:** Navegação completa por teclado, links de salto (*skip links*) e fluxo operacional simplificado.
3. 🧠 **Compreensão:** Legibilidade Flesch, erradicação de jargões técnicos (`payload`, `backend`, `token`) e mensagens de erro acolhedoras com instrução de solução.
4. 🧭 **Fluxo:** Indicadores visuais de progresso (*breadcrumbs*), etapas curtas (máximo 3 campos/tela) e consistência de nomenclatura.

---

## 2. Padrões de Projeto Aplicados (GoF & GRASP)

| Categoria | Padrão Adotado | Aplicação no Agente 3 |
|---|---|---|
| **Criação (GoF)** | **Factory Method** | `PredictorFactory` instancia dinamicamente os preditores especialistas (`PercepcaoPredictor`, `OperacaoPredictor`, `CompreensaoPredictor`, `FluxoPredictor`). |
| **Estrutural (GoF)** | **Decorator** | `RuleDecorator` decora qualquer preditor em tempo de execução, injetando regras WCAG 60+ do arquivo YAML sem alterar a classe base. |
| **Comportamental (GoF)**| **Observer** | O Agente assina eventos no `EventBus` e notifica listeners quando barreiras críticas (severidade alta) são identificadas. |
| **Arquitetura (MVC)** | **MVC Adaptado** | **Model:** Regras 60+ e dataclasses (`BarreiraPreditiva`).<br>**View:** Gerador de relatórios executivos em Markdown (`AccessibilityEngine.gerar_relatorio_markdown`).<br>**Controller:** `AccessibilityEngine`, que coordena o fluxo entre dados e visualização. |
| **GRASP** | **Especialista + Controlador** | Cada frente é uma classe especialista autônoma; o `AccessibilityEngine` atua como controlador de consolidação. |

---

## 3. Conformidade com os Critérios de Aceitação (Entrega 2)

Todos os 5 critérios formais de aceitação estabelecidos no documento acadêmico estão 100% implementados e testados:

| Critério | Descrição | Status | Como é Validado |
|---|---|---|---|
| **3.1** | Cruzar métricas de documentação e estruturais com regras 60+ | ✅ **Aprovado** | Cruza automaticamente métricas com `config/rules_60plus.yaml`. |
| **3.2** | Prever pelo menos 4 categorias/tipos de barreira | ✅ **Aprovado** | Cobre integralmente: *Percepção*, *Operação*, *Compreensão* e *Fluxo*. |
| **3.3** | Gerar relatório por arquivo e por tela | ✅ **Aprovado** | Gera relatórios em `.md` (Markdown legível) e `.json` estruturado. |
| **3.4** | Emitir sugestão de correção para cada barreira | ✅ **Aprovado** | 100% das barreiras contêm plano de ação corretiva acionável. |
| **3.5** | Tempo de análise ≤ 30 segundos por arquivo | ✅ **Aprovado** | Execução ultra-rápida (média de **0.003s** por arquivo). |

---

## 4. Como Executar o Agente 3

O Agente 3 possui CLI própria e opera de forma **100% autônoma**:

### 4.1. Analisar um arquivo de código ou tela diretamente
```bash
python3 agente3_cli.py analyze sample_ergane_module.py
```
*O Agente extrai as informações estruturais e gera o relatório preditivo no terminal e na pasta `output/`.*

### 4.2. Executar o Scorecard de Critérios de Aceitação
```bash
python3 agente3_cli.py test
```
*Executa a bateria de verificação dos 5 critérios da Entrega 2 e exibe o scorecard no terminal.*

### 4.3. Executar os Testes Unitários Automatizados (`unittest`)
```bash
python3 -m unittest tests/test_agente3_standalone.py
```

### 4.4. Cruzar métricas JSON existentes (Modo pipeline)
```bash
python3 agente3_cli.py cruzamento \
  --doc-metrics output/ergane_metricas_sample_ergane_module.json \
  --struct-metrics output/ergane_metricas_sample_ergane_module.json
```

---

## 5. Estrutura dos Arquivos do Agente 3

```
ergane/
├── agente3_cli.py                          # CLI dedicada do Agente 3 (Ponto de entrada)
├── README_AGENTE3.md                       # Documentação da entrega individual
├── config/
│   └── rules_60plus.yaml                   # Regras WCAG 2.2 e usabilidade sênior
├── ergane_agents/
│   ├── agent3_acessibilidade/              # Pacote do Agente 3
│   │   ├── agent.py                        # Classe principal AgenteAcessibilidade
│   │   ├── engine.py                       # Controller (MVC) e gerador de relatórios (View)
│   │   └── predictors.py                   # Preditores especialistas (Factory Method + Decorator)
│   └── shared/                             # Dataclasses tipadas, EventBus e utilitários
├── output/                                 # Relatórios Markdown e JSON gerados
│   ├── relatorio_acessibilidade_*.md       # Relatório executivo com plano de ação
│   └── predicoes_acessibilidade_*.json     # JSON estruturado de barreiras
└── tests/
    └── test_agente3_standalone.py          # Bateria de testes unitários do Agente 3
```
