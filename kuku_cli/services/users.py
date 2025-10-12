"""
User use-cases: list, create, delete.
"""
from typing import Iterable
from kuku_cli.core.models import User
from kuku_cli.core.errors import DomainError
from kuku_cli.infra.repo import UsersRepo


class UsersService:
    def __init__(self, repo: UsersRepo) -> None:
        self.repo = repo

    def list(self) -> Iterable[User]:
        return self.repo.all()

    def create(
        self,
        username: str,
        password: str,
        first: str,
        last: str,
        balance: float,
        is_admin: bool = False,
    ) -> User:
        if username in [u.username for u in self.repo.all()]:
            raise DomainError("Username already exists.")
        u = User(
            username=username,
            password=password,
            first_name=first,
            last_name=last,
            balance=balance,
            is_admin=is_admin,
        )
        self.repo.upsert(u)
        return u

    def delete(self, username: str) -> None:
        if username == "admin":
            raise DomainError("Admin user cannot be deleted.")
        self.repo.delete(username)
