"""Programmatic SEO (pSEO) page generator for 104+ high-CPC USD passive income queries."""
from __future__ import annotations

import html
from typing import Any

from .calculators import (
    calc_capital_for_income,
    calc_drip_projection,
    calc_hysa_comparison,
    calc_microsaas_mrr,
    calc_pod_economics,
    calc_property_comparison,
)
from .config import SiteConfig
from .public_domain_db import PUBLIC_DOMAIN_CATALOG
from .templates import render_ad_slot, render_page


def _usd(v: float) -> str:
    sign = "-" if v < 0 else ""
    return f"{sign}${abs(v):,.0f}"


def _usd2(v: float) -> str:
    sign = "-" if v < 0 else ""
    return f"{sign}${abs(v):,.2f}"


def build_hysa_pages(cfg: SiteConfig, market: dict[str, Any]) -> list[tuple[str, str, str]]:
    """24 High-CPC HYSA comparison pages ($5k..$250k x 4.0%..5.0% APY)."""
    amounts = [5_000, 10_000, 25_000, 50_000, 100_000, 250_000]
    apys = [4.0, 4.2, 4.5, 5.0]
    gbp_rate = market["fx_rates"].get("GBP", 0.79)
    krw_rate = market["fx_rates"].get("KRW", 1385.0)
    pages: list[tuple[str, str, str]] = []

    for amt in amounts:
        amt_slug = f"{amt // 1000}k"
        for apy in apys:
            apy_slug = str(apy).replace(".", "_")
            rel = f"hysa/hysa-{amt_slug}-{apy_slug}-apy.html"
            r1 = calc_hysa_comparison(amt, apy, 0.38, years=1)
            r5 = calc_hysa_comparison(amt, apy, 0.38, years=5)
            cap_100wk = calc_capital_for_income(5_200, apy)
            fdic_note = (
                "Fully within the standard US FDIC $250,000 per-depositor, per-bank limit."
                if amt <= 250_000
                else "Exceeds $250,000 FDIC limit — split across multiple insured banks."
            )
            title = f"{_usd(amt)} in a {apy:.1f}% APY High-Yield Savings Account (2027 Interest Calculator)"
            desc = (
                f"See how much interest {_usd(amt)} earns at {apy:.1f}% APY ({_usd2(r1['hysa_interest'])}/yr) "
                f"vs a 0.38% average US bank account ({_usd2(r1['base_interest'])}/yr). Includes 5-year compounding and FDIC check."
            )
            related = "".join(
                f'<a class="pill" href="hysa-{a // 1000}k-{apy_slug}-apy.html">{_usd(a)} @ {apy:.1f}%</a>'
                for a in amounts if a != amt
            )
            body = f"""
            <section class="hero">
              <span class="badge">High-Yield Savings (HYSA) • Updated {market['updated_date']}</span>
              <h1>{html.escape(title)}</h1>
              <p class="muted">Putting <strong>{_usd(amt)}</strong> into a <strong>{apy:.1f}% APY</strong> high-yield savings account earns <strong>{_usd2(r1['hysa_interest'])}</strong> in year 1 — that is <strong>+{_usd2(r1['extra_gain'])}</strong> more passive income than leaving it in an average 0.38% US savings account ({_usd2(r1['base_interest'])}).</p>
              <a class="btn btn-sm" href="../apps/passive-income-planner.html">Open Interactive HYSA &amp; Dividend Planner →</a>
            </section>

            <div class="kpi-grid">
              <div class="kpi"><div class="kpi-label">Year 1 Interest ({apy:.1f}% APY)</div><div class="kpi-val pos">{_usd2(r1['hysa_interest'])}</div></div>
              <div class="kpi"><div class="kpi-label">Extra Earned vs 0.38% Bank</div><div class="kpi-val acc">+{_usd2(r1['extra_gain'])}</div></div>
              <div class="kpi"><div class="kpi-label">Monthly Passive Interest</div><div class="kpi-val">{_usd2(r1['monthly_passive'])}/mo</div></div>
              <div class="kpi"><div class="kpi-label">5-Year Compounded Balance</div><div class="kpi-val pos">{_usd(r5['hysa_final'])}</div></div>
            </div>

            {render_ad_slot(cfg, "hysa-mid")}

            <section class="card">
              <h2>1-Year &amp; 5-Year Comparison Table</h2>
              <table>
                <thead><tr><th>Account Type</th><th>APY</th><th>Year 1 Interest</th><th>5-Year Interest</th><th>5-Year Ending Balance</th></tr></thead>
                <tbody>
                  <tr><td><strong>High-Yield Savings (HYSA)</strong></td><td>{apy:.2f}%</td><td><strong>{_usd2(r1['hysa_interest'])}</strong></td><td><strong>{_usd2(r5['hysa_interest'])}</strong></td><td><strong>{_usd(r5['hysa_final'])}</strong></td></tr>
                  <tr><td>Average US Bank Savings</td><td>0.38%</td><td>{_usd2(r1['base_interest'])}</td><td>{_usd2(r5['base_interest'])}</td><td>{_usd(r5['base_final'])}</td></tr>
                </tbody>
              </table>
              <div class="alert success" style="margin-top:14px">
                <strong>Deposit Protection &amp; FX Equivalent:</strong> {fdic_note}
                At today's ECB rate ({market['fx_date']}), {_usd(amt)} ≈ <strong>£{amt * gbp_rate:,.0f} GBP</strong> / <strong>₩{amt * krw_rate:,.0f} KRW</strong>.
              </div>
            </section>

            <section class="card faq">
              <h2>Frequently Asked Questions</h2>
              <details open><summary>How much money do I need at {apy:.1f}% APY to make $100 a week?</summary><p>To generate $100/week ($5,200/year) purely from interest at {apy:.1f}% APY, you need approximately <strong>{_usd(cap_100wk)}</strong> deposited across FDIC-insured accounts.</p></details>
              <details><summary>Watch out for temporary introductory bonus rates</summary><p>Many high-yield accounts advertise a short-term welcome bonus rate that drops after 3–6 months. Always check the underlying base APY and verify there are no monthly maintenance fees.</p></details>
            </section>

            <section class="card">
              <h3>Compare Other Deposit Amounts at {apy:.1f}% APY</h3>
              <div class="pill-list">{related}</div>
            </section>
            """
            ld = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": f"How much interest does {_usd(amt)} earn at {apy:.1f}% APY?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": f"{_usd(amt)} at {apy:.1f}% APY earns {_usd2(r1['hysa_interest'])} in 1 year and {_usd2(r5['hysa_interest'])} over 5 years compounded.",
                        },
                    }
                ],
            }
            pages.append((rel, title, render_page(cfg, rel, title, desc, body, market["updated_date"], json_ld=ld)))
    return pages


