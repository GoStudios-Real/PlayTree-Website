"""Tree Points and Tree Coins currency system for PLAYTREE."""
import json
import os

CURRENCY_FILE = "playtree_currency.json"


class CurrencySystem:
    def __init__(self):
        self.tree_points = 0
        self.tree_coins = 0
        self.load()

    def load(self):
        try:
            if os.path.exists(CURRENCY_FILE):
                with open(CURRENCY_FILE, "r") as f:
                    data = json.load(f)
                    self.tree_points = data.get("tree_points", 0)
                    self.tree_coins = data.get("tree_coins", 0)
        except Exception:
            pass

    def save(self):
        try:
            with open(CURRENCY_FILE, "w") as f:
                json.dump({"tree_points": self.tree_points, "tree_coins": self.tree_coins}, f)
        except Exception:
            pass

    def add_points(self, amount):
        self.tree_points += amount
        self.save()

    def add_coins(self, amount):
        self.tree_coins += amount
        self.save()

    def spend_points(self, amount):
        if self.tree_points >= amount:
            self.tree_points -= amount
            self.save()
            return True
        return False

    def spend_coins(self, amount):
        if self.tree_coins >= amount:
            self.tree_coins -= amount
            self.save()
            return True
        return False

    def get_balance(self):
        return self.tree_points, self.tree_coins