from datetime import datetime, timedelta

from database import db
from models.category import Category
from models.task import Task
from models.user import User


def summary_report():
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    tasks = Task.query.all()
    users = User.query.all()
    tasks_by_user = {}
    for task in tasks:
        if task.user_id:
            tasks_by_user.setdefault(task.user_id, []).append(task)

    overdue_list = [
        {
            'id': task.id,
            'title': task.title,
            'due_date': str(task.due_date),
            'days_overdue': (datetime.utcnow() - task.due_date).days
        }
        for task in tasks
        if task.is_overdue()
    ]

    user_stats = []
    for user in users:
        user_tasks = tasks_by_user.get(user.id, [])
        completed = sum(1 for task in user_tasks if task.status == 'done')
        total = len(user_tasks)
        user_stats.append({
            'user_id': user.id,
            'user_name': user.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0
        })

    report = {
        'generated_at': str(datetime.utcnow()),
        'overview': {
            'total_tasks': total_tasks,
            'total_users': total_users,
            'total_categories': total_categories,
        },
        'tasks_by_status': {
            'pending': Task.query.filter_by(status='pending').count(),
            'in_progress': Task.query.filter_by(status='in_progress').count(),
            'done': Task.query.filter_by(status='done').count(),
            'cancelled': Task.query.filter_by(status='cancelled').count(),
        },
        'tasks_by_priority': {
            'critical': Task.query.filter_by(priority=1).count(),
            'high': Task.query.filter_by(priority=2).count(),
            'medium': Task.query.filter_by(priority=3).count(),
            'low': Task.query.filter_by(priority=4).count(),
            'minimal': Task.query.filter_by(priority=5).count(),
        },
        'overdue': {
            'count': len(overdue_list),
            'tasks': overdue_list,
        },
        'recent_activity': {
            'tasks_created_last_7_days': Task.query.filter(Task.created_at >= seven_days_ago).count(),
            'tasks_completed_last_7_days': Task.query.filter(
                Task.status == 'done',
                Task.updated_at >= seven_days_ago
            ).count(),
        },
        'user_productivity': user_stats,
    }

    return report, 200


def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    done = sum(1 for task in tasks if task.status == 'done')
    pending = sum(1 for task in tasks if task.status == 'pending')
    in_progress = sum(1 for task in tasks if task.status == 'in_progress')
    cancelled = sum(1 for task in tasks if task.status == 'cancelled')
    overdue = sum(1 for task in tasks if task.is_overdue())
    high_priority = sum(1 for task in tasks if task.priority <= 2)
    total = len(tasks)

    report = {
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
        },
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': pending,
            'in_progress': in_progress,
            'cancelled': cancelled,
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0
        }
    }

    return report, 200
