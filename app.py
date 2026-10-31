from __future__ import annotations
import os
import streamlit as st
from dotenv import load_dotenv
from src.config import Settings
from src.ingestion.pdf import ingest_pdf
from src.retrieval.store import EvidenceStore
from src.generation.answer import answer_question
from src.utils.files import save_upload, remove_document_file

load_dotenv()
settings = Settings.from_env()
st.set_page_config(page_title="EvidenceDesk", page_icon="📚", layout="wide")

@st.cache_resource
def get_store():
    return EvidenceStore(settings)

store = get_store()
if "messages" not in st.session_state: st.session_state.messages = []
if "notice" not in st.session_state: st.session_state.notice = None

st.markdown("""<style>
.block-container{padding-top:2rem;max-width:1440px}.ed-muted{color:#687386;font-size:.9rem}
[data-testid="stSidebar"]{background:#f7f8fb}.stChatMessage{border:1px solid #e7eaf0;border-radius:14px}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.title("📚 EvidenceDesk")
    st.caption("Answers grounded in your documents")
    st.divider()
    st.subheader("Add documents")
    uploads = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)
    if st.button("Index PDFs", type="primary", disabled=not uploads, use_container_width=True):
        progress = st.progress(0)
        status = st.empty()
        for i, upload in enumerate(uploads):
            try:
                status.write(f"Processing {upload.name}…")
                path, digest = save_upload(upload, settings)
                result = ingest_pdf(path, upload.name, digest, settings)
                if result.chunks:
                    store.add_chunks(result.chunks)
                    store.register_document(result.document)
                    status.success(f"Indexed {upload.name} — {result.document['page_count']} pages, {len(result.chunks)} chunks")
                else:
                    status.warning(f"{upload.name}: no extractable text found. Scanned PDFs need OCR before indexing.")
                    if os.path.exists(path): os.remove(path)
            except Exception as exc:
                status.error(f"Could not index {upload.name}: {exc}")
            progress.progress((i+1)/len(uploads))
        st.rerun()
    st.divider()
    st.subheader("Knowledge base")
    docs = store.list_documents()
    st.caption(f"{len(docs)} indexed document(s)")
    if not docs: st.info("Your library is empty. Add a PDF to get started.")
    for doc in docs:
        with st.container(border=True):
            st.markdown(f"**{doc['filename']}**")
            st.caption(f"{doc['page_count']} pages · {doc['chunk_count']} chunks")
            if st.button("Delete", key=f"delete_{doc['document_id']}", type="secondary"):
                st.session_state[f"confirm_{doc['document_id']}"] = True
            if st.session_state.get(f"confirm_{doc['document_id']}"):
                st.warning("This removes the PDF and all its indexed passages.")
                c1,c2=st.columns(2)
                if c1.button("Confirm",key=f"yes_{doc['document_id']}"):
                    store.delete_document(doc['document_id'])
                    remove_document_file(doc, settings, store.list_documents())
                    st.session_state.pop(f"confirm_{doc['document_id']}",None)
                    st.rerun()
                if c2.button("Cancel",key=f"no_{doc['document_id']}"):
                    st.session_state.pop(f"confirm_{doc['document_id']}",None); st.rerun()
    st.divider()
    st.caption("Privacy: PDFs and index are stored locally. Cloud LLM use is optional and disclosed in Settings below.")

st.title("Your document workspace")
st.markdown("Ask questions across your indexed PDFs. Every factual answer should be traceable to a source page.")
if not docs:
    st.info("**Start here:** upload a PDF from the left sidebar, then index it. You can ask questions across multiple documents once indexing finishes.")
    st.markdown("**Try asking:**\n- What are the main topics covered?\n- Summarize the eligibility criteria.\n- Which deadlines are mentioned, and where?")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("Evidence used"):
                for source in msg["sources"]:
                    st.markdown(f"**[{source['citation_id']}] {source['filename']} — page {source['page']}**")
                    st.write(source['text'])
                    st.caption(f"Chunk: {source['chunk_id']} · similarity distance: {source['distance']:.3f}")

question = st.chat_input("Ask a question about your documents…", disabled=not docs)
if question:
    st.session_state.messages.append({"role":"user","content":question})
    with st.chat_message("user"): st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Searching your documents and checking evidence…"):
            result = answer_question(question, store, settings)
        st.markdown(result.answer)
        if result.sources:
            with st.expander(f"Evidence used ({len(result.sources)} passages)", expanded=True):
                for source in result.sources:
                    st.markdown(f"**[{source['citation_id']}] {source['filename']} — page {source['page']}**")
                    st.write(source['text'])
                    st.caption(f"Chunk: {source['chunk_id']} · similarity distance: {source['distance']:.3f}")
        if result.conflict: st.warning("Potentially conflicting passages were retrieved. Review both sources before relying on this answer.")
    st.session_state.messages.append({"role":"assistant","content":result.answer,"sources":result.sources})

with st.expander("Settings & processing disclosure"):
    st.write(f"**Embedding model:** `{settings.embedding_model}`")
    st.write(f"**Retrieval:** top {settings.top_k} · maximum L2 distance {settings.max_distance}")
    if settings.openai_api_key:
        st.success(f"Cloud generation enabled: questions and retrieved excerpts are sent to OpenAI model `{settings.llm_model}`.")
    else:
        st.info("No OPENAI_API_KEY configured. EvidenceDesk runs in local extractive mode and will not call a cloud LLM.")
    st.write("Scanned PDF OCR is not enabled. Similarity distance is not a confidence percentage.")
