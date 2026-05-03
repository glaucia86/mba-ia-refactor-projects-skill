from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db


def row_to_user(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def get_all_users():
    cursor = get_db().cursor()
    cursor.execute("SELECT id, nome, email, tipo, criado_em FROM usuarios")
    return [row_to_user(row) for row in cursor.fetchall()]


def get_user_by_id(user_id):
    cursor = get_db().cursor()
    cursor.execute(
        "SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id = ?",
        (user_id,),
    )
    row = cursor.fetchone()
    return row_to_user(row) if row else None


def create_user(nome, email, senha, tipo="cliente"):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, generate_password_hash(senha), tipo),
    )
    db.commit()
    return cursor.lastrowid


def authenticate_user(email, senha):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    row = cursor.fetchone()
    if not row or not _password_matches(row, senha):
        return None
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
    }


def _password_matches(row, senha):
    stored_password = row["senha"]
    if stored_password.startswith(("scrypt:", "pbkdf2:", "argon2:")):
        return check_password_hash(stored_password, senha)

    if stored_password == senha:
        _upgrade_plaintext_password(row["id"], senha)
        return True
    return False


def _upgrade_plaintext_password(user_id, senha):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE usuarios SET senha = ? WHERE id = ?",
        (generate_password_hash(senha), user_id),
    )
    db.commit()
