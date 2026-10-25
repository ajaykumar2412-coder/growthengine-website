POPUP_CSS = """
/* ---------- Booking popup ---------- */
.fx-modal{position:fixed;inset:0;z-index:100000;display:none;align-items:center;justify-content:center;padding:16px;font-family:'Manrope',system-ui,sans-serif;}
.fx-modal.fx-open{display:flex;}
.fx-modal-bg{position:absolute;inset:0;background:rgba(20,17,43,.55);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);animation:fx-fade .25s ease both;}
.fx-modal-box{position:relative;width:100%;max-width:480px;max-height:calc(100vh - 32px);overflow:auto;padding:34px 30px 28px;border-radius:26px;color:#14112B;
  border:1.5px solid transparent;background:linear-gradient(160deg,#fff 0%,#F7F4FF 100%) padding-box,linear-gradient(100deg,#8B5CF6,#22D3EE 48%,#FF3DCB) border-box;
  box-shadow:0 40px 100px -30px rgba(76,52,160,.55);animation:fx-pop .3s cubic-bezier(.2,.8,.2,1) both;}
@keyframes fx-fade{from{opacity:0;}} @keyframes fx-pop{from{opacity:0;transform:translateY(18px) scale(.97);}}
.fx-modal-x{position:absolute;top:14px;right:14px;width:38px;height:38px;border-radius:50%;border:1px solid rgba(76,52,160,.2);background:#fff;color:#14112B;font-size:20px;line-height:1;cursor:pointer;}
.fx-modal h3{margin:0 0 6px;padding-right:40px;font-family:'Unbounded','Manrope',sans-serif;font-size:23px;font-weight:700;letter-spacing:-.035em;line-height:1.15;color:#14112B;}
.fx-modal-sub{margin:0 0 22px;font-size:15px;line-height:1.55;color:#4E4A68;}
.fx-modal label{display:block;margin:0 0 14px;font-size:13.5px;font-weight:700;color:#14112B;}
.fx-modal input,.fx-modal select{display:block;width:100%;margin-top:6px;padding:12px 14px;border-radius:12px;border:1px solid rgba(76,52,160,.24);background:#fff;font:600 15px 'Manrope',sans-serif;color:#14112B;box-sizing:border-box;}
.fx-modal input:focus,.fx-modal select:focus{outline:2px solid #7C3AED;outline-offset:1px;border-color:transparent;}
.fx-modal-row{display:grid;grid-template-columns:1fr 1fr;gap:12px;}
.fx-modal button.fx-submit{width:100%;min-height:54px;margin-top:6px;border:0;border-radius:14px;cursor:pointer;color:#fff;font:600 15px 'Unbounded','Manrope',sans-serif;
  background:linear-gradient(100deg,#7C3AED 0%,#5B3FF0 45%,#2563EB 100%);box-shadow:0 16px 36px -14px rgba(124,58,237,.6);}
.fx-modal button.fx-submit[disabled]{opacity:.6;cursor:wait;}
.fx-modal-fine{margin:12px 0 0;text-align:center;font-size:12.5px;font-weight:600;color:#77738F;}
.fx-modal-done{display:none;text-align:center;padding:10px 0 4px;}
.fx-modal.fx-sent form{display:none;} .fx-modal.fx-sent .fx-modal-done{display:block;}
.fx-modal-tick{width:64px;height:64px;margin:0 auto 18px;border-radius:50%;display:grid;place-items:center;background:#E3F7EE;color:#059669;font-size:30px;font-weight:800;}
.fx-modal-done a{display:inline-flex;margin-top:18px;padding:14px 22px;border-radius:14px;color:#fff;text-decoration:none;font:600 14.5px 'Unbounded',sans-serif;background:linear-gradient(100deg,#7C3AED,#2563EB);}
@media (max-width:480px){.fx-modal-box{padding:30px 20px 22px;} .fx-modal-row{grid-template-columns:1fr;gap:0;}}
"""

