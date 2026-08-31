"""
Módulo de Recuperação Contextual e Citação de Protocolos Oficiais RAG (Guardiã AI)
Fornece métodos de busca estruturada e formatação de citações para o orquestrador LLM.
"""

from typing import List, Dict, Any
from src.config import TOP_K_PROTOCOLS
from src.rag.vector_store import get_vector_store, DocumentChunk


def retrieve_relevant_protocols(
    query: str,
    top_k: int = TOP_K_PROTOCOLS,
    min_score: float = 0.05,
) -> Dict[str, Any]:
    """
    Recupera fragmentos de protocolos clínicos e de segurança pertinentes à consulta.
    Retorna uma lista estruturada de fontes e o texto de contexto consolidado para a LLM.
    """
    store = get_vector_store()
    raw_results = store.search(query=query, top_k=top_k)

    sources: List[Dict[str, Any]] = []
    context_blocks: List[str] = []

    for i, (chunk, score) in enumerate(raw_results, 1):
        if score < min_score:
            continue

        citation_id = f"REF-{i:02d}"
        source_entry = {
            "citation_id": citation_id,
            "chunk_id": chunk.chunk_id,
            "doc_title": chunk.doc_title,
            "section_title": chunk.section_title,
            "source_file": chunk.metadata.get("source_file", ""),
            "relevance_score": round(score, 4),
            "content": chunk.content,
        }
        sources.append(source_entry)

        # Bloco formatado para inclusão no prompt
        block_text = (
            f"--- FONTE [{citation_id}]: {chunk.doc_title} | Seção: {chunk.section_title} ---\n"
            f"{chunk.content}\n"
        )
        context_blocks.append(block_text)

    consolidated_context = "\n".join(context_blocks) if context_blocks else "Nenhum protocolo específico recuperado."

    return {
        "query": query,
        "total_retrieved": len(sources),
        "sources": sources,
        "context_text": consolidated_context,
    }
