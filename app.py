# pip install transformers torch gradio sentencepiece

import gradio as gr
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import re
import os
import difflib

# ─────────────────────────────────────────────
#  Model Loading
# ─────────────────────────────────────────────

# Use absolute path to avoid directory confusion on different machines
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "muril_humor_model")

tokenizer = None
model = None
model_load_error = None


def load_model():
    global tokenizer, model, model_load_error
    try:
        if not os.path.isdir(MODEL_DIR):
            model_load_error = (
                f"Model directory not found at: {MODEL_DIR}\n"
                "Please Ensure the 'muril_humor_model' folder is in the same folder as app.py."
            )
            return
        
        # Check for essential files
        required_files = ["config.json", "model.safetensors", "tokenizer.json"]
        missing = [f for f in required_files if not os.path.exists(os.path.join(MODEL_DIR, f))]
        if missing:
            model_load_error = f"Missing core model files in {MODEL_DIR}: {', '.join(missing)}"
            return

        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_DIR, local_files_only=True, use_fast=True
        )
        model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_DIR, local_files_only=True
        )
        model.eval()
        print(f"✅ Model loaded successfully from {MODEL_DIR}")
    except Exception as e:
        error_msg = str(e)
        if "NoneType" in error_msg:
            model_load_error = "Model load failed (NoneType Error). This usually means 'sentencepiece' or 'protobuf' is not installed correctly. Run: pip install --upgrade sentencepiece protobuf"
        else:
            model_load_error = f"Model load failed: {error_msg}"
        print(f"❌ {model_load_error}")


load_model()

# ─────────────────────────────────────────────
#  Heuristic Humor Scoring Engine
# ─────────────────────────────────────────────

# ── Category 1: Funny Emojis ──────────────────────────────────────────────────
FUNNY_EMOJIS = {
    "😂", "🤣", "💀", "😹", "😆", "😅", "🤪", "😝", "🤭", "🙊", "🤡",
    "😜", "😛", "🤙", "🫠", "💅", "🧢", "🫡", "😏", "😒", "🙃", "🫣",
    "😈", "👀", "💀", "⚰️", "🪦", "🫶", "😭", "🤌", "💩", "🤑", "🤫"
}

# Neutral / non-humor emojis that weakly signal seriousness
SERIOUS_EMOJIS = {"❤️", "🙏", "✅", "📌", "⚠️", "🔔", "📢", "📅", "🕐"}

# ── Category 2: English Internet Slang ────────────────────────────────────────
EN_SLANGS_SINGLE = {
    "lol", "lmao", "lmfao", "rofl", "haha", "hahaha", "hehe", "lmaoo",
    "lmaooo", "lmfaoo", "roflmao", "ded", "dead", "rip", "xd", "gg",
    "bruh", "bruhhh", "omg", "wtf", "ngl", "fr", "frfr", "lowkey",
    "highkey", "oof", "yikes", "sheesh", "bussin", "slay", "no cap",
    "cap", "sus", "simp", "ratio", "mid", "salty", "triggered", "vibe",
    "mood", "tea", "spill", "clout", "fam", "bro", "dude", "mate",
    "dawg", "brah", "blud", "mandem", "innit", "aight", "deadass",
    "tf", "smh", "facepalm", "clown", "cope", "seethe", "cringe",
    "based", "goated", "rent free", "hits different", "no thoughts",
    "understood the assignment", "its giving", "understood",
}

EN_SLANGS_MULTI = [
    "no cap", "rent free", "hits different", "no thoughts", "main character",
    "understood the assignment", "touch grass", "not my problem", "as if",
    "wait what", "hold up", "pause out", "plot twist", "plot armor",
    "skill issue", "cope harder", "not gonna lie", "for real for real",
    "goes hard", "lowkey highkey", "living rent free",
]

# ── Category 3: Telugu Slangs ─────────────────────────────────────────────────
TE_SLANGS_SINGLE = {
    "vammo", "vammoo", "vammoooo", "odiyamma", "baboi", "baboiii",
    "aiyyoo", "aiyyooo", "aiyya", "ammoo", "ammo", "emmo", "emmoo",
    "orey", "oreyy", "oreyyyy", "ra", "da", "le", "bro",
    "bokka", "bokkaley", "bokkaleyyyy", "bokkale",
    "kiraak", "kiraaak", "racha", "rachaa", "mass", "keka", "kekaa",
    "thop", "ramp", "josh", "joshh", "ulta", "seedha",
    "mawa", "mama", "machan", "nanba",
    "enti", "entii", "entoo", "em", "emandi", "emdii",
    "chala", "chalaaa", "chetta", "chettaa", "worst", "super",
    "keka", "danger", "bangaram", "pakkinti", "pakka",
    "chesav", "chesindi", "chesadu", "chesam",
    "arachakam", "mechindi", "pichha", "pichhaa",
    "ela", "enti", "antav", "antunnav", "annadu", "annaru",
    "ledu", "undu", "undi", "unte", "ante", "ayite",
    "avunu", "illa", "okka", "okate", "okatey",
    "navvaleka", "navsthe", "navvindi",
    "baaga", "chaala", "chala", "chaalaa",
    "telusa", "telusu", "telisindi", "telisi",
    "poddu", "podava", "podaava", "potav", "potaav",
    "gurram", "pedda", "chhota", "chinna",
}

