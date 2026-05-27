from pathlib import Path


PDF_NAME = "InstruksionetVT_sq-AL.pdf"


def escape_pdf_text(text):
    """Escape characters that have special meaning inside PDF text."""
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def create_sample_pdf(output_path):
    """Create a simple PDF file using only built-in Python code."""
    lines = [
        "StudyMateAI - Material testues",
        "",
        "StudyMateAI eshte nje asistent studimi me GenAI.",
        "Ai lexon dokumente PDF, ndan tekstin ne pjese te vogla,",
        "krijon embeddings me modelin all-MiniLM-L6-v2 dhe i ruan ne FAISS.",
        "",
        "Kur studenti ben nje pyetje, sistemi kerkon pjeset me relevante",
        "nga dokumenti dhe perdor modelin google/flan-t5-base per te gjeneruar pergjigje.",
        "",
        "Ky projekt perdor vetem mjete falas dhe open-source.",
        "Nuk perdor OpenAI API.",
        "",
        "English summary:",
        "StudyMateAI is a GenAI study assistant.",
        "It reads PDF files, creates embeddings, stores them in FAISS,",
        "retrieves relevant chunks, and answers questions with google/flan-t5-base.",
        "This project uses free and open-source tools.",
        "This project does not use the OpenAI API.",
        "",
        "Shembull pyetje:",
        "What does StudyMateAI do?",
        "Which model creates embeddings?",
        "Does this project use OpenAI API?",
    ]

    text_commands = ["BT", "/F1 14 Tf", "72 760 Td", "18 TL"]
    for line in lines:
        text_commands.append(f"({escape_pdf_text(line)}) Tj")
        text_commands.append("T*")
    text_commands.append("ET")

    stream = "\n".join(text_commands).encode("latin-1")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]

    pdf = bytearray()
    pdf.extend(b"%PDF-1.4\n")
    offsets = []

    for number, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")

    for offset in offsets:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF\n"
        ).encode("ascii")
    )

    output_path.write_bytes(pdf)


if __name__ == "__main__":
    create_sample_pdf(Path(PDF_NAME))
    print(f"Created {PDF_NAME}")
