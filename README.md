# Roshni (روشنی)

Roshni turns confusing BISP and government benefit messages into plain language. Paste a message, and it explains what it says in simple Urdu, Roman Urdu or English, reads the explanation aloud, and tells you whether the message looks safe, needs caution, or is likely a scam.

I built it for low-literacy users, especially mothers who receive BISP Benazir Taleemi Wazaif (education stipend) messages they can't easily read or verify. Scam messages imitating BISP are common, and the people they target are often the least able to check them.

## What it does

- Explains any pasted BISP, benefit or school-stipend message: what it says, who it's for, what to do, and any deadline
- Shows the explanation in Urdu, Roman Urdu or English, switchable on the result screen
- Reads the explanation aloud
- Gives a clear verdict (**safe**, **caution** or **likely scam**) with the reason behind it
- Points users to BISP's official 8171 service to verify a message
- Mobile-first, right-to-left Urdu interface, with bilingual labels for non-Urdu readers

## How it works

A FastAPI backend sends the message to GPT-4o with a system prompt (`system_prompt.md`) that classifies it and returns a structured explanation in all three languages. A second endpoint turns the explanation into speech with OpenAI's `gpt-4o-mini-tts`, falling back to `tts-1`. Before the text is spoken, Urdu numbers are converted into words and the 8171 helpline is read out digit by digit, so it's easy to follow. The frontend is a single HTML page in plain JavaScript, with no build step.

Roshni explains messages. It doesn't decide who qualifies for BISP support; only BISP does.

Messages you paste are sent to OpenAI's API to generate the explanation and the audio.

## Run it locally

```bash
git clone https://github.com/sherazhassan7/roshni.git
cd roshni
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then add your OpenAI API key to .env
uvicorn main:app --reload
```

Open [http://localhost:8000](http://localhost:8000). `test_messages.json` has sample messages to try.

## Project structure

```
main.py              FastAPI backend: /explain and /speak endpoints
system_prompt.md     System prompt sent to GPT-4o to classify and explain messages
static/index.html    Single-page frontend (plain JavaScript, no build step)
requirements.txt     Python dependencies
.env.example         Template for your API key (copy to .env, which is not committed)
test_messages.json   Sample messages for manual testing
```

## API

### POST /explain

Classifies and explains a message, returning structured JSON in all three languages.

**Request**

```json
{ "message": "BISP: آپ کے بچوں کے لیے تعلیمی وظائف منظور ہو گئے ہیں۔" }
```

**Response**

```json
{
  "message_type": "official",
  "safety_status": "safe",
  "urdu": {
    "summary": "یہ بی آئی ایس پی کا میسج ہے۔ آپ کے بچوں کے وظائف منظور ہو گئے ہیں۔",
    "applies_to_you": "یہ ان ماؤں کے لیے ہے جن کے بچے سکول میں پڑھتے ہیں۔",
    "what_to_do": ["8171 پر اپنا شناختی کارڈ نمبر بھیج کر تصدیق کریں۔"],
    "deadline": "",
    "safety_reason": "",
    "official_source": "8171 پر اپنا 13 ہندسے کا شناختی کارڈ نمبر بھیجیں۔",
    "note": "وظیفہ ملنا بی آئی ایس پی طے کرتی ہے، یہ ایپ نہیں۔",
    "spoken_version": "یہ بی آئی ایس پی کا میسج ہے۔ ..."
  },
  "roman_urdu": { "...same eight fields in Roman Urdu...": "" },
  "english":    { "...same eight fields in English...": "" }
}
```

**Top-level fields**

| Field | Values |
|---|---|
| `message_type` | `official` · `scam` · `unrelated` · `unclear` |
| `safety_status` | `safe` · `caution` · `likely_scam` |

**Fields in each language block** (`urdu`, `roman_urdu`, `english`)

| Field | What it holds |
|---|---|
| `summary` | One or two plain sentences describing the message |
| `applies_to_you` | Who the message is for |
| `what_to_do` | Concrete steps, or `[]` if there's nothing to do |
| `deadline` | Any date or time limit stated in the message, or `""` |
| `safety_reason` | Why this safety verdict was given |
| `official_source` | How to verify (usually: send your CNIC number to 8171) |
| `note` | Eligibility reminder: only BISP decides who qualifies |
| `spoken_version` | A natural paragraph written for text-to-speech |

Fields that don't apply to a given `message_type` come back as empty strings or arrays and aren't shown in the interface.

### POST /speak

Converts text to speech and returns MP3 audio. The frontend calls it internally.

**Request**

```json
{ "text": "یہ میسج محفوظ ہے۔", "lang": "urdu" }
```

`lang` is one of `urdu`, `roman_urdu` or `english`. Urdu text gets number-to-words conversion before synthesis, and 8171 is spaced out so it's read digit by digit.

**Response:** `audio/mpeg`

**Models:** `gpt-4o-mini-tts` (primary), with `tts-1` as a fallback. Voice: nova.
