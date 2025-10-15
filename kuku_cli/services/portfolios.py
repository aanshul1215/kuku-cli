"""
Portfolio operations: list/create/delete + buy/sell.
"""

from typing import Dict
from kuku_cli.core.errors import DomainError, NotFound
from kuku_cli.infra.repo import PortfoliosRepo
from kuku_cli.data import market  # use market helpers (fixed-price catalog)


class PortfolioService:
    def __init__(self, repo: PortfoliosRepo) -> None:
        self.repo = repo

    def list_for(self, username: str):
        return self.repo.for_user(username)

    def create(self, owner: str, name: str, strategy: str):
        return self.repo.create(owner, name, strategy)

    def delete(self, pid: str):
        self.repo.delete(pid)

    # ---------------------------- BUY -------------------------------------

    def buy(
        self,
        pid: str,
        username: str,
        tickers: Dict[str, tuple[float, float]],  # {ticker: (qty, price_ignored)}
        debit: float,
        balance_getter,
    ) -> float:
        """
        Validates the purchase and appends quantities to portfolio holdings.
        Returns the new balance after debit.

        Note: price from caller is ignored; the UI computes debit using market prices.
        Holdings here store only quantities.
        """
        p = self.repo.get(pid)
        if p.owner != username:
            raise DomainError("Portfolio does not belong to user.")

        for t in tickers:
            if market.get_security(t) is None:
                raise NotFound(f"Unknown ticker: {t}")

        balance = float(balance_getter())
        if debit > balance:
            raise DomainError("Insufficient balance.")

        for t, (qty, _ignored) in tickers.items():
            q = float(qty)
            if q <= 0:
                raise DomainError(f"Quantity must be > 0 for {t}.")
            p.holdings[t] = float(p.holdings.get(t, 0.0)) + q

        self.repo.update(p)
        return round(balance - float(debit), 2)

    # ---------------------------- SELL ------------------------------------

    def sell(
        self,
        pid: str,
        username: str,
        tickers: Dict[str, tuple[float, float]],  # {ticker: (qty, user_sale_price)}
    ) -> float:
        """
        Validates the sale, reduces holdings, and returns total proceeds.
        Uses the **user-provided sale price** per ticker (second tuple item).
        """
        p = self.repo.get(pid)
        if p.owner != username:
            raise DomainError("Portfolio does not belong to user.")

        proceeds = 0.0
        for t, (qty, price) in tickers.items():
            owned = float(p.holdings.get(t, 0.0))
            q = float(qty)
            pr = float(price)

            if q <= 0 or q > owned:
                raise DomainError(f"Invalid quantity for {t}. Owned: {owned}")

            new_qty = owned - q
            if new_qty > 0:
                p.holdings[t] = new_qty
            else:
                p.holdings.pop(t, None)

            proceeds += q * pr

        self.repo.update(p)
        return round(proceeds, 2)
