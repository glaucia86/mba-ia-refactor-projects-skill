from flask import Blueprint, jsonify

from controllers import system_controller


system_bp = Blueprint("system", __name__)


@system_bp.get("/")
def index():
    payload, status = system_controller.index()
    return jsonify(payload), status


@system_bp.get("/health")
def health_check():
    payload, status = system_controller.health_check()
    return jsonify(payload), status
