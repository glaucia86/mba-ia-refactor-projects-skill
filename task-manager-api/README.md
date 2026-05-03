# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`. Diferente dos outros projetos, este já possui alguma separação de camadas (`models/`, `routes/`, `services/`, `utils/`), mas ainda contém problemas arquiteturais e de qualidade.

## Resultado do refactor-arch

O projeto foi auditado e refatorado para uma arquitetura MVC incremental, preservando Flask, SQLAlchemy, SQLite e os endpoints públicos existentes.

Estrutura principal após a refatoração:

```text
config/        Configuração baseada em variáveis de ambiente
controllers/   Fluxo de aplicação, validações e orquestração dos casos de uso
middlewares/   Tratamento centralizado de erros
models/        Models SQLAlchemy, serializers seguros e helpers de domínio
routes/        Camada HTTP fina: rotas, request e response JSON
services/      Integrações externas, como notificações
utils/         Constantes e helpers compartilhados
reports/       Relatório de auditoria e refatoração
```

Principais correções aplicadas:

- `app.py` virou composition root/app factory.
- Configuração sensível foi movida para `config/settings.py`.
- Rotas deixaram de concentrar regra de negócio e persistência.
- `Query.get()` foi substituído por `db.session.get(...)`.
- Senhas novas usam hashing do Werkzeug em vez de MD5.
- O serializer público de usuário não retorna mais senha.
- O login não retorna mais token falso previsível; o campo `token` agora recebe um token assinado.
- Erros inesperados e erros de banco passam por handler centralizado.

O relatório completo está em `reports/audit-project-3.md`.

## Como rodar

```bash
pip install -r requirements.txt
python seed.py
python app.py
```

A aplicação sobe por padrão em `http://127.0.0.1:5000`. O `seed.py` popula o banco SQLite (`tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso contrário os endpoints vão retornar listas vazias.

## Configuração

As principais variáveis de ambiente são:

| Variável | Padrão | Uso |
|---|---|---|
| `DATABASE_URI` | `sqlite:///tasks.db` | Banco usado pelo SQLAlchemy |
| `SECRET_KEY` | `dev-secret-key-change-me` | Assinatura de tokens e configuração Flask |
| `FLASK_DEBUG` | `false` | Habilita debug quando `true` |
| `HOST` | `127.0.0.1` | Host do servidor local |
| `PORT` | `5000` | Porta do servidor local |
| `SMTP_HOST` | vazio | Host SMTP para notificações |
| `SMTP_PORT` | `587` | Porta SMTP |
| `SMTP_USER` | vazio | Usuário SMTP |
| `SMTP_PASSWORD` | vazio | Senha SMTP |

Em produção, configure pelo menos `SECRET_KEY` com um valor forte e não use o valor padrão de desenvolvimento.

## Validação executada

```bash
python -m compileall .
```

Também foi executada uma validação com `Flask.test_client()` usando `DATABASE_URI=sqlite:///:memory:` para evitar mutar o `tasks.db` local. Os checks representativos retornaram sucesso para `/`, `/health`, criação/login de usuário, criação de categoria, criação/listagem/stats de task e `/reports/summary`.

## Observações de segurança

Esta refatoração endurece senha, serialização, configuração e erros, mas ainda não implementa autenticação/autorização real nos endpoints destrutivos. Antes de expor a API fora de ambiente local ou didático, adicione um boundary de autenticação e autorização por papel.
