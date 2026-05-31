import re


OUT_OF_SCOPE_MESSAGE = "This assistant is designed only for Generative AI topics."
OUT_OF_SCOPE_MESSAGE_SQ = "Ky asistent eshte krijuar vetem per temat e Generative AI."
NOT_FOUND_MESSAGE = "I could not find enough information in the study materials."
NOT_FOUND_MESSAGE_SQ = "Nuk gjeta informacion te mjaftueshem ne materialet e studimit."

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

    for line in text.splitlines():
        clean_line = " ".join(line.split())
        if not clean_line:
            continue
        line_sentences = re.split(r"(?<=[.!?])\s+", clean_line)
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
        "english summary",
        "shembull pyetje",
    ]

    if any(phrase in sentence_lower for phrase in noise_phrases):
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
        return 6
    if word_count < 600:
        return 12
    if word_count < 1200:
        return 12
    if word_count < 2500:
        return 14
    return 15


def summarize_text(text):
    language = detect_language(text)

    if not text or not text.strip():
        return message(NOT_FOUND_MESSAGE, NOT_FOUND_MESSAGE_SQ, language)

    if not is_genai_material(text):
        return message(OUT_OF_SCOPE_MESSAGE, OUT_OF_SCOPE_MESSAGE_SQ, language)

    concepts = extract_key_concepts(text)
    best_sentences = get_best_sentences(text, limit=6)

    if language == "sq":
        concept_line = "Konceptet kryesore: " + ", ".join(concepts or ["nuk u identifikuan qarte"])
        summary_title = "Permbledhje:"
    else:
        concept_line = "Key concepts: " + ", ".join(concepts or ["not clearly identified"])
        summary_title = "Summary:"

    bullet_lines = [f"- {sentence}" for sentence in best_sentences]
    return "\n".join([concept_line, "", summary_title, *bullet_lines])


def clean_answer(text):
    return text.strip().rstrip(".") + "."


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
            return (f"Cfare roli ka {concept} sipas materialit?", clean_answer(sentence))
        return ("Cfare ideje kryesore shpjegon materiali?", clean_answer(sentence))

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
        return (f"What role does {concept} have according to the material?", clean_answer(sentence))
    return ("What main idea does the material explain?", clean_answer(sentence))


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
            items.append(("Cilat jane disa perdorime te LLM sipas materialit?", clean_answer(sentence)))
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
            items.append(("Cfare eshte StudyMateAI sipas materialit?", clean_answer(sentence)))
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
            items.append(("What is StudyMateAI according to the material?", clean_answer(sentence)))
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
    language = detect_language(text)

    if not text or not text.strip():
        return message(NOT_FOUND_MESSAGE, NOT_FOUND_MESSAGE_SQ, language)

    if not is_genai_material(text):
        return message(OUT_OF_SCOPE_MESSAGE, OUT_OF_SCOPE_MESSAGE_SQ, language)

    concepts = extract_key_concepts(text)
    count = quiz_question_count(text)
    candidate_sentences = split_sentences(text)

    quiz_items = []
    used_answers = set()
    used_questions = set()

    for sentence in candidate_sentences:
        normalized_answer = sentence.lower()

        matched_concept = ""
        sentence_lower = sentence.lower()
        for concept, aliases in GENAI_CONCEPTS.items():
            if concept in concepts and any(alias in sentence_lower for alias in aliases):
                matched_concept = concept
                break

        for question, answer in build_specific_quiz_items(sentence, matched_concept, language):
            if not is_valid_quiz_answer(answer):
                continue

            normalized_question = question.lower()
            normalized_specific_answer = answer.lower()
            if normalized_question in used_questions or normalized_specific_answer in used_answers:
                continue

            used_questions.add(normalized_question)
            used_answers.add(normalized_specific_answer)
            used_answers.add(normalized_answer)

            label_question = "Pyetje" if language == "sq" else "Question"
            label_answer = "Pergjigje" if language == "sq" else "Answer"
            quiz_items.append(
                f"{len(quiz_items) + 1}. {label_question}: {question}\n"
                f"   {label_answer}: {answer}"
            )

            if len(quiz_items) >= count:
                break

        if len(quiz_items) >= count:
            break

    if not quiz_items:
        return message(NOT_FOUND_MESSAGE, NOT_FOUND_MESSAGE_SQ, language)

    return "\n".join(quiz_items)


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
