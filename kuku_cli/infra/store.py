"""
A tiny pickle-backed store so data survives between runs.
"""
import os
import pickle
from typing import Dict
from kuku_cli.core.models import User, Portfolio


class Store:
    def __init__(self, path: str = "data/state.pkl") -> None:
        self.path = path
        self.users: Dict[str, User] = {}
        self.portfolios: Dict[str, Portfolio] = {}

        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.path):
            with open(self.path, "rb") as f:
                state = pickle.load(f)
            self.users = state.get("users", {})
            self.portfolios = state.get("portfolios", {})

    def save(self) -> None:
        with open(self.path, "wb") as f:
            pickle.dump(
                {
                    "users": self.users,
                    "portfolios": self.portfolios,
                },
                f,
            )
