import unittest

from voc_agent.tools import nlp


class TestNLP(unittest.TestCase):
    def test_positive_sentiment_from_rating_and_text(self):
        sentiment, themes = nlp.classify_review(
            "Great sound and comfort",
            "Excellent bass and very comfortable for long usage",
            5,
        )
        self.assertEqual(sentiment, "Positive")
        self.assertIn("Sound Quality", themes)
        self.assertIn("Comfort/Fit", themes)

    def test_negative_sentiment_from_text(self):
        sentiment, themes = nlp.classify_review(
            "Battery issue",
            "Worst backup and charging problem after one week",
            2,
        )
        self.assertEqual(sentiment, "Negative")
        self.assertIn("Battery Life", themes)

    def test_neutral_when_no_clear_signal(self):
        sentiment, themes = nlp.classify_review(
            "Okay product",
            "Received product and started using it",
            3,
        )
        self.assertEqual(sentiment, "Neutral")
        self.assertGreaterEqual(len(themes), 1)


if __name__ == "__main__":
    unittest.main()
