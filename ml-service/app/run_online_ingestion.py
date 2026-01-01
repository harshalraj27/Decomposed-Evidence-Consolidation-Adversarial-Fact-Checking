from app.online_ingestion import (
    arxiv_ingestion,
    wikipedia_ingestion,
    pubmed_ingestion,
    openreview_ingestion
)

def prompt_list(msg):
    print(msg)
    vals = []
    while True:
        x = input("> ").strip()
        if not x:
            break
        vals.append(x)
    return vals

def main():
    print("Select source:")
    print("1. arxiv")
    print("2. wikipedia")
    print("3. pubmed")
    print("4. openreview")

    choice = input("> ").strip()

    if choice == "1":
        categories = prompt_list("Enter arXiv categories (empty line to finish):")
        max_results = int(input("Max results: ").strip())
        arxiv_ingestion(categories, max_results=max_results)

    elif choice == "2":
        pages = prompt_list("Enter Wikipedia page titles (empty line to finish):")
        max_pages = int(input("Max pages: ").strip())
        wikipedia_ingestion(pages, max_pages=max_pages)

    elif choice == "3":
        pmids = prompt_list("Enter PubMed PMIDs (empty line to finish):")
        max_papers = int(input("Max papers: ").strip())
        pubmed_ingestion(pmids, max_papers=max_papers)

    elif choice == "4":
        invitation = input("OpenReview venue invitation: ").strip()
        max_papers = int(input("Max papers: ").strip())
        include_reviews = input("Include reviews? (y/n): ").strip().lower() == "y"
        openreview_ingestion(
            invitation,
            max_papers=max_papers,
            include_reviews=include_reviews
        )

    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
