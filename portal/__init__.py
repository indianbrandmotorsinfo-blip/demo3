import logging
from datetime import datetime
from pathlib import Path

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from portal.config import config_by_name, default_config_name, ProductionConfig
from portal.extensions import db, migrate, login_manager, csrf, init_redis
from portal.utilities.helpers import format_datetime, status_badge_class
from portal.utilities.errors import register_error_handlers
from portal.routes import auth_bp, admin_bp, student_bp, main_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# <repo root>/  (portal/ lives one level below it)
BASE_DIR = Path(__file__).resolve().parent.parent


def create_app(config=None) -> Flask:
    """Application factory.

    ``config`` may be a name ("production"), a config class, or None (auto-detect:
    FLASK_ENV if set, otherwise "production" on Vercel and "development" elsewhere).
    """
    if config is None:
        config = default_config_name()

    if isinstance(config, str):
        config_name = config.lower()
        config_class = config_by_name.get(config_name, config_by_name["default"])
    else:
        config_class = config
        config_name = config_class.__name__

    if config_class is ProductionConfig:
        ProductionConfig.validate()

    app = Flask(
        __name__,
        template_folder="templates",  # portal/templates
        # On Vercel, /static/* is served straight from the CDN out of public/static.
        # This mapping only matters for local development (flask run / python app.py).
        static_folder=str(BASE_DIR / "public" / "static"),
        static_url_path="/static",
    )
    app.config.from_object(config_class)

    # Vercel terminates TLS and forwards the original scheme/host/IP.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    db.init_app(app)
    migrate.init_app(app, db, directory=str(BASE_DIR / "migrations"))
    login_manager.init_app(app)
    csrf.init_app(app)
    init_redis(app)

    app.jinja_env.filters["datetime"] = format_datetime
    app.jinja_env.filters["status_badge"] = status_badge_class

    @app.context_processor
    def inject_global_vars():
        return {
            "app_name": app.config.get("APP_NAME", "Assignment Group Portal"),
            "current_year": datetime.now().year,
        }

    register_error_handlers(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(student_bp)

    logger.info("Initialized %s with config '%s'", app.config.get("APP_NAME"), config_name)
    return app
