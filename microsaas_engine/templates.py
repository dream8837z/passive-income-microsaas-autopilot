"""Shared responsive HTML layout, SEO/JSON-LD, AdSense, and cross-linking templates."""
from __future__ import annotations

import html
import json
from typing import Any

from .config import SiteConfig


BASE_CSS = """
:root {
  --bg: #0b1120;
  --surface: #111827;
  --surface-2: #1e293b;
  --border: #334155;
  --text: #f8fafc;
  --muted: #94a3b8;
  --accent: #38bdf8;
  --accent-2: #22c55e;
  --warn: #f59e0b;
  --danger: #ef4444;
  --radius: 14px;
}
body.light-mode {
  --bg: #f8fafc;
  --surface: #ffffff;
  --surface-2: #f1f5f9;
  --border: #cbd5e1;
  --text: #0f172a;
  --muted: #475569;
  --accent: #0284c7;
  --accent-2: #16a34a;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.65;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.topbar {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 40;
}
.topbar-inner {
  max-width: 1120px;
  margin: 0 auto;
  padding: 12px 20px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.brand {
  font-weight: 800;
  font-size: 1.05rem;
  color: var(--text);
  letter-spacing: -0.02em;
}
.brand span { color: var(--accent); }
.nav-links {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  font-size: 0.9rem;
  align-items: center;
}
.nav-links a { color: var(--muted); font-weight: 600; }
.nav-links a:hover { color: var(--text); text-decoration: none; }
.wrap {
  max-width: 1120px;
  margin: 0 auto;
  padding: 28px 20px 64px;
}
.hero {
  background: linear-gradient(135deg, rgba(56,189,248,0.14), rgba(34,197,94,0.10));
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 28px;
  margin-bottom: 24px;
}
.badge {
  display: inline-block;
  font-size: 0.78rem;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(56,189,248,0.18);
  color: var(--accent);
  margin-bottom: 10px;
}
.badge.green { background: rgba(34,197,94,0.18); color: var(--accent-2); }
.badge.warn { background: rgba(245,158,11,0.18); color: var(--warn); }
h1 { margin: 0 0 10px; font-size: clamp(1.55rem, 3vw, 2.2rem); line-height: 1.25; }
h2 { margin: 0 0 12px; font-size: 1.3rem; }
h3 { margin: 0 0 8px; font-size: 1.05rem; }
p { margin: 0 0 12px; color: var(--text); }
.muted { color: var(--muted); }
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 22px;
  margin-bottom: 20px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}
.grid-2 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 18px;
}
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin: 16px 0;
}
.kpi {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px;
}
.kpi-label { font-size: 0.8rem; color: var(--muted); margin-bottom: 4px; }
.kpi-val { font-size: 1.4rem; font-weight: 800; color: var(--text); }
.kpi-val.pos { color: var(--accent-2); }
.kpi-val.neg { color: var(--danger); }
.kpi-val.acc { color: var(--accent); }
.btn {
  display: inline-block;
  background: var(--accent);
  color: #0b1120;
  font-weight: 700;
  padding: 10px 16px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  font-size: 0.92rem;
}
.btn:hover { opacity: 0.92; text-decoration: none; }
.btn.secondary {
  background: var(--surface-2);
  color: var(--text);
  border: 1px solid var(--border);
}
.btn.green { background: var(--accent-2); color: #052e16; }
.btn.danger { background: var(--danger); color: #fff; }
.btn-sm { padding: 6px 11px; font-size: 0.82rem; border-radius: 8px; }
input, select, textarea {
  width: 100%;
  padding: 10px 12px;
  border-radius: 9px;
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: var(--text);
  font-size: 0.95rem;
  margin-top: 4px;
}
label { display: block; font-size: 0.85rem; color: var(--muted); margin-bottom: 10px; font-weight: 600; }
table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.92rem; }
th, td { padding: 10px 12px; border-bottom: 1px solid var(--border); text-align: left; }
th { color: var(--muted); font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.04em; }
.ad-slot {
  margin: 22px 0;
  padding: 10px;
  border-radius: 12px;
  background: var(--surface-2);
  border: 1px dashed var(--border);
  text-align: center;
  min-height: 96px;
}
.ad-label { font-size: 0.7rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px; }
.pill-list { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
.pill {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 999px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  color: var(--text);
  font-size: 0.84rem;
}
.pill:hover { border-color: var(--accent); text-decoration: none; }
.alert {
  padding: 14px 16px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: rgba(245,158,11,0.12);
  color: var(--text);
  margin: 12px 0;
  font-size: 0.92rem;
}
.alert.danger { background: rgba(239,68,68,0.14); border-color: rgba(239,68,68,0.45); }
.alert.success { background: rgba(34,197,94,0.14); border-color: rgba(34,197,94,0.45); }
.faq details {
  border-bottom: 1px solid var(--border);
  padding: 12px 0;
}
.faq summary { font-weight: 700; cursor: pointer; }
.faq p { margin-top: 8px; color: var(--muted); }
footer {
  border-top: 1px solid var(--border);
  margin-top: 40px;
  padding-top: 22px;
  font-size: 0.85rem;
  color: var(--muted);
}
@media print {
  .topbar, .ad-slot, .no-print, footer { display: none !important; }
  body { background: #fff; color: #000; }
  .card { border: 1px solid #ccc; background: #fff; }
}
""".strip()


