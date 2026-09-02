import os
import time
import requests
from google import genai
from ddgs import DDGS # 👈 Sudah diperbarui agar tidak muncul warning lagi

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

with DDGS() as ddgs:
    hasil_news = list(ddgs.news("Perkembangan AI teknologi terbaru", max_results=7))
    
    for i, berita in enumerate(hasil_news):
        berita_mentah += f"{i+1}. Judul: {berita.get('title')}\nIsi: {berita.get('body')}\n\n"
        if not gambar_utama and berita.get('image') and berita.get('image').startswith('https'):
            gambar_utama = berita.get('image')

# ==========================================
# 3. SURUH GEMINI MERANGKUMNYA (DENGAN SISTEM COBA LAGI)
# ==========================================
print("🧠 AI sedang merangkum berita yang lebih banyak...")
prompt = f"""
Berdasarkan kumpulan berita terbaru berikut, buatlah ringkasan yang komprehensif berisi 5 hingga 7 poin utama.
Gunakan bahasa yang santai, menarik, dan informatif. Berikan sedikit penjelasan pada tiap poinnya.

Kumpulan Berita:
{berita_mentah}
"""

hasil_rangkuman = ""
maksimal_percobaan = 3

# 👈 SISTEM ANTI-GAGAL: Akan mencoba hingga 3 kali jika server sibuk
for percobaan in range(maksimal_percobaan):
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
        hasil_rangkuman = response.text
        print("✅ Rangkuman berhasil dibuat!")
        break  # Jika berhasil, langsung keluar dari perulangan
    except Exception as e:
        print(f"⚠️ Percobaan {percobaan + 1} gagal (Server Google sibuk). Menunggu 15 detik...")
        time.sleep(15) # Tunggu 15 detik sebelum mencoba lagi
else:
    print("❌ Server Google Gemini benar-benar penuh setelah 3 kali percobaan.")
    hasil_rangkuman = "Halo! Maaf, bot berita saat ini belum bisa merangkum karena server Google AI sedang kepenuhan. Nanti saya coba lagi di jadwal berikutnya ya! 🤖"

# ==========================================
# 4. KIRIM TEKS DAN GAMBAR KE LINE
# ==========================================
def kirim_ke_line(pesan, url_gambar):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    
    pesan_array = []
    
    # Hanya kirim gambar jika berhasil merangkum berita (tidak error)
    if url_gambar and "Maaf" not in pesan:
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
