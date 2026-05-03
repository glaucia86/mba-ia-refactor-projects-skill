from flask import Blueprint, jsonify

from controllers import system_controller


admin_bp = Blueprint("admin", __name__)


@admin_bp.post("/admin/reset-db")
def reset_database():
    payload, status = system_controller.admin_endpoint_disabled()
    return jsonify(payload), status


@admin_bp.post("/admin/query")
def executar_query():
    payload, status = system_controller.admin_endpoint_disabled()
    return jsonify(payload), status
