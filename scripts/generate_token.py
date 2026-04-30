#!/usr/bin/env python3
"""
Generate an OAuth2 token.json for Google Drive access (one-time use).

This script reads `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` from the
environment, starts an OAuth2 flow (opens your browser), and saves the
resulting token to `token.json` (or a custom path).

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
from typing import Optional

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except Exception as exc:  # pragma: no cover - dependency may be missing
    print("Missing dependency: google-auth-oauthlib. Install from pip.")
    raise


DEFAULT_SCOPE = ["https://www.googleapis.com/auth/drive.file"]


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
    parser = argparse.ArgumentParser(description="Generate Google OAuth2 token.json")
    parser.add_argument("--out", "-o", default="token.json", help="Output token file path")
    # Accept either REDIRECT_URI or REDIRECT_URL from env for convenience
    default_redirect = os.environ.get("REDIRECT_URI") or os.environ.get("REDIRECT_URL") or "http://localhost:8000/auth/google/callback"
    parser.add_argument("--redirect-uri", "-r", default=default_redirect, help="Redirect URI registered in Google Cloud (default: http://localhost:8000/auth/google/callback)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically (prints auth URL)")
    args = parser.parse_args(argv)

    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("Environment variables GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set.")
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
    print("\nOne-line token JSON (copy to GOOGLE_TOKEN_JSON):\n")
    print(compact)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
