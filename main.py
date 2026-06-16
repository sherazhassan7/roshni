import json
import logging
import os
import re
import time
from pathlib import Path


from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = Path("system_prompt.md").read_text(encoding="utf-8")

EXPECTED_TOP = {"message_type", "safety_status", "urdu", "roman_urdu", "english"}
EXPECTED_LANG = {"summary", "applies_to_you", "what_to_do", "deadline",
                 "safety_reason", "official_source", "note", "spoken_version"}


class ExplainRequest(BaseModel):
    message: str


class SpeakRequest(BaseModel):
    text: str
    lang: str = "urdu"


@app.post("/explain")
async def explain(req: ExplainRequest):
    t0 = time.monotonic()
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": req.message},
            ],
            response_format={"type": "json_object"},
            timeout=20.0,
        )
        raw = response.choices[0].message.content
        log.info("/explain OK — %.1fs, %d chars", time.monotonic() - t0, len(raw))
    except Exception as e:
        log.error("/explain FAILED — %.1fs: %s", time.monotonic() - t0, e)
        raise HTTPException(status_code=502, detail=f"OpenAI error: {e}")

    log.info("Raw model response:\n%s", raw)

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        log.error("Model returned invalid JSON: %s", raw)
        raise HTTPException(status_code=502, detail="Model returned invalid JSON")

    missing_top = EXPECTED_TOP - result.keys()
    if missing_top:
        log.warning("STRUCTURE MISMATCH — missing top-level keys: %s", sorted(missing_top))
        log.warning("Top-level keys actually present: %s", sorted(result.keys()))
    else:
        for lang in ("urdu", "roman_urdu", "english"):
            block = result.get(lang, {})
            if not isinstance(block, dict):
                log.warning("'%s' is not a dict — got: %r", lang, block)
                continue
            missing = EXPECTED_LANG - block.keys()
            if missing:
                log.warning("'%s' block missing keys: %s", lang, sorted(missing))

    return result


_ONES = [
    '', 'ایک', 'دو', 'تین', 'چار', 'پانچ', 'چھ', 'سات', 'آٹھ', 'نو',
    'دس', 'گیارہ', 'بارہ', 'تیرہ', 'چودہ', 'پندرہ', 'سولہ', 'سترہ', 'اٹھارہ', 'انیس',
]
_TENS = ['', '', 'بیس', 'تیس', 'چالیس', 'پچاس', 'ساٹھ', 'ستر', 'اسی', 'نوے']
_COMPOUND = {
    21:'اکیس',22:'بائیس',23:'تئیس',24:'چوبیس',25:'پچیس',26:'چھبیس',27:'ستائیس',28:'اٹھائیس',29:'انتیس',
    31:'اکتیس',32:'بتیس',33:'تینتیس',34:'چونتیس',35:'پینتیس',36:'چھتیس',37:'سینتیس',38:'اڑتیس',39:'انتالیس',
    41:'اکتالیس',42:'بیالیس',43:'تینتالیس',44:'چوالیس',45:'پینتالیس',46:'چھیالیس',47:'سینتالیس',48:'اڑتالیس',49:'انچاس',
    51:'اکیاون',52:'باون',53:'ترپن',54:'چون',55:'پچپن',56:'چھپن',57:'ستاون',58:'اٹھاون',59:'انسٹھ',
    61:'اکسٹھ',62:'باسٹھ',63:'تریسٹھ',64:'چونسٹھ',65:'پینسٹھ',66:'چھیاسٹھ',67:'سڑسٹھ',68:'اڑسٹھ',69:'انہٹھ',
    71:'اکہتر',72:'بہتر',73:'تہتر',74:'چوہتر',75:'پچہتر',76:'چھہتر',77:'ستہتر',78:'اٹھہتر',79:'انہتر',
    81:'اکیاسی',82:'بیاسی',83:'تراسی',84:'چوراسی',85:'پچاسی',86:'چھیاسی',87:'ستاسی',88:'اٹھاسی',89:'نواسی',
    91:'اکانوے',92:'بانوے',93:'ترانوے',94:'چورانوے',95:'پچانوے',96:'چھیانوے',97:'ستانوے',98:'اٹھانوے',99:'ننانوے',
}

def _urdu_words(n: int) -> str:
    if n == 0:
        return 'صفر'
    if n < 20:
        return _ONES[n]
    if n < 100:
        return _COMPOUND.get(n, _TENS[n // 10])
    if n < 1000:
        h, r = divmod(n, 100)
        head = ('' if h == 1 else _ONES[h] + ' ') + 'سو'
        return head if r == 0 else head + ' ' + _urdu_words(r)
    if n < 100_000:
        t, r = divmod(n, 1000)
        head = _urdu_words(t) + ' ہزار'
        return head if r == 0 else head + ' ' + _urdu_words(r)
    if n < 10_000_000:
        l, r = divmod(n, 100_000)
        head = _urdu_words(l) + ' لاکھ'
        return head if r == 0 else head + ' ' + _urdu_words(r)
    c, r = divmod(n, 10_000_000)
    head = _urdu_words(c) + ' کروڑ'
    return head if r == 0 else head + ' ' + _urdu_words(r)


def _preprocess_tts(text: str, lang: str) -> str:
    # Always space out the helpline code so it reads digit-by-digit
    text = re.sub(r'(?<!\d)8171(?!\d)', '8 1 7 1', text)
    if lang == "urdu":
        # Convert remaining standalone numbers to Urdu words
        text = re.sub(r'(?<!\d)\d+(?!\d)', lambda m: _urdu_words(int(m.group())), text)
        # Backup: اِن/اُن at sentence start gets mispronounced as English "in".
        # Insert a zero-width non-joiner after it so the TTS sees Urdu context.
        text = re.sub(r'(?m)(^|[۔؟!.?]\s*)(اِن|اُن|ان)(\s)', r'\1\2‌\3', text)
    # For roman_urdu / english, leave digits as-is — the TTS reads them naturally
    return text


@app.post("/speak")
async def speak(req: SpeakRequest):
    text = _preprocess_tts(req.text, req.lang)
    t0 = time.monotonic()
    # Try primary model; fall back to tts-1 once if it errors (e.g. quota/availability).
    # This is two calls only on primary failure, not a blind retry loop.
    for model in ("gpt-4o-mini-tts", "tts-1"):
        try:
            tts = client.audio.speech.create(
                model=model,
                voice="nova",
                input=text,
                timeout=20.0,
            )
            log.info("/speak OK — model=%s, %.1fs, %d bytes",
                     model, time.monotonic() - t0, len(tts.content))
            return Response(content=tts.content, media_type="audio/mpeg")
        except Exception as e:
            log.warning("/speak FAILED — model=%s, %.1fs: %s", model, time.monotonic() - t0, e)
    raise HTTPException(status_code=502, detail="TTS unavailable — both models failed")


app.mount("/", StaticFiles(directory="static", html=True), name="static")
