import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blogger_sync as sync


def article(source='VisualRehab_001', digest='current'):
    marker = {'repository': sync.CONFIG['repository'], 'source': source,
              'sha256': digest, 'labels': ['視覺復健']}
    return {'source': source, 'marker': marker,
            'body': {'title': '文章', 'labels': ['視覺復健'], 'published': '2026-10-27T08:00:00+08:00',
                     'content': '<div data-ian-blogger-sync=\'' + json.dumps(marker) + '\'>正文</div>'}}


def remote(item, post_id='123', **overrides):
    return {'id': post_id, 'status': 'LIVE', **copy.deepcopy(item['body']), **overrides}


class FakeAPI:
    def __init__(self, posts=(), failure=None):
        self.records = list(posts)
        self.calls = []
        self.failure = failure
        self.reads = 0

    def posts(self):
        self.reads += 1
        return self.records

    def call(self, method='GET', post_id='', body=None, **query):
        self.calls.append((method, post_id, body, query))
        if self.failure:
            raise self.failure


class BloggerSyncTests(unittest.TestCase):
    def test_list_omits_empty_page_token_and_reads_all_pages(self):
        api = sync.BloggerAPI({'client_id': 'id', 'client_secret': 'secret', 'refresh_token': 'refresh'}, '123')
        with patch.object(api, 'call', side_effect=[{'items': [{'id': '1'}], 'nextPageToken': 'next'},
                                                   {'items': [{'id': '2'}]}]) as call, patch.object(sync.time, 'sleep'):
            self.assertEqual([post['id'] for post in api.posts()], ['1', '2'])
        self.assertNotIn('pageToken', call.call_args_list[0].kwargs)
        self.assertEqual(call.call_args_list[1].kwargs['pageToken'], 'next')

    def test_plan_preserves_unmanaged_posts_and_native_labels(self):
        changed = article(digest='changed')
        old = remote(article(), labels=['視覺復健', 'Blogger自訂標籤'])
        removed = remote(article('VisualRehab_002'), '456')
        unmanaged = {'id': '999', 'content': '<p>手動發布</p>'}
        plan = sync.plan_sync([changed, article('VisualRehab_003')], [old, removed, unmanaged])
        self.assertEqual([op[0] for op in plan], ['delete', 'update', 'insert'])
        self.assertEqual(plan[0][2], '456')
        self.assertEqual(set(plan[1][3]['labels']), {'視覺復健', 'Blogger自訂標籤'})

    def test_unchanged_sources_leave_blogger_edits_untouched(self):
        item = article()
        post = remote(item, title='Blogger修改標題', labels=['原生標籤'])
        self.assertEqual(sync.plan_sync([item], [post]), [])

    def test_duplicate_sources_abort_before_writes(self):
        with self.assertRaisesRegex(RuntimeError, 'Duplicate Blogger'):
            sync.plan_sync([article()], [remote(article()), remote(article(), '456')])
        with self.assertRaisesRegex(RuntimeError, 'Duplicate local'):
            sync.plan_sync([article(), article()], [])

    def test_marker_recovers_a_write_whose_response_was_lost(self):
        item = article()
        api, state = FakeAPI(), {}

        def committed_then_disconnected(*args, **kwargs):
            api.records.append(remote(item))
            raise RuntimeError('Response lost after creation')

        with patch.object(api, 'call', side_effect=committed_then_disconnected) as write:
            with self.assertRaisesRegex(RuntimeError, 'Response lost'):
                sync.sync(api, [item], state, apply=True, sleep=lambda _: None,
                          persist=lambda _: None)
            self.assertEqual(write.call_count, 1)
            pending = sync.sync(api, [item], state, apply=True, sleep=lambda _: None,
                                persist=lambda _: None)
            self.assertEqual(pending, 0)
            self.assertEqual(write.call_count, 1, 'Resuming must not create a duplicate after a lost response')

    def test_batch_limit_and_spacing_include_first_write(self):
        api, waits, saves = FakeAPI(), [], []
        local = [article(f'VisualRehab_{i:03d}') for i in range(1, 8)]
        pending = sync.sync(api, local, {}, apply=True, sleep=waits.append,
                            now=lambda: 1000, persist=lambda state: saves.append(dict(state)))
        self.assertEqual(pending, 2)
        self.assertEqual(len(api.calls), 5)
        self.assertEqual(waits, [120] * 5)
        self.assertEqual(len(saves), 10)
        self.assertTrue(all(call[0] == 'POST' for call in api.calls))

    def test_dry_run_and_deletion_to_trash(self):
        api = FakeAPI([remote(article())])
        self.assertEqual(sync.sync(api, [], {}), 1)
        self.assertEqual(api.calls, [])
        sync.sync(api, [], {}, apply=True, sleep=lambda _: None, persist=lambda _: None)
        self.assertEqual(api.calls[0][0], 'DELETE')
        self.assertEqual(api.calls[0][3], {'useTrash': 'true'})

    def test_limits_stop_immediately_and_persist_cooldown(self):
        for status in (403, 429):
            with self.subTest(status=status):
                api, state = FakeAPI(failure=sync.APIError(status, 90000)), {}
                with self.assertRaises(sync.APIError):
                    sync.sync(api, [article()], state, apply=True, now=lambda: 1000,
                              sleep=lambda _: None, persist=lambda _: None)
                self.assertEqual(len(api.calls), 1)
                self.assertEqual(state['cooldown_until'], 91000)
                with self.assertRaisesRegex(RuntimeError, 'cooldown'):
                    sync.sync(api, [article()], state, now=lambda: 1001)
                self.assertEqual(api.reads, 1)

    def test_export_preserves_source_bytes_dates_references_and_absolute_links(self):
        with tempfile.TemporaryDirectory(prefix='blogger-export-') as directory:
            root = Path(directory)
            path = root / 'VisualRehab' / '001_article.html'
            path.parent.mkdir()
            raw = '''<h1>文章標題</h1><article class="article-container"><h1>文章標題</h1><span class="material-symbols-outlined">person</span>
            <figure><img src="/assets/image.jpg"></figure><p id="section">內文</p>
            <a href="#section">跳轉</a><section class="article-references"><a href="https://doi.org/10.1/test">引用</a></section>
            <nav class="prev-next-nav"><a href="/blog">導覽</a></nav></article>'''.encode()
            path.write_bytes(raw)
            art = {'folder': 'VisualRehab', 'order': 1, 'old_filename': path.name,
                   'new_filename': path.name, 'tags': ['視覺復健'], 'date_published': '2026-10-27T08:00:00+08:00'}
            with patch.object(sync.articles, 'CONTENT_DIR', root):
                item = sync.export_article(art)
            self.assertEqual(path.read_bytes(), raw)
            self.assertEqual(item['body']['published'], art['date_published'])
            self.assertIn('https://ian030590.trainerhub.cc/assets/image.jpg', item['body']['content'])
            self.assertIn('article-references', item['body']['content'])
            self.assertNotIn('material-symbols-outlined', item['body']['content'])
            self.assertEqual(sync.managed_posts([remote(item)])['VisualRehab_001'][1], item['marker'])

    def test_checkpoint_is_replaced_atomically(self):
        with tempfile.TemporaryDirectory(prefix='blogger-state-') as directory:
            path = Path(directory) / 'state.json'
            sync.save_state({'last_write': 100}, path)
            self.assertEqual(sync.read_state(path), {'last_write': 100})
            self.assertFalse(path.with_suffix('.tmp').exists())


if __name__ == '__main__':
    unittest.main()
