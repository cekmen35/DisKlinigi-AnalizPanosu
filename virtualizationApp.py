import pandas as pd
import plotly.express as px
import dash
from dash import dcc  # Dash Core Components (Grafikler, Menüler vb.)
from dash import html  # Dash HTML Components (HTML etiketleri)

# --- 1. Veri Hazırlama ---

# Veriyi CSV dosyasından yükle
try:
    df = pd.read_csv('veri.csv')
except FileNotFoundError:
    print("HATA: 'veri.csv' dosyası bulunamadı. Lütfen dosyayı oluşturun.")
    exit()

# Tarih sütununu Python'un anlayacağı datetime formatına çevir
df['Tarih'] = pd.to_datetime(df['Tarih'])

# --- 2. Grafikleri Oluşturma (Plotly Express) ---

# Grafik 1: Hizmet Türüne Göre Talep Dağılımı (Çubuk Grafik)
# Hizmet_Turu sütunundaki her bir değeri say ve yeni bir dataframe oluştur
hizmet_sayilari = df['Hizmet_Turu'].value_counts().reset_index()
hizmet_sayilari.columns = ['Hizmet Türü', 'Kayıt Sayısı']  # Sütun adlarını düzelt

fig_bar_hizmet = px.bar(
    hizmet_sayilari,
    x='Hizmet Türü',
    y='Kayıt Sayısı',
    title='Hizmet Türüne Göre Ön Kayıt Dağılımı',
    color='Hizmet Türü'  # Renklendirme
)

# Grafik 2: Kaynağa Göre Talep Dağılımı (Pasta Grafik)
kaynak_sayilari = df['Kaynak'].value_counts().reset_index()
kaynak_sayilari.columns = ['Kaynak', 'Kayıt Sayısı']

fig_pie_kaynak = px.pie(
    kaynak_sayilari,
    names='Kaynak',
    values='Kayıt Sayısı',
    title='Hastaların Bize Ulaştığı Kaynaklar',
    hole=0.3  # Ortasını delikli (donut) yap
)

# Grafik 3: Günlük Kayıt Trendi (Çizgi Grafik)
# Tarihe göre kayıtları grupla ve her gün kaç kayıt olduğunu say
gunluk_kayitlar = df.groupby('Tarih').size().reset_index(name='Günlük Kayıt Sayısı')

fig_line_trend = px.line(
    gunluk_kayitlar,
    x='Tarih',
    y='Günlük Kayıt Sayısı',
    title='Günlük Gelen Ön Kayıt Sayısı Trendi',
    markers=True  # Her noktayı işaretle
)

# --- 3. Dash Pano Tasarımı (Layout) ---

# Dash uygulamasını başlat
app = dash.Dash(__name__)

# Panonun tarayıcıda nasıl görüneceğini HTML bileşenleriyle tanımla
app.layout = html.Div(
    style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#f4f4f4', 'padding': '20px'},
    children=[

        # Ana Başlık
        html.H1(
            children='Diş Kliniği Veri Analiz Panosu',
            style={'textAlign': 'center', 'color': '#333'}
        ),

        # Alt Başlık
        html.Div(
            children='Gelen ön kayıtların interaktif analizi.',
            style={'textAlign': 'center', 'color': '#555', 'marginBottom': '30px'}
        ),

        # Grafikleri Ekleme
        # Çubuk Grafik
        dcc.Graph(
            id='hizmet-grafigi',
            figure=fig_bar_hizmet,
            style={'marginBottom': '20px'}
        ),

        # Pasta Grafik
        dcc.Graph(
            id='kaynak-grafigi',
            figure=fig_pie_kaynak,
            style={'marginBottom': '20px'}
        ),

        # Çizgi Grafik
        dcc.Graph(
            id='trend-grafigi',
            figure=fig_line_trend
        )
    ]
)

# --- 4. Sunucuyu Başlatma ---
if __name__ == '__main__':
    # 'debug=True' modu, kodu her değiştirdiğinizde sunucunun otomatik yenilenmesini sağlar
    # DEĞİŞİKLİK BURADA: 'app.run_server' yerine 'app.run' kullanıyoruz
    app.run(debug=True)