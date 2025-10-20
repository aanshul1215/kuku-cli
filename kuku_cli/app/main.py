# kuku_cli/app/main.py
"""
Kuku CLI - Application shell (menu loop)

Guided order entry:
  - user picks tickers (comma separated)
  - app asks quantity for each ticker
  - app asks price for each ticker
Then we show a summary table and update portfolio + balance.

No 'justify=' kwargs are used when printing tables.
"""

from typing import Dict, Tuple, List

from kuku_cli.ui.console import ConsoleUI
from kuku_cli.ui import menus
from kuku_cli.core.errors import DomainError, AuthError, NotFound
from kuku_cli.infra.store import Store
from kuku_cli.infra.repo import UsersRepo, PortfoliosRepo
from kuku_cli.services.auth import AuthService
from kuku_cli.services.users import UsersService
from kuku_cli.services.portfolios import PortfolioService
from kuku_cli.data.market import SECURITIES


# --------------------------- helpers ----------------------------------------


def _seed_admin_once(users: UsersService) -> None:
    """Create a default admin user if missing."""
    names = [u.username for u in users.list()]
    if "admin" not in names:
        users.create("admin", "adminpass", "Kuku", "Admin", balance=5000.0, is_admin=True)


def _money(x: float) -> str:
    return f"{x:,.2f}"


def _ask_float(ui: ConsoleUI, label: str) -> float:
    while True:
        s = ui.ask(label).strip()
        try:
            v = float(s)
            if v <= 0:
                ui.warn("Enter a value greater than 0.")
                continue
            return v
        except ValueError:
            ui.warn("Enter a numeric value.")


def _parse_tickers(ui: ConsoleUI, *, require_known: bool) -> List[str]:
    """Ask for comma-separated tickers and validate/normalize them."""
    raw = ui.ask("Securities to add (comma-separated), e.g. AAPL, MSFT").strip()
    out: List[str] = []
    seen = set()
    for part in raw.split(","):
        t = part.strip().upper()
        if not t:
            continue
        if require_known and t not in SECURITIES:
            ui.warn(f"Unknown ticker: {t}")
            raise ValueError(f"Unknown ticker: {t}")
        if t not in seen:
            seen.add(t)
            out.append(t)
    if not out:
        raise ValueError("No tickers provided.")
    return out


def _collect_orders_guided(
    ui: ConsoleUI,
    *,
    require_known_tickers: bool,
    qty_label_tmpl: str,
    price_label_tmpl: str,
) -> Tuple[Dict[str, Tuple[float, float]], float]:
    """
    Guided buy/sell entry:
      1) optionally show marketplace
      2) ask tickers (comma-separated)
      3) ask qty per ticker
      4) ask price per ticker
    Returns: (orders_map, total_cost_or_proceeds)
             where orders_map = { ticker: (qty, price) }
    """
    if require_known_tickers:
        ui.table("Marketplace", ["Ticker", "Name"], SECURITIES.items())

    tickers = _parse_tickers(ui, require_known=require_known_tickers)

    qty_map: Dict[str, float] = {}
    for t in tickers:
        qty_map[t] = _ask_float(ui, qty_label_tmpl.format(ticker=t))

    price_map: Dict[str, float] = {}
    for t in tickers:
        price_map[t] = _ask_float(ui, price_label_tmpl.format(ticker=t))

    orders: Dict[str, Tuple[float, float]] = {}
    total = 0.0
    for t in tickers:
        q = qty_map[t]
        p = price_map[t]
        orders[t] = (q, p)
        total += q * p

    return orders, total


# --------------------------- app entry --------------------------------------


