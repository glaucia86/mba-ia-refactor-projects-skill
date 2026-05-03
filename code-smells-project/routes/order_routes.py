from flask import Blueprint, jsonify, request

from controllers import order_controller


order_bp = Blueprint("orders", __name__)


@order_bp.post("/pedidos")
def criar_pedido():
    payload, status = order_controller.create_order(request.get_json(silent=True))
    return jsonify(payload), status


@order_bp.get("/pedidos")
def listar_todos_pedidos():
    payload, status = order_controller.list_all_orders()
    return jsonify(payload), status


@order_bp.get("/pedidos/usuario/<int:usuario_id>")
def listar_pedidos_usuario(usuario_id):
    payload, status = order_controller.list_user_orders(usuario_id)
    return jsonify(payload), status


@order_bp.put("/pedidos/<int:pedido_id>/status")
def atualizar_status_pedido(pedido_id):
    payload, status = order_controller.update_order_status(
        pedido_id,
        request.get_json(silent=True),
    )
    return jsonify(payload), status
