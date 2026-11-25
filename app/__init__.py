import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
from .config import config_map

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
migrate = Migrate()

def create_app(config_name: str = os.environ.get("FLASK_CONFIG", "development")) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    db.init_app(app)
    migrate.init_app(app, db)

    from .views import main_bp
    from .users import user_bp
    from .products import product_bp
    from .auth import auth_bp
    from .posts import post_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(post_bp)

    from .products.model import init_db
    with app.app_context():
        init_db()
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html', title='404'), 404
    
    @app.shell_context_processor
    def make_shell_context():
        from .posts.models import Post
        return dict(db=db, Post=Post)
    return app