def run() -> None:
    ui = ConsoleUI()

    # Infrastructure wiring
    store = Store(path="data/state.pkl")      # persisted to disk
    users_repo = UsersRepo(store)
    ports_repo = PortfoliosRepo(store)

    users = UsersService(users_repo)
    auth = AuthService(users_repo)
    ports = PortfolioService(ports_repo)

    _seed_admin_once(users)

    current = menus.WELCOME_MENU

    while True:
        try:
            # ----------------------- WELCOME ---------------------------------
            if current == menus.WELCOME_MENU:
                ui.title("Kuku CLI")
                ui.palette("Welcome", menus.WELCOME)

                choice = ui.ask("> ").strip()
                if not choice:
                    continue

                if choice == "1":  # Admin login
                    u = ui.ask("Admin username")
                    p = ui.ask_password("Password")
                    auth.login(u, p)
                    auth.require_admin()
                    ui.ok("Welcome, admin.")
                    current = menus.ADMIN_MENU

                elif choice == "2":  # User login
                    u = ui.ask("Username")
                    p = ui.ask_password("Password")
                    auth.login(u, p)
                    ui.ok(f"Welcome, {auth.current.first_name}!")
                    current = menus.USER_MENU

                elif choice == "3":  # Create new user
                    ui.title("Create Account")
                    username = ui.ask("Choose a username")
                    password = ui.ask_password("Choose a password")
                    first = ui.ask("First name")
                    last = ui.ask("Last name")
                    balance_str = ui.ask("Initial deposit (e.g., 1000)")
                    try:
                        balance = float(balance_str)
                        if balance < 0:
                            raise ValueError()
                    except ValueError:
                        ui.warn("Please enter a positive numeric amount. Account not created.")
                        ui.pause()
                        continue

                    users.create(username, password, first, last, balance, is_admin=False)
                    ui.ok("Account created. You can now login as a user.")
                    ui.pause()
                    current = menus.WELCOME_MENU

                elif choice == "0":
                    ui.info("Bye!")
                    break
                else:
                    ui.warn("Unknown option.")

            # ----------------------- ADMIN -----------------------------------
            elif current == menus.ADMIN_MENU:
                try:
                    auth.require_admin()
                except AuthError:
                    ui.warn("Admins only. Returning to welcome.")
                    auth.logout()
                    current = menus.WELCOME_MENU
                    continue

                ui.title("Admin")
                ui.palette("Manage users", menus.ADMIN)

                choice = ui.ask("> ").strip()
                if choice == "1":  # view users
                    hdrs = ["Username", "Name", "Admin", "Balance"]
                    rows = [
                        (u.username, f"{u.first_name} {u.last_name}", "yes" if u.is_admin else "no", _money(u.balance))
                        for u in users.list()
                    ]
                    ui.table("Users", hdrs, rows)
                    ui.pause()

                elif choice == "2":  # create user
                    un = ui.ask("Username")
                    pw = ui.ask_password("Password")
                    fn = ui.ask("First name")
                    ln = ui.ask("Last name")
                    bal = _ask_float(ui, "Initial balance")
                    adm = ui.ask("Make admin? (y/n)").lower().startswith("y")
                    users.create(un, pw, fn, ln, bal, is_admin=adm)
                    ui.ok("User created.")

                elif choice == "3":  # delete user
                    un = ui.ask("Username to delete")
                    users.delete(un)
                    ui.ok("User deleted.")

                elif choice == "9":
                    auth.logout()
                    current = menus.WELCOME_MENU
                else:
                    ui.warn("Unknown option.")

            # ----------------------- USER HOME --------------------------------
            elif current == menus.USER_MENU:
                u = auth.require_login()
                ui.title("User")
                ui.palette("Choose", menus.USER)

                choice = ui.ask("> ").strip()
                if choice == "1":
                    current = menus.PORTFOLIOS_MENU
                elif choice == "2":
                    current = menus.MARKET_MENU
                elif choice == "9":
                    auth.logout()
                    current = menus.WELCOME_MENU
                else:
                    ui.warn("Unknown option.")

            # ----------------------- PORTFOLIOS -------------------------------
            elif current == menus.PORTFOLIOS_MENU:
                u = auth.require_login()
                ui.title("Manage Portfolios")
                ui.palette("Options", menus.PORTFOLIOS)

                choice = ui.ask("> ").strip()
                if choice == "1":  # view portfolios with live holdings
                    ps = list(ports.list_for(u.username))
                    hdrs = ["Name", "Strategy", "Holdings", "ID"]
                    rows = []
                    for p in ps:
                        holdings = " ".join(f"{t}:{q}" for t, q in p.holdings.items()) or "-"
                        rows.append((p.name, p.strategy, holdings, p.id))
                    ui.table("Your Portfolios", hdrs, rows)
                    ui.pause()

                elif choice == "2":  # create + (optional) initial guided buy
                    name = ui.ask("Portfolio name")
                    strategy = ui.ask("Strategy")
                    p = ports.create(u.username, name, strategy)
                    ui.ok(f"Created portfolio {p.id}.")

                    add_now = ui.ask("Add securities now? (y/n)").strip().lower().startswith("y")
                    if add_now:
                        try:
                            orders, total = _collect_orders_guided(
                                ui,
                                require_known_tickers=True,
                                qty_label_tmpl="Quantity for {ticker}",
                                price_label_tmpl="Purchase price for {ticker}",
                            )
                        except ValueError as ve:
                            ui.warn(str(ve))
                            ui.pause()
                        else:
                            new_balance = ports.buy(p.id, u.username, orders, total, lambda: u.balance)
                            u.balance = new_balance
                            users_repo.upsert(u)  # persist

                            hdrs = ["Ticker", "Qty", "Price", "Cost"]
                            rows = [(t, q, pr, q * pr) for t, (q, pr) in orders.items()]
                            ui.table("Initial Purchase Allocation", hdrs, rows)
                            ui.ok(f"Total spent: ${_money(total)}. New balance: ${_money(u.balance)}")

                elif choice == "3":  # delete
                    pid = ui.ask("Portfolio ID")
                    ports.delete(pid)
                    ui.ok("Portfolio deleted.")

                elif choice == "4":  # sell / liquidate
                    pid = ui.ask("Portfolio ID")
                    try:
                        orders, _ = _collect_orders_guided(
                            ui,
                            require_known_tickers=False,
                            qty_label_tmpl="Quantity to sell for {ticker}",
                            price_label_tmpl="Sale price for {ticker}",
                        )
                    except ValueError as ve:
                        ui.warn(str(ve))
                        ui.pause()
                    else:
                        proceeds = ports.sell(pid, u.username, orders)
                        u.balance += proceeds
                        users_repo.upsert(u)
                        hdrs = ["Ticker", "Qty", "Price", "Proceeds"]
                        rows = [(t, q, pr, q * pr) for t, (q, pr) in orders.items()]
                        ui.table("Sale Summary", hdrs, rows)
                        ui.ok(f"Proceeds: ${_money(proceeds)}. New balance: ${_money(u.balance)}")

                elif choice == "9":
                    current = menus.USER_MENU
                else:
                    ui.warn("Unknown option.")

            # ----------------------- MARKETPLACE ------------------------------
            elif current == menus.MARKET_MENU:
                u = auth.require_login()
                ui.title("Marketplace")
                ui.palette("Options", menus.MARKET)

                choice = ui.ask("> ").strip()
                if choice == "1":  # view securities
                    ui.table("Securities", ["Ticker", "Name"], SECURITIES.items())
                    ui.pause()

                elif choice == "2":  # buy (guided) into an existing portfolio
                    pid = ui.ask("Portfolio ID")
                    try:
                        orders, total = _collect_orders_guided(
                            ui,
                            require_known_tickers=True,
                            qty_label_tmpl="Quantity for {ticker}",
                            price_label_tmpl="Purchase price for {ticker}",
                        )
                    except ValueError as ve:
                        ui.warn(str(ve))
                        ui.pause()
                    else:
                        new_balance = ports.buy(pid, u.username, orders, total, lambda: u.balance)
                        u.balance = new_balance
                        users_repo.upsert(u)
                        hdrs = ["Ticker", "Qty", "Price", "Cost"]
                        rows = [(t, q, pr, q * pr) for t, (q, pr) in orders.items()]
                        ui.table("Purchase Allocation", hdrs, rows)
                        ui.ok(f"Total spent: ${_money(total)}. New balance: ${_money(u.balance)}")

                elif choice == "9":
                    current = menus.USER_MENU
                else:
                    ui.warn("Unknown option.")

        # ---- friendly error handling ---------------------------------------
        except (DomainError, AuthError, NotFound) as e:
            ui.error(str(e))
            ui.pause()
        except ValueError:
            ui.warn("Enter a numeric value where expected.")
            ui.pause()
            