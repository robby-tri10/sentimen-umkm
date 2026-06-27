# verify_api.py
import urllib.request
import json
import uuid

BASE_URL = "http://127.0.0.1:5000"

def post_json(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as response:
        return response.status, json.loads(response.read().decode('utf-8'))

def post_multipart(url, filename, content, algo="svm"):
    boundary = uuid.uuid4().hex
    headers = {'Content-Type': f'multipart/form-data; boundary={boundary}'}
    
    body = []
    # File field
    body.append(f'--{boundary}'.encode('utf-8'))
    body.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode('utf-8'))
    body.append(b'Content-Type: text/csv')
    body.append(b'')
    body.append(content.encode('utf-8'))
    
    # Algo field
    body.append(f'--{boundary}'.encode('utf-8'))
    body.append(f'Content-Disposition: form-data; name="algo"'.encode('utf-8'))
    body.append(b'')
    body.append(algo.encode('utf-8'))
    
    body.append(f'--{boundary}--'.encode('utf-8'))
    body.append(b'')
    
    body_bytes = b'\r\n'.join(body)
    
    req = urllib.request.Request(url, data=body_bytes, headers=headers)
    with urllib.request.urlopen(req) as response:
        return response.status, json.loads(response.read().decode('utf-8'))

def test_predict_teks_selection():
    print("Testing single review algorithm selection...")
    
    # Test with SVM
    payload_svm = {
        "teks": "Kualitas produk agak buruk, jahitannya retak dan lepas pas pertama dibuka. Pengirimannya lambat banget, telat seminggu.",
        "algo": "svm"
    }
    status_svm, data_svm = post_json(f"{BASE_URL}/api/predict-teks", payload_svm)
    print(f"Status SVM: {status_svm}")
    assert "selected_algo" in data_svm
    assert data_svm["selected_algo"] == "svm"
    assert "naive_bayes" in data_svm
    assert "svm" in data_svm
    
    # Test with NB
    payload_nb = {
        "teks": "Kualitas produk agak buruk, jahitannya retak dan lepas pas pertama dibuka. Pengirimannya lambat banget, telat seminggu.",
        "algo": "nb"
    }
    status_nb, data_nb = post_json(f"{BASE_URL}/api/predict-teks", payload_nb)
    print(f"Status NB: {status_nb}")
    assert "selected_algo" in data_nb
    assert data_nb["selected_algo"] == "nb"
    
    print("[OK] Single review algorithm selection test passed.")

def test_predict_csv_selection():
    print("\nTesting batch CSV algorithm selection...")
    csv_content = """ulasan
"Pengiriman super cepat dan seller responsif banget, suka belanja di sini."
"Kualitas jahitannya jelek sekali dan robek pas pertama dipakai, kecewa berat."
"Barang ukurannya agak kekecilan di badan saya tapi lumayan adem."
"""
    # Test with SVM
    status_svm, data_svm = post_multipart(f"{BASE_URL}/api/predict-csv", "test_reviews.csv", csv_content, algo="svm")
    print(f"Status SVM CSV: {status_svm}")
    assert "selected_algo" in data_svm
    assert data_svm["selected_algo"] == "svm"
    assert "distribusi_nb" in data_svm
    assert "distribusi_svm" in data_svm
    
    # Test with NB
    status_nb, data_nb = post_multipart(f"{BASE_URL}/api/predict-csv", "test_reviews.csv", csv_content, algo="nb")
    print(f"Status NB CSV: {status_nb}")
    assert "selected_algo" in data_nb
    assert data_nb["selected_algo"] == "nb"
    
    print("[OK] Batch CSV algorithm selection test passed.")

if __name__ == "__main__":
    try:
        test_predict_teks_selection()
        test_predict_csv_selection()
        print("\n==============================")
        print("ALL ALGORITHM SELECTION API TESTS PASSED SUCCESSFULLY!")
        print("==============================")
    except Exception as e:
        print("\n[ERROR] Verification failed:")
        import traceback
        traceback.print_exc()
