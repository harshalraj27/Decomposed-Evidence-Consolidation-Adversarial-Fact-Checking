from fastapi import FastAPI, Query, File, UploadFile
from pathlib import Path
import logging
from .local_search import search_query
from .build_metadata import upload_file
from .schemas import SuccessResponse, ErrorResponse, handle_response, SearchResponse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
app = FastAPI(title="Document Search API", version="1.0.0")


@app.get("/")
def root():
    logger.info("Health check endpoint accessed")
    return {"message": "ML service is running 🚀"}


@app.get("/search", response_model=SearchResponse)
def search(
    query: str = Query(..., description="Search Query"),
    k: int = Query(default=5, ge=1, le=100, description="Number of citations")
):
    try:
        citations = search_query(query, k)
        logger.info(f"Search completed: {len(citations)} results returned")
        return {"status": "success", "results": citations}
    except Exception as e:
        logger.error(f"Search failed for query '{query}': {str(e)}")
        raise ErrorResponse(
            message="Search failed due to internal error",
            error_type="system"
        ).to_http_exception()


@app.post(
    "/createfile",
    response_model=SuccessResponse,
    responses={422: {"model": ErrorResponse}, 400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def create_file(file: UploadFile = File(...)):
    logger.info(f"File upload started: {file.filename} ({file.content_type})")

    if not file.filename:
        logger.warning("Upload attempted without filename")
        raise ErrorResponse(
            message="No filename provided",
            error_type="validation"
        ).to_http_exception()

    file_extension = Path(file.filename).suffix.lower()
    logger.debug(f"Detected file extension: {file_extension}")

    if file_extension not in ['.txt', '.md', '.csv']:
        logger.warning(f"Unsupported file type attempted: {file_extension}")
        raise ErrorResponse(
            message=f"Unsupported file type: {file_extension}. Supported types: .txt, .md, .csv",
            error_type="validation"
        ).to_http_exception()

    try:
        content = await file.read()
        logger.debug(f"File read successfully: {len(content)} bytes")

        try:
            text_content = content.decode("utf-8")
        except UnicodeDecodeError:
            logger.error(f"File encoding error for {file.filename}")
            raise ErrorResponse(
                message="File must be valid UTF-8 text",
                error_type="file_error"
            ).to_http_exception()

        response = upload_file(text_content, file.filename, file_extension)
        return handle_response(response)

    except Exception as e:
        logger.error(f"Unexpected error processing {file.filename}: {str(e)}")
        raise ErrorResponse(
            message="Internal server error occurred",
            error_type="system"
        ).to_http_exception()


@app.on_event("startup")
async def startup_event():
    logger.info("Document Search API is starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Document Search API is shutting down...")