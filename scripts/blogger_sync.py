"""Mirror repository articles to Blogger; a dry run is the default."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build_static_articles as articles

CONFIG = json.loads((ROOT / 'blogger.config.json').read_text(encoding='utf-8'))
SCOPE = 'https://www.googleapis.com/auth/blogger'
TOKEN_URL = 'https://oauth2.googleapis.com/token'
STATE_FILE = ROOT / '.blogger' / 'state.json'
MARKER = 'data-ian-blogger-sync'
EXPORT_VERSION = 2
POST_STYLE = '''<style>
.ian-blogger-article { line-height:1.85; overflow-wrap:anywhere; }
.ian-blogger-article img { max-width:100%; height:auto; }
.ian-blogger-article figure { margin:1.5em 0; }
.ian-blogger-article figcaption { font-size:.9em; }
.ian-blogger-article .table-wrapper { overflow-x:auto; }
.ian-blogger-article table { border-collapse:collapse; width:100%; }
.ian-blogger-article th,.ian-blogger-article td { border:1px solid #888; padding:.6em; }
.ian-blogger-article pre { overflow-x:auto; white-space:pre; }
.ian-blogger-article .callout-box,.ian-blogger-article .article-lead-box { border-left:3px solid #888; padding:1em; margin:1em 0; }
</style>'''


def credentials():
    path = ROOT / '.blogger' / 'credentials.json'
    local = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    return {key: os.environ.get('BLOGGER_' + key.upper()) or local.get(key, '')
            for key in ('client_id', 'client_secret', 'refresh_token')}


def save_state(state, path=STATE_FILE):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(state), encoding='utf-8')
    temporary.replace(path)


def read_state(path=STATE_FILE):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}


class APIError(RuntimeError):
    def __init__(self, status, retry_after=0):
        self.status = status
        self.retry_after = retry_after
        super().__init__(f'Google API HTTP {status}; stopped without retrying writes.')


def request_json(url, method='GET', body=None, headers=None):
    data = None if body is None else json.dumps(body).encode('utf-8')
    request = Request(url, method=method, data=data,
                      headers={'Content-Type': 'application/json', **(headers or {})})
    try:
        with urlopen(request, timeout=60) as response:
            raw = response.read()
            return json.loads(raw) if raw else {}
    except HTTPError as error:
        retry = error.headers.get('Retry-After', '0')
        raise APIError(error.code, int(retry) if retry.isdigit() else 0) from None
    except (URLError, TimeoutError, OSError):
        # A failed POST response can still mean Google created the post. Rescan next run.
        raise RuntimeError('Google API connection failed; stopped without retrying writes.') from None


class BloggerAPI:
    def __init__(self, auth, blog_id):
        if not all(auth.values()):
            raise RuntimeError('Set BLOGGER_CLIENT_ID, BLOGGER_CLIENT_SECRET and BLOGGER_REFRESH_TOKEN; see docs/DEVELOPMENT.md.')
        self.auth = auth
        self.base = f'https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts'
        self.token = ''
        self.expires = 0

    def access_token(self):
        if time.time() >= self.expires:
            data = urlencode({**self.auth, 'grant_type': 'refresh_token'}).encode()
            try:
                with urlopen(Request(TOKEN_URL, data=data), timeout=30) as response:
                    token = json.load(response)
            except (HTTPError, URLError, TimeoutError, OSError):
                raise RuntimeError('OAuth refresh failed; renew authorization with scripts/blogger_auth.py.') from None
            self.token = token['access_token']
            self.expires = time.time() + int(token.get('expires_in', 3600)) - 120
        return self.token

    def call(self, method='GET', post_id='', body=None, **query):
        url = self.base + (f'/{post_id}' if post_id else '')
        if query:
            url += '?' + urlencode(query, doseq=True)
        return request_json(url, method, body, {'Authorization': 'Bearer ' + self.access_token()})

    def posts(self):
        posts, page_token, seen = [], '', set()
        while True:
            query = {'pageToken': page_token} if page_token else {}
            page = self.call(view='ADMIN', status=['live', 'draft', 'scheduled'],
                             fetchBodies='true', maxResults=100, **query)
            posts.extend(page.get('items', []))
            page_token = page.get('nextPageToken', '')
            if not page_token:
                return posts
            if page_token in seen:
                raise RuntimeError('Repeated Blogger page token; stopped before writing.')
            seen.add(page_token)
            time.sleep(1)


def export_article(art):
    source = articles.CONTENT_DIR / art['folder'] / art['old_filename']
    raw = source.read_text(encoding='utf-8')
    soup = BeautifulSoup(raw, 'html.parser')
    container = soup.select_one('.article-container')
    if container is None:
        raise RuntimeError(f'Missing article container: {source.name}')
    source_id = f"{art['folder']}_{art['order']:03d}"
    labels = art['tags']
    title = soup.h1.get_text(' ', strip=True)
    digest = hashlib.sha256(json.dumps([EXPORT_VERSION, raw, labels, art['date_published']],
                                      ensure_ascii=False).encode()).hexdigest()
    marker = {'repository': CONFIG['repository'], 'source': source_id,
              'sha256': digest, 'labels': labels}
    for node in container.select('script, .material-symbols-outlined, .article-bottom-actions, .article-trainerhub-cta, h1'):
        node.decompose()
    base_url = articles.article_public_url(art)
    for node in container.select('[href], [src]'):
        for attr in ('href', 'src'):
            if node.has_attr(attr):
                node[attr] = urljoin(base_url, node[attr])
    wrapper = soup.new_tag('div', attrs={'class': 'ian-blogger-article',
                                       MARKER: json.dumps(marker, separators=(',', ':'))})
    wrapper.append(container)
    return {'source': source_id, 'marker': marker,
            'body': {'title': title, 'labels': labels, 'published': art['date_published'],
                     'content': POST_STYLE + str(wrapper)}}


def managed_posts(posts):
    managed = {}
    for post in posts:
        node = BeautifulSoup(post.get('content', ''), 'html.parser').find(attrs={MARKER: True})
        if node is None:
            continue
        try:
            marker = json.loads(node[MARKER])
        except (ValueError, TypeError):
            raise RuntimeError(f"Invalid sync marker on Blogger post {post['id']}; inspect manually.") from None
        if marker.get('repository') != CONFIG['repository']:
            continue
        source = marker['source']
        if source in managed:
            raise RuntimeError(f'Duplicate Blogger source {source}; inspect manually before syncing.')
        managed[source] = (post, marker)
    return managed


def plan_sync(local, remote):
    managed = managed_posts(remote)
    desired = {item['source']: item for item in local}
    if len(desired) != len(local):
        raise RuntimeError('Duplicate local article IDs.')
    operations = []
    # Remove withdrawn articles first, then update existing articles before adding new ones.
    for source, (post, _) in managed.items():
        if source not in desired:
            if post.get('status') == 'DRAFT':
                raise RuntimeError(f"Removed source {source} is a Blogger draft; move it to trash manually.")
            operations.append(('delete', source, post['id'], None))
    for item in local:
        source, body = item['source'], dict(item['body'])
        if source not in managed:
            operations.append(('insert', source, '', body))
            continue
        post, previous = managed[source]
        if item['marker']['sha256'] != previous.get('sha256'):
            # Native labels added in Blogger survive subsequent local text edits.
            extra = set(post.get('labels', [])) - set(previous.get('labels', []))
            body['labels'] = sorted(set(body['labels']) | extra)
            operations.append(('update', source, post['id'], body))
    return sorted(operations, key=lambda item: {'delete': 0, 'update': 1, 'insert': 2}[item[0]])


def sync(api, local, state, *, apply=False, interval=120, limit=5,
         now=time.time, sleep=time.sleep, persist=save_state):
    if state.get('cooldown_until', 0) > now():
        raise RuntimeError('Blogger cooldown is active; no API calls made. See .blogger/state.json.')
    try:
        operations = plan_sync(local, api.posts())
        counts = {verb: sum(op[0] == verb for op in operations) for verb in ('insert', 'update', 'delete')}
        print('Blogger plan: ' + json.dumps(counts) + ('' if apply else ' (dry run; no writes)'), flush=True)
        if not apply:
            return len(operations)
        for verb, source, post_id, body in operations[:limit]:
            # Waiting before the first write also separates runs if the cache was evicted.
            sleep(max(interval, state.get('last_write', 0) + interval - now()))
            state['last_write'] = now()
            persist(state)
            if verb == 'insert':
                api.call('POST', body=body, isDraft='false')
            elif verb == 'update':
                api.call('PATCH', post_id, body=body)
            else:
                api.call('DELETE', post_id, useTrash='true')
            state['last_write'] = now()
            persist(state)
            print(f'{verb}: {source}', flush=True)
        pending = max(0, len(operations) - limit)
        print(f'Blogger batch complete; {pending} pending for the next scheduled run.')
        return pending
    except APIError as error:
        if error.status in (403, 429):
            state['cooldown_until'] = now() + max(CONFIG['cooldownSeconds'], error.retry_after)
            persist(state)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Write changes (otherwise dry run)')
    parser.add_argument('--export-only', action='store_true', help='Validate local export without any network requests')
    parser.add_argument('--allow-empty', action='store_true', help='Allow intentional removal of every managed article')
    args = parser.parse_args()
    local = [export_article(art) for art in articles.collect_article_metadata()]
    if not local and not args.allow_empty:
        raise RuntimeError('No local articles; refusing a mass deletion. Use --allow-empty for intentional removal.')
    if args.export_only:
        print(f'{len(local)} articles exported successfully; no source files modified.')
        return
    api = BloggerAPI(credentials(), CONFIG['blogId'])
    sync(api, local, read_state(), apply=args.apply,
         interval=CONFIG['writeIntervalSeconds'], limit=CONFIG['maxWritesPerRun'])


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, ValueError, KeyError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
