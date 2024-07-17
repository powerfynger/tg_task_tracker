from flask import Blueprint, jsonify, request
from . import db
from .models import Task, User

tasks_bp = Blueprint('tasks_bp', __name__)

users_bp = Blueprint('users_bp', __name__)

@users_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': user.id, 'username': user.username, 'tg_id': user.tg_id} for user in users])

@users_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({'username': user.username, 'tg_id': user.tg_id})

@users_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(
        username=data['username'],
        tg_id=data['tg_id']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'id': new_user.id, 'username': new_user.username, 'tg_id': new_user.tg_id}), 201

@users_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.username = data.get('username', user.username)
    user.tg_id = data.get('tg_id', user.tg_id)
    db.session.commit()
    return jsonify({'id': user.id, 'username': user.username, 'tg_id': user.tg_id})

@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204

@tasks_bp.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])

@tasks_bp.route('/tasks/<int:tg_id>', methods=['GET'])
def get_user_tasks(tg_id):
    user = User.query.filter_by(tg_id=tg_id).first()
    print(user)
    if user:
        tasks = user.tasks.all()
        print(tasks)
        return jsonify([task.to_dict() for task in tasks])
    return ''

@tasks_bp.route('/task', methods=['POST'])
def create_task():
    data = request.get_json()
    user = User.query.filter_by(tg_id=data.get('tg_id')).first()
    try:
        user_id = user.id
    except:
        return '', 400

    new_task = Task(
        title=data.get('title'),
        description=data.get('description', None),
        hours_spent=data.get('hours_spent', None),
        deadline=data.get('deadline', None),
        priority=data.get('priority', None),
        user_id=user_id,
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201

@tasks_bp.route('/task/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())

@tasks_bp.route('/task/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.hours_spent = data.get('hours_spent', task.hours_spent)
    task.deadline = data.get('deadline', task.deadline)
    task.priority = data.get('priority', task.priority)
    task.user_id = data.get('user_id', task.user_id)

    db.session.commit()
    return jsonify(task.to_dict())

@tasks_bp.route('/task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    reason = data.get('is_completed', False)
    if reason:
        # TODO:
        # Увеличить поле пользователя содержащее кол-во выполненных задач
        pass

    db.session.delete(task)
    db.session.commit()
    return '', 204