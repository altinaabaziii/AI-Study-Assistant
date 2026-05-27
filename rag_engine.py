from pathlib import Path

import faiss
import numpy as np
import torch
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


# Free and open-source models used by StudyMateAI.
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
GENERATION_MODEL_NAME = "google/flan-t5-base"


class RAGEngine:
    """A simple Retrieval-Augmented Generation engine for PDF study notes."""

    def __init__(self):
        # Load the embedding model used to turn text chunks into vectors.
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

        # Load a free HuggingFace text-to-text model for answering questions.
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(GENERATION_MODEL_NAME)
        self.generator = AutoModelForSeq2SeqLM.from_pretrained(
            GENERATION_MODEL_NAME
        ).to(self.device)

        self.chunks = []
        self.index = None

    def read_pdf(self, pdf_path):
        """Read a PDF file and return all extracted text."""
        reader = PdfReader(str(pdf_path))
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        return text

    def split_text(self, text, chunk_size=500, overlap=100):
        """Split long text into smaller overlapping chunks."""
        words = text.split()
        chunks = []
        start = 0

        while start < len(words):
            end = start + chunk_size
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start += chunk_size - overlap

        return chunks

    def build_index(self, pdf_files):
        """Create a FAISS index from one or more PDF files."""
        self.chunks = []

        for pdf_file in pdf_files:
            pdf_text = self.read_pdf(pdf_file)
            self.chunks.extend(self.split_text(pdf_text))

        if not self.chunks:
            raise ValueError("No text was extracted from the PDF files.")

        # Convert every chunk into an embedding vector.
        embeddings = self.embedding_model.encode(
            self.chunks,
            convert_to_numpy=True,
            show_progress_bar=True,
        )
        embeddings = embeddings.astype("float32")

        # FAISS uses vector similarity search to find relevant chunks quickly.
        vector_size = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(vector_size)
        self.index.add(embeddings)

    def retrieve_chunks(self, question, top_k=3):
        """Find the most relevant text chunks for a question."""
        if self.index is None:
            raise ValueError("FAISS index is empty. Run build_index() first.")

        question_embedding = self.embedding_model.encode(
            [question],
            convert_to_numpy=True,
        ).astype("float32")

        distances, indices = self.index.search(question_embedding, top_k)

        relevant_chunks = []
        for index_id in indices[0]:
            if index_id != -1:
                relevant_chunks.append(self.chunks[index_id])

        return relevant_chunks

    def ask_question(self, question, top_k=3):
        """Answer a student question using retrieved PDF context."""
        relevant_chunks = self.retrieve_chunks(question, top_k=top_k)
        context = "\n\n".join(relevant_chunks)

        prompt = (
            "Answer the question using only the context below.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Answer:"
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )
        inputs = {name: value.to(self.device) for name, value in inputs.items()}

        output_ids = self.generator.generate(
            **inputs,
            max_new_tokens=200,
            do_sample=False,
        )

        return self.tokenizer.decode(output_ids[0], skip_special_tokens=True)


# A global engine makes it easy for a Streamlit app to import and use this file.
rag_engine = RAGEngine()


def build_index(pdf_files):
    """Helper function to build the study index from PDF file paths."""
    pdf_paths = [Path(pdf_file) for pdf_file in pdf_files]
    rag_engine.build_index(pdf_paths)


def ask_question(question):
    """Helper function used by the app to ask questions."""
    return rag_engine.ask_question(question)
