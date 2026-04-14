from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2

app = FastAPI()

# ✅ CORS FIX (IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store uploaded notes globally
notes_data = ""


# -------------------------
# 📁 FILE UPLOAD ENDPOINT
# -------------------------
@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    global notes_data

    if file.filename.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(file.file)
        text = ""

        for page in pdf_reader.pages:
            if page.extract_text():
                text += page.extract_text()

        notes_data = text

    elif file.filename.endswith(".txt"):
        notes_data = file.file.read().decode("utf-8")

    else:
        return {"message": "Only PDF and TXT files are supported"}

    return {"message": "File uploaded successfully"}


# -------------------------
# 🤖 CHAT REQUEST MODEL
# -------------------------
class Query(BaseModel):
    question: str


# -------------------------
# 💬 CHAT ENDPOINT
# -------------------------
@app.post("/chat")
def chat(query: Query):
    global notes_data
    q = query.question.lower()

    if not notes_data:
        return {"answer": "Please upload notes first."}

    notes_lower = notes_data.lower()

    # ✅ Step 1: direct keyword match
    if q in notes_lower:
        return {
            "answer": "Found exact match in notes:\n\n" + notes_data[:800]
        }

    # ✅ Step 2: smart word scoring (IMPORTANT)
    words = q.split()
    best_lines = []
    best_score = 0

    for line in notes_data.split("\n"):
        line_lower = line.lower()
        score = sum(1 for word in words if word in line_lower)

        if score > best_score:
            best_score = score
            best_lines = [line]
        elif score == best_score and score > 0:
            best_lines.append(line)

    if best_score > 0:
        return {
            "answer": "Most relevant content from notes:\n\n" + "\n".join(best_lines)
        }

    # ✅ Step 3: fallback
    return {
        "answer": "No relevant information found in notes."
    }


# -------------------------
# 🏠 TEST ROUTE
# -------------------------
@app.get("/")
def home():
    return {"message": "EduAI Nexus Backend Running 🚀"}