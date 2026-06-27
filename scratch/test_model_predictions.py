# scratch/test_model_predictions.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pickle
from preprocessor import preprocess

# Load models
with open("models/svm_model.pkl", "rb") as f:
    svm_model = pickle.load(f)
with open("models/nb_model.pkl", "rb") as f:
    nb_model = pickle.load(f)
with open("models/vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

test_reviews = [
    "Sippp,sesuai pic,dscrbs..cuma blum dicoba",
    "Sayang produk yg datang di paking kurang rapi sehingga kebuka n isinya terhambur. Saran klo mengirimkan isi paku tembak seperti ini di beri lakban dulu dikemasan pakunya baru di gabung kan dgn yg lain supaya tidak tercecer. Untuk kualitas barang seperinya bagus walau saya belum coba. Terima kasih",
    "Barang sesuai deskripsi..respon dan proses cepat. Terima kasih",
    "Mantaaaaaaappp..........",
    "superrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr",
    "josss pokok e bisa buat langganan",
    "berfungsi dengan baik, normal",
    "Cara Memberikan Nilai Reputasi ke Penjual Untuk dapat memberikan nilai reputasi ke penjual, Anda dapat melakukan langkah-langkah berikut ini:",
    "Barang sesuai dengan deskripsi. Pengiriman cepat gak pake lama. Barang bagus. Mantap dahh pokoknya. Thanks gan"
]

print("PREDICTIONS ON USER REVIEWS:")
print("=" * 60)
for text in test_reviews:
    cleaned = preprocess(text)
    vector = vectorizer.transform([cleaned])
    svm_pred = svm_model.predict(vector)[0]
    nb_pred = nb_model.predict(vector)[0]
    print(f"Original : {text[:80]}...")
    print(f"Cleaned  : {cleaned}")
    print(f"SVM Pred : {svm_pred}")
    print(f"NB Pred  : {nb_pred}")
    print("-" * 60)
