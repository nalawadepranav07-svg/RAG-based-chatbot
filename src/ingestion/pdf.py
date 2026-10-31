from pathlib import Path
import hashlib, re, uuid
import fitz
from dataclasses import dataclass

@dataclass
class IngestionResult:
    document: dict
    chunks: list[dict]

def _clean(text: str) -> str:
    text=text.replace("\x00", " ").replace("\u00ad", "")
    return re.sub(r"[ \t]+", " ", text).strip()

def ingest_pdf(path: str|Path, filename: str, digest: str, settings) -> IngestionResult:
    path=Path(path)
    if path.suffix.lower() != ".pdf": raise ValueError("Only PDF files are supported")
    doc_id=hashlib.sha256((digest+filename).encode()).hexdigest()[:24]
    pages=[]
    try:
        pdf=fitz.open(path)
        if pdf.is_encrypted and not pdf.authenticate(""): raise ValueError("Encrypted PDF is not supported")
        if pdf.page_count == 0: raise ValueError("PDF has no pages")
        for index,page in enumerate(pdf):
            text=_clean(page.get_text("text"))
            if text: pages.append((index+1,text))
        page_count=pdf.page_count; pdf.close()
    except Exception as exc:
        raise ValueError(f"PDF extraction failed: {exc}") from exc
    chunks=[]
    for page_no,text in pages:
        start=0
        while start < len(text):
            end=min(start+settings.chunk_size,len(text))
            if end < len(text):
                boundary=max(text.rfind(". ",start,end),text.rfind("\n",start,end),text.rfind("; ",start,end))
                if boundary > start+settings.chunk_size//2: end=boundary+1
            part=text[start:end].strip()
            if part:
                chunk_id=hashlib.sha256(f"{doc_id}:{page_no}:{start}:{part}".encode()).hexdigest()[:24]
                chunks.append({"document_id":doc_id,"chunk_id":chunk_id,"filename":filename,"page":page_no,"text":part,"start":start,"end":end,"content_hash":hashlib.sha256(part.encode()).hexdigest()})
            if end >= len(text): break
            start=max(start+1,end-settings.chunk_overlap)
    document={"document_id":doc_id,"filename":filename,"sha256":digest,"page_count":page_count,"chunk_count":len(chunks),"status":"indexed"}
    return IngestionResult(document,chunks)
