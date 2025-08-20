# services/review_service/sentiment/analyzer.py
import os
import re
import difflib
from typing import List

import nltk
from nltk.tokenize import word_tokenize

# --- NLTK path & lazy ensure ---
NLTK_DATA = os.environ.get("NLTK_DATA") or os.path.join(os.path.dirname(__file__), "nltk_data")
os.makedirs(NLTK_DATA, exist_ok=True)
if NLTK_DATA not in nltk.data.path:
    nltk.data.path.append(NLTK_DATA)

def _ensure(resource: str):
    """Гарантируем наличие ресурса NLTK; при ошибке не валимся."""
    try:
        nltk.data.find(resource)
    except LookupError:
        try:
            nltk.download(resource.split("/")[-1], download_dir=NLTK_DATA, quiet=True)
        except Exception as e:
            print(f"[nltk] can't ensure {resource}: {e}")

# Пытаемся обеспечить 'punkt'; при фейле будет фолбэк
_ensure("tokenizers/punkt")

# WordNet лемматизация для английского — опциональна; для RU/UK вернёт слово как есть.
try:
    from nltk.stem import WordNetLemmatizer
    _ensure("corpora/wordnet")
    _lemmatizer = WordNetLemmatizer()
    def _lem(w: str) -> str:
        try:
            return _lemmatizer.lemmatize(w)
        except Exception:
            return w
except Exception:
    def _lem(w: str) -> str:
        return w

# --- Лексиконы (RU + UK, можно расширять) ---
POSITIVE_WORDS = [
    "качественный", "удобный", "красивый", "отличный", "классный", "хороший", "нравится",
    "чудовий", "зручний", "стильний", "класний", "відмінний", "гарний", "якісний"
]
NEGATIVE_WORDS = [
    "плохой", "медленный", "разочарован", "ненадежный", "ужасный", "плохая", "не понравилось", "тусклый",
    "поганий", "повільний", "розчарований", "ненадійний", "жахливий", "тьмяний", "не сподобалось"
]

# --- Утилиты ---
def _tokenize(text: str) -> List[str]:
    """Пытаемся токенизировать через punkt; если его нет — простой regex."""
    try:
        toks = word_tokenize(text)
        return [t for t in toks if t.isalpha()]
    except Exception:
        return re.findall(r"[A-Za-zА-Яа-яЁёІіЇїЄєҐґ]+", text)

def _similarity_to_lexicon(word: str, lexicon: List[str]) -> float:
    """max similarity к словам в лексиконе (0..1)."""
    best = 0.0
    for w in lexicon:
        r = difflib.SequenceMatcher(None, word, w).ratio()
        if r > best:
            best = r
    return best

# --- Основная функция ---
def analyze_sentiment(text: str):
    # нормализация
    text = (text or "").lower()

    # токены -> "леммы" (для RU/UK лемматизатор английский, поэтому вернёт как есть — это ок)
    tokens = _tokenize(text)
    lexemes = [_lem(t) for t in tokens]

    # считаем похожесть на позитив/негатив; берём только достаточно похожие слова
    THRESHOLD = 0.6  # можно подстроить
    pos_scores = []
    neg_scores = []
    for w in lexemes:
        sp = _similarity_to_lexicon(w, POSITIVE_WORDS)
        sn = _similarity_to_lexicon(w, NEGATIVE_WORDS)
        if sp >= THRESHOLD:
            pos_scores.append(sp)
        if sn >= THRESHOLD:
            neg_scores.append(sn)

    # усредняем (0..1), округляем до 2 знаков
    avg_pos = round(sum(pos_scores) / len(pos_scores), 2) if pos_scores else 0.0
    avg_neg = round(sum(neg_scores) / len(neg_scores), 2) if neg_scores else 0.0

    # решение
    DECISION_THRESHOLD = 0.6  # чтобы "нейтральный" не пропадал
    if avg_pos > avg_neg and avg_pos >= DECISION_THRESHOLD:
        sentiment = "positive"
    elif avg_neg > avg_pos and avg_neg >= DECISION_THRESHOLD:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {
        "sentiment": sentiment,
        "pos_score": avg_pos,  # 0..1
        "neg_score": avg_neg,  # 0..1
    }
