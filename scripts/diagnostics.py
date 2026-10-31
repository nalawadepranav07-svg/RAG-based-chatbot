from dotenv import load_dotenv
from src.config import Settings

def main():
    load_dotenv(); s=Settings.from_env()
    print("Configuration valid")
    print("Embedding model:",s.embedding_model)
    print("Vector path:",s.chroma_path)
    print("Raw PDF path:",s.raw_pdf_dir)
    print("Cloud LLM:","enabled" if s.openai_api_key else "disabled (extractive mode)")
if __name__=="__main__": main()
