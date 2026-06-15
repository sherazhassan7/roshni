# Roshni (روشنی)

Roshni explains confusing official messages in simple Urdu, reads them aloud, and warns when a message looks like a scam. It is built for people who receive government and benefit messages they cannot easily read or trust, with a focus on Pakistan's Benazir Income Support Programme (BISP), the Benazir Taleemi Wazaif education stipend, and school notices.

## The problem

Government support often does not reach the people it was built for. A family can qualify for help and still miss it, because the message that explains it is written in formal language, arrives mixed in with scams, and assumes a level of literacy many recipients do not have. A mother in a rural village can lose the stipend meant to keep her child in school simply because she cannot understand the notice that says she qualifies, or cannot tell a real notice from a fake one.

## What Roshni does

A person pastes or forwards the message they received. Roshni reads it and returns, in plain spoken Urdu (and in Roman Urdu or English if they prefer):

- what the message is, in plain words
- whether it applies to them and what matters most
- what to do, and by when if the message gives a date
- whether the message looks safe or like a scam

Every answer can be read aloud, which matters for users who cannot read well. Roshni never decides who qualifies and never invents details that are not in the message. When it is unsure, it points the user to the official 8171 service to confirm.

## How it works

Input: the message the user received (Urdu script, Roman Urdu, English, or a mix).

Processing: the message is sent to OpenAI's GPT-4o with a system prompt that explains it in simple language, classifies the type of message, and follows strict rules about never inventing information. A separate endpoint turns the explanation into speech.

Output: a structured result shown as a card, plus an audio version the user can play.

## Features

- Explanations in simple, spoken Urdu, with Roman Urdu and English views on a toggle
- Read-aloud voice for every explanation, in the selected language
- Scam detection with a clear red warning
- Context-aware output: a scam result shows a warning and what to avoid, an unrelated message is gently turned away, and only the fields that actually apply are shown
- Refuses to invent dates, amounts, or eligibility, and routes the user to the official source

## Tech stack

- Python with FastAPI
- OpenAI GPT-4o for the explanation, gpt-4o-mini-tts for the voice
- Plain HTML, CSS, and JavaScript for the frontend (mobile-first, right-to-left Urdu)
- python-dotenv for configuration

## Running locally

1. Install dependencies:

```
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Add your OpenAI API key. Create a file named `.env` in the project root:

```
OPENAI_API_KEY=your-key-here
```

3. Start the server:

```
uvicorn main:app --reload
```

4. Open http://localhost:8000 in your browser.

## API

### POST /explain

Request:

```
{ "message": "<the message text>" }
```

Response:

```
{
  "safety_status": "safe | caution | likely_scam",
  "message_type": "official | scam | unrelated | unclear",
  "urdu":       { "summary", "applies_to_you", "what_to_do", "deadline", "safety_reason", "official_source", "note", "spoken_version" },
  "roman_urdu": { same fields },
  "english":    { same fields }
}
```

`what_to_do` is a list of steps. Fields that do not apply to a given message are returned empty and are not shown.

### POST /speak

Request:

```
{ "text": "<text to read>", "lang": "urdu | roman_urdu | english" }
```

Returns MP3 audio. Numbers are prepared so each language reads them correctly, and the 8171 helpline code is read digit by digit.

## Responsible AI

- Risk: a confidently wrong simplification could make someone miss real help, dismiss a genuine notice, or trust a scam.
- Mitigation: the model may only state what is actually written in the message. For anything not stated, it says so and points the user to the official 8171 service. It never guarantees money or eligibility.
- Human in the loop: Roshni does not decide who qualifies. Eligibility is decided only by BISP. Roshni explains and guides, then sends the user to the official channel to confirm.
- Scam handling: messages that ask for an ATM or wallet PIN, ask for a fee to release money, contain suspicious links, or claim a prize are flagged as likely scams with a plain warning.

## Data

Roshni uses no real personal data. The sample messages in `test_messages.json` are synthetic, written to match the real public formats of BISP and 8171 communications, including common scam patterns.

## Project structure

```
.
├── main.py             FastAPI backend (/explain and /speak)
├── system_prompt.md    The prompt that defines how messages are explained
├── test_messages.json  Synthetic sample messages for testing
├── static/
│   └── index.html      Mobile-first, right-to-left Urdu frontend
├── requirements.txt
├── .env.example        Template showing which keys are needed. Copy it to .env and add your own key.
└── README.md
```

## Deployment

Roshni runs on any host that supports Python. For a free public deployment, connect this repository to Render, set the start command to `uvicorn main:app --host 0.0.0.0 --port $PORT`, and add `OPENAI_API_KEY` as an environment variable in the Render dashboard rather than in the code.
