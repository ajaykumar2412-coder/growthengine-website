import json, sys

SRC, OUT = sys.argv[1:3]
d = json.load(open(SRC))
secs = d["content"]

def html_of(sec):
    return sec["elements"][0]["elements"][0]["settings"]["html"]

core = html_of(secs[0])
blocks = []
for i, s in enumerate(secs[1:], 1):
    title = s["settings"].get("_title", f"Section {i}")
    blocks.append(f'<div class="ed-sec" data-idx="{i}" data-title="{title}">\n{html_of(s)}\n</div>')

template = json.dumps(d, ensure_ascii=False).replace("</", "<\\/")

EDITOR = r"""
<style>
body{padding-top:62px;}
.ed-bar{position:fixed;top:0;left:0;right:0;z-index:200000;display:flex;align-items:center;gap:8px;flex-wrap:wrap;min-height:62px;padding:10px 14px;box-sizing:border-box;
  background:#14112B;color:#fff;font:600 13px/1.2 system-ui,-apple-system,'Segoe UI',sans-serif;box-shadow:0 8px 24px rgba(0,0,0,.25);}
.ed-bar b{font-weight:800;}
.ed-bar .ed-sel{min-width:150px;max-width:240px;padding:0 8px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;color:#C4B5FD;}
.ed-bar button,.ed-bar label.ed-btn{display:inline-flex;align-items:center;gap:6px;height:36px;padding:0 12px;border-radius:9px;border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.06);
  color:#fff;font:inherit;cursor:pointer;white-space:nowrap;}
.ed-bar button:hover:not([disabled]),.ed-bar label.ed-btn:hover{background:rgba(255,255,255,.14);}
.ed-bar button[disabled]{opacity:.35;cursor:not-allowed;}
.ed-bar button.ed-on{background:#7C3AED;border-color:#7C3AED;}
.ed-bar button.ed-primary{background:linear-gradient(100deg,#7C3AED,#2563EB);border:0;}
.ed-bar button.ed-danger:hover:not([disabled]){background:#BE123C;}
.ed-bar input[type=color]{width:22px;height:22px;padding:0;border:0;background:none;cursor:pointer;}
.ed-sp{flex:1;}
.ed-sep{width:1px;height:26px;background:rgba(255,255,255,.18);margin:0 2px;}
.ed-layers{position:fixed;top:74px;left:12px;z-index:199999;width:210px;max-height:calc(100vh - 90px);overflow:auto;padding:8px;border-radius:14px;background:#fff;
  box-shadow:0 14px 40px rgba(20,17,43,.22);font:600 12.5px system-ui,sans-serif;color:#14112B;}
.ed-layers p{margin:4px 6px 8px;font-size:11px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:#77738F;}
.ed-layers div{padding:8px 10px;border-radius:8px;cursor:pointer;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.ed-layers div:hover{background:#F3F1FA;}
.ed-layers div.ed-active{background:#7C3AED;color:#fff;}
.ed-layers div.ed-hid{opacity:.45;text-decoration:line-through;}
body.ed-nolayers .ed-layers{display:none;}
body.ed-edit .ed-sec{position:relative;cursor:pointer;}
body.ed-edit .ed-sec::after{content:"";position:absolute;inset:0;z-index:99990;pointer-events:none;outline:2px dashed transparent;outline-offset:-3px;transition:outline-color .12s;}
body.ed-edit .ed-sec:hover::after{outline-color:#8B5CF6;}
body.ed-edit .ed-sec.ed-active::after{outline:3px solid #7C3AED;outline-offset:-3px;}
body.ed-edit .ed-sec::before{content:attr(data-title);position:absolute;top:10px;left:10px;z-index:99991;padding:5px 10px;border-radius:7px;background:#7C3AED;color:#fff;
  font:700 12px system-ui,sans-serif;opacity:0;pointer-events:none;transition:opacity .12s;}
body.ed-edit .ed-sec:hover::before,body.ed-edit .ed-sec.ed-active::before{opacity:1;}
.ed-sec.ed-hidden{display:none;}
body.ed-edit .ed-sec.ed-hidden{display:block;opacity:.3;}
body.ed-edit .ed-sec[contenteditable=true]{cursor:text;}
body.ed-edit .ed-sec[contenteditable=true]::before{content:"Editing text: click any words to change them";background:#059669;}
.ed-toast{position:fixed;left:50%;bottom:22px;z-index:200001;transform:translateX(-50%);padding:11px 18px;border-radius:11px;background:#14112B;color:#fff;font:600 13.5px system-ui,sans-serif;
  box-shadow:0 10px 30px rgba(0,0,0,.3);opacity:0;transition:opacity .2s;pointer-events:none;}
.ed-toast.ed-show{opacity:1;}
@media (max-width:1100px){.ed-layers{display:none;}}
</style>
<div class="ed-bar" id="ed-bar">
  <button id="ed-mode" class="ed-on" title="Switch between editing and clicking through the page normally">✎ Edit mode</button>
  <button id="ed-layers-t" title="Show or hide the section list">☰ Sections</button>
  <span class="ed-sep"></span>
  <span class="ed-sel" id="ed-sel">Hover a section and click it</span>
  <button data-a="up" title="Move up">↑ Up</button>
  <button data-a="down" title="Move down">↓ Down</button>
  <button data-a="dup" title="Duplicate">⧉ Duplicate</button>
  <button data-a="text" title="Edit the words in this section">T Edit text</button>
  <label class="ed-btn" title="Background colour">Bg <input type="color" id="ed-bg" value="#ffffff"></label>
  <button data-a="bgreset" title="Reset background">Reset bg</button>
  <button data-a="hide" title="Hide / show">◐ Hide</button>
  <button data-a="del" class="ed-danger" title="Delete">✕ Delete</button>
  <span class="ed-sp"></span>
  <button id="ed-undo" title="Undo (Ctrl+Z)">↶ Undo</button>
  <button id="ed-html" title="Download the page as HTML">⬇ HTML</button>
  <button id="ed-json" class="ed-primary" title="Download an Elementor template you can import">⬇ Elementor JSON</button>
</div>
<div class="ed-layers" id="ed-layers"></div>
<div class="ed-toast" id="ed-toast"></div>
<script>
(function(){
  var TEMPLATE = __TEMPLATE__;
  var root = document.getElementById('ed-root'), body = document.body;
  var selSpan = document.getElementById('ed-sel'), layers = document.getElementById('ed-layers');
  var current = null, textMode = false, undo = [], dupN = 0;
  body.classList.add('ed-edit');

  function secs(){ return Array.prototype.slice.call(root.querySelectorAll(':scope > .ed-sec')); }
  function toast(m){ var t = document.getElementById('ed-toast'); t.textContent = m; t.classList.add('ed-show'); clearTimeout(t._h); t._h = setTimeout(function(){ t.classList.remove('ed-show'); }, 1800); }
  function snap(){ stopText(); undo.push(root.innerHTML); if(undo.length > 60) undo.shift(); }
  function sectionEl(w){ return w.querySelector('section') || w.firstElementChild; }

  function renderLayers(){
    layers.innerHTML = '<p>Sections</p>';
    secs().forEach(function(w){
      var r = document.createElement('div');
      r.textContent = w.dataset.title;
      if(w === current) r.className = 'ed-active';
      if(w.classList.contains('ed-hidden')) r.className += ' ed-hid';
      r.onclick = function(){ select(w, true); };
      layers.appendChild(r);
    });
  }
  function refresh(){
    var none = !current, all = secs(), i = all.indexOf(current);
    document.querySelectorAll('.ed-bar [data-a]').forEach(function(b){ b.disabled = none; });
    document.getElementById('ed-bg').disabled = none;
    if(current){
      document.querySelector('[data-a=up]').disabled = i <= 0;
      document.querySelector('[data-a=down]').disabled = i >= all.length - 1;
      document.querySelector('[data-a=hide]').textContent = current.classList.contains('ed-hidden') ? '◑ Show' : '◐ Hide';
      document.querySelector('[data-a=text]').classList.toggle('ed-on', textMode);
    }
    selSpan.textContent = current ? current.dataset.title : 'Hover a section and click it';
    document.getElementById('ed-undo').disabled = !undo.length;
    renderLayers();
  }
  function select(w, scroll){
    if(current && current !== w) stopText();
    secs().forEach(function(s){ s.classList.toggle('ed-active', s === w); });
    current = w; refresh();
    if(scroll && w) w.scrollIntoView({behavior:'smooth', block:'start'});
  }
  function stopText(){ if(textMode && current){ current.removeAttribute('contenteditable'); } textMode = false; }

  root.addEventListener('click', function(e){
    if(!body.classList.contains('ed-edit')) return;
    var w = e.target.closest('.ed-sec');
    if(textMode && w === current){ if(e.target.closest('a,summary,button')){ e.preventDefault(); e.stopPropagation(); } return; }
    e.preventDefault(); e.stopPropagation();
    if(w) select(w);
  }, true);

  var actions = {
    up: function(){ var p = current.previousElementSibling; if(p){ snap(); root.insertBefore(current, p); } },
    down: function(){ var n = current.nextElementSibling; if(n){ snap(); root.insertBefore(n, current); } },
    dup: function(){ snap(); var c = current.cloneNode(true); c.classList.remove('ed-active'); c.dataset.title = current.dataset.title.replace(/ \(copy.*\)$/, '') + ' (copy ' + (++dupN) + ')';
      c.querySelectorAll('[id]').forEach(function(el){ el.removeAttribute('id'); }); current.after(c); select(c, true); toast('Section duplicated'); },
    hide: function(){ snap(); current.classList.toggle('ed-hidden'); toast(current.classList.contains('ed-hidden') ? 'Hidden: it won\'t be exported' : 'Visible again'); },
    del: function(){ if(!confirm('Delete "' + current.dataset.title + '"? You can undo this.')) return; snap(); var n = current.nextElementSibling || current.previousElementSibling; current.remove(); current = null; select(n); toast('Section deleted'); },
    text: function(){ if(textMode){ stopText(); toast('Text editing off'); } else { snap(); textMode = true; current.setAttribute('contenteditable','true'); current.focus(); toast('Click any text in the section to edit it'); } },
    bgreset: function(){ snap(); sectionEl(current).style.background = ''; toast('Background reset'); }
  };
  document.querySelectorAll('.ed-bar [data-a]').forEach(function(b){ b.addEventListener('click', function(){ if(current){ actions[b.dataset.a](); refresh(); } }); });
  var bg = document.getElementById('ed-bg');
  bg.addEventListener('focus', function(){ if(current) snap(); });
  bg.addEventListener('input', function(){ if(current) sectionEl(current).style.background = bg.value; });

  function doUndo(){ if(!undo.length) return; stopText(); var idx = current ? secs().indexOf(current) : -1; root.innerHTML = undo.pop(); current = null; var s = secs(); if(idx >= 0 && s[Math.min(idx, s.length-1)]) select(s[Math.min(idx, s.length-1)]); else refresh(); toast('Undone'); }
  document.getElementById('ed-undo').onclick = doUndo;
  document.addEventListener('keydown', function(e){
    if((e.ctrlKey || e.metaKey) && e.key === 'z' && !textMode){ e.preventDefault(); doUndo(); }
    if(e.key === 'Escape' && body.classList.contains('ed-edit')){ if(textMode){ stopText(); refresh(); } else { select(null); } }
  });
  document.getElementById('ed-mode').onclick = function(){
    var on = body.classList.toggle('ed-edit'); stopText();
    this.classList.toggle('ed-on', on); this.textContent = on ? '✎ Edit mode' : '▶ Preview mode';
    if(!on){ select(null); } toast(on ? 'Edit mode: click a section to select it' : 'Preview mode: buttons and popup work normally');
  };
  document.getElementById('ed-layers-t').onclick = function(){ body.classList.toggle('ed-nolayers'); };

  // ---------- Export ----------
  function cleanHTML(w){
    var c = w.cloneNode(true);
    c.removeAttribute('contenteditable');
    c.querySelectorAll('[contenteditable]').forEach(function(el){ el.removeAttribute('contenteditable'); });
    c.querySelectorAll('.fx-show').forEach(function(el){ el.classList.remove('fx-show'); });
    c.querySelectorAll('.fx-road').forEach(function(el){ el.style.removeProperty('--fx-p'); if(!el.getAttribute('style')) el.removeAttribute('style'); });
    return c.innerHTML.replace(/^\n|\n$/g, '');
  }
  function rid(){ return Math.random().toString(16).slice(2, 9); }
  function download(name, text, type){ var a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([text], {type:type})); a.download = name; a.click(); setTimeout(function(){ URL.revokeObjectURL(a.href); }, 1000); }
  function live(){ return secs().filter(function(w){ return !w.classList.contains('ed-hidden'); }); }
  document.getElementById('ed-json').onclick = function(){
    stopText(); refresh();
    var out = JSON.parse(JSON.stringify(TEMPLATE)), used = {};
    out.content = [TEMPLATE.content[0]].concat(live().map(function(w){
      var idx = +w.dataset.idx, s = JSON.parse(JSON.stringify(TEMPLATE.content[idx]));
      if(used[idx]){ s.id = rid(); s.elements[0].id = rid(); s.elements[0].elements[0].id = rid(); }
      used[idx] = 1;
      s.settings._title = w.dataset.title;
      s.elements[0].elements[0].settings.html = cleanHTML(w);
      return s;
    }));
    download('FX-LP-edited-elementor-template.json', JSON.stringify(out, null, 1), 'application/json');
    toast('Elementor template downloaded');
  };
  document.getElementById('ed-html').onclick = function(){
    stopText(); refresh();
    var page = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Landing page</title><style>body{margin:0}</style></head><body>'
      + TEMPLATE.content[0].elements[0].elements[0].settings.html + '\n' + live().map(cleanHTML).join('\n') + '</body></html>';
    download('landing-page.html', page, 'text/html');
    toast('HTML downloaded');
  };
  refresh();
})();
</script>
""".replace("__TEMPLATE__", template)

page = ('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Landing Page Editor</title><style>body{margin:0}</style></head><body>'
        + core + '\n<div id="ed-root">\n' + "\n".join(blocks) + '\n</div>\n' + EDITOR + '</body></html>')
open(OUT, "w").write(page)