POPUP_HTML = """<div class="fx-modal" id="fx-modal" role="dialog" aria-modal="true" aria-labelledby="fx-modal-title" aria-hidden="true">
  <div class="fx-modal-bg" data-fx-close></div>
  <div class="fx-modal-box">
    <button type="button" class="fx-modal-x" data-fx-close aria-label="Close">&times;</button>
    <form novalidate>
      <h3 id="fx-modal-title">Book your free 30-min call</h3>
      <p class="fx-modal-sub">Tell us a little about your business. We'll reply within 24 hours to fix a time.</p>
      <label>Your name<input name="name" autocomplete="name" required></label>
      <div class="fx-modal-row">
        <label>WhatsApp / phone<input name="phone" type="tel" autocomplete="tel" required></label>
        <label>Email<input name="email" type="email" autocomplete="email" required></label>
      </div>
      <label>What do you sell?<select name="business" required><option value="">Choose one</option><option>Coaching</option><option>Online course</option><option>Consulting</option><option>Content / community</option><option>Something else</option></select></label>
      <label>Current monthly revenue<select name="revenue" required><option value="">Choose one</option><option>Just starting (₹0)</option><option>Under ₹1L</option><option>₹1L – ₹5L</option><option>₹5L – ₹20L</option><option>₹20L+</option></select></label>
      <button type="submit" class="fx-submit">Request my call</button>
      <p class="fx-modal-fine">No spam. No sales pitch.</p>
    </form>
    <div class="fx-modal-done" aria-live="polite">
      <div class="fx-modal-tick">&#10003;</div>
      <h3>You're on the list!</h3>
      <p class="fx-modal-sub">Thanks. We'll message you within 24 hours to fix a time that suits you.</p>
      <a class="fx-modal-cal" href="#" target="_blank" rel="noopener" hidden>Pick a time now</a>
    </div>
  </div>
</div>"""

POPUP_JS = r"""    // 1. "Book a call" buttons open the booking popup
    var modal = document.getElementById('fx-modal');
    if(!modal){ var tmp = document.createElement('div'); tmp.innerHTML = FX_POPUP_HTML; modal = tmp.firstElementChild; document.body.appendChild(modal); }
    var form = modal.querySelector('form'), lastFocus = null;
    if(FX_BOOK_URL){ var cal = modal.querySelector('.fx-modal-cal'); cal.href = FX_BOOK_URL; cal.hidden = false; }
    function openModal(){ lastFocus = document.activeElement; modal.classList.remove('fx-sent'); modal.classList.add('fx-open'); modal.setAttribute('aria-hidden','false');
      document.documentElement.style.overflow = 'hidden'; setTimeout(function(){ var f = modal.querySelector('input'); if(f) f.focus(); }, 60); }
    function closeModal(){ modal.classList.remove('fx-open'); modal.setAttribute('aria-hidden','true'); document.documentElement.style.overflow = ''; if(lastFocus) lastFocus.focus(); }
    document.addEventListener('click', function(e){
      var b = e.target.closest && e.target.closest('[data-fx-book]');
      if(b && !editor){ e.preventDefault(); openModal(); return; }
      if(e.target.closest && e.target.closest('[data-fx-close]')) closeModal();
    });
    document.addEventListener('keydown', function(e){ if(e.key === 'Escape' && modal.classList.contains('fx-open')) closeModal(); });
    form.addEventListener('submit', function(e){
      e.preventDefault();
      if(!form.checkValidity()){ form.reportValidity(); return; }
      var btn = form.querySelector('.fx-submit'), data = {};
      new FormData(form).forEach(function(v,k){ data[k] = v; });
      var done = function(){ btn.disabled = false; form.reset(); modal.classList.add('fx-sent'); };
      btn.disabled = true;
      if(FX_FORM_URL){ fetch(FX_FORM_URL,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}).then(done,done); }
      else { done(); }
    });
"""

def patch_core(h):
    h = h.replace("/* ---------- Motion off", POPUP_CSS + "\n/* ---------- Motion off", 1)
    h = h.replace("  var FX_NEW_TAB  = false;  // true = open the booking link in a new tab\n",
        "  var FX_NEW_TAB  = false;  // (unused: the booking link now opens from the popup)\n"
        "  var FX_FORM_URL = '';     // Optional: URL that receives the popup form as JSON (e.g. a Zapier / Make / Google Apps Script webhook)\n", 1)
    a = h.index("    // 1. Point every")
    b = h.index("    if(!('IntersectionObserver' in window)) return;")
    h = h[:a] + POPUP_JS + h[b:]
    h = h.replace("(function(){\n", "(function(){\n  var FX_POPUP_HTML = " + json.dumps(POPUP_HTML).replace("</", "<\\/") + ";\n", 1)
    assert "FX_FORM_URL" in h and "openModal" in h
    return h
