"""Builds 4 interactive, zero-backend Vibe-Coded B2B Micro-SaaS web apps."""
from __future__ import annotations

import json
from typing import Any

from .config import SiteConfig
from .public_domain_db import PUBLIC_DOMAIN_CATALOG
from .templates import render_ad_slot, render_page


def build_clutch_app(cfg: SiteConfig, market: dict[str, Any]) -> tuple[str, str]:
    rel = "apps/clutch-driving-instructor.html"
    title = "Clutch — Free Driving Instructor Student & Lesson Manager App"
    desc = (
        "Free browser-based B2B management app for independent driving instructors. "
        "Track 30+ learners, lesson bookings, skill checklists, payments, and print progress reports offline."
    )
    body = f"""
    <section class="hero">
      <span class="badge green">Vibe-Coded B2B Micro-SaaS • 100% Free &amp; Offline-Ready</span>
      <h1>Clutch — Driving Instructor &amp; Learner Manager</h1>
      <p class="muted">Manage active learners, lesson bookings, skill readiness toggles, and monthly revenue directly in your browser. All data saves automatically to your device with 1-click JSON backup and printable student progress sheets.</p>
      <div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:14px" class="no-print">
        <button class="btn" type="button" onclick="exportClutchJSON()">Export Backup (JSON)</button>
        <button class="btn secondary" type="button" onclick="document.getElementById('importFile').click()">Import Backup</button>
        <input id="importFile" type="file" accept=".json" style="display:none" onchange="importClutchJSON(event)">
        <button class="btn secondary" type="button" onclick="window.print()">Print Progress Report</button>
        <button class="btn secondary" type="button" onclick="resetDemoData()">Load Demo Students</button>
      </div>
    </section>

    <div class="kpi-grid">
      <div class="kpi"><div class="kpi-label">Active Learners</div><div class="kpi-val acc" id="kpiStudents">0</div></div>
      <div class="kpi"><div class="kpi-label">Upcoming Lessons</div><div class="kpi-val" id="kpiLessons">0</div></div>
      <div class="kpi"><div class="kpi-label">Avg Test Readiness</div><div class="kpi-val pos" id="kpiReady">0%</div></div>
      <div class="kpi"><div class="kpi-label">Logged Lesson Revenue</div><div class="kpi-val pos" id="kpiRev">$0</div></div>
    </div>

    {render_ad_slot(cfg, "clutch-top")}

    <div class="grid-2">
      <section class="card no-print">
        <h2>Add New Learner</h2>
        <form id="studentForm" onsubmit="addStudent(event)">
          <label>Learner Full Name<input id="sName" required placeholder="e.g. Alex Carter"></label>
          <label>Phone / Contact<input id="sPhone" placeholder="e.g. +1 555-0192"></label>
          <label>Hourly Lesson Rate (USD)<input id="sRate" type="number" min="10" step="1" value="65"></label>
          <label>Target Driving Test Date<input id="sTestDate" type="date"></label>
          <button class="btn green" type="submit">Add Learner</button>
        </form>
      </section>

      <section class="card no-print">
        <h2>Book a Lesson (Calendar)</h2>
        <form id="lessonForm" onsubmit="bookLesson(event)">
          <label>Select Learner<select id="lStudent" required></select></label>
          <label>Lesson Date &amp; Time<input id="lDateTime" type="datetime-local" required></label>
          <label>Duration (Hours)<input id="lHours" type="number" min="0.5" max="4" step="0.5" value="2"></label>
          <label>Focus Topic<input id="lTopic" placeholder="e.g. Parallel parking &amp; highway merge"></label>
          <button class="btn" type="submit">Schedule Lesson</button>
        </form>
      </section>
    </div>

    <section class="card">
      <h2>Active Learners &amp; Skill Mastery Toggles</h2>
      <p class="muted">Click any skill badge to toggle mastery status. Progress updates automatically for test-day readiness.</p>
      <div id="studentList"></div>
    </section>

    <section class="card">
      <h2>Scheduled Lessons Calendar</h2>
      <div style="overflow-x:auto">
        <table>
          <thead><tr><th>Date &amp; Time</th><th>Learner</th><th>Hours</th><th>Focus</th><th>Fee</th><th class="no-print">Action</th></tr></thead>
          <tbody id="lessonTable"></tbody>
        </table>
      </div>
    </section>

    {render_ad_slot(cfg, "clutch-bottom")}

    <section class="card faq">
      <h2>Why Independent Driving Instructors Use Clutch</h2>
      <details open><summary>Does Clutch require a $29/month subscription?</summary><p>No. Clutch runs 100% client-side in your browser using LocalStorage, so there are zero server fees, no account sign-up, and full data privacy on your own device.</p></details>
      <details><summary>How do I move my student roster to another laptop or phone?</summary><p>Click <strong>Export Backup (JSON)</strong> at the top of the page and import that file on your other device anytime.</p></details>
    </section>

    <script>
    const SKILLS = ["Controls", "City Traffic", "Parallel Park", "Highway", "Mock Test"];
    const STORAGE_KEY = "wealthstack_clutch_v1";

    function defaultState() {{
      return {{
        students: [
          {{ id: "st1", name: "Maya Lin", phone: "555-0148", rate: 65, testDate: "2027-01-18", skills: [true, true, true, false, false] }},
          {{ id: "st2", name: "Daniel Brooks", phone: "555-0194", rate: 70, testDate: "2027-02-05", skills: [true, true, true, true, false] }},
          {{ id: "st3", name: "Sofia Patel", phone: "555-0123", rate: 65, testDate: "2027-02-22", skills: [true, false, false, false, false] }}
        ],
        lessons: [
          {{ id: "ls1", studentId: "st1", dt: "2026-11-24T10:00", hours: 2, topic: "Parallel parking &amp; hill starts", fee: 130 }},
          {{ id: "ls2", studentId: "st2", dt: "2026-11-25T14:30", hours: 1.5, topic: "Full 45-min mock exam route", fee: 105 }}
        ]
      }};
    }}

    let state = (() => {{
      try {{
        const raw = localStorage.getItem(STORAGE_KEY);
        if (raw) return JSON.parse(raw);
      }} catch (e) {{}}
      return defaultState();
    }})();

    function save() {{
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
      render();
    }}

    function addStudent(e) {{
      e.preventDefault();
      state.students.push({{
        id: "st" + Date.now(),
        name: document.getElementById("sName").value.trim(),
        phone: document.getElementById("sPhone").value.trim(),
        rate: Number(document.getElementById("sRate").value) || 65,
        testDate: document.getElementById("sTestDate").value || "TBD",
        skills: [false, false, false, false, false]
      }});
      e.target.reset();
      document.getElementById("sRate").value = 65;
      save();
    }}

    function toggleSkill(sid, idx) {{
      const s = state.students.find(x => x.id === sid);
      if (!s) return;
      s.skills[idx] = !s.skills[idx];
      save();
    }}

    function removeStudent(sid) {{
      state.students = state.students.filter(x => x.id !== sid);
      state.lessons = state.lessons.filter(x => x.studentId !== sid);
      save();
    }}

    function bookLesson(e) {{
      e.preventDefault();
      const sid = document.getElementById("lStudent").value;
      const st = state.students.find(x => x.id === sid);
      if (!st) return;
      const hours = Number(document.getElementById("lHours").value) || 1;
      state.lessons.push({{
        id: "ls" + Date.now(),
        studentId: sid,
        dt: document.getElementById("lDateTime").value,
        hours,
        topic: document.getElementById("lTopic").value.trim() || "General driving practice",
        fee: Math.round(hours * st.rate * 100) / 100
      }});
      e.target.reset();
      document.getElementById("lHours").value = 2;
      save();
    }}

    function removeLesson(lid) {{
      state.lessons = state.lessons.filter(x => x.id !== lid);
      save();
    }}

    function exportClutchJSON() {{
      const blob = new Blob([JSON.stringify(state, null, 2)], {{ type: "application/json" }});
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "clutch-instructor-backup.json";
      a.click();
    }}

    function importClutchJSON(e) {{
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => {{
        try {{
          const parsed = JSON.parse(reader.result);
          if (Array.isArray(parsed.students) && Array.isArray(parsed.lessons)) {{
            state = parsed;
            save();
          }}
        }} catch (err) {{ alert("Invalid backup JSON file."); }}
      }};
      reader.readAsText(file);
    }}

    function resetDemoData() {{
      state = defaultState();
      save();
    }}

    function render() {{
      const sel = document.getElementById("lStudent");
      sel.innerHTML = state.students.map(s => `<option value="${{s.id}}">${{s.name}} ($${{s.rate}}/hr)</option>`).join("");

      const totalReady = state.students.length
        ? Math.round(state.students.reduce((acc, s) => acc + (s.skills.filter(Boolean).length / SKILLS.length) * 100, 0) / state.students.length)
        : 0;
      const totalRev = state.lessons.reduce((acc, l) => acc + Number(l.fee || 0), 0);

      document.getElementById("kpiStudents").textContent = state.students.length;
      document.getElementById("kpiLessons").textContent = state.lessons.length;
      document.getElementById("kpiReady").textContent = totalReady + "%";
      document.getElementById("kpiRev").textContent = "$" + totalRev.toLocaleString();

      const list = document.getElementById("studentList");
      list.innerHTML = state.students.map(s => {{
        const pct = Math.round((s.skills.filter(Boolean).length / SKILLS.length) * 100);
        const badges = SKILLS.map((label, i) => `
          <button type="button" class="btn btn-sm ${{s.skills[i] ? 'green' : 'secondary'}}" onclick="toggleSkill('${{s.id}}', ${{i}})">
            ${{s.skills[i] ? '✓ ' : ''}}${{label}}
          </button>
        `).join(" ");
        return `
          <div style="border:1px solid var(--border);border-radius:12px;padding:14px;margin-bottom:12px;background:var(--surface-2)">
            <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;align-items:center">
              <div><strong>${{s.name}}</strong> <span class="muted">(${{s.phone || 'No phone'}} • $${{s.rate}}/hr • Test: ${{s.testDate}})</span></div>
              <div><span class="badge green">${{pct}}% Ready</span> <button class="btn danger btn-sm no-print" onclick="removeStudent('${{s.id}}')">Remove</button></div>
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:10px">${{badges}}</div>
          </div>
        `;
      }}).join("") || '<p class="muted">No learners yet. Add your first learner above.</p>';

      const tbody = document.getElementById("lessonTable");
      const sorted = [...state.lessons].sort((a, b) => (a.dt || "").localeCompare(b.dt || ""));
      tbody.innerHTML = sorted.map(l => {{
        const st = state.students.find(x => x.id === l.studentId);
        return `<tr>
          <td>${{(l.dt || "").replace("T", " ")}}</td>
          <td>${{st ? st.name : "Unknown"}}</td>
          <td>${{l.hours}}h</td>
          <td>${{l.topic}}</td>
          <td>$${{Number(l.fee).toLocaleString()}}</td>
          <td class="no-print"><button class="btn danger btn-sm" onclick="removeLesson('${{l.id}}')">Delete</button></td>
        </tr>`;
      }}).join("") || '<tr><td colspan="6" class="muted">No lessons scheduled yet.</td></tr>';
    }}
    render();
    </script>
    """
    ld = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Clutch Driving Instructor Manager",
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web Browser",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
    }
    return rel, render_page(cfg, rel, title, desc, body, market["updated_date"], json_ld=ld)


