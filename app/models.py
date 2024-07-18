from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    tg_id = db.Column(db.Integer, unique=True, nullable=False)
    last_time_interaction = db.Column(db.DateTime)
    tasks_completed = db.Column(db.Integer, default=0)

    tasks = db.relationship('Task', backref='owner', lazy='dynamic')

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(256))
    days_spent = db.Column(db.Integer, default=0)
    deadline = db.Column(db.DateTime)
    priority = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {
        'id': self.id,
        'title': self.title,
        'description': self.description,
        'days_spent': self.days_spent,
        'deadline': self.deadline.isoformat() if self.deadline else None,
        'priority': self.priority,
        'user_id': self.user_id
        }

        