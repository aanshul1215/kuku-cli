# kuku_cli/data/market.py
from __future__ import annotations
from typing import Dict, List, Optional
from kuku_cli.core.models import Security

# Fixed-price catalog
SECURITIES: Dict[str, Security] = {
    "AAPL": Security("AAPL", "Apple", 100.00),
    "MSFT": Security("MSFT", "Microsoft", 120.00),
    "GOOG": Security("GOOG", "Alphabet", 150.00),
    "TSLA": Security("TSLA", "Tesla", 180.00),
    "NVDA": Security("NVDA", "Nvidia", 200.00),
    # add/remove here as needed
}

def list_securities() -> List[Security]:
    """Return all available securities (with fixed prices)."""
    return list(SECURITIES.values())

def get_security(ticker: str) -> Optional[Security]:
    """Find a security by ticker (case-insensitive)."""
    return SECURITIES.get(ticker.upper())

def get_price(ticker: str) -> float:
    """Convenience accessor for price."""
    sec = get_security(ticker)
    if sec is None:
        raise KeyError(f"Unknown ticker: {ticker}")
    return sec.price
