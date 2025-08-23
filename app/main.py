import os
import weaviate
from fpdf import FPDF
from fastapi import FastAPI, Query
import requests

# ====== CONFIG ======
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
CLASS_NAME = "Eval"
# ====================

app = FastAPI()

# Connect to Weaviate
client = weaviate.connect_to_custom(
    http_host="weaviate",
    http_port=8080,
    http_secure=False,
    grpc_host="weaviate",
    grpc_port=50051,
    grpc_secure=False,
)

# Confirm
print(client.is_ready())

def query_weaviate(query_text):
    """Search Weaviate for relevant chunks."""
    result = (
        client.query.get(CLASS_NAME, ["filename", "content"])
        .with_near_text({"concepts": [query_text]})
        .do()
    )

    docs = []
    try:
        for item in result["data"]["Get"][CLASS_NAME]:
            docs.append(item["content"])
    except KeyError:
        pass

    return docs


def ask_ollama(prompt: str):
    """Send a prompt to Ollama and get the generated text."""
    resp = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt},
        stream=False
    )
    data = resp.json()
    return data.get("response", "")


def create_pdf(text, filename="output.pdf"):
    """Generate a PDF from the given text."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    for line in text.split("\n"):
        pdf.multi_cell(0, 8, line)
    pdf.output(filename)
    return filename


@app.get("/generate-pdf")
def generate_pdf(query: str = Query(..., description="Your query or request")):
    # Step 1: Search Weaviate
    context_docs = query_weaviate(query)

    if not context_docs:
        return {"error": "No relevant documents found."}

    # Step 2: Prepare RAG prompt
    rag_prompt = f"""You are a military supervisor and need to complete your annual evaluations on your subordinates.

Context:
{''.join(context_docs)}

Instruction:
{query}
"""

    # Step 3: Ask Ollama
    generated_text = ask_ollama(rag_prompt)

    # Step 4: Save to PDF
    output_path = "/app/generated_document.pdf"
    create_pdf(generated_text, filename=output_path)

    return {"message": "PDF generated successfully", "file_path": output_path}