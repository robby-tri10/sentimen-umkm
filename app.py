# app.py
# Backend Flask untuk sistem analisis sentimen ulasan produk e-commerce
# Jalankan dengan: python app.py

import pickle
import os
import io
import uuid
import pandas as pd
from flask import (
    Flask, render_template, request,
    jsonify, session, send_file
)
from preprocessor import preprocess, preprocess_batch
from recommender import get_rekomendasi, get_rekomendasi_batch

app = Flask(__name__)
app.secret_key = 'sentimen-umkm-secret-key-2024'

# ============================================================
# LOAD MODEL & SETUP
# ============================================================
MODEL_DIR = "models"
TEMP_DIR = "temp_results"
os.makedirs(TEMP_DIR, exist_ok=True)

def load_models():
    """Memuat semua model yang sudah ditraining."""
    try:
        with open(f"{MODEL_DIR}/nb_model.pkl", "rb") as f:
            nb_model = pickle.load(f)
        with open(f"{MODEL_DIR}/svm_model.pkl", "rb") as f:
            svm_model = pickle.load(f)
        with open(f"{MODEL_DIR}/vectorizer.pkl", "rb") as f:
            vectorizer = pickle.load(f)
        with open(f"{MODEL_DIR}/metrics.pkl", "rb") as f:
            metrics = pickle.load(f)
        print("[OK] Semua model berhasil dimuat.")
        return nb_model, svm_model, vectorizer, metrics
    except FileNotFoundError:
        print("[ERROR] Model belum ada. Jalankan train_model.py terlebih dahulu.")
        return None, None, None, None

nb_model, svm_model, vectorizer, metrics_data = load_models()

# ============================================================
# HELPER: Prediksi satu teks
# ============================================================
def predict_single(teks_asli, algo='svm'):
    """Memproses dan memprediksi sentimen dari satu teks ulasan."""
    teks_bersih = preprocess(teks_asli)

    if not teks_bersih.strip():
        return {
            "error": "Teks terlalu pendek atau tidak mengandung kata bermakna."
        }

    vektor = vectorizer.transform([teks_bersih])

    # Prediksi Naive Bayes
    nb_label = nb_model.predict(vektor)[0]
    try:
        nb_proba = nb_model.predict_proba(vektor)[0]
        nb_conf = round(float(max(nb_proba)) * 100, 1)
    except Exception:
        nb_conf = 75.0  # fallback jika predict_proba gagal

    # Prediksi SVM (LinearSVC tidak punya predict_proba)
    svm_label = svm_model.predict(vektor)[0]
    try:
        svm_decision = svm_model.decision_function(vektor)[0]
        import numpy as np
        if hasattr(svm_decision, '__len__'):
            # Softmax conversion to get natural probability percentage
            exp_scores = np.exp(svm_decision - np.max(svm_decision))
            probs = exp_scores / np.sum(exp_scores)
            svm_conf = round(float(np.max(probs)) * 100, 1)
        else:
            # Sigmoid for binary classification
            prob = 1 / (1 + np.exp(-svm_decision))
            svm_conf = round(float(max(prob, 1 - prob)) * 100, 1)
        svm_conf = min(svm_conf, 99.9)
    except Exception:
        svm_conf = 80.0  # fallback jika decision_function gagal

    # Rekomendasi dari model terpilih (bila labelnya negatif)
    rekomendasi = []
    target_label = nb_label if algo == 'nb' else svm_label
    if target_label == 'negative':
        rekomendasi = get_rekomendasi(teks_bersih)

    return {
        "teks_asli": teks_asli,
        "teks_bersih": teks_bersih,
        "naive_bayes": {
            "label": nb_label,
            "label_id": label_to_id(nb_label),
            "keyakinan": nb_conf
        },
        "svm": {
            "label": svm_label,
            "label_id": label_to_id(svm_label),
            "keyakinan": svm_conf
        },
        "rekomendasi": rekomendasi
    }


def label_to_id(label):
    """Mengubah label teks ke ID untuk styling frontend."""
    mapping = {
        'positive': 'positif',
        'negative': 'negatif',
        'neutral': 'netral'
    }
    return mapping.get(label, label)


def label_to_indo(label):
    """Mengubah label bahasa Inggris ke bahasa Indonesia."""
    mapping = {
        'positive': 'Positif',
        'negative': 'Negatif',
        'neutral': 'Netral'
    }
    return mapping.get(label, label)


# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def landing():
    """Halaman Landing Page."""
    return render_template('landing.html')


@app.route('/analisis')
def index():
    """Halaman utama - Analisis sentimen."""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Halaman dashboard visualisasi."""
    hasil_csv = session.get('hasil_csv', None)
    return render_template('dashboard.html', hasil=hasil_csv)


@app.route('/rekomendasi')
def rekomendasi():
    """Halaman rekomendasi perbaikan produk."""
    hasil_csv = session.get('hasil_csv', None)
    return render_template('rekomendasi.html', hasil=hasil_csv)


@app.route('/perbandingan')
def perbandingan():
    """Halaman perbandingan metrik Naive Bayes vs SVM."""
    hasil_csv = session.get('hasil_csv', None)
    return render_template('perbandingan.html', metrics=metrics_data, hasil_csv=hasil_csv)


@app.route('/clear-data')
def clear_data():
    """Hapus semua data hasil analisis CSV dari session."""
    session.pop('hasil_csv', None)
    from flask import redirect, url_for
    return redirect(url_for('index'))


# ============================================================
# API ENDPOINTS
# ============================================================

@app.route('/api/predict-teks', methods=['POST'])
def api_predict_teks():
    """
    API untuk analisis satu ulasan teks.
    Request: { "teks": "ulasan produk..." }
    Response: hasil klasifikasi NB + SVM + rekomendasi
    """
    if nb_model is None:
        return jsonify({"error": "Model belum dilatih. Jalankan train_model.py"}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body tidak valid."}), 400

        teks = data.get('teks', '').strip()
        algo = data.get('algo', 'svm').strip().lower()

        if not teks:
            return jsonify({"error": "Teks ulasan tidak boleh kosong."}), 400

        hasil = predict_single(teks, algo=algo)

        if "error" in hasil:
            return jsonify(hasil), 400

        # Format label ke bahasa Indonesia untuk tampilan
        hasil['naive_bayes']['label_tampil'] = label_to_indo(hasil['naive_bayes']['label'])
        hasil['svm']['label_tampil'] = label_to_indo(hasil['svm']['label'])
        hasil['selected_algo'] = algo

        return jsonify(hasil)

    except Exception as e:
        print(f"[ERROR predict-teks] {str(e)}")
        return jsonify({"error": f"Terjadi kesalahan server: {str(e)}"}), 500


@app.route('/api/predict-csv', methods=['POST'])
def api_predict_csv():
    """
    API untuk analisis banyak ulasan dari file CSV.
    Request: multipart/form-data dengan file CSV
    Response: distribusi sentimen + rekomendasi batch
    """
    if nb_model is None:
        return jsonify({"error": "Model belum dilatih. Jalankan train_model.py"}), 500

    if 'file' not in request.files:
        return jsonify({"error": "File CSV tidak ditemukan."}), 400

    file = request.files['file']
    algo = request.form.get('algo', 'svm').strip().lower()

    if file.filename == '' or not file.filename.endswith('.csv'):
        return jsonify({"error": "Format file harus CSV."}), 400

    try:
        df = pd.read_csv(io.StringIO(file.stream.read().decode('utf-8')))
    except Exception:
        return jsonify({"error": "File CSV tidak dapat dibaca. Pastikan encoding UTF-8."}), 400

    # Deteksi kolom ulasan
    kolom_kandidat = ['ulasan', 'Customer Review', 'review', 'teks', 'text', 'komentar', 'comment']
    kolom_teks = None
    for kol in kolom_kandidat:
        if kol in df.columns:
            kolom_teks = kol
            break

    if kolom_teks is None:
        return jsonify({
            "error": f"Kolom ulasan tidak ditemukan. Pastikan CSV memiliki kolom: {kolom_kandidat}"
        }), 400

    df = df[[kolom_teks]].dropna()
    df.columns = ['teks']
    df['teks'] = df['teks'].astype(str)

    if len(df) == 0:
        return jsonify({"error": "File CSV tidak memiliki data ulasan."}), 400

    if len(df) > 50000:
        df = df.head(50000)  # Batasi maksimum 50.000 baris

    # Preprocessing batch
    df['teks_bersih'] = preprocess_batch(df['teks'].tolist())
    df = df[df['teks_bersih'].str.strip() != '']

    # Prediksi batch
    vektor = vectorizer.transform(df['teks_bersih'])
    df['label_nb'] = nb_model.predict(vektor)
    df['label_svm'] = svm_model.predict(vektor)

    # Hitung distribusi
    total = len(df)

    def hitung_distribusi(kolom):
        counts = df[kolom].value_counts().to_dict()
        return {
            "positif": counts.get('positive', 0),
            "negatif": counts.get('negative', 0),
            "netral": counts.get('neutral', 0),
            "total": total
        }

    dist_nb = hitung_distribusi('label_nb')
    dist_svm = hitung_distribusi('label_svm')

    # Rekomendasi dari ulasan negatif (berdasarkan model terpilih)
    label_col = 'label_nb' if algo == 'nb' else 'label_svm'
    teks_negatif = df[df[label_col] == 'negative']['teks_bersih'].tolist()
    rekomendasi_batch = get_rekomendasi_batch(teks_negatif)

    # Kata kunci paling sering dari ulasan negatif
    kata_kunci = []
    if teks_negatif:
        kata_blacklist = {
            'barang', 'produk', 'item', 'beli', 'bisa', 'ada', 'tidak',
            'tdk', 'udah', 'sudah', 'belum', 'lebih', 'sangat', 'banget',
            'aja', 'saja', 'juga', 'sama', 'lagi', 'nya', 'ini', 'itu',
            'yang', 'dan', 'tapi', 'atau', 'dengan', 'untuk', 'dari',
            'ke', 'di', 'pada', 'karena', 'jadi', 'kalau', 'mau', 'maka',
            'bagus', 'baik', 'oke', 'ok', 'good', 'best', 'sesuai',
            'pesan', 'beli', 'dapat', 'terima', 'sampai', 'datang',
            'kirim', 'paket', 'order', 'seller', 'toko', 'harga',
            'gambar', 'foto', 'warna', 'ukuran', 'size', 'kualitas'
        }
        kata_negatif_leksikon = {
            'rusak', 'cacat', 'penyok', 'pecah', 'hancur', 'patah',
            'lambat', 'lama', 'telat', 'terlambat', 'slow',
            'palsu', 'tipu', 'menipu', 'bohong', 'curang',
            'mengecewakan', 'kecewa', 'buruk', 'jelek', 'parah',
            'bau', 'kotor', 'bekas', 'lecet', 'sobek', 'retak',
            'salah', 'keliru', 'tidak sesuai', 'berbeda',
            'mahal', 'kemahalan', 'kemurahan',
            'tidak responsif', 'tidak balas', 'tidak respon',
            'kecil', 'kebesaran', 'kekecilan',
            'zonk', 'sampah', 'busuk'
        }
        from sklearn.feature_extraction.text import CountVectorizer
        cv = CountVectorizer(max_features=50, ngram_range=(1, 2), min_df=2)
        try:
            matrix = cv.fit_transform(teks_negatif)
            vocab = cv.get_feature_names_out()
            frekuensi = matrix.toarray().sum(axis=0)
            hasil_kata = []
            for kata, freq in zip(vocab, frekuensi):
                kata_bersih = kata.strip().lower()
                if kata_bersih in kata_negatif_leksikon:
                    hasil_kata.append({"kata": kata_bersih, "frekuensi": int(freq), "prioritas": 1})
                elif kata_bersih not in kata_blacklist and len(kata_bersih) > 3:
                    hasil_kata.append({"kata": kata_bersih, "frekuensi": int(freq), "prioritas": 2})
            hasil_kata.sort(key=lambda x: (x['prioritas'], -x['frekuensi']))
            kata_kunci = [{"kata": item["kata"], "frekuensi": item["frekuensi"]} for item in hasil_kata[:8]]
        except Exception:
            kata_kunci = []

    # Hitung perbandingan prediksi NB vs SVM
    sama = int((df['label_nb'] == df['label_svm']).sum())
    berbeda = int((df['label_nb'] != df['label_svm']).sum())
    persen_sama = round(sama / total * 100, 1)
    persen_berbeda = round(berbeda / total * 100, 1)

    kelas = ['positive', 'negative', 'neutral']
    kelas_id = {'positive': 'Positif', 'negative': 'Negatif', 'neutral': 'Netral'}
    ketidaksesuaian = []
    for kls_nb in kelas:
        for kls_svm in kelas:
            if kls_nb != kls_svm:
                jumlah = int(((df['label_nb'] == kls_nb) & (df['label_svm'] == kls_svm)).sum())
                if jumlah > 0:
                    ketidaksesuaian.append({
                        "nb": kelas_id[kls_nb],
                        "svm": kelas_id[kls_svm],
                        "jumlah": jumlah,
                        "persen": round(jumlah / total * 100, 1)
                    })
    ketidaksesuaian.sort(key=lambda x: -x['jumlah'])

    # Ambil maksimal 500 baris untuk detail ulasan di frontend
    detail_ulasan = []
    df_sample = df.head(500)
    for _, row in df_sample.iterrows():
        detail_ulasan.append({
            "teks_asli": row['teks'],
            "teks_bersih": row['teks_bersih'],
            "label_nb": label_to_id(row['label_nb']),
            "label_nb_tampil": label_to_indo(row['label_nb']),
            "label_svm": label_to_id(row['label_svm']),
            "label_svm_tampil": label_to_indo(row['label_svm'])
        })

    # Simpan dataframe ke file temp untuk diunduh nanti
    file_id = str(uuid.uuid4())
    temp_path = os.path.join(TEMP_DIR, f"{file_id}.csv")
    df_export = df[['teks', 'teks_bersih', label_col]].copy()
    df_export.columns = ['Ulasan Asli', 'Ulasan Bersih', 'Sentimen']
    df_export['Sentimen'] = df_export['Sentimen'].map({'positive': 'Positif', 'negative': 'Negatif', 'neutral': 'Netral'})
    df_export.to_csv(temp_path, index=False, encoding='utf-8')

    hasil = {
        "total_ulasan": total,
        "distribusi_nb": dist_nb,
        "distribusi_svm": dist_svm,
        "rekomendasi": rekomendasi_batch,
        "kata_kunci_negatif": kata_kunci,
        "detail_ulasan": detail_ulasan,
        "selected_algo": algo,
        "file_id": file_id
    }

    # Simpan ke session tanpa detail_ulasan agar tidak overflow cookie
    hasil_session = {
        "total_ulasan": total,
        "distribusi_nb": dist_nb,
        "distribusi_svm": dist_svm,
        "rekomendasi": rekomendasi_batch,
        "kata_kunci_negatif": kata_kunci,
        "selected_algo": algo,
        "perbandingan_csv": {
            "total": total,
            "sama": sama,
            "berbeda": berbeda,
            "persen_sama": persen_sama,
            "persen_berbeda": persen_berbeda,
            "ketidaksesuaian": ketidaksesuaian[:5],
            "distribusi_nb": dist_nb,
            "distribusi_svm": dist_svm,
            "selected_algo": algo
        }
    }
    session['hasil_csv'] = hasil_session

    return jsonify(hasil)


@app.route('/api/download-csv/<file_id>', methods=['GET'])
def download_csv(file_id):
    """
    Endpoint untuk mendownload hasil analisis CSV yang sudah difilter berdasarkan sentimen.
    """
    sentiment_filter = request.args.get('sentiment', 'all').lower()
    
    # Path ke file sementara
    temp_path = os.path.join(TEMP_DIR, f"{file_id}.csv")
    if not os.path.exists(temp_path):
        return "File tidak ditemukan atau sudah kadaluarsa", 404

    try:
        df = pd.read_csv(temp_path)
        
        # Filter berdasarkan sentimen
        if sentiment_filter == 'positive':
            df = df[df['Sentimen'] == 'Positif']
            filename_suffix = "Positif"
        elif sentiment_filter == 'negative':
            df = df[df['Sentimen'] == 'Negatif']
            filename_suffix = "Negatif"
        elif sentiment_filter == 'neutral':
            df = df[df['Sentimen'] == 'Netral']
            filename_suffix = "Netral"
        else:
            filename_suffix = "Lengkap"

        # Simpan sementara memori buffer untuk didownload
        output = io.BytesIO()
        df.to_csv(output, index=False, encoding='utf-8')
        output.seek(0)

        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'Hasil_Analisis_Sentimen_{filename_suffix}.csv'
        )
    except Exception as e:
        print(f"[ERROR download-csv] {str(e)}")
        return "Terjadi kesalahan saat membuat file unduhan", 500


# ============================================================
# JALANKAN SERVER
# ============================================================
if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("SISTEM ANALISIS SENTIMEN UMKM")
    print("=" * 50)
    print("Akses di browser: http://127.0.0.1:5000")
    print("Tekan CTRL+C untuk menghentikan server.")
    print("=" * 50 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5000)