def render_ad_slot(cfg: SiteConfig, slot_name: str = "content") -> str:
    if not cfg.adsense_client_id:
        return ""
    return (
        f'<div class="ad-slot no-print" data-slot="{html.escape(slot_name)}">'
        f'<div class="ad-label">Advertisement</div>'
        f'<ins class="adsbygoogle" style="display:block" '
        f'data-ad-client="{html.escape(cfg.adsense_client_id)}" '
        f'data-ad-format="auto" data-full-width-responsive="true"></ins>'
        f'<script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>'
        f'</div>'
    )


def render_page(
    cfg: SiteConfig,
    rel_path: str,
    title: str,
    description: str,
    body_html: str,
    updated_date: str,
    json_ld: dict[str, Any] | None = None,
    extra_head: str = "",
) -> str:
    canonical = f"{cfg.site_url}/{rel_path.lstrip('/')}"
    if rel_path == "index.html":
        canonical = f"{cfg.site_url}/"
    depth = rel_path.count("/")
    prefix = "../" * depth

    adsense_head = ""
    if cfg.adsense_client_id:
        cid = html.escape(cfg.adsense_client_id)
        adsense_head = (
            f'<meta name="google-adsense-account" content="{cid}">\n'
            f'  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={cid}" crossorigin="anonymous"></script>'
        )

    ld_script = ""
    if json_ld:
        ld_script = (
            '<script type="application/ld+json">\n'
            + json.dumps(json_ld, ensure_ascii=False, indent=2)
            + "\n</script>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)} | WealthStack Studio</title>
  <meta name="description" content="{html.escape(description)}">
  <link rel="canonical" href="{html.escape(canonical)}">
  <link rel="manifest" href="{prefix}manifest.json">
  <meta name="theme-color" content="#0b1120">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{html.escape(canonical)}">
  {adsense_head}
  <style>{BASE_CSS}</style>
  {ld_script}
  {extra_head}
</head>
<body>
  <header class="topbar no-print">
    <div class="topbar-inner">
      <a class="brand" href="{prefix}index.html">WealthStack <span>Studio</span></a>
      <nav class="nav-links">
        <a href="{prefix}apps/clutch-driving-instructor.html">Clutch B2B App</a>
        <a href="{prefix}apps/commercial-nnn-analyzer.html">NNN Property</a>
        <a href="{prefix}apps/passive-income-planner.html">HYSA &amp; Dividend</a>
        <a href="{prefix}apps/public-domain-pod-studio.html">PD-POD Studio</a>
        <a href="{html.escape(cfg.kr_hub_url)}">KR Finance Hub</a>
        <button class="btn secondary btn-sm" type="button" onclick="document.body.classList.toggle('light-mode')">Theme</button>
      </nav>
    </div>
  </header>
  <main class="wrap">
    {body_html}
    <footer>
      <p><strong>WealthStack Studio</strong> — Free Vibe-Coded B2B Micro-SaaS &amp; 2027 Passive Income Calculator Suite. Auto-synced daily ({html.escape(updated_date)}).</p>
      <p>
        <a href="{prefix}index.html">Studio Home</a> ·
        <a href="{prefix}about.html">About</a> ·
        <a href="{prefix}privacy.html">Privacy Policy</a> ·
        <a href="{prefix}disclaimer.html">Financial Disclaimer</a> ·
        <a href="{prefix}terms.html">Terms</a> ·
        <a href="{html.escape(cfg.root_portal_url)}">Main Portal</a>
      </p>
    </footer>
  </main>
</body>
</html>
"""
