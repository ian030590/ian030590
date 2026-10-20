import assert from 'node:assert/strict';
import worker from '../worker/index.js';

const site = 'https://ian030590.trainerhub.cc';
const apiKey = 're_test_secret_key';
const valid = {
  name: '林治療師',
  role: '職能／物理／語言治療師',
  email: 'name@example.org',
  subject: '開源專案技術交流與代碼貢獻',
  body: '想詢問 trainerhub 的部署方式。\n第二行內容。',
  website: '',
};

let resendCalls = [];
let resendStatus = 200;
globalThis.fetch = async (url, init) => {
  resendCalls.push({ url, headers: init.headers, body: JSON.parse(init.body) });
  return resendStatus === 200
    ? Response.json({ id: 'email-id' })
    : Response.json({ statusCode: resendStatus, message: 'error' }, { status: resendStatus });
};
console.error = () => {};

function env(overrides = {}) {
  return {
    RESEND_API_KEY: apiKey,
    CONTACT_FROM_EMAIL: 'Website Contact <contact@example.com>',
    CONTACT_TO_EMAIL: 'owner@example.com',
    CONTACT_RATE_LIMITER: { limit: async () => ({ success: true }) },
    ASSETS: { fetch: async () => new Response('asset') },
    ...overrides,
  };
}

function post(body, headers = {}) {
  return new Request(`${site}/api/contact`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Origin: site, ...headers },
    body: typeof body === 'string' ? body : JSON.stringify(body),
  });
}

async function send(request, environment = env()) {
  resendCalls = [];
  const response = await worker.fetch(request, environment);
  return { status: response.status, data: await response.json().catch(() => null) };
}

let result = await send(post(valid));
assert.equal(result.status, 200);
assert.deepEqual(result.data, { ok: true });
assert.equal(resendCalls.length, 1);
assert.equal(resendCalls[0].url, 'https://api.resend.com/emails');
assert.equal(resendCalls[0].headers.Authorization, `Bearer ${apiKey}`);
const email = resendCalls[0].body;
assert.equal(email.from, 'Website Contact <contact@example.com>');
assert.equal(email.to, 'owner@example.com');
assert.equal(email.reply_to, valid.email, 'Replies go straight to the visitor');
assert.equal(email.subject, `[網站聯絡] ${valid.subject} - ${valid.name}`);
for (const value of [valid.name, valid.role, valid.email, valid.body]) {
  assert.ok(email.text.includes(value), `Email text must include ${value}`);
}

result = await send(post({ ...valid, name: '林\r\nBcc: x@evil.example', subject: '主旨\n第二行' }));
assert.equal(result.status, 200);
assert.ok(!/[\r\n]/.test(resendCalls[0].body.subject), 'Subject must stay on one line');

result = await send(post({ ...valid, body: '   ' }));
assert.equal(result.status, 400);
assert.equal(resendCalls.length, 0);

for (const address of ['not-an-email', 'a@b.co,c@d.co', 'Name <a@b.co>']) {
  result = await send(post({ ...valid, email: address }));
  assert.equal(result.status, 400, `${address} must be rejected`);
  assert.equal(resendCalls.length, 0);
}

result = await send(post({ ...valid, body: 'x'.repeat(3501) }));
assert.equal(result.status, 400);

result = await send(post('x'.repeat(17 * 1024)));
assert.equal(result.status, 413);

result = await send(post('{not json'));
assert.equal(result.status, 400);

result = await send(post(valid, { Origin: 'https://evil.example' }));
assert.equal(result.status, 403);
assert.equal(resendCalls.length, 0);

result = await send(post(valid, { 'Content-Type': 'text/plain' }));
assert.equal(result.status, 415);

result = await send(post({ ...valid, website: 'https://spam.example' }));
assert.equal(result.status, 200, 'Spam trap answers like a success');
assert.equal(resendCalls.length, 0, 'Spam trap must not send email');

result = await send(post(valid), env({ CONTACT_RATE_LIMITER: { limit: async () => ({ success: false }) } }));
assert.equal(result.status, 429);
assert.equal(resendCalls.length, 0);

for (const missing of ['RESEND_API_KEY', 'CONTACT_FROM_EMAIL', 'CONTACT_TO_EMAIL']) {
  result = await send(post(valid), env({ [missing]: undefined }));
  assert.equal(result.status, 503, `Missing ${missing} must not send`);
  assert.equal(resendCalls.length, 0);
}

resendStatus = 422;
result = await send(post(valid));
assert.equal(result.status, 502);
assert.ok(!JSON.stringify(result.data).includes(apiKey), 'Errors must not leak the API key');
resendStatus = 200;

result = await send(new Request(`${site}/api/contact`));
assert.equal(result.status, 405);

result = await send(new Request(`${site}/api/other`));
assert.equal(result.status, 404);

const page = await worker.fetch(new Request(`${site}/contact`), env());
assert.equal(await page.text(), 'asset', 'Non-API paths fall through to static assets');

console.log('Contact worker checks passed: Resend email, validation, origin, spam trap, rate limit and secret handling.');
