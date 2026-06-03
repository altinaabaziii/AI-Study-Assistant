import json
import os
import urllib.error
import urllib.request


DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llama3.2:3b"


def local_llm_enabled():
    return os.getenv("DISABLE_LOCAL_LLM", "").lower() not in {"1", "true", "yes"}


def ollama_model_name():
    return os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)


def llm_status_label(used_llm):
    return f"Ollama ({ollama_model_name()})" if used_llm else "Fallback lokal"


def ollama_base_url():
    return os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL).rstrip("/")


def build_study_prompt(question, sources, language):
    language_instruction = (
        "Pergjigju ne shqip te qarte dhe te shkurter."
        if language == "sq"
        else "Answer in clear, concise English."
    )
    context_blocks = []

    for index, source in enumerate(sources, start=1):
        text = " ".join(str(source.get("text", "")).split())
        if not text:
            continue
        context_blocks.append(
            f"Source {index}: {source.get('source', 'study material')}\n{text[:700]}"
        )

    context = "\n\n".join(context_blocks)
    if not context:
        context = "No specific study-material excerpt was retrieved for this question."

    return (
        "You are a helpful GenAI study assistant.\n"
        "Answer the user's question directly, like a normal Ollama chat response.\n"
        "Use your general Generative AI knowledge. Use the provided study material only as helpful background.\n"
        "For detailed questions, start with a short introduction and then use clear numbered points.\n"
        "Do not refuse or say the material is insufficient when the topic is standard Generative AI.\n"
        f"{language_instruction}\n\n"
        f"Question:\n{question}\n\n"
        f"Optional background material:\n{context}\n\n"
        "Answer:"
    )


def build_study_messages(question, sources, language):
    language_instruction = (
        "Përgjigju vetëm në shqip të qartë. Mos e përsërit këtë instruksion në përgjigje."
        if language == "sq"
        else "Answer only in clear English. Do not repeat this instruction in the answer."
    )
    context_blocks = []

    for index, source in enumerate(sources, start=1):
        text = " ".join(str(source.get("text", "")).split())
        if not text:
            continue
        context_blocks.append(
            f"Source {index}: {source.get('source', 'study material')}\n{text[:700]}"
        )

    context = "\n\n".join(context_blocks) or "No specific study-material excerpt was retrieved."
    system_message = (
        "You are a helpful GenAI study assistant. "
        "Answer the user's question directly, like a normal Ollama chat response. "
        "Use your general Generative AI knowledge. Use provided study material only as helpful background. "
        "For detailed questions, start with a short introduction and then use clear numbered points. "
        "Finish the answer with a complete final sentence. "
        "Do not say the material is insufficient when the topic is standard Generative AI. "
        f"{language_instruction}"
    )
    user_message = (
        f"Question:\n{question}\n\n"
        f"Optional background material:\n{context}"
    )
    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]


def clean_model_output(answer):
    answer = str(answer).strip()
    leaked_prefixes = (
        "Pergjigju ne shqip te qarte dhe te shkurter!",
        "Përgjigju në shqip të qartë dhe të shkurtër!",
        "Përgjigju vetëm në shqip të qartë.",
        "Answer only in clear English.",
    )
    for prefix in leaked_prefixes:
        if answer.startswith(prefix):
            answer = answer[len(prefix):].strip()
    return answer


def generate_study_answer(question, sources, language, timeout=180):
    if not local_llm_enabled():
        return None

    payload = {
        "model": ollama_model_name(),
        "messages": build_study_messages(question, sources, language),
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 700,
        },
    }
    request = urllib.request.Request(
        f"{ollama_base_url()}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        return None

    answer = data.get("message", {}).get("content", "")
    answer = clean_model_output(answer)
    return answer or None


def stream_study_answer(question, sources, language, timeout=180):
    if not local_llm_enabled():
        return

    payload = {
        "model": ollama_model_name(),
        "messages": build_study_messages(question, sources, language),
        "stream": True,
        "options": {
            "temperature": 0.2,
            "num_predict": 700,
        },
    }
    request = urllib.request.Request(
        f"{ollama_base_url()}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            for raw_line in response:
                if not raw_line:
                    continue
                try:
                    data = json.loads(raw_line.decode("utf-8"))
                except json.JSONDecodeError:
                    continue
                token = data.get("message", {}).get("content", "")
                if token:
                    yield token
                if data.get("done"):
                    break
    except (OSError, urllib.error.URLError):
        return
