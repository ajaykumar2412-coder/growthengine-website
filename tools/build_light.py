import json, sys, copy
import os; exec(open(os.path.join(os.path.dirname(__file__), 'popup_patch.py')).read())

SRC, OUT_JSON, OUT_HTML = sys.argv[1:4]
d = json.load(open(SRC))

TOKENS = {
    "--fx-void:#07051A;": "--fx-void:#FAFAFD;",
    "--fx-void-2:#0C0924;": "--fx-void-2:#F3F1FA;",
    "--fx-line:rgba(183,148,255,.15);": "--fx-line:rgba(76,52,160,.13);",
    "--fx-line-2:rgba(183,148,255,.32);": "--fx-line-2:rgba(76,52,160,.26);",
    "--fx-text:#F4F1FF;": "--fx-text:#14112B;",
    "--fx-muted:#B4ADD8;": "--fx-muted:#4E4A68;",
    "--fx-dim:#8A83B3;": "--fx-dim:#77738F;",
    "--fx-violet:#8B5CF6;": "--fx-violet:#7C3AED;",
    "--fx-violet-hi:#C4A8FF;": "--fx-violet-hi:#6D28D9;",
    "--fx-blue:#3B82F6;": "--fx-blue:#2563EB;",
    "--fx-cyan:#22D3EE;": "--fx-cyan:#0891B2;",
    "--fx-magenta:#FF3DCB;": "--fx-magenta:#DB2777;",
    "--fx-green:#3EF0A6;": "--fx-green:#059669;",
    "--fx-red:#FF6B86;": "--fx-red:#E11D48;",
    "--fx-holo-text:linear-gradient(95deg,#E6DBFF 0%,#9ED8FF 28%,#3DE0F5 48%,#C4A8FF 72%,#FF7ADB 100%);":
        "--fx-holo-text:linear-gradient(95deg,#6D28D9 0%,#2563EB 35%,#0891B2 60%,#7C3AED 80%,#DB2777 100%);",
    "--fx-card:linear-gradient(165deg,rgba(255,255,255,.06) 0%,rgba(255,255,255,.012) 100%);":
        "--fx-card:linear-gradient(165deg,#FFFFFF 0%,#FBFAFF 100%);",
    "body:has(.fx.fx-hero){background:#07051A;}": "body:has(.fx.fx-hero){background:#FAFAFD;}",
}

# Hard-coded colours inside the SVG illustrations / inline styles
SVG = {
    'fill="#150F3A" stroke="#3A2E7A"': 'fill="#F5F1FF" stroke="#D9CFF7"',
    'fill="#140F38"': 'fill="#F5F1FF"',
    'fill="#0F2A2A"': 'fill="#E8FBF3"',
    'fill="#F4F1FF"': 'fill="#14112B"',
    'fill="#E9E4FF"': 'fill="#14112B"',
    'fill="#3A3170"': 'fill="#D4CBF0"',
    'stroke="#3EF0A6"': 'stroke="#10B981"',
    'fill="#3EF0A6"': 'fill="#10B981"',
    'fill="#C4A8FF"': 'fill="#7C3AED"',
    'stroke="#C4A8FF"': 'stroke="#7C3AED"',
    'stroke="#22D3EE"': 'stroke="#0891B2"',
    '<circle r="3.6" fill="#fff">': '<circle r="3.6" fill="#7C3AED">',
    'style="--fx-c:#22D3EE"': 'style="--fx-c:#0891B2"',
    'style="--fx-c:#C4A8FF"': 'style="--fx-c:#7C3AED"',
    'style="--fx-c:#FF7ADB"': 'style="--fx-c:#DB2777"',
}

