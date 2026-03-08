import unittest
from unittest.mock import patch

from voc_agent.tools.query import compare_products_on_themes


class TestQuery(unittest.TestCase):
    @patch("voc_agent.tools.query.get_all_reviews")
    def test_compare_products_on_themes_grounded(self, mock_reviews):
        mock_reviews.return_value = [
            {
                "product_id": "master_buds_1",
                "sentiment": "Negative",
                "themes": "Comfort/Fit|ANC",
                "review_text": "Fit hurts after one hour",
            },
            {
                "product_id": "master_buds_max",
                "sentiment": "Positive",
                "themes": "Comfort/Fit|ANC",
                "review_text": "Very comfortable and ANC works great",
            },
        ]

        answer = compare_products_on_themes(
            "master_buds_1",
            "master_buds_max",
            ["Comfort/Fit", "ANC"],
        )

        self.assertIn("Grounded comparison", answer)
        self.assertIn("master_buds_max is currently performing better", answer)
        self.assertIn("Evidence:", answer)


if __name__ == "__main__":
    unittest.main()