TE_SLANGS_MULTI = [
    "ori nayano", "ori devuda", "entra idhi", "em baadha ra",
    "mind block", "brain freeze", "mind ki andi", "pedda problem",
    "pedda sketch", "pichha comedy", "full paisa vasool",
    "miku dannam ra", "dandam ra", "dandam pettu",
    "rod esadu", "rod ichadu", "rod kotti",
    "kinda lo pettadu", "kinda padeyyadu",
    "navvinchaadu", "entayya idi", "enti ra idi",
    "naaku ardam kadu", "naaku artham kaadu",
    "full tension", "full gas", "full josh",
    "baaga chesav", "chala chesav",
    "em chestunnav", "em antunnav",
    "cheppinchav", "cheppindi", "cheppadu",
    "oka pani cheyyav", "oka pani cheyya",
    "na life waste", "life waste chesav",
    "super ga undi", "baaga undi", "chala baagundi",
    "evaraina cheppu", "yelantivi ra", "yellantivi da",
    "light ga teesuko", "light teesuko",
    "heavy ga undi", "light ga anipinchindi",
    "nee valla kaadu", "nee valla kakunda",
    "lost in translation", "hyderabad chronicles",
]

# ── Category 4: Hyderabadi / Deccani Slang ────────────────────────────────────
HYD_SLANGS = {
    "kya baat", "kya scene", "scene set", "scene tight", "scene pakka",
    "bol bhai", "bol na", "bolo bhai", "yaar", "yaaro", "dost",
    "sahi baat", "sahi hai", "bilkul sahi", "ekdum sahi",
    "bindaas", "mast", "jhakaas", "fatafat", "jaldi",
    "kya karein", "kya karoon", "kuch nahi", "kuch bhi",
    "arrey", "arre", "arre bhai", "arrey yaar",
    "bhai sun", "bhai ek kaam", "pehle ye bata",
    "kuthe jaatav", "kha gaya", "kha liya",
    "khaali timepass", "timepass", "bakwaas",
    "lafda", "jhanjhat", "nautanki", "drama",
}

# ── Category 5: Structural / Pattern rules ────────────────────────────────────
# These are checked with regex on the *original* text

SARCASM_PATTERNS = [
    r"\bsure\b.{0,30}\bsure\b",              # "sure sure"
    r"\bha(ha){2,}\b",                        # hahaha+
    r"\boh wow\b",
    r"\btotally\b.{0,20}\bnot\b",
    r"\bnot\b.{0,20}\bproblematic\b",
    r"\bvery\b.{0,10}\b(helpful|useful|smart|genius|brilliant)\b",
    r"\bthanks.{0,15}(bro|man|yaar|ra|da)\b",
    r"\bwow\b.{0,15}(cool|great|nice|super)\b",
    r"\bso (helpful|nice|kind|smart)\b",
    r"\bgenius move\b",
    r"\bmaster plan\b",
    r"\bnailed it\b",
    r"\bjust (what|what I) (needed|wanted)\b",
    r"\bthanks for nothing\b",
]

# Contrast/irony patterns common in Tenglish humor
CONTRAST_PATTERNS = [
    r"(cheppindi|annadu|annaru|cheppadu|chepparu).{0,50}(kaadu|ledu|ayipoindi|aipoindi)",
    r"(annanu|antunnanu|antaa).{0,50}(ayindi|aipoindi|chesadu|chesindi)",
    r"\b(speed test|exam|result|mark|rank).{0,40}(actual|reality|realga|nijamga)",
    r"\b(dream|wish|hope|expect).{0,40}(reality|actual|nijam|actual ga)",
    r"\b(anukunna|expect chesina|hopesina).{0,50}(kaadu|ledu|jarugaledu)",
    r"(morning|repu|inkaa).{0,30}(meeting|exam|test|interview)",  # dread humor
    r"(plan|planning).{0,40}(fail|failed|potundi|poindi|waste)",
    r"—.{5,60}—",                             # "X — Y" setup-punchline dashes
    r"–.{5,60}–",
    r"\bexpect.{0,30}reality\b",
    r"\bhoped.{0,30}(got|received|happened)\b",
]

# Self-deprecating patterns
SELF_DEPRECATING = [
    r"\b(naa|na|my|mee|nenu).{0,30}(fail|waste|useless|zindagi|life|career|brain)\b",
    r"\b(nenu|i).{0,20}(bad|worst|useless|stupid|dumb|idiot)\b",
    r"\bnaa.{0,15}(amma|nanna|dad|mom).{0,30}(cheppindi|annadu|annari|update)\b",
    r"\b(job|career|life|zindagi).{0,20}(over|finish|end|waste|ruined)\b",
    r"\bpadipoyanu\b", r"\bpadipoindi\b", r"\blift aipoindi\b",
]