def build_dividend_pages(cfg: SiteConfig, market: dict[str, Any]) -> list[tuple[str, str, str]]:
    """24 High-CPC Dividend ETF income goal pages."""
    targets = [
        ("100-week", "$100/Week", 5_200),
        ("250-week", "$250/Week", 13_000),
        ("500-month", "$500/Month", 6_000),
        ("1000-month", "$1,000/Month", 12_000),
        ("2500-month", "$2,500/Month", 30_000),
        ("5000-month", "$5,000/Month", 60_000),
    ]
    yields = [2.97, 4.0, 5.0, 6.0]
    pages: list[tuple[str, str, str]] = []

    for slug_t, label_t, annual_usd in targets:
        for yld in yields:
            y_slug = str(yld).replace(".", "_")
            rel = f"dividend/invest-for-{slug_t}-at-{y_slug}-yield.html"
            cap = calc_capital_for_income(annual_usd, yld)
            drip10 = calc_drip_projection(25_000, 500, yld, price_growth_pct=4.0, years=10)
            etf_note = (
                "Matches the Vanguard FTSE All-World High Dividend Yield ETF (2.97%) global benchmark."
                if yld == 2.97
                else f"Typical of diversified high-dividend ETFs, REITs, or covered-call income portfolios yielding {yld:.1f}%."
            )
            title = f"How Much to Invest for {label_t} in Dividends at {yld:.2f}% Yield (2027 Calculator)"
            desc = (
                f"To earn {label_t} ({_usd(annual_usd)}/yr) in passive dividend income at a {yld:.2f}% yield, "
                f"you need {_usd(cap)} invested. Compare DRIP compounding and ETF diversification."
            )
            related = "".join(
                f'<a class="pill" href="invest-for-{st}-at-{y_slug}-yield.html">{lt} @ {yld:.2f}%</a>'
                for st, lt, _ in targets if st != slug_t
            )
            body = f"""
            <section class="hero">
              <span class="badge green">Dividend ETF Passive Income • Updated {market['updated_date']}</span>
              <h1>{html.escape(title)}</h1>
              <p class="muted">To generate <strong>{label_t}</strong> ({_usd(annual_usd)}/year) in quarterly dividends at a <strong>{yld:.2f}%</strong> dividend yield, you need approximately <strong>{_usd(cap)}</strong> invested. {etf_note}</p>
              <a class="btn btn-sm" href="../apps/passive-income-planner.html">Customize in DiviFlow DRIP Planner →</a>
            </section>

            <div class="kpi-grid">
              <div class="kpi"><div class="kpi-label">Required Dividend Portfolio</div><div class="kpi-val acc">{_usd(cap)}</div></div>
              <div class="kpi"><div class="kpi-label">Annual Dividend Target</div><div class="kpi-val pos">{_usd(annual_usd)}/yr</div></div>
              <div class="kpi"><div class="kpi-label">Monthly Average Payout</div><div class="kpi-val">{_usd2(annual_usd / 12)}/mo</div></div>
              <div class="kpi"><div class="kpi-label">Weekly Passive Income</div><div class="kpi-val pos">{_usd2(annual_usd / 52)}/wk</div></div>
            </div>

            {render_ad_slot(cfg, "dividend-mid")}

            <section class="card">
              <h2>10-Year DRIP Simulation ($25,000 Start + $500/mo Auto-Invest)</h2>
              <p class="muted">Assuming {yld:.2f}% dividend yield reinvested plus 4.0% annual share-price appreciation:</p>
              <table>
                <thead><tr><th>Metric</th><th>10-Year DRIP Outcome</th></tr></thead>
                <tbody>
                  <tr><td>Total Cash Contributed</td><td>{_usd(drip10['total_contributed'])}</td></tr>
                  <tr><td>Projected Ending Portfolio Value</td><td><strong>{_usd(drip10['ending_balance'])}</strong></td></tr>
                  <tr><td>Projected Annual Dividend in Year 10</td><td><strong>{_usd2(drip10['annual_dividend'])}/yr ({_usd2(drip10['weekly_dividend'])}/wk)</strong></td></tr>
                </tbody>
              </table>
            </section>

            <section class="card">
              <h3>Explore Other Passive Dividend Targets at {yld:.2f}% Yield</h3>
              <div class="pill-list">{related}</div>
            </section>
            """
            pages.append((rel, title, render_page(cfg, rel, title, desc, body, market["updated_date"])))
    return pages