def build_property_app(cfg: SiteConfig, market: dict[str, Any]) -> tuple[str, str]:
    rel = "apps/commercial-nnn-analyzer.html"
    title = "PropYield Pro — Commercial NNN vs Residential Rental Cash Flow Analyzer"
    desc = (
        "Compare leveraged residential rental cash flow (with mortgage, 1% maintenance & 8% management fees) "
        "against outright Commercial NNN leases and 10-year property appreciation."
    )
    body = f"""
    <section class="hero">
      <span class="badge warn">Real Estate Cash Flow &amp; NNN Lease Engine</span>
      <h1>PropYield Pro — Commercial NNN vs Residential Rental Analyzer</h1>
      <p class="muted">Most beginner landlords buy an average residential home and accidentally end up with negative monthly cash flow after 1% maintenance and 8% management fees. Compare side-by-side against a tenant-maintained Commercial NNN unit.</p>
      <button class="btn secondary btn-sm no-print" type="button" onclick="window.print()">Print Investor Report (PDF)</button>
    </section>

    <div class="grid-2">
      <section class="card">
        <h2>Residential Rental Inputs</h2>
        <label>Property Purchase Price ($)<input id="pPrice" type="number" value="370000" step="5000" oninput="calcProp()"></label>
        <label>Down Payment (%)<input id="pDown" type="number" value="20" step="1" oninput="calcProp()"></label>
        <label>30-Yr Mortgage Interest Rate (%)<input id="pRate" type="number" value="7.0" step="0.1" oninput="calcProp()"></label>
        <label>Monthly Gross Rent ($)<input id="pRent" type="number" value="2289" step="50" oninput="calcProp()"></label>
        <label>Annual Maintenance (% of value) + Management (% of rent)<div style="display:flex;gap:8px"><input id="pMaint" type="number" value="1.0" step="0.1" oninput="calcProp()"><input id="pMgmt" type="number" value="8.0" step="0.5" oninput="calcProp()"></div></label>
      </section>

      <section class="card">
        <h2>Commercial NNN Unit Inputs</h2>
        <label>Commercial Unit Cash Purchase Price ($)<input id="cPrice" type="number" value="200000" step="5000" oninput="calcProp()"></label>
        <label>Monthly NNN Rent ($ — Tenant pays repairs/maintenance)<input id="cRent" type="number" value="1850" step="50" oninput="calcProp()"></label>
        <label>Annual Property Appreciation Assumption (%)<input id="pApprec" type="number" value="4.5" step="0.1" oninput="calcProp()"></label>
        <label>Holding Horizon (Years)<input id="pYears" type="number" value="10" min="1" max="30" oninput="calcProp()"></label>
        <div id="propAlert" class="alert"></div>
      </section>
    </div>

    <div class="kpi-grid">
      <div class="kpi"><div class="kpi-label">Residential Mortgage / Mo</div><div class="kpi-val" id="oMort">$0</div></div>
      <div class="kpi"><div class="kpi-label">Residential Net Cash Flow / Mo</div><div class="kpi-val" id="oResNet">$0</div></div>
      <div class="kpi"><div class="kpi-label">Commercial NNN Net / Mo</div><div class="kpi-val pos" id="oCommNet">$0</div></div>
      <div class="kpi"><div class="kpi-label">Commercial Cap Rate (Yield)</div><div class="kpi-val acc" id="oCap">0%</div></div>
      <div class="kpi"><div class="kpi-label">Residential Value in N Yrs</div><div class="kpi-val" id="oResVal">$0</div></div>
      <div class="kpi"><div class="kpi-label">Commercial Value in N Yrs</div><div class="kpi-val pos" id="oCommVal">$0</div></div>
    </div>

    {render_ad_slot(cfg, "property-mid")}

    <section class="card">
      <h2>Side-by-Side Breakdown</h2>
      <table>
        <thead><tr><th>Metric</th><th>Residential (Mortgaged)</th><th>Commercial NNN (Outright)</th></tr></thead>
        <tbody id="propTable"></tbody>
      </table>
    </section>

    <script>
    function fmt(n) {{
      const sign = n < 0 ? "-" : "";
      return sign + "$" + Math.abs(Math.round(n)).toLocaleString();
    }}
    function calcProp() {{
      const price = Number(document.getElementById("pPrice").value) || 0;
      const downPct = Number(document.getElementById("pDown").value) || 0;
      const rate = Number(document.getElementById("pRate").value) || 0;
      const rent = Number(document.getElementById("pRent").value) || 0;
      const maintPct = Number(document.getElementById("pMaint").value) || 0;
      const mgmtPct = Number(document.getElementById("pMgmt").value) || 0;

      const cPrice = Number(document.getElementById("cPrice").value) || 1;
      const cRent = Number(document.getElementById("cRent").value) || 0;
      const apprec = Number(document.getElementById("pApprec").value) || 0;
      const yrs = Number(document.getElementById("pYears").value) || 10;

      const downAmt = price * (downPct / 100);
      const loan = Math.max(0, price - downAmt);
      const r = (rate / 100) / 12;
      const n = 360;
      const mort = loan > 0 ? (r === 0 ? loan / n : loan * (r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1)) : 0;
      const maintMo = (price * (maintPct / 100)) / 12;
      const mgmtMo = rent * (mgmtPct / 100);
      const resNet = rent - mort - maintMo - mgmtMo;

      const commNet = cRent;
      const capRate = (cRent * 12 / cPrice) * 100;
      const resFuture = price * Math.pow(1 + apprec / 100, yrs);
      const commFuture = cPrice * Math.pow(1 + apprec / 100, yrs);

      document.getElementById("oMort").textContent = fmt(mort);
      const resEl = document.getElementById("oResNet");
      resEl.textContent = fmt(resNet);
      resEl.className = "kpi-val " + (resNet >= 0 ? "pos" : "neg");
      document.getElementById("oCommNet").textContent = fmt(commNet);
      document.getElementById("oCap").textContent = capRate.toFixed(2) + "%";
      document.getElementById("oResVal").textContent = fmt(resFuture);
      document.getElementById("oCommVal").textContent = fmt(commFuture);

      const alertEl = document.getElementById("propAlert");
      if (resNet < 0) {{
        alertEl.className = "alert danger";
        alertEl.innerHTML = `<strong>Negative Cash Flow Warning:</strong> This residential rental loses <strong>${{fmt(resNet)}}/month</strong> before vacancies or major capex, whereas the NNN commercial unit nets <strong>+${{fmt(commNet)}}/month</strong> (${{capRate.toFixed(1)}}% annual yield).`;
      }} else {{
        alertEl.className = "alert success";
        alertEl.innerHTML = `<strong>Positive Cash Flow:</strong> Residential nets <strong>+${{fmt(resNet)}}/mo</strong>. Commercial NNN nets <strong>+${{fmt(commNet)}}/mo</strong> with zero landlord maintenance overhead.`;
      }}

      document.getElementById("propTable").innerHTML = `
        <tr><td>Upfront Cash Required</td><td>${{fmt(downAmt)}}</td><td>${{fmt(cPrice)}}</td></tr>
        <tr><td>Monthly Gross Rent</td><td>${{fmt(rent)}}</td><td>${{fmt(cRent)}}</td></tr>
        <tr><td>Monthly Mortgage Payment</td><td>-${{fmt(mort)}}</td><td>$0</td></tr>
        <tr><td>Maintenance &amp; Management / Mo</td><td>-${{fmt(maintMo + mgmtMo)}}</td><td>$0 (Tenant NNN)</td></tr>
        <tr><td><strong>Net Monthly Passive Cash Flow</strong></td><td><strong>${{fmt(resNet)}}</strong></td><td><strong>${{fmt(commNet)}}</strong></td></tr>
        <tr><td>Projected Value After ${{yrs}} Years (${{apprec}}%/yr)</td><td>${{fmt(resFuture)}}</td><td>${{fmt(commFuture)}}</td></tr>
      `;
    }}
    calcProp();
    </script>
    """
    ld = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "PropYield Pro Commercial NNN Analyzer",
        "applicationCategory": "FinanceApplication",
        "operatingSystem": "Web Browser",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
    }
    return rel, render_page(cfg, rel, title, desc, body, market["updated_date"], json_ld=ld)


