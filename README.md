# نوٹس سمجھیں — Hackathon Build

Helps Pakistani citizens understand government notices, utility bills, and official letters in plain Urdu.

## Setup

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Add your OpenAI key

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-...
```

### 3. Run the server

```bash
uvicorn main:app --reload
```

### 4. Open the app

Visit [http://localhost:8000](http://localhost:8000) in your browser.

## Project structure

```
.
├── main.py            # FastAPI backend
├── system_prompt.md   # Prompt sent to gpt-4o
├── static/
│   └── index.html     # Mobile-first RTL Urdu frontend
├── requirements.txt
├── .env               # Not committed — add your key here
└── README.md
```

## API

`POST /explain`

Request body:
```json
{ "message": "<text of the notice>" }
```

Response:
```json
{
  "summary": "...",
  "applies_to_you": "...",
  "what_to_do": ["...", "..."],
  "deadline": "...",
  "safety": { "status": "safe|warning|danger", "reason": "..." },
  "official_source": "...",
  "note": "...",
  "spoken_version": "..."
}
```
