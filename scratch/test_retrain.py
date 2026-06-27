# scratch/test_retrain.py
import re
import string
import pandas as pd
import pickle
from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# --- Setup Stemmer & Stopwords ---
factory = StemmerFactory()
stemmer = factory.create_stemmer()

stop_words = set(stopwords.words('indonesian'))
negations = {'tidak', 'bukan', 'belum', 'kurang', 'jangan', 'tanpa', 'tidaklah', 'tidakkah'}
stop_words = stop_words - negations

# Additional stopwords (excluding negation slang)
stop_words.update([
    'yg', 'dgn', 'ny', 'nya',
    'udah', 'udh', 'sdh', 'sudah', 'jg', 'juga', 'tp', 'tapi',
    'klo', 'kalo', 'kalau', 'bgt', 'banget', 'aja', 'saja',
    'lg', 'lagi', 'emg', 'emang', 'memang', 'sih', 'deh', 'dong',
    'lah', 'kan', 'kok', 'wkwk', 'haha', 'hehe', 'wah', 'wow', 'n'
])

slang_dict = {
    'gak': 'tidak',
    'ga': 'tidak',
    'ngga': 'tidak',
    'nggak': 'tidak',
    'blum': 'belum',
    'belom': 'belum',
    'dscrbs': 'deskripsi',
    'pic': 'foto',
    'paking': 'kemas',
    'packing': 'kemas',
}

def normalize_word(word):
    # 1. Reduce repeated chars (mantaaaaapp -> mantap)
    word = re.sub(r'(.)\1{2,}', r'\1', word)
    # 2. Slang mapping
    return slang_dict.get(word, word)

def preprocess(text):
    if not isinstance(text, str) or text.strip() == '':
        return ''
    text = text.lower()
    # Remove emoji
    text = text.encode('ascii', 'ignore').decode('ascii')
    # Remove URL, mention, hashtag, number, punctuation
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'@\w+|#\w+', '', text)
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\s+', ' ', text).strip()
    
    tokens = text.split()
    tokens = [normalize_word(w) for w in tokens]
    tokens = [word for word in tokens if word not in stop_words]
    tokens = [stemmer.stem(word) for word in tokens]
    return ' '.join(tokens)

# --- Test Reviews from User Image ---
test_reviews = [
    ("Sippp,sesuai pic,dscrbs..cuma blum dicoba", "positive"),
    ("Sayang produk yg datang di paking kurang rapi sehingga kebuka n isinya terhambur. Saran klo mengirimkan isi paku tembak seperti ini di beri lakban dulu dikemasan pakunya baru di gabung kan dgn yg lain supaya tidak tercecer. Untuk kualitas barang seperinya bagus walau saya belum coba. Terima kasih", "negative"),
    ("Barang sesuai deskripsi..respon dan proses cepat. Terima kasih", "positive"),
    ("Mantaaaaaaappp..........", "positive"),
    ("superrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr", "positive"),
    ("josss pokok e bisa buat langganan", "positive"),
    ("berfungsi dengan baik, normal", "positive"),
    ("Cara Memberikan Nilai Reputasi ke Penjual Untuk dapat memberikan nilai reputasi ke penjual, Anda dapat melakukan langkah-langkah berikut ini:", "neutral"),
    ("Barang sesuai dengan deskripsi. Pengiriman cepat gak pake lama. Barang bagus. Mantap dahh pokoknya. Thanks gan", "positive")
]

print("Preprocessing test cases:")
for rev, expected in test_reviews:
    print(f"Original: {rev[:60]}...")
    print(f"Cleaned : {preprocess(rev)}")
    print("-" * 30)
