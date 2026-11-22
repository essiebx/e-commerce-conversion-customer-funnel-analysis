import unittest
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.analyze_funnel import funnel_summary, revenue_opportunity


class FunnelLogicTests(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame([
            {"user_id": "1", "campaign": "A", "channel": "search", "device": "mobile", "stage": "landing", "cart_value": 0, "revenue": 0},
            {"user_id": "1", "campaign": "A", "channel": "search", "device": "mobile", "stage": "product_view", "cart_value": 0, "revenue": 0},
            {"user_id": "1", "campaign": "A", "channel": "search", "device": "mobile", "stage": "cart", "cart_value": 100, "revenue": 0},
            {"user_id": "1", "campaign": "A", "channel": "search", "device": "mobile", "stage": "checkout", "cart_value": 100, "revenue": 0},
            {"user_id": "1", "campaign": "A", "channel": "search", "device": "mobile", "stage": "purchase", "cart_value": 100, "revenue": 100},
            {"user_id": "2", "campaign": "A", "channel": "search", "device": "mobile", "stage": "landing", "cart_value": 0, "revenue": 0},
            {"user_id": "2", "campaign": "A", "channel": "search", "device": "mobile", "stage": "product_view", "cart_value": 0, "revenue": 0},
            {"user_id": "3", "campaign": "A", "channel": "search", "device": "mobile", "stage": "landing", "cart_value": 0, "revenue": 0},
        ])

    def test_landing_to_purchase_is_50_percent(self):
        summary = funnel_summary(self.frame)
        landing = summary.loc[summary["stage"] == "landing", "overall_conversion_rate"].iloc[0]
        purchase = summary.loc[summary["stage"] == "purchase", "overall_conversion_rate"].iloc[0]
        self.assertEqual(landing, 1.0)
        self.assertAlmostEqual(purchase, 1 / 3, places=4)

    def test_revenue_opportunity_has_every_transition(self):
        opportunity = revenue_opportunity(self.frame)
        self.assertEqual(len(opportunity), 4)

    def test_chronological_funnel_excludes_purchase_before_cart(self):
        frame = pd.DataFrame([
            {"user_id": "1", "campaign": "A", "channel": "search", "device": "mobile", "stage": "landing", "cart_value": 0, "revenue": 0, "event_timestamp": "2026-01-01T00:00:00Z"},
            {"user_id": "1", "campaign": "A", "channel": "search", "device": "mobile", "stage": "product_view", "cart_value": 0, "revenue": 0, "event_timestamp": "2026-01-01T00:01:00Z"},
            {"user_id": "1", "campaign": "A", "channel": "search", "device": "mobile", "stage": "cart", "cart_value": 100, "revenue": 0, "event_timestamp": "2026-01-01T00:02:00Z"},
            {"user_id": "1", "campaign": "A", "channel": "search", "device": "mobile", "stage": "purchase", "cart_value": 100, "revenue": 100, "event_timestamp": "2026-01-01T00:03:00Z"},
            {"user_id": "2", "campaign": "A", "channel": "search", "device": "mobile", "stage": "landing", "cart_value": 0, "revenue": 0, "event_timestamp": "2026-01-01T00:00:00Z"},
            {"user_id": "2", "campaign": "A", "channel": "search", "device": "mobile", "stage": "product_view", "cart_value": 0, "revenue": 0, "event_timestamp": "2026-01-01T00:01:00Z"},
            {"user_id": "2", "campaign": "A", "channel": "search", "device": "mobile", "stage": "purchase", "cart_value": 100, "revenue": 100, "event_timestamp": "2026-01-01T00:02:00Z"},
        ])
        frame = pd.concat([frame], ignore_index=True)
        frame["event_timestamp"] = pd.to_datetime(frame["event_timestamp"], utc=True)
        summary = funnel_summary(frame)
        purchase_users = int(summary.loc[summary["stage"] == "purchase", "users"].iloc[0])
        self.assertEqual(purchase_users, 1)


if __name__ == "__main__":
    unittest.main()
