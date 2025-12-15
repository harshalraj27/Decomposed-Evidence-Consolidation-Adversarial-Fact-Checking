import json
import logging
import wikipediaapi
import arxiv
import openreview

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize

from .build_index import get_faiss_index
from .config import *
from .schemas import ErrorResponse
from .build_metadata import build_metadata

logger = logging.getLogger(__name__)
model = SentenceTransformer(gte)

id_to_meta = {}

def arxiv_ingestion(categories):
    if not categories:
        return

    client = arxiv.Client()
    seen_ids = set()

    for category in categories:
        search = arxiv.Search(
            query=f"cat:{category}",
            max_results=100,
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

            data = {
                "source_type": "arxiv",
                "source_url": result.entry_id,
                "pdf_url": result.pdf_url,
                "id": arxiv_id,
                "file_name": f"arxiv_{arxiv_id}.pdf",
                "primary_category": result.primary_category,
                "all_categories": result.categories,
                "credibility": credibility,
                "comment": result.comment,
                "reference": result.journal_ref,
                "doi": result.doi,
            }

            try:
                result.download_pdf(dirpath=ingested_dir)

                meta_path = ingested_meta_dir / f"arxiv_{arxiv_id}.meta.json"
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)

            except Exception as e:
                ErrorResponse(e)





            




