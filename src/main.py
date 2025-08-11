import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import json

# ===== 1. Setup Credentials =====
# Ambil credential dari GitHub Secrets (disimpan di variabel GCP_SERVICE_ACCOUNT)
service_account_info = json.loads(os.environ["GCP_SERVICE_ACCOUNT"])
SCOPES = [
    'https://www.googleapis.com/auth/webmasters.readonly',
]

creds = service_account.Credentials.from_service_account_info(
    service_account_info, scopes=SCOPES
)

# ===== 2. Ambil Data GSC =====
service = build('searchconsole', 'v1', credentials=creds)
site_url = 'https://flashcomindonesia.com/'  # Website target

request = {
    'startDate': '2024-03-22',
    'endDate': '2025-08-11',
    'dimensions': ['date', 'page', 'query'],  # tambahkan 'date'
    'rowLimit': 6000
}
response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()

rows = response.get('rows', [])
df = pd.DataFrame([{
    'Date': r['keys'][0],           # indeks 0 = date
    'Page': r['keys'][1],           # indeks 1 = page
    'Query': r['keys'][2],          # indeks 2 = query
    'Clicks': r['clicks'],
    'Impressions': r['impressions'],
    'CTR': r['ctr'],
    'Position': r['position']
} for r in rows])

# ===== 3. Generate Insight =====
insight_data = []
for _, row in df.iterrows():
    # Strategy
    if row['CTR'] > 0.05 and row['Position'] <= 10:
        strategy = ("Strategi SEO sudah optimal, tidak perlu perbaikan", "Mudah", "✅")
    elif row['CTR'] < 0.02 and row['Position'] <= 20:
        strategy = ("Perlu meningkatkan strategi SEO untuk menaikkan CTR", "Sedang", "⚠️")
    else:
        strategy = ("Pantau terus performa SEO secara berkala", "Sedang", "ℹ️")

    # SERP Features
    if row['Position'] <= 10 and row['CTR'] < 0.04:
        serp = ("Coba optimalkan untuk mendapatkan featured snippets", "Sedang", "💡")
    else:
        serp = ("Tidak perlu tindakan untuk SERP features", "Mudah", "✅")

    # Content
    if row['Impressions'] > 1000 and row['Clicks'] < 50:
        content = ("Fokus membuat konten yang lebih informatif dan relevan", "Sedang", "📄")
    else:
        content = ("Performa konten sudah baik", "Mudah", "✅")

    insight_data.extend([
        [row['Page'], row['Query'], "Strategi", strategy[0], strategy[1], strategy[2]],
        [row['Page'], row['Query'], "Fitur SERP", serp[0], serp[1], serp[2]],
        [row['Page'], row['Query'], "Konten", content[0], content[1], content[2]],
    ])

df_insight = pd.DataFrame(insight_data, columns=["Halaman", "Kueri", "Kategori", "Rekomendasi", "Tingkat Kesulitan", "Status"])

# ===== 4. Simpan CSV =====
df.to_csv("gsc_data.csv", index=False)
df_insight.to_csv("gsc_insights.csv", index=False)
print("✅ Data dan insight berhasil disimpan sebagai CSV lokal.")
