import hashlib
import re


OUT_OF_SCOPE_MESSAGE = "This assistant is designed only for Generative AI topics."
OUT_OF_SCOPE_MESSAGE_SQ = "Ky asistent eshte krijuar vetem per temat e Generative AI."
NOT_FOUND_MESSAGE = "I could not find enough information in the study materials."
NOT_FOUND_MESSAGE_SQ = "Nuk gjeta informacion te mjaftueshem ne materialet e studimit."
SUMMARY_SENTENCE_LIMIT = 10

GENAI_CONCEPTS = {
    "Generative AI": ["generative ai", "genai", "gjenerative ai"],
    "LLMs": ["llm", "large language model", "model gjuhesor", "modele gjuhesore"],
    "Prompt Engineering": ["prompt engineering", "prompt", "prompti"],
    "Context Engineering": ["context engineering", "context", "kontekst"],
    "Embeddings": ["embedding", "embeddings", "embedim", "embedime"],
    "Vector Search": ["vector search", "vector", "faiss", "kerkimi vektorial"],
    "RAG": ["rag", "retrieval-augmented generation", "retrieval augmented generation"],
    "AI Agents": ["ai agent", "agent", "agjent"],
    "Multi-Agent Systems": ["multi-agent", "multi agent"],
    "MLflow": ["mlflow"],
    "Unity Catalog": ["unity catalog"],
    "Governance": ["governance", "qeverisje"],
    "Evaluation": ["evaluation", "evaluate", "vleresim"],
    "Security": ["security", "siguri", "prompt injection"],
    "Agent Bricks": ["agent bricks"],
    "Enterprise AI": ["enterprise ai"],
}

TRICKY_DISTRACTORS_EN = {
    "Generative AI": [
        "It only classifies existing data and cannot generate new content.",
        "It is a database search method with no language generation.",
        "It is used only to compress files and reduce storage cost.",
    ],
    "LLMs": [
        "It is a small rule-based script that follows fixed if-else commands.",
        "It stores documents in tables but does not understand or generate text.",
        "It is a vector index used only for nearest-neighbor search.",
    ],
    "Prompt Engineering": [
        "It means training the model weights from scratch for every question.",
        "It is the process of storing embeddings in a vector database.",
        "It removes the need to give the model task instructions.",
    ],
    "Context Engineering": [
        "It means ignoring retrieved documents and using only the model memory.",
        "It is the same as writing a short prompt without examples or data.",
        "It trains a new model instead of selecting useful information.",
    ],
    "Embeddings": [
        "They are final answers written directly for the user.",
        "They are passwords used to secure a model endpoint.",
        "They are manually written summaries of every document.",
    ],
    "Vector Search": [
        "It searches only exact keyword matches and ignores meaning.",
        "It generates the final answer without retrieving any context.",
        "It is used only to format text after the answer is produced.",
    ],
    "RAG": [
        "It answers without retrieving source material first.",
        "It replaces search with a fixed list of memorized responses.",
        "It is only a UI pattern for arranging chat messages.",
    ],
    "AI Agents": [
        "It is a static document with no ability to choose steps or use tools.",
        "It only stores chat history and cannot act on a task.",
        "It is a file format for saving prompts.",
    ],
    "Evaluation": [
        "It is the process of deleting all outputs after generation.",
        "It measures only the visual style of the interface.",
        "It prevents the system from checking correctness or grounding.",
    ],
    "Security": [
        "It means sharing prompts and data without access control.",
        "It removes limits from tools so every action is allowed.",
        "It is only about changing the color of warning messages.",
    ],
}

