import logging
from flask import render_template

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Registers standard HTTP error templates."""

    @app.errorhandler(400)
    def bad_request(error):
        return render_template("errors/400.html", error=error), 400

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html", error=error), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html", error=error), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error(f"Internal Server Error: {error}", exc_info=True)
        return render_template("errors/500.html", error=error), 500
