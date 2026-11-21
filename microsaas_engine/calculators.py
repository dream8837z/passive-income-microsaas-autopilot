"""Verified financial, real estate, POD, and Micro-SaaS calculators."""
from __future__ import annotations

import math
from dataclasses import dataclass


def calc_hysa_comparison(
    principal: float,
    hysa_apy_pct: float,
    baseline_apy_pct: float = 0.38,
    years: int = 1,
) -> dict[str, float]:
    """Compare High-Yield Savings Account vs standard bank savings."""
    hysa_r = hysa_apy_pct / 100.0
    base_r = baseline_apy_pct / 100.0
    hysa_final = principal * ((1.0 + hysa_r) ** years)
    base_final = principal * ((1.0 + base_r) ** years)
    hysa_interest = hysa_final - principal
    base_interest = base_final - principal
    return {
        "principal": principal,
        "hysa_final": round(hysa_final, 2),
        "hysa_interest": round(hysa_interest, 2),
        "base_final": round(base_final, 2),
        "base_interest": round(base_interest, 2),
        "extra_gain": round(hysa_interest - base_interest, 2),
        "monthly_passive": round((principal * hysa_r) / 12.0, 2),
        "weekly_passive": round((principal * hysa_r) / 52.0, 2),
    }


def calc_capital_for_income(annual_income_usd: float, yield_pct: float) -> float:
    """Calculate required capital to generate a target annual passive income."""
    if yield_pct <= 0:
        raise ValueError("yield_pct must be > 0")
    return round(annual_income_usd / (yield_pct / 100.0), 2)


def calc_drip_projection(
    initial_capital: float,
    monthly_contribution: float,
    dividend_yield_pct: float,
    price_growth_pct: float = 4.0,
    years: int = 10,
) -> dict[str, float]:
    """Simulate DRIP (Dividend Reinvestment) portfolio growth over N years."""
    total_r = (dividend_yield_pct + price_growth_pct) / 100.0
    monthly_r = total_r / 12.0
    months = years * 12
    balance = initial_capital
    for _ in range(months):
        balance = balance * (1.0 + monthly_r) + monthly_contribution
    total_contributed = initial_capital + monthly_contribution * months
    annual_div = balance * (dividend_yield_pct / 100.0)
    return {
        "ending_balance": round(balance, 2),
        "total_contributed": round(total_contributed, 2),
        "total_growth": round(balance - total_contributed, 2),
        "annual_dividend": round(annual_div, 2),
        "monthly_dividend": round(annual_div / 12.0, 2),
        "weekly_dividend": round(annual_div / 52.0, 2),
    }


def calc_monthly_mortgage(loan_amount: float, annual_rate_pct: float, years: int = 30) -> float:
    """Standard fixed-rate monthly principal & interest payment."""
    if loan_amount <= 0:
        return 0.0
    r = (annual_rate_pct / 100.0) / 12.0
    n = years * 12
    if r == 0:
        return round(loan_amount / n, 2)
    payment = loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    return round(payment, 2)


def calc_property_comparison(
    price: float,
    down_pct: float = 20.0,
    mortgage_rate_pct: float = 7.0,
    monthly_rent: float | None = None,
    maintenance_pct_yr: float = 1.0,
    management_pct_rent: float = 8.0,
    commercial_cap_rate_pct: float = 7.5,
    appreciation_pct_yr: float = 4.5,
    years: int = 10,
) -> dict[str, float]:
    """Compare leveraged residential rental vs outright commercial NNN lease."""
    down_payment = price * (down_pct / 100.0)
    loan_amount = price - down_payment
    mortgage_mo = calc_monthly_mortgage(loan_amount, mortgage_rate_pct, 30)
    est_rent = monthly_rent if monthly_rent is not None else round(price * 0.006186, 2)
    maint_mo = (price * (maintenance_pct_yr / 100.0)) / 12.0
    mgmt_mo = est_rent * (management_pct_rent / 100.0)
    res_net_mo = est_rent - mortgage_mo - maint_mo - mgmt_mo

    # Outright commercial NNN: tenant pays maintenance & repairs, 0 mortgage
    comm_annual_noi = price * (commercial_cap_rate_pct / 100.0)
    comm_net_mo = comm_annual_noi / 12.0
    future_value = price * ((1.0 + appreciation_pct_yr / 100.0) ** years)

    return {
        "price": round(price, 2),
        "down_payment": round(down_payment, 2),
        "loan_amount": round(loan_amount, 2),
        "mortgage_mo": round(mortgage_mo, 2),
        "res_rent_mo": round(est_rent, 2),
        "res_expenses_mo": round(maint_mo + mgmt_mo, 2),
        "res_net_cashflow_mo": round(res_net_mo, 2),
        "comm_net_cashflow_mo": round(comm_net_mo, 2),
        "comm_net_cashflow_wk": round(comm_annual_noi / 52.0, 2),
        "future_value_10y": round(future_value, 2),
        "equity_gain_10y": round(future_value - price, 2),
    }


def calc_pod_economics(
    retail_price: float = 24.0,
    margin_pct: float = 30.0,
    target_weekly_usd: float = 100.0,
) -> dict[str, float]:
    """Calculate Print-on-Demand profit per order and weekly sales needed."""
    profit_per_sale = retail_price * (margin_pct / 100.0)
    sales_per_week = math.ceil(target_weekly_usd / profit_per_sale) if profit_per_sale > 0 else 0
    return {
        "retail_price": round(retail_price, 2),
        "profit_per_sale": round(profit_per_sale, 2),
        "sales_per_week": int(sales_per_week),
        "sales_per_month": int(math.ceil(sales_per_week * 52 / 12)),
        "annual_revenue_at_target": round(sales_per_week * 52 * retail_price, 2),
        "annual_profit_at_target": round(sales_per_week * 52 * profit_per_sale, 2),
    }


def calc_microsaas_mrr(
    monthly_price: float,
    target_monthly_usd: float,
    monthly_churn_pct: float = 4.0,
) -> dict[str, float]:
    """Calculate B2B Micro-SaaS subscriber targets, LTV, and ARR."""
    subs_needed = math.ceil(target_monthly_usd / monthly_price) if monthly_price > 0 else 0
    actual_mrr = subs_needed * monthly_price
    actual_weekly = actual_mrr * 12.0 / 52.0
    avg_lifetime_months = (100.0 / monthly_churn_pct) if monthly_churn_pct > 0 else 60.0
    ltv = monthly_price * avg_lifetime_months
    return {
        "monthly_price": round(monthly_price, 2),
        "subs_needed": int(subs_needed),
        "actual_mrr": round(actual_mrr, 2),
        "actual_arr": round(actual_mrr * 12.0, 2),
        "actual_weekly": round(actual_weekly, 2),
        "avg_lifetime_months": round(avg_lifetime_months, 1),
        "customer_ltv": round(ltv, 2),
    }
