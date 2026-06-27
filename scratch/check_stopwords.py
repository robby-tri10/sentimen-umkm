# scratch/check_stopwords.py
import nltk
from nltk.corpus import stopwords
import re

try:
    stop_words = set(stopwords.words('indonesian'))
    print("Total Indonesian stopwords:", len(stop_words))
    
    negations = [w for w in stop_words if w in ['tidak', 'bukan', 'belum', 'kurang', 'jangan', 'tanpa', 'tidaklah', 'tidakkah']]
    print("Negation words in stopwords:", negations)
    
except Exception as e:
    print("Error:", e)

# Test repeated character reduction
def reduce_repeated_chars(text):
    # reduce 3 or more repeated characters to 1
    return re.sub(r'(.)\1{2,}', r'\1', text)

test_cases = [
    "Mantaaaaaaappp..........",
    "superrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr",
    "Sippp,sesuai pic",
    "josss pokok e"
]
for tc in test_cases:
    print(f"'{tc}' -> '{reduce_repeated_chars(tc)}'")
