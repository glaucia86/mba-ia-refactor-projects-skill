from flask import Blueprint, jsonify, request

from controllers import user_controller


user_bp = Blueprint('users', __name__)


def _json_response(result):
    data, status = result
    return jsonify(data), status


@user_bp.route('/users', methods=['GET'])
def get_users():
    return _json_response(user_controller.list_users())


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return _json_response(user_controller.get_user(user_id))


@user_bp.route('/users', methods=['POST'])
def create_user():
    return _json_response(user_controller.create_user(request.get_json()))


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    return _json_response(user_controller.update_user(user_id, request.get_json()))


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    return _json_response(user_controller.delete_user(user_id))


@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    return _json_response(user_controller.get_user_tasks(user_id))


@user_bp.route('/login', methods=['POST'])
def login():
    return _json_response(user_controller.login(request.get_json()))
