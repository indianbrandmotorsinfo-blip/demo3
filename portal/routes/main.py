import hmac
import logging
from pathlib import Path

from flask import Blueprint, abort, current_app, jsonify, redirect, request, url_for
from flask_login import current_user

from portal.extensions import csrf

logger = logging.getLogger(__name__)

main_bp = Blueprint("main", __name__)

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent.parent / "migrations"


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("student.dashboard"))
    return redirect(url_for("auth.login"))


@main_bp.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "assignment-group-portal"})


@main_bp.route("/internal/init-db", methods=["POST"])
@csrf.exempt
def init_db():
    """One-shot bootstrap for serverless hosting (there is no container entrypoint to run migrations).

    Disabled (404) unless INIT_TOKEN is set. Call with the token in a header:

        curl -X POST -H "X-Init-Token: $INIT_TOKEN" "https://<app>/internal/init-db?seed=admin"

    ?seed=admin  -> create only the administrator (ADMIN_EMAIL / ADMIN_PASSWORD)
    ?seed=demo   -> administrator + demo students, assignments, groups
    (omit seed)  -> just apply migrations
    """
    expected = current_app.config.get("INIT_TOKEN", "")
    supplied = request.headers.get("X-Init-Token", "")
    if not expected or not hmac.compare_digest(supplied.encode(), expected.encode()):
        abort(404)

    from flask_migrate import upgrade
    from portal.seeding import seed_database, SeedError

    seed = request.args.get("seed", "").lower()
    if seed not in ("", "admin", "demo"):
        return jsonify({"ok": False, "error": "seed must be 'admin' or 'demo'"}), 400

    try:
        upgrade(directory=str(MIGRATIONS_DIR))
        seeded = None
        if seed:
            seeded = seed_database(admin_only=(seed == "admin"))
        return jsonify({"ok": True, "migrated": True, "seeded": seeded})
    except SeedError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except Exception:
        logger.exception("init-db failed")
        return jsonify({"ok": False, "error": "init-db failed; see function logs"}), 500
