# 🌾 Farmer Scheme Assistant (AI Govt. Scheme Chatbot)

A modern AI-powered web app that helps Indian farmers discover relevant **government schemes** (central + state-ready design) using natural language queries — with **official source links**, **voice typing**, and **read aloud** support.

---

## ✅ Key Features

### 🤖 AI Scheme Search (ChatGPT-like)
- Farmers can type normal messages like:
  - “I want to buy a tractor, is there any subsidy or loan scheme?”
  - “My crop got damaged due to rainfall, which insurance scheme can help?”
- The system understands the user’s intent and returns **relevant schemes** with explanation.

### 📌 Official Sources
- Every scheme is returned with an **official link**
- Output also provides short summary, eligibility, and benefits

### 🔎 Smart Matching (Future-Proof)
- Uses a **unified scheme knowledge base** (`schemes_clean.jsonl`)
- Uses **FAISS + embeddings** for fast semantic search
- Uses **multi-intent reranking** so results are not random or generic

### 🎙️ Voice + Accessibility
- ✅ Voice typing (English + Hindi)
- ✅ Read aloud (Text-to-Speech)

### 📱 Responsive UI
- Works on mobile, tablet, and desktop devices

---

## DEMO Link
``` bash

https://farmer-scheme-assistant-frontend.vercel.app/

```

---

## 🧠 Tech Stack

### Backend
- **FastAPI**
- **Groq LLM API** (Llama model)
- **FAISS** (vector search)
- **SentenceTransformers** (embeddings)

### Frontend
- **Next.js (App Router)**
- **TailwindCSS**
- **Web Speech API** (Speech-to-text + Text-to-speech)

---

## ⚙️ Project Architecture (High Level)

1. **Intent Understanding**
   - Extract user intent and search reasoning from the message

2. **Scheme Retrieval (RAG-style)**
   - Search in local scheme index (`FAISS index`)
   - Multi-intent reranking to ensure relevant schemes

3. **Final Response Generation**
   - Produces ChatGPT-style answer (`final_answer`)
   - Provides scheme cards + official sources

---

## ✅ API Endpoints

### `POST /analyze`
Returns structured scheme matching result.

**Request**
```json
{
  "message": "I want to buy a tractor"
}
