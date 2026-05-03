from flask import Blueprint, jsonify, request

from controllers import category_controller, report_controller


report_bp = Blueprint('reports', __name__)


def _json_response(result):
    data, status = result
    return jsonify(data), status


@report_bp.route('/reports/summary', methods=['GET'])
def summary_report():
    return _json_response(report_controller.summary_report())


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report(user_id):
    return _json_response(report_controller.user_report(user_id))


@report_bp.route('/categories', methods=['GET'])
def get_categories():
    return _json_response(category_controller.list_categories())


@report_bp.route('/categories', methods=['POST'])
def create_category():
    return _json_response(category_controller.create_category(request.get_json()))


@report_bp.route('/categories/<int:cat_id>', methods=['PUT'])
def update_category(cat_id):
    return _json_response(category_controller.update_category(cat_id, request.get_json()))


@report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    return _json_response(category_controller.delete_category(cat_id))
