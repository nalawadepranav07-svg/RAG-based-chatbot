# Privacy and data handling

- Uploaded PDFs are stored under `data/raw/`; Chroma vectors and metadata are stored under `data/chroma/`.
- The default embedding model runs locally after its model files are downloaded. Initial download contacts the model host.
- Without `OPENAI_API_KEY`, no cloud LLM is called; the UI returns retrieved excerpts.
- With `OPENAI_API_KEY`, the question and retrieved excerpts are sent to OpenAI through its API. Review applicable provider terms before using confidential material.
- Deleting a document removes its vector records and document-library metadata. The original content-addressed PDF is removed when no remaining library entry references its content hash.
- Logs do not include document text or API keys. This project makes no compliance certification.
