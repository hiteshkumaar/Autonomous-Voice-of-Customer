from voc_agent.tools.query import compare_products_on_themes, quick_theme_heatmap


if __name__ == "__main__":
    print("Voice of Customer Analyst CLI")
    print("Commands: compare, heatmap, exit")
    while True:
        cmd = input("> ").strip().lower()
        if cmd == "exit":
            break
        if cmd == "heatmap":
            print(quick_theme_heatmap())
            continue
        if cmd == "compare":
            a = input("Product A id: ").strip()
            b = input("Product B id: ").strip()
            themes = input("Themes comma separated: ").strip().split(",")
            print(compare_products_on_themes(a, b, [t.strip() for t in themes if t.strip()]))
            continue
        print("unknown command")
