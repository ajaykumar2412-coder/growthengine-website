/**
 * growthengine.club bootcamp pages → this Google Sheet (+ Razorpay for the ₹99 page).
 *
 * Free page  (/aravind-india/)     : POST  → saves a row.
 * ₹99 page   (/aravind-india-99/)  : GET ?action=order  → saves row as Pending, creates a Razorpay order
 *                                    GET ?action=verify → checks the payment signature, marks row Paid
 *
 * Razorpay keys live in Project Settings → Script properties (never in this code):
 *   RAZORPAY_KEY_ID      rzp_test_... or rzp_live_...
 *   RAZORPAY_KEY_SECRET  the matching secret
 *
 * After editing: Deploy → Manage deployments → ✏️ edit → Version: New version → Deploy
 * (the /exec URL stays the same).
 */
var SHEET_NAME = 'Registrations';
var PRICE_PAISE = 9900;            // ₹99. Fixed here so nobody can change the price from the browser.
var HEADERS = ['Timestamp', 'Name', 'WhatsApp', 'Email', 'Why join', 'How serious', 'Profession',
               'UTM source', 'UTM medium', 'UTM campaign', 'UTM content', 'Page URL',
               'Plan', 'Payment status', 'Lead ID', 'Razorpay order', 'Razorpay payment', 'Paid at'];

/* ---------- free page ---------- */
function doPost(e) {
  var r = routeToAutomation_(e); if (r) return r; // WhatsApp & Email automation (Automation.gs)
  return withLock_(function () {
    var d = JSON.parse((e.postData && e.postData.contents) || '{}');
    d.plan = d.plan || 'Free';
    addRow_(d, '');
    return { ok: true };
  });
}

/* ---------- ₹99 page + health check ---------- */
function doGet(e) {
  var p = (e && e.parameter) || {};
  if (p.unsub || p['hub.mode']) return automationDoGet(e); // WhatsApp & Email automation
  if (p.action === 'order')  return withLock_(function () { return createOrder_(JSON.parse(p.data || '{}')); });
  if (p.action === 'verify') return withLock_(function () { return verify_(p); });
  getSheet_();
  return json_({ ok: true, msg: 'ready' });
}

function createOrder_(d) {
  var keyId = prop_('RAZORPAY_KEY_ID'), secret = prop_('RAZORPAY_KEY_SECRET');
  var leadId = 'L' + new Date().getTime() + Math.floor(Math.random() * 1000);
  d.plan = '₹99';
  var res = UrlFetchApp.fetch('https://api.razorpay.com/v1/orders', {
    method: 'post', contentType: 'application/json', muteHttpExceptions: true,
    headers: { Authorization: 'Basic ' + Utilities.base64Encode(keyId + ':' + secret) },
    payload: JSON.stringify({ amount: PRICE_PAISE, currency: 'INR', receipt: leadId,
                              notes: { name: clean_(d.name), phone: clean_(d.phone) } })
  });
  var order = JSON.parse(res.getContentText());
  if (res.getResponseCode() !== 200 || !order.id) {
    addRow_(d, 'Order failed', leadId, '');
    return { ok: false, error: 'Could not start payment. Please try again.' };
  }
  addRow_(d, 'Pending', leadId, order.id);
  return { ok: true, key: keyId, order_id: order.id, amount: PRICE_PAISE, lead: leadId };
}

function verify_(p) {
  var secret = prop_('RAZORPAY_KEY_SECRET');
  var sig = Utilities.computeHmacSha256Signature(p.order + '|' + p.payment, secret)
    .map(function (b) { return ('0' + (b & 0xff).toString(16)).slice(-2); }).join('');
  if (sig !== p.sig) return { ok: false, error: 'Payment could not be verified' };
  var sh = getSheet_(), col = colMap_(sh), rows = sh.getDataRange().getValues();
  for (var r = rows.length - 1; r >= 1; r--) {
    if (rows[r][col['Razorpay order'] - 1] === p.order) {
      sh.getRange(r + 1, col['Payment status']).setValue('Paid');
      sh.getRange(r + 1, col['Razorpay payment']).setValue(p.payment);
      sh.getRange(r + 1, col['Paid at']).setValue(new Date());
      return { ok: true };
    }
  }
  return { ok: false, error: 'Order not found' };
}

/* ---------- helpers ---------- */
function addRow_(d, status, leadId, orderId) {
  var sh = getSheet_(), col = colMap_(sh), row = new Array(sh.getLastColumn()).fill('');
  var v = {
    'Timestamp': new Date(), 'Name': clean_(d.name), 'WhatsApp': clean_(d.phone),   // clean_ already adds ' before "+91" so Sheets keeps it as text
    'Email': clean_(d.email), 'Why join': clean_(d.reason), 'How serious': clean_(d.serious),
    'Profession': clean_(d.profession), 'UTM source': clean_(d.utm_source), 'UTM medium': clean_(d.utm_medium),
    'UTM campaign': clean_(d.utm_campaign), 'UTM content': clean_(d.utm_content), 'Page URL': clean_(d.page),
    'Plan': clean_(d.plan), 'Payment status': status || '', 'Lead ID': leadId || '', 'Razorpay order': orderId || ''
  };
  for (var k in v) row[col[k] - 1] = v[k];
  sh.appendRow(row);
}

// Creates the tab if missing and adds any new header columns to the right (keeps old rows intact).
function getSheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
  var have = sh.getLastColumn() ? sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0] : [];
  HEADERS.forEach(function (h) { if (have.indexOf(h) < 0) { have.push(h); sh.getRange(1, have.length).setValue(h); } });
  sh.setFrozenRows(1); sh.getRange(1, 1, 1, have.length).setFontWeight('bold');
  return sh;
}

function colMap_(sh) {
  var m = {}; sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0].forEach(function (h, i) { m[h] = i + 1; });
  return m;
}

function prop_(k) {
  var v = PropertiesService.getScriptProperties().getProperty(k);
  if (!v) throw new Error('Missing script property ' + k);
  return v;
}

function withLock_(fn) {
  var lock = LockService.getScriptLock(); lock.waitLock(15000);
  try { return json_(fn()); } catch (err) { return json_({ ok: false, error: String(err.message || err) }); }
  finally { lock.releaseLock(); }
}

// Stops formula injection (cells starting with = + - @) and trims length.
function clean_(v) {
  v = String(v == null ? '' : v).slice(0, 300);
  return /^[=+\-@]/.test(v) ? "'" + v : v;
}

function json_(o) {
  return o && o.getContent ? o : ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
