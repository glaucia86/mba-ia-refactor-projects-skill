from database import get_db


def create_order(usuario_id, itens):
    db = get_db()
    cursor = db.cursor()

    try:
        products = _get_products_for_items(cursor, itens)
        total = 0

        for item in itens:
            product_id = item["produto_id"]
            produto = products.get(product_id)
            if produto is None:
                return {"erro": f"Produto {product_id} não encontrado"}
            if produto["estoque"] < item["quantidade"]:
                return {"erro": "Estoque insuficiente para " + produto["nome"]}
            total += produto["preco"] * item["quantidade"]

        cursor.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, "pendente", total),
        )
        pedido_id = cursor.lastrowid

        for item in itens:
            produto = products[item["produto_id"]]
            cursor.execute(
                """
                INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
                VALUES (?, ?, ?, ?)
                """,
                (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
            )
            cursor.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )

        db.commit()
        return {"pedido_id": pedido_id, "total": total}
    except Exception:
        db.rollback()
        raise


def get_orders_by_user(usuario_id):
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,))
    return _load_order_items(cursor, cursor.fetchall())


def get_all_orders():
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM pedidos")
    return _load_order_items(cursor, cursor.fetchall())


def update_order_status(pedido_id, novo_status):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE pedidos SET status = ? WHERE id = ?",
        (novo_status, pedido_id),
    )
    db.commit()
    return True


def sales_report():
    cursor = get_db().cursor()
    cursor.execute(
        """
        SELECT
            COUNT(*) AS total_pedidos,
            COALESCE(SUM(total), 0) AS faturamento,
            SUM(CASE WHEN status = 'pendente' THEN 1 ELSE 0 END) AS pendentes,
            SUM(CASE WHEN status = 'aprovado' THEN 1 ELSE 0 END) AS aprovados,
            SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END) AS cancelados
        FROM pedidos
        """
    )
    row = cursor.fetchone()
    total_pedidos = row["total_pedidos"]
    faturamento = row["faturamento"]
    desconto = _calculate_discount(faturamento)

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": row["pendentes"],
        "pedidos_aprovados": row["aprovados"],
        "pedidos_cancelados": row["cancelados"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }


def count_orders():
    cursor = get_db().cursor()
    cursor.execute("SELECT COUNT(*) FROM pedidos")
    return cursor.fetchone()[0]


def _get_products_for_items(cursor, itens):
    product_ids = sorted({item["produto_id"] for item in itens})
    placeholders = ",".join("?" for _ in product_ids)
    cursor.execute(f"SELECT * FROM produtos WHERE id IN ({placeholders})", product_ids)
    return {row["id"]: row for row in cursor.fetchall()}


def _load_order_items(cursor, orders):
    if not orders:
        return []

    order_ids = [row["id"] for row in orders]
    placeholders = ",".join("?" for _ in order_ids)
    cursor.execute(
        f"""
        SELECT i.*, p.nome AS produto_nome
        FROM itens_pedido i
        LEFT JOIN produtos p ON p.id = i.produto_id
        WHERE i.pedido_id IN ({placeholders})
        ORDER BY i.pedido_id, i.id
        """,
        order_ids,
    )
    items_by_order = {}
    for item in cursor.fetchall():
        items_by_order.setdefault(item["pedido_id"], []).append(
            {
                "produto_id": item["produto_id"],
                "produto_nome": item["produto_nome"] if item["produto_nome"] else "Desconhecido",
                "quantidade": item["quantidade"],
                "preco_unitario": item["preco_unitario"],
            }
        )

    result = []
    for row in orders:
        result.append(
            {
                "id": row["id"],
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": items_by_order.get(row["id"], []),
            }
        )
    return result


def _calculate_discount(faturamento):
    if faturamento > 10000:
        return faturamento * 0.1
    if faturamento > 5000:
        return faturamento * 0.05
    if faturamento > 1000:
        return faturamento * 0.02
    return 0
