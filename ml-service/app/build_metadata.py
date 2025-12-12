import pandas as pd
import spacy
import json
from pathlib import Path
from io import StringIO
import threading
import logging

from .build_index import add_faiss_index, get_faiss_index
from .config import metas_file, raw_dir
from .schemas import SuccessResponse, ErrorResponse
from .local_search import load_id_to_meta

nlp = spacy.load("en_core_web_sm")
logger = logging.getLogger(__name__)

_metadata_lock = threading.Lock()

def get_new_id():
    with _metadata_lock:
        if not metas_file.exists():
            return 0
        max_id = 0
        with open(metas_file, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                max_id = max(max_id, data.get("id", 0))
        return max_id + 1

def build_metadata(content, file_name, file_type):
    metadata = []
    current_id = get_new_id()
    try:
        if file_type in [".txt", ".md"]:
            doc = nlp(content)
            for pos, sent in enumerate(doc.sents):
                sent = sent.text.strip()
                if len(sent.split()) > 60 or len(sent.split()) < 3:
                    continue
                metadata.append({
                    "id": current_id,
                    "file_name": file_name,
                    "position": pos,
                    "sentence": sent
                })
                current_id+=1

        elif file_type == ".csv":
            try:
                df = pd.read_csv(StringIO(content), encoding="utf-8", on_bad_lines="skip")
            except Exception as e:
                logger.error(f"Failed to parse CSV {file_name}: {e}")
                return [], ErrorResponse(
                    message=f"Invalid CSV format in {file_name}",
                    error_type="file_error"
                )
            if "text" not in df.columns:
                logger.warning(f"No 'text' column found in CSV: {file_name}")
                return [], ErrorResponse(
                    message=f"No 'text' column found in {file_name}. CSV files must have a 'text' column.",
                    error_type="file_error"
                )

            for row_pos, text in enumerate(df["text"].dropna()):
                csv_doc = nlp(text)
                for sent_pos, csv_sent in enumerate(csv_doc.sents):
                    sent_text = csv_sent.text.strip()
                    if len(sent_text.split()) > 60 or len(sent_text.split()) < 3:
                        continue
                    metadata.append({
                        "id": current_id,
                        "file_name": file_name,
                        "position": sent_pos,
                        "sentence": sent_text
                    })
                    current_id += 1
        else:
            return [], ErrorResponse(message=f"Unsupported file type: {file_type}")

        with _metadata_lock:
            with open(metas_file, "a", encoding="utf-8") as f:
                for data in metadata:
                    f.write(json.dumps(data, ensure_ascii=False) + "\n")

        logger.info(f"Successfully processed {file_name}: {len(metadata)} sentences extracted")

        return metadata, None

    except Exception as e:
        logger.error(f"Unexpected error processing {file_name}: {str(e)}")
        return [], ErrorResponse(
            message=f"Failed to process {file_name}: {str(e)}",
            error_type="system"
        )
"""
def upload_file(content, file_name, file_type):
    logger.info(f"Starting upload process for {file_name}")

    try:
        save_path = Path(raw_dir)
        file_path = save_path / file_name

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.debug(f"File saved to disk: {file_path}")

        metadata, error = build_metadata(content, file_name, file_type)

        if error is not None:
            logger.error(f"Metadata processing failed for {file_name}: {error.message}")
            raise error.to_http_exception()

        if metadata:
            try:
                add_faiss_index(metadata)
                load_id_to_meta()
                logger.info(f"FAISS index updated for {file_name}")
            except Exception as e:
                logger.error(f"FAISS indexing failed for {file_name}: {e}")
                return ErrorResponse(
                    message=f"File uploaded but search indexing failed: {str(e)}",
                    error_type="system"
                )

            logger.info(f"Upload completed successfully for {file_name}")
            return SuccessResponse(
                file_name=file_name,
                sentences_added=len(metadata),
                max_id=metadata[-1]["id"] if metadata else None
            )
        else:
            return ErrorResponse(
                message=f"No valid content found in {file_name}",
                error_type="processing"
            )
    except PermissionError:
        logger.error(f"Permission denied saving {file_name}")
        return ErrorResponse(
            message="Permission denied saving file",
            error_type="system"
        )
    except Exception as e:
        logger.error(f"Unexpected error in upload_file for {file_name}: {str(e)}")
        return ErrorResponse(
            message=f"Upload failed: {str(e)}",
            error_type="system"
        )
"""

def initialize_metadata():
    files = [f for f in raw_dir.iterdir() if f.suffix.lower() in [".txt", ".md"]]

    i = 0
    metadata = []
    for file in files:
        try:
            text = file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Could not read {file}: {e}")
            continue

        doc = nlp(text)

        for pos, sent in enumerate(doc.sents):
            sent = sent.text.strip()
            if len(sent.split()) > 60 or len(sent.split()) < 3:
                continue
            metadata.append({
                "id": i,
                "file_name": file.name,
                "position": pos,
                "sentence": sent
            })
            i+=1

    csv_files = [f for f in raw_dir.iterdir() if f.suffix.lower() in [".csv"]]
    for file in csv_files:
        try:
            df = pd.read_csv(file, encoding="utf-8", on_bad_lines="skip")
        except Exception as e:
            print(f" Failed to load {file.name}: {e}")
            continue
        if "text" not in df.columns:
            print(f" Skipping {file.name}: no 'text' column found")
            continue

        for row_pos, text in enumerate(df["text"].dropna()):
            csv_doc = nlp(text)
            for sent_pos, csv_sent in enumerate(csv_doc.sents):
                sent = csv_sent.text.strip()
                if len(sent.split()) > 60 or len(sent.split()) < 3:
                    continue
                metadata.append({
                    "id": i,
                    "file_name": file.name,
                    "position": sent_pos,
                    "sentence": sent
                })
                i+=1

    with open(metas_file, "w", encoding="utf-8") as f:
        for data in metadata:
            f.write(json.dumps(data, ensure_ascii = False) + "\n")

if not Path(metas_file).exists():
    initialize_metadata()