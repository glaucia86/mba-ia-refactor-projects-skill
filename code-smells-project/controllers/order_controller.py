from models import order_model
from services.validation import STATUS_PEDIDO_VALIDOS, validate_order_items


def create_order(dados):
    if not dados:
        return {"erro": "Dados inválidos"}, 400

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        return {"erro": "Usuario ID é obrigatório"}, 400

    error = validate_order_items(itens)
    if error:
        return {"erro": error}, 400

    resultado = order_model.create_order(usuario_id, itens)
    if "erro" in resultado:
        return {"erro": resultado["erro"], "sucesso": False}, 400

    return {
        "dados": resultado,
        "sucesso": True,
        "mensagem": "Pedido criado com sucesso",
    }, 201


def list_user_orders(usuario_id):
    pedidos = order_model.get_orders_by_user(usuario_id)
    return {"dados": pedidos, "sucesso": True}, 200


def list_all_orders():
    pedidos = order_model.get_all_orders()
    return {"dados": pedidos, "sucesso": True}, 200


def update_order_status(pedido_id, dados):
    dados = dados or {}
    novo_status = dados.get("status", "")

    if novo_status not in STATUS_PEDIDO_VALIDOS:
        return {"erro": "Status inválido"}, 400

    order_model.update_order_status(pedido_id, novo_status)
    return {"sucesso": True, "mensagem": "Status atualizado"}, 200
