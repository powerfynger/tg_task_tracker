from functools import wraps

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta

from . import db, app
from .models import Task, User, Timer

timers_names = {
    0 : 'Pomodoro: 25/5',
    1 : 'Neo Pomodoro: 52/17',
    2 : 'School: 45/15',
    3 : 'Deep: 90/30',
    # 4 : 'Test: 1/1'
}

timers_duration = {
    0 : (25, 5),
    1 : (52, 17),
    2 : (45, 15),
    3 : (90, 30),
    # 4 : (1, 1)
}

tasks_bp = Blueprint('tasks_bp', __name__)

users_bp = Blueprint('users_bp', __name__)

timers_bp = Blueprint('timers_bp', __name__)

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
    return jsonify([user.to_dict() for user in users])

@users_bp.route('/user', methods=['GET'])
@require_api_key
def get_user_info():
    try:
        data = request.get_json()
    except:
        return '', 400

    query = User.query
    for key, value in data.items():
        if hasattr(User, key): 
            query = query.filter(getattr(User, key) == value)

    users = query.all()
    
    if users:
        return jsonify([user.to_dict() for user in users])  
    
    return '', 404


@users_bp.route('/user', methods=['POST'])
@require_api_key
def create_user():
    data = request.get_json()
    new_user = User(
        username=data['username'],
        tg_id=data['tg_id']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 200

@users_bp.route('/user/<int:user_id>', methods=['GET'])
@require_api_key
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@users_bp.route('/user_tg/<int:tg_id>', methods=['GET'])
@require_api_key
def get_user_tg(tg_id):
    try:
        data = request.get_json()
    except:
        data = None
    user = User.query.filter_by(tg_id=tg_id).first()
    if user:
        return jsonify(user.to_dict())
    return ''


@users_bp.route('/user/<int:user_id>', methods=['PUT'])
@require_api_key
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.username = data.get('username', user.username)
    user.tg_id = data.get('tg_id', user.tg_id)
    user.is_subscribed_to_daily= data.get('is_subscribed_to_daily', user.is_subscribed_to_daily)
    db.session.commit()
    return jsonify(user.to_dict()), 200

@users_bp.route('/user/<int:user_id>', methods=['DELETE'])
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
        planned_for_tomorrow=data.get('planned_for_tomorrow', False),
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
    print(data)
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.days_spent = data.get('days_spent', task.days_spent)
    task.planned_for_tomorrow = data.get('planned_for_tomorrow', task.planned_for_tomorrow)
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

@tasks_bp.route('/timers', methods=['GET'])
@require_api_key
def get_timers():
    return timers_names, 200

@tasks_bp.route('/timer', methods=['PUT'])
@require_api_key
def update_timer():
    try:
        data = request.get_json()
    except:
        return '', 400    
    
    user = User.query.filter_by(tg_id=data.get('tg_id')).first()
    if user.has_timer:
        timer = user.timer
        if data.get('state') is not None:
            timer.state = not timer.state 
            user.productivity_time += timers_duration[timer.type_id][timer.state]
            timer.time_end=datetime.now() + timedelta(minutes=timers_duration[timer.type_id][1-timer.state])
            db.session.commit()
        return jsonify(timer.to_dict()), 200
    return '', 400


@tasks_bp.route('/timer', methods=['GET'])
@require_api_key
def get_user_timer():
    try:
        data = request.get_json()
    except:
        return '', 400
    query = User.query
    for key, value in data.items():
        if hasattr(User, key): 
            query = query.filter(getattr(User, key) == value)
    
    user = query.first()
        
    if user is None:
        return '', 400
        
    if user.has_timer:
        timer = user.timer
        return jsonify(timer.to_dict()), 200
    return '', 400

@tasks_bp.route('/timer', methods=['POST'])
@require_api_key
def create_timer():
    data = request.get_json()
    user = User.query.filter_by(tg_id=data.get('tg_id')).first()
    try:
        user_id = user.id
    except:
        return '', 418

    new_timer = Timer(
        type_id=data.get('type_id'),
        time_start=datetime.now(),
        state=True,
        time_end=datetime.now() + 
        timedelta(minutes=timers_duration[data.get('type_id')][0]),
        user_id=user_id,
    )
    user.has_timer = True
    db.session.add(new_timer)
    db.session.commit()
    return jsonify(new_timer.to_dict())

@tasks_bp.route('/timer', methods=['DELETE'])
@require_api_key
def delete_timer():
    data = request.get_json()
    user = User.query.filter_by(tg_id=data.get('tg_id')).first()
    if user.has_timer:
        timer = user.timer
        user.has_timer = False
        db.session.delete(timer)
        db.session.commit()
        return '', 200
    return '', 400