LIGHT_CSS = """
/* ---------- Light theme overrides ---------- */
.fx::after{display:none;}
.fx.fx-hero{background:
  radial-gradient(ellipse 60% 55% at 88% 8%,rgba(139,92,246,.16),transparent 62%),
  radial-gradient(ellipse 45% 50% at 0% 62%,rgba(37,99,235,.10),transparent 64%),
  radial-gradient(ellipse 35% 35% at 62% 92%,rgba(219,39,119,.08),transparent 70%),var(--fx-void);}
.fx .fx-floor{opacity:.35;}
.fx .fx-kicker{background:#F1EBFF;}
.fx a.fx-ghost{background:#fff;}
.fx a.fx-btn{box-shadow:inset 0 1px 0 rgba(255,255,255,.3),0 16px 36px -14px rgba(124,58,237,.55);}
.fx .fx-holo-frame{background:linear-gradient(160deg,#FFFFFF 0%,#F7F4FF 100%) padding-box,var(--fx-holo-bg) border-box;}
.fx .fx-console{box-shadow:0 40px 90px -45px rgba(76,52,160,.45),0 0 0 8px rgba(139,92,246,.05);}
.fx .fx-live{background:#E7F8F1;}
.fx .fx-tk{color:#14112B;} .fx .fx-tk svg{color:#14112B;} .fx .fx-tk.fx-tk-o{color:rgba(20,17,43,.45);}
.fx .fx-ticker{box-shadow:0 20px 50px -28px rgba(219,39,119,.45);}
.fx .fx-pain,.fx .fx-tile,.fx .fx-pcard,.fx .fx-step,.fx .fx-kpi,.fx .fx-chart{box-shadow:0 1px 2px rgba(20,17,43,.04),0 18px 40px -30px rgba(76,52,160,.35);}
.fx .fx-pain-ico{background:#FFF0F3;border-color:#FBC9D4;}
.fx .fx-mk-x{background:#FFE8EC;} .fx .fx-mk-ok{background:#E3F7EE;}
.fx.fx-why{background:radial-gradient(ellipse 55% 60% at 78% 55%,rgba(139,92,246,.10),transparent 70%),var(--fx-void-2);}
.fx .fx-vs-bad{border-color:rgba(20,17,43,.18);background:#fff;}
.fx .fx-vs-good{box-shadow:0 30px 80px -40px rgba(124,58,237,.5);}
.fx .fx-vs-badge{color:#fff;box-shadow:0 0 0 8px var(--fx-void-2),0 14px 30px rgba(219,39,119,.3);}
.fx .fx-tile-ghost{color:#6D28D9;opacity:.06;}
.fx .fx-tile.fx-accent{background:linear-gradient(160deg,#F3EEFF 0%,#FFFFFF 70%) padding-box,var(--fx-holo-bg) border-box;}
.fx .fx-tile-ico,.fx .fx-proc-num{box-shadow:0 10px 24px -10px rgba(124,58,237,.6);}
.fx .fx-eq-noise{text-shadow:3px 0 rgba(219,39,119,.35),-3px 0 rgba(8,145,178,.35);}
.fx .fx-eq-system{text-shadow:0 0 28px rgba(139,92,246,.35);}
.fx .fx-pcard::before{box-shadow:none;}
.fx.fx-road-sec{background:radial-gradient(ellipse 60% 50% at 15% 100%,rgba(37,99,235,.08),transparent 70%),var(--fx-void-2);}
.fx .fx-shift{background:#fff;} .fx .fx-shift-head{background:#F6F4FC;}
.fx .fx-step::before{background:#fff;box-shadow:0 0 0 4px rgba(8,145,178,.12);}
.fx .fx-road-fill{box-shadow:none;}
.fx .fx-mark{background:linear-gradient(transparent 62%,rgba(219,39,119,.25) 62%,rgba(124,58,237,.25) 92%,transparent 92%);}
.fx.fx-results{color:#14112B;}
.fx.fx-results .fx-h2,.fx.fx-results .fx-label,.fx .fx-result-num{color:#14112B;}
.fx .fx-result-client{background:#14112B;}
.fx .fx-photo{box-shadow:0 30px 80px -40px rgba(124,58,237,.5);}
.fx .fx-ghost-word{color:rgba(109,40,217,.06);}
.fx.fx-final{background:
  radial-gradient(ellipse 60% 70% at 50% 105%,rgba(139,92,246,.20),transparent 70%),
  radial-gradient(ellipse 35% 40% at 50% 105%,rgba(219,39,119,.12),transparent 70%),var(--fx-void);}
.fx.fx-footer{background:#F3F1FA;}
.fx .fx-mbar{background:rgba(255,255,255,.95);box-shadow:0 18px 40px -12px rgba(20,17,43,.25);}
.fx ::selection{background:rgba(124,58,237,.2);color:#14112B;}

/* ---------- KPI dashboard ---------- */
.fx.fx-kpis{background:var(--fx-void);}
.fx .fx-kpi-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;}
.fx .fx-kpi{position:relative;padding:26px 26px 22px;border-radius:22px;border:1px solid var(--fx-line);background:var(--fx-card);overflow:hidden;}
.fx .fx-kpi-top{display:flex;justify-content:space-between;align-items:center;gap:10px;font-size:14px;font-weight:700;color:var(--fx-muted);}
.fx .fx-kpi-ico{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;color:var(--fx-c);background:color-mix(in srgb,var(--fx-c) 10%,#fff);}
.fx .fx-kpi-ico svg{width:17px;height:17px;}
.fx .fx-kpi-num{margin-top:18px;font-family:var(--fx-display);font-weight:700;font-size:clamp(30px,3vw,40px);line-height:1;letter-spacing:-.045em;color:var(--fx-text);}
.fx .fx-kpi-foot{display:flex;align-items:center;gap:10px;margin-top:14px;font-size:13.5px;font-weight:600;color:var(--fx-dim);}
.fx .fx-delta{display:inline-flex;align-items:center;gap:4px;padding:3px 9px;border-radius:999px;font-size:12.5px;font-weight:800;background:#E3F7EE;color:#047857;}
.fx .fx-kpi svg.fx-spark{position:absolute;right:18px;bottom:18px;width:96px;height:34px;}
.fx .fx-chart{margin-top:16px;padding:28px 30px 22px;border-radius:24px;border:1px solid var(--fx-line);background:var(--fx-card);}
.fx .fx-chart-head{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:flex-end;gap:16px;margin-bottom:18px;}
.fx .fx-legend{display:flex;gap:18px;font-size:13.5px;font-weight:700;color:var(--fx-muted);}
.fx .fx-legend i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:7px;vertical-align:-1px;}
.fx svg.fx-bars{display:block;width:100%;height:auto;}
.fx svg.fx-bars text{font-family:var(--fx-body);font-size:12px;font-weight:600;fill:#77738F;}
.fx .fx-note{margin-top:16px;font-size:13px;font-weight:600;color:var(--fx-dim);}
@media (max-width:900px){.fx .fx-kpi-grid{grid-template-columns:1fr 1fr;}}
@media (max-width:560px){.fx .fx-kpi-grid{grid-template-columns:1fr;} .fx .fx-chart{padding:22px 16px 18px;} .fx svg.fx-bars text{font-size:22px;}}
"""

