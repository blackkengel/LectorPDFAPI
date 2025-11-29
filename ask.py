from fastapi import APIRouter, Form
import os
import requests
from utils.extract_pdf import extract_text_from_pdf
from utils.chunks import chunk_text
from utils.rag import EmbeddingsClient
from utils.vector import VectorIndex

router = APIRouter()
UPLOAD_DIR = os.path.join(os.getcwd(), "public", "pdf")

embedder = EmbeddingsClient(model="text-embedding-3-small")
index = VectorIndex()
pdf_indices = {}

def download_pdf_from_url(url: str) -> str:
    """Descarga un PDF desde una URL y lo guarda en UPLOAD_DIR."""
    filename = url.split("/")[-1].split("?")[0]
    filepath = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(filepath):
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("No se pudo descargar el PDF desde la URL")

        with open(filepath, "wb") as f:
            f.write(response.content)

    return filename


@router.post("/ask")
async def ask(question: str = Form(...), pdf_name: str = Form(...)):

    if pdf_name.startswith("http://") or pdf_name.startswith("https://"):
        try:
            pdf_name = download_pdf_from_url(pdf_name)
        except Exception as e:
            return {"error": f"Error descargando PDF: {str(e)}"}

    pdf_path = os.path.join(UPLOAD_DIR, pdf_name)

    if not os.path.exists(pdf_path):
        return {"error": "PDF no encontrado"}
    
    if pdf_name not in pdf_indices:
        text = extract_text_from_pdf(pdf_path)
        chunks = chunk_text(text)
        embeddings = embedder.embed(chunks)

        idx = VectorIndex()
        idx.add(embeddings, chunks)
        pdf_indices[pdf_name] = idx
    else:
        idx = pdf_indices[pdf_name]

    q_vec = embedder.embed([question])
    context_results = idx.search(q_vec, k=5)

    context = "\n\n".join([
        "[score={:.4f}] {}".format(r['score'], r['doc'])
        for r in context_results
    ])

    try:
        response = embedder.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Usa el contexto que te estoy otorgando para responder; no inventes."
                },
                {
                    "role": "user",
                    "content": f"Pregunta: {question}\n\nContexto:\n{context}"
                }
            ]
        )
        answer = response.choices[0].message.content
    except Exception as e:
        return {"error": f"Error al generar respuesta: {str(e)}"}

    return {
        "question": question,
        "answer": answer
    }