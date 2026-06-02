from pathlib import Path
from tempfile import NamedTemporaryFile
import html
import os
import time

import streamlit as st
from pypdf import PdfReader


APP_NAME = "AI Study Assistant"
MLFLOW_EXPERIMENT_NAME = "GenAIStudyAssistant"
MAX_PARAM_LENGTH = 250
ENABLE_MLFLOW = os.getenv("ENABLE_MLFLOW", "").lower() in {"1", "true", "yes"}
QUIZ_FORMAT_VERSION = 5


st.set_page_config(
    page_title=APP_NAME,
    page_icon=":material/school:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def apply_custom_style():
    st.markdown(
        """
        <style>
        :root {
            --bg: #000000;
            --surface: #050505;
            --surface-2: #0d0d0d;
            --border: #262626;
            --border-strong: #404040;
            --text: #f5f5f5;
            --muted: #a3a3a3;
            --success: #22c55e;
            --danger: #ef4444;
        }

        .stApp {
            background: var(--bg);
            color: var(--text);
        }

        header[data-testid="stHeader"] {
            background: rgba(0, 0, 0, 0.86);
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }

        [data-testid="stSidebar"] {
            background: #050505;
            border-right: 1px solid var(--border);
        }

        [data-testid="stSidebar"] * {
            color: var(--text);
        }

        .block-container {
            max-width: 960px;
            padding-top: 1.2rem;
            padding-bottom: 5rem;
        }

        h1, h2, h3 {
            color: var(--text) !important;
            letter-spacing: 0 !important;
        }

        h1 {
            font-size: 1.45rem !important;
            font-weight: 720 !important;
            margin: 0 !important;
        }

        p, label, span, div[data-testid="stMarkdownContainer"] {
            color: var(--muted);
        }

        div[data-testid="stChatMessage"] {
            background: transparent;
            border: 0;
        }

        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
            color: var(--text);
            line-height: 1.62;
        }

        div[data-testid="stChatInput"] {
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            background: rgba(0, 0, 0, 0.92);
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text);
        }

        div[data-testid="stFileUploader"] section {
            background: var(--surface);
            border: 1px dashed var(--border-strong);
            border-radius: 8px;
        }

        div[data-testid="stFileUploader"] button {
            background: #ffffff !important;
            color: #000000 !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
            font-weight: 650 !important;
        }

        div[data-testid="stFileUploader"] button * {
            color: #000000 !important;
        }

        div.stButton > button {
            border-radius: 8px;
            border: 1px solid var(--border);
            background: #ffffff !important;
            color: #000000 !important;
            font-weight: 650;
            min-height: 2.65rem;
        }

        div.stButton > button * {
            color: #000000 !important;
        }

        div.stButton > button:hover {
            border-color: #ffffff;
            background: #f4f4f5 !important;
            color: #000000 !important;
        }

        div.stButton > button:disabled {
            background: #ffffff !important;
            color: #000000 !important;
            border-color: var(--border) !important;
            opacity: 0.58;
        }

        div[data-testid="stAlert"],
        div[data-testid="stExpander"],
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 8px;
            border-color: var(--border);
            background: var(--surface);
        }

        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border);
            margin-bottom: 1rem;
        }

        .subtitle {
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.5;
            margin-top: 0.35rem;
        }

        .status-pill {
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: 0.32rem 0.65rem;
            color: var(--text);
            font-size: 0.78rem;
            white-space: nowrap;
            background: var(--surface-2);
        }

        .quick-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.65rem;
            margin: 0.6rem 0 1rem;
        }

        .quick-card {
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--surface);
            padding: 0.75rem;
            min-height: 5rem;
        }

        .quick-title {
            color: var(--text);
            font-weight: 700;
            font-size: 0.9rem;
            margin-bottom: 0.25rem;
        }

        .quick-copy {
            color: var(--muted);
            font-size: 0.8rem;
            line-height: 1.45;
        }

        .result-meta {
            color: var(--muted);
            font-size: 0.8rem;
            margin-top: 0.4rem;
        }

        @media (max-width: 760px) {
            .block-container {
                padding-top: 0.8rem;
            }

            .topbar,
            .quick-grid {
                grid-template-columns: 1fr;
                display: grid;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner=False)
def load_rag_functions():
    from rag_engine import ask_question, build_index, retrieve_sources

    return build_index, ask_question, retrieve_sources


@st.cache_resource(show_spinner=False)
def load_study_functions():
    from study_tools import (
        explain_concept,
        generate_quiz_items,
        is_genai_material,
        summarize_text,
    )

    return (
        summarize_text,
        generate_quiz_items,
        explain_concept,
        is_genai_material,
    )


def clean_quiz_question(question, language=None):
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
    return question.replace("PDF-ja", "materiali").replace("PDF", "material").strip()


def is_material_overview_question(question):
    normalized = question.lower().strip()
    normalized = normalized.replace("ç", "c").replace("ë", "e")
    overview_phrases = (
        "cfare permban materiali",
        "qfare permban materiali",
        "cka permban materiali",
        "cfa permban materiali",
        "per cka eshte materiali",
        "per cfare eshte materiali",
        "me trego per materialin",
        "me trego cfare permban",
        "what does the material contain",
        "what is this material about",
        "summarize the material",
    )
    return any(phrase in normalized for phrase in overview_phrases)


def answer_material_overview():
    pdf_text = st.session_state.get("pdf_text", "")
    if not pdf_text:
        return (
            "Nuk ka PDF te ngarkuar per kete pamje. Ngarko nje PDF GenAI dhe kliko "
            "`Proceso materialin`, pastaj mund te pyesesh cfare permban materiali."
        )
    return summarize_text(pdf_text)


def save_uploaded_pdf(uploaded_file):
    suffix = Path(uploaded_file.name).suffix or ".pdf"

    with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        return temp_file.name


def read_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)
    pages = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            pages.append(page_text)

    return "\n".join(pages).strip()


def reset_outputs():
    for key in (
        "answer",
        "summary",
        "quiz",
        "explanation",
        "sources",
        "explanation_sources",
        "last_runtime",
        "messages",
        "summary_messages",
    ):
        st.session_state.pop(key, None)

    reset_quiz_choices()


def reset_quiz_choices():
    for key in list(st.session_state):
        if key.startswith("quiz_choice_"):
            st.session_state.pop(key, None)


def short_text(text, max_length=MAX_PARAM_LENGTH):
    text = " ".join(str(text).split())
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def log_mlflow_event(task_type, user_input, generated_answer, response_time):
    if not ENABLE_MLFLOW:
        return

    try:
        import mlflow

        mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

        with mlflow.start_run(run_name=task_type):
            mlflow.log_param("task_type", task_type)
            mlflow.log_param("uploaded_file", st.session_state.get("pdf_name", ""))
            mlflow.log_param("user_question", short_text(user_input))
            mlflow.log_metric("response_time_seconds", round(response_time, 3))
            mlflow.log_text(str(user_input), f"{task_type}_input.txt")
            mlflow.log_text(str(generated_answer), f"{task_type}_answer.txt")

    except Exception as exc:
        st.warning(f"MLflow logging failed: {exc}")


def show_sources(sources):
    if not sources:
        return

    with st.expander("Burimet", expanded=False):
        for index, source in enumerate(sources, start=1):
            st.markdown(f"**{index}. {source['source']}**")
            st.write(source["text"])


def ensure_messages():
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": (
                    "Pershendetje. Upload nje PDF ose perdor bazen GenAI, "
                    "pastaj bej pyetje. Pergjigjet kthehen nga materiali i procesuar."
                ),
            }
        ]


def ensure_summary_messages():
    if "summary_messages" not in st.session_state:
        st.session_state["summary_messages"] = [
            {
                "role": "assistant",
                "content": (
                    "Kjo pamje eshte vetem per permbledhjen dhe pyetje rreth PDF-se "
                    "se ngarkuar."
                ),
            }
        ]


def process_material(uploaded_pdf):
    reset_outputs()

    pdf_files = []
    uploaded_text = ""

    if uploaded_pdf is not None:
        pdf_path = save_uploaded_pdf(uploaded_pdf)
        uploaded_text = read_pdf_text(pdf_path)
        if not uploaded_text:
            raise ValueError("Nuk u gjet tekst i lexueshem ne kete PDF.")
        if not is_genai_material(uploaded_text):
            raise ValueError(
                "Ky dokument nuk duket se ka lidhje me Generative AI. "
                "Ky eshte vetem AI Study Assistant per temat GenAI."
            )
        pdf_files.append(pdf_path)
        st.session_state["pdf_name"] = uploaded_pdf.name
        st.session_state["pdf_text"] = uploaded_text
    else:
        st.session_state["pdf_name"] = ""
        st.session_state["pdf_text"] = ""

    start_time = time.perf_counter()
    build_index(pdf_files)
    st.session_state["last_runtime"] = time.perf_counter() - start_time
    st.session_state["documents_ready"] = True
    st.session_state["view"] = "chat"
    ensure_messages()


def ensure_default_material_ready():
    if st.session_state.get("documents_ready"):
        return

    start_time = time.perf_counter()
    build_index()
    st.session_state["last_runtime"] = time.perf_counter() - start_time
    st.session_state["documents_ready"] = True
    st.session_state["pdf_name"] = ""
    st.session_state["pdf_text"] = ""
    st.session_state.setdefault("view", "chat")
    ensure_messages()


def start_new_chat():
    for key in (
        "messages",
        "summary_messages",
        "answer",
        "summary",
        "quiz",
        "sources",
        "explanation",
        "explanation_sources",
    ):
        st.session_state.pop(key, None)
    reset_quiz_choices()
    st.session_state["view"] = "chat"
    ensure_messages()


def render_topbar(documents_ready):
    material = st.session_state.get("pdf_name") or "Baza GenAI"
    status = "Gati" if documents_ready else "Duke u pergatitur"

    st.markdown(
        f"""
        <div class="topbar">
            <div>
                <h1>AI Study Assistant</h1>
                <div class="subtitle">
                    Pyet shpejt, merr pergjigje nga materiali, krijo permbledhje dhe quiz.
                </div>
            </div>
            <div class="status-pill">{html.escape(status)} - {html.escape(material)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_quick_actions(documents_ready):
    st.markdown(
        """
        <div class="quick-grid">
            <div class="quick-card">
                <div class="quick-title">Pyetje</div>
                <div class="quick-copy">Shkruaj poshte dhe merr pergjigje te bazuar ne burime.</div>
            </div>
            <div class="quick-card">
                <div class="quick-title">Permbledhje PDF</div>
                <div class="quick-copy">Pas upload-it, nxirr pikat kryesore pa pritur gjate.</div>
            </div>
            <div class="quick-card">
                <div class="quick-title">Quiz</div>
                <div class="quick-copy">Gjenero pyetje me alternativa dhe kontrollo pergjigjet menjehere.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_chat, col_summary, col_quiz = st.columns(3)
    with col_chat:
        chat_clicked = st.button(
            "Chat me materialin",
            disabled=not documents_ready,
            use_container_width=True,
        )
    with col_summary:
        summarize_clicked = st.button(
            "Permbledh PDF",
            disabled=not documents_ready or not st.session_state.get("pdf_text"),
            use_container_width=True,
        )
    with col_quiz:
        quiz_clicked = st.button(
            "Gjenero Quiz",
            disabled=not documents_ready or not st.session_state.get("pdf_text"),
            use_container_width=True,
        )

    if chat_clicked:
        st.session_state["view"] = "chat"
        st.rerun()

    if summarize_clicked:
        should_rerun = False
        with st.spinner("Duke bere permbledhjen..."):
            try:
                start_time = time.perf_counter()
                summary = summarize_text(st.session_state["pdf_text"])
                response_time = time.perf_counter() - start_time
                st.session_state["summary"] = summary
                st.session_state["view"] = "summary"
                ensure_summary_messages()
                log_mlflow_event("summary", st.session_state["pdf_name"], summary, response_time)
                should_rerun = True
            except Exception as exc:
                st.error(f"Nuk u krijua permbledhja: {exc}")
        if should_rerun:
            st.rerun()

    if quiz_clicked:
        should_rerun = False
        with st.spinner("Duke gjeneruar quiz-in..."):
            try:
                reset_quiz_choices()
                start_time = time.perf_counter()
                quiz = generate_quiz_items(st.session_state["pdf_text"])
                response_time = time.perf_counter() - start_time
                st.session_state["quiz"] = quiz
                st.session_state["quiz_format_version"] = QUIZ_FORMAT_VERSION
                st.session_state["view"] = "quiz"
                log_mlflow_event("quiz", st.session_state["pdf_name"], quiz, response_time)
                should_rerun = True
            except Exception as exc:
                st.error(f"Nuk u krijua quiz-i: {exc}")
        if should_rerun:
            st.rerun()


def render_chat(documents_ready):
    ensure_messages()

    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input(
        "Bej nje pyetje per materialin...",
        disabled=not documents_ready,
    )

    if not prompt:
        return

    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Duke kerkuar ne material..."):
            try:
                start_time = time.perf_counter()
                result = ask_question(prompt.strip())
                response_time = time.perf_counter() - start_time
                answer = result["answer"]
                st.session_state["answer"] = answer
                st.session_state["sources"] = result["sources"]
                st.session_state["last_runtime"] = response_time
                log_mlflow_event("question", prompt.strip(), answer, response_time)
            except Exception as exc:
                answer = f"Nuk munda ta pergjigjem pyetjen: {exc}"
                st.session_state["sources"] = []

        st.markdown(answer)
        if st.session_state.get("last_runtime") is not None:
            st.markdown(
                f"<div class='result-meta'>Koha: {st.session_state['last_runtime']:.2f}s</div>",
                unsafe_allow_html=True,
            )

    st.session_state["messages"].append({"role": "assistant", "content": answer})


def render_pdf_question_chat():
    ensure_summary_messages()

    st.subheader("Pyetje rreth PDF-se")
    for message in st.session_state["summary_messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input(
        "Pyet vetem rreth PDF-se se ngarkuar...",
        disabled=not st.session_state.get("pdf_text"),
        key="summary_chat_input",
    )

    if not prompt:
        return

    st.session_state["summary_messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Duke kerkuar ne PDF dhe bazen GenAI..."):
            try:
                start_time = time.perf_counter()
                if is_material_overview_question(prompt):
                    answer = answer_material_overview()
                    sources = []
                else:
                    result = ask_question(prompt.strip())
                    answer = result["answer"]
                    sources = result["sources"]
                response_time = time.perf_counter() - start_time
                st.session_state["sources"] = sources
                st.session_state["last_runtime"] = response_time
                log_mlflow_event("pdf_question", prompt.strip(), answer, response_time)
            except Exception as exc:
                answer = f"Nuk munda ta pergjigjem pyetjen: {exc}"
                st.session_state["sources"] = []

        st.markdown(answer)
        if st.session_state.get("last_runtime") is not None:
            st.markdown(
                f"<div class='result-meta'>Koha: {st.session_state['last_runtime']:.2f}s</div>",
                unsafe_allow_html=True,
            )

    st.session_state["summary_messages"].append({"role": "assistant", "content": answer})


def render_summary():
    if not st.session_state.get("summary"):
        return

    st.subheader("Permbledhje")
    st.markdown(st.session_state["summary"])
    render_pdf_question_chat()


def render_quiz(quiz_items):
    if not quiz_items:
        return

    st.subheader("Quiz")
    if isinstance(quiz_items, str):
        st.warning(quiz_items)
        return
    if st.session_state.get("quiz_format_version") != QUIZ_FORMAT_VERSION:
        st.session_state.pop("quiz", None)
        reset_quiz_choices()
        st.session_state["view"] = "chat"
        st.warning("Quiz-i i vjeter u pastrua. Kliko `Gjenero Quiz` perseri per versionin e ri.")
        return

    correct_count = 0
    answered_count = 0

    for index, item in enumerate(quiz_items):
        with st.container(border=True):
            if item.get("concept"):
                st.caption(f"Koncepti: {item['concept']}")
            question = clean_quiz_question(item["question"])
            st.markdown(f"**{index + 1}. {question}**")
            choice = st.radio(
                "Zgjidh pergjigjen",
                item["options"],
                index=None,
                key=f"quiz_choice_{index}",
                label_visibility="collapsed",
            )

            if choice:
                answered_count += 1
                if choice == item["answer"]:
                    correct_count += 1
                    st.success("Sakte.")
                else:
                    st.error(f"Gabim. Pergjigjja e sakte: {item['answer']}")

    if answered_count:
        st.caption(f"Rezultati: {correct_count}/{answered_count}")


build_index, ask_question, retrieve_sources = load_rag_functions()
(
    summarize_text,
    generate_quiz_items,
    explain_concept,
    is_genai_material,
) = load_study_functions()

apply_custom_style()
try:
    ensure_default_material_ready()
except Exception as exc:
    st.session_state["documents_ready"] = False
    st.error(f"Nuk u pergatit baza GenAI: {exc}")

documents_ready = st.session_state.get("documents_ready", False)

with st.sidebar:
    st.header("Materiali")
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    process_documents = st.button("Proceso materialin", type="primary", use_container_width=True)
    new_chat_clicked = st.button("Chat i ri", use_container_width=True)

    if new_chat_clicked:
        start_new_chat()
        st.rerun()

    if process_documents:
        with st.spinner("Duke lexuar PDF dhe duke ndertuar indeksin..."):
            try:
                process_material(uploaded_pdf)
                documents_ready = True
                st.success("Materiali eshte gati.")
            except Exception as exc:
                st.session_state["documents_ready"] = False
                documents_ready = False
                st.error(f"Nuk u procesua materiali: {exc}")

    st.divider()
    if documents_ready:
        st.success("Gati per pyetje")
        st.caption(st.session_state.get("pdf_name") or "Baza GenAI")
    else:
        st.info("Baza GenAI po pergatitet. PDF eshte opsional.")

    if st.session_state.get("last_runtime") is not None:
        st.caption(f"Operacioni i fundit: {st.session_state['last_runtime']:.2f}s")

    if st.session_state.get("sources"):
        show_sources(st.session_state["sources"])

render_topbar(documents_ready)
render_quick_actions(documents_ready)

current_view = st.session_state.get("view", "chat")
if current_view == "summary":
    render_summary()
elif current_view == "quiz":
    render_quiz(st.session_state.get("quiz"))
else:
    render_chat(documents_ready)

if not documents_ready:
    st.info("Baza GenAI nuk u pergatit ende. Mund te provosh perseri ose te ngarkosh PDF GenAI.")
