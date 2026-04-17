from flask import Flask

from app.config import Config
from app.extensions import db, migrate, opensearch
from app.routes import bp as main_bp


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    opensearch.init_app(app)

    app.register_blueprint(main_bp)

    return app