def build_property_pages(cfg: SiteConfig, market: dict[str, Any]) -> list[tuple[str, str, str]]:
    """24 Commercial NNN vs Residential Rental comparison pages."""
    prices = [150_000, 200_000, 300_000, 370_000, 500_000, 1_000_000]
    caps = [6.5, 7.5, 8.5, 9.5]
    pages: list[tuple[str, str, str]] = []

    for price in prices:
        p_slug = f"{price // 1000}k"
        for cap in caps:
            c_slug = str(cap).replace(".", "_")
            rel = f"property/nnn-vs-residential-{p_slug}-{c_slug}-cap.html"
            res = calc_property_comparison(price, commercial_cap_rate_pct=cap)
            title = f"{_usd(price)} Property: Commercial NNN ({cap:.1f}% Cap) vs Mortgaged Residential Cash Flow"
            desc = (
                f"Compare a {_usd(price)} leveraged residential rental ({_usd(res['res_net_cashflow_mo'])}/mo net cash flow) "
                f"against an outright Commercial NNN lease ({_usd(res['comm_net_cashflow_mo'])}/mo) and 10-year value ({_usd(res['future_value_10y'])})."
            )
            related = "".join(
                f'<a class="pill" href="nnn-vs-residential-{p // 1000}k-{c_slug}-cap.html">{_usd(p)} @ {cap:.1f}% Cap</a>'
                for p in prices if p != price
            )
            alert_cls = "danger" if res["res_net_cashflow_mo"] < 0 else "success"
            body = f"""
            <section class="hero">
              <span class="badge warn">Commercial NNN vs Residential Analysis • {market['updated_date']}</span>
              <h1>{html.escape(title)}</h1>
              <p class="muted">At 7.0% mortgage rates with 20% down ({_usd(res['down_payment'])}), a {_usd(price)} residential rental faces {_usd(res['mortgage_mo'])}/mo in debt service plus {_usd(res['res_expenses_mo'])}/mo in 1% maintenance &amp; 8% management fees — leaving <strong>{_usd(res['res_net_cashflow_mo'])}/mo</strong>. Meanwhile, an outright Commercial NNN lease at {cap:.1f}% cap rate yields <strong>+{_usd(res['comm_net_cashflow_mo'])}/mo</strong> with tenant-paid maintenance.</p>
              <a class="btn btn-sm" href="../apps/commercial-nnn-analyzer.html">Run Custom Numbers in PropYield Pro →</a>
            </section>

            <div class="alert {alert_cls}">
              <strong>Cash Flow Verdict:</strong> Residential Net = <strong>{_usd(res['res_net_cashflow_mo'])}/mo</strong> vs Commercial NNN Net = <strong>+{_usd(res['comm_net_cashflow_mo'])}/mo</strong> ({_usd(res['comm_net_cashflow_wk'])}/week).
            </div>

            <div class="kpi-grid">
              <div class="kpi"><div class="kpi-label">Residential Net / Mo</div><div class="kpi-val {'neg' if res['res_net_cashflow_mo'] < 0 else 'pos'}">{_usd(res['res_net_cashflow_mo'])}</div></div>
              <div class="kpi"><div class="kpi-label">Commercial NNN Net / Mo</div><div class="kpi-val pos">+{_usd(res['comm_net_cashflow_mo'])}</div></div>
              <div class="kpi"><div class="kpi-label">10-Yr Value (4.5%/yr)</div><div class="kpi-val acc">{_usd(res['future_value_10y'])}</div></div>
              <div class="kpi"><div class="kpi-label">10-Yr Equity Appreciation</div><div class="kpi-val pos">+{_usd(res['equity_gain_10y'])}</div></div>
            </div>

            {render_ad_slot(cfg, "property-seo")}

            <section class="card">
              <h3>Compare Other Property Price Tiers at {cap:.1f}% Cap Rate</h3>
              <div class="pill-list">{related}</div>
            </section>
            """
            pages.append((rel, title, render_page(cfg, rel, title, desc, body, market["updated_date"])))
    return pages


