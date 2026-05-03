from flask import Blueprint, jsonify

from controllers import report_controller


report_bp = Blueprint("reports", __name__)


@report_bp.get("/relatorios/vendas")
def relatorio_vendas():
    payload, status = report_controller.sales_report()
    return jsonify(payload), status
