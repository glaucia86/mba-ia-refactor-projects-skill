# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Arquitetura atual

A aplicação foi refatorada para uma organização MVC adaptada para API Flask:

```text
config/        Configuração por variáveis de ambiente
controllers/   Orquestração dos casos de uso
models/        Acesso a dados SQLite e serialização segura
routes/        Camada HTTP/Views com Blueprints Flask
services/      Validações e constantes de domínio
middlewares/   Tratamento centralizado de erros
app.py         Composition root e bootstrap da aplicação
database.py    Conexão, schema e seed do SQLite
```

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo.

## Configuração

Variáveis opcionais:

```bash
DATABASE_PATH=loja.db
SECRET_KEY=<valor-seguro>
FLASK_DEBUG=false
HOST=0.0.0.0
PORT=5000
SEED_ADMIN_PASSWORD=<senha-admin-local>
SEED_JOAO_PASSWORD=<senha-cliente-local>
SEED_MARIA_PASSWORD=<senha-cliente-local>
```

Se `SECRET_KEY` não for informada, a aplicação gera um valor aleatório em memória no boot. Para produção, informe um segredo estável por variável de ambiente.

As senhas antigas dos usuários seedados foram revogadas. Para conseguir fazer login com os usuários de exemplo em ambiente local, defina as variáveis `SEED_ADMIN_PASSWORD`, `SEED_JOAO_PASSWORD` e `SEED_MARIA_PASSWORD` antes de iniciar a aplicação. Se essas variáveis não forem informadas, a aplicação gera senhas aleatórias não recuperáveis para evitar credenciais padrão no repositório.

## Rotas principais

- `GET /`
- `GET /health`
- `GET /produtos`
- `GET /produtos/busca?q=Mouse`
- `GET /produtos/<id>`
- `POST /produtos`
- `PUT /produtos/<id>`
- `DELETE /produtos/<id>`
- `GET /usuarios`
- `GET /usuarios/<id>`
- `POST /usuarios`
- `POST /login`
- `GET /pedidos`
- `POST /pedidos`
- `GET /pedidos/usuario/<usuario_id>`
- `PUT /pedidos/<pedido_id>/status`
- `GET /relatorios/vendas`

As rotas administrativas antigas (`/admin/reset-db` e `/admin/query`) foram preservadas no roteamento, mas retornam `403` porque eram destrutivas e não tinham autenticação.

## Validação executada

```bash
python -m compileall .
```

Também foram verificados via `Flask.test_client()` os endpoints `/`, `/health`, `/produtos`, `/produtos/1`, `/produtos/busca`, `/usuarios`, `/login`, `/pedidos`, `/relatorios/vendas` e `/admin/query`.

O relatório da auditoria e refatoração está em `reports/audit-project-code-smells.md`.
