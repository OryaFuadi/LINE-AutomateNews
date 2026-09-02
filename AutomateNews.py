import os
import requests
from google import genai
from duckduckgo_search import DDGS # Kita gunakan ini langsung untuk mengambil gambar

# ==========================================
# 1. KREDENSIAL & INISIALISASI
# ==========================================
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
LINE_TOKEN = os.environ.get("LINE_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")

client = genai.Client(api_key=GOOGLE_API_KEY)

print("🤖 AI sedang mencari berita dan gambar...")

# ==========================================
# 2. CARI BERITA & GAMBAR DENGAN DUCKDUCKGO
# ==========================================
berita_mentah = ""
gambar_utama = ""

# Mencari berita spesifik (max 7 berita terbaru)
with DDGS() as ddgs:
    hasil_news = list(ddgs.news("Perkembangan AI teknologi terbaru", max_results=7))
    
    for i, berita in enumerate(hasil_news):
        # Kumpulkan teks berita untuk dibaca Gemini
        berita_mentah += f"{i+1}. Judul: {berita.get('title')}\nIsi: {berita.get('body')}\n\n"
        
        # Ambil gambar dari berita pertama yang memiliki link gambar https
        if not gambar_utama and berita.get('image') and berita.get('image').startswith('https'):
            gambar_utama = berita.get('image')

# ==========================================
# 3. SURUH GEMINI MERANGKUMNYA LEBIH PANJANG
# ==========================================
print("🧠 AI sedang merangkum berita yang lebih banyak...")
prompt = f"""
Berdasarkan kumpulan berita terbaru berikut, buatlah ringkasan yang komprehensif berisi 5 hingga 7 poin utama.
Gunakan bahasa yang santai, menarik, dan informatif. Berikan sedikit penjelasan pada tiap poinnya.

Kumpulan Berita:
{berita_mentah}
"""

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt,
)
hasil_rangkuman = response.text

# ==========================================
# 4. KIRIM TEKS DAN GAMBAR KE LINE
# ==========================================
def kirim_ke_line(pesan, url_gambar):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    
    # Kita bisa mengirim maksimal 5 pesan sekaligus di LINE
    # Pesan 1: Gambar (Jika berhasil ditemukan), Pesan 2: Teks Berita
    pesan_array = []
    
    if url_gambar:
        pesan_array.append({
            "type": "image",
            "originalContentUrl": url_gambar,
            "previewImageUrl": url_gambar
        })
        
    pesan_array.append({
        "type": "text",
        "text": pesan
    })
    
    payload = {
        "to": LINE_USER_ID,
        "messages": pesan_array
    }
    
    kirim = requests.post(url, headers=headers, json=payload)
    if kirim.status_code == 200:
        print("\n✅ SUKSES! Gambar dan berita terkirim ke LINE Anda.")
    else:
        print(f"\n❌ Gagal mengirim pesan. Error: {kirim.text}")

kirim_ke_line(hasil_rangkuman, gambar_utama)