# ── Category 6: Caps / Elongation / Punctuation signals ──────────────────────
def score_stylistic(original_text: str) -> float:
    """Returns a 0.0–1.0 humor-signal score from stylistic cues."""
    score = 0.0
    # Repeated characters (loool, whyyyy, ammooo) — strong humor signal
    if re.search(r'(.)\1{2,}', original_text):
        score += 0.25
    # Excessive exclamation / question marks
    if re.search(r'[!?]{2,}', original_text):
        score += 0.2
    # ALL CAPS word (emphasis for shock/sarcasm) — at least one word fully caps 3+ chars
    caps_words = re.findall(r'\b[A-Z]{3,}\b', original_text)
    if caps_words:
        score += min(0.25, 0.1 * len(caps_words))
    # Ellipsis (dramatic pause — often sarcasm)
    if re.search(r'\.{2,}', original_text):
        score += 0.1
    # Multiple newlines in a short text (punchline formatting)
    if original_text.count('\n') >= 2 and len(original_text) < 200:
        score += 0.15
    return min(score, 0.6)

# ── Category 7: Emoticon detection ────────────────────────────────────────────
EMOTICONS = [":D", "xD", "XD", ":P", ";)", ":3", "^_^", ">_<", "o_O", "O_o",
             "T_T", ":')",":')", "B)", ";P", "^.^", "uwu", "owo", "o.o", "O.O"]

# ── Category 8: Non-humor suppression signals ─────────────────────────────────
SERIOUS_SIGNALS = [
    r"\b(died|death|funeral|accident|hospital|surgery|cancer|disease)\b",
    r"\b(police|court|arrested|legal|lawsuit|crime)\b",
    r"\b(please|plz|kindly).{0,20}(help|assist|support)\b",
    r"\b(urgent|emergency|asap|immediately|important)\b",
    r"\b(result|marks|score).{0,20}(out|released|announced)\b",
    r"dear (sir|madam|all|team)\b",
    r"\b(meeting|agenda|minutes|rescheduled|postponed)\b",
]


# ── Master Scoring Function ────────────────────────────────────────────────────

def compute_humor_score(original_text: str) -> tuple[float, list[str]]:
    """
    Returns (humor_score 0.0–1.0, list of triggered rule labels).
    Score >= 0.3  → strong heuristic humor signal (override model if needed).
    Score >= 0.15 → moderate signal (blend with model).
    Score <= -0.2 → suppression signal (text is likely serious).
    """
    text_lower = original_text.lower()
    text_orig  = original_text
    words      = set(re.findall(r"\b\w+\b", text_lower))
    score      = 0.0
    triggered  = []

    # ── 1. Funny emojis ──────────────────────────────────────────
    funny_emoji_count = sum(1 for e in FUNNY_EMOJIS if e in original_text)
    if funny_emoji_count:
        pts = min(0.4, 0.15 * funny_emoji_count)
        score += pts
        triggered.append(f"Funny emoji ×{funny_emoji_count}")

    # Serious emojis slightly penalise
    if any(e in original_text for e in SERIOUS_EMOJIS):
        score -= 0.05

    # ── 2. Emoticons ─────────────────────────────────────────────
    emote_hits = [e for e in EMOTICONS if e.lower() in text_lower]
    if emote_hits:
        score += 0.2
        triggered.append(f"Emoticon: {', '.join(emote_hits[:3])}")

    # ── 3. English internet slangs (exact) ───────────────────────
    en_hits = words & EN_SLANGS_SINGLE
    if en_hits:
        pts = min(0.35, 0.12 * len(en_hits))
        score += pts
        triggered.append(f"EN slang: {', '.join(list(en_hits)[:4])}")

    for phrase in EN_SLANGS_MULTI:
        if phrase in text_lower:
            score += 0.2
            triggered.append(f"EN phrase: '{phrase}'")

    # ── 4. Telugu slangs (exact) ─────────────────────────────────
    te_hits = words & TE_SLANGS_SINGLE
    if te_hits:
        pts = min(0.4, 0.15 * len(te_hits))
        score += pts
        triggered.append(f"TE slang: {', '.join(list(te_hits)[:4])}")

    for phrase in TE_SLANGS_MULTI:
        if phrase in text_lower:
            score += 0.25
            triggered.append(f"TE phrase: '{phrase}'")

    # ── 5. Hyderabadi slangs ─────────────────────────────────────
    hyd_hits = words & HYD_SLANGS
    if hyd_hits:
        score += min(0.3, 0.12 * len(hyd_hits))
        triggered.append(f"Hyderabadi slang: {', '.join(list(hyd_hits)[:3])}")

    # ── 6. Fuzzy matching for Telugu slangs (typos/elongation) ───
    all_single_slangs = list(TE_SLANGS_SINGLE | EN_SLANGS_SINGLE)
    fuzzy_hits = []
    for word in re.findall(r'\b\w{4,}\b', text_lower):
        if word not in all_single_slangs:
            match = difflib.get_close_matches(word, all_single_slangs, n=1, cutoff=0.82)
            if match:
                fuzzy_hits.append(f"{word}≈{match[0]}")
                score += 0.15
    if fuzzy_hits:
        triggered.append(f"Fuzzy match: {', '.join(fuzzy_hits[:3])}")

    # ── 7. Sarcasm patterns ──────────────────────────────────────
    for pat in SARCASM_PATTERNS:
        if re.search(pat, text_lower):
            score += 0.2
            triggered.append(f"Sarcasm pattern")
            break

    # ── 8. Contrast / irony / setup-punchline patterns ───────────
    contrast_count = 0
    for pat in CONTRAST_PATTERNS:
        if re.search(pat, text_lower):
            contrast_count += 1
    if contrast_count:
        pts = min(0.4, 0.2 * contrast_count)
        score += pts
        triggered.append(f"Contrast/irony ×{contrast_count}")

    # ── 9. Self-deprecating humor ────────────────────────────────
    for pat in SELF_DEPRECATING:
        if re.search(pat, text_lower):
            score += 0.2
            triggered.append("Self-deprecating")
            break

    # ── 10. Stylistic signals (caps, elongation, punctuation) ────
    style_score = score_stylistic(text_orig)
    if style_score > 0:
        score += style_score
        triggered.append(f"Stylistic cue (+{style_score:.2f})")

    # ── 11. Laughter word detection (haha, hehe variants) ────────
    if re.search(r'\bha(ha){1,}\b|\bhe(he){1,}\b|\bhi(hi){1,}\b', text_lower):
        score += 0.3
        triggered.append("Laughter word")

    # ── 12. Serious / anti-humor suppression ─────────────────────
    suppressed = False
    for pat in SERIOUS_SIGNALS:
        if re.search(pat, text_lower):
            score -= 0.35
            suppressed = True
            triggered.append("⛔ Serious context suppressor")
            break

    # ── 13. Code-mix ratio boost ─────────────────────────────────
    # If text mixes Telugu and English words, it's more likely Tenglish humor
    te_word_count = len(words & TE_SLANGS_SINGLE)
    en_word_count = len(words & EN_SLANGS_SINGLE)
    if te_word_count > 0 and en_word_count > 0:
        score += 0.15
        triggered.append("Code-mix blend")

    return round(score, 3), triggered


