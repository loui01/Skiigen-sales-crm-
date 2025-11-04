"""Simple sign portal server using Python's standard library.
"""
from __future__ import annotations

import hashlib
import json
import secrets
import sqlite3
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Dict, Tuple
from urllib.parse import parse_qs, quote_plus

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
PUBLIC_DIR = BASE_DIR / "public"
TEMPLATES_DIR = BASE_DIR / "templates"
DB_PATH = DATA_DIR / "users.db"


def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role in ('admin', 'user')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    conn.close()


def hash_password(password: str, salt: str | None = None) -> Tuple[str, str]:
    if salt is None:
        salt_bytes = secrets.token_bytes(16)
    else:
        salt_bytes = bytes.fromhex(salt)
    hash_bytes = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, 100_000)
    return hash_bytes.hex(), salt_bytes.hex()


def load_template(name: str) -> str:
    template_path = TEMPLATES_DIR / name
    return template_path.read_text(encoding="utf-8")


def render_template(name: str, context: Dict[str, str] | None = None) -> str:
    context = context or {}
    content = load_template(name)
    for key, value in context.items():
        content = content.replace(f"{{{{ {key} }}}}", value)
    return content


class SignPortalRequestHandler(BaseHTTPRequestHandler):
    server_version = "SignPortal/1.0"

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/" or self.path.startswith("/?"):
            self.serve_index()
        elif self.path.startswith("/users"):
            self.serve_users()
        elif self.path.startswith("/static/"):
            self.serve_static()
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/register":
            self.handle_register()
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    # Helpers
    def serve_index(self) -> None:
        query = parse_qs(self.path.partition("?")[2])
        message = query.get("message", [""])[0]
        level = query.get("level", ["info"])[0]
        content = render_template(
            "index.html",
            {
                "message": message,
                "message_class": level if message else "",
            },
        )
        encoded = content.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def serve_users(self) -> None:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        with conn:
            rows = conn.execute(
                "SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC"
            ).fetchall()
        conn.close()
        users = [dict(row) for row in rows]
        payload = json.dumps({"users": users}, indent=2)
        encoded = payload.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def serve_static(self) -> None:
        relative_path = self.path.replace("/static/", "", 1)
        candidate = PUBLIC_DIR / relative_path
        if candidate.is_file():
            content = candidate.read_bytes()
            mime_type = "text/css" if candidate.suffix == ".css" else "application/octet-stream"
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", f"{mime_type}; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Asset not found")

    def handle_register(self) -> None:
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        data = parse_qs(body)
        name = (data.get("name") or [""])[0].strip()
        email = (data.get("email") or [""])[0].strip().lower()
        password = (data.get("password") or [""])[0]
        role = (data.get("role") or [""])[0].strip().lower()

        errors = []
        if not name:
            errors.append("Name is required.")
        if not email:
            errors.append("Email is required.")
        if not password:
            errors.append("Password is required.")
        if role not in {"admin", "user"}:
            errors.append("Role must be 'admin' or 'user'.")

        if errors:
            self.redirect_with_message(" ".join(errors), level="error")
            return

        password_hash, salt = hash_password(password)
        try:
            conn = sqlite3.connect(DB_PATH)
            with conn:
                conn.execute(
                    "INSERT INTO users (name, email, password_hash, password_salt, role, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, email, password_hash, salt, role, datetime.utcnow().isoformat()),
                )
            conn.close()
        except sqlite3.IntegrityError:
            self.redirect_with_message("That email is already registered.", level="error")
            return

        self.redirect_with_message("Registration successful!", level="success")

    def redirect_with_message(self, message: str, level: str = "info") -> None:
        location = f"/?message={quote_plus(message)}&level={quote_plus(level)}"
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", location)
        self.end_headers()

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        # Override default logging to include timestamp
        timestamp = datetime.utcnow().isoformat(timespec="seconds")
        Path("server.log").open("a", encoding="utf-8").write(
            "%s - - [%s] %s\n" % (self.client_address[0], timestamp, format % args)
        )


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    init_db()
    httpd = HTTPServer((host, port), SignPortalRequestHandler)
    print(f"Sign portal running on http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    run_server()
