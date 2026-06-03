# AI Study Assistant

AI Study Assistant është aplikacion Streamlit për studim të materialeve rreth Generative AI. Projekti punon lokalisht: lexon një bazë njohurish GenAI, pranon PDF të ngarkuar, ndërton një indeks kërkimi dhe përdor LLM lokal me Ollama për të kthyer përgjigje të bazuara në material.

## Funksionalitetet

- Chat me materialin e studimit
- Upload PDF për tema Generative AI
- Përgjigje me burime nga materiali
- Përgjigje të formuluara nga LLM lokal falas me Ollama
- Përmbledhje automatike e PDF-së
- Gjenerim quiz-i me alternativa
- Regjistrim i operacioneve me MLflow

## Teknologjite

- Python
- Streamlit
- pypdf
- MLflow
- Ollama për LLM lokal
- RAG lokal me tokenizim, TF-IDF dhe ngjashmëri kosinus

## Struktura

- `app.py` - ndërfaqja Streamlit dhe rrjedha kryesore e aplikacionit
- `llm_client.py` - lidhja me Ollama dhe modeli lokal LLM
- `rag_engine.py` - leximi i materialeve, indeksimi dhe kërkimi i burimeve relevante
- `study_tools.py` - përmbledhja, quiz-i, detektimi i gjuhës dhe pastrimi i tekstit
- `data/genai_knowledge_base/` - baza lokale e njohurive per Generative AI
- `mlruns/` dhe `mlflow.db` - të dhënat e eksperimenteve/logimeve MLflow

## Instalimi

Krijo dhe aktivizo një virtual environment, pastaj instalo paketat:

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## LLM lokal pa pagesë

Projekti përdor Ollama si zgjidhje falas për LLM lokal. Instalimi i Ollama bëhet jashtë Python-it, pastaj modeli shkarkohet në kompjuter.

Instalo Ollama nga:

```text
https://ollama.com
```

Pastaj shkarko modelin e rekomanduar:

```powershell
ollama pull llama3.2:3b
```

Sigurohu që Ollama është aktiv. Zakonisht API lokale punon në:

```text
http://localhost:11434
```

Modeli default në projekt është:

```text
llama3.2:3b
```

Mund ta ndryshosh me environment variable:

```powershell
$env:OLLAMA_MODEL="qwen2.5:3b"
```

Nëse Ollama nuk është aktiv, aplikacioni nuk ndalet. Ai përdor fallback-un lokal me rregulla, kështu që chat-i vazhdon të punojë.

## Ekzekutimi

```powershell
streamlit run app.py
```

Pastaj hape URL-në që shfaq Streamlit, zakonisht:

```text
http://localhost:8501
```

## Si funksionon

Kur aplikacioni hapet, ai ndërton indeksin nga `data/genai_knowledge_base`. Nëse përdoruesi ngarkon PDF, teksti i PDF-së lexohet me `pypdf`, kontrollohet nëse lidhet me GenAI dhe shtohet në indeks. Kur përdoruesi bën pyetje, sistemi kërkon chunks relevante dhe ia dërgon ato LLM-së lokale në Ollama. LLM-ja përdor materialin kur është relevant, por për pyetje të përgjithshme rreth Generative AI mund të përdorë edhe njohurinë e përgjithshme të modelit për të kthyer përgjigje më të plotë. Për quiz dhe përmbledhje përdoren rregulla lokale mbi tekstin.

## Kufizime

- Projekti kërkon Ollama për përgjigje me LLM lokal.
- Nuk përdor API me pagesë ose cloud LLM.
- Cilësia e përgjigjeve varet nga modeli lokal dhe nga materiali në knowledge base ose PDF.
- PDF-të pa tekst të ekstraktueshëm nuk mund të përpunohen mirë.

## Përshkrim i shkurtër për prezantim

Ky projekt është një AI Study Assistant për Generative AI. Ai përdor Streamlit për ndërfaqen, lexon PDF dhe materiale lokale, ndërton një indeks RAG lokal dhe përdor një LLM lokal falas me Ollama për të formuluar përgjigje nga materiali i studimit.