# ── Preprocessing + Full Predict ──────────────────────────────────────────────

def preprocess(text: str) -> str:
    t = text.lower()
    t = re.sub(r"[ \t]+", " ", t).strip()
    return t


def predict(text: str):
    if model_load_error:
        return None, None, None, None, None, model_load_error
    if not text or not text.strip():
        return None, None, None, None, None, "⚠️ Input is empty. Please type some Tenglish text."
    if len(text) > 500:
        return None, None, None, None, None, "⚠️ Input exceeds 500 characters."

    # 1. Neural model prediction
    cleaned = preprocess(text)
    inputs = tokenizer(cleaned, max_length=128, padding="max_length",
                       truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=-1)[0]

    prob_nh_model = probs[0].item()
    prob_h_model  = probs[1].item()

    # 2. Heuristic scoring
    h_score, triggered_rules = compute_humor_score(text)

    # 3. Blend: heuristic dominates when score is clear
    #    score >= 0.30  → force humorous, boost confidence
    #    0.15 <= score < 0.30 → blend 60% heuristic / 40% model
    #    -0.20 < score < 0.15 → trust model
    #    score <= -0.20 → lean non-humorous

    STRONG_THRESHOLD  = 0.30
    WEAK_THRESHOLD    = 0.15
    SUPPRESS_THRESHOLD = -0.20

    if h_score >= STRONG_THRESHOLD:
        # Heuristic is very confident → humorous
        blend_h  = min(0.97, max(0.80, 0.65 + h_score * 0.5))
        blend_nh = 1.0 - blend_h
    elif h_score >= WEAK_THRESHOLD:
        # Blend
        blend_h  = 0.6 * (0.65 + h_score) + 0.4 * prob_h_model
        blend_h  = min(0.97, blend_h)
        blend_nh = 1.0 - blend_h
    elif h_score <= SUPPRESS_THRESHOLD:
        # Suppression
        blend_nh = min(0.95, max(0.75, 0.65 + abs(h_score) * 0.5))
        blend_h  = 1.0 - blend_nh
    else:
        # Trust neural model
        blend_h  = prob_h_model
        blend_nh = prob_nh_model

    predicted_class = 1 if blend_h >= 0.5 else 0
    label_str = "HUMOROUS" if predicted_class == 1 else "NON-HUMOROUS"
    confidence_pct = (blend_h if predicted_class == 1 else blend_nh) * 100

    return label_str, confidence_pct, blend_h * 100, blend_nh * 100, triggered_rules, None


# ─────────────────────────────────────────────
#  Prediction History
# ─────────────────────────────────────────────

history: list = []


def update_history(text: str, label: str, confidence: float):
    short_text = text[:55] + "…" if len(text) > 55 else text
    label_display = "😂 Humorous" if label == "HUMOROUS" else "😐 Non-Humorous"
    history.insert(0, [short_text, label_display, f"{confidence:.1f}%"])
    if len(history) > 5:
        history.pop()
    return history[:]


# ─────────────────────────────────────────────
#  CSS — Complete Modern Rewrite
# ─────────────────────────────────────────────

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

/* ── Tokens ── */
:root {
    --bg:         #0d0d14;
    --surface:    #13131f;
    --surface-2:  #1a1a2e;
    --border:     rgba(255,255,255,0.07);
    --border-hl:  rgba(99,102,241,0.5);
    --text:       #f1f1f8;
    --muted:      #8b8baa;
    --accent:     #6366f1;
    --accent-2:   #a855f7;
    --green:      #22c55e;
    --red:        #ef4444;
    --radius-xl:  20px;
    --radius-lg:  14px;
    --radius-md:  10px;
    --shadow-lg:  0 25px 50px rgba(0,0,0,0.5);
    --shadow-glow: 0 0 40px rgba(99,102,241,0.15);
}

