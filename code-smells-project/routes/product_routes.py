from flask import Blueprint, jsonify, request

from controllers import product_controller


product_bp = Blueprint("products", __name__)


@product_bp.get("/produtos")
def listar_produtos():
    payload, status = product_controller.list_products()
    return jsonify(payload), status


@product_bp.get("/produtos/busca")
def buscar_produtos():
    payload, status = product_controller.search_products(request.args)
    return jsonify(payload), status


@product_bp.get("/produtos/<int:product_id>")
def buscar_produto(product_id):
    payload, status = product_controller.get_product(product_id)
    return jsonify(payload), status


@product_bp.post("/produtos")
def criar_produto():
    payload, status = product_controller.create_product(request.get_json(silent=True))
    return jsonify(payload), status


@product_bp.put("/produtos/<int:product_id>")
def atualizar_produto(product_id):
    payload, status = product_controller.update_product(
        product_id,
        request.get_json(silent=True),
    )
    return jsonify(payload), status


@product_bp.delete("/produtos/<int:product_id>")
def deletar_produto(product_id):
    payload, status = product_controller.delete_product(product_id)
    return jsonify(payload), status