def build_pod_pages(cfg: SiteConfig, market: dict[str, Any]) -> list[tuple[str, str, str]]:
    """12 Copyright-Safe Public Domain POD Blueprint pages."""
    econ = calc_pod_economics(24.0, 30.0, 100.0)
    pages: list[tuple[str, str, str]] = []
    for item in PUBLIC_DOMAIN_CATALOG:
        rel = f"pod/{item.slug}-public-domain-pod-guide.html"
        title = f"{item.name} Public Domain POD Guide — Copyright-Safe Slogans, Etsy Tags & Margins"
        desc = (
            f"Sell {item.name} ({item.pd_year}) legally with Print-on-Demand on Gelato & Etsy. "
            f"Includes verified copyright scope, {len(item.slogans)} ready slogans, SEO tags, and $100/week margin math."
        )
        slogans_li = "".join(f"<li><strong>{html.escape(s)}</strong></li>" for s in item.slogans)
        tags_html = "".join(f'<span class="pill">{html.escape(t)}</span>' for t in item.etsy_tags)
        other_links = "".join(
            f'<a class="pill" href="{x.slug}-public-domain-pod-guide.html">{html.escape(x.name)}</a>'
            for x in PUBLIC_DOMAIN_CATALOG if x.slug != item.slug
        )
        body = f"""
        <section class="hero">
          <span class="badge green">Public Domain POD Blueprint • {html.escape(item.pd_year)}</span>
          <h1>{html.escape(item.name)} — Copyright-Safe Print-on-Demand Blueprint</h1>
          <p class="muted"><strong>Creator:</strong> {html.escape(item.creator)} | <strong>Public Domain Status:</strong> {html.escape(item.pd_year)}</p>
          <a class="btn green btn-sm" href="../apps/public-domain-pod-studio.html">Open Live SVG Mockup Generator for {html.escape(item.name)} →</a>
        </section>

        <div class="alert success"><strong>Safe Legal Scope:</strong> {html.escape(item.safe_scope)}</div>
        <div class="alert danger"><strong>Trademark &amp; Adaptation Warning:</strong> {html.escape(item.caution)}</div>

        <div class="kpi-grid">
          <div class="kpi"><div class="kpi-label">Avg POD Retail Price</div><div class="kpi-val">{_usd2(econ['retail_price'])}</div></div>
          <div class="kpi"><div class="kpi-label">Est. Profit / Sale (30%)</div><div class="kpi-val pos">{_usd2(econ['profit_per_sale'])}</div></div>
          <div class="kpi"><div class="kpi-label">Sales Needed for $100/Wk</div><div class="kpi-val acc">{econ['sales_per_week']} / week</div></div>
          <div class="kpi"><div class="kpi-label">Best Product Formats</div><div class="kpi-val" style="font-size:0.95rem">{html.escape(', '.join(item.best_products[:2]))}</div></div>
        </div>

        {render_ad_slot(cfg, "pod-seo")}

        <section class="card">
          <h2>Ready-to-Print Slogan Ideas for {html.escape(item.name)}</h2>
          <ul>{slogans_li}</ul>
          <h3 style="margin-top:16px">Etsy / Gelato SEO Tags</h3>
          <div class="pill-list">{tags_html}</div>
        </section>

        <section class="card">
          <h3>More Copyright-Safe Public Domain POD Niches</h3>
          <div class="pill-list">{other_links}</div>
        </section>
        """
        pages.append((rel, title, render_page(cfg, rel, title, desc, body, market["updated_date"])))
    return pages


