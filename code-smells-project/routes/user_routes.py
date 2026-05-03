from flask import Blueprint, jsonify, request

from controllers import user_controller


user_bp = Blueprint("users", __name__)


@user_bp.get("/usuarios")
def listar_usuarios():
    payload, status = user_controller.list_users()
    return jsonify(payload), status


@user_bp.get("/usuarios/<int:user_id>")
def buscar_usuario(user_id):
    payload, status = user_controller.get_user(user_id)
    return jsonify(payload), status


@user_bp.post("/usuarios")
def criar_usuario():
    payload, status = user_controller.create_user(request.get_json(silent=True))
    return jsonify(payload), status


@user_bp.post("/login")
def login():
    payload, status = user_controller.login(request.get_json(silent=True))
    return jsonify(payload), status