/* Light mode */
.light-mode {
    --bg:         #f0f0f8;
    --surface:    #ffffff;
    --surface-2:  #f5f5ff;
    --border:     rgba(0,0,0,0.08);
    --border-hl:  rgba(99,102,241,0.4);
    --text:       #111128;
    --muted:      #6b6b8a;
    --shadow-lg:  0 25px 50px rgba(0,0,0,0.08);
    --shadow-glow: 0 0 40px rgba(99,102,241,0.08);
}

/* ── Base ── */
html, body, .gradio-container {
    font-family: 'Inter', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
    transition: background 0.3s, color 0.3s;
}

/* Kill ALL Gradio chrome */
.gradio-container { max-width: 100% !important; padding: 0 !important; }
footer { display: none !important; }
.gr-prose, .prose { max-width: none !important; }

/* ── Animated background ── */
body::before {
    content: '';
    position: fixed; inset: 0; z-index: 0;
    background:
        radial-gradient(ellipse 80% 60% at 20% 10%, rgba(99,102,241,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 80% 90%, rgba(168,85,247,0.07) 0%, transparent 60%);
    pointer-events: none;
    animation: auroraPulse 12s ease-in-out infinite alternate;
}
@keyframes auroraPulse {
    0%   { opacity: 0.6; transform: scale(1); }
    100% { opacity: 1;   transform: scale(1.05); }
}

/* ── Page shell ── */
#page-shell {
    position: relative; z-index: 1;
    max-width: 1100px;
    margin: 0 auto;
    padding: 2.5rem 1.5rem 4rem;
}

/* ── Header ── */
#app-header { text-align: center; margin-bottom: 2.5rem; }

#header-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 99px;
    padding: 5px 14px;
    font-size: 0.75rem; font-weight: 600; letter-spacing: 0.1em;
    color: #a5b4fc; text-transform: uppercase;
    margin-bottom: 1.2rem;
}
#header-badge::before { content: '●'; color: #6366f1; font-size: 8px; }

#app-title {
    font-size: clamp(2.5rem, 6vw, 4.2rem);
    font-weight: 800;
    letter-spacing: -2px;
    line-height: 1.05;
    color: var(--text);
    margin-bottom: 0.7rem;
}
#app-title span.grad {
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
#app-subtitle {
    font-size: 1.05rem;
    color: var(--muted);
    font-weight: 400;
    max-width: 480px;
    margin: 0 auto 1.8rem;
    line-height: 1.6;
}

/* Stat pills row */
#stat-row {
    display: flex; justify-content: center; gap: 1rem;
    flex-wrap: wrap; margin-bottom: 0;
}
.stat-pill {
    display: flex; align-items: center; gap: 8px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 99px;
    padding: 7px 16px;
    font-size: 0.85rem; color: var(--muted);
}
.stat-pill strong { color: var(--text); font-weight: 600; }

/* ── Theme toggle ── */
#theme-toggle {
    position: fixed !important; top: 1.2rem !important; right: 1.5rem !important; z-index: 999 !important;
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 99px !important;
    padding: 8px 16px !important;
    cursor: pointer !important; color: var(--muted) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important; font-weight: 500 !important;
    transition: all 0.2s !important;
    width: auto !important; min-width: 140px !important;
    display: inline-flex !important; justify-content: center !important;
    box-shadow: var(--shadow-glow) !important;
}
#theme-toggle:hover { border-color: var(--border-hl) !important; color: var(--text) !important; }

/* ── Cards ── */
.card {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-xl) !important;
    padding: 1.6rem !important;
    box-shadow: var(--shadow-lg) !important;
    transition: border-color 0.25s, box-shadow 0.25s;
    margin-bottom: 1.2rem;
}
.card:hover {
    border-color: var(--border-hl) !important;
    box-shadow: var(--shadow-lg), var(--shadow-glow) !important;
}

/* ── Section labels ── */
.section-label {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    margin-bottom: 0.8rem !important;
    display: flex; align-items: center; gap: 8px;
}
.section-label::after {
    content: ''; flex: 1; height: 1px;
    background: var(--border);
}

/* ── Textbox ── */
#input-box textarea {
    background: var(--surface-2) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
    line-height: 1.6 !important;
    padding: 1rem 1.1rem !important;
    transition: border-color 0.25s, box-shadow 0.25s;
    resize: vertical !important;
    min-height: 130px !important;
}
#input-box textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.2) !important;
    outline: none !important;
}
#input-box textarea::placeholder { color: var(--muted) !important; }

/* ── Detect button ── */
#detect-btn {
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
    border: none !important;
    border-radius: var(--radius-lg) !important;
    color: #fff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
    padding: 0.85rem !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: opacity 0.2s, transform 0.15s, box-shadow 0.25s !important;
    box-shadow: 0 8px 24px rgba(99,102,241,0.35) !important;
    margin-top: 0.8rem !important;
}
#detect-btn:hover {
    opacity: 0.92 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 32px rgba(99,102,241,0.5) !important;
}
#detect-btn:active { transform: translateY(0) !important; }