TRICKY_DISTRACTORS_SQ = {
    "Generative AI": [
        "Perdor vetem klasifikim te dhenash dhe nuk krijon permbajtje te re.",
        "Eshte metode kerkimi ne databaze pa gjenerim gjuhe.",
        "Perdoret vetem per kompresim skedaresh dhe ulje te ruajtjes.",
    ],
    "LLMs": [
        "Eshte skript i vogel me rregulla fikse if-else.",
        "Ruan dokumente ne tabela, por nuk kupton dhe nuk gjeneron tekst.",
        "Eshte indeks vektorial vetem per nearest-neighbor search.",
    ],
    "Prompt Engineering": [
        "Do te thote te trajnohen peshat e modelit nga fillimi per cdo pyetje.",
        "Eshte procesi i ruajtjes se embeddings ne databaze vektoriale.",
        "E heq nevojen per t'i dhene modelit udhezime per detyren.",
    ],
    "Context Engineering": [
        "Do te thote te injorohen dokumentet e gjetura dhe te perdoret vetem memoria e modelit.",
        "Eshte e njejte si nje prompt i shkurter pa shembuj ose te dhena.",
        "Trajnon model te ri ne vend se te zgjedhe informacionin e dobishem.",
    ],
    "Embeddings": [
        "Jane pergjigje finale te shkruara direkt per perdoruesin.",
        "Jane fjalekalime per sigurimin e nje model endpoint.",
        "Jane permbledhje manuale per cdo dokument.",
    ],
    "Vector Search": [
        "Kerkohet vetem per fjale identike dhe e injoron kuptimin.",
        "Gjeneron pergjigjen finale pa marre kontekst.",
        "Perdoret vetem per formatim teksti pas pergjigjes.",
    ],
    "RAG": [
        "Pergjigjet pa gjetur material burimor me pare.",
        "Zevendeson kerkimin me nje liste fikse pergjigjesh te memorizuara.",
        "Eshte vetem model UI per renditjen e mesazheve ne chat.",
    ],
    "AI Agents": [
        "Eshte dokument statik pa aftesi te zgjedhe hapa ose te perdore mjete.",
        "Ruan vetem historine e chat-it dhe nuk mund te veproje mbi detyren.",
        "Eshte format skedari per ruajtjen e prompts.",
    ],
    "Evaluation": [
        "Eshte procesi i fshirjes se te gjitha output-eve pas gjenerimit.",
        "Mat vetem stilin vizual te nderfaqes.",
        "E pengon sistemin te kontrolloje saktesine ose burimet.",
    ],
    "Security": [
        "Do te thote ndarje e prompts dhe te dhenave pa kontroll aksesi.",
        "Heq kufizimet nga mjetet qe cdo veprim te lejohet.",
        "Ka te beje vetem me ndryshimin e ngjyres se mesazheve paralajmeruese.",
    ],
}

ALBANIAN_WORDS = {
    "cfare",
    "cka",
    "qka",
    "eshte",
    "jane",
    "si",
    "pse",
    "per",
    "nga",
    "dhe",
    "shpjego",
}

QUESTION_STARTERS = {
    "cfare",
    "cka",
    "qka",
    "what",
    "which",
    "does",
    "can",
    "how",
    "why",
    "a",
}

SUBJECT_STOP_WORDS = {
    "ai",
    "ajo",
    "it",
    "this",
    "that",
    "ky",
    "kjo",
    "nje",
    "një",
    "the",
    "a",
    "an",
    "ai",
    "ajo",
    "it",
    "they",
    "when",
    "kur",
    "mund",
    "te",
    "të",
    "ne",
    "në",
    "per",
    "për",
}


def detect_language(text):
    text_lower = text.lower()
    words = set(re.findall(r"[a-zA-ZçÇëË]+", text_lower))
    if any(letter in text_lower for letter in ("ç", "ë")) or words & ALBANIAN_WORDS:
        return "sq"
    return "en"


def message(english, albanian, language):
    return albanian if language == "sq" else english


def split_sentences(text):
    sentences = []
    paragraphs = []
    current_lines = []
    skip_section = False

    for line in text.splitlines():
        clean_line = " ".join(line.split())
        lower_line = clean_line.lower()

        if "english summary" in lower_line or "shembull pyetje" in lower_line:
            skip_section = True
            if current_lines:
                paragraphs.append(" ".join(current_lines))
                current_lines = []
            continue

        if skip_section:
            if not clean_line:
                skip_section = False
            continue

        if clean_line:
            current_lines.append(clean_line)
        elif current_lines:
            paragraphs.append(" ".join(current_lines))
            current_lines = []

    if current_lines:
        paragraphs.append(" ".join(current_lines))

    for paragraph in paragraphs:
        paragraph = re.sub(r"\s*[•●]\s*", ". ", paragraph)
        paragraph = re.sub(r"\s+(?=\d+\s+[A-Z][A-Za-z])", ". ", paragraph)
        line_sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        sentences.extend(sentence.strip() for sentence in line_sentences)

    return [
        sentence
        for sentence in sentences
        if len(sentence.split()) >= 4 and is_learning_sentence(sentence)
    ]


def is_learning_sentence(sentence):
    sentence_lower = sentence.lower()
    noise_phrases = [
        "material testues",
        "source basis",
        "english summary",
        "shembull pyetje",
    ]

    if any(phrase in sentence_lower for phrase in noise_phrases):
        return False
    if sentence_lower.strip(" .?!").split(" ", 1)[0] in QUESTION_STARTERS:
        return False

    return True


def is_genai_material(text):
    text_lower = text.lower()
    return any(alias in text_lower for aliases in GENAI_CONCEPTS.values() for alias in aliases)


def extract_key_concepts(text):
    text_lower = text.lower()
    concepts = []

    for concept, aliases in GENAI_CONCEPTS.items():
        if any(alias in text_lower for alias in aliases):
            concepts.append(concept)

    return concepts


