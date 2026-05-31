from pathlib import Path


PDF_NAME = "GenAI_Test_Material.pdf"


def escape_pdf_text(text):
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def create_pdf(output_path):
    lines = [
        "GenAI Study Assistant - Material testues",
        "",
        "Generative AI, ose GenAI, eshte AI qe krijon permbajtje te re.",
        "Ajo mund te krijoje tekst, permbledhje, kod, ide, shpjegime dhe pergjigje.",
        "",
        "LLM eshte Large Language Model.",
        "LLM trajnohet me tekst dhe perdoret per te kuptuar e gjeneruar gjuhe natyrore.",
        "Shembuj te perdorimit jane chatbot, permbledhje, kerkim ne dokumente dhe ndihme ne kodim.",
        "",
        "Prompt engineering eshte menyra si shkruajme udhezime te qarta per modelin.",
        "Nje prompt i mire tregon rolin, detyren, formatin e pergjigjes dhe kufizimet.",
        "",
        "Context engineering eshte zgjedhja e informacionit qe i jepet modelit.",
        "Konteksti mund te perfshije dokumente, shembuj, rregulla sistemi, histori bisede dhe rezultate nga tools.",
        "",
        "Embeddings jane perfaqesime numerike te tekstit.",
        "Tekste me kuptim te ngjashem duhet te kene embeddings te ngjashme.",
        "Modeli sentence-transformers/all-MiniLM-L6-v2 mund te perdoret per te krijuar embeddings.",
        "",
        "Vector search perdoret per te gjetur tekstin me kuptim me te afert me pyetjen.",
        "FAISS eshte librari lokale per ruajtje dhe kerkim te vektoreve.",
        "",
        "RAG do te thote Retrieval-Augmented Generation.",
        "Ne RAG, sistemi fillimisht ndan dokumentin ne chunks.",
        "Pastaj krijon embeddings per cdo chunk dhe i ruan ne FAISS.",
        "Kur studenti ben pyetje, sistemi gjen chunks me relevante.",
        "Modeli gjuhesor perdor chunks si kontekst per te kthyer pergjigje.",
        "",
        "AI agent eshte sistem qe perdor modelin per te zgjedhur hapa dhe per te perdorur tools.",
        "Nje multi-agent system ka disa agjente me role te ndryshme.",
        "Shembull: nje agent planifikon, nje kerkon informacion, nje shkruan pergjigjen dhe nje e vlereson.",
        "",
        "MLflow perdoret per te ruajtur eksperimente, parametra, metrika, modele dhe rezultate vleresimi.",
        "Ne GenAI, MLflow mund te ruaje pyetje, prompts, pergjigje dhe kohen e pergjigjes.",
        "",
        "Unity Catalog perdoret per governance te te dhenave dhe aseteve AI.",
        "Governance ndihmon ne kontrollin e aksesit, pronesine e te dhenave dhe sigurine.",
        "",
        "Evaluation kontrollon nese pergjigjet jane te sakta, relevante, te sigurta dhe te bazuara ne burime.",
        "RAG evaluation kontrollon cilesine e retrieval dhe nese pergjigjja mbeshtetet ne dokumente.",
        "",
        "Security ne GenAI perfshin mbrojtjen e te dhenave, kufizimin e tools dhe mbrojtjen nga prompt injection.",
        "Prompt injection ndodh kur nje input tenton te ndryshoje rregullat e sistemit.",
        "",
        "Agent Bricks eshte qasje per ndertimin dhe optimizimin e AI agents per enterprise.",
        "Enterprise AI kerkon governance, evaluation, monitoring, siguri dhe kontroll aksesi.",
        "",
        "Ky material perdor vetem mjete falas dhe open-source.",
        "Ky material nuk perdor OpenAI API.",
    ]

    page_width = 612
    page_height = 792
    margin_left = 56
    start_y = 748
    line_height = 15
    lines_per_page = 44

    pages = [lines[index : index + lines_per_page] for index in range(0, len(lines), lines_per_page)]
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        None,
    ]
    page_object_numbers = []

    for page_lines in pages:
        page_number = len(objects) + 1
        font_number = page_number + 1
        content_number = page_number + 2
        page_object_numbers.append(page_number)

        text_commands = ["BT", "/F1 11 Tf", f"{margin_left} {start_y} Td", f"{line_height} TL"]
        for line in page_lines:
            text_commands.append(f"({escape_pdf_text(line)}) Tj")
            text_commands.append("T*")
        text_commands.append("ET")
        stream = "\n".join(text_commands).encode("latin-1")

        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_width} {page_height}] "
            f"/Resources << /Font << /F1 {font_number} 0 R >> >> /Contents {content_number} 0 R >>".encode("ascii")
        )
        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        objects.append(
            b"<< /Length "
            + str(len(stream)).encode("ascii")
            + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        )

    kids = " ".join(f"{number} 0 R" for number in page_object_numbers)
    objects[1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_object_numbers)} >>".encode("ascii")

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
    create_pdf(Path(PDF_NAME))
    print(f"Created {PDF_NAME}")
