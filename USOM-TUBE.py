import pandas as pd
import networkx as nx
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from matplotlib import rcParams
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from googleapiclient.discovery import build
import requests
import re
from collections import Counter
import nltk
import ollama
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from datetime import datetime
from tqdm import tqdm

# Devanagari karakterlerini destekleyen bir yazı tipi ayarlayın
rcParams['font.family'] = 'Noto Sans Devanagari'

# NLTK verilerini indir
nltk.download('punkt')
nltk.download('stopwords')

def tarih_formatlayici(tarih_str):
    """Farklı formatlardaki tarihleri YYYY-MM-DD formatına çevirir"""
    try:
        for format in ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d']:
            try:
                tarih = datetime.strptime(tarih_str, format)
                return tarih.strftime('%Y-%m-%d')
            except:
                continue
        
        tarih = pd.to_datetime(tarih_str)
        return tarih.strftime('%Y-%m-%d')
    except:
        return None

def usom_veri_cek():
    """USOM verilerini API üzerinden çeker"""
    print("\n============= USOM API Veri Çekme Aracı =============")
    
    api_base = "https://www.usom.gov.tr/api/incident/index"
    
    print("\nTarih Giriş Formatı: YYYY-MM-DD")
    print("Örnek: 2024-01-01 veya 2024-1-1")
    print("-" * 60)
    
    while True:
        baslangic_tarihi = input("\nBaşlangıç tarihini girin: ").strip()
        formatted_date = tarih_formatlayici(baslangic_tarihi)
        if formatted_date:
            baslangic_tarihi = formatted_date
            print(f"Tarih formatlandı: {formatted_date}")
            break
        else:
            print("! Hatalı tarih formatı. Örnek: 2024-01-01 veya 2024-1-1")
    
    while True:
        bitis_tarihi = input("Bitiş tarihini girin: ").strip()
        formatted_date = tarih_formatlayici(bitis_tarihi)
        if formatted_date:
            bitis_tarihi = formatted_date
            if pd.to_datetime(bitis_tarihi) >= pd.to_datetime(baslangic_tarihi):
                print(f"Tarih formatlandı: {formatted_date}")
                break
            else:
                print("! Bitiş tarihi başlangıç tarihinden önce olamaz!")
        else:
            print("! Hatalı tarih formatı. Örnek: 2024-01-01 veya 2024-1-1")
    
    try:
        print("\nZafiyet verileri çekiliyor...")
        zaafiyetler = []
        page = 1
        
        while True:
            params = {
                "page": page,
                "date_gte": baslangic_tarihi,
                "date_lte": bitis_tarihi,
                "language": "tr",
                "url": "https://www.usom.gov.tr/bildirim",  # Eklenen URL parametresi
                "address": "https://www.usom.gov.tr/adres"  # Eklenen adres parametresi
            }
            
            response = requests.get(api_base, params=params)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                yeni_kayitlar = len(models)
                
                if yeni_kayitlar == 0:
                    break
                    
                for item in models:
                    zaafiyetler.append({
                        'baslik': item.get('title', 'Başlık Yok'),
                        'aciklama': item.get('description', 'Açıklama Yok'),
                        'tarih': item.get('date', 'Tarih Yok'),
                        'kaynak': 'USOM API',
                        'kategori': item.get('category', 'Kategori Yok'),
                        'seviye': item.get('level', 'Seviye Yok'),
                        'url': item.get('url', '')
                    })
                
                print(f"Sayfa {page} işlendi. Toplam {len(zaafiyetler)} kayıt bulundu.")
                
                if page >= data.get('pageCount', 1):
                    break
                    
                page += 1
            else:
                print(f"\nAPI Hata Kodu: {response.status_code}")
                break
        
        df = pd.DataFrame(zaafiyetler)
        
        if not df.empty:
            print("\n\nVeri Analizi:")
            print("-" * 60)
            print(f"Toplam Kayıt: {len(df)}")
            print(f"Tarih Aralığı: {df['tarih'].min()} - {df['tarih'].max()}")
            print(f"Benzersiz Kategori Sayısı: {df['kategori'].nunique()}")
            print(f"Benzersiz Seviye Sayısı: {df['seviye'].nunique()}")
            
            return df
        else:
            print("\nHiç veri bulunamadı!")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"\nAPI Hatası: {e}")
        return pd.DataFrame()
    
