# EvidenceDesk — Document RAG Chatbot

A local-first PDF question-answering workspace. Upload PDFs, index page-aware chunks, retrieve relevant passages, and answer with page citations. When an OpenAI API key is configured, answers are generated from retrieved evidence only. Without a key, the app provides a clearly labelled extractive evidence view rather than pretending to generate an answer.

## Requirements
- Python 3.10+ (3.11 recommended)
- Internet connection on first run to download the sentence-transformers embedding model
- OpenAI API key only if you want natural-language answer generation (optional)

## Windows setup (VS Code PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```
If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again. You can also run `.venv\Scripts\python.exe -m streamlit run app.py` without activating.

## Use
1. Open the Streamlit URL shown in the terminal.
2. Upload one or more text-based PDFs in the sidebar and click **Index PDFs**.
3. Ask questions in the chat. Click citation chips to inspect exact excerpts and pages.
4. Delete a document from the library to remove its indexed chunks and stored source file.

Scanned/image-only PDFs are detected and reported; OCR is intentionally not included. Documents are stored locally in `data/raw/` and vectors in `data/chroma/`. The default embedding model is `sentence-transformers/all-MiniLM-L6-v2`; it is downloaded on first use. When OpenAI is enabled, retrieved passages and questions are sent to the configured OpenAI API. See `.env.example` and `docs/PRIVACY.md`.

## Configuration
Copy `.env.example` to `.env`. Set `OPENAI_API_KEY` and `LLM_MODEL` to enable grounded answer generation. You can change the embedding model, chunk size, overlap, retrieval count, and conservative distance threshold there. Never commit `.env` or private PDFs.

## Checks
```powershell
pytest -q
python scripts/diagnostics.py
```

## Important limitations
- This is a working educational MVP, not a certified legal, medical, or policy authority.
- Similarity distance is a retrieval signal, not a calibrated confidence score.
- Basic conflict flagging surfaces divergent evidence but does not prove that two passages logically contradict.
- PDF extraction quality varies, especially for tables, columns, and scanned pages.
- Do not upload sensitive documents to a cloud LLM unless you have permission and accept the provider's data terms.
