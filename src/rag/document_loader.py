"""
Módulo de Carregamento e Fragmentação (Chunking) de Documentos Clínicos e Diretrizes (Guardiã AI)
Lê arquivos Markdown de protocolos oficiais e divide em unidades semânticas com metadados.
"""

from pathlib import Path
from typing import List, Dict, Any
import re
from src.config import DATA_PROTOCOLS_DIR


class DocumentChunk:
    """Representa um fragmento de documento com texto e metadados contextuais."""

    def __init__(
        self,
        chunk_id: str,
        doc_name: str,
        doc_title: str,
        section_title: str,
        content: str,
        metadata: Dict[str, Any] = None,
    ):
        self.chunk_id = chunk_id
        self.doc_name = doc_name
        self.doc_title = doc_title
        self.section_title = section_title
        self.content = content.strip()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_name": self.doc_name,
            "doc_title": self.doc_title,
            "section_title": self.section_title,
            "content": self.content,
            "metadata": self.metadata,
        }

    def __repr__(self) -> str:
        return f"<DocumentChunk id={self.chunk_id} doc={self.doc_name} section='{self.section_title}'>"


def load_protocol_documents(protocols_dir: Path = DATA_PROTOCOLS_DIR) -> List[DocumentChunk]:
    """
    Varre o diretório de protocolos Markdown e divide por seções (# e ##).
    """
    chunks: List[DocumentChunk] = []

    if not protocols_dir.exists():
        return chunks

    for file_path in protocols_dir.glob("*.md"):
        doc_name = file_path.stem
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Extrair título principal (# Título)
        main_title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        doc_title = main_title_match.group(1).strip() if main_title_match else doc_name.replace("_", " ").title()

        # Dividir por seções de nível 2 (## Seção)
        sections = re.split(r"(^##\s+.+$)", text, flags=re.MULTILINE)

        if len(sections) <= 1:
            # Documento sem subseções
            chunk_id = f"{doc_name}_00"
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    doc_name=doc_name,
                    doc_title=doc_title,
                    section_title="Geral",
                    content=text,
                    metadata={"source_file": file_path.name, "doc_title": doc_title},
                )
            )
            continue

        # A primeira parte antes do primeiro ## é a introdução
        intro = sections[0].strip()
        if intro:
            chunk_id = f"{doc_name}_intro"
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    doc_name=doc_name,
                    doc_title=doc_title,
                    section_title="Introdução e Objetivos",
                    content=intro,
                    metadata={"source_file": file_path.name, "doc_title": doc_title},
                )
            )

        # Iterar pelos pares (Header, Conteúdo)
        chunk_idx = 1
        for i in range(1, len(sections), 2):
            sec_header = sections[i].replace("##", "").strip()
            sec_body = sections[i + 1].strip() if i + 1 < len(sections) else ""
            full_sec_text = f"## {sec_header}\n\n{sec_body}"

            chunk_id = f"{doc_name}_{chunk_idx:02d}"
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    doc_name=doc_name,
                    doc_title=doc_title,
                    section_title=sec_header,
                    content=full_sec_text,
                    metadata={
                        "source_file": file_path.name,
                        "doc_title": doc_title,
                        "section": sec_header,
                    },
                )
            )
            chunk_idx += 1

    return chunks
