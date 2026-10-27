"""Authorize Blogger once, keeping credentials in the ignored .blogger directory."""

import argparse
import base64
import getpass
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request, urlopen
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
AUTH_FILE = ROOT / '.blogger' / 'credentials.json'
SCOPE = 'https://www.googleapis.com/auth/blogger'


def save_credentials(auth):
    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    AUTH_FILE.write_text(json.dumps(auth, indent=2), encoding='utf-8')
    os.chmod(AUTH_FILE, 0o600)


def authorize(auth):
    state, verifier = secrets.token_urlsafe(32), secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')
    result = {}

    class Callback(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlsplit(self.path)
            query = parse_qs(parsed.query)
            if parsed.path != '/' or query.get('state') != [state]:
                self.send_error(400)
                return
            result.update(query)
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('授權回應已收到，可以關閉分頁。'.encode())

        def log_message(self, *_):
            pass  # The callback URL contains a one-time authorization code.

    with HTTPServer(('127.0.0.1', 8765), Callback) as server:
        server.timeout = 1
        redirect = 'http://127.0.0.1:8765/'
        url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urlencode({
            'client_id': auth['client_id'], 'redirect_uri': redirect, 'response_type': 'code',
            'scope': SCOPE, 'access_type': 'offline', 'prompt': 'consent',
            'state': state, 'code_challenge': challenge, 'code_challenge_method': 'S256',
        })
        print('Opening Google authorization. Register this redirect URI for a Web client: ' + redirect, flush=True)
        print(url, flush=True)
        webbrowser.open(url)
        deadline = time.monotonic() + 600
        while not result and time.monotonic() < deadline:
            server.handle_request()
    if not result.get('code'):
        raise RuntimeError('Authorization was cancelled or timed out. No credentials uploaded.')
    data = urlencode({'client_id': auth['client_id'], 'client_secret': auth['client_secret'],
                      'code': result['code'][0], 'code_verifier': verifier,
                      'redirect_uri': redirect, 'grant_type': 'authorization_code'}).encode()
    try:
        with urlopen(Request('https://oauth2.googleapis.com/token', data=data), timeout=30) as response:
            token = json.load(response)
    except (HTTPError, URLError, TimeoutError, OSError):
        raise RuntimeError('OAuth code exchange failed; check the client and redirect URI.') from None
    if not token.get('refresh_token'):
        raise RuntimeError('Google did not issue a refresh token. Run authorization again with consent.')
    auth['refresh_token'] = token['refresh_token']
    save_credentials(auth)
    print('Refresh token saved locally in .blogger/credentials.json; no token printed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--github-secrets', action='store_true', help='Upload local credentials to encrypted Actions Secrets using gh')
    parser.add_argument('--worker-secret', action='store_true', help='Upload local api_key to the Cloudflare Worker secret using Wrangler')
    args = parser.parse_args()
    auth = json.loads(AUTH_FILE.read_text(encoding='utf-8')) if AUTH_FILE.exists() else {}
    if args.github_secrets:
        for key in ('client_id', 'client_secret', 'refresh_token'):
            if not auth.get(key):
                raise RuntimeError('Complete local OAuth authorization first.')
        config = json.loads((ROOT / 'blogger.config.json').read_text(encoding='utf-8'))
        for key in ('client_id', 'client_secret', 'refresh_token'):
            subprocess.run(['gh', 'secret', 'set', 'BLOGGER_' + key.upper(),
                            '--repo', config['repository']], input=auth[key], text=True, check=True)
        print('Blogger OAuth credentials saved to encrypted GitHub Actions Secrets.')
    elif args.worker_secret:
        if not auth.get('api_key'):
            raise RuntimeError('Set api_key in .blogger/credentials.json first.')
        subprocess.run(['node', 'node_modules/wrangler/bin/wrangler.js', 'secret', 'put',
                        'BLOGGER_API_KEY'], input=auth['api_key'], text=True, check=True, cwd=ROOT)
    else:
        auth['client_id'] = auth.get('client_id') or input('OAuth client ID: ').strip()
        auth['client_secret'] = auth.get('client_secret') or getpass.getpass('OAuth client secret: ').strip()
        authorize(auth)


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
