# recommender.py
# Modul rule-based recommendation untuk menghasilkan rekomendasi
# perbaikan produk berdasarkan kata kunci dari ulasan negatif.

# Tabel aturan: kata kunci -> rekomendasi perbaikan
RULE_TABLE = [
    {
        "keywords": ["rusak", "cacat", "penyok", "pecah", "hancur", "patah", "retak", "bengkok"],
        "kategori": "Kualitas Produk",
        "rekomendasi": "Tingkatkan standar pengemasan dan penanganan produk sebelum pengiriman. Pertimbangkan penggunaan bahan pelindung tambahan seperti bubble wrap atau kardus tebal."
    },
    {
        "keywords": ["lambat", "lama", "telat", "terlambat", "lelet", "lambat banget", "lama banget"],
        "kategori": "Kecepatan Pengiriman",
        "rekomendasi": "Evaluasi mitra logistik yang digunakan dan pertimbangkan untuk menambah opsi layanan pengiriman ekspres agar konsumen memiliki pilihan yang lebih cepat."
    },
    {
        "keywords": ["tidak sesuai", "berbeda", "beda", "foto", "deskripsi", "palsu", "asli", "tipu", "menipu"],
        "kategori": "Akurasi Informasi Produk",
        "rekomendasi": "Perbarui foto dan deskripsi produk agar lebih akurat dan mencerminkan kondisi nyata produk, termasuk ukuran, warna, material, dan detail lainnya."
    },
    {
        "keywords": ["respon", "balas", "slow", "lambat respon", "tidak responsif", "diam", "tidak dibalas"],
        "kategori": "Layanan Pelanggan",
        "rekomendasi": "Tetapkan standar waktu respons maksimal satu jam pada jam operasional toko dan pastikan ada petugas yang memantau pesan masuk secara aktif."
    },
    {
        "keywords": ["mahal", "harga", "kemahalan", "tidak worth", "kemurahan", "murah", "tidak sesuai harga"],
        "kategori": "Harga Produk",
        "rekomendasi": "Evaluasi strategi penetapan harga produk dan pertimbangkan program diskon atau bundling agar konsumen merasa harga yang dibayarkan sesuai dengan nilai produk."
    },
    {
        "keywords": ["kecil", "besar", "tidak pas", "ukuran", "size", "salah ukuran", "kebesaran", "kekecilan"],
        "kategori": "Ketepatan Ukuran",
        "rekomendasi": "Tambahkan panduan ukuran yang lebih detail dan akurat pada halaman produk, termasuk tabel ukuran dan tips pemilihan ukuran yang tepat."
    },
    {
        "keywords": ["bau", "aroma", "wangi", "tidak wangi", "busuk", "apek"],
        "kategori": "Kualitas Aroma/Bahan",
        "rekomendasi": "Periksa kembali proses penyimpanan dan pengemasan produk untuk memastikan kualitas aroma dan bahan tetap terjaga hingga sampai ke tangan konsumen."
    },
    {
        "keywords": ["salah", "keliru", "item", "produk salah", "bukan", "tidak sama"],
        "kategori": "Kesalahan Pengiriman",
        "rekomendasi": "Perkuat sistem pengecekan produk sebelum pengiriman dengan menerapkan prosedur verifikasi berlapis untuk memastikan produk yang dikirim sesuai pesanan."
    },
]

DEFAULT_REKOMENDASI = {
    "kategori": "Evaluasi Umum",
    "rekomendasi": "Lakukan evaluasi menyeluruh terhadap aspek produk dan layanan berdasarkan ulasan pelanggan yang ada. Pertimbangkan untuk melakukan survei kepuasan pelanggan secara berkala."
}


def get_rekomendasi(text):
    """
    Menghasilkan rekomendasi perbaikan berdasarkan kata kunci
    yang terdeteksi dalam teks ulasan negatif.

    Args:
        text (str): Teks ulasan yang sudah dipreprocess
    Returns:
        list: Daftar dict berisi kategori dan rekomendasi yang cocok
    """
    if not text or text.strip() == '':
        return [DEFAULT_REKOMENDASI]

    hasil = []
    text_lower = text.lower()
    kategori_sudah_ada = set()

    for rule in RULE_TABLE:
        for keyword in rule["keywords"]:
            if keyword in text_lower:
                if rule["kategori"] not in kategori_sudah_ada:
                    hasil.append({
                        "keyword_terdeteksi": keyword,
                        "kategori": rule["kategori"],
                        "rekomendasi": rule["rekomendasi"]
                    })
                    kategori_sudah_ada.add(rule["kategori"])
                break  # Satu keyword per rule sudah cukup

    if not hasil:
        return [{"keyword_terdeteksi": "-", **DEFAULT_REKOMENDASI}]

    return hasil


def get_rekomendasi_batch(texts_negatif):
    """
    Menghasilkan rekomendasi dari banyak ulasan negatif sekaligus
    dengan menggabungkan dan mendeduplikasi hasilnya.

    Args:
        texts_negatif (list): Daftar teks ulasan bersentimen negatif
    Returns:
        list: Daftar rekomendasi unik yang teridentifikasi
    """
    semua_rekomendasi = {}

    for text in texts_negatif:
        hasil = get_rekomendasi(text)
        for item in hasil:
            kategori = item["kategori"]
            if kategori not in semua_rekomendasi:
                semua_rekomendasi[kategori] = item

    return list(semua_rekomendasi.values())
