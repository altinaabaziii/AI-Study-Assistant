from pathlib import Path
from collections import Counter
import math
import re

KNOWLEDGE_BASE_DIR = Path("data/genai_knowledge_base")

OUT_OF_SCOPE_MESSAGE = "This assistant is designed only for Generative AI topics."
NOT_FOUND_MESSAGE = "I could not find enough information in the study materials."
OUT_OF_SCOPE_MESSAGE_SQ = "Ky asistent eshte krijuar vetem per temat e Generative AI."
NOT_FOUND_MESSAGE_SQ = "Nuk gjeta informacion te mjaftueshem ne materialet e studimit."

GENAI_TOPICS = [
    "generative ai",
    "genai",
    "large language model",
    "llm",
    "prompt engineering",
    "context engineering",
    "embedding",
    "vector search",
    "rag",
    "retrieval augmented generation",
    "agent",
    "multi-agent",
    "mlflow",
    "unity catalog",
    "governance",
    "evaluation",
    "security",
    "agent bricks",
    "enterprise ai",
    "inteligjence artificiale gjenerative",
    "gjenerative ai",
    "modele te medha gjuhesore",
    "modele gjuhesore",
    "inxhinieri e promptit",
    "inxhinieri e kontekstit",
    "embedime",
    "kerkimi vektorial",
    "agjente",
    "sisteme multi-agjente",
    "qeverisje",
    "vleresim",
    "siguri",
]

ALBANIAN_WORDS = {
    "cfare",
    "cfa",
    "cka",
    "qka",
    "eshte",
    "jane",
    "si",
    "pse",
    "kur",
    "ku",
    "me",
    "ne",
    "per",
    "nga",
    "dhe",
    "apo",
    "shpjego",
    "trego",
    "thjeshte",
    "shqip",
}

DEFINITION_WORDS = {
    "what",
    "define",
    "explain",
    "cfare",
    "cfa",
    "cka",
    "qka",
    "shpjego",
}

