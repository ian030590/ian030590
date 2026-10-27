import DOMPurify from 'dompurify';

export async function loadBloggerArticle() {
  const reader = document.getElementById('blogger-reader')!;
  const title = document.getElementById('reader-title')!;
  const status = document.getElementById('reader-status')!;
  const body = document.getElementById('reader-body')!;
  const tags = document.getElementById('reader-tags')!;
  const date = document.getElementById('reader-date') as HTMLTimeElement;
  try {
    const id = new URLSearchParams(location.search).get('id');
    if (!id || !/^\d+$/.test(id)) throw new Error('missing');
    const response = await fetch('/api/articles');
    if (!response.ok) throw new Error('unavailable');
    const { items } = await response.json();
    if (!Array.isArray(items)) throw new Error('unavailable');
    const post = items.find((item) => item.id === id);
    if (!post) throw new Error('missing');

    const clean = DOMPurify.sanitize(post.content || '', {
      USE_PROFILES: { html: true },
      ADD_ATTR: ['target'],
      FORBID_TAGS: ['style', 'iframe', 'form', 'input', 'button', 'object', 'embed', 'link', 'meta', 'base'],
      FORBID_ATTR: ['style', 'srcdoc', 'srcset'],
      SANITIZE_NAMED_PROPS: true,
    });
    const doc = new DOMParser().parseFromString(clean, 'text/html');
    const container = doc.querySelector('.ian-blogger-article .article-container') || doc.body;
    container.querySelectorAll('.article-detail-header, .material-symbols-outlined').forEach((node) => node.remove());
    body.append(...Array.from(container.childNodes));
    body.querySelectorAll<HTMLAnchorElement>('a[target]').forEach((link) => {
      link.relList.add('noopener', 'noreferrer');
    });
    body.querySelectorAll<HTMLAnchorElement>('a[href^="#"]').forEach((link) => {
      link.setAttribute('href', '#user-content-' + link.getAttribute('href')!.slice(1));
    });
    title.textContent = post.title || '文章';
    document.title = `${post.title || '文章'} | 蔡泓恩 | 職能治療師`;
    date.dateTime = post.published || '';
    date.textContent = String(post.published || '').slice(0, 10);
    for (const label of post.labels || []) {
      const link = document.createElement('a');
      link.className = 'article-badge';
      link.href = '/blog?tag=' + encodeURIComponent(label);
      link.textContent = label;
      tags.append(link);
    }
    status.hidden = true;
  } catch (error) {
    title.textContent = error instanceof Error && error.message === 'missing' ? '找不到這篇文章' : '暫時無法載入文章';
    status.textContent = '請稍後重新整理，或返回文章列表選擇其他文章。';
  } finally {
    reader.setAttribute('aria-busy', 'false');
  }
}
