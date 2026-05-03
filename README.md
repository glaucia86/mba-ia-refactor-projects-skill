<div align="center">

# Refactor Arch - Skill Codex para Auditoria e Refatoração MVC

Repositório com a entrega da skill `refactor-arch` usando o OpenAI Codex, criada para auditar projetos backend legados, identificar anti-patterns arquiteturais e orientar uma refatoração incremental para o padrão MVC.

![OpenAI Codex](https://img.shields.io/badge/OpenAI%20Codex-Skill-111111?logo=openai&logoColor=white)
![Python](https://img.shields.io/badge/Python-Flask-3776AB?logo=python&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-Express-339933?logo=node.js&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)
![MVC](https://img.shields.io/badge/Architecture-MVC-5B4B8A)
![Markdown](https://img.shields.io/badge/Docs-Markdown-000000?logo=markdown&logoColor=white)
![Status](https://img.shields.io/badge/Entrega-Alinhada-2ea44f)

</div>

> [!NOTE]
> Este repositório é parte da entrega da tarefa do **[MBA de Engenharia de Software com IA da Full Cycle](https://ia.fullcycle.com.br/mba-ia/)**

## Navegação Rápida

- [Análise Manual](#análise-manual)
- [Criação da Skill](#Criação-da-skill)
- [Resultados](#resultados)
- [Como Executar](#como-executar)
- [Sobre Mim](#sobre-mim)

## Visão Geral

Este repositório entrega uma skill capaz de analisar, auditar e refatorar três projetos legados para uma arquitetura MVC mais clara, segura e sustentável.

Ferramenta escolhida: **OpenAI Codex**

Convenção adotada para a skill:

```text
<projeto>/.codex/skills/refactor-arch/
```

A tarefa usa `.claude/skills/` nos exemplos, mas permite adaptar a estrutura para a ferramenta escolhida. Por isso, a skill foi entregue em `.codex/skills/refactor-arch/` dentro dos três projetos-alvo.

## Análise Manual

### Projeto 1 - `code-smells-project`

Stack detectada: Python + Flask + SQLite. Domínio: e-commerce com produtos, usuários, pedidos e relatórios.

| Severidade | Arquivo | Problema | Justificativa |
|---|---|---|---|
| CRITICAL | `app.py:7-8` | `SECRET_KEY` e `DEBUG` hardcoded | Expõe configuração sensível e executa debug no código da aplicação. |
| CRITICAL | `app.py:59-69` | Endpoint `/admin/query` executa SQL arbitrário | Permite execução remota de queries recebidas via request. |
| CRITICAL | `models.py:28-49`, `models.py:109-110`, `models.py:289-299` | SQL concatenado com dados externos | Risco direto de SQL Injection em leitura, login, criação e busca. |
| HIGH | `controllers.py:24-62`, `controllers.py:188-220` | Controllers com validação, regra de negócio, persistência indireta e notificação | Viola separação MVC e dificulta testes isolados. |
| MEDIUM | `models.py:171-233` | Queries N+1 em pedidos e itens | Executa consultas dentro de loops e degrada desempenho conforme o volume de dados cresce. |
| MEDIUM | `controllers.py:257-292` | Health check retorna detalhes internos e secret | Mistura verificação operacional com dados sensíveis. |
| LOW | `controllers.py:52`, `controllers.py:242` | Listas de constantes espalhadas | Categorias e status deveriam ficar em constantes de domínio. |
| LOW | `controllers.py:8-11`, `controllers.py:57` | Uso de `print` para logs | Logs sem nível/contexto e com risco de expor dados sensíveis. |

### Projeto 2 - `ecommerce-api-legacy`

Stack detectada: Node.js + Express + SQLite. Domínio: LMS com checkout, cursos, matrículas, pagamentos e relatório financeiro.

| Severidade | Arquivo | Problema | Justificativa |
|---|---|---|---|
| CRITICAL | `src/utils.js:1-6` | Credenciais e chave de pagamento hardcoded | Secrets ficam versionados e reutilizados em runtime. |
| CRITICAL | `src/AppManager.js:45` | Log de cartão e chave de pagamento | Expõe dados financeiros e credencial em log. |
| HIGH | `src/AppManager.js:4-139` | God Class `AppManager` | Classe inicializa DB, registra rotas, processa checkout, gera relatórios e deleta usuários. |
| HIGH | `src/utils.js:17-23` | Hash fraco baseado em base64 repetido | Não é hashing seguro de senha. |
| MEDIUM | `src/AppManager.js:89-127` | N+1 e callback nesting no relatório financeiro | Consulta usuários e pagamentos dentro de loops de cursos/matrículas. |
| MEDIUM | `src/AppManager.js:131-136` | Delete de usuário sem integridade referencial | Remove usuário e deixa matrículas/pagamentos inconsistentes. |
| LOW | `src/AppManager.js:29-33` | Campos crípticos (`usr`, `eml`, `pwd`, `c_id`) | Reduz legibilidade e clareza do contrato. |
| LOW | `src/utils.js:9-10` | Estado global mutável pouco usado | `globalCache` e `totalRevenue` dificultam previsibilidade e testes. |

### Projeto 3 - `task-manager-api`

Stack detectada: Python + Flask + Flask-SQLAlchemy + SQLite. Domínio: gestão de tasks, usuários, categorias e relatórios.

| Severidade | Arquivo | Problema | Justificativa |
|---|---|---|---|
| CRITICAL | `app.py:11-13` | URI do banco e `SECRET_KEY` hardcoded | Configuração sensível fica acoplada ao código. |
| HIGH | `models/user.py:27-32` | Senhas com MD5 | Hash obsoleto e inseguro para credenciais. |
| HIGH | `models/user.py:16-25` | Serializer retorna password | Vaza hash/senha em endpoints que usam `to_dict()`. |
| MEDIUM | `routes/task_routes.py:41-57`, `routes/report_routes.py:53-68` | Queries dentro de loops | Gera N+1 em listagens e relatórios. |
| MEDIUM | `routes/task_routes.py:67`, `routes/user_routes.py:29`, `routes/report_routes.py:105` | Uso de `Query.get()` legado | API legada no SQLAlchemy 2.x; preferir `db.session.get(Model, id)`. |
| MEDIUM | `routes/task_routes.py:62`, `routes/user_routes.py:130`, `routes/report_routes.py:186` | `except` genérico | Esconde causa real e torna erro inconsistente. |
| LOW | `app.py:7`, `routes/task_routes.py:7` | Imports não usados | Ruído e baixa higiene de código. |
| LOW | `routes/task_routes.py:30-39`, `models/task.py:50-60` | Lógica de overdue duplicada | Deveria chamar método de domínio único. |

## Criação da Skill

A skill foi criada com o nome obrigatório `refactor-arch` e entregue nos três projetos:

```text
code-smells-project/.codex/skills/refactor-arch/
ecommerce-api-legacy/.codex/skills/refactor-arch/
task-manager-api/.codex/skills/refactor-arch/
```

Cada cópia contém:

```text
SKILL.md
agents/openai.yaml
references/
  project-analysis.md
  antipattern-catalog.md
  audit-report-template.md
  mvc-guidelines.md
  refactoring-playbook.md
```

### Decisões de Design

- `SKILL.md` contém somente o workflow central em três fases: análise, auditoria e refatoração.
- Os arquivos em `references/` concentram conhecimento reutilizável para permitir carregamento progressivo de contexto.
- A Fase 2 tem parada obrigatória antes de qualquer modificação de arquivo.
- A Fase 3 exige validação por boot da aplicação e endpoints originais.
- A skill preserva framework, banco, gerenciador de pacotes e contratos HTTP existentes.
- Em APIs Flask/Express, `routes/` foi tratado como a camada View do MVC, responsável por declarar rotas e traduzir HTTP.

### Anti-patterns Incluídos

O catálogo possui mais de 8 anti-patterns, distribuídos entre CRITICAL, HIGH, MEDIUM e LOW.

| Severidade | Anti-pattern | Motivo |
|---|---|---|
| CRITICAL | Secrets/config hardcoded | Risco direto de vazamento e configuração insegura. |
| CRITICAL | SQL injection/query dinâmica insegura | Permite leitura, alteração ou destruição indevida de dados. |
| CRITICAL/HIGH | God class/god module | Quebra separação de responsabilidades e impede testes isolados. |
| CRITICAL/HIGH | Dados sensíveis em logs/respostas | Expõe senha, cartão, secrets ou detalhes internos. |
| CRITICAL/HIGH | Hash fraco de senha | Compromete credenciais em caso de vazamento. |
| HIGH | Fat controller/route | Acopla HTTP, validação, negócio e persistência. |
| HIGH | Estado global mutável | Dificulta previsibilidade e segurança em runtime. |
| HIGH | Falta de autorização em endpoints destrutivos | Permite operações administrativas sem controle de acesso. |
| MEDIUM | N+1 queries | Degrada performance conforme crescimento dos dados. |
| MEDIUM | APIs deprecated | Evita risco de upgrade e warnings de runtime. |
| MEDIUM | Tratamento genérico de erros | Pode ocultar causa raiz ou vazar detalhes internos. |
| LOW | Magic values, nomes ruins e imports mortos | Reduz legibilidade e manutenção. |

### Playbook de Refatoração

O playbook contém 12 transformações com exemplos antes/depois:

- Configuração hardcoded para módulo `config/settings`.
- SQL concatenado para query parametrizada.
- Endpoint de SQL arbitrário para endpoint desabilitado ou protegido.
- Rota gorda para rota + controller + service.
- God manager para módulos de database, models, controllers, routes e services.
- Query em loop para JOIN ou consulta em lote.
- `Model.query.get(...)` para `db.session.get(Model, id)`.
- MD5/base64 fake hash para hashing seguro.
- Serializer sensível para DTO seguro.
- `except` genérico para error handler centralizado.
- Validação duplicada para helpers compartilhados.
- Campos públicos legados para adapter de compatibilidade.

### Como a Skill se Mantém Agnóstica

- Detecta stack por manifests, imports, entry points e padrões de rota.
- Define responsabilidades MVC por camada, não por tecnologia fixa.
- Adapta a estrutura para Flask, Express ou stacks similares de API.
- Preserva endpoints, métodos HTTP, payloads e comandos existentes sempre que possível.
- Usa os recursos já presentes no projeto antes de sugerir dependência nova.

### Desafios Encontrados

- Os exemplos da tarefa usam Claude Code, mas a entrega foi feita em Codex. A estrutura foi adaptada para `.codex/skills/` sem mudar o conceito de `SKILL.md` + referências Markdown.
- O projeto 3 já tinha uma organização parcial, então a refatoração precisou melhorar MVC sem aplicar uma reescrita desnecessária.
- Alguns endpoints destrutivos não tinham autenticação real. Em vez de inventar uma autorização incompleta, a refatoração preservou compatibilidade quando necessário e registrou risco residual.
- Os projetos não possuíam suítes automatizadas completas. A validação foi feita com boot, compilação/syntax check e chamadas representativas aos endpoints.

## Resultados

### Relatórios de Auditoria

| Projeto | Relatório | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---:|---:|---:|---:|---:|
| `code-smells-project` | `reports/audit-project-1.md` | 5 | 3 | 3 | 1 | 12 |
| `ecommerce-api-legacy` | `reports/audit-project-2.md` | 3 | 3 | 4 | 2 | 12 |
| `task-manager-api` | `reports/audit-project-3.md` | 4 | 3 | 5 | 2 | 14 |

### Comparação Antes/Depois

| Projeto | Antes | Depois |
|---|---|---|
| `code-smells-project` | Flask em poucos arquivos raiz, com rotas, controllers, SQL, validação e serialização misturados. | `app.py` como composition root; `routes/`, `controllers/`, `models/`, `services/`, `config/` e `middlewares/` separados. |
| `ecommerce-api-legacy` | `AppManager` centralizava banco, seed, rotas, checkout, relatório financeiro e delete de usuários. | Express separado em `routes/`, `controllers/`, `services/`, `models/`, `database/`, `config/`, `errors/` e `middlewares/`. |
| `task-manager-api` | Estrutura parcialmente organizada, mas rotas ainda continham validação, ORM, negócio e resposta HTTP. | Rotas ficaram finas; controllers concentram fluxo; models mantêm persistência e DTOs seguros; error handling e config centralizados. |

### Evidências de Validação

| Projeto | Validação executada | Resultado |
|---|---|---|
| `code-smells-project` | `python -m compileall .` e chamadas via `Flask.test_client()` para todos os endpoints originais. | Boot e endpoints principais passaram; `/admin/reset-db` e `/admin/query` retornam `403` por segurança. |
| `ecommerce-api-legacy` | `node --check` nos arquivos JS, boot com `node src/app.js` e chamadas HTTP dos endpoints originais. | Startup observado: `LMS API rodando na porta 3100...`; checkout, relatório financeiro e delete responderam corretamente. |
| `task-manager-api` | `python -m compileall .` e chamadas via `Flask.test_client()` com banco SQLite em memória. | Boot e endpoints representativos passaram; login retorna token assinado e não retorna password no payload do usuário. |

### Checklist de Validação

#### Fase 1 - Análise

- [x] Linguagem detectada corretamente nos 3 projetos.
- [x] Framework detectado corretamente nos 3 projetos.
- [x] Domínio da aplicação descrito corretamente nos 3 projetos.
- [x] Número de arquivos analisados registrado nos relatórios.

#### Fase 2 - Auditoria

- [x] Relatórios seguem formato estruturado.
- [x] Cada finding tem arquivo e linha exatos.
- [x] Findings ordenados por severidade.
- [x] Mínimo de 5 findings identificado em cada projeto.
- [x] Pelo menos 1 finding CRITICAL ou HIGH em cada projeto.
- [x] Pelo menos 2 findings MEDIUM e 2 LOW documentados na análise manual.
- [x] Detecção de APIs deprecated incluída.
- [x] Skill pausa e pede confirmação antes da Fase 3.

#### Fase 3 - Refatoração

- [x] Estrutura de diretórios segue responsabilidades MVC.
- [x] Configuração extraída para módulo de config.
- [x] Models criados ou preservados para abstrair dados/persistência.
- [x] Views/Routes separadas para roteamento.
- [x] Controllers concentram fluxo da aplicação.
- [x] Error handling centralizado.
- [x] Entry point claro.
- [x] Aplicações iniciam sem erros nas validações registradas.
- [x] Endpoints originais respondem corretamente, exceto rotas administrativas inseguras que foram preservadas com resposta segura `403`.

### Riscos Residuais e Trade-offs

- Os projetos continuam sem uma camada completa de autenticação/autorização. Onde não havia base segura, endpoints administrativos foram desabilitados ou ficaram dependentes de configuração como `ADMIN_TOKEN`.
- SQLite foi preservado por ser o banco existente dos projetos, embora não seja ideal para alta concorrência de escrita.
- Algumas compatibilidades legadas foram mantidas, como leitura de senha MD5 antiga no `task-manager-api`, para evitar quebra de bancos já populados.
- Não havia suítes automatizadas completas nos projetos; por isso, a validação foi baseada em compilação/syntax check, boot e endpoints representativos.

## Como Executar

### Pré-requisitos

- OpenAI Codex com suporte a skills locais.
- Python para os projetos Flask.
- Node.js para o projeto Express.
- Dependências instaladas em cada projeto conforme seus respectivos `README.md`, `requirements.txt` ou `package.json`.

### Executar no Projeto 1

```bash
cd code-smells-project
codex 'Use $refactor-arch to audit this project and refactor it to MVC after confirmation.'
```

Validações esperadas:

```bash
python -m compileall .
python app.py
```

Endpoints principais para conferir: `/`, `/health`, `/produtos`, `/usuarios`, `/pedidos`, `/relatorios/vendas`.

### Executar no Projeto 2

```bash
cd ecommerce-api-legacy
codex 'Use $refactor-arch to audit this project and refactor it to MVC after confirmation.'
```

Validações esperadas:

```powershell
Get-ChildItem src -Recurse -Filter *.js | ForEach-Object { node --check $_.FullName }
npm start
```

Endpoints principais para conferir: `POST /api/checkout`, `GET /api/admin/financial-report`, `DELETE /api/users/:id`.

### Executar no Projeto 3

```bash
cd task-manager-api
codex 'Use $refactor-arch to audit this project and refactor it to MVC after confirmation.'
```

Validações esperadas:

```bash
python -m compileall .
python app.py
```

Endpoints principais para conferir: `/`, `/health`, `/tasks`, `/users`, `/login`, `/reports/summary`, `/categories`.

### Validar a Estrutura da Skill

```powershell
python C:\Users\glauc\OneDrive\Documents\Labs\repocheckai\.codex\skills\.system\skill-creator\scripts\quick_validate.py code-smells-project\.codex\skills\refactor-arch
python C:\Users\glauc\OneDrive\Documents\Labs\repocheckai\.codex\skills\.system\skill-creator\scripts\quick_validate.py ecommerce-api-legacy\.codex\skills\refactor-arch
python C:\Users\glauc\OneDrive\Documents\Labs\repocheckai\.codex\skills\.system\skill-creator\scripts\quick_validate.py task-manager-api\.codex\skills\refactor-arch
```

## Sobre Mim

<div align="center">
  <img src="https://github.com/glaucia86.png" width="100" alt="Glaucia Lemos"/>
  <br/><br/>
  <strong>Glaucia Lemos</strong>
  <br/>
  <sub>AI Transformation Lead, Engineering Specialist II @ Itaú | Codex Ambassador | Microsoft MVP - Web Technologies</sub>
  <br/><br/>
  <a href="https://github.com/glaucia86">
    <img src="https://img.shields.io/badge/GitHub-%40glaucia86-181717?logo=github&logoColor=white" alt="GitHub"/>
  </a>
  <a href="https://www.linkedin.com/in/glaucialemos/">
    <img src="https://img.shields.io/badge/LinkedIn-Glaucia%20Lemos-0a66c2?logo=linkedin&logoColor=white" alt="LinkedIn"/>
  </a>
  <a href="https://x.com/glaucia_lemos86">
    <img src="https://img.shields.io/badge/X-%40glaucia__lemos86-000000?logo=x&logoColor=white" alt="X"/>
  </a>
  <a href="https://mvp.microsoft.com/pt-BR/MVP/profile/d3200941-395d-423b-a0ec-eb0577d3bb86">
    <img src="https://img.shields.io/badge/Microsoft%20MVP-Web%20Technologies-0078d4?logo=microsoft&logoColor=white" alt="Microsoft MVP"/>
  </a>
</div>
