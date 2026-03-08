from typing import Callable, Any

from voc_agent.pipeline import run_weekly_ingestion
from voc_agent.tools.query import compare_products_on_themes


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., Any]] = {
            "run_weekly_ingestion": run_weekly_ingestion,
            "compare_products_on_themes": compare_products_on_themes,
        }

    def call(self, name: str, **kwargs: Any) -> Any:
        if name not in self._tools:
            raise ValueError(f"Unknown tool: {name}")
        return self._tools[name](**kwargs)


class ClawdBotAgent:
    """
    Minimal agent facade compatible with tool-use style orchestration.
    Replace `decide_next_action` with your OpenClaw function-calling loop.
    """

    def __init__(self) -> None:
        self.registry = ToolRegistry()

    def decide_next_action(self, user_goal: str) -> tuple[str, dict]:
        goal = user_goal.lower()
        if "weekly" in goal or "ingestion" in goal:
            return "run_weekly_ingestion", {"use_seed_csv": False}
        if "better" in goal and "comfort" in goal:
            return "compare_products_on_themes", {
                "product_a": "master_buds_1",
                "product_b": "master_buds_max",
                "themes": ["Comfort/Fit", "ANC"],
            }
        return "compare_products_on_themes", {
            "product_a": "master_buds_1",
            "product_b": "master_buds_max",
            "themes": ["Sound Quality"],
        }

    def run(self, user_goal: str):
        tool_name, kwargs = self.decide_next_action(user_goal)
        return self.registry.call(tool_name, **kwargs)


if __name__ == "__main__":
    agent = ClawdBotAgent()
    print(agent.run("Run weekly ingestion"))