CONCEPT_DEFINITIONS = {
    "genai": {
        "en": (
            "GenAI, or Generative AI, is artificial intelligence "
            "that creates new content such as text, code, summaries, explanations, "
            "images, or answers from a prompt or task."
        ),
        "sq": (
            "GenAI, ose Generative AI, eshte lloj i "
            "inteligjences artificiale qe krijon permbajtje te re, si tekst, "
            "kod, permbledhje, shpjegime, imazhe ose pergjigje nga nje prompt "
            "ose detyre."
        ),
    },
    "llm": {
        "en": (
            "An LLM is a large language model trained to understand "
            "and generate text. It is often used in chat assistants, summaries, "
            "coding tools, and question-answering systems."
        ),
        "sq": (
            "LLM eshte model i madh gjuhesor qe trajnohet "
            "te kuptoje dhe te gjeneroje tekst. Perdoret shpesh ne asistente "
            "chat, permbledhje, mjete kodimi dhe sisteme pyetje-pergjigje."
        ),
    },
    "rag": {
        "en": (
            "RAG means Retrieval-Augmented Generation. It retrieves "
            "relevant material first, then uses that material as context to answer."
        ),
        "sq": (
            "RAG do te thote Retrieval-Augmented Generation. "
            "Fillimisht gjen materialin relevant, pastaj e perdor si kontekst per "
            "te kthyer pergjigje."
        ),
    },
    "embedding": {
        "en": (
            "An embedding is a numeric representation of text. It "
            "helps the system compare meaning and find similar or relevant text."
        ),
        "sq": (
            "Embedding eshte perfaqesim numerik i tekstit. "
            "E ndihmon sistemin te krahasoje kuptimin dhe te gjeje tekst te "
            "ngjashem ose relevant."
        ),
    },
    "prompt_engineering": {
        "en": (
            "Prompt engineering means writing clear instructions "
            "for an AI model. A good prompt explains the task, audience, format, "
            "and limits so the model gives a better answer."
        ),
        "sq": (
            "Prompt engineering do te thote te shkruash "
            "udhezime te qarta per modelin AI. Prompti i mire tregon detyren, "
            "audiencen, formatin dhe kufizimet."
        ),
    },
    "context_engineering": {
        "en": (
            "Context engineering means choosing the right "
            "information to give the model, such as documents, examples, tool "
            "results, conversation history, and system rules."
        ),
        "sq": (
            "Context engineering do te thote te zgjedhesh "
            "informaten e duhur qe i jepet modelit, si dokumente, shembuj, "
            "rezultate nga tools, histori bisede dhe rregulla sistemi."
        ),
    },
    "vector_search": {
        "en": (
            "Vector search finds text with similar meaning by "
            "comparing embeddings. In RAG, it helps retrieve the most relevant "
            "chunks before the model answers."
        ),
        "sq": (
            "Vector search gjen tekst me kuptim te "
            "ngjashem duke krahasuar embeddings. Ne RAG ndihmon te gjenden "
            "chunk-et me relevante para pergjigjes."
        ),
    },
    "agents": {
        "en": (
            "An AI agent is a GenAI system that can reason about a "
            "task, choose steps, and use tools or data to complete work."
        ),
        "sq": (
            "AI agent eshte sistem GenAI qe mund te "
            "arsyetoje per nje detyre, te zgjedhe hapa dhe te perdore tools ose "
            "te dhena per ta kryer punen."
        ),
    },
    "multi_agent": {
        "en": (
            "A multi-agent system uses more than one AI agent. "
            "Agents can have different roles, such as planner, researcher, "
            "executor, and evaluator."
        ),
        "sq": (
            "Sistem multi-agent perdor me shume se nje AI "
            "agent. Agjentet mund te kene role te ndryshme si planifikues, "
            "hulumtues, ekzekutues dhe vleresues."
        ),
    },
    "mlflow": {
        "en": (
            "MLflow tracks experiments, parameters, metrics, "
            "models, prompts, and evaluation results so teams can compare and "
            "manage AI work."
        ),
        "sq": (
            "MLflow ruan eksperimente, parametra, metrika, "
            "modele, prompts dhe rezultate vleresimi, qe ekipi t'i krahasoje "
            "dhe menaxhoje punet AI."
        ),
    },
    "unity_catalog": {
        "en": (
            "Unity Catalog is used for governance. It helps manage "
            "permissions, discovery, and access control for data and AI assets."
        ),
        "sq": (
            "Unity Catalog perdoret per governance. Ndihmon "
            "ne menaxhimin e lejeve, zbulimin e aseteve dhe kontrollin e aksesit "
            "per te dhena dhe asete AI."
        ),
    },
    "governance": {
        "en": (
            "Governance means controlling how data, models, prompts, "
            "tools, and outputs are used. It protects quality, privacy, access, "
            "and accountability."
        ),
        "sq": (
            "Governance do te thote kontroll mbi menyren si "
            "perdoren te dhenat, modelet, prompts, tools dhe output-et. Mbron "
            "cilesine, privatesine, aksesin dhe pergjegjesine."
        ),
    },
    "evaluation": {
        "en": (
            "Evaluation checks if a GenAI system is correct, useful, "
            "safe, grounded in sources, and fast enough for users."
        ),
        "sq": (
            "Evaluation kontrollon nese sistemi GenAI eshte "
            "i sakte, i dobishem, i sigurt, i bazuar ne burime dhe mjaft i shpejte."
        ),
    },
    "security": {
        "en": (
            "GenAI security protects data, prompts, tools, and users. "
            "It includes access control, safe logging, prompt-injection defense, "
            "and limits on tool use."
        ),
        "sq": (
            "Siguria ne GenAI mbron te dhenat, prompts, "
            "tools dhe perdoruesit. Perfshin kontroll aksesi, logging te sigurt, "
            "mbrojtje nga prompt injection dhe kufizim te tools."
        ),
    },
    "agent_bricks": {
        "en": (
            "Agent Bricks is a Databricks approach for building and "
            "optimizing domain-specific AI agents that use enterprise data, tools, "
            "governance, and evaluation."
        ),
        "sq": (
            "Agent Bricks eshte qasje e Databricks per te "
            "ndertuar dhe optimizuar AI agents specifike per domen, me te dhena, "
            "tools, governance dhe evaluation te enterprise-it."
        ),
    },
    "enterprise_ai": {
        "en": (
            "Enterprise AI means AI built for an organization with "
            "security, governance, monitoring, evaluation, access control, and "
            "clear ownership."
        ),
        "sq": (
            "Enterprise AI do te thote AI e ndertuar per "
            "organizate, me siguri, governance, monitorim, evaluation, kontroll "
            "aksesi dhe pronesi te qarte."
        ),
    },
    "hallucination": {
        "en": (
            "A hallucination is when a model gives an answer that "
            "sounds confident but is not supported by the study material or facts."
        ),
        "sq": (
            "Hallucination ndodh kur modeli jep pergjigje "
            "qe tingellon e sigurt, por nuk mbeshtetet ne material ose fakte."
        ),
    },
    "tokens": {
        "en": (
            "Tokens are small pieces of text that a language model "
            "reads and generates. Context length and cost are usually measured in "
            "tokens."
        ),
        "sq": (
            "Tokens jane pjese te vogla teksti qe modeli "
            "gjuhesor i lexon dhe gjeneron. Gjatesia e kontekstit dhe kostoja "
            "zakonisht maten me tokens."
        ),
    },
}

