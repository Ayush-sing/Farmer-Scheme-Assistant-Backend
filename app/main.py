from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.schemas import UserMessage
from app.intent.intent_analyzer import analyze_intent
from app.schemes.scheme_service import find_schemes
from app.response.answer_generator import generate_answer


app = FastAPI(
    title="Farmer Scheme AI",
    description="AI-powered assistant to identify government schemes and link to official sources",
    version="3.0.0"
    
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
def analyze_user_message(payload: UserMessage):

    # STEP 1: Intent understanding
    intent_result = analyze_intent(payload.message)

    # STEP 2: Build search query (best field)
    query = intent_result.get("search_reasoning") or intent_result.get("intent_summary")

    if not query:
        return {
            "status": "error",
            "message": "Could not generate search query from intent.",
            "analysis": intent_result
        }

    # STEP 3: Search schemes from local index
    schemes = find_schemes(query, user_message=payload.message, max_results=2)

    # STEP 4: Return response
    if not schemes:
        return {
            "status": "no_scheme_found",
            "analysis": intent_result,
            "message": "No matching schemes found in the local scheme knowledge base yet."
        }

    return {
        "status": "success",
        "analysis": intent_result,
        "schemes_found": schemes
    }

@app.post("/chat")
def chat(payload: UserMessage):


    intent_result = analyze_intent(payload.message)

    query = intent_result.get("search_reasoning") or intent_result.get("intent_summary")
    if not query:
        return {
            "status": "error",
            "message": "Could not generate search query from intent.",
            "analysis": intent_result
        }

    schemes = find_schemes(query, user_message=payload.message, max_results=2)

    if not schemes:
        return {
            "status": "no_scheme_found",
            "analysis": intent_result,
            "message": "I couldn’t find a matching scheme in the local knowledge base yet."
        }

    final_answer = generate_answer(
        user_message=payload.message,
        analysis=intent_result,
        schemes_found=schemes
    )

    return {
        "status": "success",
        "analysis": intent_result,
        "schemes_found": schemes,
        "final_answer": final_answer
    }
