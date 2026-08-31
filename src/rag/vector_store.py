"""
Módulo de Indexação Vetorial e Busca Semântica RAG (Guardiã AI)
Gerencia o armazenamento vetorial com SentenceTransformers / TF-IDF híbrido para recuperação de diretrizes.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.rag.document_loader import DocumentChunk, load_protocol_documents


class HybridVectorStore:
    """
    Índice vetorial semântico híbrido de alta performance com suporte a busca neural e lexical.
    """

    def __init__(self, use_neural_embeddings: bool = True):
        self.chunks: List[DocumentChunk] = []
        self.use_neural = use_neural_embeddings
        self.embedder = None
        self.embeddings: np.ndarray = None
        self.tfidf_vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        self.tfidf_matrix = None
        self._is_indexed = False

    def build_index(self, chunks: List[DocumentChunk] = None):
        """
        Carrega os documentos e constrói as matrizes de indexação vetorial.
        """
        if chunks is None:
            chunks = load_protocol_documents()

        self.chunks = chunks
        if not self.chunks:
            print("[RAG] Nenhum documento encontrado para indexação.")
            return

        corpus = [f"{c.doc_title} {c.section_title}\n{c.content}" for c in self.chunks]

        # 1. Indexação Léxica TF-IDF
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus)

        # 2. Indexação Neural com SentenceTransformers se disponível
        if self.use_neural:
            try:
                from sentence_transformers import SentenceTransformer
                if self.embedder is None:
                    # Modelo multilíngue leve e de alta acurácia
                    self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
                self.embeddings = self.embedder.encode(corpus, convert_to_numpy=True, normalize_embeddings=True)
            except Exception as e:
                print(f"[RAG] Aviso: Falha ao carregar SentenceTransformer ({e}). Utilizando TF-IDF.")
                self.use_neural = False

        self._is_indexed = True
        print(f"[RAG] Índice construído com sucesso! {len(self.chunks)} fragmentos indexados.")

    def search(self, query: str, top_k: int = 3) -> List[Tuple[DocumentChunk, float]]:
        """
        Realiza busca semântica no corpus e retorna os Top-K fragmentos com scores de relevância.
        """
        if not self._is_indexed:
            self.build_index()

        if not self.chunks:
            return []

        # Vetorização da consulta
        query_tfidf = self.tfidf_vectorizer.transform([query])
        tfidf_scores = cosine_similarity(query_tfidf, self.tfidf_matrix)[0]

        if self.use_neural and self.embeddings is not None and self.embedder is not None:
            try:
                query_emb = self.embedder.encode([query], convert_to_numpy=True, normalize_embeddings=True)
                neural_scores = cosine_similarity(query_emb, self.embeddings)[0]
                # Fusão de scores: 70% Neural Semântico + 30% Léxico TF-IDF
                final_scores = (0.70 * neural_scores) + (0.30 * tfidf_scores)
            except Exception:
                final_scores = tfidf_scores
        else:
            final_scores = tfidf_scores

        # Obter índices ordenados por maior relevância
        top_indices = np.argsort(final_scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(final_scores[idx])
            results.append((self.chunks[idx], score))

        return results


# Instância singleton global do Vector Store para reaproveitamento em memória
_GLOBAL_VECTOR_STORE = None


def get_vector_store() -> HybridVectorStore:
    """Retorna a instância singleton do Vector Store."""
    global _GLOBAL_VECTOR_STORE
    if _GLOBAL_VECTOR_STORE is None:
        _GLOBAL_VECTOR_STORE = HybridVectorStore(use_neural_embeddings=True)
        _GLOBAL_VECTOR_STORE.build_index()
    return _GLOBAL_VECTOR_STORE
