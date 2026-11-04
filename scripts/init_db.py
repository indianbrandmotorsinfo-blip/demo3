"""Apply database migrations (and optionally seed) from your own machine.

    # point at the same database Vercel uses
    vercel env pull .env.local            # or: export DATABASE_URL=...
    python scripts/init_db.py                  # migrations only
    python scripts/init_db.py --seed admin     # + administrator (needs ADMIN_PASSWORD)
    python scripts/init_db.py --seed demo      # + demo data
"""
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from flask_migrate import upgrade  # noqa: E402

from portal import create_app  # noqa: E402
from portal.seeding import seed_database  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", choices=["admin", "demo"], help="optionally seed data after migrating")
    args = parser.parse_args()

    # Scripts run on your laptop, so default to development unless told otherwise,
    # but still honour FLASK_ENV if you export it.
    app = create_app(os.getenv("FLASK_ENV") or "development")
    with app.app_context():
        print("Applying migrations...")
        upgrade(directory=str(ROOT / "migrations"))
        print("Migrations applied.")
        if args.seed:
            seed_database(admin_only=(args.seed == "admin"))


if __name__ == "__main__":
    main()
