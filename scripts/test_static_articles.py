import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import quote

from bs4 import BeautifulSoup

import build_static_articles as build


def article(order, folder='VisualRehab', cluster='series'):
    return {
        'folder': folder,
        'cluster': cluster,
        'order': order,
        'new_filename': f'{order:03d}_視覺復健_測試.html',
        'title': f'文章 {order}：A & B < C',
    }


class NavigationTests(unittest.TestCase):
    def setUp(self):
        self.first, self.middle, self.last = [article(n) for n in (2, 7, 12)]
        self.articles = [self.last, article(8, cluster='other'), self.first,
                         article(6, folder='MotorRehab'), self.middle]

    def navigation(self, current):
        return BeautifulSoup(build.render_prev_next_navigation(current, self.articles), 'html.parser').nav

    def test_neighbors_use_series_order_and_skip_number_gaps(self):
        links = self.navigation(self.middle).select('a')
        self.assertEqual([link['rel'] for link in links], [['prev'], ['next']])
        self.assertEqual([link['href'] for link in links], [
            f"/content/VisualRehab/{quote(art['new_filename'])}" for art in (self.first, self.last)
        ])
        self.assertEqual([link.select_one('.prev-next-title').get_text() for link in links],
                         [self.first['title'], self.last['title']])

    def test_series_boundaries_keep_both_slots_without_dead_links(self):
        for current, disabled_direction, enabled_direction in (
            (self.first, 'prev', 'next'), (self.last, 'next', 'prev')
        ):
            with self.subTest(direction=disabled_direction):
                nav = self.navigation(current)
                self.assertEqual(len(nav.select('.prev-next-card')), 2)
                disabled = nav.select_one(f'.prev-next-card--{disabled_direction}')
                self.assertEqual(disabled.name, 'div')
                self.assertEqual(disabled['aria-disabled'], 'true')
                self.assertNotIn('href', disabled.attrs)
                self.assertEqual(nav.select_one('a')['rel'], [enabled_direction])

    def test_single_article_series_has_two_disabled_cards(self):
        nav = self.navigation(self.articles[1])
        self.assertEqual(len(nav.select('[aria-disabled="true"]')), 2)
        self.assertFalse(nav.select('a'))

    def test_legacy_div_and_duplicate_navigation_are_replaced_idempotently(self):
        soup = BeautifulSoup('<div class="article-container"><p>保留正文</p>'
                             '<div class="prev-next-nav"><div>old card</div></div>'
                             '<nav class="prev-next-nav"><a href="#">duplicate</a></nav></div>',
                             'html.parser')
        build.sync_article_source(soup, self.middle, self.articles)
        build.validate_article_navigation(soup, self.middle, self.articles)
        self.assertEqual(soup.p.get_text(), '保留正文')
        once = str(soup)
        build.sync_article_source(soup, self.middle, self.articles)
        self.assertEqual(str(soup), once)

    def test_missing_navigation_is_inserted_before_bottom_actions(self):
        for container in ('div', 'article'):
            with self.subTest(container=container):
                soup = BeautifulSoup(f'<{container} class="article-container"><p>正文</p>'
                                     f'<div class="article-bottom-actions"></div></{container}>', 'html.parser')
                build.sync_article_source(soup, self.middle, self.articles)
                build.validate_article_navigation(soup, self.middle, self.articles)
                self.assertEqual(soup.select_one('.article-bottom-actions').previous_sibling.name, 'nav')

    def test_new_page_and_existing_page_use_identical_navigation(self):
        current = dict(self.middle, cat_name='視覺復健', summary='測試摘要', tags=['視覺復健'],
                       citations=[], img_src='', caption='', read_time='約 1 分鐘閱讀',
                       raw_body='<p>正文</p>', date_published='2026-10-15T08:00:00+08:00',
                       date_modified='2026-10-15T08:00:00+08:00')
        soup = BeautifulSoup(build.build_article_html(current, self.articles), 'html.parser')
        build.validate_article_navigation(soup, current, self.articles)
        before = str(soup.select_one('.prev-next-nav'))
        build.sync_article_source(soup, current, self.articles)
        self.assertEqual(str(soup.select_one('.prev-next-nav')), before)

    def test_validator_rejects_wrong_target_title_direction_or_duplicate(self):
        for mutation in ('href', 'title', 'direction', 'duplicate'):
            with self.subTest(mutation=mutation):
                nav = self.navigation(self.middle)
                soup = BeautifulSoup(str(nav), 'html.parser')
                if mutation == 'href':
                    soup.a['href'] = '/blog'
                elif mutation == 'title':
                    soup.select_one('.prev-next-title').string = 'wrong title'
                elif mutation == 'direction':
                    soup.a['rel'] = ['next']
                else:
                    soup.append(BeautifulSoup(str(nav), 'html.parser').nav)
                with self.assertRaisesRegex(RuntimeError, 'Inconsistent series navigation'):
                    build.validate_article_navigation(soup, self.middle, self.articles)


class InternalLinkTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='article-link-tests-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.patch = patch.object(build, 'BASE_DIR', self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.source = self.root / 'content' / 'VisualRehab' / '001_source.html'
        self.source.parent.mkdir(parents=True)
        self.source.write_text('<h1 id="intro">Intro</h1>', encoding='utf-8')
        self.target = self.source.with_name('007_視覺復健.html')
        self.target.write_text('<h1 id="重點">Title</h1><a name="legacy"></a>', encoding='utf-8')
        (self.root / 'blog.html').write_text('<h1 id="articles">Articles</h1>', encoding='utf-8')
        (self.root / 'index.html').write_text('<h1>Home</h1>', encoding='utf-8')

    def test_relative_root_absolute_and_encoded_links_resolve(self):
        for href in (self.target.name, './' + self.target.name,
                     '../../content/VisualRehab/' + self.target.name,
                     '/content/VisualRehab/' + quote(self.target.name),
                     build.SITE_BASE_URL + '/content/VisualRehab/' + quote(self.target.name),
                     '//ian030590.trainerhub.cc/content/VisualRehab/' + quote(self.target.name)):
            with self.subTest(href=href):
                self.assertEqual(build.validate_internal_link(self.source, href, {}), self.target)

    def test_clean_routes_queries_and_fragments(self):
        for href, target in (('/', self.root / 'index.html'),
                             ('/blog?tag=視覺復健#articles', self.root / 'blog.html'),
                             ('#intro', self.source),
                             (self.target.name + '#' + quote('重點'), self.target),
                             (self.target.name + '#legacy', self.target)):
            with self.subTest(href=href):
                self.assertEqual(build.validate_internal_link(self.source, href, {}), target)

    def test_missing_files_and_fragments_are_rejected(self):
        for href in ('missing.html', '../missing.html', '/missing',
                     build.SITE_BASE_URL + '/missing.html', '#missing',
                     self.target.name + '#missing'):
            with self.subTest(href=href):
                with self.assertRaisesRegex(RuntimeError, 'Broken internal'):
                    build.validate_internal_link(self.source, href, {})

    def test_external_mail_and_phone_links_are_skipped(self):
        for href in ('https://example.com/missing', '//example.com/missing',
                     'mailto:test@example.com', 'tel:+88612345678'):
            with self.subTest(href=href):
                self.assertIsNone(build.validate_internal_link(self.source, href, {}))


class AstroAssetsTests(unittest.TestCase):
    def test_staging_preserves_article_bytes_and_excludes_private_sources(self):
        with tempfile.TemporaryDirectory(prefix='astro-assets-tests-') as temporary:
            root = Path(temporary)
            for directory in ('assets', 'css', 'icons', 'js'):
                (root / directory).mkdir()
                (root / directory / 'asset.txt').write_text('public asset', encoding='utf-8')
            for filename in ('favicon.ico', 'robots.txt', 'llms.txt', '_headers', '_redirects'):
                (root / filename).write_text('public asset', encoding='utf-8')
            (root / 'js' / 'articles-data.js').write_text('stale catalog', encoding='utf-8')
            references = root / 'content' / 'References'
            references.mkdir(parents=True)
            (references / 'private.pdf').write_bytes(b'private reference')
            source = root / 'content' / 'VisualRehab' / '001_article.html'
            source.parent.mkdir()
            original = '<!doctype html>\r\n<p>保留原始文章 &amp; 日期</p>\r\n'.encode('utf-8')
            source.write_bytes(original)
            current = dict(article(1), old_filename=source.name, new_filename=source.name,
                           summary='摘要', img_src='', tags=['視覺復健'], read_time='約 1 分鐘閱讀',
                           date_published='2026-10-15T08:00:00+08:00',
                           date_modified='2026-10-15T08:00:00+08:00', cat_name='視覺復健', sub_cluster='測試')
            with patch.object(build, 'BASE_DIR', root):
                build.prepare_astro_assets([current])
                public = root / '.generated' / 'public'
                stale = public / 'stale.html'
                stale.write_text('must disappear on the next build', encoding='utf-8')
                build.prepare_astro_assets([current])
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual((public / source.relative_to(root)).read_bytes(), original)
            self.assertFalse((public / 'content' / 'References').exists())
            self.assertFalse(stale.exists())
            self.assertIn('window.__STATIC_ARTICLES__', (public / 'js' / 'articles-data.js').read_text(encoding='utf-8'))
            for filename in ('sitemap.xml', 'rss.xml', '_headers', '_redirects'):
                self.assertTrue((public / filename).is_file())

    def test_conflict_files_fail_without_deleting_or_renaming_sources(self):
        with tempfile.TemporaryDirectory(prefix='astro-conflict-tests-') as temporary:
            root = Path(temporary)
            folder = next(iter(build.ADDITIONAL_CONTENT_FOLDERS))
            target = root / folder / '001_article[conflicted].html'
            target.parent.mkdir()
            target.write_text('keep me', encoding='utf-8')
            with patch.object(build, 'CONTENT_DIR', root):
                with self.assertRaisesRegex(RuntimeError, 'manual resolution'):
                    build.collect_article_metadata()
            self.assertEqual(target.read_text(encoding='utf-8'), 'keep me')


if __name__ == '__main__':
    unittest.main()
