"""Stripe client for PLAYTREE in-game purchases.
Uses the API key from .env / environment. Never hardcodes keys.
Product IDs match stripe_backend.py catalog.
"""
import os
import json
import webbrowser
import urllib.request
import urllib.error

BACKEND = os.environ.get("PLAYTREE_BACKEND_URL", "http://localhost:5000")

PRODUCTS = {
    "points_500":  {"name": "Starter Pack - 500 Tree Points", "amount": 500},
    "points_1300": {"name": "Value Pack - 1,300 Tree Points", "amount": 1300},
    "points_3500": {"name": "Mega Pack - 3,500 Tree Points", "amount": 3500},
    "coins_1000":  {"name": "Coin Pouch - 1,000 Tree Coins", "amount": 1000},
    "coins_3500":  {"name": "Coin Chest - 3,500 Tree Coins", "amount": 3500},
    "coins_12000": {"name": "Coin Vault - 12,000 Tree Coins", "amount": 12000},
}


def load_env():
    """Load STRIPE_* and backend URL from a .env file next to the game."""
    paths = [os.path.join(os.getcwd(), ".env"),
             os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")]
    for p in paths:
        if os.path.exists(p):
            try:
                for line in open(p, encoding="utf-8"):
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
            except Exception:
                pass
            break


def get_publishable_key():
    load_env()
    return os.environ.get("STRIPE_PUBLISHABLE_KEY", "")


def get_secret_key():
    load_env()
    return os.environ.get("STRIPE_SECRET_KEY", "")


def create_checkout(product_key, user="guest"):
    """Create a real Stripe Checkout Session via the backend.
    Returns (url, error). Opens the browser to Stripe Checkout on success.
    """
    load_env()
    backend = os.environ.get("PLAYTREE_BACKEND_URL", BACKEND)
    if product_key not in PRODUCTS:
        return None, "Unknown product"
    body = json.dumps({"product": product_key, "user": user}).encode("utf-8")
    req = urllib.request.Request(
        backend.rstrip("/") + "/create-checkout-session",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        url = data.get("url")
        if url:
            try:
                webbrowser.open(url)
            except Exception:
                pass
            return url, None
        return None, data.get("error", "No checkout URL returned")
    except urllib.error.HTTPError as e:
        try:
            msg = json.loads(e.read().decode("utf-8")).get("error", str(e))
        except Exception:
            msg = str(e)
        return None, msg
    except Exception as e:
        return None, f"Backend unavailable: {e}"


def configured():
    return bool(get_secret_key() and get_publishable_key())
