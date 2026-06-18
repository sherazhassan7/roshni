# Roshni (روشنی)

Roshni explains confusing Pakistani BISP and government benefit messages in simple Urdu, Roman Urdu, or English, reads the explanation aloud via text-to-speech, and gives a plain safety verdict — safe, caution, or likely scam.

Built for low-literacy users, especially mothers who receive BISP Benazir Taleemi Wazaif (education stipend) messages they cannot easily read or verify.

---

## Features

- Paste any BISP, government benefit, or school-stipend message
- Plain-language explanation in Urdu, Roman Urdu, or English (toggle on the result)
- Explanation read aloud via text-to-speech
- Clear safety verdict: **safe** · **caution** · **likely scam**
- Accurate scam warnings — never confuses real BISP notices with fraud
- Mobile-first, right-to-left Urdu UI; bilingual labels for non-Urdu readers

---

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-...
```

Start the server:

```bash
uvicorn main:app --reload
```

Open [http://localhost:8000](http://localhost:8000).

---

## Project structure

```
main.py              FastAPI backend — /explain and /speak endpoints
system_prompt.md     System prompt sent to gpt-4o for message classification
static/index.html    Single-page frontend (vanilla JS, no build step)
requirements.txt     Python dependencies
.env                 API key — not committed
test_messages.json   Sample messages for manual testing
README.md
```

---

## API

### POST /explain

Classifies and explains a message. Returns structured JSON in all three languages.

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
  "roman_urdu": { "...same eight fields in Roman Urdu..." },
  "english":    { "...same eight fields in English..." }
}
```

**Top-level fields**

| Field | Values |
|---|---|
| `message_type` | `official` · `scam` · `unrelated` · `unclear` |
| `safety_status` | `safe` · `caution` · `likely_scam` |

**Per-language fields** (same structure for `urdu`, `roman_urdu`, `english`)

| Field | Notes |
|---|---|
| `summary` | One or two plain sentences describing the message |
| `applies_to_you` | Who this message is for |
| `what_to_do` | Array of concrete steps; `[]` if nothing to do |
| `deadline` | Date or time limit stated in the message, or `""` |
| `safety_reason` | Why this safety verdict was assigned |
| `official_source` | How to verify (typically: send CNIC to 8171) |
| `note` | Eligibility reminder — only BISP decides who qualifies |
| `spoken_version` | Natural flowing paragraph for TTS playback |

Fields that do not apply to a given `message_type` are returned as empty strings or empty arrays and are not shown in the UI.

### POST /speak

Converts text to speech and returns MP3 audio. Called internally by the frontend.

**Request**

```json
{ "text": "یہ میسج محفوظ ہے۔", "lang": "urdu" }
```

`lang` is one of `urdu` · `roman_urdu` · `english`. Urdu text gets Urdu number-to-words conversion and helpline spacing (8171 → digit-by-digit) before synthesis.

**Response:** `audio/mpeg` binary.

**Models:** `gpt-4o-mini-tts` (primary), falls back to `tts-1`. Voice: nova.
