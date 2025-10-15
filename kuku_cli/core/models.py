"""
Domain models only (no logic or persistence).
"""
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class User:
    username: str
    password: str
    first_name: str
    last_name: str
    balance: float
    is_admin: bool = False


@dataclass
class Portfolio:
    id: str
    owner: str
    name: str
    strategy: str
    # holdings: ticker -> quantity
    holdings: Dict[str, float] = field(default_factory=dict)
from dataclasses import dataclass

@dataclass(frozen=True)
class Security:
    ticker: str
    name: str
    price: float
