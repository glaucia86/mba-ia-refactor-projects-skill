from flask import current_app, jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(HTTPException)
    def http_error(error):
        return jsonify({"erro": error.description, "sucesso": False}), error.code

    @app.errorhandler(Exception)
    def internal_error(error):
        current_app.logger.exception("Unhandled request error")
        return jsonify({"erro": "Erro interno"}), 500
