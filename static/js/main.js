// main.js — SentimenUMKM Premium Dashboard

// ============================================================
// INIT
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initDragAndDrop();
    initDashboardTable();
    animateKeywordBars();
});

// ============================================================
// 1. THEME MANAGEMENT
// ============================================================
function initTheme() {
    const btn = document.getElementById('theme-toggle');
    if (!btn) return;
    btn.addEventListener('click', () => {
        const curr = document.documentElement.getAttribute('data-theme') || 'dark';
        const next = curr === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
    });
}

// ============================================================
// 2. TAB SWITCHING
// ============================================================
function switchTab(el, tabName) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    el.classList.add('active');

    const tabTeks = document.getElementById('tab-teks');
    const tabCsv  = document.getElementById('tab-csv');
    if (tabTeks && tabCsv) {
        tabTeks.style.display = tabName === 'teks' ? 'block' : 'none';
        tabCsv.style.display  = tabName === 'csv'  ? 'block' : 'none';
    }

    const hasilTeks = document.getElementById('hasil-teks');
    const hasilCsv  = document.getElementById('hasil-csv');
    if (hasilTeks) hasilTeks.style.display = 'none';
    if (hasilCsv)  hasilCsv.style.display  = 'none';
}

// ============================================================
// 3. QUICK EXAMPLE TEXTS
// ============================================================
const CONTOH_TEKS = {
    positif: 'Barangnya bagus sekali, kualitas premium! Bahan tebal dan awet dipakai. Pengiriman super cepat dan penjual sangat ramah dalam melayani.',
    negatif: 'Kualitas produk agak buruk, jahitannya retak dan lepas pas pertama dibuka. Pengirimannya lambat banget, telat seminggu dari estimasi yang diberikan.',
    netral:  'Barang ukurannya pas di badan saya, bahannya lumayan adem. Tapi respon chat seller agak lambat balasnya, perlu ditingkatkan.'
};

function isiContohTeks(sentiment) {
    const ta = document.getElementById('input-teks');
    if (ta && CONTOH_TEKS[sentiment]) {
        ta.value = CONTOH_TEKS[sentiment];
        ta.focus();
    }
}

