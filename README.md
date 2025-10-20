# Kuku CLI — Assignment 1

## What I built
- Fixed-price catalog for securities (`kuku_cli/data/market.py`)
- Marketplace shows **Ticker · Name · Price**
- **Buy** uses fixed prices (no manual price entry)
- **Sell** prompts for a user sale price; proceeds/balance use that price
- Portfolio holdings and user cash balance update accordingly

## How to run
python -m venv .venv
.venv\Scripts\Activate.ps1   # on Windows PowerShell
pip install -r requirements.txt
python -m kuku_cli