CONCEPT_ALIASES = {
    "genai": ["genai", "generative ai", "gjenerative ai", "ai gjenerative"],
    "llm": ["llm", "large language model", "modele gjuhesore", "model gjuhesor"],
    "rag": ["rag", "retrieval augmented generation"],
    "embedding": ["embedding", "embeddings", "embedim", "embedime"],
    "prompt_engineering": ["prompt engineering", "prompt", "prompti", "promptit"],
    "context_engineering": ["context engineering", "context", "kontekst", "kontekstit"],
    "vector_search": ["vector search", "vector", "vektor", "faiss", "kerkimi vektorial"],
    "agents": ["ai agent", "agent", "agjent", "agjente"],
    "multi_agent": ["multi-agent", "multi agent", "multi-agjent"],
    "mlflow": ["mlflow"],
    "unity_catalog": ["unity catalog"],
    "governance": ["governance", "qeverisje"],
    "evaluation": ["evaluation", "evaluate", "vleresim", "vleresimi"],
    "security": ["security", "siguri", "prompt injection"],
    "agent_bricks": ["agent bricks"],
    "enterprise_ai": ["enterprise ai"],
    "hallucination": ["hallucination", "hallucinations", "halucinim", "halucinacione"],
    "tokens": ["token", "tokens", "tokena"],
}

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "about",
    "for",
    "how",
    "is",
    "it",
    "like",
    "me",
    "of",
    "the",
    "to",
    "what",
    "why",
    "cfare",
    "cfa",
    "cka",
    "qka",
    "thote",
    "tregon",
    "sipas",
    "pdf",
    "material",
    "materiali",
    "cilin",
    "cila",
    "cili",
    "ben",
    "bene",
    "perdor",
    "perdoret",
    "përdor",
    "përdoret",
    "uses",
    "used",
    "with",
    "nje",
    "një",
    "dhe",
    "eshte",
    "është",
    "jane",
    "janë",
    "per",
    "për",
    "si",
    "nga",
    "ne",
    "në",
    "me",
}