def ico(path):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{path}</svg>'

KPIS = [
    ("Monthly revenue", "₹48.6L", "+182%", "vs. month 1", "#7C3AED", '<path d="M12 3v18M17 7H9.5a3 3 0 000 6h5a3 3 0 010 6H6"/>', "2,30 18,26 34,27 50,18 66,14 82,8 94,3"),
    ("Net profit", "₹19.2L", "+214%", "after ad spend", "#059669", '<path d="M3 17l6-6 4 4 8-8M15 7h6v6"/>', "2,31 18,28 34,25 50,20 66,15 82,9 94,4"),
    ("Profit margin", "39.5%", "+8.4 pts", "net / revenue", "#0891B2", '<circle cx="12" cy="12" r="9"/><path d="M12 3v9l6 5"/>', "2,22 18,21 34,18 50,17 66,12 82,10 94,8"),
    ("Return on ad spend", "4.8x", "+2.1x", "revenue per ₹1 spent", "#2563EB", '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>', "2,28 18,24 34,22 50,17 66,13 82,10 94,6"),
    ("Cost per client", "₹1,240", "−38%", "lower is better", "#DB2777", '<circle cx="9" cy="8" r="4"/><path d="M2 21c0-4 3-6 7-6s7 2 7 6M17 11l2 2 4-4"/>', "2,4 18,9 34,12 50,17 66,20 82,25 94,28"),
    ("Lifetime value : cost", "6.2x", "+2.6x", "each client returns", "#D97706", '<path d="M12 2l3 6.5 7 .8-5.2 4.8 1.4 7L12 17.6 5.8 21.1l1.4-7L2 9.3l7-.8z"/>', "2,27 18,25 34,20 50,18 66,13 82,9 94,5"),
]

def kpi_card(label, num, delta, sub, c, path, pts):
    return f'''      <div class="fx-kpi" style="--fx-c:{c}">
        <div class="fx-kpi-top"><span>{label}</span><span class="fx-kpi-ico">{ico(path)}</span></div>
        <p class="fx-kpi-num">{num}</p>
        <p class="fx-kpi-foot"><span class="fx-delta">{delta}</span>{sub}</p>
        <svg class="fx-spark" viewBox="0 0 96 34" fill="none" aria-hidden="true"><polyline points="{pts}" stroke="{c}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </div>'''