def ollama_suzme(transcript, search_results):
    """Uses the local Ollama model to filter the transcript, focusing on words outside the search results."""
    url = "YOUR_OLLAMA_API_URL"  # Ollama API URL
    headers = {
        "Content-Type": "application/json"
    }
    
    # Combine search results into a single text
    search_results_text = " ".join(search_results)
    
    # Create the prompt for filtering
    prompt = f"Filter the following text: {transcript}\n\nSearch results: {search_results_text}\n\nPlease filter out only the words that are not in the search results."
    
    data = {
        "model": "mistral:latest",  # Specify the model you want to use
        "prompt": prompt,
        "max_tokens": 1000  # Desired maximum number of tokens
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json().get("text", "")
    else:
        print(f"Ollama API error: {response.status_code}")
        return transcript  # Return the original transcript in case of an error

def youtube_veri_cek():
    """YouTube'dan video başlıkları, ID'leri ve transkriptlerini çeker"""
    api_key = "YOUR_API_KEY"
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    print("\nYouTube'da aranacak güvenlik konularını giriniz.")
    print("Her sorguyu Enter'a basarak girin, bitirmek için boş satır bırakın.\n")
    
    sorgular = []
    while True:
        sorgu = input("Sorgu giriniz (Çıkmak için Enter): ").strip()
        if not sorgu:
            break
        sorgular.append(sorgu)

    while True:
        try:
            max_results = int(input("Çekilecek maksimum video sayısını girin (örneğin 10): "))
            if max_results <= 0:
                print("Lütfen pozitif bir sayı girin.")
            else:
                break
        except ValueError:
            print("Lütfen geçerli bir sayı girin.")
    
    tum_videolar = []
    for sorgu in sorgular:
        try:
            request = youtube.search().list(
                part="snippet",
                q=sorgu,
                type="video",
                order="viewCount",
                maxResults=max_results,
                relevanceLanguage="tr",
            )
            
            response = request.execute()
            
            if 'items' not in response or not response['items']:
                print(f"{sorgu} için sonuç bulunamadı.")
                continue
            
            toplam_videolar = len(response['items'])
            print(f"\n{sorgu} için {toplam_videolar} video bulundu, transkriptler çekiliyor...")
            
            for item in tqdm(response.get("items", []), desc="İşlenen videolar", unit="video"):
                video_id = item['id']['videoId']
                video_info = {
                    'baslik': item['snippet']['title'],
                    'aciklama': item['snippet']['description'],
                    'video_id': video_id,
                    'yayin_tarihi': item['snippet']['publishedAt'],
                    'kanal_adi': item['snippet']['channelTitle']
                }
                
                # Video süresini kontrol et
                video_details = youtube.videos().list(part="contentDetails", id=video_id).execute()
                duration = video_details['items'][0]['contentDetails']['duration']
                
                # Sadece normal videoları al (60 saniyeden uzun)
                if duration.startswith('PT') and 'M' in duration:
                    minutes = int(duration.split('M')[0][2:])  # 'PT1M30S' gibi bir format
                    seconds = int(duration.split('M')[1][:-1]) if 'S' in duration.split('M')[1] else 0
                    total_seconds = minutes * 60 + seconds
                    
                    if total_seconds <= 60:  # 60 saniye veya daha kısa olan videoları atla
                        print(f"Video {video_id} için Shorts videosu, atlanıyor.")
                        continue
                
                # Transkript çekme denemesi
                try:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                    
                    # Önce Türkçe transkript dene
                    try:
                        transcript = transcript_list.find_transcript(['tr'])
                    except NoTranscriptFound:
                        # Türkçe bulunamazsa, İngilizce dene
                        try:
                            transcript = transcript_list.find_transcript(['en'])
                        except NoTranscriptFound:
                            # Hiçbiri bulunamazsa, bu videoyu atla
                            print(f"Video {video_id} için transkript bulunamadı, atlanıyor.")
                            continue
                    
                    # Transkripti metin olarak birleştir
                    video_info['transkript'] = " ".join([entry['text'] for entry in transcript.fetch()])
                    
                except (TranscriptsDisabled, NoTranscriptFound, Exception) as e:
                    video_info['transkript'] = None
                    print(f"Video {video_id} için transkript alınamadı: {str(e)}")
                    continue  # Bu videoyu atla
                
                tum_videolar.append(video_info)
                
        except Exception as e:
            print(f"\nYouTube verisi çekilirken hata: {e}")
            continue
    
    youtube_df = pd.DataFrame(tum_videolar)
    
    if youtube_df.empty:
        print("\nHiç video verisi çekilemedi!")
    else:
        print(f"\nToplam {len(youtube_df)} video verisi çekildi.")
        transkript_sayisi = youtube_df['transkript'].notna().sum()
        print(f"Transkript alınan video sayısı: {transkript_sayisi}")
        print(f"Transkript alınamayan video sayısı: {len(youtube_df) - transkript_sayisi}")
    
    return youtube_df

def metin_temizle(metin):
    """Metni temizler ve stop words'leri kaldırır"""
    stop_words = set(stopwords.words('english') + stopwords.words('turkish'))
    
    metin = re.sub(r'[^\w\s]', ' ', str(metin).lower())
    kelimeler = word_tokenize(metin)
    temiz_kelimeler = [kelime for kelime in kelimeler if kelime not in stop_words and len(kelime) > 2]
    
    return temiz_kelimeler
def veri_analiz(usom_df, youtube_df):
    """USOM ve YouTube verilerini analiz eder"""
    usom_kelimeler = []
    youtube_kelimeler = []
    
    # USOM verilerini işle
    if not usom_df.empty and all(col in usom_df.columns for col in ['baslik', 'aciklama']):
        try:
            metin_birlesik = usom_df['baslik'].fillna('') + ' ' + usom_df['aciklama'].fillna('')
            for metin in metin_birlesik:
                usom_kelimeler.extend(metin_temizle(metin))
        except Exception as e:
            print(f"USOM veri işleme hatası: {e}")
    
    # YouTube verilerini işle
    if not youtube_df.empty:
        if 'baslik' in youtube_df.columns:
            for metin in youtube_df['baslik'].fillna(''):
                youtube_kelimeler.extend(metin_temizle(metin))
        
        if 'transkript' in youtube_df.columns:
            for metin in youtube_df['transkript'].fillna(''):
                youtube_kelimeler.extend(metin_temizle(metin))
    
    return usom_kelimeler, youtube_kelimeler

def gorselleştir(G, kelime_frekanslari, isim, usom_kelimeler, youtube_kelimeler):
    """Ağ ve kelime bulutu görselleştirmesi"""
    if not G.nodes() or not kelime_frekanslari:
        print(f"{isim} için görselleştirme yapılamıyor - veri yok")
        return
    
    try:
        # Matplotlib figürünü oluştur
        plt.figure(figsize=(20,10))
        
        # Kelime bulutu
        plt.subplot(1, 2, 1)
        wordcloud = WordCloud(
            width=1600, 
            height=800,
            background_color='white',
            min_font_size=10,
            max_font_size=150,
            prefer_horizontal=0.7
        ).generate_from_frequencies(dict(kelime_frekanslari))
        
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'{isim} Kelime Bulutu', pad=20)
        
        # Ortak analizde ilişki ağı oluştur
        if isim == "Ortak":
            ortak_kelimeler = set(G.nodes())
            G_ortak = nx.Graph()
            
            for kelime1 in set(usom_kelimeler):
                for kelime2 in set(youtube_kelimeler):
                    if kelime1 in ortak_kelimeler and kelime2 in ortak_kelimeler:
                        G_ortak.add_edge(kelime1, kelime2)
            
            # Ağ grafiği
            plt.subplot(1, 2, 2)
            pos = nx.spring_layout(G_ortak, k=1, iterations=50)
            
            # Node boyutlarını normalize et
            max_degree = max(dict(G_ortak.degree()).values()) if G_ortak.nodes() else 1
            node_sizes = [100 + (G_ortak.degree(node) * 500 / max_degree) for node in G_ortak.nodes()]
            
            nx.draw(G_ortak, pos,
                   node_color='lightblue',
                   node_size=node_sizes,
                   with_labels=True,
                   font_size=8,
                   edge_color='gray',
                   alpha=0.7)
            
            plt.title(f'{isim} İlişki Ağı', pad=20)
        
        plt.tight_layout()
        
        # Dosyaya kaydet ve göster
        plt.savefig(f'{isim.lower()}_analizi.png', dpi=300, bbox_inches='tight')
        plt.show()
        plt.close()  # Belleği temizle
        
    except Exception as e:
        print(f"{isim} görselleştirme hatası: {e}")
        