def build_passive_income_app(cfg: SiteConfig, market: dict[str, Any]) -> tuple[str, str]:
    rel = "apps/passive-income-planner.html"
    title = "DiviFlow — HYSA & Dividend ETF $100/Week Passive Income Goal Planner"
    desc = (
        "Calculate exact capital needed for $100/week to $1,000/day passive income using High-Yield Savings (4.2% APY) "
        "vs Global Dividend ETFs (2.97%+), with live USD/GBP/EUR/KRW conversion and FDIC/FSCS checks."
    )
    fx_json = json.dumps(market["fx_rates"])
    body = f"""
    <section class="hero">
      <span class="badge">Live ECB/Frankfurter FX ({market['fx_date']}) • HYSA + Dividend ETF</span>
      <h1>DiviFlow — Passive Income &amp; DRIP Goal Planner</h1>
      <p class="muted">Compare how much capital you need in a High-Yield Savings Account (4.2% APY) vs a Dividend ETF (e.g., Vanguard FTSE All-World at 2.97% yield), and simulate monthly DRIP compounding in USD, GBP, EUR, or KRW.</p>
    </section>

    <div class="grid-2">
      <section class="card">
        <h2>1. Target Passive Income Reverse Calculator</h2>
        <label>Display Currency
          <select id="dCur" onchange="calcDivi()">
            <option value="USD">USD ($)</option>
            <option value="GBP">GBP (£)</option>
            <option value="EUR">EUR (€)</option>
            <option value="KRW">KRW (₩)</option>
          </select>
        </label>
        <label>Target Weekly Passive Income (in USD equivalent)<input id="dWeekly" type="number" value="100" step="25" oninput="calcDivi()"></label>
        <label>High-Yield Savings APY (%)<input id="dHysa" type="number" value="4.20" step="0.1" oninput="calcDivi()"></label>
        <label>Dividend ETF Yield (%)<input id="dYield" type="number" value="2.97" step="0.1" oninput="calcDivi()"></label>
        <div id="fdicAlert" class="alert"></div>
      </section>

      <section class="card">
        <h2>2. Monthly DRIP Compounding Simulator</h2>
        <label>Starting Investment (USD)<input id="dInit" type="number" value="10000" step="1000" oninput="calcDivi()"></label>
        <label>Monthly Auto-Invest Contribution (USD)<input id="dMonthly" type="number" value="500" step="50" oninput="calcDivi()"></label>
        <label>Expected Price Growth (%/yr, excluding dividend)<input id="dGrowth" type="number" value="4.5" step="0.5" oninput="calcDivi()"></label>
        <label>Investment Horizon (Years)<input id="dYears" type="number" value="15" min="1" max="40" oninput="calcDivi()"></label>
      </section>
    </div>

    <div class="kpi-grid">
      <div class="kpi"><div class="kpi-label">HYSA Capital Needed</div><div class="kpi-val acc" id="kHysaCap">$0</div></div>
      <div class="kpi"><div class="kpi-label">Dividend ETF Capital Needed</div><div class="kpi-val" id="kDivCap">$0</div></div>
      <div class="kpi"><div class="kpi-label">1-Yr Extra vs 0.38% Bank</div><div class="kpi-val pos" id="kExtra">$0</div></div>
      <div class="kpi"><div class="kpi-label">DRIP Portfolio After N Yrs</div><div class="kpi-val pos" id="kDripBal">$0</div></div>
      <div class="kpi"><div class="kpi-label">Future Weekly Dividend</div><div class="kpi-val pos" id="kDripWk">$0</div></div>
    </div>

    {render_ad_slot(cfg, "diviflow-mid")}

    <section class="card">
      <h2>Quick Benchmark Scenarios</h2>
      <div class="pill-list">
        <button class="btn secondary btn-sm" onclick="setWeekly(100)">$100/week ($5,200/yr)</button>
        <button class="btn secondary btn-sm" onclick="setWeekly(250)">$250/week ($13,000/yr)</button>
        <button class="btn secondary btn-sm" onclick="setWeekly(500)">$500/week ($26,000/yr)</button>
        <button class="btn secondary btn-sm" onclick="setWeekly(1000)">$1,000/week ($52,000/yr)</button>
        <button class="btn secondary btn-sm" onclick="setWeekly(7000)">$1,000/day ($365,000/yr)</button>
      </div>
    </section>

    <script>
    const FX = {fx_json};
    const SYM = {{ USD: "$", GBP: "£", EUR: "€", KRW: "₩" }};
    function setWeekly(w) {{ document.getElementById("dWeekly").value = w; calcDivi(); }}
    function fmtC(usdVal, cur) {{
      const val = usdVal * (FX[cur] || 1);
      return SYM[cur] + Math.round(val).toLocaleString();
    }}
    function calcDivi() {{
      const cur = document.getElementById("dCur").value;
      const wk = Number(document.getElementById("dWeekly").value) || 0;
      const hysa = Number(document.getElementById("dHysa").value) || 0.01;
      const dy = Number(document.getElementById("dYield").value) || 0.01;
      const init = Number(document.getElementById("dInit").value) || 0;
      const mo = Number(document.getElementById("dMonthly").value) || 0;
      const growth = Number(document.getElementById("dGrowth").value) || 0;
      const yrs = Number(document.getElementById("dYears").value) || 10;

      const annual = wk * 52;
      const hysaCap = annual / (hysa / 100);
      const divCap = annual / (dy / 100);
      const extraOnInit = init * ((hysa - 0.38) / 100);

      let bal = init;
      const mRate = ((dy + growth) / 100) / 12;
      for (let i = 0; i < yrs * 12; i++) {{ bal = bal * (1 + mRate) + mo; }}
      const futWk = (bal * (dy / 100)) / 52;

      document.getElementById("kHysaCap").textContent = fmtC(hysaCap, cur);
      document.getElementById("kDivCap").textContent = fmtC(divCap, cur);
      document.getElementById("kExtra").textContent = "+" + fmtC(extraOnInit, cur);
      document.getElementById("kDripBal").textContent = fmtC(bal, cur);
      document.getElementById("kDripWk").textContent = fmtC(futWk, cur) + "/wk";

      const al = document.getElementById("fdicAlert");
      if (hysaCap > 250000) {{
        al.className = "alert danger";
        al.innerHTML = `<strong>Deposit Protection Note:</strong> Required HYSA capital (${{fmtC(hysaCap, cur)}}) exceeds the US FDIC $250,000 per-bank limit (UK FSCS: £120,000). Split deposits across multiple insured institutions.`;
      }} else {{
        al.className = "alert success";
        al.innerHTML = `<strong>Protected Range:</strong> Required HYSA capital (${{fmtC(hysaCap, cur)}}) fits within the standard US FDIC $250,000 deposit insurance limit.`;
      }}
    }}
    calcDivi();
    </script>
    """
    ld = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "DiviFlow Passive Income Planner",
        "applicationCategory": "FinanceApplication",
        "operatingSystem": "Web Browser",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
    }
    return rel, render_page(cfg, rel, title, desc, body, market["updated_date"], json_ld=ld)


