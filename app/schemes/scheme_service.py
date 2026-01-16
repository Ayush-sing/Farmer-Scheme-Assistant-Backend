import re
from app.schemes.retriever import SchemeRetriever

retriever = SchemeRetriever(
    index_path="data/schemes.index",
    docs_path="data/schemes_docs.json"
)

def _keywords_from_text(text: str) -> set:
    """
    Extract user-important keywords dynamically (no scheme hardcoding).
    """
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    words = [w for w in text.split() if len(w) >= 3]

    stop = {
        "government","scheme","schemes","support","help","need","want","provide",
        "farm","farmer","farming","purchase","buy","from","also","know","there",
        "tell","me","any","can","please","able","some","sometimes"
    }
    return set([w for w in words if w not in stop])

def _doc_text(doc: dict) -> str:
    return " ".join([
        doc.get("scheme_name",""),
        doc.get("summary",""),
        doc.get("eligibility",""),
        doc.get("benefits",""),
        " ".join(doc.get("tags", []) or [])
    ]).lower()

def _make_facets(user_message: str, search_reasoning: str) -> list:
    """
    Make multiple 'facets' (mini-queries) from the user's message.
    This is NOT hardcoding categories. It uses the user's own words.
    """
    base = (user_message or "") + " " + (search_reasoning or "")
    base = base.lower()

    # Split on common multi-intent separators
    parts = re.split(r"\b(and|also|but|plus|along with|,|\.|\n)\b", base)
    parts = [p.strip() for p in parts if p.strip() and p not in {"and","also","but","plus",",",".","\n","along with"}]

    facets = []
    for p in parts:
        kw = _keywords_from_text(p)
        if len(kw) >= 2:
            facets.append({"text": p, "keywords": kw})

    # Always add one global facet (full query)
    facets.insert(0, {"text": base, "keywords": _keywords_from_text(base)})

    # Deduplicate facets by keyword signature
    seen = set()
    uniq = []
    for f in facets:
        sig = tuple(sorted(list(f["keywords"]))[:10])
        if sig in seen:
            continue
        seen.add(sig)
        uniq.append(f)

    return uniq[:5]  # keep it small + fast

def find_schemes(search_reasoning: str, user_message: str = "", max_results: int = 2):
    """
    FINAL retrieval (multi-intent, future-proof):
    1) semantic candidates
    2) rerank by keyword overlap (user words)
    3) select best schemes across multiple facets (risk + equipment + finance etc.)
    """

    # 1) Get a wider semantic pool (we'll filter later)
    candidates = retriever.search(
        query=search_reasoning,
        top_k=70,
        max_results=20,
        max_distance=1.30
    )
    if not candidates:
        return []

    # Build facets from user message (multi-intent handling)
    facets = _make_facets(user_message, search_reasoning)

    # Precompute doc text
    doc_texts = [(doc, _doc_text(doc)) for doc in candidates]

    # 2) Pick top scheme per facet (balanced selection)
    chosen = []
    chosen_names = set()

    for facet in facets:
        best = None
        best_score = -10**9

        for doc, text in doc_texts:
            name = doc.get("scheme_name", "")
            if not name or name in chosen_names:
                continue

            overlap = sum(1 for k in facet["keywords"] if k in text)

            # If facet has no overlap, ignore this doc for this facet
            if overlap == 0:
                continue

            dist = float(doc.get("score_distance", 999))
            score = (overlap * 10) - dist

            if score > best_score:
                best_score = score
                best = doc

        if best:
            chosen.append(best)
            chosen_names.add(best.get("scheme_name", ""))

        if len(chosen) >= max_results:
            break

    # 3) Fallback: if facet selection gave too few, fill from global rerank
    if len(chosen) < max_results:
        global_kw = _keywords_from_text(user_message + " " + search_reasoning)

        scored = []
        for doc, text in doc_texts:
            name = doc.get("scheme_name", "")
            if not name or name in chosen_names:
                continue

            overlap = sum(1 for k in global_kw if k in text)
            if overlap == 0:
                continue

            dist = float(doc.get("score_distance", 999))
            score = (overlap * 10) - dist
            scored.append((score, doc))

        scored.sort(reverse=True, key=lambda x: x[0])

        for _, doc in scored:
            chosen.append(doc)
            chosen_names.add(doc.get("scheme_name", ""))
            if len(chosen) >= max_results:
                break

    return chosen
