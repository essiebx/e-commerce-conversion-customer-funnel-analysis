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
        self.assertEqual(purchase, 1 / 3)

    def test_revenue_opportunity_has_every_transition(self):
        opportunity = revenue_opportunity(self.frame)
        self.assertEqual(len(opportunity), 4)


if __name__ == "__main__":
    unittest.main()
