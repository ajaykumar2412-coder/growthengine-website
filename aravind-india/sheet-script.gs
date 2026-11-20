/**
 * Saves sign-ups from growthengine.club/aravind-india/ into this Google Sheet.
 *
 * Setup (one time):
 * 1. Create a Google Sheet → Extensions → Apps Script → paste this file → Save.
 * 2. Deploy → New deployment → type "Web app"
 *      Execute as: Me      Who has access: Anyone
 * 3. Approve permissions, copy the Web app URL (ends in /exec).
 * 4. Paste that URL into SHEET_URL in aravind-india/index.html and push.
 */
var SHEET_NAME = 'Registrations';
var HEADERS = ['Timestamp', 'Name', 'WhatsApp', 'Email', 'Why join', 'How serious',
               'Profession', 'UTM source', 'UTM medium', 'UTM campaign', 'UTM content', 'Page URL'];

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var d = JSON.parse(e.postData.contents || '{}');
    var sh = getSheet_();
    sh.appendRow([
      new Date(), clean_(d.name), "'" + clean_(d.phone), clean_(d.email), clean_(d.reason),
      clean_(d.serious), clean_(d.profession), clean_(d.utm_source), clean_(d.utm_medium),
      clean_(d.utm_campaign), clean_(d.utm_content), clean_(d.page)
    ]);
    return json_({ ok: true });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

// Visiting the /exec URL in a browser should show {"ok":true,"msg":"ready"}
function doGet() { getSheet_(); return json_({ ok: true, msg: 'ready' }); }

function getSheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
  if (sh.getLastRow() === 0) { sh.appendRow(HEADERS); sh.setFrozenRows(1); sh.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold'); }
  return sh;
}

// Stops formula injection (cells starting with = + - @) and trims length.
function clean_(v) {
  v = String(v == null ? '' : v).slice(0, 300);
  return /^[=+\-@]/.test(v) ? "'" + v : v;
}

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
