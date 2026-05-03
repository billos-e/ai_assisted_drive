#!/usr/bin/env python3
"""
Generate an OAuth2 token.json for Google Drive access (one-time use).

This script reads `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` from the
project `.env` file when available, starts an OAuth2 flow (opens your
browser), and saves the resulting token to `token.json` (or a custom path).

After the flow completes, it also writes the compact token JSON back to
`GOOGLE_TOKEN_JSON` inside `.env`.

Scope: https://www.googleapis.com/auth/drive.file

Usage:
  export GOOGLE_CLIENT_ID=...
  export GOOGLE_CLIENT_SECRET=...
  python scripts/generate_token.py --out token.json

After running, copy the contents of `token.json` into the environment
variable `GOOGLE_TOKEN_JSON` (single-line) on your server.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Optional

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except Exception as exc:  # pragma: no cover - dependency may be missing
    print("Missing dependency: google-auth-oauthlib. Install from pip.")
    raise


DEFAULT_SCOPE = ["https://www.googleapis.com/auth/drive.file"]
DEFAULT_ENV_FILE = Path(".env")


def load_env_file(env_path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not env_path.exists():
        return values

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if value and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        values[key] = value
    return values


def quote_env_value(value: str) -> str:
    if "'" not in value:
        return f"'{value}'"
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def upsert_env_value(env_path: Path, key: str, value: str) -> None:
    lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    updated = False
    new_lines: list[str] = []

    for raw_line in lines:
        stripped = raw_line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            current_key = stripped.split("=", 1)[0].strip()
            if current_key == key:
                new_lines.append(f"{key}={quote_env_value(value)}")
                updated = True
                continue
        new_lines.append(raw_line)

    if not updated:
        if new_lines and new_lines[-1].strip():
            new_lines.append("")
        new_lines.append(f"{key}={quote_env_value(value)}")

    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def resolve_redirect_uri(env_values: dict[str, str]) -> str:
    return (
        env_values.get("REDIRECT_URI")
        or env_values.get("REDIRECT_URL")
        or os.environ.get("REDIRECT_URI")
        or os.environ.get("REDIRECT_URL")
        or "http://localhost:8000/auth/google/callback"
    )


def parse_port_from_redirect(redirect_uri: str) -> int:
    parsed = urllib.parse.urlparse(redirect_uri)
    if parsed.port:
        return parsed.port
    # default to 8000 if not present
    return 8000


class OAuthCallbackServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.authorization_response: Optional[str] = None
        self.error_message: Optional[str] = None


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 - BaseHTTPRequestHandler API
        parsed = urllib.parse.urlsplit(self.path)

        if parsed.path != "/auth/google/callback":
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Not found")
            return

        if "error" in urllib.parse.parse_qs(parsed.query):
            self.server.error_message = parsed.query  # type: ignore[attr-defined]
            self.send_response(400)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"OAuth authorization failed. You can close this window.")
            return

        request_uri = f"http://{self.headers['Host']}{self.path}"
        self.server.authorization_response = request_uri.replace("http://", "https://", 1)  # type: ignore[attr-defined]

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Authorization complete. You can close this window.")

    def log_message(self, format, *args):  # noqa: A003 - inherited API
        return


def wait_for_oauth_callback(host: str, port: int) -> str:
    server = OAuthCallbackServer((host, port), OAuthCallbackHandler)
    try:
        while server.authorization_response is None:
            if server.error_message is not None:
                raise RuntimeError(f"OAuth callback returned an error: {server.error_message}")
            server.handle_request()
        return server.authorization_response
    finally:
        server.server_close()


def main(argv: Optional[list[str]] = None) -> int:

    env_path = Path(DEFAULT_ENV_FILE)
    env_values = load_env_file(env_path)
    default_redirect = resolve_redirect_uri(env_values)

    parser = argparse.ArgumentParser(description="Generate Google OAuth2 token.json")
    parser.add_argument("--out", "-o", default="token.json", help="Output token file path")
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_FILE), help="Path to the .env file to read and update")
    parser.add_argument("--redirect-uri", "-r", default=default_redirect, help="Redirect URI registered in Google Cloud (default: http://localhost:8000/auth/google/callback)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically (prints auth URL)")
    args = parser.parse_args(argv)

    client_id = env_values.get("GOOGLE_CLIENT_ID") or os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = env_values.get("GOOGLE_CLIENT_SECRET") or os.environ.get("GOOGLE_CLIENT_SECRET")

    if not client_id or not client_secret:
        print(f"Missing GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET in {env_path} or environment variables.")
        return 2

    # Build client config using the `web` key (matches Web application credentials)
    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [args.redirect_uri],
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, scopes=DEFAULT_SCOPE)

    port = parse_port_from_redirect(args.redirect_uri)

    # Ensure the flow uses the exact redirect_uri we registered in Google Cloud.
    # We do not use run_local_server(), because it always rewrites the redirect
    # URI to the local root path '/'.
    flow.redirect_uri = args.redirect_uri

    if args.no_browser:
        # Fallback to console flow where user copies the code
        auth_url, _ = flow.authorization_url(prompt="consent")
        print("Open this URL in a browser and follow the steps:\n")
        print(auth_url)
        code = input("Enter the authorization code: ").strip()
        flow.fetch_token(code=code)
        creds = flow.credentials
    else:
        auth_url, _ = flow.authorization_url(prompt="consent")
        print(f"Using redirect URI: {flow.redirect_uri}")
        print("Open this URL in your browser and complete the consent screen:\n")
        print(auth_url)
        authorization_response = wait_for_oauth_callback("localhost", port)
        flow.fetch_token(authorization_response=authorization_response)
        creds = flow.credentials

    data = json.loads(creds.to_json())

    out_path = args.out
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Print a one-line version suitable for copying to an env var
    compact = json.dumps(data, separators=(',', ':'))
    print(f"Saved token to {out_path}")
    upsert_env_value(env_path, "GOOGLE_TOKEN_JSON", compact)
    print(f"Updated {env_path} with GOOGLE_TOKEN_JSON")
    print("\nOne-line token JSON (copy to GOOGLE_TOKEN_JSON):\n")
    print(compact)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