def build_pod_studio_app(cfg: SiteConfig, market: dict[str, Any]) -> tuple[str, str]:
    rel = "apps/public-domain-pod-studio.html"
    title = "PD-POD Studio — Copyright-Safe Public Domain POD Slogan, SVG Mockup & Margin Tool"
    desc = (
        "Build copyright-safe Print-on-Demand t-shirts & posters using verified Public Domain characters "
        "(Sherlock Holmes, Alice, Dracula, Steamboat Willie, Popeye 1929). Live SVG mockup download + Gelato/Etsy margin calculator."
    )
    catalog_json = json.dumps(
        [
            {
                "slug": item.slug,
                "name": item.name,
                "creator": item.creator,
                "pd_year": item.pd_year,
                "safe_scope": item.safe_scope,
                "caution": item.caution,
                "slogans": list(item.slogans),
                "tags": list(item.etsy_tags),
                "accent": item.accent_color,
                "motif": item.motif_label,
            }
            for item in PUBLIC_DOMAIN_CATALOG
        ],
        ensure_ascii=False,
    )
    body = f"""
    <section class="hero">
      <span class="badge green">Copyright-Safe Public Domain POD Generator</span>
      <h1>PD-POD Studio — Public Domain Slogan, SVG Print &amp; Margin Engine</h1>
      <p class="muted">Avoid copyright strikes from trademarked superheroes. Pick a verified Public Domain literary/classic character, customize a print-ready typography SVG for Gelato/Etsy, copy 13 SEO tags, and verify your 30% profit margin.</p>
    </section>

    <div class="grid-2">
      <section class="card">
        <h2>1. Choose Public Domain Character &amp; Slogan</h2>
        <label>Public Domain Asset<select id="pdSelect" onchange="onSelectPD()"></select></label>
        <label>Slogan Preset<select id="pdSloganSel" onchange="syncSlogan()"></select></label>
        <label>Custom Print Headline<input id="pdCustom" oninput="renderSVG()"></label>
        <label>Shirt / Poster Background Color
          <select id="pdBg" onchange="renderSVG()">
            <option value="#111111">Classic Black (#111111)</option>
            <option value="#1e293b">Vintage Navy (#1e293b)</option>
            <option value="#f8fafc">Off-White Cream (#f8fafc)</option>
            <option value="#14532d">Forest Green (#14532d)</option>
          </select>
        </label>
        <div id="pdSafety" class="alert"></div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:10px">
          <button class="btn green" type="button" onclick="downloadSVG()">Download Print-Ready SVG</button>
          <button class="btn secondary" type="button" onclick="copyTags()">Copy Etsy SEO Tags</button>
        </div>
      </section>

      <section class="card">
        <h2>2. Live Print Mockup Preview</h2>
        <div id="svgWrap" style="display:flex;justify-content:center;padding:12px;background:var(--surface-2);border-radius:12px;border:1px solid var(--border)"></div>
        <p class="muted" style="margin-top:10px;font-size:0.84rem"><strong>Etsy SEO Tags:</strong> <span id="tagPreview"></span></p>
      </section>
    </div>

    {render_ad_slot(cfg, "pod-mid")}

    <section class="card">
      <h2>3. Gelato / Etsy Profit Margin &amp; $100/Week Target Calculator</h2>
      <div class="grid">
        <label>Retail Price ($)<input id="podPrice" type="number" value="24" step="1" oninput="calcPod()"></label>
        <label>Fulfillment + Shipping Cost ($)<input id="podCost" type="number" value="13.50" step="0.5" oninput="calcPod()"></label>
        <label>Marketplace Fees (% — Etsy ~13.5%)<input id="podFee" type="number" value="13.5" step="0.5" oninput="calcPod()"></label>
        <label>Target Weekly Profit ($)<input id="podTarget" type="number" value="100" step="25" oninput="calcPod()"></label>
      </div>
      <div class="kpi-grid">
        <div class="kpi"><div class="kpi-label">Net Profit / Order</div><div class="kpi-val pos" id="oPodProf">$0</div></div>
        <div class="kpi"><div class="kpi-label">Net Margin (%)</div><div class="kpi-val acc" id="oPodMarg">0%</div></div>
        <div class="kpi"><div class="kpi-label">Orders Needed / Week</div><div class="kpi-val" id="oPodOrders">0</div></div>
        <div class="kpi"><div class="kpi-label">Annualized Profit</div><div class="kpi-val pos" id="oPodAnn">$0</div></div>
      </div>
    </section>

    <script>
    const PD_ITEMS = {catalog_json};
    let currentItem = PD_ITEMS[0];

    const pdSel = document.getElementById("pdSelect");
    pdSel.innerHTML = PD_ITEMS.map((x, i) => `<option value="${{i}}">${{x.name}} — ${{x.pd_year}}</option>`).join("");

    function onSelectPD() {{
      currentItem = PD_ITEMS[Number(pdSel.value) || 0];
      const slSel = document.getElementById("pdSloganSel");
      slSel.innerHTML = currentItem.slogans.map(s => `<option value="${{s.replace(/"/g, '&quot;')}}">${{s}}</option>`).join("");
      document.getElementById("pdCustom").value = currentItem.slogans[0];
      document.getElementById("pdSafety").innerHTML = `<strong>Safe Scope:</strong> ${{currentItem.safe_scope}}<br><strong>Legal Caution:</strong> ${{currentItem.caution}}`;
      document.getElementById("tagPreview").textContent = currentItem.tags.join(", ");
      renderSVG();
    }}

    function syncSlogan() {{
      document.getElementById("pdCustom").value = document.getElementById("pdSloganSel").value;
      renderSVG();
    }}

    function escapeXml(s) {{
      return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
    }}

    function buildSVGString() {{
      const bg = document.getElementById("pdBg").value;
      const fg = bg === "#f8fafc" ? "#0f172a" : "#f8fafc";
      const txt = document.getElementById("pdCustom").value || currentItem.slogans[0];
      const words = txt.split(" ");
      const mid = Math.ceil(words.length / 2);
      const line1 = escapeXml(words.slice(0, mid).join(" "));
      const line2 = escapeXml(words.slice(mid).join(" "));
      return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 460" width="340" height="372">
        <rect width="420" height="460" rx="18" fill="${{bg}}"/>
        <rect x="24" y="24" width="372" height="412" rx="12" fill="none" stroke="${{currentItem.accent}}" stroke-width="3" stroke-dasharray="8 6"/>
        <text x="210" y="92" text-anchor="middle" fill="${{currentItem.accent}}" font-family="Georgia,serif" font-size="16" font-weight="700" letter-spacing="4">${{escapeXml(currentItem.motif)}}</text>
        <line x1="90" y1="114" x2="330" y2="114" stroke="${{currentItem.accent}}" stroke-width="1.5"/>
        <text x="210" y="210" text-anchor="middle" fill="${{fg}}" font-family="Georgia,serif" font-size="26" font-weight="700">${{line1}}</text>
        <text x="210" y="252" text-anchor="middle" fill="${{fg}}" font-family="Georgia,serif" font-size="26" font-weight="700">${{line2}}</text>
        <line x1="120" y1="310" x2="300" y2="310" stroke="${{currentItem.accent}}" stroke-width="1.5"/>
        <text x="210" y="352" text-anchor="middle" fill="${{fg}}" opacity="0.78" font-family="sans-serif" font-size="13" letter-spacing="2">${{escapeXml(currentItem.name.toUpperCase())}}</text>
        <text x="210" y="380" text-anchor="middle" fill="${{currentItem.accent}}" font-family="sans-serif" font-size="11">PUBLIC DOMAIN EDITION</text>
      </svg>`;
    }}

    function renderSVG() {{
      document.getElementById("svgWrap").innerHTML = buildSVGString();
    }}

    function downloadSVG() {{
      const blob = new Blob([buildSVGString()], {{ type: "image/svg+xml" }});
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = currentItem.slug + "-pod-design.svg";
      a.click();
    }}

    function copyTags() {{
      navigator.clipboard.writeText(currentItem.tags.join(", ")).then(() => alert("Copied Etsy SEO tags!"));
    }}

    function calcPod() {{
      const price = Number(document.getElementById("podPrice").value) || 0;
      const cost = Number(document.getElementById("podCost").value) || 0;
      const feePct = Number(document.getElementById("podFee").value) || 0;
      const target = Number(document.getElementById("podTarget").value) || 0;
      const net = price - cost - (price * feePct / 100);
      const margin = price > 0 ? (net / price) * 100 : 0;
      const orders = net > 0 ? Math.ceil(target / net) : 0;
      document.getElementById("oPodProf").textContent = "$" + net.toFixed(2);
      document.getElementById("oPodMarg").textContent = margin.toFixed(1) + "%";
      document.getElementById("oPodOrders").textContent = orders + " / wk";
      document.getElementById("oPodAnn").textContent = "$" + Math.round(orders * 52 * Math.max(0, net)).toLocaleString();
    }}

    onSelectPD();
    calcPod();
    </script>
    """
    ld = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "PD-POD Studio Public Domain Print Generator",
        "applicationCategory": "DesignApplication",
        "operatingSystem": "Web Browser",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
    }
    return rel, render_page(cfg, rel, title, desc, body, market["updated_date"], json_ld=ld)


def build_all_micro_apps(cfg: SiteConfig, market: dict[str, Any]) -> list[tuple[str, str]]:
    return [
        build_clutch_app(cfg, market),
        build_property_app(cfg, market),
        build_passive_income_app(cfg, market),
        build_pod_studio_app(cfg, market),
    ]