// ============================================================
// 4. RADIAL PROGRESS SVG ANIMATION
// ============================================================
function setRadialProgress(circleId, pctTextId, pct, color) {
    const circle = document.getElementById(circleId);
    const pctEl  = document.getElementById(pctTextId);
    if (!circle || !pctEl) return;

    const circumference = 2 * Math.PI * 46; // r=46 → ~289
    const offset = circumference - (pct / 100) * circumference;

    // Animate with rAF
    let start = null;
    const startOffset = circumference;

    function animate(ts) {
        if (!start) start = ts;
        const progress = Math.min((ts - start) / 900, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        const currentOffset = startOffset - eased * (startOffset - offset);
        circle.style.strokeDashoffset = currentOffset;

        const currentPct = Math.round(eased * pct);
        pctEl.textContent = currentPct + '%';

        if (progress < 1) requestAnimationFrame(animate);
    }
    requestAnimationFrame(animate);
}

// Badge class helper
function getBadgeClass(label_id) {
    return { positif: 'badge-positif', negatif: 'badge-negatif', netral: 'badge-netral' }[label_id] || '';
}

// ============================================================
// 5. NEGATIVE KEYWORD HIGHLIGHTING
// ============================================================
const KEYWORDS_NEGATIF = [
    'rusak','cacat','penyok','pecah','hancur','patah','retak','bengkok',
    'lambat','lama','telat','terlambat','lelet',
    'tidak sesuai','berbeda','beda','palsu','tipu','menipu',
    'respon','balas','diam',
    'mahal','kemahalan',
    'kecil','besar','ukuran','kebesaran','kekecilan',
    'bau','busuk','apek',
    'salah','keliru','bukan','jelek','robek','kecewa','buruk','lecet'
];

function highlightNegativeKeywords(text) {
    if (!text) return '';
    const words = text.split(/(\s+)/);
    return words.map(word => {
        const clean = word.toLowerCase().replace(/[.,/#!$%^&*;:{}=\-_`~()]/g, '').trim();
        if (clean && KEYWORDS_NEGATIF.some(kw => clean.includes(kw) || kw.includes(clean))) {
            return `<span class="highlight-keyword">${word}</span>`;
        }
        return word;
    }).join('');
}

// ============================================================
// 6. SINGLE TEXT ANALYSIS
// ============================================================
async function analisTeks() {
    const teksInput = document.getElementById('input-teks');
    if (!teksInput) return;

    const teks = teksInput.value.trim();
    if (!teks) { alert('Masukkan ulasan terlebih dahulu.'); return; }

    const selectedAlgo = document.getElementById('selected-algo')?.value || 'svm';

    showLoading();
    const hasilTeks = document.getElementById('hasil-teks');
    if (hasilTeks) hasilTeks.style.display = 'none';

    try {
        const resp = await fetch('/api/predict-teks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ teks, algo: selectedAlgo })
        });
        const data = await resp.json();
        hideLoading();

        if (data.error) { alert('Error: ' + data.error); return; }
        tampilHasilTeks(data);

    } catch (err) {
        hideLoading();
        alert('Koneksi ke server gagal. Pastikan server Flask aktif di port 5000.');
        console.error(err);
    }
}

function tampilHasilTeks(data) {
    const nb  = data.naive_bayes;
    const svm = data.svm;
    const selectedAlgo = data.selected_algo || 'svm';

    // NB Badge & Radial
    const nbBadge = document.getElementById('nb-badge');
    if (nbBadge) {
        nbBadge.textContent  = nb.label_tampil;
        nbBadge.className    = `badge ${getBadgeClass(nb.label_id)}`;
    }
    setRadialProgress('nb-circle', 'nb-pct', nb.keyakinan, '#818cf8');
    const nbConf = document.getElementById('nb-conf');
    if (nbConf) nbConf.textContent = `Tingkat keyakinan model: ${nb.keyakinan}%`;

    // SVM Badge & Radial
    const svmBadge = document.getElementById('svm-badge');
    if (svmBadge) {
        svmBadge.textContent = svm.label_tampil;
        svmBadge.className   = `badge ${getBadgeClass(svm.label_id)}`;
    }
    setRadialProgress('svm-circle', 'svm-pct', svm.keyakinan, 'url(#svmGrad)');
    const svmConf = document.getElementById('svm-conf');
    if (svmConf) svmConf.textContent = `Tingkat keyakinan model: ${svm.keyakinan}%`;

    // Highlight selected model card as Model Utama
    const cardNb = document.getElementById('card-nb');
    const cardSvm = document.getElementById('card-svm');
    if (cardNb && cardSvm) {
        cardNb.classList.remove('winner');
        cardSvm.classList.remove('winner');
        
        // Remove existing best-tag
        const oldTags = document.querySelectorAll('.compare-head .best-tag');
        oldTags.forEach(tag => tag.remove());

        if (selectedAlgo === 'nb') {
            cardNb.classList.add('winner');
            const head = cardNb.querySelector('.compare-head');
            if (head) head.insertAdjacentHTML('beforeend', '<span class="best-tag">Model Utama</span>');
        } else {
            cardSvm.classList.add('winner');
            const head = cardSvm.querySelector('.compare-head');
            if (head) head.insertAdjacentHTML('beforeend', '<span class="best-tag">Model Utama</span>');
        }
    }

    // Highlighted clean text
    const highlightWrapper = document.getElementById('highlight-wrapper');
    const highlightedPara  = document.getElementById('clean-text-highlighted');
    if (highlightWrapper && highlightedPara && data.teks_bersih) {
        highlightedPara.innerHTML     = highlightNegativeKeywords(data.teks_bersih);
        highlightWrapper.style.display = 'block';
    } else if (highlightWrapper) {
        highlightWrapper.style.display = 'none';
    }

    // Recommendations
    const rekoSection = document.getElementById('reko-section');
    const rekoList    = document.getElementById('reko-list');
    if (rekoSection && rekoList) {
        const selectedModel = selectedAlgo === 'nb' ? nb : svm;
        if (selectedModel.label_id === 'negatif' && data.rekomendasi && data.rekomendasi.length > 0) {
            rekoList.innerHTML = data.rekomendasi.map(r => `
                <div class="reko-card">
                    <div class="reko-header" onclick="toggleRekoCard(this)">
                        <div class="reko-header-left">
                            <span class="reko-keyword-badge">Kata Kunci: "${r.keyword_terdeteksi}"</span>
                            <span class="reko-title">${r.kategori}</span>
                        </div>
                        <span class="reko-arrow">▼</span>
                    </div>
                    <div class="reko-content">
                        <div class="reko-body">
                            <div style="display:flex; gap:12px; align-items:flex-start; background:var(--bg-card); padding:14px; border-radius:9px; border-left:3px solid var(--danger);">
                                <span style="font-size:18px; line-height:1; flex-shrink:0;">🎯</span>
                                <div>
                                    <div style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:var(--text-muted); margin-bottom:5px;">Tindakan Perbaikan</div>
                                    <p style="font-size:13px; color:var(--text-primary); line-height:1.65; margin:0;">${r.rekomendasi}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
            rekoSection.style.display = 'block';
        } else {
            rekoSection.style.display = 'none';
        }
    }

    // Show results
    const hasilTeks = document.getElementById('hasil-teks');
    if (hasilTeks) {
        hasilTeks.style.display = 'block';
        setTimeout(() => hasilTeks.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 50);
    }
}

function resetTeks() {
    const ta = document.getElementById('input-teks');
    if (ta) ta.value = '';
    const hasilTeks = document.getElementById('hasil-teks');
    if (hasilTeks) hasilTeks.style.display = 'none';
}

// ============================================================
// 7. CSV DRAG & DROP + PREVIEW
// ============================================================
let selectedFile = null;

function initDragAndDrop() {
    const box = document.getElementById('upload-box');
    if (!box) return;

    box.addEventListener('click', () => document.getElementById('file-input').click());

    ['dragenter', 'dragover'].forEach(ev => {
        box.addEventListener(ev, e => { e.preventDefault(); e.stopPropagation(); box.classList.add('dragover'); }, false);
    });
    ['dragleave', 'drop'].forEach(ev => {
        box.addEventListener(ev, e => { e.preventDefault(); e.stopPropagation(); box.classList.remove('dragover'); }, false);
    });

    box.addEventListener('drop', e => {
        const files = e.dataTransfer.files;
        if (files.length > 0) handleFileSelect({ files });
    }, false);
}

function handleFileSelect(input) {
    const file = input.files[0];
    if (!file) return;
    if (!file.name.endsWith('.csv')) { alert('File harus berformat .csv'); return; }

    selectedFile = file;

    const fileInfo = document.getElementById('file-info');
    if (fileInfo) {
        fileInfo.innerHTML = `✓ File terpilih: <strong>${file.name}</strong> (${(file.size / 1024).toFixed(1)} KB)`;
        fileInfo.style.display = 'block';
    }

    const btnUpload = document.getElementById('btn-upload');
    if (btnUpload) btnUpload.disabled = false;

    const hint = document.getElementById('csv-upload-hint');
    if (hint) hint.style.display = 'none';

    previewCsvData(file);
}

function previewCsvData(file) {
    const reader = new FileReader();
    reader.onload = e => {
        const lines   = e.target.result.split('\n').map(l => l.trim()).filter(l => l);
        if (!lines.length) return;

        const headers = lines[0].split(',');
        const rows    = lines.slice(1, 4).map(row => row.split(','));

        const previewArea   = document.getElementById('csv-preview-area');
        const headerRow     = document.getElementById('preview-headers');
        const rowsContainer = document.getElementById('preview-rows');

        if (previewArea && headerRow && rowsContainer) {
            headerRow.innerHTML     = headers.map(h => `<th>${h}</th>`).join('');
            rowsContainer.innerHTML = rows.map(row =>
                `<tr>${row.map(v => `<td>${v.replace(/^"|"$/g, '')}</td>`).join('')}</tr>`
            ).join('');
            previewArea.style.display = 'block';
        }
    };
    reader.readAsText(file);
}

async function uploadCSV() {
    if (!selectedFile) { alert('Pilih file CSV terlebih dahulu.'); return; }

    showLoading();
    const hasilCsv = document.getElementById('hasil-csv');
    if (hasilCsv) hasilCsv.style.display = 'none';

    const selectedAlgo = document.getElementById('selected-algo')?.value || 'svm';

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('algo', selectedAlgo);

    try {
        const resp = await fetch('/api/predict-csv', { method: 'POST', body: formData });
        const data = await resp.json();
        hideLoading();

        if (data.error) { alert('Error: ' + data.error); return; }

        if (data.detail_ulasan) {
            sessionStorage.setItem('detail_ulasan', JSON.stringify(data.detail_ulasan));
        }
        tampilHasilCSV(data);

    } catch (err) {
        hideLoading();
        alert('Kesalahan koneksi saat mengunggah file.');
        console.error(err);
    }
}

function tampilHasilCSV(data) {
    const nb = data.distribusi_nb;
    const svm = data.distribusi_svm;
    const selectedAlgo = data.selected_algo || 'svm';

    // Update NB values
    const nbPos = document.getElementById('csv-nb-pos');
    const nbNeg = document.getElementById('csv-nb-neg');
    const nbNet = document.getElementById('csv-nb-net');
    const nbTotal = nb.total;
    const pctNb = n => nbTotal > 0 ? ((n / nbTotal) * 100).toFixed(1) : 0;
    if (nbPos) nbPos.textContent = `${nb.positif} (${pctNb(nb.positif)}%)`;
    if (nbNeg) nbNeg.textContent = `${nb.negatif} (${pctNb(nb.negatif)}%)`;
    if (nbNet) nbNet.textContent = `${nb.netral} (${pctNb(nb.netral)}%)`;

    // Update SVM values
    const svmPos = document.getElementById('csv-svm-pos');
    const svmNeg = document.getElementById('csv-svm-neg');
    const svmNet = document.getElementById('csv-svm-net');
    const svmTotal = svm.total;
    const pctSvm = n => svmTotal > 0 ? ((n / svmTotal) * 100).toFixed(1) : 0;
    if (svmPos) svmPos.textContent = `${svm.positif} (${pctSvm(svm.positif)}%)`;
    if (svmNeg) svmNeg.textContent = `${svm.negatif} (${pctSvm(svm.negatif)}%)`;
    if (svmNet) svmNet.textContent = `${svm.netral} (${pctSvm(svm.netral)}%)`;

    // Update "Model Utama" badge dynamically
    const nbBadge = document.getElementById('csv-nb-badge');
    const svmBadge = document.getElementById('csv-svm-badge');
    
    if (nbBadge && svmBadge) {
        if (selectedAlgo === 'nb') {
            nbBadge.textContent = 'Model Utama';
            nbBadge.className = 'badge badge-positif';
            nbBadge.style.background = '';
            nbBadge.style.color = '';
            
            svmBadge.textContent = 'Pembanding';
            svmBadge.className = 'badge';
            svmBadge.style.background = 'var(--bg-input)';
            svmBadge.style.color = 'var(--text-secondary)';
        } else {
            nbBadge.textContent = 'Baseline';
            nbBadge.className = 'badge';
            nbBadge.style.background = 'rgba(59, 130, 246, 0.1)';
            nbBadge.style.color = 'var(--accent)';
            
            svmBadge.textContent = 'Model Utama';
            svmBadge.className = 'badge badge-positif';
            svmBadge.style.background = '';
            svmBadge.style.color = '';
        }
    }

    // Save selected algo to sessionStorage
    sessionStorage.setItem('selected_algo', selectedAlgo);

    const hasilCsv = document.getElementById('hasil-csv');
    if (hasilCsv) {
        hasilCsv.style.display = 'block';
        setTimeout(() => hasilCsv.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 50);
    }
}

function resetCSV() {
    selectedFile = null;
    const fi = document.getElementById('file-input');
    if (fi) fi.value = '';
    ['file-info','csv-preview-area','hasil-csv'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = 'none';
    });
    const btn = document.getElementById('btn-upload');
    if (btn) btn.disabled = true;

    const hint = document.getElementById('csv-upload-hint');
    if (hint) hint.style.display = 'block';
}

function toggleCsvGuide() {
    const guide = document.getElementById('csv-guide-panel');
    if (guide) guide.classList.toggle('collapsed');
}

// ============================================================
// 8. DASHBOARD TABLE — SEARCH / FILTER / PAGINATION
// ============================================================
let tableData            = [];
let filteredTableData    = [];
let tableCurrentPage     = 1;
const tablePageSize      = 10;
let activeTableSentiment = 'all';

function initDashboardTable() {
    const tableCard = document.getElementById('detail-ulasan-card');
    if (!tableCard) return;

    const cached = sessionStorage.getItem('detail_ulasan');
    if (!cached) { tableCard.style.display = 'none'; return; }

    try {
        tableData         = JSON.parse(cached);
        filteredTableData = [...tableData];
        tableCurrentPage  = 1;
        tableCard.style.display = 'block';
        renderDashboardTable();
    } catch {
        tableCard.style.display = 'none';
    }
}

function renderDashboardTable() {
    const tbody    = document.getElementById('ulasan-table-body');
    const infoText = document.getElementById('pagination-info');
    const btnPrev  = document.getElementById('btn-prev');
    const btnNext  = document.getElementById('btn-next');
    const totalInfo = document.getElementById('table-total-info');
    if (!tbody) return;

    const totalRows  = filteredTableData.length;
    if (totalInfo) totalInfo.textContent = `${totalRows} ulasan ditemukan`;

    if (totalRows === 0) {
        tbody.innerHTML = `<tr><td colspan="3" style="text-align:center; padding:32px; color:var(--text-muted);">Tidak ada ulasan sesuai filter / pencarian.</td></tr>`;
        if (infoText) infoText.textContent = 'Menampilkan 0 dari 0';
        if (btnPrev) btnPrev.disabled = true;
        if (btnNext) btnNext.disabled = true;
        return;
    }

    const totalPages = Math.ceil(totalRows / tablePageSize);
    tableCurrentPage = Math.max(1, Math.min(tableCurrentPage, totalPages));

    const startIdx = (tableCurrentPage - 1) * tablePageSize;
    const endIdx   = Math.min(startIdx + tablePageSize, totalRows);
    const pageData = filteredTableData.slice(startIdx, endIdx);

    tbody.innerHTML = pageData.map(row => `
        <tr>
            <td style="font-size:13px; line-height:1.5;">${row.teks_asli}</td>
            <td style="text-align:center;"><span class="badge ${getBadgeClass(row.label_nb)}">${row.label_nb_tampil}</span></td>
            <td style="text-align:center;"><span class="badge ${getBadgeClass(row.label_svm)}">${row.label_svm_tampil}</span></td>
        </tr>
    `).join('');

    if (infoText) infoText.textContent = `Menampilkan ${startIdx + 1}–${endIdx} dari ${totalRows}`;
    if (btnPrev) btnPrev.disabled = tableCurrentPage === 1;
    if (btnNext) btnNext.disabled = tableCurrentPage === totalPages;
}

function changeTablePage(direction) {
    tableCurrentPage += direction;
    renderDashboardTable();
}

function filterTableSentiment(sentiment, btn) {
    activeTableSentiment = sentiment;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    applyTableFilters();
}

function handleTableSearch() {
    applyTableFilters();
}

function applyTableFilters() {
    const query = (document.getElementById('search-input')?.value || '').toLowerCase().trim();
    const selectedAlgo = sessionStorage.getItem('selected_algo') || 'svm';
    const labelKey = selectedAlgo === 'nb' ? 'label_nb' : 'label_svm';
    filteredTableData = tableData.filter(row => {
        const matchSentiment = activeTableSentiment === 'all' || row[labelKey] === activeTableSentiment;
        const matchQuery     = !query || row.teks_asli.toLowerCase().includes(query);
        return matchSentiment && matchQuery;
    });
    tableCurrentPage = 1;
    renderDashboardTable();
}

// ============================================================
// 9. REKOMENDASI ACCORDION + FILTER + DOWNLOAD
// ============================================================
function toggleRekoCard(el) {
    const card    = el.closest('.reko-card');
    const content = card.querySelector('.reko-content');
    if (card.classList.contains('active')) {
        content.style.maxHeight = '0px';
        card.classList.remove('active');
    } else {
        content.style.maxHeight = content.scrollHeight + 'px';
        card.classList.add('active');
    }
}

function filterRekoCategory(category, badge) {
    document.querySelectorAll('.reko-filter-tag').forEach(t => t.classList.remove('active-reko-filter'));
    badge.classList.add('active-reko-filter');

    document.querySelectorAll('#reko-container .reko-card').forEach(card => {
        const cat = card.getAttribute('data-category');
        card.style.display = (category === 'all' || cat === category) ? 'block' : 'none';
    });
}

function unduhLaporanRekomendasi() {
    const cards = document.querySelectorAll('#reko-container .reko-card');
    if (!cards.length) return;

    let content  = '========================================================\n';
    content     += '       LAPORAN REKOMENDASI PERBAIKAN UMKM              \n';
    content     += '========================================================\n';
    content     += `Tanggal: ${new Date().toLocaleString('id-ID')}\n\n`;
    content     += 'Dibuat otomatis dari pola ulasan negatif konsumen\n';
    content     += '--------------------------------------------------------\n\n';

    let no = 1;
    cards.forEach(card => {
        if (card.style.display === 'none') return;
        const title   = card.querySelector('.reko-title')?.textContent?.trim()   || '-';
        const keyword = card.querySelector('.reko-keyword-badge')?.textContent?.trim() || '-';
        const desc    = card.querySelector('.reko-body p')?.textContent?.trim()  || '-';
        content += `${no}. KATEGORI : ${title}\n`;
        content += `   ${keyword}\n`;
        content += `   Tindakan  : ${desc}\n`;
        content += `   --------------------------------------------------\n\n`;
        no++;
    });

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const link = document.createElement('a');
    link.href     = URL.createObjectURL(blob);
    link.download = `Laporan_Rekomendasi_UMKM_${new Date().toISOString().slice(0,10)}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ============================================================
// 10. KEYWORD BAR ANIMATION
// ============================================================
function animateKeywordBars() {
    setTimeout(() => {
        document.querySelectorAll('.keyword-bar-fill').forEach(el => {
            el.style.width = el.getAttribute('data-width') || '0%';
        });
    }, 300);
}

// ============================================================
// 11. LOADING HELPERS
// ============================================================
function showLoading() {
    const el = document.getElementById('loading');
    if (el) el.style.display = 'flex';
}

function hideLoading() {
    const el = document.getElementById('loading');
    if (el) el.style.display = 'none';
}
