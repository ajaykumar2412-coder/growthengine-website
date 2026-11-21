/**
 * growthengine.club bootcamp pages → A2 funnel lead tabs (+ Razorpay for the ₹99 page).
 *
 * Each page sends a funnel_id. The lead is written to that funnel's "Lead Tab" (Funnels tab),
 * so the A2 automation (Automation.gs) sends that funnel's WhatsApp/Email sequence.
 *   Free page  /aravind-india/     funnel ARVIND01 → POST            → row saved
 *   ₹99 page   /aravind-india-99/  funnel ARVIND99 → GET action=order  → row saved as Pending + Razorpay order
 *                                                  GET action=verify → signature checked, row marked Paid
 *
 * Razorpay keys live in Project Settings → Script properties (never in this code):
 *   RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
 */
var DEFAULT_FUNNEL = { free: 'ARVIND01', paid: 'ARVIND99' };
var FALLBACK_TAB = 'Registrations';
var PRICE_PAISE = 9900;            // ₹99. Fixed here so nobody can change the price from the browser.

// Columns we write. The first name is used when creating a column; any alias already in the tab is reused,
// so A2's own names (Registered At, Phone, Payment Status, Paid At) and older ones (Timestamp, WhatsApp) both work.
var FIELDS = [
  ['ts',        ['Registered At', 'Timestamp']],
  ['name',      ['Name']],
  ['phone',     ['Phone', 'WhatsApp']],
  ['email',     ['Email']],
  ['reason',    ['Why join']],
  ['serious',   ['How serious']],
  ['profession',['Profession']],
  ['utm_source',['UTM source']], ['utm_medium',['UTM medium']], ['utm_campaign',['UTM campaign']], ['utm_content',['UTM content']],
  ['page',      ['Page URL']],
  ['plan',      ['Plan']],
  ['status',    ['Payment Status']],
  ['lead',      ['Lead ID']],
  ['order',     ['Razorpay Order']],
  ['payment',   ['Razorpay Payment']],
  ['paid_at',   ['Paid At']]
];
var PAID_ONLY = ['status', 'lead', 'order', 'payment', 'paid_at'];

/* ---------- free page ---------- */
function doPost(e) {
  var r = routeToAutomation_(e); if (r) return r; // WhatsApp & Email automation (Automation.gs)
  var res = locked_(function () {
    var d = JSON.parse((e.postData && e.postData.contents) || '{}');
    d.plan = d.plan || 'Free';
    addRow_(d.funnel_id || DEFAULT_FUNNEL.free, d, {});
    return { ok: true };
  });
  if (res.ok) kickAutomation_();       // send the confirmation right away
  return json_(res);
}

/* ---------- ₹99 page + health check ---------- */
function doGet(e) {
  var p = (e && e.parameter) || {};
  if (p.unsub || p['hub.mode']) return automationDoGet(e); // WhatsApp & Email automation
  if (p.action === 'order') return json_(locked_(function () { return createOrder_(JSON.parse(p.data || '{}')); }));
  if (p.action === 'verify') {
    var res = locked_(function () { return verify_(p); });
    if (res.ok) kickAutomation_();     // paid → send the paid-funnel confirmation right away
    return json_(res);
  }
  return json_({ ok: true, msg: 'ready' });
}

function createOrder_(d) {
  var keyId = prop_('RAZORPAY_KEY_ID'), secret = prop_('RAZORPAY_KEY_SECRET');
  var leadId = 'L' + new Date().getTime() + Math.floor(Math.random() * 1000);
  var funnel = d.funnel_id || DEFAULT_FUNNEL.paid;
  d.plan = '₹99';
  var res = UrlFetchApp.fetch('https://api.razorpay.com/v1/orders', {
    method: 'post', contentType: 'application/json', muteHttpExceptions: true,
    headers: { Authorization: 'Basic ' + Utilities.base64Encode(keyId + ':' + secret) },
    payload: JSON.stringify({ amount: PRICE_PAISE, currency: 'INR', receipt: leadId,
                              notes: { name: clean_(d.name), phone: clean_(d.phone), funnel: funnel } })
  });
  var order = JSON.parse(res.getContentText());
  if (res.getResponseCode() !== 200 || !order.id) {
    addRow_(funnel, d, { status: 'Order failed', lead: leadId });
    return { ok: false, error: 'Could not start payment. Please try again.' };
  }
  addRow_(funnel, d, { status: 'Pending', lead: leadId, order: order.id });
  return { ok: true, key: keyId, order_id: order.id, amount: PRICE_PAISE, lead: leadId };
}