# Revenue vs profit, ₹ lakh, months 1-6
months = ["Month 1", "Month 2", "Month 3", "Month 4", "Month 5", "Month 6"]
rev = [17.2, 21.5, 26.8, 33.4, 40.9, 48.6]
prof = [6.1, 7.9, 10.2, 13.0, 16.1, 19.2]
W, H, top, base, left = 720, 260, 16, 220, 72
scale = (base - top) / 50
grid = "".join(
    f'<line x1="{left}" x2="{W}" y1="{base - v*scale:.1f}" y2="{base - v*scale:.1f}" stroke="#ECE9F5"/>'
    f'<text x="{left-10}" y="{base - v*scale + 4:.1f}" text-anchor="end">₹{v}L</text>'
    for v in (0, 10, 20, 30, 40, 50))
slot = (W - left) / 6
bars = ""
for i, (m, r, p) in enumerate(zip(months, rev, prof)):
    x = left + i * slot + slot / 2
    bars += (f'<rect x="{x-26:.1f}" y="{base - r*scale:.1f}" width="24" height="{r*scale:.1f}" rx="6" fill="url(#fx-rev)"/>'
             f'<rect x="{x+2:.1f}" y="{base - p*scale:.1f}" width="24" height="{p*scale:.1f}" rx="6" fill="#10B981"/>'
             f'<text x="{x:.1f}" y="{base+24}" text-anchor="middle">{m.replace("Month ","M")}</text>')

KPI_HTML = f'''<!-- 02B · BUSINESS KPIs
     Sample numbers: replace them with a real client's results (with permission) or your own. -->
<section class="fx fx-sec fx-kpis" id="fx-kpis">
  <div class="fx-wrap">
    <div class="fx-head">
      <span class="fx-label">The numbers that actually matter</span>
      <h2 class="fx-h2">Not likes and views. <span class="fx-holo">Revenue and profit.</span></h2>
      <p class="fx-lead">Every month you get one simple dashboard showing what the marketing made you, what it cost and what you kept.</p>
    </div>
    <div class="fx-kpi-grid">
{chr(10).join(kpi_card(*k) for k in KPIS)}
    </div>
    <div class="fx-chart">
      <div class="fx-chart-head">
        <h3 class="fx-h3">Revenue vs. net profit, first 6 months</h3>
        <div class="fx-legend"><span><i style="background:linear-gradient(#7C3AED,#2563EB)"></i>Revenue</span><span><i style="background:#10B981"></i>Net profit</span></div>
      </div>
      <svg class="fx-bars" viewBox="0 0 {W} {H}" role="img" aria-label="Revenue grows from 17.2 lakh to 48.6 lakh and net profit from 6.1 lakh to 19.2 lakh over six months">
        <defs><linearGradient id="fx-rev" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7C3AED"/><stop offset="1" stop-color="#2563EB"/></linearGradient></defs>
        {grid}{bars}
      </svg>
      <p class="fx-note">Sample dashboard for illustration. Your numbers will depend on your offer, price and budget.</p>
    </div>
  </div>
</section>'''

def all_html(n):
    for e in n:
        if e.get("widgetType") == "html":
            yield e
        yield from all_html(e.get("elements", []))

for w in all_html(d["content"]):
    h = w["settings"]["html"]
    for a, b in {**TOKENS, **SVG}.items():
        h = h.replace(a, b)
    if "FX CORE" in h:
        assert all(k in w["settings"]["html"] for k in TOKENS), "token missing"
        h = h.replace("/* ---------- Motion off", LIGHT_CSS + "\n/* ---------- Motion off", 1)
        h = patch_core(h)
    w["settings"]["html"] = h

new = copy.deepcopy(d["content"][2])
new["id"], new["elements"][0]["id"], new["elements"][0]["elements"][0]["id"] = "b7e41a0", "c2d93f1", "e5a07c4"
new["settings"]["_title"] = "02B Business KPIs"
new["elements"][0]["elements"][0]["settings"]["html"] = KPI_HTML
d["content"].insert(3, new)
d["title"] = "FX Light LP – Coaches & Creators"

json.dump(d, open(OUT_JSON, "w"), ensure_ascii=False, indent=1)
parts = [w["settings"]["html"] for w in all_html(d["content"])]
open(OUT_HTML, "w").write('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FX Light Landing Page</title><style>body{margin:0}</style></head><body>' + "\n".join(parts) + "</body></html>")
