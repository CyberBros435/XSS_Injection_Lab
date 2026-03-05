#!/usr/bin/env python3
"""
Vulnerable Lab (Local Only)
- Frontend: html/index.html, css/style.css, js/app.js
- Backend: Python standard library HTTP server
- Database: SQLite auto-created and seeded in ./data/lab.db

WARNING:
Run locally only. Do NOT expose to the internet.
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
HTML_DIR = APP_DIR / "html"
CSS_DIR = APP_DIR / "css"
JS_DIR = APP_DIR / "js"
DATA_DIR = APP_DIR / "data"
DB_PATH = DATA_DIR / "lab.db"

HOST = "127.0.0.1"
PORT = 8000


def ensure_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            bio TEXT NOT NULL
        )
    """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            comment TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """
    )

    # Seed only if empty
    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if user_count == 0:
        conn.executemany(
            "INSERT INTO users (username, email, bio) VALUES (?, ?, ?)",
            [
                (
                    "alice",
                    "alice@example.com",
                    "Hi, I'm Alice. I love web security labs.",
                ),
                ("bob", "bob@example.com", "Bob here. Practicing XSS and safe coding."),
                (
                    "charlie",
                    "charlie@example.com",
                    "Charlie: learning secure frontend patterns.",
                ),
            ],
        )

    comment_count = conn.execute("SELECT COUNT(*) FROM comments").fetchone()[0]
    if comment_count == 0:
        conn.executemany(
            "INSERT INTO comments (name, comment) VALUES (?, ?)",
            [
                ("Admin", "Welcome to the lab! Try the modules on the left."),
                ("Alice", "This is a <b>bold</b> comment (HTML inside)."),
                ("Bob", "Try switching between Vulnerable vs Safe render modes."),
            ],
        )

    conn.commit()
    conn.close()


def read_file_bytes(path: Path) -> bytes:
    return path.read_bytes()


def json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    # Intentionally minimal headers (part of learning)
    handler.end_headers()
    handler.wfile.write(body)


def text_response(
    handler: BaseHTTPRequestHandler,
    status: int,
    body: str,
    content_type="text/plain; charset=utf-8",
) -> None:
    data = body.encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def get_db_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class LabHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Keep logs readable
        sys.stdout.write(
            "%s - - [%s] %s\n"
            % (self.client_address[0], self.log_date_time_string(), fmt % args)
        )

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        # Serve main page
        if path == "/" or path == "/lab.html":
            return self.serve_static(HTML_DIR / "lab.html", "text/html; charset=utf-8")

        # Serve static assets
        if path.startswith("/vulnerable_lab/css/"):
            file_path = CSS_DIR / path.replace("/vulnerable_lab/css/", "")
            return self.serve_static(file_path, "text/css; charset=utf-8")

        if path.startswith("/vulnerable_lab/js/"):
            file_path = JS_DIR / path.replace("/vulnerable_lab/js/", "")
            return self.serve_static(file_path, "application/javascript; charset=utf-8")

        # API: reflected XSS style response (intentionally unsafe content returned)
        if path == "/api/reflected":
            q = qs.get("q", [""])[0]
            # Intentionally returning q as-is (lab)
            return json_response(
                self, 200, {"ok": True, "reflected": f"You searched for: {q}"}
            )

        # API: list comments
        if path == "/api/comments":
            conn = get_db_conn()
            rows = conn.execute(
                "SELECT id, name, comment, created_at FROM comments ORDER BY id DESC LIMIT 50"
            ).fetchall()
            conn.close()
            comments = [dict(r) for r in rows]
            return json_response(self, 200, {"ok": True, "comments": comments})

        # API: list users (seeded data practice)
        if path == "/api/users":
            conn = get_db_conn()
            rows = conn.execute(
                "SELECT id, username, email, bio FROM users ORDER BY id ASC"
            ).fetchall()
            conn.close()
            users = [dict(r) for r in rows]
            return json_response(self, 200, {"ok": True, "users": users})

        # Basic health endpoint
        if path == "/api/health":
            return json_response(self, 200, {"ok": True, "db": str(DB_PATH)})

        return self.not_found()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length) if length > 0 else b""

        if path == "/api/comments":
            try:
                data = json.loads(raw.decode("utf-8") or "{}")
            except Exception:
                return json_response(self, 400, {"ok": False, "error": "Invalid JSON"})

            name = (data.get("name") or "").strip()
            comment = (data.get("comment") or "").strip()

            if not name or not comment:
                return json_response(
                    self, 400, {"ok": False, "error": "name and comment required"}
                )

            conn = get_db_conn()
            conn.execute(
                "INSERT INTO comments (name, comment) VALUES (?, ?)", (name, comment)
            )
            conn.commit()
            conn.close()

            return json_response(self, 201, {"ok": True})

        return self.not_found()

    def serve_static(self, file_path: Path, content_type: str):
        try:
            # Prevent directory traversal
            file_path = file_path.resolve()
            if not str(file_path).startswith(str(APP_DIR.resolve())):
                return self.forbidden()

            if not file_path.exists() or not file_path.is_file():
                return self.not_found()

            data = read_file_bytes(file_path)
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            return json_response(
                self, 500, {"ok": False, "error": f"Static serve error: {e}"}
            )

    def forbidden(self):
        return text_response(self, 403, "403 Forbidden")

    def not_found(self):
        return text_response(self, 404, "404 Not Found")


def main():
    ensure_db()

    httpd = ThreadingHTTPServer((HOST, PORT), LabHandler)
    print(f"\n[Vulnerable Lab] Running on: http://{HOST}:{PORT}")
    print("[DB] " + str(DB_PATH))
    print("Press CTRL+C to stop.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
