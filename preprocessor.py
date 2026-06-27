import re
import string
from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Inisialisasi stemmer Sastrawi (hanya sekali agar lebih efisien)
factory = StemmerFactory()
stemmer = factory.create_stemmer()

# Stopword bahasa Indonesia dari NLTK
stop_words = set(stopwords.words('indonesian'))

# Kata negasi penting yang TIDAK BOLEH dihapus untuk menjaga makna sentimen
negasi_words = {'tidak', 'bukan', 'belum', 'kurang', 'jangan', 'tanpa', 'tidaklah', 'tidakkah'}
stop_words = stop_words - negasi_words

# Tambahan stopword manual (yang tidak mengandung kata negasi)
stop_words.update([
    'yg', 'dgn', 'ny', 'nya',
    'udah', 'udh', 'sdh', 'sudah', 'jg', 'juga',
    'klo', 'kalo', 'kalau', 'bgt', 'banget', 'aja', 'saja',
    'lg', 'lagi', 'emg', 'emang', 'memang', 'sih', 'deh', 'dong',
    'lah', 'kan', 'kok', 'wkwk', 'haha', 'hehe', 'wah', 'wow', 'n'
])

# Kamus normalisasi slang/singkatan
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
    'jos': 'bagus',
    'joss': 'bagus',
    'josss': 'bagus',
    'sip': 'oke',
    'sipp': 'oke',
    'sippp': 'oke',
}


def case_folding(text):
    """Mengubah seluruh teks menjadi huruf kecil."""
    return text.lower()


def remove_noise(text):
    """Menghapus angka, tanda baca, URL, dan karakter khusus."""
    # Hapus URL
    text = re.sub(r'http\S+|www\S+', '', text)
    # Hapus mention dan hashtag
    text = re.sub(r'@\w+|#\w+', '', text)
    # Hapus angka
    text = re.sub(r'\d+', '', text)
    
    # Ganti tanda baca dengan spasi agar kata tidak menempel (contoh: "sipp,sesuai" -> "sipp sesuai")
    translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    text = text.translate(translator)
    
    # Hapus spasi berlebih
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def tokenize(text):
    """Memecah kalimat menjadi daftar kata (token)."""
    return text.split()


def normalize_token(word):
    """Mereduksi pengulangan karakter berlebih dan memetakan slang."""
    # 1. Reduksi karakter berlebih (misal: "mantaaaaaapp" -> "mantap", "superrrr" -> "super")
    word = re.sub(r'(.)\1{2,}', r'\1', word)
    
    # 2. Pemetaan kata slang/singkatan
    return slang_dict.get(word, word)


def remove_stopwords(tokens):
    """Menghapus kata-kata yang tidak bermakna (stopwords)."""
    return [word for word in tokens if word not in stop_words]


def stem(tokens):
    """Mengubah kata berimbuhan menjadi kata dasar menggunakan Sastrawi."""
    return [stemmer.stem(word) for word in tokens]


def preprocess(text):
    """
    Fungsi utama preprocessing yang menjalankan seluruh tahapan:
    case folding -> remove noise -> tokenize -> normalize -> remove stopwords -> stem
    
    Returns:
        str: Teks yang sudah bersih dan siap diproses model
    """
    if not isinstance(text, str) or text.strip() == '':
        return ''
    
    # Deteksi & hapus emoji agar tidak mengganggu pemrosesan teks dasar
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    text = case_folding(text)
    text = remove_noise(text)
    tokens = tokenize(text)
    
    # Langkah normalisasi (reduksi kata berulang + pemetaan slang)
    tokens = [normalize_token(w) for w in tokens]
    
    tokens = remove_stopwords(tokens)
    tokens = stem(tokens)
    
    return ' '.join(tokens)


def preprocess_batch(texts):
    """
    Memproses banyak teks sekaligus (untuk upload CSV).
    
    Args:
        texts: list atau pandas Series berisi teks ulasan
    Returns:
        list: Daftar teks yang sudah dipreprocess
    """
    return [preprocess(str(text)) for text in texts]
