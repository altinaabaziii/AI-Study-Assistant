from pathlib import Path
from tempfile import NamedTemporaryFile
import time

import mlflow
import streamlit as st
from pypdf import PdfReader


APP_NAME = "GenAI Study Assistant"
MLFLOW_EXPERIMENT_NAME = "GenAIStudyAssistant"
MAX_PARAM_LENGTH = 250


st.set_page_config(
    page_title=APP_NAME,
    page_icon=":books:",
    layout="wide",
)


@st.cache_resource(show_spinner="Loading GenAI RAG engine...")
def load_rag_functions():
    from rag_engine import ask_question, build_index, retrieve_sources

    return build_index, ask_question, retrieve_sources


@st.cache_resource(show_spinner="Loading study tools...")
def load_study_functions():
    from study_tools import explain_concept, generate_quiz, summarize_text

    return summarize_text, generate_quiz, explain_concept


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
    for key in ("answer", "summary", "quiz", "explanation", "sources"):
        st.session_state.pop(key, None)


def short_text(text, max_length=MAX_PARAM_LENGTH):
    text = " ".join(str(text).split())
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def log_mlflow_event(task_type, user_input, generated_answer, response_time):
    try:
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


build_index, ask_question, retrieve_sources = load_rag_functions()
summarize_text, generate_quiz, explain_concept = load_study_functions()

st.title(APP_NAME)
st.caption(
    "A domain-specific assistant for Generative AI, LLMs, RAG, agents, "
    "MLflow, governance, evaluation, security, and enterprise AI."
)

with st.sidebar:
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

    with st.spinner("Reading materials and building GenAI vector index..."):
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
            st.error(f"Could not process documents: {exc}")
        else:
            st.session_state["documents_ready"] = True
            st.success("GenAI study index created successfully.")

documents_ready = st.session_state.get("documents_ready", False)

left_column, right_column = st.columns([1, 1], gap="large")

with left_column:
    st.subheader("Ask Questions About GenAI")
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

with right_column:
    st.subheader("Study Tools")

    summarize_clicked = st.button(
        "Summarize Material",
        disabled=not documents_ready or not st.session_state.get("pdf_text"),
        use_container_width=True,
    )

    quiz_clicked = st.button(
        "Generate Quiz",
        disabled=not documents_ready or not st.session_state.get("pdf_text"),
        use_container_width=True,
    )

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

    if quiz_clicked:
        with st.spinner("Creating GenAI quiz questions..."):
            try:
                start_time = time.perf_counter()
                quiz = generate_quiz(st.session_state["pdf_text"])
                response_time = time.perf_counter() - start_time

                st.session_state["quiz"] = quiz
                log_mlflow_event("quiz", st.session_state["pdf_name"], quiz, response_time)
            except Exception as exc:
                st.error(f"Could not create quiz: {exc}")

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

    if st.session_state.get("summary"):
        st.markdown("#### Summary")
        st.success(st.session_state["summary"])

    if st.session_state.get("quiz"):
        st.markdown("#### Quiz")
        st.code(st.session_state["quiz"], language="text")

    if st.session_state.get("explanation"):
        st.markdown("#### Intern-Level Explanation")
        st.info(st.session_state["explanation"])
        show_sources(st.session_state.get("explanation_sources", []))

if not documents_ready:
    st.divider()
    st.write(
        "This assistant is not a general chatbot. It answers only Generative AI "
        "questions using uploaded materials and the built-in GenAI knowledge base."
    )
