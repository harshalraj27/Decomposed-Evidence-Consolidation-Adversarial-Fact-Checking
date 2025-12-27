import json
import logging
import wikipediaapi
import openreview
from Bio import Entrez
import arxiv

from .config import *
from .schemas import ErrorResponse
from .build_metadata import build_metadata

logger = logging.getLogger(__name__)
Entrez.email = "harshalraj27@gmail.com"


PRIMARY_CATEGORY_PRIORITY = [
    "natural language processing",
    "machine learning",
    "artificial intelligence",
    "deep learning",
    "neural networks"
]

def write_meta(doc_id, meta):
    meta_path = ingested_meta_dir / f"{doc_id}.meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4)

def _collect_sections(section, drop_titles, out):
    if section.title.lower() not in drop_titles:
        if section.text:
            out.append(section.text)
    for sub in section.sections:
        _collect_sections(sub, drop_titles, out)

def infer_primary_category(categories):
    normalized = [c.lower().replace("category:", "").strip() for c in categories]

    for target in PRIMARY_CATEGORY_PRIORITY:
        for c in normalized:
            if target in c:
                return target

    return normalized[0] if normalized else None

def arxiv_ingestion(categories, max_results=20):
    if not categories:
        return []

    client = arxiv.Client()
    seen_ids = set()
    ingested_ids = []

    for category in categories:
        search = arxiv.Search(
            query=f"cat:{category}",
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )

        for result in client.results(search):
            arxiv_id = result.get_short_id()
            if arxiv_id in seen_ids:
                continue
            seen_ids.add(arxiv_id)

            credibility = 0.7
            if result.journal_ref:
                credibility += 0.2
            if result.comment and "accepted" in result.comment.lower():
                credibility += 0.1
            if result.doi:
                credibility += 0.1
            credibility = min(1.0, credibility)

            doc_id = f"arxiv_{arxiv_id}"

            meta = {
                "source_type": "arxiv",
                "doc_id": doc_id,
                "title": result.title,
                "source_url": result.entry_id,
                "pdf_url": result.pdf_url,
                "primary_category": result.primary_category,
                "all_categories": result.categories,
                "journal_ref": result.journal_ref,
                "comment": result.comment,
                "doi": result.doi,
                "credibility": credibility
            }

            try:
                result.download_pdf(dirpath=ingested_pdf_dir)
                write_meta(doc_id, meta)
                ingested_ids.append(arxiv_id)

            except Exception as e:
                logger.error(f"arXiv ingestion failed for {arxiv_id}: {e}")
                ErrorResponse(e)

    return ingested_ids

def wikipedia_ingestion(pages, max_pages=10, min_chars=500, max_chars=50_000):
    wiki = wikipediaapi.Wikipedia(
        user_agent="FactAnchor/0.1 (research project; contact: harshalraj27@gmail.com)",
        language=wiki_language,
        extract_format=wikipediaapi.ExtractFormat.WIKI
    )

    DROP_SECTIONS = {
        "see also",
        "references",
        "external links",
        "further reading"
    }

    count = 0
    for title in pages:
        if count >= max_pages:
            break

        page = wiki.page(title)
        if not page.exists():
            continue

        categories = list(page.categories.keys())
        primary_category = infer_primary_category(categories)

        sections = []
        for sec in page.sections:
            _collect_sections(sec, DROP_SECTIONS, sections)

        full_text = "\n\n".join(sections)[:max_chars]
        if len(full_text.strip()) < min_chars:
            continue

        doc_id = f"wiki_{title.replace(' ', '_')}"

        meta = {
            "source_type": "wikipedia",
            "doc_id": doc_id,
            "title": page.title,
            "source_url": page.fullurl,
            "categories": categories,
            "primary_category": primary_category,
            "credibility": 0.6
        }

        try:
            write_meta(doc_id, meta)

            build_metadata(
                content=full_text,
                file_name=doc_id,
                file_type=".txt",
                source_type="wikipedia",
                credibility=meta["credibility"],
                extra_meta=meta,
                already_split=False
            )

            count += 1

        except Exception as e:
            logger.error(f"Wikipedia ingestion failed for {doc_id}: {e}")
            ErrorResponse(e)

def pubmed_ingestion(pmids, max_papers=10, prefer_abstract=True, max_chars=40_000):
    count = 0

    for pmid in pmids:
        if count >= max_papers:
            break

        try:
            handle = Entrez.efetch(
                db="pubmed",
                id=pmid,
                rettype="xml",
                retmode="text"
            )

            records = Entrez.read(handle)
            handle.close()

            article = records["PubmedArticle"][0]["MedlineCitation"]["Article"]

            abstract = " ".join(
                str(x) for x in article.get("Abstract", {}).get("AbstractText", [])
            )

            full_text = abstract

            pmc_id = None
            for iden in records["PubmedArticle"][0]["PubmedData"]["ArticleIdList"]:
                if iden.attributes.get("IdType") == "pmc":
                    pmc_id = str(iden)

            if pmc_id and not prefer_abstract:
                pmc_handle = Entrez.efetch(
                    db="pmc",
                    id=pmc_id,
                    rettype="full",
                    retmode="text"
                )
                pmc_text = pmc_handle.read()
                pmc_handle.close()

                if pmc_text:
                    full_text = pmc_text

            full_text = full_text[:max_chars]
            if len(full_text) < 500:
                continue

            doc_id = f"pubmed_{pmid}"

            meta = {
                "source_type": "pubmed",
                "doc_id": doc_id,
                "title": article.get("ArticleTitle", ""),
                "journal": article["Journal"]["Title"],
                "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "pmc_id": pmc_id,
                "credibility": 0.8
            }

            write_meta(doc_id, meta)

            build_metadata(
                content=full_text,
                file_name=doc_id,
                file_type=".txt",
                source_type="pubmed",
                credibility=meta["credibility"],
                extra_meta=meta,
                already_split=False
            )

            count += 1

        except Exception as e:
            logger.error(f"PubMed ingestion failed for {pmid}: {e}")
            ErrorResponse(e)

def openreview_ingestion(invitation, max_papers=20, include_reviews=False):
    client = openreview.Client(baseurl="https://api.openreview.net")

    notes = client.get_all_notes(
        content={"venueid": invitation}
    )
    count = 0
    for note in notes:
        if count >= max_papers:
            break

        try:
            parts = []

            if note.content.get("abstract"):
                parts.append(note.content["abstract"])

            if include_reviews:
                reviews = client.get_notes(
                    forum=note.id,
                    invitation="*/-/Official_Review"
                )
                for r in reviews:
                    if "review" in r.content:
                        parts.append(r.content["review"])

            full_text = "\n\n".join(parts)
            if len(full_text) < 500:
                continue

            doc_id = f"openreview_{note.id}"

            meta = {
                "source_type": "openreview",
                "doc_id": doc_id,
                "title": note.content.get("title", ""),
                "source_url": f"https://openreview.net/forum?id={note.id}",
                "credibility": 0.7
            }

            write_meta(doc_id, meta)

            build_metadata(
                content=full_text,
                file_name=doc_id,
                file_type=".txt",
                source_type="openreview",
                credibility=meta["credibility"],
                extra_meta=meta,
                already_split=False
            )

            count += 1

        except Exception as e:
            logger.error(f"OpenReview ingestion failed for {note.id}: {e}")
            ErrorResponse(e)