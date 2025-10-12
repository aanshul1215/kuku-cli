# kuku_cli/ui/menus.py

WELCOME_MENU = 10
ADMIN_MENU = 20
USER_MENU = 30
PORTFOLIOS_MENU = 40
MARKET_MENU = 50

WELCOME = (
    "1. Admin login\n"
    "2. User login\n"
    "3. Create new user\n"     # <-- added
    "0. Exit"
)

ADMIN = (
    "1. View users\n"
    "2. Create user\n"
    "3. Delete user\n"
    "9. Back"
)

USER = (
    "1. Manage portfolios\n"
    "2. Visit market\n"
    "9. Logout"
)

PORTFOLIOS = (
    "1. View my portfolios\n"
    "2. Create new portfolio\n"
    "3. Delete a portfolio\n"
    "4. Sell (liquidate)\n"
    "9. Back"
)

MARKET = (
    "1. View securities\n"
    "2. Buy (purchase)\n"
    "9. Back"
)
