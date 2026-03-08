from dataclasses import dataclass
from typing import Optional


@dataclass
class ReviewRecord:
    run_id: str
    source: str
    product_id: str
    product_name: str
    review_id: str
    review_title: str
    review_text: str
    rating: Optional[float]
    review_date: str
    author: str
    sentiment: str
    themes: str
