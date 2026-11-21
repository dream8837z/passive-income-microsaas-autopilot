"""Unit & integration tests for WealthStack Studio Micro-SaaS & pSEO pipeline."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from microsaas_engine.calculators import (
    calc_capital_for_income,
    calc_drip_projection,
    calc_hysa_comparison,
    calc_microsaas_mrr,
    calc_monthly_mortgage,
    calc_pod_economics,
    calc_property_comparison,
)
from microsaas_engine.config import SiteConfig
from microsaas_engine.pipeline import run_pipeline


class TestCalculators(unittest.TestCase):
    def test_hysa_benchmark_numbers(self) -> None:
        # $10,000 at 4.2% APY = $420 vs 0.38% = $38 (+$382 extra)
        res = calc_hysa_comparison(10_000, 4.2, 0.38, years=1)
        self.assertAlmostEqual(res["hysa_interest"], 420.0, places=2)
        self.assertAlmostEqual(res["base_interest"], 38.0, places=2)
        self.assertAlmostEqual(res["extra_gain"], 382.0, places=2)

    def test_capital_for_100_per_week(self) -> None:
        # $100/week ($5,200/yr) at 4.2% = $123,809.52; at 2.97% = $175,084.18
        hysa_cap = calc_capital_for_income(5_200, 4.2)
        div_cap = calc_capital_for_income(5_200, 2.97)
        self.assertAlmostEqual(hysa_cap, 123_809.52, delta=1.0)
        self.assertAlmostEqual(div_cap, 175_084.18, delta=1.0)

    def test_residential_vs_commercial_property(self) -> None:
        # $370k home, 20% down ($74k -> $296k loan), 7% 30yr mortgage ≈ $1,969.29/mo
        mort = calc_monthly_mortgage(296_000, 7.0, 30)
        self.assertAlmostEqual(mort, 1969.29, delta=2.0)
        comp = calc_property_comparison(370_000, down_pct=20.0, mortgage_rate_pct=7.0, monthly_rent=2289.0)
        self.assertLess(comp["res_net_cashflow_mo"], 0)
        self.assertGreater(comp["comm_net_cashflow_mo"], 2000)
        self.assertAlmostEqual(comp["future_value_10y"], 574_598.0, delta=500.0)

    def test_pod_and_microsaas_unit_economics(self) -> None:
        pod = calc_pod_economics(retail_price=24.0, margin_pct=30.0, target_weekly_usd=100.0)
        self.assertAlmostEqual(pod["profit_per_sale"], 7.20, places=2)
        self.assertEqual(pod["sales_per_week"], 14)

        saas = calc_microsaas_mrr(monthly_price=29.0, target_monthly_usd=434.0)
        self.assertEqual(saas["subs_needed"], 15)
        self.assertGreater(saas["actual_weekly"], 100.0)

    def test_drip_projection_positive_growth(self) -> None:
        drip = calc_drip_projection(10_000, 500, 2.97, 4.0, years=10)
        self.assertGreater(drip["ending_balance"], drip["total_contributed"])
        self.assertGreater(drip["weekly_dividend"], 50.0)


class TestFullPipelineBuild(unittest.TestCase):
    def test_end_to_end_dry_run_and_seo_audit(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cfg = SiteConfig(
                site_name="WealthStack Studio",
                site_url="https://dream8837z.github.io/passive-income-microsaas-autopilot",
                root_portal_url="https://dream8837z.github.io/",
                kr_hub_url="https://dream8837z.github.io/pseo-revenue-autopilot/",
                adsense_client_id="ca-pub-9014872001634608",
                contact_email="contact@wealthstack.studio",
                dry_run=True,
                dist_dir=root / "dist",
                data_dir=root / "data",
            )
            result = run_pipeline(cfg)
            self.assertEqual(result["audit"]["status"], "PASS")
            self.assertEqual(result["audit"]["error_count"], 0)
            self.assertEqual(result["audit"]["page_count"], 113)
            self.assertTrue((cfg.dist_dir / "apps/clutch-driving-instructor.html").exists())
            self.assertTrue((cfg.dist_dir / "ads.txt").exists())
            self.assertTrue((cfg.dist_dir / "sitemap.xml").exists())


if __name__ == "__main__":
    unittest.main()
