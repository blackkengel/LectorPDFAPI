from fastapi import APIRouter, Form
import os
from utils.extract_pdf import extract_text_from_pdf
from utils.chunks import chunk_text
from utils.rag import EmbeddingsClient
from utils.vector import VectorIndex

router = APIRouter()
UPLOAD_DIR = os.path.join(os.getcwd(), "public", "pdf")

embedder = EmbeddingsClient(model="text-embedding-3-small")
index = VectorIndex()
pdf_indices = {}

@router.post("/ask")
async def ask(question: str = Form(...), pdf_name: str = Form(...)):
    pdf_path = os.path.join(UPLOAD_DIR, pdf_name)
    if not os.path.exists(pdf_path):
        return {"error": "PDF no encontrado"}
    
    if pdf_name not in pdf_indices:
        text = extract_text_from_pdf(pdf_path)
        chunks = chunk_text(text)
        embeddings = embedder.embed(chunks)
        index = VectorIndex()
        index.add(embeddings, chunks)
        pdf_indices[pdf_name] = index
    else:
        index = pdf_indices[pdf_name]

    q_vec = embedder.embed([question])
    context_results = index.search(q_vec, k=5)

    context = "\n\n".join([f"[score={r['score']:.4f}] {r['doc']}" for r in context_results])
    # print("question:", question)
    # print("context:", context)
    try:
        response = embedder.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Usa el contexto que te estoy otorgando para responder la pregunta; no inventes, solo devuelve información relevante del contexto."
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
