# Diş Kliniği Veri Analiz Panosu

Interaktif Dash tabanlı bir pano ile `veri.csv` içindeki klinik ön kayıtlarını görselleştirip istatistiklendirir.

## Özellikler
- Tarih, hizmet türü ve kaynak bazlı filtreler
- Özet kartlar (toplam kayıt, farklı hizmet sayısı, ortalama yaş)
- Grafikler: hizmet dağılımı (bar), kaynak (pie), günlük trend (line), yaş dağılımı (hist)
- Tanımlayıcı istatistik tablosu ve korelasyon ısı haritası
- Filtrelenmiş veriyi CSV olarak indirme

## Kurulum
```bash
python -m venv venv
./venv/Scripts/Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
```

## Çalıştırma
```bash
python app.py
```
Ardından tarayıcıdan: `http://127.0.0.1:8050`

Alternatif tek tuş: `run.bat`

## Veri
`veri.csv` örnek veri içerir. Sütunlar: `Kayit_ID, Tarih, Hizmet_Turu, Hasta_Yasi, Kaynak`.

## Lisans
Bu proje örnek amaçlıdır.
