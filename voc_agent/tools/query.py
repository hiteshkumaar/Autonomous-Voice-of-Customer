from __future__ import annotations

from collections import Counter

from voc_agent.tools.storage import get_all_reviews


def compare_products_on_themes(product_a: str, product_b: str, themes: list[str]) -> str:
    rows = get_all_reviews()
    theme_set = {t.lower() for t in themes}

    def score(product_id: str) -> tuple[int, int, int]:
        pos = neg = total = 0
        for r in rows:
            if r.get("product_id") != product_id:
                continue
            tags = {x.strip().lower() for x in (r.get("themes") or "").split("|") if x.strip()}
            if not (tags & theme_set):
                continue
            total += 1
            if r.get("sentiment") == "Positive":
                pos += 1
            elif r.get("sentiment") == "Negative":
                neg += 1
        return pos, neg, total

    a_pos, a_neg, a_total = score(product_a)
    b_pos, b_neg, b_total = score(product_b)

    lines = [
        f"Grounded comparison on themes: {', '.join(themes)}",
        f"{product_a}: {a_pos} positive, {a_neg} negative, {a_total} total relevant reviews",
        f"{product_b}: {b_pos} positive, {b_neg} negative, {b_total} total relevant reviews",
    ]

    if b_pos - b_neg > a_pos - a_neg:
        lines.append(f"{product_b} is currently performing better than {product_a} on these themes.")
    elif b_pos - b_neg < a_pos - a_neg:
        lines.append(f"{product_a} is currently performing better than {product_b} on these themes.")
    else:
        lines.append("Both products are performing similarly on these themes.")

    evidence = []
    for r in rows:
        if r.get("product_id") not in {product_a, product_b}:
            continue
        tags = {x.strip().lower() for x in (r.get("themes") or "").split("|") if x.strip()}
        if tags & theme_set:
            evidence.append(r)
        if len(evidence) >= 6:
            break

    lines.append("Evidence:")
    for r in evidence:
        snippet = (r.get("review_text") or "").strip()[:140]
        lines.append(f"- {r.get('product_id')} [{r.get('sentiment')}]: {snippet}")

    return "\n".join(lines)


def quick_theme_heatmap() -> str:
    rows = get_all_reviews()
    c = Counter()
    for r in rows:
        for t in (r.get("themes") or "").split("|"):
            if t:
                c[(r.get("product_id"), t, r.get("sentiment"))] += 1
    lines = ["product_id,theme,sentiment,count"]
    for (p, t, s), n in sorted(c.items()):
        lines.append(f"{p},{t},{s},{n}")
    return "\n".join(lines)
