from pathlib import Path
from tempfile import NamedTemporaryFile
import time

import mlflow
import streamlit as st
from pypdf import PdfReader


MLFLOW_EXPERIMENT_NAME = "StudyMateAI"
MAX_PARAM_LENGTH = 250


st.set_page_config(
    page_title="StudyMateAI",
    page_icon=":books:",
    layout="wide",
)


@st.cache_resource(show_spinner="Loading RAG engine...")
def load_rag_functions():
    from rag_engine import ask_question, build_index

    return build_index, ask_question


@st.cache_resource(show_spinner="Loading study tools...")
def load_study_functions():
    from study_tools import generate_quiz, summarize_text

    return summarize_text, generate_quiz


def save_uploaded_pdf(uploaded_file):
    """Save an uploaded PDF to a temporary file and return its path."""
    suffix = Path(uploaded_file.name).suffix or ".pdf"

    with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        return temp_file.name


def read_pdf_text(pdf_path):
    """Extract text from a PDF file for summary and quiz generation."""
    reader = PdfReader(pdf_path)
    pages = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            pages.append(page_text)

    return "\n".join(pages).strip()


def reset_outputs():
    """Clear old outputs when a new PDF is processed."""
    for key in ("answer", "summary", "quiz"):
        st.session_state.pop(key, None)


def short_text(text, max_length=MAX_PARAM_LENGTH):
    """Keep MLflow params small and readable."""
    text = " ".join(str(text).split())
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def log_mlflow_event(action, input_text, output_text, response_time):
    """Log one user action to MLflow without interrupting the app."""
    try:
        mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

        with mlflow.start_run(run_name=action):
            mlflow.log_param("action", action)
            mlflow.log_param("pdf_name", st.session_state.get("pdf_name", ""))
            mlflow.log_param("input_preview", short_text(input_text))
            mlflow.log_metric("response_time_seconds", round(response_time, 3))
            mlflow.log_text(str(input_text), f"{action}_input.txt")
            mlflow.log_text(str(output_text), f"{action}_output.txt")

    except Exception as exc:
        st.warning(f"MLflow logging failed: {exc}")


build_index, ask_question = load_rag_functions()
summarize_text, generate_quiz = load_study_functions()

st.title("StudyMateAI")
st.caption("Upload a PDF, process it, then ask questions, summarize, or create a quiz.")

with st.sidebar:
    st.header("PDF")
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    process_pdf = st.button(
        "Process PDF",
        type="primary",
        use_container_width=True,
        disabled=uploaded_pdf is None,
    )

    if st.session_state.get("pdf_ready"):
        st.success("PDF processed")
        st.write(st.session_state.get("pdf_name", "Current PDF"))
    else:
        st.info("Upload and process a PDF to begin.")

if process_pdf:
    reset_outputs()

    with st.spinner("Reading PDF and building study index..."):
        try:
            pdf_path = save_uploaded_pdf(uploaded_pdf)
            pdf_text = read_pdf_text(pdf_path)

            if not pdf_text:
                raise ValueError("No readable text was found in this PDF.")

            build_index([pdf_path])

        except Exception as exc:
            st.session_state["pdf_ready"] = False
            st.error(f"Could not process PDF: {exc}")
        else:
            st.session_state["pdf_ready"] = True
            st.session_state["pdf_name"] = uploaded_pdf.name
            st.session_state["pdf_path"] = pdf_path
            st.session_state["pdf_text"] = pdf_text
            st.success("PDF processed successfully.")

pdf_ready = st.session_state.get("pdf_ready", False)

left_column, right_column = st.columns([1, 1], gap="large")

with left_column:
    st.subheader("Ask Question")
    question = st.text_input(
        "Question",
        placeholder="Example: What is this document about?",
        disabled=not pdf_ready,
    )

    ask_clicked = st.button(
        "Ask Question",
        disabled=not pdf_ready or not question.strip(),
        use_container_width=True,
    )

    if ask_clicked:
        with st.spinner("Searching the PDF and generating an answer..."):
            try:
                start_time = time.perf_counter()
                answer = ask_question(question.strip())
                response_time = time.perf_counter() - start_time

                st.session_state["answer"] = answer
                log_mlflow_event("question", question.strip(), answer, response_time)
            except Exception as exc:
                st.error(f"Could not answer question: {exc}")

    if st.session_state.get("answer"):
        st.markdown("#### Answer")
        st.info(st.session_state["answer"])

with right_column:
    st.subheader("Study Tools")

    summarize_clicked = st.button(
        "Summarize",
        disabled=not pdf_ready,
        use_container_width=True,
    )

    quiz_clicked = st.button(
        "Generate Quiz",
        disabled=not pdf_ready,
        use_container_width=True,
    )

    if summarize_clicked:
        with st.spinner("Creating summary..."):
            try:
                start_time = time.perf_counter()
                summary = summarize_text(st.session_state["pdf_text"])
                response_time = time.perf_counter() - start_time

                st.session_state["summary"] = summary
                log_mlflow_event(
                    "summary",
                    st.session_state["pdf_text"],
                    summary,
                    response_time,
                )
            except Exception as exc:
                st.error(f"Could not create summary: {exc}")

    if quiz_clicked:
        with st.spinner("Creating quiz..."):
            try:
                start_time = time.perf_counter()
                quiz = generate_quiz(st.session_state["pdf_text"])
                response_time = time.perf_counter() - start_time

                st.session_state["quiz"] = quiz
                log_mlflow_event(
                    "quiz",
                    st.session_state["pdf_text"],
                    quiz,
                    response_time,
                )
            except Exception as exc:
                st.error(f"Could not create quiz: {exc}")

    if st.session_state.get("summary"):
        st.markdown("#### Summary")
        st.success(st.session_state["summary"])

    if st.session_state.get("quiz"):
        st.markdown("#### Quiz")
        st.code(st.session_state["quiz"], language="text")

if not pdf_ready:
    st.divider()
    st.write("Start by uploading a PDF in the sidebar.")
