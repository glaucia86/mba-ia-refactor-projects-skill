# Refactor Arch - Skill Codex para Auditoria e Refatoração MVC

Este repositorio entrega a skill `refactor-arch` para Codex, criada para auditar projetos backend, identificar anti-patterns arquiteturais e orientar uma refatoração incremental para MVC.

Ferramenta escolhida: **OpenAI Codex**  
Caminho da skill: `.codex/skills/refactor-arch/`

## Análise Manual

### Projeto 1 - `code-smells-project`

Stack detectada: Python + Flask + SQLite. Domínio: e-commerce com produtos, usuários, pedidos e relatórios.

| Severidade | Arquivo | Problema | Justificativa |
|---|---|---|---|
| CRITICAL | `app.py:7-8` | `SECRET_KEY` e `DEBUG` hardcoded | Expoe configuracao sensivel e executa debug no codigo da aplicacao. |
| CRITICAL | `app.py:59-69` | Endpoint `/admin/query` executa SQL arbitrario | Permite execucao remota de queries recebidas via request. |
| CRITICAL | `models.py:28-49`, `models.py:109-110`, `models.py:289-299` | SQL concatenado com dados externos | Risco direto de SQL Injection em leitura, login, criacao e busca. |
| HIGH | `controllers.py:24-62`, `controllers.py:188-220` | Controllers com validacao, regra de negocio, persistencia indireta e notificacao | Viola separacao MVC e dificulta testes isolados. |
| MEDIUM | `models.py:171-233` | Queries N+1 em pedidos e itens | Executa consultas dentro de loops e degrada desempenho conforme volume. |
| MEDIUM | `controllers.py:257-292` | Health check retorna detalhes internos e secret | Mistura verificacao operacional com dados sensiveis. |
| LOW | `controllers.py:52`, `controllers.py:242` | Listas de constantes espalhadas | Categorias e status deveriam ficar em constantes de dominio. |
| LOW | `controllers.py:8-11`, `controllers.py:57` | Uso de `print` para logs | Logs sem nivel/contexto e com risco de dados sensiveis. |

### Projeto 2 - `ecommerce-api-legacy`

Stack detectada: Node.js + Express + SQLite. Dominio: LMS com checkout, cursos, matriculas, pagamentos e relatorio financeiro.

| Severidade | Arquivo | Problema | Justificativa |
|---|---|---|---|
| CRITICAL | `src/utils.js:1-6` | Credenciais e chave de pagamento hardcoded | Secrets ficam versionados e reutilizados em runtime. |
| CRITICAL | `src/AppManager.js:45` | Log de cartao e chave de pagamento | Expoe dados financeiros e credencial em log. |
| HIGH | `src/AppManager.js:4-139` | God Class `AppManager` | Classe inicializa DB, registra rotas, processa checkout, gera relatorios e deleta usuarios. |
| HIGH | `src/utils.js:17-23` | Hash fraco baseado em base64 repetido | Nao e hashing seguro de senha. |
| MEDIUM | `src/AppManager.js:89-127` | N+1 e callback nesting no relatorio financeiro | Consulta usuarios e pagamentos dentro de loops de cursos/matriculas. |
| MEDIUM | `src/AppManager.js:131-136` | Delete de usuario sem integridade referencial | Remove usuario e deixa matriculas/pagamentos inconsistentes. |
| LOW | `src/AppManager.js:29-33` | Campos cripticos (`usr`, `eml`, `pwd`, `c_id`) | Reduz legibilidade e clareza do contrato. |
| LOW | `src/utils.js:9-10` | Estado global mutavel pouco usado | `globalCache` e `totalRevenue` dificultam previsibilidade e testes. |

### Projeto 3 - `task-manager-api`

Stack detectada: Python + Flask + Flask-SQLAlchemy + SQLite. Dominio: gestao de tasks, usuarios, categorias e relatorios.

