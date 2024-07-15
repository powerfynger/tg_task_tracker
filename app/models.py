from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    tg_id = db.Column(db.Integer, unique=True, nullable=False)
    tasks = db.relationship('Task', backref='owner', lazy='dynamic')

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(256))
    hours_spent = db.Column(db.Integer, default=0)
    deadline = db.Column(db.DateTime)
    priority = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {
        'id': self.id,
        'title': self.title,
        'description': self.description,
        'hours_spent': self.hours_spent,
        'deadline': self.deadline.isoformat() if self.deadline else None,
        'priority': self.priority,
        'user_id': self.user_id
        }

        