def sentence_score(sentence, concepts):
    sentence_lower = sentence.lower()
    score = 0

    for concept, aliases in GENAI_CONCEPTS.items():
        if concept in concepts and any(alias in sentence_lower for alias in aliases):
            score += 3

    important_words = [
        "means",
        "is",
        "are",
        "helps",
        "used",
        "creates",
        "retrieves",
        "stores",
        "generates",
        "perdor",
        "eshte",
        "krijon",
        "ndihmon",
    ]
    score += sum(1 for word in important_words if word in sentence_lower)
    return score


def get_best_sentences(text, limit):
    concepts = extract_key_concepts(text)
    sentences = split_sentences(text)
    scored = []

    for index, sentence in enumerate(sentences):
        score = sentence_score(sentence, concepts)
        if score > 0:
            scored.append((score, index, sentence))

    if not scored:
        return sentences[:limit]

    scored.sort(key=lambda item: (-item[0], item[1]))
    selected = sorted(scored[:limit], key=lambda item: item[1])
    return [sentence for _, _, sentence in selected]


def quiz_question_count(text):
    word_count = len(text.split())

    if word_count < 120:
        return 3
    if word_count < 300:
        return 5
    if word_count < 600:
        return 7
    if word_count < 1200:
        return 8
    return 8


def join_natural_sentences(sentences):
    cleaned = [" ".join(sentence.split()).strip() for sentence in sentences if sentence.strip()]
    text = " ".join(cleaned)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def summarize_text(text):
    language = detect_language(text)

    if not text or not text.strip():
        return message(NOT_FOUND_MESSAGE, NOT_FOUND_MESSAGE_SQ, language)

    concepts = extract_key_concepts(text)
    best_sentences = get_best_sentences(text, limit=SUMMARY_SENTENCE_LIMIT)
    opening_sentences = best_sentences[:5]
    point_sentences = best_sentences[5:] or best_sentences[:5]

    if language == "sq":
        concept_line = "Konceptet kryesore: " + ", ".join(concepts or ["nuk u identifikuan qarte"])
        essay_title = "Cfare permban materiali:"
        points_title = "Pikat me te rendesishme:"
        if opening_sentences:
            essay = join_natural_sentences(opening_sentences)
            essay = (
                "Ky material paraqet temat kryesore te Generative AI dhe shpjegon "
                "si lidhen ato me ndertimin e asistenteve, kerkimin ne dokumente, "
                "permbledhjen dhe gjenerimin e pergjigjeve. "
                + essay
            )
        else:
            essay = "Materiali nuk jep mjaft tekst te qarte per nje permbledhje te plote."
    else:
        concept_line = "Key concepts: " + ", ".join(concepts or ["not clearly identified"])
        essay_title = "What the material covers:"
        points_title = "Most important points:"
        if opening_sentences:
            essay = join_natural_sentences(opening_sentences)
            essay = (
                "This material presents the main Generative AI topics and explains "
                "how they connect to assistants, document retrieval, summarization, "
                "and answer generation. "
                + essay
            )
        else:
            essay = "The material does not provide enough clear text for a complete summary."

    bullet_lines = [f"- {sentence}" for sentence in point_sentences]
    return "\n".join([concept_line, "", essay_title, essay, "", points_title, *bullet_lines])


def clean_answer(text):
    return text.strip().rstrip(".") + "."


def clean_quiz_question(question, language=None):
    language = language or detect_language(question)
    question = " ".join(str(question).split())
    replacements = {
        "Cfare thote PDF-ja per": "Cfare eshte",
        "Cfare thote PDF per": "Cfare eshte",
        "Cila fjali mbeshtetet nga PDF-ja?": "Cila fjali eshte e sakte?",
        "Cila fjali mbeshtetet nga PDF?": "Cila fjali eshte e sakte?",
        "What does the PDF say about": "What is",
        "Which statement is supported by the PDF?": "Which statement is correct?",
        "Which point is mentioned in the uploaded material?": "Which point is mentioned in the material?",
    }
    for old, new in replacements.items():
        question = question.replace(old, new)
    question = question.replace("PDF-ja", "materiali")
    question = question.replace("PDF", "material")
    question = question.replace("  ", " ").strip()
    if language == "sq":
        question = question.replace("materiali-ja", "materiali")
    return question


