"""Vercel entrypoint (also used for local development).

Vercel looks for a top-level WSGI object called ``app`` in this file.

    local:   flask --app app run --debug        (or: python app.py)
    vercel:  vercel dev   /   vercel --prod
"""
from portal import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=app.config.get("DEBUG", False))
