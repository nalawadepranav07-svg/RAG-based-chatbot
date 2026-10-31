from dataclasses import dataclass
from pathlib import Path
import os

@dataclass(frozen=True)
class Settings:
    embedding_model: str
    chroma_path: Path
    raw_pdf_dir: Path
    chunk_size: int
    chunk_overlap: int
    top_k: int
    max_distance: float
    max_file_mb: int
    openai_api_key: str | None
    llm_model: str

    @classmethod
    def from_env(cls):
        chunk_size=int(os.getenv("CHUNK_SIZE","900")); overlap=int(os.getenv("CHUNK_OVERLAP","150"))
        if chunk_size < 100 or overlap < 0 or overlap >= chunk_size: raise ValueError("CHUNK_SIZE must be >=100 and CHUNK_OVERLAP must be smaller than CHUNK_SIZE")
        return cls(os.getenv("EMBEDDING_MODEL","sentence-transformers/all-MiniLM-L6-v2"),Path(os.getenv("CHROMA_PATH","data/chroma")),Path(os.getenv("RAW_PDF_DIR","data/raw")),chunk_size,overlap,int(os.getenv("TOP_K","5")),float(os.getenv("MAX_DISTANCE","1.35")),int(os.getenv("MAX_FILE_MB","25")),os.getenv("OPENAI_API_KEY") or None,os.getenv("LLM_MODEL","gpt-4o-mini"))
