const ALLOWED_ORIGINS = [
  'https://aiasset.market',
  'https://www.aiasset.market',
  'http://localhost:8788',
  'http://localhost:8888',
];

// Allow CF Pages preview deployments (each deploy gets a unique hash subdomain)
function isAllowedOrigin(origin) {
  if (isAllowedOrigin(origin)) return true;
  if (/^https:\/\/[a-f0-9]+\.aiasset-market\.pages\.dev$/.test(origin)) return true;
  return false;
}

// in-memory fallback for local dev (CF Workers isolates don't share memory)
const ipLog = {};
const RATE_LIMIT = 5;
const RATE_WINDOW_MS = 60 * 60 * 1000;

const MAX_FIELD_LEN = 2000;

// 2.6: strict sheet allowlist — reject unknown sheet values
const ALLOWED_SHEETS = ['Assets', 'Bounties', 'Watchlist'];

const REQUIRED = {
  Assets:    ['asset_name', 'category', 'description', 'contact'],
  Bounties:  ['type', 'description', 'contact'],
  Watchlist: ['contact', 'role'],
};

// 2.7: per-form field allowlist — only pass known fields to Apps Script
const ALLOWED_FIELDS = {
  Assets:    ['asset_name', 'category', 'description', 'contact', 'submitted_at'],
  Bounties:  ['type', 'description', 'contact', 'submitted_at'],
  Watchlist: ['contact', 'role', 'interest_note', 'submitted_at'],
};

// Sanitize field values to prevent Google Sheets formula injection.
// Fields starting with =, +, -, @ are prefixed with a tab so Sheets treats them as text.
function sanitizeForSheets(obj) {
  const out = {};
  for (const [k, v] of Object.entries(obj)) {
    if (typeof v === 'string' && /^[=+\-@\t\r]/.test(v)) {
      out[k] = '\t' + v;
    } else {
      out[k] = v;
    }
  }
  return out;
}

// Escape HTML special chars for Telegram HTML parse_mode
function escapeHtml(str) {
  return String(str ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

async function rateCheckKV(ip, kv) {
  const key = `rl:submit:${ip}`;
  const raw = await kv.get(key);
  const now = Date.now();
  if (!raw) {
    await kv.put(key, JSON.stringify({ count: 1, resetAt: now + RATE_WINDOW_MS }), { expirationTtl: 3600 });
    return true;
  }
  const rec = JSON.parse(raw);
  if (now > rec.resetAt) {
    await kv.put(key, JSON.stringify({ count: 1, resetAt: now + RATE_WINDOW_MS }), { expirationTtl: 3600 });
    return true;
  }
  if (rec.count >= RATE_LIMIT) return false;
  await kv.put(key, JSON.stringify({ count: rec.count + 1, resetAt: rec.resetAt }), { expirationTtl: 3600 });
  return true;
}

function rateCheckMemory(ip) {
  const now = Date.now();
  if (!ipLog[ip] || now > ipLog[ip].resetAt) {
    ipLog[ip] = { count: 1, resetAt: now + RATE_WINDOW_MS };
    return true;
  }
  ipLog[ip].count++;
  return ipLog[ip].count <= RATE_LIMIT;
}

async function rateCheck(ip, kv) {
  if (kv) return rateCheckKV(ip, kv);
  return rateCheckMemory(ip);
}

// Turnstile verification (set TURNSTILE_SECRET in CF dashboard to enforce)
async function verifyTurnstile(token, ip, secret) {
  if (!secret) return true;
  if (!token) return false;
  try {
    const res = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ secret, response: token, remoteip: ip }),
    });
    const data = await res.json().catch(() => ({}));
    return data.success === true;
  } catch {
    return false;
  }
}

// 3.9: Security headers on all Pages Function responses
function securityHeaders() {
  return {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
  };
}

function corsHeaders(origin) {
  return {
    ...securityHeaders(),
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Vary': 'Origin',
    'Content-Type': 'application/json',
  };
}

function json(body, status, origin) {
  return new Response(JSON.stringify(body), {
    status,
    headers: corsHeaders(origin),
  });
}

