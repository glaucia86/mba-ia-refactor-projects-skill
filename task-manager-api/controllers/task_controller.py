from sqlalchemy.orm import joinedload

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import DEFAULT_PRIORITY, VALID_STATUSES, process_task_data


def _task_payload(task, include_names=False, include_overdue=True):
    data = task.to_dict()
    if include_overdue:
        data['overdue'] = task.is_overdue()
    if include_names:
        data['user_name'] = task.user.name if task.user else None
        data['category_name'] = task.category.name if task.category else None
    return data


def list_tasks():
    stmt = db.select(Task).options(joinedload(Task.user), joinedload(Task.category))
    tasks = db.session.scalars(stmt).all()
    return [_task_payload(task, include_names=True) for task in tasks], 200


def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404
    return _task_payload(task), 200


def create_task(data):
    if not data:
        return {'error': 'Dados inválidos'}, 400

    data = dict(data)
    data.setdefault('status', 'pending')
    data.setdefault('priority', DEFAULT_PRIORITY)
    task_data, error = process_task_data(data)
    if error:
        return {'error': error}, 400
    if 'title' not in task_data:
        return {'error': 'Título é obrigatório'}, 400

    relation_error = _validate_relations(data)
    if relation_error:
        return relation_error

    task = Task()
    _apply_task_data(task, task_data)
    task.user_id = data.get('user_id')
    task.category_id = data.get('category_id')

    db.session.add(task)
    db.session.commit()
    return task.to_dict(), 201


def update_task(task_id, data):
    task = db.session.get(Task, task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404
    if not data:
        return {'error': 'Dados inválidos'}, 400

    task_data, error = process_task_data(data)
    if error:
        return {'error': error}, 400

    relation_error = _validate_relations(data)
    if relation_error:
        return relation_error

    _apply_task_data(task, task_data)
    if 'user_id' in data:
        task.user_id = data['user_id']
    if 'category_id' in data:
        task.category_id = data['category_id']

    db.session.commit()
    return task.to_dict(), 200


def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404

    db.session.delete(task)
    db.session.commit()
    return {'message': 'Task deletada com sucesso'}, 200


def search_tasks(args):
    stmt = db.select(Task)
    query = args.get('q', '')
    status = args.get('status', '')
    priority = args.get('priority', '')
    user_id = args.get('user_id', '')

    if query:
        stmt = stmt.where(
            db.or_(
                Task.title.like(f'%{query}%'),
                Task.description.like(f'%{query}%')
            )
        )
    if status:
        if status not in VALID_STATUSES:
            return {'error': 'Status inválido'}, 400
        stmt = stmt.where(Task.status == status)
    if priority:
        try:
            stmt = stmt.where(Task.priority == int(priority))
        except ValueError:
            return {'error': 'Prioridade inválida'}, 400
    if user_id:
        try:
            stmt = stmt.where(Task.user_id == int(user_id))
        except ValueError:
            return {'error': 'Usuário inválido'}, 400

    tasks = db.session.scalars(stmt).all()
    return [task.to_dict() for task in tasks], 200


def task_stats():
    total = Task.query.count()
    done = Task.query.filter_by(status='done').count()
    all_tasks = Task.query.all()

    stats = {
        'total': total,
        'pending': Task.query.filter_by(status='pending').count(),
        'in_progress': Task.query.filter_by(status='in_progress').count(),
        'done': done,
        'cancelled': Task.query.filter_by(status='cancelled').count(),
        'overdue': sum(1 for task in all_tasks if task.is_overdue()),
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0
    }
    return stats, 200


def _validate_relations(data):
    if data.get('user_id') and not db.session.get(User, data['user_id']):
        return {'error': 'Usuário não encontrado'}, 404
    if data.get('category_id') and not db.session.get(Category, data['category_id']):
        return {'error': 'Categoria não encontrada'}, 404
    return None


def _apply_task_data(task, data):
    for field in ['title', 'description', 'status', 'priority', 'due_date', 'tags']:
        if field in data:
            setattr(task, field, data[field])
