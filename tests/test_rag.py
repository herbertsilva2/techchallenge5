"""
Testes unitários para o módulo RAG (Guardiã AI).
"""

from src.rag.document_loader import load_protocol_documents
from src.rag.vector_store import get_vector_store
from src.rag.retriever import retrieve_relevant_protocols


def test_load_protocol_documents():
    """Verifica se os arquivos de diretrizes são carregados e fragmentados."""
    chunks = load_protocol_documents()
    assert len(chunks) > 0
    first = chunks[0]
    assert hasattr(first, "chunk_id")
    assert hasattr(first, "doc_title")
    assert hasattr(first, "content")
    assert len(first.content) > 0


def test_vector_store_and_search():
    """Verifica a indexação e busca vetorial de protocolos."""
    store = get_vector_store()
    results = store.search("diabetes gestacional rastreamento", top_k=3)
    assert len(results) > 0
    top_chunk, score = results[0]
    assert score > 0.0
    assert "diabetes" in top_chunk.content.lower() or "gestacional" in top_chunk.content.lower() or "glicemia" in top_chunk.content.lower()


def test_retrieve_relevant_protocols_formatting():
    """Verifica o formato estruturado de retorno do retriever com citações."""
    res = retrieve_relevant_protocols("violência doméstica acolhimento", top_k=2)
    assert "sources" in res
    assert "context_text" in res
    assert len(res["sources"]) > 0

    first_source = res["sources"][0]
    assert "citation_id" in first_source
    assert "doc_title" in first_source
    assert "relevance_score" in first_source
