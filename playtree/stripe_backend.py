#!/usr/bin/env python3
"""PLAYTREE Stripe Backend - Real payments with API keys (not links).

Usage:
  1. Set environment variables:
     set STRIPE_SECRET_KEY=sk_live_...   (or sk_test_... for testing)
     set STRIPE_PUBLISHABLE_KEY=pk_live_...
  2. pip install flask stripe python-dotenv
  3. python stripe_backend.py
  4. Frontend calls http://localhost:5000/create-checkout-session

This keeps the secret key server-side only.
"""
import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load from environment (never hardcode)
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")

stripe = None
try:
    import stripe as stripe_lib
    stripe = stripe_lib
    if STRIPE_SECRET_KEY:
        stripe.api_key = STRIPE_SECRET_KEY
except ImportError:
    print("Warning: stripe module not installed. Run: pip install stripe")

# Product catalog (price in cents)
PRODUCTS = {
    "points_500":   {"name": "Starter Pack - 500 Tree Points",   "amount": 499,  "currency": "usd"},
    "points_1300":  {"name": "Value Pack - 1,300 Tree Points",    "amount": 999,  "currency": "usd"},
    "points_3500":  {"name": "Mega Pack - 3,500 Tree Points",     "amount": 2499, "currency": "usd"},
    "coins_1000":   {"name": "Coin Pouch - 1,000 Tree Coins",     "amount": 299,  "currency": "usd"},
    "coins_3500":   {"name": "Coin Chest - 3,500 Tree Coins",     "amount": 799,  "currency": "usd"},
    "coins_12000":  {"name": "Coin Vault - 12,000 Tree Coins",    "amount": 1999, "currency": "usd"},
}


@app.route("/config", methods=["GET"])
def config():
    return jsonify({"publishableKey": STRIPE_PUBLISHABLE_KEY})


@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    if not stripe or not STRIPE_SECRET_KEY:
        return jsonify({"error": "Stripe not configured. Set STRIPE_SECRET_KEY env var."}), 500
    data = request.get_json() or {}
    product_key = data.get("product")
    if product_key not in PRODUCTS:
        return jsonify({"error": "Unknown product"}), 400
    product = PRODUCTS[product_key]
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": product["currency"],
                    "product_data": {"name": product["name"]},
                    "unit_amount": product["amount"],
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=data.get("success_url", "http://localhost:8000/store.html?success=1"),
            cancel_url=data.get("cancel_url", "http://localhost:8000/store.html?cancel=1"),
            metadata={"product_key": product_key, "user": data.get("user", "guest")},
        )
        return jsonify({"sessionId": session.id, "url": session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/webhook", methods=["POST"])
def webhook():
    # Handle Stripe webhooks (payment success, etc.)
    if not stripe:
        return "", 500
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", "")
    # In production, verify signature with STRIPE_WEBHOOK_SECRET
    try:
        event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            print(f"Payment completed: {session.get('id')} for {session.get('metadata', {}).get('product_key')}")
        return "", 200
    except Exception as e:
        return str(e), 400


if __name__ == "__main__":
    if not STRIPE_SECRET_KEY:
        print("WARNING: STRIPE_SECRET_KEY not set. Payments will fail.")
        print("Set it with: set STRIPE_SECRET_KEY=sk_test_...")
    print(f"Stripe backend running on http://localhost:5000")
    print(f"Publishable key configured: {bool(STRIPE_PUBLISHABLE_KEY)}")
    app.run(host="0.0.0.0", port=5000, debug=True)
