import tempfile
import unittest
from pathlib import Path

import pandas as pd

from pipeline.ingestion.validate_source import validate_retailrocket_source
from pipeline.transformation.clean_data import clean_funnel_data


class PipelineModuleTests(unittest.TestCase):
    def test_retailrocket_source_validation(self):
        frame = pd.DataFrame([
            {"timestamp": 1, "visitorid": 10, "event": "view", "itemid": 100},
            {"timestamp": 2, "visitorid": 10, "event": "addtocart", "itemid": 100},
        ])
        result = validate_retailrocket_source(frame)
        self.assertEqual(result["supported_rows"], 2)
        self.assertEqual(result["unique_visitors"], 1)

    def test_cleaning_exports_valid_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.csv"
            output = Path(directory) / "clean.csv"
            frame = pd.DataFrame([
                {"event_id": "EVT-1", "user_id": "VIS-1", "session_id": "SES-1", "event_timestamp": "2026-01-01T00:00:00Z", "campaign": "unknown", "channel": "unknown", "device": "unknown", "stage": "product_view", "cart_value": "0.00", "revenue": "0.00"},
                {"event_id": "EVT-1", "user_id": "VIS-1", "session_id": "SES-1", "event_timestamp": "2026-01-01T00:00:00Z", "campaign": "unknown", "channel": "unknown", "device": "unknown", "stage": "product_view", "cart_value": "0.00", "revenue": "0.00"},
                {"event_id": "EVT-2", "user_id": "VIS-2", "session_id": "SES-2", "event_timestamp": "not-a-date", "campaign": "unknown", "channel": "unknown", "device": "unknown", "stage": "purchase", "cart_value": "1.00", "revenue": "1.00"},
            ])
            frame.to_csv(source, index=False)
            clean, quality = clean_funnel_data(source, output)
            self.assertEqual(len(clean), 1)
            self.assertEqual(len(quality), 1)
            self.assertTrue(output.exists())


if __name__ == "__main__":
    unittest.main()
