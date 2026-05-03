CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
STATUS_PEDIDO_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]


def validate_product_payload(dados):
    if not dados:
        return "Dados inválidos"
    if "nome" not in dados:
        return "Nome é obrigatório"
    if "preco" not in dados:
        return "Preço é obrigatório"
    if "estoque" not in dados:
        return "Estoque é obrigatório"

    try:
        preco = float(dados["preco"])
        estoque = int(dados["estoque"])
    except (TypeError, ValueError):
        return "Preço e estoque devem ser numéricos"

    nome = dados["nome"]
    categoria = dados.get("categoria", "geral")
    if preco < 0:
        return "Preço não pode ser negativo"
    if estoque < 0:
        return "Estoque não pode ser negativo"
    if len(nome) < 2:
        return "Nome muito curto"
    if len(nome) > 200:
        return "Nome muito longo"
    if categoria not in CATEGORIAS_VALIDAS:
        return "Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS)
    return None


def normalize_product_payload(dados):
    return {
        "nome": dados["nome"],
        "descricao": dados.get("descricao", ""),
        "preco": float(dados["preco"]),
        "estoque": int(dados["estoque"]),
        "categoria": dados.get("categoria", "geral"),
    }


def validate_order_items(itens):
    if not itens:
        return "Pedido deve ter pelo menos 1 item"

    for item in itens:
        if "produto_id" not in item or "quantidade" not in item:
            return "Itens devem informar produto_id e quantidade"
        try:
            item["produto_id"] = int(item["produto_id"])
            item["quantidade"] = int(item["quantidade"])
        except (TypeError, ValueError):
            return "Produto e quantidade devem ser numéricos"
        if item["quantidade"] <= 0:
            return "Quantidade deve ser maior que zero"
    return None
