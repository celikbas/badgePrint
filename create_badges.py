import pandas as pd
from pypdf import PdfReader, PdfWriter
import io
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

# 1. Font Kayıt İşlemi (Türkçe Karakter Desteği İçin)
try:
    pdfmetrics.registerFont(TTFont("Georgia", "/usr/share/fonts/truetype/msttcorefonts/Georgia.ttf"))
    pdfmetrics.registerFont(TTFont("Georgia-Bold", "/usr/share/fonts/truetype/msttcorefonts/Georgia_Bold.ttf"))
    pdfmetrics.registerFont(TTFont("DejaVuSans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
    active_font = "DejaVuSans" # Varsayılan olarak DejaVu seçelim (daha geniş destek sunar)
except:
    # Eğer font yolları sunucuda/bilgisayarda farklıysa hata almamak için fallback
    active_font = "Helvetica"
    print("Uyarı: Belirtilen font yolları bulunamadı, varsayılan fonta dönülüyor.")


# 1. Verileri Yükle
df = pd.read_csv('Participant_List.csv')
template_path = 'Badge_master.pdf'
output_pdf_path = 'Katilimci_Yaka_Kartlari.pdf'

def generate_badges():
    # Şablonu oku (Sayfa boyutlarını almak için)
    reader = PdfReader(template_path)
    template_page = reader.pages[0]
    width = float(template_page.mediabox.width)
    height = float(template_page.mediabox.height)
    
    writer = PdfWriter()

    for index, row in df.iterrows():
        # Verileri Hazırla
        full_name = f"{row['First']} {row['Last']}".upper()
        institution = str(row['Instutition'])

        # Üzerine yazılacak metin katmanını (overlay) oluştur
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(width, height))
        
        # İsim Soyisim Ayarları (Orta Bölüm)
        if len(full_name) < 18:
            can.setFont("DejaVuSans-Bold", 12)
            # Y koordinatı (-40) şablonun görsel yapısına göre ayarlanmıştır
            can.drawCentredString(width / 2.0, height / 2.0 - 20, full_name)
        else:
            # Split once starting from the right
            parts = full_name.rsplit(' ', 1)
            first_part = parts[0]  # "The quick brown"
            last_part = parts[1]   # "fox"

            can.setFont("DejaVuSans-Bold", 12)
            # Y koordinatı (-40) şablonun görsel yapısına göre ayarlanmıştır
            can.drawCentredString(width / 2.0, height / 2.0 - 5, first_part)
            can.drawCentredString(width / 2.0, height / 2.0 - 20, last_part)

        
        # Kurum Bilgisi Ayarları
        if len(institution) < 35:
            can.setFont(active_font, 8)
            can.drawCentredString(width / 2.0, height / 2.0 - 35, institution)
        else:
            # Split once starting from the right
            parts = institution.rsplit(' ', 1)
            first_part = parts[0]  # "The quick brown"
            last_part = parts[1]   # "fox"
            can.setFont(active_font, 8)
            can.drawCentredString(width / 2.0, height / 2.0 - 35, first_part)
            can.drawCentredString(width / 2.0, height / 2.0 - 45, last_part)

        
        can.save()
        packet.seek(0)
        
        # Şablon ile Metni Birleştirme
        overlay_pdf = PdfReader(packet)
        new_page = PdfReader(template_path).pages[0]
        new_page.merge_page(overlay_pdf.pages[0])
        
        # Yeni sayfayı ana dosyaya ekle
        writer.add_page(new_page)

    # Dosyayı Kaydet
    with open(output_pdf_path, "wb") as f:
        writer.write(f)

if __name__ == "__main__":
    generate_badges()
    print(f"Başarıyla oluşturuldu: {output_pdf_path}")