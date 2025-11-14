# app/rag/rag_indexer.py

"""
rag_indexer.py
----------------------------------
Builds or updates a FAISS index from uploaded Markdown files.
Markdown files are not saved; only vector embeddings and metadata are persisted.

Each chunk stores:
  - source (file name)
  - section (nearest heading)
  - hierarchy (full path of parent headings)
  - chunk_id (unique)
"""

from pathlib import Path
from typing import List, Dict
import uuid
import json
import logging
import re

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereEmbeddings

from dotenv import load_dotenv
load_dotenv()  # Carga variables de entorno desde .env si existe

# ==========================================================
# CONFIGURATION
# ==========================================================
INDEX_DIR = Path(__file__).parent.parent / "data/hotel_context_faiss_index"
CHUNK_STORE_PATH = INDEX_DIR / "chunk_store.json"
EMBED_MODEL = "embed-multilingual-light-v3.0"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


# ==========================================================
# HELPER: Parse Markdown into hierarchical sections
# ==========================================================
def parse_markdown_sections(md_text: str):
    """
    Parses Markdown text into a list of sections with hierarchical headings.
    Each section includes:
        - heading (current heading)
        - hierarchy (list of parent headings)
        - content (text under that section)
    """
    sections = []
    stack = []  # (level, heading)
    current_content = []

    def flush_section():
        if current_content:
            hierarchy = [h for _, h in stack]
            sections.append({
                "heading": stack[-1][1] if stack else "Introduction",
                "hierarchy": hierarchy,
                "content": "\n".join(current_content).strip(),
            })
            current_content.clear()

    for line in md_text.splitlines():
        heading_match = re.match(r"^(#{1,6})\s+(.*)", line.strip())
        if heading_match:
            flush_section()
            level = len(heading_match.group(1))
            heading = heading_match.group(2).strip()
            # Pop deeper or equal levels
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, heading))
        else:
            current_content.append(line)

    flush_section()
    return [s for s in sections if s["content"].strip()]


# ==========================================================
# CHUNK STORE UTILITIES
# ==========================================================
def load_chunk_store() -> Dict[str, Dict]:
    if CHUNK_STORE_PATH.exists():
        with open(CHUNK_STORE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_chunk_store(store: Dict[str, Dict]):
    with open(CHUNK_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)


# ==========================================================
# MAIN INDEXER
# ==========================================================
def index_markdown_contents(
    file_contents: List[bytes],
    filenames: List[str],
    rebuild: bool = False
):
    """
    Builds or updates the FAISS index from Markdown file contents.

    Parameters:
        file_contents : list of bytes for each uploaded file
        filenames     : list of filenames
        rebuild       : if True, rebuilds index from scratch
    """
    chunk_store = load_chunk_store()
    embeddings = CohereEmbeddings(model=EMBED_MODEL)
    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    all_chunks = []

    for content, fname in zip(file_contents, filenames):
        text = content.decode("utf-8")
        sections = parse_markdown_sections(text)

        for sec in sections:
            section_text = sec["content"]
            section_heading = sec["heading"]
            section_hierarchy = sec["hierarchy"]

            # Prepare LangChain Document
            docs = [Document(
                page_content=section_text,
                metadata={
                    "source": fname,
                    "section": section_heading,
                    "hierarchy": " > ".join(section_hierarchy)
                },
            )]

            # Split into smaller chunks
            chunked_docs = splitter.split_documents(docs)
            for c in chunked_docs:
                cid = str(uuid.uuid4())
                c.metadata["chunk_id"] = cid
                chunk_store[cid] = {
                    "text": c.page_content,
                    "metadata": c.metadata
                }
                all_chunks.append(c)

    if not all_chunks:
        logger.warning("No content found to index.")
        return {"status": "empty"}

    # Build or update FAISS
    if rebuild or not INDEX_DIR.exists():
        logger.info("Rebuilding FAISS index from scratch.")
        vectorstore = FAISS.from_documents(all_chunks, embeddings)
    else:
        vectorstore = FAISS.load_local(
            str(INDEX_DIR), embeddings, allow_dangerous_deserialization=True
        )
        vectorstore.add_documents(all_chunks)

    INDEX_DIR.mkdir(exist_ok=True)
    vectorstore.save_local(str(INDEX_DIR))
    save_chunk_store(chunk_store)

    logger.info(f"Indexed {len(all_chunks)} chunks from {len(filenames)} markdowns.")
    return {"status": "success", "chunks_indexed": len(all_chunks)}


# ==========================================================
# EXAMPLE EXECUTION (for manual testing)
# ==========================================================
if __name__ == "__main__":
    # Example usage: simulate uploaded files
    md_text = b"""
# Accommodations
## Beachfront Suites
### Amenities
Private terrace, king bed, ocean view.
### Policies
No pets allowed.
"""
    result = index_markdown_contents([md_text], ["itzana_rooms.md"], rebuild=True)
    print(result)
