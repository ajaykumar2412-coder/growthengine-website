/**
 * Google Sheet -> lead-reminders server.
 *
 * Setup: Extensions > Apps Script, paste this file, set SERVER_URL and SECRET,
 * then run setup() once (it adds a 1-minute trigger).
 *
 * Row 1 must be headers and include a "Phone" column. Every column is sent,
 * so any header (Name, Service, City...) can be used as {name}, {service}...
 * in sequence.json. A "WA Status" column is added to mark rows already sent.
 */
const SERVER_URL = 'https://your-server.example.com/lead';
const SECRET = 'change-me-to-a-long-random-string';
const SHEET_NAME = ''; // blank = first sheet
const STATUS_HEADER = 'WA Status';

function setup() {
  ScriptApp.getProjectTriggers().forEach(t => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('syncNewLeads').timeBased().everyMinutes(1).create();
  syncNewLeads();
}

function syncNewLeads() {
  const ss = SpreadsheetApp.getActive();
  const sheet = SHEET_NAME ? ss.getSheetByName(SHEET_NAME) : ss.getSheets()[0];
  const rows = sheet.getDataRange().getValues();
  if (rows.length < 2) return;

  const headers = rows[0].map(String);
  let statusCol = headers.indexOf(STATUS_HEADER);
  if (statusCol === -1) {
    statusCol = headers.length;
    sheet.getRange(1, statusCol + 1).setValue(STATUS_HEADER);
  }

  for (let r = 1; r < rows.length; r++) {
    const row = rows[r];
    if (row[statusCol]) continue; // already handled
    const lead = {};
    headers.forEach((h, i) => { if (h && i !== statusCol) lead[h] = String(row[i]); });
    if (!Object.keys(lead).some(k => /phone|whatsapp|mobile/i.test(k) && lead[k])) continue;

    const res = UrlFetchApp.fetch(SERVER_URL, {
      method: 'post',
      contentType: 'application/json',
      headers: { 'X-Secret': SECRET },
      payload: JSON.stringify(lead),
      muteHttpExceptions: true,
    });
    const ok = res.getResponseCode() === 200;
    sheet.getRange(r + 1, statusCol + 1)
      .setValue(ok ? 'Queued ' + new Date().toLocaleString() : 'Error: ' + res.getContentText().slice(0, 100));
  }
}
