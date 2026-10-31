# Architecture decisions (2026-10-31)

- **Parser:** PyMuPDF; fast page-level text extraction. Limitation: scanned PDFs need OCR, which is not included.
- **Chunking:** page-local character windows with overlap and sentence/newline boundary preference; preserves page traceability.
- **Embeddings:** configurable SentenceTransformers model, default all-MiniLM-L6-v2, local inference.
- **Vector store:** persistent Chroma for a small local project.
- **Retrieval:** dense top-k only in MVP; no reranker or BM25 until a benchmark justifies it.
- **LLM:** optional OpenAI adapter; no-key mode returns retrieved passages, not fabricated synthesis.
- **Deployment:** Streamlit single-process local app.
- **Privacy:** local files and index; cloud transmission only when user configures an OpenAI key.
- **Evaluation:** pytest unit tests plus a starter benchmark plan; no accuracy scores claimed.
