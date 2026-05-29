import re

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


# Free and open-source model. This does not use any paid API.
MODEL_NAME = "google/flan-t5-base"

tokenizer = None
model = None
device = "cuda" if torch.cuda.is_available() else "cpu"


def load_model():
    """Load the model one time and reuse it."""
    global tokenizer, model

    if tokenizer is None or model is None:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(device)


def generate_text(prompt, max_new_tokens=250):
    """Send a prompt to the model and return the generated text."""
    load_model()

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512,
    )
    inputs = {name: value.to(device) for name, value in inputs.items()}

    output_ids = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=False,
    )

    return tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()


def clean_model_text(text):
    """Keep generated text short and easy to read."""
    return " ".join(text.replace("\n", " ").split())


def get_study_points(text, count=5):
    """Pick simple text parts that can become quiz questions."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    points = [sentence.strip() for sentence in sentences if sentence.strip()]

    if not points:
        points = [text.strip()]

    if len(points) < count and len(points) > 1:
        points.append(" ".join(points))

    while len(points) < count:
        points.append(points[len(points) % len(points)])

    return points[:count]


def summarize_text(text):
    """Create a short and simple summary from study text."""
    if not text or not text.strip():
        return "Please provide some text to summarize."

    prompt = (
        "Summarize this study text in simple language. "
        "Use short sentences and include only the main ideas.\n\n"
        f"Text:\n{text.strip()}\n\n"
        "Summary:"
    )

    return generate_text(prompt, max_new_tokens=180)


def generate_quiz(text):
    """Create 5 beginner-friendly quiz questions with answers."""
    if not text or not text.strip():
        return "Please provide some text to create a quiz."

    quiz_items = []
    used_questions = set()

    for index, point in enumerate(get_study_points(text), start=1):
        question_prompt = (
            "Write one short quiz question in simple language. "
            "Use only this study fact.\n\n"
            f"Study fact: {point}\n\n"
            "Question:"
        )

        question = clean_model_text(generate_text(question_prompt, max_new_tokens=60))

        if not question:
            question = f"What is one important idea from fact {index}?"
        if not question.endswith("?"):
            question = f"{question}?"

        if question.lower() in used_questions:
            question = f"What does study fact {index} say?"
        used_questions.add(question.lower())

        answer = point

        quiz_items.append(f"{index}. Question: {question}\n   Answer: {answer}")

    return "\n".join(quiz_items)