def build_saas_pages(cfg: SiteConfig, market: dict[str, Any]) -> list[tuple[str, str, str]]:
    """20 B2B Micro-SaaS MRR & $100/Week Subscriber Calculator pages."""
    prices = [19, 29, 49, 79, 99]
    targets = [
        ("100-week", "$100/Week", 434),
        ("1000-month", "$1,000/Month", 1_000),
        ("5000-month", "$5,000/Month", 5_000),
        ("10000-month", "$10,000/Month", 10_000),
    ]
    pages: list[tuple[str, str, str]] = []

    for price in prices:
        for t_slug, t_label, t_mo in targets:
            rel = f"saas/micro-saas-{price}-mo-for-{t_slug}.html"
            m = calc_microsaas_mrr(price, t_mo, monthly_churn_pct=4.0)
            title = f"B2B Micro-SaaS at ${price}/Month: How Many Subscribers for {t_label}?"
            desc = (
                f"At ${price}/month, your Vibe-Coded B2B Micro-SaaS needs just {m['subs_needed']} paying business customers "
                f"to earn {t_label} (${m['actual_mrr']:,.0f} MRR / ${m['actual_arr']:,.0f} ARR)."
            )
            related = "".join(
                f'<a class="pill" href="micro-saas-{p}-mo-for-{t_slug}.html">${p}/mo → {t_label}</a>'
                for p in prices if p != price
            )
            body = f"""
            <section class="hero">
              <span class="badge">Vibe-Coded B2B Micro-SaaS Unit Economics • {market['updated_date']}</span>
              <h1>{html.escape(title)}</h1>
              <p class="muted">Instead of competing with Uber or MyFitnessPal, solving one painful B2B workflow (like driving instructor scheduling or niche contractor quoting) at <strong>${price}/month</strong> requires only <strong>{m['subs_needed']} paying businesses</strong> to hit <strong>{t_label}</strong>.</p>
              <a class="btn btn-sm" href="../apps/clutch-driving-instructor.html">Inspect Our Live Vibe-Coded B2B Demo (Clutch) →</a>
            </section>

            <div class="kpi-grid">
              <div class="kpi"><div class="kpi-label">Paying Subscribers Needed</div><div class="kpi-val acc">{m['subs_needed']}</div></div>
              <div class="kpi"><div class="kpi-label">Monthly Recurring Revenue</div><div class="kpi-val pos">{_usd(m['actual_mrr'])}/mo</div></div>
              <div class="kpi"><div class="kpi-label">Annualized Run Rate (ARR)</div><div class="kpi-val pos">{_usd(m['actual_arr'])}/yr</div></div>
              <div class="kpi"><div class="kpi-label">Customer LTV (4% Churn)</div><div class="kpi-val">{_usd(m['customer_ltv'])}</div></div>
            </div>

            {render_ad_slot(cfg, "saas-seo")}

            <section class="card">
              <h2>Churn Sensitivity Table at ${price}/month</h2>
              <table>
                <thead><tr><th>Monthly Churn</th><th>Avg Customer Lifetime</th><th>Customer LTV</th><th>New Signups/Mo to Hold {m['subs_needed']} Users</th></tr></thead>
                <tbody>
                  <tr><td>2% (Sticky B2B Workflow)</td><td>50.0 months</td><td>{_usd(price * 50)}</td><td>{max(1, round(m['subs_needed'] * 0.02))}</td></tr>
                  <tr><td>4% (Healthy SMB SaaS)</td><td>25.0 months</td><td>{_usd(price * 25)}</td><td>{max(1, round(m['subs_needed'] * 0.04))}</td></tr>
                  <tr><td>8% (High Churn Consumer)</td><td>12.5 months</td><td>{_usd(price * 12.5)}</td><td>{max(1, round(m['subs_needed'] * 0.08))}</td></tr>
                </tbody>
              </table>
            </section>

            <section class="card">
              <h3>Compare Other Price Points for {t_label}</h3>
              <div class="pill-list">{related}</div>
            </section>
            """
            pages.append((rel, title, render_page(cfg, rel, title, desc, body, market["updated_date"])))
    return pages


