from models import product_model
from services.validation import normalize_product_payload, validate_product_payload


PRODUCT_NOT_FOUND_ERROR = "Produto não encontrado"


def list_products():
    produtos = product_model.get_all_products()
    return {"dados": produtos, "sucesso": True}, 200


def get_product(product_id):
    produto = product_model.get_product_by_id(product_id)
    if not produto:
        return {"erro": PRODUCT_NOT_FOUND_ERROR, "sucesso": False}, 404
    return {"dados": produto, "sucesso": True}, 200


def create_product(dados):
    error = validate_product_payload(dados)
    if error:
        return {"erro": error}, 400

    payload = normalize_product_payload(dados)
    product_id = product_model.create_product(**payload)
    return {"dados": {"id": product_id}, "sucesso": True, "mensagem": "Produto criado"}, 201


def update_product(product_id, dados):
    produto_existente = product_model.get_product_by_id(product_id)
    if not produto_existente:
        return {"erro": PRODUCT_NOT_FOUND_ERROR}, 404

    error = validate_product_payload(dados)
    if error:
        return {"erro": error}, 400

    payload = normalize_product_payload(dados)
    product_model.update_product(product_id, **payload)
    return {"sucesso": True, "mensagem": "Produto atualizado"}, 200


def delete_product(product_id):
    produto = product_model.get_product_by_id(product_id)
    if not produto:
        return {"erro": PRODUCT_NOT_FOUND_ERROR}, 404

    product_model.delete_product(product_id)
    return {"sucesso": True, "mensagem": "Produto deletado"}, 200


def search_products(args):
    termo = args.get("q", "")
    categoria = args.get("categoria")
    try:
        preco_min = float(args["preco_min"]) if args.get("preco_min") else None
        preco_max = float(args["preco_max"]) if args.get("preco_max") else None
    except ValueError:
        return {"erro": "Filtros de preço devem ser numéricos"}, 400

    resultados = product_model.search_products(termo, categoria, preco_min, preco_max)
    return {"dados": resultados, "total": len(resultados), "sucesso": True}, 200
