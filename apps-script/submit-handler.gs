/**
 * AIAsset.Market — Google Apps Script form handler
 *
 * Deploy: Extensions → Apps Script → Deploy → New deployment → Web App
 *   Execute as: Me
 *   Who has access: Anyone
 *
 * After deploy, copy the Web App URL into the Cloudflare Worker environment
 * variable APPS_SCRIPT_URL (set via wrangler secret or CF dashboard).
 *
 * Secrets — set in Script Properties (Project Settings → Script properties):
 *   TG_BOT_TOKEN  — Telegram bot token
 *   TG_CHAT_ID    — Telegram chat/channel ID for notifications
 *
 * DO NOT hardcode tokens in this file.
 */

const ALLOWED_SHEETS = ['Assets', 'Bounties', 'Watchlist'];

const ALLOWED_FIELDS = {
  Assets:    ['asset_name', 'category', 'description', 'contact'],
  Bounties:  ['type', 'description', 'contact'],
  Watchlist: ['contact', 'role', 'interest_note'],
};

function doPost(e) {
  try {
    const payload = JSON.parse(e.postData.contents);
    const sheet   = payload.sheet;
    const data    = payload.data || {};

    if (!ALLOWED_SHEETS.includes(sheet)) {
      return jsonResponse({ ok: false, error: 'Unknown sheet' });
    }

    const ss    = SpreadsheetApp.getActiveSpreadsheet();
    const tab   = ss.getSheetByName(sheet) || ss.insertSheet(sheet);
    const fields = ALLOWED_FIELDS[sheet];

    // Build row: timestamp + allowed fields only
    const row = [new Date().toISOString()].concat(
      fields.map(f => String(data[f] ?? '').trim().substring(0, 2000))
    );

    // Guard against formula injection
    const safeRow = row.map(v =>
      typeof v === 'string' && /^[=+\-@]/.test(v) ? "'" + v : v
    );

    tab.appendRow(safeRow);

    // Telegram notification (best-effort, does not block response)
    sendTelegram(sheet, data, fields);

    return jsonResponse({ ok: true });

  } catch (err) {
    console.error('submit-handler error:', err);
    return jsonResponse({ ok: false, error: 'Internal error' });
  }
}

function sendTelegram(sheet, data, fields) {
  const props    = PropertiesService.getScriptProperties();
  const botToken = props.getProperty('TG_BOT_TOKEN');
  const chatId   = props.getProperty('TG_CHAT_ID');
  if (!botToken || !chatId) return;

  const lines = [`📋 *New ${escTg(sheet)} submission*`].concat(
    fields.map(f => `*${escTg(f)}:* ${escTg(String(data[f] ?? ''))}`)
  );

  const url  = `https://api.telegram.org/bot${botToken}/sendMessage`;
  const body = JSON.stringify({
    chat_id:    chatId,
    text:       lines.join('\n'),
    parse_mode: 'Markdown',
  });

  UrlFetchApp.fetch(url, {
    method:      'post',
    contentType: 'application/json',
    payload:     body,
    muteHttpExceptions: true,
  });
}

function escTg(s) {
  return String(s).replace(/[_*[\]()~`>#+=|{}.!\\-]/g, '\\$&');
}

function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
