from itsdangerous import URLSafeTimedSerializer
from sqlalchemy.orm import selectinload

from config.settings import SECRET_KEY
from database import db
from models.task import Task
from models.user import User
from utils.helpers import MIN_PASSWORD_LENGTH, VALID_ROLES, validate_email


def list_users():
    stmt = db.select(User).options(selectinload(User.tasks))
    users = db.session.scalars(stmt).all()
    result = []
    for user in users:
        user_data = user.to_dict()
        user_data['task_count'] = len(user.tasks)
        result.append(user_data)
    return result, 200


def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    data = user.to_dict()
    data['tasks'] = [task.to_dict() for task in Task.query.filter_by(user_id=user_id).all()]
    return data, 200


def create_user(data):
    if not data:
        return {'error': 'Dados inválidos'}, 400

    error = _validate_user_payload(data, require_password=True)
    if error:
        return error

    existing = User.query.filter_by(email=data['email']).first()
    if existing:
        return {'error': 'Email já cadastrado'}, 409

    user = User()
    user.name = data['name']
    user.email = data['email']
    user.set_password(data['password'])
    user.role = data.get('role', 'user')

    db.session.add(user)
    db.session.commit()
    return user.to_dict(), 201


def update_user(user_id, data):
    user = db.session.get(User, user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404
    if not data:
        return {'error': 'Dados inválidos'}, 400

    error = _validate_user_payload(data, partial=True)
    if error:
        return error

    if 'email' in data:
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            return {'error': 'Email já cadastrado'}, 409
        user.email = data['email']
    if 'name' in data:
        user.name = data['name']
    if 'password' in data:
        user.set_password(data['password'])
    if 'role' in data:
        user.role = data['role']
    if 'active' in data:
        user.active = data['active']

    db.session.commit()
    return user.to_dict(), 200


def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    for task in Task.query.filter_by(user_id=user_id).all():
        db.session.delete(task)
    db.session.delete(user)
    db.session.commit()
    return {'message': 'Usuário deletado com sucesso'}, 200


def get_user_tasks(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    result = []
    for task in tasks:
        task_data = task.to_dict()
        task_data['overdue'] = task.is_overdue()
        result.append(task_data)
    return result, 200


def login(data):
    if not data:
        return {'error': 'Dados inválidos'}, 400

    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return {'error': 'Email e senha são obrigatórios'}, 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return {'error': 'Credenciais inválidas'}, 401
    if not user.active:
        return {'error': 'Usuário inativo'}, 403

    token = URLSafeTimedSerializer(SECRET_KEY).dumps({'user_id': user.id})
    return {
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': token
    }, 200


def _validate_user_payload(data, require_password=False, partial=False):
    if not partial or 'name' in data:
        if not data.get('name'):
            return {'error': 'Nome é obrigatório'}, 400
    if not partial or 'email' in data:
        if not data.get('email'):
            return {'error': 'Email é obrigatório'}, 400
        if not validate_email(data['email']):
            return {'error': 'Email inválido'}, 400
    if require_password or 'password' in data:
        if not data.get('password'):
            return {'error': 'Senha é obrigatória'}, 400
        if len(data['password']) < MIN_PASSWORD_LENGTH:
            return {'error': 'Senha deve ter no mínimo 4 caracteres'}, 400
    if 'role' in data and data['role'] not in VALID_ROLES:
        return {'error': 'Role inválido'}, 400
    return None
