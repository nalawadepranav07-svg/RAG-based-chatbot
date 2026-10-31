# Architecture

`Streamlit UI → PDF validation/extraction → page-aware chunker → SentenceTransformer embeddings → persistent Chroma → top-k retrieval → evidence threshold → optional OpenAI generation → citation panel`.

Each chunk stores a stable chunk ID, document ID, original filename, one-based PDF page number, offsets, and content hash. A document is listed only after chunks are embedded and the document metadata is registered. Failed extraction is surfaced in the UI. Retrieval distances are L2 distances in the normalized embedding space and are not calibrated confidence values.

Document lifecycle: uploaded → validating → extracting → chunking → embedding → indexed; errors are surfaced and the document is not registered as indexed. Deletion removes Chroma chunks and document metadata. OCR, hybrid BM25, reranking, and a formal contradiction classifier are not implemented in this MVP.