/* ── Example chips ── */
#example-dataset {
    border: none !important;
    background: transparent !important;
    margin-top: 0.3rem !important;
}
#example-dataset .output-class, #example-dataset .gallery { border: none !important; }

#example-dataset button, #example-dataset .table-cell {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    padding: 0.4rem 0.8rem !important;
    text-align: left !important;
    transition: all 0.2s !important;
    cursor: pointer !important;
    width: 100% !important;
    display: block !important;
    margin-bottom: 0.2rem !important;
    line-height: 1.5 !important;
}
#example-dataset button:hover {
    background: rgba(99,102,241,0.1) !important;
    border-color: var(--accent) !important;
    transform: translateX(4px) !important;
}

/* ── Result card ── */
#result-zone { background: transparent !important; border: none !important; }

/* ── History table ── */
#hist-table table {
    width: 100% !important; border-collapse: collapse !important;
    font-size: 0.875rem !important;
}
#hist-table th {
    color: var(--muted) !important;
    font-size: 0.72rem !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: 0.1em !important;
    border-bottom: 1px solid var(--border) !important;
    padding: 0.6rem 0.8rem !important; text-align: left !important;
    background: transparent !important;
}
#hist-table td {
    color: var(--text) !important;
    padding: 0.65rem 0.8rem !important;
    border-bottom: 1px solid var(--border) !important;
    background: transparent !important;
    transition: background 0.15s;
}
#hist-table tr:hover td { background: rgba(99,102,241,0.05) !important; }

/* ── Footer ── */
#app-footer {
    text-align: center; margin-top: 3rem;
    font-size: 0.78rem; color: var(--muted);
    letter-spacing: 0.05em;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

/* ── Accordion ── */
.info-accordion {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    background: var(--surface) !important;
    margin-top: 0.5rem;
}
.info-accordion .label-wrap { color: var(--muted) !important; font-size: 0.85rem !important; }
"""

# ─────────────────────────────────────────────
#  HTML Builders
# ─────────────────────────────────────────────



HEADER_HTML = """
<div id="app-header">
  <div id="header-badge">MuRIL · Tenglish NLP · v2.0</div>
  <h1 id="app-title">Detect Humour in<br><span class="grad">Tenglish Text</span></h1>
  <p id="app-subtitle">Type code-mixed Telugu-English and the AI will tell you if it's funny.</p>
  <div id="stat-row">
    <div class="stat-pill">🧠 <strong>MuRIL</strong>&nbsp;Base Model</div>
    <div class="stat-pill">✅ <strong>Fuzzy</strong>&nbsp;Slang Matching</div>
    <div class="stat-pill">🔥 <strong>Emoji</strong>&nbsp;Aware</div>
  </div>
</div>
"""


def build_result_html(label: str, confidence: float, prob_h: float, prob_nh: float, triggered_rules: list) -> str:
    is_h = label == "HUMOROUS"
    icon = "😂" if is_h else "😐"
    text = "Humorous" if is_h else "Non-Humorous"
    accent_color = "#22c55e" if is_h else "#a855f7"
    fill_bar = (
        "linear-gradient(90deg,#6366f1,#22c55e)" if is_h
        else "linear-gradient(90deg,#a855f7,#ec4899)"
    )

    if confidence >= 80:
        conf_label = "High Confidence"
        conf_color = "#22c55e"
    elif confidence >= 60:
        conf_label = "Moderate"
        conf_color = "#f59e0b"
    else:
        conf_label = "Low Confidence"
        conf_color = "#ef4444"

    # Build triggered rules chips
    rules_html = ""
    if triggered_rules:
        chips = ""
        for rule in triggered_rules:
            is_bad = rule.startswith("⛔")
            chip_bg   = "rgba(239,68,68,0.12)"  if is_bad else "rgba(99,102,241,0.12)"
            chip_bord = "rgba(239,68,68,0.3)"   if is_bad else "rgba(99,102,241,0.3)"
            chip_col  = "#fca5a5"               if is_bad else "#a5b4fc"
            chips += f'<span style="background:{chip_bg};border:1px solid {chip_bord};border-radius:99px;padding:3px 10px;font-size:0.72rem;color:{chip_col};font-weight:600;white-space:nowrap;">{rule}</span>'
        rules_html = f"""
  <div style="margin-top:1.2rem;padding-top:1rem;border-top:1px solid rgba(255,255,255,0.07);">
    <div style="font-size:0.72rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
         color:#8b8baa;margin-bottom:8px;">🔍 Signals Detected</div>
    <div style="display:flex;flex-wrap:wrap;gap:6px;">{chips}</div>
  </div>"""

    return f"""
<style>
  @keyframes popIn {{from{{opacity:0;transform:scale(0.95) translateY(10px)}}to{{opacity:1;transform:scale(1) translateY(0)}}}}
  @keyframes barFill {{from{{width:0%}}to{{width:{confidence:.1f}%}}}}
</style>