class GenAIStudyRAG:
    """Small RAG engine for a domain-specific GenAI study assistant."""

    def __init__(self):
        self.chunks = []
        self.sources = []
        self.source_kinds = []
        self.uploaded_source_names = set()
        self.index = None
        self.idf = {}
        self.chunk_vectors = []
        self.chunk_norms = []

    def read_pdf(self, pdf_path):
        from pypdf import PdfReader

        reader = PdfReader(str(pdf_path))
        pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()
            if page_text:
                pages.append(
                    {
                        "text": page_text,
                        "source": f"{Path(pdf_path).name}, page {page_number}",
                        "kind": "uploaded",
                    }
                )

        return pages

    def read_text_file(self, text_path):
        text = Path(text_path).read_text(encoding="utf-8")
        return [{"text": text, "source": Path(text_path).name, "kind": "knowledge_base"}]

    def read_knowledge_base(self, kb_dir=KNOWLEDGE_BASE_DIR):
        kb_path = Path(kb_dir)
        documents = []

        if not kb_path.exists():
            return documents

        for text_file in sorted(kb_path.glob("*.txt")):
            documents.extend(self.read_text_file(text_file))

        return documents

    def split_text(self, text, source, chunk_size=140, overlap=30):
        sentences = self.split_sentences(text)
        chunks = []
        current_sentences = []
        current_size = 0

        for sentence in sentences:
            sentence_size = len(sentence.split())
            if current_sentences and current_size + sentence_size > chunk_size:
                chunks.append({"text": " ".join(current_sentences), "source": source})
                current_sentences = current_sentences[-2:] if overlap else []
                current_size = sum(len(item.split()) for item in current_sentences)

            current_sentences.append(sentence)
            current_size += sentence_size

        if current_sentences:
            chunks.append({"text": " ".join(current_sentences), "source": source})

        return chunks

    def build_index(self, pdf_files=None):
        pdf_files = [Path(pdf_file) for pdf_file in pdf_files or []]
        self.uploaded_source_names = {pdf_file.name for pdf_file in pdf_files}
        documents = self.read_knowledge_base()

        for pdf_file in pdf_files:
            documents.extend(self.read_pdf(pdf_file))

        self.chunks = []
        self.sources = []
        self.source_kinds = []

        for document in documents:
            split_chunks = self.split_text(document["text"], document["source"])
            for chunk in split_chunks:
                self.chunks.append(chunk["text"])
                self.sources.append(chunk["source"])
                self.source_kinds.append(document.get("kind", "knowledge_base"))

        if not self.chunks:
            raise ValueError("No text was found in uploaded files or the GenAI knowledge base.")

        self.build_keyword_index()
        self.index = True

    def normalize_text(self, text):
        replacements = {
            "ë": "e",
            "Ë": "e",
            "ç": "c",
            "Ç": "c",
            "Ã«": "e",
            "Ã‹": "e",
            "Ã§": "c",
            "Ã‡": "c",
        }
        normalized = text.lower()
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        return normalized

    def tokenize(self, text):
        normalized = self.normalize_text(text)
        terms = re.findall(r"[a-z0-9][a-z0-9_-]+", normalized)
        return [term for term in terms if term not in STOP_WORDS and len(term) > 2]

    def build_keyword_index(self):
        tokenized_chunks = [self.tokenize(chunk) for chunk in self.chunks]
        document_frequency = Counter()

        for terms in tokenized_chunks:
            document_frequency.update(set(terms))

        total_chunks = max(len(tokenized_chunks), 1)
        self.idf = {
            term: math.log((1 + total_chunks) / (1 + frequency)) + 1
            for term, frequency in document_frequency.items()
        }

        self.chunk_vectors = []
        self.chunk_norms = []

        for terms in tokenized_chunks:
            counts = Counter(terms)
            vector = {
                term: count * self.idf.get(term, 1.0)
                for term, count in counts.items()
            }
            norm = math.sqrt(sum(weight * weight for weight in vector.values())) or 1.0
            self.chunk_vectors.append(vector)
            self.chunk_norms.append(norm)

    def is_genai_question(self, question):
        question_lower = question.lower()
        return any(topic in question_lower for topic in GENAI_TOPICS) or bool(
            self.find_concepts(question)
        )

    def detect_language(self, text):
        text_lower = text.lower()
        words = set(re.findall(r"[a-zA-ZçÇëË]+", text_lower))
        has_albanian_letters = any(letter in text_lower for letter in ("ç", "ë"))
        has_albanian_words = bool(words & ALBANIAN_WORDS)
        return "sq" if has_albanian_letters or has_albanian_words else "en"

    def message(self, english, albanian, language):
        return albanian if language == "sq" else english

    def question_terms(self, question):
        return self.tokenize(question)

    def contains_alias(self, question_lower, alias):
        if " " in alias or "-" in alias:
            return alias in question_lower
        return re.search(rf"\b{re.escape(alias)}\b", question_lower) is not None

    def find_concepts(self, question):
        question_lower = question.lower()
        matches = []

        for concept, aliases in CONCEPT_ALIASES.items():
            if any(self.contains_alias(question_lower, alias) for alias in aliases):
                matches.append(concept)

        if "multi_agent" in matches and "agents" in matches:
            matches.remove("agents")
        if "agent_bricks" in matches and "agents" in matches:
            matches.remove("agents")
        if "unity_catalog" in matches and "governance" in matches:
            matches.remove("governance")
        if "genai" in matches and len(matches) > 1:
            matches.remove("genai")

        return matches[:3]

    def direct_concept_answer(self, question, language):
        question_lower = question.lower()
        words = set(re.findall(r"[a-zA-ZçÇëË]+", question_lower))
        is_definition_question = bool(words & DEFINITION_WORDS) or "what is" in question_lower
        concepts = self.find_concepts(question)

        if not concepts:
            return None

        if is_definition_question or len(concepts) <= 3:
            answers = [CONCEPT_DEFINITIONS[concept][language] for concept in concepts]
            if len(answers) == 1:
                return answers[0]
            return "\n\n".join(answers)

        return None

    def split_sentences(self, text):
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return [sentence.strip() for sentence in sentences if sentence.strip()]

    def is_answer_sentence(self, sentence):
        sentence_lower = sentence.lower().strip()
        if not sentence_lower:
            return False
        if sentence_lower.endswith("?"):
            return False
        if any(
            phrase in sentence_lower
            for phrase in ("shembull pyetje", "english summary", "material testues")
        ):
            return False
        return True

    def sentence_score(self, sentence, terms):
        sentence_lower = sentence.lower()
        score = sum(1 for term in terms if term in sentence_lower)
        if "generative ai, also called genai" in sentence_lower:
            score += 4
        if "create new content" in sentence_lower:
            score += 3
        if "answer by themselves" in sentence_lower:
            score += 2
        if "numeric representation" in sentence_lower:
            score += 2
        if "similar meanings" in sentence_lower:
            score += 1
        return score

    def translate_sentence_to_albanian(self, sentence):
        translations = {
            "An embedding is a numeric representation of text.": (
                "Embedding eshte perfaqesim numerik i tekstit."
            ),
            "Similar meanings should have similar vectors.": (
                "Tekste me kuptim te ngjashem duhet te kene vektore te ngjashem."
            ),
            "Sentence Transformers are commonly used to create embeddings.": (
                "Sentence Transformers perdoren shpesh per te krijuar embedding-e."
            ),
            "Embeddings are not answers by themselves.": (
                "Embedding-et nuk jane pergjigje vetvetiu."
            ),
            "They help a system search for relevant text.": (
                "Ato e ndihmojne sistemin te kerkoje tekst relevant."
            ),
            "After relevant chunks are found, a language model can use those chunks as context to answer a question.": (
                "Pasi gjenden pjeset relevante, modeli gjuhesor i perdor si kontekst per t'iu pergjigjur pyetjes."
            ),
        }
        return translations.get(sentence, sentence)

    def build_fast_answer(self, question, retrieved, language):
        terms = self.question_terms(question)
        candidate_sentences = []

        for item in retrieved:
            for sentence in self.split_sentences(item["text"]):
                if not self.is_answer_sentence(sentence):
                    continue
                score = self.sentence_score(sentence, terms)
                if score > 0:
                    candidate_sentences.append((score, sentence))

        if not candidate_sentences:
            return self.message(NOT_FOUND_MESSAGE, NOT_FOUND_MESSAGE_SQ, language)

        candidate_sentences.sort(key=lambda item: item[0], reverse=True)
        selected = []
        seen = set()

        for _, sentence in candidate_sentences:
            normalized = sentence.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            selected.append(sentence)
            if len(selected) == 3:
                break

        if language == "sq":
            selected = [self.translate_sentence_to_albanian(sentence) for sentence in selected]

        return " ".join(selected)

    def retrieve_chunks(self, question, top_k=4):
        if self.index is None:
            self.build_index()

        question_counts = Counter(self.tokenize(question))
        question_vector = {
            term: count * self.idf.get(term, 1.0)
            for term, count in question_counts.items()
        }
        question_norm = math.sqrt(
            sum(weight * weight for weight in question_vector.values())
        ) or 1.0

        scored_chunks = []
        for index_id, vector in enumerate(self.chunk_vectors):
            shared_terms = question_vector.keys() & vector.keys()
            score = sum(question_vector[term] * vector[term] for term in shared_terms)
            score = score / (question_norm * self.chunk_norms[index_id])
            matched_score = score

            chunk_lower = self.normalize_text(self.chunks[index_id])
            for concept in self.find_concepts(question):
                aliases = CONCEPT_ALIASES.get(concept, [])
                if any(self.normalize_text(alias) in chunk_lower for alias in aliases):
                    score += 0.05
                    matched_score += 0.05

            if matched_score > 0 and self.source_kinds[index_id] == "uploaded":
                score += 0.35

            scored_chunks.append((score, index_id))

        scored_chunks.sort(key=lambda item: item[0], reverse=True)
        retrieved = []

        for score, index_id in scored_chunks[:top_k]:
            if score <= 0:
                continue
            retrieved.append(
                {
                    "text": self.chunks[index_id],
                    "source": self.sources[index_id],
                    "kind": self.source_kinds[index_id],
                    "distance": round(1 - score, 4),
                }
            )

        return retrieved

    def has_uploaded_material(self):
        return bool(self.uploaded_source_names)

    def has_uploaded_sources(self, sources):
        return any(source.get("kind") == "uploaded" for source in sources)

    def answer_question(self, question):
        language = self.detect_language(question)
        retrieved = []

        if not self.is_genai_question(question):
            retrieved = self.retrieve_chunks(question, top_k=2)
            if not retrieved:
                answer = self.message(OUT_OF_SCOPE_MESSAGE, OUT_OF_SCOPE_MESSAGE_SQ, language)
                return {"answer": answer, "sources": []}

        if self.has_uploaded_material():
            retrieved = self.retrieve_chunks(question)
            uploaded_retrieved = [
                source for source in retrieved if source.get("kind") == "uploaded"
            ]
            if uploaded_retrieved:
                answer = self.build_fast_answer(question, uploaded_retrieved, language)
                return {"answer": answer, "sources": uploaded_retrieved}

        direct_answer = self.direct_concept_answer(question, language)
        if direct_answer:
            sources = self.retrieve_chunks(question, top_k=2)
            return {"answer": direct_answer, "sources": sources}

        if not retrieved:
            retrieved = self.retrieve_chunks(question)
        if not retrieved:
            answer = self.message(NOT_FOUND_MESSAGE, NOT_FOUND_MESSAGE_SQ, language)
            return {"answer": answer, "sources": []}

        answer = self.build_fast_answer(question, retrieved, language)
        return {"answer": answer, "sources": retrieved}


rag_engine = GenAIStudyRAG()


def build_index(pdf_files=None):
    pdf_paths = [Path(pdf_file) for pdf_file in pdf_files or []]
    rag_engine.build_index(pdf_paths)


def ask_question(question):
    return rag_engine.answer_question(question)


def retrieve_sources(question, top_k=4):
    return rag_engine.retrieve_chunks(question, top_k=top_k)