| Severidade | Arquivo | Problema | Justificativa |
|---|---|---|---|
| CRITICAL | `app.py:11-13` | URI do banco e `SECRET_KEY` hardcoded | Configuracao sensivel fica acoplada ao codigo. |
| HIGH | `models/user.py:27-32` | Senhas com MD5 | Hash obsoleto e inseguro para credenciais. |
| HIGH | `models/user.py:16-25` | Serializer retorna password | Vaza hash/senha em endpoints que usam `to_dict()`. |
| MEDIUM | `routes/task_routes.py:41-57`, `routes/report_routes.py:53-68` | Queries dentro de loops | Gera N+1 em listagens e relatorios. |
| MEDIUM | `routes/task_routes.py:67`, `routes/user_routes.py:29`, `routes/report_routes.py:105` | Uso de `Query.get()` legado | API legada no SQLAlchemy 2.x; preferir `db.session.get(Model, id)`. |
| MEDIUM | `routes/task_routes.py:62`, `routes/user_routes.py:130`, `routes/report_routes.py:186` | `except` generico | Esconde causa real e torna erro inconsistente. |
| LOW | `app.py:7`, `routes/task_routes.py:7` | Imports nao usados | Ruido e baixa higiene de codigo. |
| LOW | `routes/task_routes.py:30-39`, `models/task.py:50-60` | Logica de overdue duplicada | Deveria chamar metodo de dominio unico. |

## Construção da Skill

A skill foi criada com o nome obrigatório `refactor-arch` e estruturada para Codex em:

```text
code-smells-project/.codex/skills/refactor-arch/
  SKILL.md
  agents/openai.yaml
  references/
    project-analysis.md
    antipattern-catalog.md
    audit-report-template.md
    mvc-guidelines.md
    refactoring-playbook.md
```

Decisões de design:

- `SKILL.md` contém apenas o workflow central em três fases: análise, auditoria e refatoração.
- As cinco áreas obrigatórias ficam em arquivos Markdown de referência para preservar contexto e permitir carregamento progressivo.
- O catálogo inclui mais de 8 anti-patterns distribuídos entre CRITICAL, HIGH, MEDIUM e LOW.
- A detecção de APIs deprecated foi incluída explicitamente, com exemplo de `Model.query.get(...)` para SQLAlchemy 2.x.
- O playbook contém 12 padrões de transformação com exemplos antes/depois.
- A Fase 2 tem parada obrigatória antes de qualquer modificação.
- A Fase 3 exige validação por boot da aplicação e endpoints originais.

Como a skill se mantém agnóstica:

- Detecta stack por manifests, imports, entry points e padrões de rota.
- Trata `routes/` como camada View em APIs Flask/Express.
- Preserva framework, banco, gerenciador de pacotes e contratos HTTP existentes.
- Define responsabilidades MVC por camada, não por tecnologia fixa.

## Resultados

Relatórios de auditoria criados:

| Projeto | Relatório | CRITICAL | HIGH | MEDIUM | LOW |
|---|---|---:|---:|---:|---:|
| `code-smells-project` | `reports/audit-project-1.md` | 3 | 1 | 2 | 2 |
| `ecommerce-api-legacy` | `reports/audit-project-2.md` | 2 | 2 | 2 | 2 |
| `task-manager-api` | `reports/audit-project-3.md` | 1 | 2 | 3 | 2 |

Checklist da skill:

- [x] Fase 1 definida para detectar linguagem, framework, domínio e arquitetura.
- [x] Fase 2 definida para gerar relatório com linhas exatas e severidades ordenadas.
- [x] Fase 2 pausa e pede confirmação antes da Fase 3.
- [x] Fase 3 definida para criar ou melhorar estrutura MVC.
- [x] Fase 3 exige extração de config, separação de camadas, error handling e validação.
- [x] Skill validada com `quick_validate.py`.

## Como Executar

Pré-requisitos:

- OpenAI Codex com suporte a skills locais.
- Python para projetos Flask.
- Node.js para o projeto Express.

Executar no projeto 1:

```bash
cd code-smells-project
codex 'Use $refactor-arch to audit this project and refactor it to MVC after confirmation.'
```

Executar no projeto 2:

```bash
cd ecommerce-api-legacy
codex 'Use $refactor-arch to audit this project and refactor it to MVC after confirmation.'
```

Executar no projeto 3:

```bash
cd task-manager-api
codex 'Use $refactor-arch to audit this project and refactor it to MVC after confirmation.'
```

Validar a estrutura da skill:

```bash
python C:\Users\glauc\OneDrive\Documents\Labs\repocheckai\.codex\skills\.system\skill-creator\scripts\quick_validate.py code-smells-project\.codex\skills\refactor-arch
```
