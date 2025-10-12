"""
Repository layer – all persistence and ID generation lives here.
"""
import uuid
from typing import Iterable
from kuku_cli.core.models import User, Portfolio
from kuku_cli.core.errors import NotFound
from .store import Store


class UsersRepo:
    def __init__(self, store: Store) -> None:
        self.store = store

    def get(self, username: str) -> User:
        u = self.store.users.get(username)
        if not u:
            raise NotFound(f"Unknown user: {username}")
        return u

    def all(self) -> Iterable[User]:
        return self.store.users.values()

    def upsert(self, user: User) -> None:
        self.store.users[user.username] = user
        self.store.save()

    def delete(self, username: str) -> None:
        if username in self.store.users:
            del self.store.users[username]
            self.store.save()
        else:
            raise NotFound(f"Unknown user: {username}")


class PortfoliosRepo:
    def __init__(self, store: Store) -> None:
        self.store = store

    def get(self, pid: str) -> Portfolio:
        p = self.store.portfolios.get(pid)
        if not p:
            raise NotFound(f"Portfolio not found: {pid}")
        return p

    def for_user(self, username: str) -> Iterable[Portfolio]:
        return [p for p in self.store.portfolios.values() if p.owner == username]

    def create(self, owner: str, name: str, strategy: str) -> Portfolio:
        pid = uuid.uuid4().hex[:8]
        p = Portfolio(id=pid, owner=owner, name=name, strategy=strategy)
        self.store.portfolios[p.id] = p
        self.store.save()
        return p

    def delete(self, pid: str) -> None:
        if pid in self.store.portfolios:
            del self.store.portfolios[pid]
            self.store.save()
        else:
            raise NotFound(f"Portfolio not found: {pid}")

    def update(self, p: Portfolio) -> None:
        self.store.portfolios[p.id] = p
        self.store.save()