def build_core_pages(
    cfg: SiteConfig,
    market: dict[str, Any],
    hysa_pages: list[tuple[str, str, str]],
    div_pages: list[tuple[str, str, str]],
    prop_pages: list[tuple[str, str, str]],
    pod_pages: list[tuple[str, str, str]],
    saas_pages: list[tuple[str, str, str]],
) -> list[tuple[str, str]]:
    """Build index.html, about.html, privacy.html, disclaimer.html, terms.html."""
    total_pages = 4 + len(hysa_pages) + len(div_pages) + len(prop_pages) + len(pod_pages) + len(saas_pages) + 5

    hysa_links = "".join(f'<a class="pill" href="{rel}">{html.escape(t.split("(")[0].strip())}</a>' for rel, t, _ in hysa_pages[:8])
    div_links = "".join(f'<a class="pill" href="{rel}">{html.escape(t.split("(")[0].strip())}</a>' for rel, t, _ in div_pages[:8])
    prop_links = "".join(f'<a class="pill" href="{rel}">{html.escape(t.split(":")[0])} ({rel.split("-")[-2].replace("_",".")}% Cap)</a>' for rel, t, _ in prop_pages[:8])
    pod_links = "".join(f'<a class="pill" href="{rel}">{html.escape(t.split("—")[0].strip())}</a>' for rel, t, _ in pod_pages)
    saas_links = "".join(f'<a class="pill" href="{rel}">{html.escape(t.split(":")[0])} → {rel.split("-for-")[1].replace(".html","")}</a>' for rel, t, _ in saas_pages[:8])

    index_body = f"""
    <section class="hero">
      <span class="badge green">Live Auto-Synced Suite ({market['updated_date']}) • {total_pages} Free Tools &amp; Blueprints</span>
      <h1>WealthStack Studio — 2027 Passive Income Calculators &amp; Free B2B Micro-SaaS Apps</h1>
      <p class="muted">Zero sign-up, zero subscription fees. Use our 4 full browser-based Vibe-Coded web apps and 100+ data-backed calculators covering High-Yield Savings (HYSA), Global Dividend ETFs, Commercial NNN Real Estate, Copyright-Safe Public Domain POD, and B2B Micro-SaaS economics.</p>
      <div class="kpi-grid">
        <div class="kpi"><div class="kpi-label">US Top HYSA Benchmark</div><div class="kpi-val pos">4.20% APY</div></div>
        <div class="kpi"><div class="kpi-label">Global Dividend ETF</div><div class="kpi-val acc">2.97% Yield</div></div>
        <div class="kpi"><div class="kpi-label">Live USD/GBP Rate</div><div class="kpi-val">{market['fx_rates']['GBP']:.4f}</div></div>
        <div class="kpi"><div class="kpi-label">Live USD/KRW Rate</div><div class="kpi-val">{market['fx_rates']['KRW']:,.0f}</div></div>
      </div>
    </section>

    <section class="card">
      <h2>4 Interactive Vibe-Coded B2B &amp; Investor Web Apps (Free Forever)</h2>
      <div class="grid">
        <div class="card" style="margin:0;background:var(--surface-2)">
          <span class="badge green">B2B Micro-SaaS</span>
          <h3>Clutch — Driving Instructor Manager</h3>
          <p class="muted">Manage 30+ learners, skill checklists, lesson calendar bookings, and printable progress reports offline.</p>
          <a class="btn btn-sm" href="apps/clutch-driving-instructor.html">Launch Clutch App →</a>
        </div>
        <div class="card" style="margin:0;background:var(--surface-2)">
          <span class="badge warn">Real Estate</span>
          <h3>PropYield Pro — NNN vs Residential</h3>
          <p class="muted">Detect negative cash flow traps in mortgaged rentals vs tenant-maintained Commercial NNN leases.</p>
          <a class="btn btn-sm" href="apps/commercial-nnn-analyzer.html">Launch PropYield Pro →</a>
        </div>
        <div class="card" style="margin:0;background:var(--surface-2)">
          <span class="badge">HYSA + Dividends</span>
          <h3>DiviFlow — $100/Week Goal Planner</h3>
          <p class="muted">Reverse-calculate exact capital for $100/wk to $1,000/day with DRIP compounding &amp; FDIC/FSCS checks.</p>
          <a class="btn btn-sm" href="apps/passive-income-planner.html">Launch DiviFlow →</a>
        </div>
        <div class="card" style="margin:0;background:var(--surface-2)">
          <span class="badge green">AI POD Studio</span>
          <h3>PD-POD — Public Domain Print Studio</h3>
          <p class="muted">Generate copyright-safe SVG designs, Etsy SEO tags, and 30% margin targets from 12 Public Domain classics.</p>
          <a class="btn btn-sm" href="apps/public-domain-pod-studio.html">Launch PD-POD Studio →</a>
        </div>
      </div>
    </section>

    {render_ad_slot(cfg, "home-mid")}

    <section class="card">
      <h2>High-Yield Savings (HYSA) Interest Calculators (24 Scenarios)</h2>
      <div class="pill-list">{hysa_links}</div>
    </section>

    <section class="card">
      <h2>Dividend ETF Passive Income Reverse Calculators (24 Scenarios)</h2>
      <div class="pill-list">{div_links}</div>
    </section>

    <section class="card">
      <h2>Commercial NNN vs Residential Cash Flow Comparisons (24 Scenarios)</h2>
      <div class="pill-list">{prop_links}</div>
    </section>

    <section class="card">
      <h2>Copyright-Safe Public Domain POD Blueprints (12 Niches)</h2>
      <div class="pill-list">{pod_links}</div>
    </section>

    <section class="card">
      <h2>B2B Micro-SaaS MRR &amp; Subscriber Calculators (20 Scenarios)</h2>
      <div class="pill-list">{saas_links}</div>
    </section>
    """

    about_body = f"""
    <section class="card">
      <h1>About WealthStack Studio</h1>
      <p>WealthStack Studio is an automated open-access suite of financial calculators, public-domain Print-on-Demand generators, and client-side B2B micro-applications built to help independent operators and investors model realistic passive income unit economics.</p>
      <p>Exchange rates are refreshed daily via the European Central Bank / Frankfurter open data feed ({market['fx_date']}). All interactive B2B tools store user records exclusively in your local browser storage for maximum privacy.</p>
    </section>
    """

    privacy_body = f"""
    <section class="card">
      <h1>Privacy Policy</h1>
      <p><strong>Local-First Data Storage:</strong> Our interactive tools (including Clutch Driving Instructor Manager) save your entries solely in your browser's <code>localStorage</code>. We do not transmit or store your student lists, financial inputs, or personal records on external servers.</p>
      <p><strong>Advertising &amp; Cookies:</strong> This site uses Google AdSense (<code>{html.escape(cfg.adsense_client_id)}</code>) to serve relevant advertisements. Third-party vendors, including Google, use cookies to serve ads based on prior visits. You may opt out of personalized advertising via Google Ad Settings.</p>
      <p>Contact: {html.escape(cfg.contact_email)}</p>
    </section>
    """

    disclaimer_body = """
    <section class="card">
      <h1>Financial &amp; Legal Disclaimer</h1>
      <p>All calculators, cash-flow models, dividend projections, and Public Domain POD checklists on WealthStack Studio are provided strictly for educational and illustrative purposes. Nothing on this website constitutes regulated financial, investment, tax, or legal advice.</p>
      <p>When investing in stocks, ETFs, or real estate, your capital is at risk and past performance does not guarantee future returns. For Print-on-Demand sellers, always verify active trademarks separately from expired copyrights before listing products on commercial marketplaces.</p>
    </section>
    """

    terms_body = """
    <section class="card">
      <h1>Terms of Use</h1>
      <p>All web apps and calculators on WealthStack Studio are provided "as is" without warranty of any kind. Users are solely responsible for backing up local browser data using the provided JSON export controls and independently verifying financial or legal calculations before making decisions.</p>
    </section>
    """

    return [
        ("index.html", render_page(cfg, "index.html", "Free AI Micro-SaaS Apps & 2027 Passive Income Calculators", "113+ free browser-based B2B micro-SaaS tools, HYSA, Dividend ETF, Commercial NNN real estate, and Public Domain POD calculators.", index_body, market["updated_date"])),
        ("about.html", render_page(cfg, "about.html", "About WealthStack Studio", "About our automated financial calculators and client-side B2B Micro-SaaS tools.", about_body, market["updated_date"])),
        ("privacy.html", render_page(cfg, "privacy.html", "Privacy Policy", "Privacy policy covering local-first browser storage and Google AdSense disclosures.", privacy_body, market["updated_date"])),
        ("disclaimer.html", render_page(cfg, "disclaimer.html", "Financial & Legal Disclaimer", "Educational disclaimer for passive income calculators and Public Domain POD guides.", disclaimer_body, market["updated_date"])),
        ("terms.html", render_page(cfg, "terms.html", "Terms of Use", "Terms of use for WealthStack Studio free web applications.", terms_body, market["updated_date"])),
    ]
