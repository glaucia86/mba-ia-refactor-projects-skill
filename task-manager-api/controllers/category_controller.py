from database import db
from models.category import Category
from models.task import Task
from utils.helpers import DEFAULT_COLOR


def list_categories():
    counts = dict(
        db.session.query(Task.category_id, db.func.count(Task.id))
        .group_by(Task.category_id)
        .all()
    )
    categories = Category.query.all()
    result = []
    for category in categories:
        category_data = category.to_dict()
        category_data['task_count'] = counts.get(category.id, 0)
        result.append(category_data)
    return result, 200


def create_category(data):
    if not data:
        return {'error': 'Dados inválidos'}, 400

    name = data.get('name')
    if not name:
        return {'error': 'Nome é obrigatório'}, 400

    category = Category()
    category.name = name
    category.description = data.get('description', '')
    category.color = data.get('color', DEFAULT_COLOR)

    db.session.add(category)
    db.session.commit()
    return category.to_dict(), 201


def update_category(cat_id, data):
    category = db.session.get(Category, cat_id)
    if not category:
        return {'error': 'Categoria não encontrada'}, 404
    if not data:
        return {'error': 'Dados inválidos'}, 400

    if 'name' in data:
        category.name = data['name']
    if 'description' in data:
        category.description = data['description']
    if 'color' in data:
        category.color = data['color']

    db.session.commit()
    return category.to_dict(), 200


def delete_category(cat_id):
    category = db.session.get(Category, cat_id)
    if not category:
        return {'error': 'Categoria não encontrada'}, 404

    db.session.delete(category)
    db.session.commit()
    return {'message': 'Categoria deletada'}, 200
