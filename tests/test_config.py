from src.config import Settings

def test_default_config(monkeypatch):
    for k in ["CHUNK_SIZE","CHUNK_OVERLAP"]: monkeypatch.delenv(k,raising=False)
    s=Settings.from_env()
    assert s.chunk_size==900 and s.chunk_overlap < s.chunk_size
