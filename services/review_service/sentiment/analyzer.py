import difflib
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk
import os

nltk_data_path = os.path.join(os.path.dirname(__file__), "nltk_data")
if not os.path.exists(nltk_data_path):
    os.makedirs(nltk_data_path, exist_ok=True)

nltk.download('punkt', download_dir=nltk_data_path)
nltk.download('wordnet', download_dir=nltk_data_path)

nltk.data.path.append(nltk_data_path)


lemmatizer = WordNetLemmatizer()

positive_words = ["качественный", "удобный", "красивый", "отличный"]
negative_words = ["плохой", "медленный", "разочарован", "ненадежный"]

def get_similarity(word, word_list):
    return max([difflib.SequenceMatcher(None, word, w).ratio() for w in word_list], default=0)

def analyze_sentiment(text: str):
    tokens = word_tokenize(text.lower())
    lexemes = [lemmatizer.lemmatize(w) for w in tokens if w.isalpha()]

    pos = [get_similarity(w, positive_words) for w in lexemes if get_similarity(w, positive_words) > 0.5]
    neg = [get_similarity(w, negative_words) for w in lexemes if get_similarity(w, negative_words) > 0.5]

    avg_pos = round(sum(pos) / len(pos) * 100, 2) if pos else 0
    avg_neg = round(sum(neg) / len(neg) * 100, 2) if neg else 0

    if avg_pos > avg_neg and avg_pos > 50:
        sentiment = "positive"
    elif avg_neg > avg_pos and avg_neg > 50:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {
        "sentiment": sentiment,
        "pos_score": avg_pos,
        "neg_score": avg_neg
    }
