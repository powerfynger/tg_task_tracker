from functools import wraps

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta

from . import db, app
from .models import Task, User

tasks_bp = Blueprint('tasks_bp', __name__)

users_bp = Blueprint('users_bp', __name__)

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        # TODO:
        # Получение ключа
        if api_key != app.config['API_KEY_BACKEND']:
            print(f"{api_key}\n\n\n")
            return jsonify({"msg": "Invalid API key"}), 401
        return f(*args, **kwargs)
    return decorated_function


@users_bp.route('/users', methods=['GET'])
@require_api_key
def get_users():
    users = User.query.all()
    return jsonify([{'id': user.id, 'username': user.username, 'tg_id': user.tg_id} for user in users])

@users_bp.route('/users/<int:user_id>', methods=['GET'])
@require_api_key
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({'username': user.username, 'tg_id': user.tg_id})

@users_bp.route('/users', methods=['POST'])
@require_api_key
def create_user():
    data = request.get_json()
    new_user = User(
        username=data['username'],
        tg_id=data['tg_id']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'id': new_user.id, 'username': new_user.username, 'tg_id': new_user.tg_id}), 200

@users_bp.route('/users/<int:user_id>', methods=['PUT'])
@require_api_key
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.username = data.get('username', user.username)
    user.tg_id = data.get('tg_id', user.tg_id)
    db.session.commit()
    return jsonify({'id': user.id, 'username': user.username, 'tg_id': user.tg_id}), 200

@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_api_key
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 200

@tasks_bp.route('/tasks', methods=['GET'])
@require_api_key
def get_tasks():
    tasks = Task.query.all()

    return jsonify([task.to_dict() for task in tasks])

@tasks_bp.route('/tasks/<int:tg_id>', methods=['GET'])
@require_api_key
def get_user_tasks(tg_id):
    user = User.query.filter_by(tg_id=tg_id).first()
    if user:
        # tasks = user.tasks.all()
        tasks = user.tasks.order_by(Task.priority.desc())
        return jsonify([task.to_dict() for task in tasks])
    return ''

@tasks_bp.route('/task', methods=['POST'])
@require_api_key
def create_task():
    data = request.get_json()
    user = User.query.filter_by(tg_id=data.get('tg_id')).first()
    try:
        user_id = user.id
    except:
        return '', 418

    new_task = Task(
        title=data.get('title'),
        description=data.get('description', None),
        days_spent=data.get('days_spent', 0),
        deadline=data.get('deadline', datetime.now() + timedelta(weeks=1)),
        priority=data.get('priority', 0),
        user_id=user_id,
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201

@tasks_bp.route('/task/<int:task_id>', methods=['GET'])
@require_api_key
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict()), 200

@tasks_bp.route('/task/<int:task_id>', methods=['PUT'])
@require_api_key
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.days_spent = data.get('days_spent', task.days_spent)
    task.user_id = data.get('user_id', task.user_id)
    try:
        days_bf_deadline = int(data.get('deadline'))
        task.deadline = datetime.now() + timedelta(days=days_bf_deadline)
    except:
        pass
    try:
        task.priority = int(data.get('priority', task.priority))
        db.session.commit()
    except:
        return jsonify(task.to_dict()), 400    
    
    return jsonify(task.to_dict()), 200

@tasks_bp.route('/task/<int:task_id>', methods=['DELETE'])
@require_api_key
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    reason = data.get('is_completed', False)
    if reason:
        user = User.query.get_or_404(task.user_id)
        user.tasks_completed += 1

    db.session.delete(task)
    db.session.commit()
    return '', 204