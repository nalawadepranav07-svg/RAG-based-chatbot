from pathlib import Path
import hashlib, re, uuid

def save_upload(upload,settings):
    data=upload.getvalue()
    if len(data)>settings.max_file_mb*1024*1024: raise ValueError(f"File exceeds {settings.max_file_mb} MB limit")
    if not data.startswith(b"%PDF"): raise ValueError("The uploaded file is not a valid PDF")
    digest=hashlib.sha256(data).hexdigest()
    settings.raw_pdf_dir.mkdir(parents=True,exist_ok=True)
    # Content-addressed filename avoids traversal and duplicate storage.
    path=settings.raw_pdf_dir/f"{digest}.pdf"
    if not path.exists(): path.write_bytes(data)
    return str(path),digest

def remove_document_file(document,settings,remaining_documents=()):
    digest=document.get("sha256")
    if not digest or any(d.get("sha256")==digest for d in remaining_documents): return False
    path=settings.raw_pdf_dir/f"{digest}.pdf"
    if path.exists():
        path.unlink()
        return True
    return False
