"""
Authentication service – holds current user and enforces admin checks.
"""
from kuku_cli.core.errors import AuthError
from kuku_cli.core.models import User
from kuku_cli.infra.repo import UsersRepo


class AuthService:
    def __init__(self, users: UsersRepo) -> None:
        self.users = users
        self.current: User | None = None

    def login(self, username: str, password: str) -> User:
        u = self.users.get(username)
        if u.password != password:
            raise AuthError("Invalid credentials.")
        self.current = u
        return u

    def logout(self) -> None:
        self.current = None

    def require_login(self) -> User:
        if not self.current:
            raise AuthError("Please login first.")
        return self.current

    def require_admin(self) -> User:
        u = self.require_login()
        if not u.is_admin:
            raise AuthError("Admins only.")
        return u
