# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Arquitetura atual

O projeto foi refatorado para uma estrutura MVC simples, preservando Express e SQLite:

```text
src/
  app.js
  config/
  controllers/
  database/
  errors/
  middlewares/
  models/
  routes/
  services/
```

- `routes/`: camada de entrada HTTP, equivalente a View em uma API.
- `controllers/`: traduz requisicoes/respostas HTTP.
- `services/`: orquestra casos de uso como checkout, relatorio financeiro e delecao de usuario.
- `models/`: encapsula consultas SQLite.
- `database/`: cria conexao, schema e seeds.
- `middlewares/`: erro centralizado e autorizacao administrativa opcional.
- `config/`: configuracao por variaveis de ambiente.

## Como rodar

```bash
npm install
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot.

Exemplos de requisições estão em `api.http`.

## Configuracao

Variaveis opcionais:

| Variavel | Padrao | Uso |
|---|---|---|
| `PORT` | `3000` | Porta HTTP da API |
| `SQLITE_FILENAME` | `:memory:` | Arquivo SQLite ou banco em memoria |
| `PAYMENT_GATEWAY_KEY` | vazio | Reservado para integracao real de pagamento |
| `ADMIN_TOKEN` | vazio | Quando definido, exige header `x-admin-token` em rotas administrativas |

Com `ADMIN_TOKEN` vazio, os exemplos de `api.http` continuam funcionando sem header para manter compatibilidade local.

## Endpoints

| Metodo | Path | Descricao |
|---|---|---|
| `POST` | `/api/checkout` | Cria usuario quando necessario, processa pagamento simulado, cria matricula e pagamento |
| `GET` | `/api/admin/financial-report` | Retorna receita e alunos por curso |
| `DELETE` | `/api/users/:id` | Remove usuario e dados relacionados via cascade |

## Relatorio da refatoracao

O relatorio da auditoria e da Fase 3 esta em `reports/audit-project-ecommerce-api-legacy.md`.

Validacoes executadas:

```bash
node --check src/app.js
Get-ChildItem src -Recurse -Filter *.js | ForEach-Object { node --check $_.FullName }
PORT=3100 node src/app.js
```

Tambem foram validados manualmente os exemplos de checkout com sucesso, checkout recusado, relatorio financeiro e delecao de usuario.
