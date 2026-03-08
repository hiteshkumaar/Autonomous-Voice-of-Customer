import tempfile
import unittest
from pathlib import Path

from voc_agent.tools.reports import write_action_report


class TestReports(unittest.TestCase):
    def test_write_action_report_creates_markdown(self):
        rows = [
            {
                "product_name": "Master Buds 1",
                "sentiment": "Negative",
                "themes": "Battery Life|ANC",
                "review_text": "Battery drains too fast with ANC on",
            },
            {
                "product_name": "Master Buds Max",
                "sentiment": "Positive",
                "themes": "Comfort/Fit|ANC",
                "review_text": "Very comfortable and strong ANC",
            },
        ]

        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "report.md"
            write_action_report(rows, out, "Unit Test Report")
            self.assertTrue(out.exists())
            text = out.read_text(encoding="utf-8")
            self.assertIn("Unit Test Report", text)
            self.assertIn("Department Action Items", text)
            self.assertIn("Evidence Snippets", text)


if __name__ == "__main__":
    unittest.main()