<div style="background:var(--surface,#13131f);border:1px solid {accent_color}44;border-radius:20px;
     padding:1.6rem;animation:popIn 0.35s cubic-bezier(0.34,1.56,0.64,1);
     font-family:'Inter',sans-serif;box-shadow:0 0 40px {accent_color}18;">

  <!-- Result badge -->
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:1.2rem;">
    <div style="font-size:2.8rem;line-height:1;">{icon}</div>
    <div>
      <div style="font-size:1.6rem;font-weight:800;color:{accent_color};letter-spacing:-0.5px;">{text}</div>
      <div style="font-size:0.82rem;color:var(--muted,#8b8baa);margin-top:2px;">AI + Heuristic Prediction</div>
    </div>
    <div style="margin-left:auto;background:{conf_color}18;border:1px solid {conf_color}44;
         border-radius:99px;padding:4px 14px;font-size:0.8rem;font-weight:600;color:{conf_color};">
      {conf_label}
    </div>
  </div>

  <!-- Confidence bar -->
  <div style="margin-bottom:1.2rem;">
    <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px;">
      <span style="font-size:0.8rem;font-weight:600;color:var(--muted,#8b8baa);text-transform:uppercase;letter-spacing:0.08em;">Confidence</span>
      <span style="font-size:1.4rem;font-weight:800;color:var(--text,#f1f1f8);font-family:'JetBrains Mono',monospace;">{confidence:.1f}%</span>
    </div>
    <div style="background:rgba(255,255,255,0.07);border-radius:99px;height:10px;overflow:hidden;">
      <div style="height:100%;width:{confidence:.1f}%;background:{fill_bar};border-radius:99px;
           animation:barFill 0.7s cubic-bezier(.4,0,.2,1) both;"></div>
    </div>
  </div>

  <!-- Probability chips -->
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;">
    <div style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);
         border-radius:12px;padding:0.85rem 1rem;text-align:center;">
      <div style="font-size:0.7rem;color:#86efac;font-weight:700;letter-spacing:0.1em;
           text-transform:uppercase;margin-bottom:4px;">😂 Humorous</div>
      <div style="font-size:1.5rem;font-weight:800;color:#22c55e;
           font-family:'JetBrains Mono',monospace;">{prob_h:.1f}%</div>
    </div>
    <div style="background:rgba(168,85,247,0.08);border:1px solid rgba(168,85,247,0.2);
         border-radius:12px;padding:0.85rem 1rem;text-align:center;">
      <div style="font-size:0.7rem;color:#d8b4fe;font-weight:700;letter-spacing:0.1em;
           text-transform:uppercase;margin-bottom:4px;">😐 Non-Humorous</div>
      <div style="font-size:1.5rem;font-weight:800;color:#a855f7;
           font-family:'JetBrains Mono',monospace;">{prob_nh:.1f}%</div>
    </div>
  </div>

  {rules_html}
</div>
"""


def build_error_html(msg: str) -> str:
    return f"""
<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.3);
     border-radius:14px;padding:1rem 1.2rem;font-family:'Inter',sans-serif;
     color:#fca5a5;font-size:0.9rem;">
  {msg}
</div>"""


def build_placeholder_html() -> str:
    return """
