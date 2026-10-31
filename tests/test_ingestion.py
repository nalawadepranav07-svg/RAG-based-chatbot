from pathlib import Path
import fitz
from src.ingestion.pdf import ingest_pdf
from src.config import Settings

def test_page_aware_ingestion(tmp_path,monkeypatch):
    p=tmp_path/"sample.pdf"; d=fitz.open(); page=d.new_page(); page.insert_text((72,72),"Eligibility requires a valid application."); d.save(p); d.close()
    s=Settings.from_env(); s=type(s)(**{**s.__dict__,"chunk_size":200,"chunk_overlap":20})
    r=ingest_pdf(p,"sample.pdf","abc",s)
    assert r.document['page_count']==1 and r.chunks[0]['page']==1
    assert "Eligibility" in r.chunks[0]['text']
