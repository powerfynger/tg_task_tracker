from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    tg_id = db.Column(db.Integer, unique=True, nullable=False)
    last_time_interaction = db.Column(db.DateTime)
    tasks_completed = db.Column(db.Integer, default=0)
    is_subscribed_to_daily = db.Column(db.Boolean, default=True)
    has_timer = db.Column(db.Boolean, default=False)

    tasks = db.relationship('Task', backref='owner', lazy='dynamic')
    timer = db.relationship('Timer', uselist=False, back_populates='user')
    
    def to_dict(self):
        return {
        'id': self.id,
        'username': self.username,
        'tg_id': self.tg_id,
        'last_time_interaction': self.last_time_interaction,
        'tasks_completed': self.tasks_completed,
        'is_subscribed_to_daily': self.is_subscribed_to_daily,
        'has_timer': self.has_timer
        }

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(256))
    days_spent = db.Column(db.Integer, default=0)
    deadline = db.Column(db.DateTime)
    priority = db.Column(db.Integer, default=0)
    planned_for_tomorrow = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {
        'id': self.id,
        'title': self.title,
        'description': self.description,
        'days_spent': self.days_spent,
        'deadline': self.deadline.isoformat() if self.deadline else None,
        'priority': self.priority,
        'planned_for_tomorrow': self.planned_for_tomorrow,
        'user_id': self.user_id
        }
class Timer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, default=0)
    
    time_start = db.Column(db.DateTime)
    time_end = db.Column(db.DateTime)
    state = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    user = db.relationship('User', back_populates='timer')
    def to_dict(self):
        return {
        'id': self.id,
        'type_id': self.type_id,
        'time_start': self.time_start,
        'time_end': self.time_end,
        'state': self.state,
        'user_id': self.user_id,
        }

def reset_planned_for_tomorrow():
    tasks = Task.query.filter_by(planned_for_tomorrow=True).all()
    for task in tasks:
        task.planned_for_tomorrow = False
    db.session.commit()        