from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

class EvidenceStore:
    def __init__(self, settings):
        self.settings=settings
        settings.chroma_path.mkdir(parents=True,exist_ok=True)
        self.client=chromadb.PersistentClient(path=str(settings.chroma_path))
        self.collection=self.client.get_or_create_collection("evidencedesk_chunks",metadata={"hnsw:space":"l2"})
        self.meta=self.client.get_or_create_collection("evidencedesk_documents")
        self._model=None
    @property
    def model(self):
        if self._model is None: self._model=SentenceTransformer(self.settings.embedding_model)
        return self._model
    def add_chunks(self,chunks):
        if not chunks:return
        vectors=self.model.encode([c['text'] for c in chunks],normalize_embeddings=True).tolist()
        self.collection.upsert(ids=[c['chunk_id'] for c in chunks],documents=[c['text'] for c in chunks],embeddings=vectors,metadatas=[{k:v for k,v in c.items() if k!='text'} for c in chunks])
    def register_document(self,doc):
        self.meta.upsert(ids=[doc['document_id']],documents=[doc['filename']],metadatas=[doc])
    def list_documents(self):
        data=self.meta.get(include=['metadatas'])
        return sorted(data.get('metadatas') or [],key=lambda x:x.get('filename','').lower())
    def delete_document(self,doc_id):
        self.collection.delete(where={"document_id":doc_id})
        self.meta.delete(ids=[doc_id])
    def search(self,query,top_k=None):
        if self.collection.count()==0:return []
        vector=self.model.encode([query],normalize_embeddings=True).tolist()
        res=self.collection.query(query_embeddings=vector,n_results=min(top_k or self.settings.top_k,self.collection.count()),include=['documents','metadatas','distances'])
        rows=[]
        for text,meta,distance in zip(res['documents'][0],res['metadatas'][0],res['distances'][0]):
            rows.append({**meta,'text':text,'distance':float(distance)})
        return rows