<div style="background:var(--surface,#13131f);border:1px dashed rgba(255,255,255,0.1);
     border-radius:20px;padding:3rem 1.5rem;text-align:center;
     font-family:'Inter',sans-serif;color:var(--muted,#8b8baa);">
  <div style="font-size:2.5rem;margin-bottom:1rem;filter:grayscale(0.5);">🔍</div>
  <div style="font-size:0.95rem;font-weight:500;">Results appear here</div>
  <div style="font-size:0.82rem;margin-top:4px;opacity:0.7;">Type Tenglish text and hit Detect</div>
</div>
"""

# ─────────────────────────────────────────────
#  Examples
# ─────────────────────────────────────────────

EXAMPLES = [
    "amma cheppindi 'doctor avutav' ani, naa physics marks chusaka 'compounder avvachu' ani update chesindi 😂",
    "naa wifi chala fast undi — speed test lo matrame, actual lo ledu bro 🤣",
    "barber ki 'thoda trim' annanu — half head gone bro, lost in translation 💀",
    "Hyderabad traffic lo auto waala GPS lekka chepta 'road ki road lo pothav' ani 😅",
    "repu morning 9 o'clock ki team meeting undi office lo.",
    "Hyderabad lo eppudu chusina traffic ekkuva ga untundi.",
    "nenu kotha laptop order chesanu, repu delivery vastundi.",
]

# ─────────────────────────────────────────────
#  Event Handlers
# ─────────────────────────────────────────────


def run_detection(text: str):
    label, confidence, prob_h, prob_nh, triggered_rules, error = predict(text)
    if error:
        return build_error_html(error), history[:]
    return build_result_html(label, confidence, prob_h, prob_nh, triggered_rules), update_history(text, label, confidence)


def char_counter_update(text: str):
    n = len(text)
    if n > 450:
        color, msg = "#ef4444", f"{n}/500 — almost at limit!"
    elif n > 350:
        color, msg = "#f59e0b", f"{n}/500"
    else:
        color, msg = "var(--muted,#8b8baa)", f"{n}/500"
    return (
        f'<p style="font-size:0.78rem;text-align:right;margin:5px 0 0;'
        f'color:{color};font-family:\'Inter\',sans-serif;font-weight:500;">{msg}</p>'
    )


def load_example(evt: gr.SelectData):
    idx = evt.index if isinstance(evt.index, int) else evt.index[0]
    return EXAMPLES[idx]


# ─────────────────────────────────────────────
#  Gradio UI
# ─────────────────────────────────────────────

with gr.Blocks(title="Tenglish Humor Detector") as demo:


    with gr.Column(elem_id="page-shell"):
        theme_toggle_btn = gr.Button("☀️ Light Mode", elem_id="theme-toggle", size="sm")
        gr.HTML(HEADER_HTML)

        if model_load_error:
            gr.HTML(f"""
            <div style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.4);
                 border-radius:12px;padding:0.9rem 1.2rem;font-family:'Inter',sans-serif;
                 color:#fcd34d;font-size:0.9rem;margin-bottom:1.5rem;">
              ⚠️ <strong>Model not loaded.</strong> {model_load_error}
            </div>""")

        with gr.Row(equal_height=False, variant="panel"):

            # ── LEFT COLUMN ──────────────────────────────────────
            with gr.Column(scale=5, min_width=340):

                with gr.Group(elem_classes="card"):
                    gr.HTML('<div class="section-label">📝 Your Input</div>')
                    input_text = gr.Textbox(
                        label="",
                        show_label=False,
                        container=False,
                        placeholder="e.g.  naa exam result chusaka naku lift aipoindi bro 😂",
                        lines=4, max_lines=9,
                        elem_id="input-box",
                    )
                    char_counter_html = gr.HTML(
                        value='<p style="font-size:0.78rem;text-align:right;margin:5px 0 0;color:var(--muted,#8b8baa);font-family:\'Inter\',sans-serif;">0/500</p>'
                    )
                    detect_btn = gr.Button("🔍  Detect Humour", elem_id="detect-btn", variant="primary")

                with gr.Group(elem_classes="card"):
                    gr.HTML('<div class="section-label">💡 Quick Examples</div>')
                    gr.HTML("""
                    <div style="display:flex;gap:8px;margin-bottom:10px;flex-wrap:wrap;">
                      <span style="background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.3);
                           border-radius:99px;padding:3px 10px;font-size:0.72rem;color:#86efac;font-weight:600;">
                           😂 Rows 1-4 = Funny
                      </span>
                      <span style="background:rgba(168,85,247,0.12);border:1px solid rgba(168,85,247,0.3);
                           border-radius:99px;padding:3px 10px;font-size:0.72rem;color:#d8b4fe;font-weight:600;">
                           😐 Rows 5-7 = Neutral
                      </span>
                    </div>
                    """)
                    example_dataset = gr.Dataset(
                        components=[gr.Textbox(visible=False)],
                        samples=[[e] for e in EXAMPLES],
                        label="",
                        samples_per_page=7,
                        elem_id="example-dataset",
                    )

                with gr.Accordion("🧠 How it works", open=False, elem_classes="info-accordion"):
                    gr.Markdown("""
**MuRIL** (Multilingual Representations for Indian Languages) is a Google-trained BERT model
specially pre-trained on 17 Indian languages plus their transliterated forms.

This instance has been fine-tuned on Romanized **Tenglish** — code-mixed Telugu + English —
and paired with a rule-based heuristic layer for emoji & slang detection to compensate for
limited training data.
                    """)

            # ── RIGHT COLUMN ─────────────────────────────────────
            with gr.Column(scale=5, min_width=340):

                gr.HTML('<div class="section-label" style="margin-bottom:0.6rem;">🎯 Result</div>')
                result_html = gr.HTML(value=build_placeholder_html(), elem_id="result-zone")

                with gr.Group(elem_classes="card", visible=True):
                    gr.HTML('<div class="section-label">📋 Recent History</div>')
                    history_table = gr.Dataframe(
                        value=[],
                        headers=["Text Snippet", "Result", "Confidence"],
                        datatype=["str", "str", "str"],
                        row_count=(5, "fixed"),
                        column_count=(3, "fixed"),
                        interactive=False,
                        elem_id="hist-table",
                        wrap=True,
                    )

    gr.HTML("""
    <div id="app-footer">
        Tenglish Humor Detector &nbsp;·&nbsp; MuRIL Fine-tune &nbsp;·&nbsp;
        Low-Resource NLP Research
    </div>
    """)

    # ── Events ──────────────────────────────────────────────────
    input_text.change(fn=char_counter_update, inputs=input_text,
                      outputs=char_counter_html, queue=False)
    detect_btn.click(fn=run_detection, inputs=input_text,
                     outputs=[result_html, history_table])
    input_text.submit(fn=run_detection, inputs=input_text,
                      outputs=[result_html, history_table])
    example_dataset.select(fn=load_example, inputs=None, outputs=input_text)
    theme_toggle_btn.click(
        fn=None,
        js="() => { document.body.classList.toggle('light-mode'); return document.body.classList.contains('light-mode') ? '🌙 Dark Mode' : '☀️ Light Mode'; }",
        outputs=theme_toggle_btn
    )

# ─────────────────────────────────────────────
#  Launch
# ─────────────────────────────────────────────

if __name__ == "__main__":
    demo.launch(
        inbrowser=True,
        server_name="localhost",
        server_port=7863,
        css=CSS,
        theme=gr.themes.Base(
            font=[gr.themes.GoogleFont("Inter"), "sans-serif"],
        ),
    )
