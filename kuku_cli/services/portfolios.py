"""
Portfolio operations: list/create/delete + buy/sell.
"""
from typing import Dict
from kuku_cli.core.errors import DomainError, NotFound
from kuku_cli.infra.repo import PortfoliosRepo
from kuku_cli.data.market import SECURITIES


class PortfolioService:
    def __init__(self, repo: PortfoliosRepo) -> None:
        self.repo = repo

    def list_for(self, username: str):
        return self.repo.for_user(username)

    def create(self, owner: str, name: str, strategy: str):
        return self.repo.create(owner, name, strategy)

    def delete(self, pid: str):
        self.repo.delete(pid)

    def buy(
        self,
        pid: str,
        username: str,
        tickers: Dict[str, tuple[float, float]],  # {ticker: (qty, price)}
        debit: float,
        balance_getter,
    ) -> float:
        """
        Validates the purchase and appends quantities to portfolio holdings.
        Returns the new balance after debit.
        """
        p = self.repo.get(pid)
        if p.owner != username:
            raise DomainError("Portfolio does not belong to user.")
        for t in tickers:
            if t not in SECURITIES:
                raise NotFound(f"Unknown ticker: {t}")

        balance = balance_getter()
        if debit > balance:
            raise DomainError("Insufficient balance.")

        for t, (qty, _price) in tickers.items():
            p.holdings[t] = p.holdings.get(t, 0.0) + float(qty)

        self.repo.update(p)
        return balance - debit

    def sell(
        self,
        pid: str,
        username: str,
        tickers: Dict[str, tuple[float, float]],  # {ticker: (qty, price)}
    ) -> float:
        """
        Validates the sale, reduces holdings, and returns total proceeds.
        """
        p = self.repo.get(pid)
        if p.owner != username:
            raise DomainError("Portfolio does not belong to user.")

        proceeds = 0.0
        for t, (qty, price) in tickers.items():
            owned = p.holdings.get(t, 0.0)
            if qty <= 0 or qty > owned:
                raise DomainError(f"Invalid quantity for {t}. Owned: {owned}")
            p.holdings[t] = owned - qty
            if p.holdings[t] == 0:
                del p.holdings[t]
            proceeds += qty * price

        self.repo.update(p)
        return proceeds
