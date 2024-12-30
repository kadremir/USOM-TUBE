# Security Analysis Tool - Complete Documentation
# Güvenlik Analizi Aracı - Kapsamlı Dokümantasyon

## English

### 1. Overview
This tool is designed to analyze security trends by combining data from two sources:
- USOM (National Computer Emergency Response Team of Türkiye)
- Security-related YouTube content

The tool creates visualizations and identifies correlations between official security incidents and public discussions.

### 2. Prerequisites
```python
# Required Libraries
pandas
networkx
wordcloud
matplotlib
youtube_transcript_api
google-api-python-client
requests
nltk
ollama
tqdm
```

### 3. Key Components

#### 3.1 Data Collection
1. **USOM Data Collection (`usom_veri_cek`)**
   - Fetches vulnerability data from USOM API
   - Requires date range input
   - Handles pagination automatically
   - Collects: titles, descriptions, dates, categories, severity levels

2. **YouTube Data Collection (`youtube_veri_cek`)**
   - Requires YouTube API key
   - Collects security-related videos
   - Extracts: titles, descriptions, transcripts
   - Filters out short videos (<60 seconds)
   - Supports both Turkish and English transcripts

#### 3.2 Data Processing
1. **Text Cleaning (`metin_temizle`)**
   - Removes stopwords in both Turkish and English
   - Performs basic text normalization
   - Filters short words

2. **Data Analysis (`veri_analiz`)**
   - Processes both USOM and YouTube data
   - Creates word lists for analysis
   - Handles missing data gracefully

#### 3.3 Visualization (`gorselleştir`)
- Creates word clouds showing frequency of terms
- Generates relationship networks between terms
- Saves visualizations as PNG files
- Uses matplotlib for rendering

### 4. Usage Instructions

1. **Initial Setup**
```bash
# Install required libraries
pip install -r requirements.txt

# Download NLTK data
python -m nltk.downloader punkt stopwords
```

2. **Running the Tool**
```bash
python security_analysis.py
```

3. **Input Requirements**
- USOM date range (YYYY-MM-DD format)
- YouTube search queries
- Maximum number of videos to analyze

4. **Output Files**
- Word cloud visualizations
- Network graphs
- CSV files with raw data
- Timestamp-based file naming

## Türkçe

### 1. Genel Bakış
Bu araç, iki kaynaktan gelen verileri birleştirerek güvenlik trendlerini analiz eder:
- USOM (Ulusal Siber Olaylara Müdahale Merkezi)
- Güvenlikle ilgili YouTube içeriği

Araç, resmi güvenlik olayları ile kamuoyu tartışmaları arasındaki korelasyonları tespit eder ve görselleştirir.

### 2. Ön Gereksinimler
```python
# Gerekli Kütüphaneler
pandas
networkx
wordcloud
matplotlib
youtube_transcript_api
google-api-python-client
requests
nltk
ollama
tqdm
```

### 3. Temel Bileşenler

#### 3.1 Veri Toplama
1. **USOM Veri Toplama (`usom_veri_cek`)**
   - USOM API'sinden zafiyet verilerini çeker
   - Tarih aralığı girişi gerektirir
   - Sayfalamayı otomatik yönetir
   - Topladığı veriler: başlıklar, açıklamalar, tarihler, kategoriler, seviyeler

2. **YouTube Veri Toplama (`youtube_veri_cek`)**
   - YouTube API anahtarı gerektirir
   - Güvenlikle ilgili videoları toplar
   - Çıkarılan veriler: başlıklar, açıklamalar, transkriptler
   - Kısa videoları filtreler (<60 saniye)
   - Türkçe ve İngilizce transkriptleri destekler

#### 3.2 Veri İşleme
1. **Metin Temizleme (`metin_temizle`)**
   - Türkçe ve İngilizce gereksiz kelimeleri temizler
   - Temel metin normalizasyonu yapar
   - Kısa kelimeleri filtreler

2. **Veri Analizi (`veri_analiz`)**
   - USOM ve YouTube verilerini işler
   - Analiz için kelime listeleri oluşturur
   - Eksik verileri uygun şekilde yönetir

#### 3.3 Görselleştirme (`gorselleştir`)
- Terimlerin sıklığını gösteren kelime bulutları oluşturur
- Terimler arası ilişki ağları oluşturur
- Görselleştirmeleri PNG dosyaları olarak kaydeder
- Görüntüleme için matplotlib kullanır

### 4. Kullanım Talimatları

1. **İlk Kurulum**
```bash
# Gerekli kütüphaneleri kur
pip install -r requirements.txt

# NLTK verilerini indir
python -m nltk.downloader punkt stopwords
```

2. **Aracı Çalıştırma**
```bash
python security_analysis.py
```

3. **Girdi Gereksinimleri**
- USOM tarih aralığı (YYYY-MM-DD formatında)
- YouTube arama sorguları
- Analiz edilecek maksimum video sayısı

4. **Çıktı Dosyaları**
- Kelime bulutu görselleştirmeleri
- Ağ grafikleri
- Ham veri içeren CSV dosyaları
- Zaman damgalı dosya isimlendirme

### 5. Örnek Kullanım

```bash
# Program başlatıldığında:
USOM verileri çekiliyor...
Başlangıç tarihini girin: 2024-01-01
Bitiş tarihini girin: 2024-01-31

YouTube'da aranacak güvenlik konularını giriniz.
Sorgu giriniz: siber güvenlik
Sorgu giriniz: veri sızıntısı
Sorgu giriniz: (Enter tuşuna basarak bitirin)

Çekilecek maksimum video sayısını girin: 10
```

### 6. Hata Yönetimi
- Geçersiz tarih formatları için kullanıcıya uyarı
- API bağlantı hataları için geri bildirim
- Eksik veya hatalı veriler için uygun işleme
- Program çökmesini engelleyen try-except blokları