export async function onRequest(context) {
  const { request, env } = context;
  const origin = request.headers.get('origin') || '';
  const method = request.method;

  try {
  if (method === 'OPTIONS') {
    if (!isAllowedOrigin(origin)) return new Response('', { status: 403 });
    return new Response('', { status: 204, headers: corsHeaders(origin) });
  }

  if (method !== 'POST') {
    return new Response('Method Not Allowed', { status: 405 });
  }

  if (!isAllowedOrigin(origin)) {
    return new Response(JSON.stringify({ error: 'Forbidden' }), {
      status: 403,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const ip = (
    request.headers.get('cf-connecting-ip') ||
    request.headers.get('x-forwarded-for') ||
    ''
  ).split(',')[0].trim() || 'unknown';

  if (!await rateCheck(ip, env.RATE_KV)) {
    return json({ error: 'Too many submissions. Please wait.' }, 429, origin);
  }

  let payload;
  try {
    payload = await request.json();
  } catch {
    return json({ error: 'Invalid request' }, 400, origin);
  }

  if (!await verifyTurnstile(payload['cf-turnstile-response'] || '', ip, env.TURNSTILE_SECRET)) {
    return json({ error: 'Human verification failed. Please try again.' }, 403, origin);
  }

  if (payload.hp_website) {
    return json({ ok: true }, 200, origin);
  }

  if (payload._form_loaded) {
    const loaded = new Date(payload._form_loaded).getTime();
    if (!isNaN(loaded) && Date.now() - loaded < 3000) {
      return json({ ok: true }, 200, origin);
    }
  }

  for (const [k, v] of Object.entries(payload)) {
    if (typeof v === 'string' && v.length > MAX_FIELD_LEN) {
      return json({ error: `Field too long: ${k}` }, 400, origin);
    }
  }

  const sheet = payload.sheet;

  // 2.6: reject unknown sheet values
  if (!ALLOWED_SHEETS.includes(sheet)) {
    return json({ error: 'Invalid form type.' }, 400, origin);
  }

  // 2.8: type-safe required field check (coerce to string before .trim())
  const required = REQUIRED[sheet];
  const missing = required.filter(f => !String(payload[f] ?? '').trim());
  if (missing.length) {
    return json({ error: `Missing: ${missing.join(', ')}` }, 400, origin);
  }

  // 2.7: filter to allowed fields only before forwarding
  const allowedFields = ALLOWED_FIELDS[sheet];
  const filteredPayload = {};
  for (const f of allowedFields) {
    if (payload[f] !== undefined) filteredPayload[f] = payload[f];
  }

  const TG_TOKEN = env.TELEGRAM_BOT_TOKEN;
  const TG_CHAT = env.TELEGRAM_CHAT_ID || '@Pirate_AI';

  // 2.9: use context.waitUntil() so the Telegram fetch survives after response is sent
  if (TG_TOKEN) {
    let msg = '';
    if (sheet === 'Watchlist') {
      msg = `📋 <b>New Watchlist signup</b>\nContact: ${escapeHtml(filteredPayload.contact)}\nRole: ${escapeHtml(filteredPayload.role)}\nTime: ${escapeHtml(filteredPayload.submitted_at)}`;
    } else if (sheet === 'Assets') {
      msg = `🛍 <b>New Asset submission</b>\nName: ${escapeHtml(filteredPayload.asset_name)}\nCategory: ${escapeHtml(filteredPayload.category)}\nContact: ${escapeHtml(filteredPayload.contact)}\nTime: ${escapeHtml(filteredPayload.submitted_at)}`;
    } else if (sheet === 'Bounties') {
      msg = `🎯 <b>New Buy request</b>\nType: ${escapeHtml(filteredPayload.type)}\nContact: ${escapeHtml(filteredPayload.contact)}\nTime: ${escapeHtml(filteredPayload.submitted_at)}`;
    }
    if (msg) {
      const tgFetch = fetch(`https://api.telegram.org/bot${TG_TOKEN}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: TG_CHAT, text: msg, parse_mode: 'HTML' }),
      }).catch(() => {});
      context.waitUntil(tgFetch);
    }
  }

  const APPS_URL = env.APPS_SCRIPT_URL;
  if (!APPS_URL) {
    console.error('APPS_SCRIPT_URL env var not set');
    return json({ error: 'Server error' }, 500, origin);
  }

  // Sanitize before writing to Google Sheets to prevent formula injection
  const safePayload = sanitizeForSheets(filteredPayload);

  // 2.5: check Apps Script response and surface errors to client
  // Contract: POST {sheet, data: {...fields}} — GAS reads payload.data
  let appsRes;
  try {
    appsRes = await fetch(APPS_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain' },
      body: JSON.stringify({ sheet, data: safePayload }),
    });
  } catch (err) {
    console.error('Apps Script forward error:', err.message);
    return json({ error: 'Could not save submission. Please try again.' }, 502, origin);
  }

  if (!appsRes.ok) {
    console.error('Apps Script returned status:', appsRes.status);
    return json({ error: 'Could not save submission. Please try again.' }, 502, origin);
  }

  let parsedBody;
  try {
    parsedBody = await appsRes.json();
  } catch {
    console.error('Apps Script response not JSON');
    return json({ error: 'Could not save submission. Please try again.' }, 502, origin);
  }

  if (!parsedBody.ok) {
    console.error('Apps Script returned error:', parsedBody.error);
    return json({ error: 'Could not save submission. Please try again.' }, 502, origin);
  }

  return json({ ok: true }, 200, origin);
  } catch (err) {
    console.error('Unhandled submit error:', err.message);
    return new Response(JSON.stringify({ error: 'Server error. Please try again.' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': origin || '*' },
    });
  }
}
