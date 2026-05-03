from models import order_model, product_model, user_model


def index():
    return {
        "mensagem": "Bem-vindo à API da Loja",
        "versao": "1.0.0",
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    }, 200


def health_check():
    return {
        "status": "ok",
        "database": "connected",
        "counts": {
            "produtos": len(product_model.get_all_products()),
            "usuarios": len(user_model.get_all_users()),
            "pedidos": order_model.count_orders(),
        },
        "versao": "1.0.0",
        "ambiente": "producao",
    }, 200


def admin_endpoint_disabled():
    return {"erro": "Endpoint administrativo desabilitado", "sucesso": False}, 403
