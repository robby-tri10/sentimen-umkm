# train_model.py
# Script untuk melatih model Naive Bayes dan SVM
# menggunakan dataset PRDECT-ID, lalu menyimpannya ke folder models/
#
# Jalankan script ini SEKALI sebelum menjalankan app.py:
#   python train_model.py

import os
import pickle
import pandas as pd
import numpy as np
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score,
    recall_score, f1_score, confusion_matrix,
    classification_report
)
from preprocessor import preprocess_batch

# ============================================================
# KONFIGURASI
# ============================================================
DATA_PATH = "data/prdect_id.csv"
MODEL_DIR = "models"
RANDOM_STATE = 42
TEST_SIZE = 0.2

# ============================================================
# LANGKAH 1: LOAD DATASET
# ============================================================
print("=" * 50)
print("TRAINING MODEL SENTIMEN UMKM")
print("=" * 50)
print("\n[1/5] Memuat dataset...")

df = pd.read_csv(DATA_PATH)
print(f"    Total data: {len(df)} baris")
print(f"    Kolom tersedia: {list(df.columns)}")

# Sesuaikan nama kolom dengan dataset PRDECT-ID
# Kolom ulasan: 'review' atau 'text' atau 'ulasan'
# Kolom label: 'sentiment' atau 'label' atau 'sentimen'
# Ganti sesuai nama kolom aktual di file CSV-mu
KOLOM_TEKS = 'Customer Review'       # Ganti jika berbeda
KOLOM_LABEL = 'Sentiment'   # Ganti jika berbeda

# Mapping label ke 3 kelas jika diperlukan
# PRDECT-ID menggunakan label: positive, negative, neutral
df = df[[KOLOM_TEKS, KOLOM_LABEL]].dropna()
df.columns = ['teks', 'label']

# Normalisasi label
df['label'] = df['label'].str.lower().str.strip()
df = df[df['label'].isin(['positive', 'negative', 'neutral'])]

print(f"    Data setelah filtering: {len(df)} baris")
print(f"    Distribusi label:\n{df['label'].value_counts().to_string()}")

# ============================================================
# LANGKAH 2: PREPROCESSING
# ============================================================
print("\n[2/5] Melakukan preprocessing teks...")
print("    (Proses ini membutuhkan beberapa menit, harap tunggu...)")

df['teks_bersih'] = preprocess_batch(df['teks'].tolist())
df = df[df['teks_bersih'].str.strip() != '']
print(f"    Data siap dilatih: {len(df)} baris")

# ============================================================
# LANGKAH 3: SPLIT DATA
# ============================================================
print(f"\n[3/5] Membagi data (Training: {int((1-TEST_SIZE)*100)}% | Testing: {int(TEST_SIZE*100)}%)...")

X = df['teks_bersih']
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=y
)

print(f"    Data training: {len(X_train)} sampel")
print(f"    Data testing : {len(X_test)} sampel")

# ============================================================
# LANGKAH 4: EKSTRAKSI FITUR TF-IDF
# ============================================================
print("\n[4/5] Ekstraksi fitur TF-IDF...")

vectorizer = TfidfVectorizer(
    max_features=10000,
    ngram_range=(1, 2),
    min_df=2
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)
print(f"    Jumlah fitur TF-IDF: {X_train_tfidf.shape[1]}")

# ============================================================
# LANGKAH 5: TRAINING DAN EVALUASI MODEL
# ============================================================
print("\n[5/5] Melatih dan mengevaluasi model...\n")

# Fungsi evaluasi
def evaluasi_model(nama, model, X_test, y_test):
    y_pred = model.predict(X_test)
    
    akurasi  = accuracy_score(y_test, y_pred) * 100
    presisi  = precision_score(y_test, y_pred, average='weighted', zero_division=0) * 100
    recall   = recall_score(y_test, y_pred, average='weighted', zero_division=0) * 100
    f1       = f1_score(y_test, y_pred, average='weighted', zero_division=0) * 100
    cm       = confusion_matrix(y_test, y_pred, labels=['positive', 'negative', 'neutral'])

    print(f"  [{nama}]")
    print(f"    Akurasi  : {akurasi:.2f}%")
    print(f"    Presisi  : {presisi:.2f}%")
    print(f"    Recall   : {recall:.2f}%")
    print(f"    F1-Score : {f1:.2f}%")
    print(f"    Confusion Matrix:\n{cm}\n")

    return {
        "akurasi": round(akurasi, 2),
        "presisi": round(presisi, 2),
        "recall": round(recall, 2),
        "f1_score": round(f1, 2),
        "confusion_matrix": cm.tolist(),
        "labels": ['positive', 'negative', 'neutral']
    }

# Training Naive Bayes
print("  Melatih Naive Bayes...")
nb_model = MultinomialNB(alpha=1.0)
nb_model.fit(X_train_tfidf, y_train)
nb_metrics = evaluasi_model("Naive Bayes", nb_model, X_test_tfidf, y_test)

# Training SVM
print("  Melatih SVM (LinearSVC)...")
svm_model = LinearSVC(C=1.0, max_iter=2000, random_state=RANDOM_STATE)
svm_model.fit(X_train_tfidf, y_train)
svm_metrics = evaluasi_model("SVM (LinearSVC)", svm_model, X_test_tfidf, y_test)

# ============================================================
# SIMPAN MODEL DAN HASIL EVALUASI
# ============================================================
os.makedirs(MODEL_DIR, exist_ok=True)

with open(f"{MODEL_DIR}/nb_model.pkl", "wb") as f:
    pickle.dump(nb_model, f)

with open(f"{MODEL_DIR}/svm_model.pkl", "wb") as f:
    pickle.dump(svm_model, f)

with open(f"{MODEL_DIR}/vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

with open(f"{MODEL_DIR}/metrics.pkl", "wb") as f:
    pickle.dump({
        "naive_bayes": nb_metrics,
        "svm": svm_metrics,
        "jumlah_data": {
            "total": len(df),
            "training": len(X_train),
            "testing": len(X_test)
        }
    }, f)

print("=" * 50)
print("TRAINING SELESAI!")
print(f"Model tersimpan di folder: {MODEL_DIR}/")
print("  - nb_model.pkl    (Naive Bayes)")
print("  - svm_model.pkl   (SVM)")
print("  - vectorizer.pkl  (TF-IDF Vectorizer)")
print("  - metrics.pkl     (Hasil evaluasi)")
print("\nSekarang jalankan: python app.py")
print("=" * 50)
