from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError

from database import db


def register_error_handlers(app):
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"error": "Recurso não encontrado"}), 404

    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error):
        db.session.rollback()
        app.logger.exception("Database error")
        return jsonify({"error": "Erro interno"}), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unhandled error")
        return jsonify({"error": "Erro interno"}), 500
