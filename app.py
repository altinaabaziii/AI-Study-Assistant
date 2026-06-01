from pathlib import Path
from tempfile import NamedTemporaryFile
import html
import time

import streamlit as st
from pypdf import PdfReader


APP_NAME = "GenAI Study Assistant"
MLFLOW_EXPERIMENT_NAME = "GenAIStudyAssistant"
MAX_PARAM_LENGTH = 250


st.set_page_config(
    page_title=APP_NAME,
    page_icon=":material/school:",
    layout="wide",
)


def apply_custom_style():
    st.markdown(
        """
        <style>
        :root {
            --app-bg: #000000;
            --panel: #0a0a0a;
            --panel-soft: #111111;
            --panel-hover: #171717;
            --border: #242424;
            --border-strong: #3f3f46;
            --text: #fafafa;
            --muted: #a1a1aa;
            --muted-2: #71717a;
            --accent: #ffffff;
            --blue: #60a5fa;
            --amber: #f59e0b;
            --success: #16a34a;
            --danger: #ef4444;
        }

        .stApp {
            background:
                linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px),
                var(--app-bg);
            background-size: 42px 42px;
            color: var(--text);
        }

        header[data-testid="stHeader"] {
            background: rgba(0, 0, 0, 0.72);
            backdrop-filter: blur(14px);
            border-bottom: 1px solid rgba(255,255,255,0.08);
        }

        [data-testid="stSidebar"] {
            background: rgba(5, 5, 5, 0.98);
            border-right: 1px solid var(--border);
        }

        [data-testid="stSidebar"] * {
            color: var(--text);
        }

        .block-container {
            max-width: 1240px;
            padding-top: 2.4rem;
            padding-bottom: 4rem;
        }

        h1 {
            font-size: clamp(2.4rem, 5vw, 5rem) !important;
            font-weight: 780 !important;
            letter-spacing: 0 !important;
            line-height: 0.96 !important;
            margin: 0 !important;
        }

        h2, h3 {
            letter-spacing: 0 !important;
            color: var(--text) !important;
        }

        p, label, span {
            color: var(--muted);
        }

        div[data-testid="stCaptionContainer"] {
            max-width: 820px;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {
            background: #050505;
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text);
            min-height: 2.9rem;
        }

        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextArea"] textarea:focus {
            border-color: #ffffff;
            box-shadow: 0 0 0 1px #ffffff;
        }

        div.stButton > button {
            border-radius: 8px;
            border: 1px solid var(--border);
            background: #ffffff;
            color: #000000;
            font-weight: 650;
            min-height: 2.75rem;
            box-shadow: 0 0 0 1px rgba(255,255,255,0.08), 0 12px 30px rgba(0,0,0,0.28);
            transition: border-color 120ms ease, transform 120ms ease, background 120ms ease;
        }

        div.stButton > button:hover {
            border-color: #ffffff;
            transform: translateY(-1px);
            background: #f4f4f5;
        }

        div.stButton > button:disabled {
            background: #111111;
            color: #737373;
            border-color: var(--border);
            transform: none;
        }

        div[data-testid="stAlert"] {
            border-radius: 8px;
            border: 1px solid var(--border);
            background: rgba(10,10,10,0.86);
        }

        div[data-testid="stExpander"] {
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--panel);
        }

        div[data-testid="stFileUploader"] section {
            background: #050505;
            border: 1px dashed var(--border-strong);
            border-radius: 8px;
        }

        div[data-testid="stFileUploader"] button {
            border-radius: 8px;
        }

        .sidebar-brand {
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.9rem;
            background: linear-gradient(180deg, #111111 0%, #050505 100%);
            margin-bottom: 1rem;
        }

        .sidebar-brand-title {
            color: var(--text);
            font-size: 0.92rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }

        .sidebar-brand-subtitle {
            color: var(--muted);
            font-size: 0.78rem;
            line-height: 1.45;
        }

        .app-hero {
            display: grid;
            grid-template-columns: minmax(0, 1.4fr) minmax(280px, 0.6fr);
            gap: 1rem;
            align-items: stretch;
            margin-bottom: 1.1rem;
        }

        .app-kicker {
            color: var(--text);
            font-size: 0.9rem;
            font-weight: 700;
            margin-bottom: 0.7rem;
            display: flex;
            align-items: center;
            gap: 0.55rem;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 999px;
            background: var(--success);
            display: inline-block;
            box-shadow: 0 0 18px rgba(22, 163, 74, 0.8);
        }

        .hero-copy {
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.4rem;
            background:
                linear-gradient(180deg, rgba(255,255,255,0.07), rgba(255,255,255,0.015)),
                #050505;
            overflow: hidden;
            position: relative;
        }

        .hero-copy:after {
            content: "";
            position: absolute;
            inset: auto -20% -40% 40%;
            height: 220px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.10), transparent);
            transform: rotate(-12deg);
        }

        .hero-copy p {
            max-width: 720px;
            color: var(--muted);
            font-size: 1rem;
            line-height: 1.7;
            margin: 1rem 0 0;
            position: relative;
            z-index: 1;
        }

        .hero-title {
            position: relative;
            z-index: 1;
        }

        .hero-panel {
            border: 1px solid var(--border);
            border-radius: 8px;
            background: #050505;
            padding: 1rem;
        }

        .hero-panel-title {
            color: var(--text);
            font-weight: 700;
            margin-bottom: 0.85rem;
        }

        .metric-list {
            display: grid;
            gap: 0.55rem;
        }

        .metric-row {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            padding: 0.72rem 0.78rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: #0a0a0a;
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.78rem;
        }

        .metric-value {
            color: var(--text);
            font-weight: 700;
            font-size: 0.8rem;
            text-align: right;
        }

        .command-strip {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.75rem;
            margin: 1rem 0 1.4rem;
        }

        .command-card {
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.9rem;
            background: rgba(8,8,8,0.92);
        }

        .command-label {
            color: var(--muted);
            font-size: 0.75rem;
            font-weight: 650;
            text-transform: uppercase;
            letter-spacing: 0;
            margin-bottom: 0.35rem;
        }

        .command-value {
            color: var(--text);
            font-size: 0.92rem;
            line-height: 1.45;
        }

        .section-shell {
            border: 1px solid var(--border);
            border-radius: 8px;
            background: rgba(5,5,5,0.94);
            padding: 1.05rem;
            margin-bottom: 1rem;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
        }

        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1rem;
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.9rem;
            margin-bottom: 1rem;
        }

        .section-title {
            color: var(--text);
            font-size: 1rem;
            font-weight: 740;
            margin-bottom: 0.2rem;
        }

        .section-subtitle {
            color: var(--muted);
            font-size: 0.83rem;
            line-height: 1.5;
        }

        .badge {
            border: 1px solid var(--border);
            border-radius: 999px;
            color: var(--muted);
            padding: 0.22rem 0.55rem;
            font-size: 0.72rem;
            white-space: nowrap;
            background: #0a0a0a;
        }

        div[data-testid="stTabs"] [data-baseweb="tab-list"] {
            gap: 0.4rem;
            border-bottom: 1px solid var(--border);
        }

        div[data-testid="stTabs"] [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            color: var(--muted);
            font-weight: 650;
        }

        div[data-testid="stTabs"] [aria-selected="true"] {
            background: #111111;
            color: #ffffff;
        }

        .quiz-item {
            border: 1px solid var(--border);
            border-radius: 8px;
            background: #050505;
            padding: 1rem;
            margin: 0.85rem 0;
        }

        .quiz-question {
            color: var(--text);
            font-weight: 650;
            margin-bottom: 0.45rem;
        }

        .feedback-ok {
            color: var(--success);
            font-weight: 650;
            margin-top: 0.65rem;
        }

        .feedback-bad {
            color: var(--danger);
            font-weight: 650;
            margin-top: 0.65rem;
        }

        div[role="radiogroup"] label {
            background: #050505;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.48rem 0.65rem;
            margin-bottom: 0.35rem;
        }

        div[role="radiogroup"] label:hover {
            border-color: var(--border-strong);
            background: #0b0b0b;
        }

        @media (max-width: 900px) {
            .app-hero,
            .command-strip {
                grid-template-columns: 1fr;
            }

            .block-container {
                padding-top: 1.2rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def load_rag_functions():
    from rag_engine import ask_question, build_index, retrieve_sources

    return build_index, ask_question, retrieve_sources


def load_study_functions():
    from study_tools import explain_concept, generate_quiz_items, summarize_text

    return summarize_text, generate_quiz_items, explain_concept


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
    ):
        st.session_state.pop(key, None)

    for key in list(st.session_state):
        if key.startswith("quiz_choice_"):
            st.session_state.pop(key, None)


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

    with st.expander("Retrieved source text", expanded=False):
        for index, source in enumerate(sources, start=1):
            st.markdown(f"**Source {index}: {source['source']}**")
            st.write(source["text"])


def render_hero(documents_ready):
    material = st.session_state.get("pdf_name") or "Built-in GenAI library"
    index_status = "Ready" if documents_ready else "Not processed"
    source_status = "Uploaded PDF" if st.session_state.get("pdf_name") else "Knowledge base"
    access_status = "Local and fast"

    st.markdown(
        f"""
        <div class="app-hero">
            <section class="hero-copy">
                <div class="app-kicker">
                    <span class="status-dot"></span>
                    Local RAG study workspace
                </div>
                <div class="hero-title">
                    <h1>GenAI Study Assistant</h1>
                </div>
                <p>
                    A focused study console for asking source-grounded questions,
                    generating concise notes, and practicing with instant quiz feedback.
                </p>
            </section>
            <aside class="hero-panel">
                <div class="hero-panel-title">Workspace status</div>
                <div class="metric-list">
                    <div class="metric-row">
                        <span class="metric-label">Index</span>
                        <span class="metric-value">{html.escape(index_status)}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Source</span>
                        <span class="metric-value">{html.escape(source_status)}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Material</span>
                        <span class="metric-value">{html.escape(material)}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Mode</span>
                        <span class="metric-value">{html.escape(access_status)}</span>
                    </div>
                </div>
            </aside>
        </div>
        <div class="command-strip">
            <div class="command-card">
                <div class="command-label">Ask</div>
                <div class="command-value">Search the processed material and get a grounded answer.</div>
            </div>
            <div class="command-card">
                <div class="command-label">Study</div>
                <div class="command-value">Summarize notes or explain a specific GenAI concept.</div>
            </div>
            <div class="command-card">
                <div class="command-label">Practice</div>
                <div class="command-value">Open an interactive quiz window with instant corrections.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_quiz(quiz_items):
    if isinstance(quiz_items, str):
        st.warning(quiz_items)
        return

    correct_count = 0
    answered_count = 0

    for index, item in enumerate(quiz_items):
        with st.container(border=True):
            st.markdown(f"**{index + 1}. {item['question']}**")
            choice = st.radio(
                "Choose an answer",
                item["options"],
                index=None,
                key=f"quiz_choice_{index}",
                label_visibility="collapsed",
            )

            if choice:
                answered_count += 1
                if choice == item["answer"]:
                    correct_count += 1
                    st.success("Sakte. Kjo eshte pergjigjja e duhur.")
                else:
                    st.error(f"Gabim. Pergjigjja e sakte: {item['answer']}")

    if answered_count:
        st.caption(f"Score: {correct_count}/{answered_count} answered correctly")


@st.dialog("Quiz Practice", width="large")
def show_quiz_dialog():
    st.caption("Choose one answer for each question. Feedback appears immediately.")
    render_quiz(st.session_state.get("quiz"))

    if st.button("Close Quiz", use_container_width=True):
        st.session_state["show_quiz_dialog"] = False
        st.rerun()


build_index, ask_question, retrieve_sources = load_rag_functions()
summarize_text, generate_quiz_items, explain_concept = load_study_functions()

apply_custom_style()
documents_ready = st.session_state.get("documents_ready", False)

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-title">GenAI Workspace</div>
            <div class="sidebar-brand-subtitle">
                Upload notes, build the study index, then ask, summarize, or practice.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.header("Study Materials")
    uploaded_pdf = st.file_uploader("Upload PDF notes or slides", type=["pdf"])
    process_documents = st.button(
        "Process Documents",
        type="primary",
        use_container_width=True,
    )

    st.markdown("Built-in knowledge base: `data/genai_knowledge_base/`")

    if st.session_state.get("documents_ready"):
        st.success("Documents processed")
        if st.session_state.get("pdf_name"):
            st.write(st.session_state["pdf_name"])
        else:
            st.write("Built-in GenAI knowledge base only")
    else:
        st.info("Process documents to build the GenAI study index.")

if process_documents:
    reset_outputs()

    with st.spinner("Reading materials and building the GenAI study index..."):
        try:
            pdf_files = []
            uploaded_text = ""

            if uploaded_pdf is not None:
                pdf_path = save_uploaded_pdf(uploaded_pdf)
                uploaded_text = read_pdf_text(pdf_path)
                if not uploaded_text:
                    raise ValueError("No readable text was found in this PDF.")
                pdf_files.append(pdf_path)
                st.session_state["pdf_name"] = uploaded_pdf.name
                st.session_state["pdf_text"] = uploaded_text
            else:
                st.session_state["pdf_name"] = ""
                st.session_state["pdf_text"] = ""

            build_index(pdf_files)

        except Exception as exc:
            st.session_state["documents_ready"] = False
            documents_ready = False
            st.error(f"Could not process documents: {exc}")
        else:
            st.session_state["documents_ready"] = True
            documents_ready = True
            st.success("GenAI study index created successfully.")

render_hero(documents_ready)

left_column, right_column = st.columns([1, 1], gap="large")

with left_column:
    st.markdown('<div class="section-shell">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-header">
            <div>
                <div class="section-title">Ask Questions</div>
                <div class="section-subtitle">
                    Query your uploaded notes and the built-in GenAI knowledge base.
                </div>
            </div>
            <span class="badge">RAG search</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    question = st.text_input(
        "Question",
        placeholder="Example: How does RAG use embeddings and vector search?",
        disabled=not documents_ready,
    )

    ask_clicked = st.button(
        "Ask Question",
        disabled=not documents_ready or not question.strip(),
        use_container_width=True,
    )

    if ask_clicked:
        with st.spinner("Retrieving GenAI material and preparing an answer..."):
            try:
                start_time = time.perf_counter()
                result = ask_question(question.strip())
                response_time = time.perf_counter() - start_time

                st.session_state["answer"] = result["answer"]
                st.session_state["sources"] = result["sources"]
                log_mlflow_event("question", question.strip(), result["answer"], response_time)
            except Exception as exc:
                st.error(f"Could not answer question: {exc}")

    if st.session_state.get("answer"):
        st.markdown("#### Answer")
        st.info(st.session_state["answer"])
        show_sources(st.session_state.get("sources", []))
    st.markdown("</div>", unsafe_allow_html=True)

with right_column:
    st.markdown('<div class="section-shell">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-header">
            <div>
                <div class="section-title">Study Tools</div>
                <div class="section-subtitle">
                    Turn the same material into notes, practice questions, or concept explanations.
                </div>
            </div>
            <span class="badge">Workspace</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    summary_tab, quiz_tab, explain_tab = st.tabs(["Summary", "Quiz", "Explain"])

    with summary_tab:
        summarize_clicked = st.button(
            "Summarize Material",
            disabled=not documents_ready or not st.session_state.get("pdf_text"),
            use_container_width=True,
        )

        if summarize_clicked:
            with st.spinner("Creating a GenAI summary..."):
                try:
                    start_time = time.perf_counter()
                    summary = summarize_text(st.session_state["pdf_text"])
                    response_time = time.perf_counter() - start_time

                    st.session_state["summary"] = summary
                    log_mlflow_event(
                        "summary",
                        st.session_state["pdf_name"],
                        summary,
                        response_time,
                    )
                except Exception as exc:
                    st.error(f"Could not create summary: {exc}")

        if st.session_state.get("summary"):
            st.markdown("#### Summary")
            st.success(st.session_state["summary"])
        else:
            st.caption("Upload and process a PDF to create a concise study summary.")

    with quiz_tab:
        quiz_clicked = st.button(
            "Generate Quiz",
            disabled=not documents_ready or not st.session_state.get("pdf_text"),
            use_container_width=True,
        )

        if quiz_clicked:
            with st.spinner("Creating GenAI quiz questions..."):
                try:
                    reset_quiz_choices()
                    start_time = time.perf_counter()
                    quiz = generate_quiz_items(st.session_state["pdf_text"])
                    response_time = time.perf_counter() - start_time

                    st.session_state["quiz"] = quiz
                    st.session_state["show_quiz_dialog"] = True
                    log_mlflow_event("quiz", st.session_state["pdf_name"], quiz, response_time)
                except Exception as exc:
                    st.error(f"Could not create quiz: {exc}")

        if st.session_state.get("quiz"):
            st.button(
                "Open Quiz Window",
                key="open_quiz_window",
                on_click=lambda: st.session_state.update(show_quiz_dialog=True),
                use_container_width=True,
            )
            st.caption("The quiz opens in a separate practice window.")
        else:
            st.caption("Generate a multiple-choice quiz from your uploaded notes.")

    with explain_tab:
        concept = st.text_input(
            "Concept",
            placeholder="Example: context engineering",
            disabled=not documents_ready,
        )

        explain_clicked = st.button(
            "Explain Concept",
            disabled=not documents_ready or not concept.strip(),
            use_container_width=True,
        )

        if explain_clicked:
            with st.spinner("Explaining the GenAI concept..."):
                try:
                    start_time = time.perf_counter()
                    sources = retrieve_sources(concept.strip())
                    context = "\n\n".join(source["text"] for source in sources)
                    explanation = explain_concept(concept.strip(), context)
                    response_time = time.perf_counter() - start_time

                    st.session_state["explanation"] = explanation
                    st.session_state["explanation_sources"] = sources
                    log_mlflow_event("explanation", concept.strip(), explanation, response_time)
                except Exception as exc:
                    st.error(f"Could not explain concept: {exc}")

        if st.session_state.get("explanation"):
            st.markdown("#### Explanation")
            st.info(st.session_state["explanation"])
            show_sources(st.session_state.get("explanation_sources", []))
        else:
            st.caption("Enter a GenAI concept and get a short explanation from the material.")
    st.markdown("</div>", unsafe_allow_html=True)

if not documents_ready:
    st.divider()
    st.write(
        "This assistant is not a general chatbot. It answers only Generative AI "
        "questions using uploaded materials and the built-in GenAI knowledge base."
    )

if st.session_state.get("show_quiz_dialog") and st.session_state.get("quiz"):
    show_quiz_dialog()
