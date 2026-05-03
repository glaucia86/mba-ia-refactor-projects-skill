from models import user_model


def list_users():
    usuarios = user_model.get_all_users()
    return {"dados": usuarios, "sucesso": True}, 200


def get_user(user_id):
    usuario = user_model.get_user_by_id(user_id)
    if not usuario:
        return {"erro": "Usuário não encontrado"}, 404
    return {"dados": usuario, "sucesso": True}, 200


def create_user(dados):
    if not dados:
        return {"erro": "Dados inválidos"}, 400

    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not nome or not email or not senha:
        return {"erro": "Nome, email e senha são obrigatórios"}, 400

    user_id = user_model.create_user(nome, email, senha)
    return {"dados": {"id": user_id}, "sucesso": True}, 201


def login(dados):
    dados = dados or {}
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not email or not senha:
        return {"erro": "Email e senha são obrigatórios"}, 400

    usuario = user_model.authenticate_user(email, senha)
    if usuario:
        return {"dados": usuario, "sucesso": True, "mensagem": "Login OK"}, 200
    return {"erro": "Email ou senha inválidos", "sucesso": False}, 401