def main():
    try:
        # USOM verilerini çek
        print("USOM verileri çekiliyor...")
        usom_df = usom_veri_cek()
        
        if usom_df.empty:
            print("USOM verisi çekilemedi!")
            return
        
        # YouTube verilerini çek
        print("\nYouTube Veri Çekme")
        youtube_df = youtube_veri_cek()
        
        if youtube_df.empty:
            print("YouTube verisi çekilemedi!")
            return
        
        # USOM ve YouTube verilerini analiz et
        print("\nUSOM ve YouTube Verileri analiz ediliyor...")
        usom_kelimeler, youtube_kelimeler = veri_analiz(usom_df, youtube_df)
        
        # Ortak verileri analiz et
        print("\nOrtak Veriler analiz ediliyor...")
        ortak_kelimeler = set(usom_kelimeler) & set(youtube_kelimeler)
        
        # Ortak kelimeler için ilişki ağı oluştur
        G_ortak = nx.Graph()
        for kelime in ortak_kelimeler:
            G_ortak.add_node(kelime)
        
        # Ortak kelimeler arasındaki ilişkiyi ekleyin
        for kelime1 in usom_kelimeler:
            for kelime2 in youtube_kelimeler:
                if kelime1 in ortak_kelimeler and kelime2 in ortak_kelimeler:
                    G_ortak.add_edge(kelime1, kelime2)
        
        # Görselleştir
        gorselleştir(G_ortak, Counter(ortak_kelimeler), "Ortak", usom_kelimeler, youtube_kelimeler)
        
        # Verileri kaydet
        zaman_damgasi = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        usom_df.to_csv(f'usom_zafiyetler_{zaman_damgasi}.csv', index=False, encoding='utf-8')
        youtube_df.to_csv(f'youtube_veriler_{zaman_damgasi}.csv', index=False, encoding='utf-8')
        print(f"\nVeriler CSV dosyalarına kaydedildi.")
        
    except Exception as e:
        print(f"Program çalışırken hata oluştu: {e}")

if __name__ == "__main__":
    main()
