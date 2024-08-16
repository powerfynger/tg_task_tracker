from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

db = SQLAlchemy()
admin = Admin(name='Admin Panel', template_mode='bootstrap3')

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
admin.init_app(app)



with app.app_context():
    from . import routes
    from .models import User, Task, Timer

    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Task, db.session))
    admin.add_view(ModelView(Timer, db.session))

    
    app.register_blueprint(routes.tasks_bp, url_prefix='/api')
    app.register_blueprint(routes.users_bp, url_prefix='/api')
    app.register_blueprint(routes.timers_bp, url_prefix='/api')

    
    db.create_all()

def create_app():
    return app