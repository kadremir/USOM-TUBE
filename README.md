import pandas as pd
import networkx as nx
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from matplotlib import rcParams  # Yazı tipi ayarları için eklenmiştir
from googleapiclient.discovery import build
import requests
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from datetime import datetime

# NLTK verilerini indir
nltk.download('punkt')
nltk.download('stopwords')

# Devanagari karakterlerini destekleyen bir yazı tipi ayarlayın
rcParams['font.family'] = 'Noto Sans Devanagari'  # Yazı tipini ayarlayın

# Ekstra gereksiz kelimeler listesi
non_stop_words_combined = [
    "yok", "bir", "ve", "ile", "bu", "da", "de", "için", "olarak", "gibi", 
    "şu", "ama", "sadece", "bunu", "şey", "kadar", "her", "çok", "daha", 
    "gerek", "merhaba", "hakkında", "nedir", "bölüm", "güncellenmesi", 
    "bilgi", "ediyoruz", "yapılır", "geliştirilmesi", "uygulama", "süreç", 
    "geliştirme", "proje", "çalışma", "yöntem", "örnek", "görmek", "şekilde", 
    "yüzünden", "gözünden", "sorun", "çözüm", "kapsamında", "kapsam", "yeni", 
    "eski", "güncel", "kullanım", "kullanılan", "kullanıcılar", "görüş", 
    "konu", "yapmak", "olmak", "nasıl", "neden", "istek", "görüşler", "takip", 
    "tamam", "almak", "düşünmek", "ben", "sen", "o", "biz", "sizin", "bizim", 
    "sadece", "gibi", "yapmak", "konusundaki", "benim", "yardımcı", "bilgileri", 
    "istediğiniz", "yine", "işlem", "istek", "geri", "tamamlamak", "geçerli", 
    "tartışma", "yapılması", "yazılan", "konusunda", "hemen", "denemek", "iyi", 
    "ne", "oldu", "olabilir", "sonuç", "işlem", "değerlendirmek", "yapıldı", 
    "ilgili", "paylaşmak", "tüm", "bunu", "sayfa", "aşağıdaki", "üzerinde", 
    "sistem", "özellik", "görüntüle", "tartışma", "yönlendirme", "toplantı", 
    "bilgi", "daha fazla", "oluşan", "iletişim", "yardım", "tespit", "dönüş", 
    "durum", "çalışma", "sorular", "açıklama", "öneriler", "kullanıcı", 
    "dönüşüm", "tavsiye", "tartışmaya", "katılmak", "güncellenmiş", "yönlendirme", 
    "çözüm", "duyuru", "açıklama", "sizinle", "kısa", "ilgilendirme", 
    "değişiklik", "gerekli", "bilgisini", "şu anda", "yapılmak", "hatırlatmak", 
    "belirtilen", "yardımcı olmak", "bildirim", "işlemler", "toplantıya", "özellikle", 
    "isteyen", "başka", "başlamak", "içerik", "test", "tartışma", "tartışmak", 
    "sonrası", "yakın", "yenilik", "şimdi", "bununla", "geliştirilmiştir", 
    "gerçekleşen", "tartışılacak", "hesap", "yapılmış", "genel", "hazır", 
    "yine", "özgün", "yeni başlayan", "ileri", "daha önce", "bilgisi", 
    "yazılım", "eklemek", "yaklaşım", "şüpheli", "güvenli", "sistemi", 
    "başka bir", "ekip", "farklı", "uygulama", "plan", "özellikler", 
    "paylaşım", "herhangi", "öncelik", "yönetici", "akademik", "ekran", 
    "bölüm", "geçmiş", "yönetim", "yardımcı", "tartışmaları", "yerine", 
    "sistemler", "değişiklikler", "gönderilen", "devam", "kapsayan", 
    "ağırlıklı", "kapsayan", "açık", "daha az", "daha çok", "ileti", 
    "odak", "görüş", "öncelikli", "bildirilen", "herkes", "önümüzdeki", 
    "bilgileri", "video", "link", "app", "tool", "people", "discuss",
    "understanding", "techniques", "skills", "number", "way", "first", "used",
    "different", "types", "everyone", "learned", "learn", "talk", "know",
    "saw", "sawant", "piratesoftware", "ngobrol", "aswad", "joseph", "prasad",
    "dell", "siber", "scam", "fraud", "index", "cyber", "electric", "protect",
    "mit", "vmware", "ibm", "adobe", "fortinet", "apache", "cisco", "linux",
    "hacking", "hackers", "security", "engineering", "wordpress", "comptia",
    "phishing", "ngobrol", "ngobrol", "ngobrol" ,"güncellemesi", "eklenti", "bildirmi" , "watch", "güvenlik"
]

def tarih_formatlayici(tarih_str):
    """Farklı formatlardaki tarihleri YYYY-MM-DD formatına çevirir"""
    try:
        for format in ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d', '%Y-%m-%d']:
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
    #Veri Çekme API : https://www.usom.gov.tr/api/incident/index?language=tr&url=https%3A%2F%2Fwww.usom.gov.tr%2Fbildirim
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
                "language": "tr"
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