function verify_(p) {
  var secret = prop_('RAZORPAY_KEY_SECRET');
  var sig = Utilities.computeHmacSha256Signature(p.order + '|' + p.payment, secret)
    .map(function (b) { return ('0' + (b & 0xff).toString(16)).slice(-2); }).join('');
  if (sig !== p.sig) return { ok: false, error: 'Payment could not be verified' };
  var sh = tabFor_(p.funnel || DEFAULT_FUNNEL.paid), col = cols_(sh, true);
  var rows = sh.getDataRange().getValues();
  for (var r = rows.length - 1; r >= 1; r--) {
    if (rows[r][col.order - 1] === p.order) {
      sh.getRange(r + 1, col.status).setValue('Paid');
      sh.getRange(r + 1, col.payment).setValue(p.payment);
      sh.getRange(r + 1, col.paid_at).setValue(new Date());
      return { ok: true };
    }
  }
  return { ok: false, error: 'Order not found' };
}

/* ---------- writing rows ---------- */
function addRow_(funnelId, d, extra) {
  var paid = !!extra.status;
  var sh = tabFor_(funnelId), col = cols_(sh, paid);
  var v = {
    ts: new Date(), name: clean_(d.name), phone: clean_(d.phone), email: clean_(d.email),
    reason: clean_(d.reason), serious: clean_(d.serious), profession: clean_(d.profession),
    utm_source: clean_(d.utm_source), utm_medium: clean_(d.utm_medium),
    utm_campaign: clean_(d.utm_campaign), utm_content: clean_(d.utm_content),
    page: clean_(d.page), plan: clean_(d.plan),
    status: extra.status || '', lead: extra.lead || '', order: extra.order || ''
  };
  var row = new Array(sh.getLastColumn()).fill('');
  for (var k in v) if (col[k]) row[col[k] - 1] = v[k];
  sh.appendRow(row);
}

// The funnel's Lead Tab from the A2 Funnels tab (created with A2's base columns if new).
function tabFor_(funnelId) {
  var ss = SpreadsheetApp.getActiveSpreadsheet(), name = FALLBACK_TAB;
  try {
    var f = getFunnels_(ss).filter(function (x) { return x.id.toLowerCase() === String(funnelId).toLowerCase(); })[0];
    if (f) name = f.leadTab;
  } catch (err) {}
  var sh = ss.getSheetByName(name);
  if (!sh) { try { sh = ensureLeadTab_(ss, name); } catch (err) { sh = ss.insertSheet(name); } }
  return sh;
}

// Maps each field to its column number, adding missing columns on the right.
function cols_(sh, paid) {
  var last = Math.max(sh.getLastColumn(), 1);
  var head = sh.getRange(1, 1, 1, last).getValues()[0].map(function (h) { return norm2_(h); });
  var col = {};
  FIELDS.forEach(function (f) {
    if (!paid && PAID_ONLY.indexOf(f[0]) >= 0) return;
    for (var i = 0; i < f[1].length; i++) {
      var at = head.indexOf(norm2_(f[1][i]));
      if (at >= 0) { col[f[0]] = at + 1; return; }
    }
    head.push(norm2_(f[1][0]));
    sh.getRange(1, head.length).setValue(f[1][0]).setFontWeight('bold');
    col[f[0]] = head.length;
  });
  sh.setFrozenRows(1);
  return col;
}

/* ---------- helpers ---------- */
function kickAutomation_() { try { runAutomation(); } catch (err) {} }

function norm2_(s) { return String(s == null ? '' : s).trim().toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, ''); }

function prop_(k) {
  var v = PropertiesService.getScriptProperties().getProperty(k);
  if (!v) throw new Error('Missing script property ' + k);
  return v;
}

function locked_(fn) {
  var lock = LockService.getScriptLock(); lock.waitLock(15000);
  try { return fn(); } catch (err) { return { ok: false, error: String(err.message || err) }; }
  finally { lock.releaseLock(); }
}

// Stops formula injection (cells starting with = + - @) and trims length.
// Also keeps "+91…" as text in Sheets.
function clean_(v) {
  v = String(v == null ? '' : v).slice(0, 300);
  return /^[=+\-@]/.test(v) ? "'" + v : v;
}

function json_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
