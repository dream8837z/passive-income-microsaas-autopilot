"""Configuration loader with affiliate & digital product slots for zero-touch CI/CD."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SiteConfig:
    site_name: str
    site_url: str
    root_portal_url: str
    kr_hub_url: str
    adsense_client_id: str
    contact_email: str
    dry_run: bool
    dist_dir: Path
    data_dir: Path
    affiliate_hysa_url: str = ""
    affiliate_broker_url: str = ""
    affiliate_pod_url: str = ""
    affiliate_property_url: str = ""
    gumroad_product_url: str = ""

    @property
    def adsense_pub_id(self) -> str:
        cid = self.adsense_client_id.strip()
        if cid.startswith("ca-"):
            return cid[3:]
        return cid


def _load_dotenv(env_path: Path) -> None:
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        os.environ.setdefault(k, v)


def load_config(project_root: Path | None = None) -> SiteConfig:
    root = project_root or Path(__file__).resolve().parent.parent
    if not root.is_dir():
        root = Path.cwd()
    _load_dotenv(root / ".env")
    site_url = os.environ.get(
        "SITE_URL",
        "https://dream8837z.github.io/passive-income-microsaas-autopilot",
    ).rstrip("/")
    return SiteConfig(
        site_name=os.environ.get(
            "SITE_NAME",
            "WealthStack Studio — Free AI Micro-SaaS & Passive Income Calculators",
        ),
        site_url=site_url,
        root_portal_url=os.environ.get("ROOT_PORTAL_URL", "https://dream8837z.github.io/"),
        kr_hub_url=os.environ.get("KR_HUB_URL", "https://dream8837z.github.io/pseo-revenue-autopilot/"),
        adsense_client_id=os.environ.get("ADSENSE_CLIENT_ID", "ca-pub-9014872001634608"),
        contact_email=os.environ.get("CONTACT_EMAIL", "contact@wealthstack.studio"),
        dry_run=os.environ.get("DRY_RUN", "false").lower() == "true",
        dist_dir=root / "dist",
        data_dir=root / "data",
        affiliate_hysa_url=os.environ.get("AFFILIATE_HYSA_URL", "").strip(),
        affiliate_broker_url=os.environ.get("AFFILIATE_BROKER_URL", "").strip(),
        affiliate_pod_url=os.environ.get("AFFILIATE_POD_URL", "").strip(),
        affiliate_property_url=os.environ.get("AFFILIATE_PROPERTY_URL", "").strip(),
        gumroad_product_url=os.environ.get("GUMROAD_PRODUCT_URL", "").strip(),
    )