def youtube_veri_cek():
    """YouTube'dan güvenlik videolarını çeker"""
    api_key = "AIzaSyDBazr6iJ84ky5-r9MQ1fXnKmOE7OvM6gA"
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    print("\nYouTube'da aranacak güvenlik konularını giriniz.")
    print("Her sorguyu Enter'a basarak girin, bitirmek için boş satır bırakın.\n")
    
    sorgular = []
    while True:
        sorgu = input("Sorgu giriniz (Çıkmak için Enter): ").strip()
        if not sorgu:
            break
        sorgular.append(sorgu)
    
    tum_videolar = []
    for sorgu in sorgular:
        try:
            request = youtube.search().list(
                part="snippet",
                q=sorgu + " social engineering",
                type="video",
                order="viewCount",
                maxResults=50
            )
            response = request.execute()
            
            for item in response.get("items", []):
                video_info = {
                    'baslik': item['snippet']['title'],
                    'aciklama': item['snippet']['description'],
                    'kaynak': 'YouTube',
                    'sorgu': sorgu
                }
                tum_videolar.append(video_info)
                
        except Exception as e:
            print(f"YouTube verisi çekilirken hata: {e}")
            continue
    
    return pd.DataFrame(tum_videolar)

def veri_analiz(usom_df, youtube_df):
    """USOM ve YouTube verilerini analiz eder"""
    G = nx.Graph()
    
    # Metinleri temizle ve kelimeleri çıkar
    usom_kelimeler = []
    for metin in usom_df['baslik'].str.cat(usom_df['aciklama'], sep=' '):
        usom_kelimeler.extend(metin_temizle(metin))
    
    youtube_kelimeler = []
    for metin in youtube_df['baslik'].str.cat(youtube_df['aciklama'], sep=' '):
        youtube_kelimeler.extend(metin_temizle(metin))
    
    # Düğümleri ekle
    for kelime in set(usom_kelimeler):
        G.add_node(kelime, type='usom')
    
    for kelime in set(youtube_kelimeler):
        G.add_node(kelime, type='youtube')
    
    # Kelimeleri birbirine bağla
    tum_kelimeler = usom_kelimeler + youtube_kelimeler
    kelime_frekanslari = Counter(tum_kelimeler)
    
    # En sık geçen kelimeleri bağla
    for kelime1 in set(usom_kelimeler):
        for kelime2 in set(youtube_kelimeler):
            if kelime1 in kelime_frekanslari and kelime2 in kelime_frekanslari:
                if kelime_frekanslari[kelime1] > 2 and kelime_frekanslari[kelime2] > 2:
                    G.add_edge(kelime1, kelime2)
    
    return G, kelime_frekanslari

def metin_temizle(metin):
    """Metni temizler ve stop words'leri kaldırır"""
    # Stop words listesi
    stop_words = set(stopwords.words('english') + stopwords.words('turkish'))
    
    # Ekstra gereksiz kelimeleri ekleyin
    stop_words.update(non_stop_words_combined)
    
    # Metni temizle
    metin = re.sub(r'[^\w\s]', ' ', str(metin).lower())
    kelimeler = word_tokenize(metin)
    temiz_kelimeler = [kelime for kelime in kelimeler if kelime not in stop_words and len(kelime) > 2]
    
    return temiz_kelimeler

def gorselleştir(G, kelime_frekanslari):
    """Ağ ve kelime bulutu görselleştirmesi"""
    # WordCloud oluşturma
    wordcloud = WordCloud(
        width=1600, 
        height=800,
        background_color='white',
        min_font_size=10,
        max_font_size=150,
        prefer_horizontal=0.7
    ).generate_from_frequencies(dict(kelime_frekanslari))
    
    plt.figure(figsize=(20,10))
    
    plt.subplot(1, 2, 1)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Güvenlik Konuları Kelime Bulutu')
    
    plt.subplot(1, 2, 2)
    pos = nx.spring_layout(G, k=1, iterations=50)
    nx.draw(G, pos, 
           node_color='lightblue',
           node_size=[G.degree(node) * 100 for node in G.nodes()],
           with_labels=True,
           font_size=8,
           edge_color='gray',
           alpha=0.7)
    plt.title('Güvenlik Konuları İlişki Ağı')
    
    plt.tight_layout()
    plt.savefig('guvenlik_analizi.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
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
    
    # Verileri analiz et
    print("\nVeriler analiz ediliyor...")
    G, kelime_frekanslari = veri_analiz(usom_df, youtube_df)
    
    # İstatistikleri göster
    print("\nAnaliz Sonuçları:")
    print("-" * 60)
    print(f"Toplam USOM kaydı: {len(usom_df)}")
    print(f"Toplam YouTube videosu: {len(youtube_df)}")
    print(f"Analiz edilen toplam düğüm sayısı: {G.number_of_nodes()}")
    print(f"Bulunan ilişki sayısı: {G.number_of_edges()}")
    
    # En önemli konuları göster
    print("\nEn Sık Geçen Güvenlik Konuları:")
    print("-" * 60)
    for kelime, freq in kelime_frekanslari.most_common(10):
        print(f"{kelime}: {freq} kez")
    
    # Görselleştir
    print("\nGörselleştirmeler oluşturuluyor...")
    gorselleştir(G, kelime_frekanslari)
    
    # Verileri kaydet
    zaman_damgasi = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    usom_df.to_csv(f'usom_zafiyetler_{zaman_damgasi}.csv', index=False, encoding='utf-8')
    youtube_df.to_csv(f'youtube_veriler_{zaman_damgasi}.csv', index=False, encoding='utf-8')
    print(f"\nVeriler CSV dosyalarına kaydedildi.")
    print(f"Görselleştirmeler 'guvenlik_analizi.png' dosyasına kaydedildi.")

if __name__ == "__main__":
    main()
