from app.claim_pipeline import claim_wrapper

COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_GRAY = "\033[90m"


def color_verdict(v):
    if v == "SUPPORT":
        return COLOR_GREEN + v + COLOR_RESET
    if v == "CONTRADICT":
        return COLOR_RED + v + COLOR_RESET
    if v == "MIXED":
        return COLOR_YELLOW + v + COLOR_RESET
    return COLOR_GRAY + v + COLOR_RESET


def print_separator():
    print("-" * 80)


def pretty_print_result(result):
    print_separator()
    print("CLAIM:")
    print(result["claim"])
    print_separator()

    print("FINAL VERDICT:")
    print(color_verdict(result["verdict"]))
    print_separator()

    print("SUMMARY:")
    print(result["explanation"]["summary"])
    print_separator()

    for section in result["explanation"]["sections"]:
        section_type = section["type"].replace("_", " ").title()
        print(COLOR_BLUE + section_type + COLOR_RESET)
        print_separator()

        for idx, item in enumerate(section["items"], start=1):
            print(f"{idx}. Subclaim:")
            print(f"   {item['subclaim']}")
            print(f"   Verdict: {color_verdict(item['verdict'])}")
            print(
                f"   Strength → Support: {item['strength_summary']['support']}, "
                f"Contradict: {item['strength_summary']['contradict']}"
            )

            evidence = item["evidence"]

            for ev_type in ["supporting", "contradicting", "neutral"]:
                ev_list = evidence.get(ev_type, [])
                if not ev_list:
                    continue

                print(f"\n   {ev_type.title()} Evidence:")
                for ev in ev_list:
                    excerpt = ev.get("excerpt", "").strip()
                    if len(excerpt) > 300:
                        excerpt = excerpt[:300] + "..."

                    print("     - Source:", ev.get("source_title", "N/A"))
                    print("       URL   :", ev.get("source_url", "N/A"))
                    print("       Stance:", ev.get("stance", "N/A"))
                    print(
                        "       Scores → "
                        f"FAISS: {round(ev.get('faiss_score', 0.0), 4)} | "
                        f"Rerank: {round(ev.get('rerank_score', 0.0), 4)} | "
                        f"NLI: {round(ev.get('nli_score', 0.0), 4)} | "
                        f"Cred: {round(ev.get('source_credibility', 0.0), 4)} | "
                        f"Combined: {round(ev.get('combined_rank_score', 0.0), 4)}"
                    )
                    print("       Excerpt:")
                    print("        ", excerpt)

            print_separator()


def main():
    claim = input("Enter a claim to verify:\n> ").strip()

    if not claim:
        print("No claim provided.")
        return

    result = claim_wrapper(claim)
    pretty_print_result(result)


if __name__ == "__main__":
    main()
