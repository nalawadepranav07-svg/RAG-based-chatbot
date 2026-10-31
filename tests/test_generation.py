from src.generation.answer import answer_question

class EmptyStore:
    def search(self,q): return []

def test_abstains_without_evidence():
    from src.config import Settings
    s=Settings.from_env()
    result=answer_question("What is the refund policy?",EmptyStore(),s)
    assert "couldn’t find sufficient evidence" in result.answer
    assert result.sources==[]