def normalize_for_match(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def answer_similarity(left, right):
    left_terms = set(normalize_for_match(left).split())
    right_terms = set(normalize_for_match(right).split())
    if not left_terms or not right_terms:
        return 0.0
    return len(left_terms & right_terms) / max(len(left_terms | right_terms), 1)


def compact_text(text, max_words=22):
    text = " ".join(text.replace("•", " ").split())
    words = text.split()
    if len(words) <= max_words:
        return clean_answer(text)
    return clean_answer(" ".join(words[:max_words]) + "...")


def is_good_quiz_sentence(sentence):
    words = sentence.split()
    sentence_lower = sentence.lower()

    if len(words) < 5 or len(words) > 34:
        return False
    if sentence_lower.endswith("?"):
        return False
    if sentence_lower.startswith(("dr mehmet", "outline of", "recap from", "in other words")):
        return False
    if sentence_lower.startswith(("outline", "course introduction", "data management sampling")):
        return False
    if sum(1 for char in sentence if char == "•") > 1:
        return False
    if len(re.findall(r"\b\d+(?:\.\d+)?\b", sentence)) > 4:
        return False

    return True


def is_fallback_quiz_sentence(sentence):
    words = sentence.split()
    sentence_lower = sentence.lower()

    if len(words) < 7 or len(words) > 55:
        return False
    if sentence_lower.endswith("?"):
        return False
    if sentence_lower.startswith(("dr mehmet", "outline", "recap", "in other words")):
        return False

    return True


def clean_subject(subject):
    subject = re.sub(r"[^A-Za-z0-9Ã§Ã‡Ã«Ã‹çÇëË./_-]+", " ", subject)
    subject = " ".join(subject.split()).strip(" .,:;")
    words = [word for word in subject.split() if word.lower() not in SUBJECT_STOP_WORDS]
    subject = " ".join(words[:5])
    return subject.strip()


def sentence_subject(sentence, concepts):
    sentence_lower = sentence.lower()

    if "sistemi" in sentence_lower:
        return "sistemi"
    if "system" in sentence_lower:
        return "the system"

    for concept, aliases in GENAI_CONCEPTS.items():
        if concept in concepts and any(alias in sentence_lower for alias in aliases):
            return concept

    if "krijoje" in sentence_lower or "krijon" in sentence_lower:
        return "GenAI"
    if "projekt" in sentence_lower:
        return "projekti"
    if "openai api" in sentence_lower:
        return "OpenAI API"

    if "modeli" in sentence_lower:
        return "modeli"
    if "model" in sentence_lower:
        return "the model"

    patterns = [
        r"^([A-Za-z0-9Ã§Ã‡Ã«Ã‹çÇëË./_-]+(?:\s+[A-Za-z0-9Ã§Ã‡Ã«Ã‹çÇëË./_-]+){0,4})\s+(?:eshte|është|jane|janë|perdoret|përdoret|do te thote|do të thotë)\b",
        r"^([A-Za-z0-9./_-]+(?:\s+[A-Za-z0-9./_-]+){0,4})\s+(?:is|are|means|uses|creates|retrieves|stores|checks)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, sentence, re.IGNORECASE)
        if match:
            subject = clean_subject(match.group(1))
            if subject:
                return subject

    words = sentence.split()
    return clean_subject(" ".join(words[:4])) or ("materialit" if detect_language(sentence) == "sq" else "the material")


def definition_quiz_item(sentence, language):
    patterns = [
        (
            r"^(.{2,70}?)\s+(?:eshte|është|jane|janë|do te thote|do të thotë)\s+(.+)$",
            "sq",
        ),
        (r"^(.{2,70}?)\s+(?:is|are|means)\s+(.+)$", "en"),
    ]

    for pattern, pattern_language in patterns:
        match = re.search(pattern, sentence, re.IGNORECASE)
        if not match:
            continue

        subject = clean_subject(match.group(1))
        if not subject or len(subject.split()) > 6:
            continue

        if language == "sq":
            return f"Cfare eshte {subject}?", compact_text(sentence)
        return f"What is {subject}?", compact_text(sentence)

    return None


def adaptive_quiz_item(sentence, concepts, language):
    definition_item = definition_quiz_item(sentence, language)
    if definition_item:
        return definition_item

    answer = compact_text(sentence)
    subject = sentence_subject(sentence, concepts)

    if language == "sq":
        return f"Cfare duhet te dish per {subject}?", answer
    return f"What should you know about {subject}?", answer


def should_replace_template_question(question):
    question_lower = question.lower()
    repeated_patterns = [
        "cfare roli ka",
        "what role does",
        "what main idea",
        "cfare ideje kryesore",
    ]
    return any(pattern in question_lower for pattern in repeated_patterns)


def clean_model_name(model_name):
    model_name = model_name.strip().rstrip(".,;:")
    invalid_names = {"per", "te", "të", "si", "dhe", "chunks", "kontekst", "modelin"}

    if model_name.lower() in invalid_names or len(model_name) < 4:
        return ""

    return clean_answer(model_name)


def is_valid_quiz_answer(answer):
    answer_text = answer.strip().rstrip(".")
    invalid_answers = {"per", "te", "të", "si", "dhe", "nga", "ne", "në"}

    if answer_text.lower() in invalid_answers:
        return False
    if len(answer_text) < 4:
        return False

    return True


def extract_embedding_model(sentence):
    patterns = [
        r"modeli\s+([A-Za-z0-9./_-]+)\s+mund te perdoret per te krijuar embeddings",
        r"embeddings?\s+me modelin\s+([A-Za-z0-9./_-]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, sentence, re.IGNORECASE)
        if match:
            return clean_model_name(match.group(1))

    return ""


def extract_generation_model(sentence):
    patterns = [
        r"perdor modelin\s+([A-Za-z0-9./_-]+)\s+per te gjeneruar",
        r"answers questions with\s+([A-Za-z0-9./_-]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, sentence, re.IGNORECASE)
        if match:
            return clean_model_name(match.group(1))

    return ""


def build_specific_quiz_item(sentence, concept, language):
    sentence_lower = sentence.lower()

    embedding_model = extract_embedding_model(sentence)
    generation_model = extract_generation_model(sentence)

    if language == "sq":
        if embedding_model:
            return (
                "Cilin model perdor sistemi per te krijuar embeddings?",
                embedding_model,
            )
        if generation_model:
            return (
                "Cilin model perdor sistemi per te gjeneruar pergjigje?",
                generation_model,
            )
        if "lexon dokumente pdf" in sentence_lower:
            return ("Cfare lloj dokumentesh lexon sistemi?", "Sistemi lexon dokumente PDF.")
        if "ndan tekstin ne pjese" in sentence_lower:
            return (
                "Si e pergatit sistemi tekstin para kerkimit?",
                "Sistemi e ndan tekstin ne pjese te vogla.",
            )
        if "faiss" in sentence_lower and ("ruan" in sentence_lower or "stores" in sentence_lower):
            return ("Ku ruhen embeddings?", "Embeddings ruhen ne FAISS.")
        if "kur studenti ben nje pyetje" in sentence_lower or "studenti ben nje pyetje" in sentence_lower:
            return (
                "Cfare ben sistemi kur studenti ben nje pyetje?",
                clean_answer(sentence),
            )
        if "mjete falas" in sentence_lower or "open-source" in sentence_lower:
            return (
                "Cfare lloj mjetesh perdor projekti?",
                "Projekti perdor mjete falas dhe open-source.",
            )
        if "nuk perdor openai api" in sentence_lower or "does not use the openai api" in sentence_lower:
            return ("A perdor projekti OpenAI API?", "Jo, projekti nuk perdor OpenAI API.")
        if concept:
            return (f"Cfare roli ka {concept}?", clean_answer(sentence))
        return ("Cila eshte ideja kryesore?", clean_answer(sentence))

    if embedding_model:
        return (
            "Which model does the system use to create embeddings?",
            embedding_model,
        )
    if generation_model:
        return (
            "Which model does the system use to generate answers?",
            generation_model,
        )
    if "reads pdf files" in sentence_lower or "reads pdf" in sentence_lower:
        return ("What type of documents does the system read?", "The system reads PDF files.")
    if "split" in sentence_lower and "chunks" in sentence_lower:
        return (
            "How does the system prepare text before retrieval?",
            "It splits the text into smaller chunks.",
        )
    if "faiss" in sentence_lower and ("store" in sentence_lower or "stores" in sentence_lower):
        return ("Where are embeddings stored?", "Embeddings are stored in FAISS.")
    if "when" in sentence_lower and "question" in sentence_lower:
        return ("What does the system do when a student asks a question?", clean_answer(sentence))
    if "free" in sentence_lower and "open-source" in sentence_lower:
        return ("What type of tools does the project use?", "It uses free and open-source tools.")
    if "does not use the openai api" in sentence_lower or "nuk perdor openai api" in sentence_lower:
        return ("Does the project use the OpenAI API?", "No, the project does not use the OpenAI API.")
    if concept:
        return (f"What role does {concept} have?", clean_answer(sentence))
    return ("What is the main idea?", clean_answer(sentence))


def build_specific_quiz_items(sentence, concept, language):
    sentence_lower = sentence.lower()
    items = []

    embedding_model = extract_embedding_model(sentence)
    generation_model = extract_generation_model(sentence)

    if language == "sq":
        if "generative ai" in sentence_lower and "krijon permbajtje" in sentence_lower:
            items.append(("Cfare eshte GenAI?", "GenAI eshte AI qe krijon permbajtje te re."))
        if "mund te krijoje" in sentence_lower and ("tekst" in sentence_lower or "kod" in sentence_lower):
            items.append(("Cfare mund te krijoje GenAI?", clean_answer(sentence)))
        if "llm eshte large language model" in sentence_lower:
            items.append(("Cfare do te thote LLM?", "LLM do te thote Large Language Model."))
        if "llm trajnohet" in sentence_lower:
            items.append(("Per cfare perdoret LLM?", clean_answer(sentence)))
        if "shembuj te perdorimit" in sentence_lower:
            items.append(("Cilat jane disa perdorime te LLM?", clean_answer(sentence)))
        if "prompt engineering eshte" in sentence_lower:
            items.append(("Cfare eshte prompt engineering?", clean_answer(sentence)))
        if "prompt i mire" in sentence_lower:
            items.append(("Cfare duhet te tregoje nje prompt i mire?", clean_answer(sentence)))
        if "context engineering eshte" in sentence_lower:
            items.append(("Cfare eshte context engineering?", clean_answer(sentence)))
        if "konteksti mund te perfshije" in sentence_lower:
            items.append(("Cfare mund te perfshije konteksti?", clean_answer(sentence)))
        if "embeddings jane" in sentence_lower:
            items.append(("Cfare jane embeddings?", clean_answer(sentence)))
        if "kuptim te ngjashem" in sentence_lower and "embeddings" in sentence_lower:
            items.append(("Si lidhet kuptimi i tekstit me embeddings?", clean_answer(sentence)))
        if "studymateai" in sentence_lower and ("asistent" in sentence_lower or "assistant" in sentence_lower):
            items.append(("Cfare eshte StudyMateAI?", clean_answer(sentence)))
        if "lexon dokumente pdf" in sentence_lower or "reads pdf files" in sentence_lower:
            items.append(("Cfare lloj dokumentesh lexon sistemi?", "Sistemi lexon dokumente PDF."))
        if "ndan tekstin ne pjese" in sentence_lower or "split" in sentence_lower:
            items.append(("Si e pergatit sistemi tekstin para kerkimit?", "Sistemi e ndan tekstin ne pjese te vogla."))
        if embedding_model:
            items.append(("Cilin model mund ta perdorim per embeddings?", embedding_model))
        if "vector search perdoret" in sentence_lower:
            items.append(("Per cfare perdoret vector search?", clean_answer(sentence)))
        if "faiss" in sentence_lower and ("ruan" in sentence_lower or "stores" in sentence_lower):
            items.append(("Ku ruhen embeddings?", "Embeddings ruhen ne FAISS."))
        if "faiss eshte" in sentence_lower:
            items.append(("Cfare eshte FAISS?", clean_answer(sentence)))
        if "rag do te thote" in sentence_lower:
            items.append(("Cfare do te thote RAG?", clean_answer(sentence)))
        if "dokumentin ne chunks" in sentence_lower:
            items.append(("Cfare ben sistemi fillimisht ne RAG?", clean_answer(sentence)))
        if "kerkon pjeset me relevante" in sentence_lower or "retrieves relevant chunks" in sentence_lower:
            items.append(("Cfare kerkon sistemi kur studenti ben nje pyetje?", "Sistemi kerkon pjeset me relevante nga dokumenti."))
        if "modeli gjuhesor perdor chunks" in sentence_lower:
            items.append(("Si i perdor modeli gjuhesor chunks ne RAG?", clean_answer(sentence)))
        if generation_model:
            items.append(("Cilin model perdor sistemi per te gjeneruar pergjigje?", generation_model))
        if "ai agent eshte" in sentence_lower:
            items.append(("Cfare eshte AI agent?", clean_answer(sentence)))
        if "multi-agent system" in sentence_lower:
            items.append(("Cfare eshte multi-agent system?", clean_answer(sentence)))
        if "mlflow perdoret" in sentence_lower:
            items.append(("Per cfare perdoret MLflow?", clean_answer(sentence)))
        if "unity catalog perdoret" in sentence_lower:
            items.append(("Per cfare perdoret Unity Catalog?", clean_answer(sentence)))
        if "governance ndihmon" in sentence_lower:
            items.append(("Si ndihmon governance ne GenAI?", clean_answer(sentence)))
        if "evaluation kontrollon" in sentence_lower:
            items.append(("Cfare kontrollon evaluation ne GenAI?", clean_answer(sentence)))
        if "rag evaluation kontrollon" in sentence_lower:
            items.append(("Cfare kontrollon RAG evaluation?", clean_answer(sentence)))
        if "security ne genai" in sentence_lower:
            items.append(("Cfare perfshin security ne GenAI?", clean_answer(sentence)))
        if "prompt injection ndodh" in sentence_lower:
            items.append(("Cfare eshte prompt injection?", clean_answer(sentence)))
        if "agent bricks eshte" in sentence_lower:
            items.append(("Cfare eshte Agent Bricks?", clean_answer(sentence)))
        if "enterprise ai kerkon" in sentence_lower:
            items.append(("Cfare kerkon Enterprise AI?", clean_answer(sentence)))
        if "mjete falas" in sentence_lower or "free and open-source" in sentence_lower:
            items.append(("Cfare lloj mjetesh perdor projekti?", "Projekti perdor mjete falas dhe open-source."))
        if "nuk perdor openai api" in sentence_lower or "does not use the openai api" in sentence_lower:
            items.append(("A perdor projekti OpenAI API?", "Jo, projekti nuk perdor OpenAI API."))
    else:
        if "generative ai" in sentence_lower and "create" in sentence_lower:
            items.append(("What is GenAI?", clean_answer(sentence)))
        if "llm is" in sentence_lower or "llm eshte" in sentence_lower:
            items.append(("What does LLM mean?", clean_answer(sentence)))
        if "studymateai" in sentence_lower and ("assistant" in sentence_lower or "asistent" in sentence_lower):
            items.append(("What is StudyMateAI?", clean_answer(sentence)))
        if "reads pdf files" in sentence_lower or "lexon dokumente pdf" in sentence_lower:
            items.append(("What type of documents does the system read?", "The system reads PDF files."))
        if "split" in sentence_lower or "ndan tekstin ne pjese" in sentence_lower:
            items.append(("How does the system prepare text before retrieval?", "It splits the text into smaller chunks."))
        if embedding_model:
            items.append(("Which model can be used to create embeddings?", embedding_model))
        if "vector search" in sentence_lower and ("used" in sentence_lower or "perdoret" in sentence_lower):
            items.append(("What is vector search used for?", clean_answer(sentence)))
        if "faiss" in sentence_lower and ("store" in sentence_lower or "ruan" in sentence_lower):
            items.append(("Where are embeddings stored?", "Embeddings are stored in FAISS."))
        if "faiss is" in sentence_lower or "faiss eshte" in sentence_lower:
            items.append(("What is FAISS?", clean_answer(sentence)))
        if "rag" in sentence_lower and ("means" in sentence_lower or "do te thote" in sentence_lower):
            items.append(("What does RAG mean?", clean_answer(sentence)))
        if "retrieves relevant chunks" in sentence_lower or "kerkon pjeset me relevante" in sentence_lower:
            items.append(("What does the system retrieve when a student asks a question?", "It retrieves the most relevant chunks from the document."))
        if generation_model:
            items.append(("Which model does the system use to generate answers?", generation_model))
        if "mlflow" in sentence_lower and ("used" in sentence_lower or "perdoret" in sentence_lower):
            items.append(("What is MLflow used for?", clean_answer(sentence)))
        if "unity catalog" in sentence_lower:
            items.append(("What is Unity Catalog used for?", clean_answer(sentence)))
        if "evaluation" in sentence_lower and ("checks" in sentence_lower or "kontrollon" in sentence_lower):
            items.append(("What does evaluation check in GenAI?", clean_answer(sentence)))
        if "security" in sentence_lower and "genai" in sentence_lower:
            items.append(("What does GenAI security include?", clean_answer(sentence)))
        if "free and open-source" in sentence_lower or "mjete falas" in sentence_lower:
            items.append(("What type of tools does the project use?", "It uses free and open-source tools."))
        if "does not use the openai api" in sentence_lower or "nuk perdor openai api" in sentence_lower:
            items.append(("Does the project use the OpenAI API?", "No, the project does not use the OpenAI API."))

    if items:
        return items

    return [build_specific_quiz_item(sentence, concept, language)]


def generate_quiz(text):
    quiz_items = generate_quiz_items(text)

    if isinstance(quiz_items, str):
        return quiz_items

    language = detect_language(text)
    label_question = "Pyetje" if language == "sq" else "Question"
    label_answer = "Pergjigje" if language == "sq" else "Answer"
    lines = []

    for index, item in enumerate(quiz_items, start=1):
        lines.append(
            f"{index}. {label_question}: {item['question']}\n"
            f"   {label_answer}: {item['answer']}"
        )

    return "\n".join(lines)


def make_distractors(correct_answer, all_answers, language, concept="", limit=3):
    fallback_answers_sq = [
        "Ky koncept nuk lidhet me Generative AI.",
        "Kjo teme perdoret vetem per ruajtje mekanike te skedareve.",
        "Pergjigjja nuk permendet si pjese e materialit te studimit.",
    ]
    fallback_answers_en = [
        "This concept is not related to Generative AI.",
        "This topic is used only for mechanical file storage.",
        "The answer is not mentioned as part of the study material.",
    ]
    fallback_answers = fallback_answers_sq if language == "sq" else fallback_answers_en
    tricky_bank = TRICKY_DISTRACTORS_SQ if language == "sq" else TRICKY_DISTRACTORS_EN
    candidates = tricky_bank.get(concept, []) + fallback_answers
    correct_normalized = normalize_for_match(correct_answer)
    distractors = []
    seen = {correct_normalized}

    for answer in candidates:
        answer = compact_text(answer)
        normalized = normalize_for_match(answer)
        if normalized in seen:
            continue
        if normalized in correct_normalized or correct_normalized in normalized:
            continue
        if answer_similarity(answer, correct_answer) >= 0.55:
            continue
        if len(answer.split()) > 24:
            continue
        distractors.append(answer)
        seen.add(normalized)
        if len(distractors) == limit:
            break

    return distractors


def stable_option_order(question, options):
    digest = hashlib.sha256(question.encode("utf-8")).hexdigest()
    start = int(digest[:2], 16) % len(options)
    return options[start:] + options[:start]


def generate_quiz_items(text):
    language = detect_language(text)

    if not text or not text.strip():
        return message(NOT_FOUND_MESSAGE, NOT_FOUND_MESSAGE_SQ, language)

    concepts = extract_key_concepts(text)
    count = quiz_question_count(text)
    all_sentences = split_sentences(text)
    candidate_sentences = [
        sentence for sentence in all_sentences if is_good_quiz_sentence(sentence)
    ]

    if len(candidate_sentences) < 3:
        candidate_sentences = [
            sentence for sentence in all_sentences if is_fallback_quiz_sentence(sentence)
        ]

    concept_first_sentences = []
    used_sentence_indexes = set()

    for concept in concepts:
        aliases = GENAI_CONCEPTS.get(concept, [])
        for index, sentence in enumerate(candidate_sentences):
            sentence_lower = sentence.lower()
            if any(alias in sentence_lower for alias in aliases):
                concept_first_sentences.append(sentence)
                used_sentence_indexes.add(index)
                break

    ordered_sentences = concept_first_sentences + [
        sentence
        for index, sentence in enumerate(candidate_sentences)
        if index not in used_sentence_indexes
    ]

    raw_items = []
    used_answers = set()
    used_questions = set()

    for sentence in ordered_sentences:
        normalized_answer = sentence.lower()

        matched_concept = ""
        sentence_lower = sentence.lower()
        for concept, aliases in GENAI_CONCEPTS.items():
            if concept in concepts and any(alias in sentence_lower for alias in aliases):
                matched_concept = concept
                break

        sentence_items = build_specific_quiz_items(sentence, matched_concept, language)
        if not sentence_items:
            sentence_items = [adaptive_quiz_item(sentence, concepts, language)]

        for question, answer in sentence_items:
            question = clean_quiz_question(question, language)
            if not is_valid_quiz_answer(answer):
                continue

            normalized_question = question.lower()
            normalized_specific_answer = answer.lower()
            if normalized_question in used_questions or normalized_specific_answer in used_answers:
                continue

            used_questions.add(normalized_question)
            used_answers.add(normalized_specific_answer)
            used_answers.add(normalized_answer)

            raw_items.append(
                {
                    "question": question,
                    "answer": clean_answer(answer),
                    "concept": matched_concept or "Koncept kryesor",
                }
            )

            if len(raw_items) >= count:
                break

        if len(raw_items) >= count:
            break

    if not raw_items:
        return message(NOT_FOUND_MESSAGE, NOT_FOUND_MESSAGE_SQ, language)

    all_answers = [item["answer"] for item in raw_items]
    quiz_items = []

    for item in raw_items:
        distractors = make_distractors(
            item["answer"],
            all_answers,
            language,
            concept=item.get("concept", ""),
        )
        if len(distractors) < 3:
            continue
        options = stable_option_order(item["question"], [item["answer"], *distractors])
        if sum(normalize_for_match(option) == normalize_for_match(item["answer"]) for option in options) != 1:
            continue
        quiz_items.append(
            {
                "question": item["question"],
                "answer": item["answer"],
                "options": options,
                "concept": item.get("concept", ""),
            }
        )

    return quiz_items


def explain_concept(concept, context):
    language = detect_language(f"{concept}\n{context}")

    if not concept or not concept.strip():
        return message("Enter a GenAI concept to explain.", "Shkruaj nje koncept GenAI per ta shpjeguar.", language)

    combined_text = f"{concept}\n{context}"
    if not is_genai_material(combined_text):
        return message(OUT_OF_SCOPE_MESSAGE, OUT_OF_SCOPE_MESSAGE_SQ, language)

    concept_lower = concept.lower()
    relevant_sentences = [
        sentence
        for sentence in split_sentences(context)
        if any(word in sentence.lower() for word in concept_lower.split())
    ]
    if not relevant_sentences:
        relevant_sentences = get_best_sentences(context, limit=3)

    if not relevant_sentences:
        return message(NOT_FOUND_MESSAGE, NOT_FOUND_MESSAGE_SQ, language)

    return " ".join(relevant_sentences[:3])
