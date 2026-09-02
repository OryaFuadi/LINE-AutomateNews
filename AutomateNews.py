import os
import requests
from google import genai
from langchain_community.tools import DuckDuckGoSearchRun

# Mengambil kredensial secara aman dari GitHub Secrets
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
LINE_TOKEN = os.environ.get("LINE_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")

client = genai.Client(api_key=GOOGLE_API_KEY)

print("🤖 AI sedang mencari berita di internet...")
search = DuckDuckGoSearchRun()
hasil_pencarian = search.run("Perkembangan AI minggu ini")

print("🧠 AI sedang merangkum berita...")
prompt = f"""
Berdasarkan informasi berita berikut, buatlah ringkasan dalam 3 poin singkat menggunakan bahasa yang santai dan mudah dibaca:

{hasil_pencarian}
"""

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt,
)
hasil_rangkuman = response.text

def kirim_ke_line(pesan):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    payload = {
        "to": LINE_USER_ID,
        "messages": [{"type": "text", "text": pesan}]
    }
    
    kirim = requests.post(url, headers=headers, json=payload)
    if kirim.status_code == 200:
        print("\n✅ SUKSES! Pesan terkirim ke LINE Anda.")
    else:
        print(f"\n❌ Gagal mengirim pesan. Error: {kirim.text}")

kirim_ke_line(hasil_rangkuman)
