# CampGuide

A retrieval-augmented (RAG) chatbot that answers questions about
[AtomCamp](https://www.atomcamp.com/) — courses, events, admissions — grounded in
the organization's own website content rather than the language model's training
data. Flask backend, ChromaDB for retrieval, Groq-hosted Llama 3 for generation.

## How it works

```
website ──scrape──> scraped_data.json ──embed──> ChromaDB ──retrieve──> Llama 3 ──> answer
        web_scrape.py                  load_data()        query_vectordb()  chat_with_groq()
```

1. **Ingest** — `web_scrape.py` crawls atomcamp.com breadth-first, following only
   internal links, and writes each page's text to `scraped_data.json`.
2. **Index** — `load_data()` adds each page to a persistent ChromaDB collection,
   which handles the embedding and vector storage.
3. **Retrieve + generate** — for each question, `query_vectordb()` pulls the two
   most relevant pages and passes them as context to Llama 3 (`llama3-8b-8192`) via
   the Groq API, so answers stay grounded in AtomCamp's actual content.

The retrieval step is what keeps the bot from inventing course names or dates: the
model is asked to answer *from the provided context*, not from memory.

## Running it

```bash
pip install -r requirements.txt
export GROQ_API_KEY=your_key_here        # or put it in a .env file

python web_scrape.py                     # build scraped_data.json (one-time)
python main.py                           # serve on :8080
```

Then open `http://localhost:8080`. The chat UI posts to `GET /chat?query=...`, which
returns the model's answer as JSON.

The API key is read from the environment (`GROQ_API_KEY`); nothing is hardcoded. The
`vectordb/` directory is built on first run and is not committed — it regenerates
from `scraped_data.json`.

## Deployment

Configured for Google App Engine (`app.yaml`, `wsgi.py`, gunicorn). Set
`GROQ_API_KEY` as a runtime environment variable in the App Engine config rather
than committing it.

## Layout

| Path | What it is |
| --- | --- |
| `web_scrape.py` | BFS crawler → `scraped_data.json` |
| `main.py` | Flask app: vector indexing, retrieval, Groq inference, routes |
| `scraped_data.json` | Scraped AtomCamp page text (the knowledge base) |
| `templates/`, `static/` | Chat UI |
| `app.yaml`, `wsgi.py` | App Engine deployment |

## Limitations

- Retrieval is fixed at the top 2 pages with no re-ranking, so questions that span
  several pages can miss context.
- The knowledge base is a static snapshot; re-run the scraper to refresh it.
- No conversation memory — each question is answered independently.
