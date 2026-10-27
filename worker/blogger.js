import config from '../blogger.config.json' with { type: 'json' };

export async function handleBlogger(request, env, ctx) {
  if (request.method !== 'GET') {
    return new Response(null, { status: 405, headers: { Allow: 'GET' } });
  }
  if (!env.BLOGGER_API_KEY) {
    return Response.json({ error: '文章暫時無法更新。' }, { status: 503 });
  }
  const cache = globalThis.caches?.default;
  // Ignore visitor query parameters: everyone shares the same public article catalog.
  const key = new Request(new URL('/api/articles', request.url));
  const cached = await cache?.match(key);
  if (cached) return cached;

  try {
    const items = [];
    let pageToken = '';
    const seen = new Set();
    do {
      const url = new URL(`https://www.googleapis.com/blogger/v3/blogs/${config.blogId}/posts`);
      url.search = new URLSearchParams({
        maxResults: '100', fetchBodies: 'true', fetchImages: 'true',
        view: 'READER', orderBy: 'published',
        fields: 'nextPageToken,items(id,title,content,url,labels,published,updated,images)',
      }).toString();
      if (pageToken) url.searchParams.set('pageToken', pageToken);
      const response = await fetch(url, {
        headers: { 'X-Goog-Api-Key': env.BLOGGER_API_KEY },
        signal: AbortSignal.timeout(15000),
      });
      if (!response.ok) throw new Error(`Blogger HTTP ${response.status}`);
      const page = await response.json();
      if (page.items !== undefined && !Array.isArray(page.items)) throw new Error('Invalid Blogger catalog');
      items.push(...(page.items || []));
      pageToken = page.nextPageToken || '';
      if (pageToken && seen.has(pageToken)) throw new Error('Repeated Blogger page token');
      seen.add(pageToken);
    } while (pageToken);

    const response = Response.json({ items }, {
      headers: { 'Cache-Control': 'public, max-age=300', 'X-Content-Type-Options': 'nosniff' },
    });
    if (cache && ctx) ctx.waitUntil(cache.put(key, response.clone()));
    return response;
  } catch {
    return Response.json({ error: '文章暫時無法更新，請稍後再試。' }, {
      status: 502, headers: { 'Cache-Control': 'no-store' },
    });
  }
}
