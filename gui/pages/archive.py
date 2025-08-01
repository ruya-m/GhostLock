import customtkinter as ctk
import os
import datetime

class ArchivePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # Sayfa başlığı
        self.label = ctk.CTkLabel(self, text="Geçmiş Arşivler", font=("Arial", 24))
        self.label.pack(pady=20)

        # Scrollable alan: ZIP arşiv listesi
        self.scroll = ctk.CTkScrollableFrame(self, height=400)
        self.scroll.pack(padx=20, pady=10, fill="both", expand=True)

        # Yenileme butonu
        self.yenile_btn = ctk.CTkButton(self, text="Yenile", command=self.yenile)
        self.yenile_btn.pack(pady=10)

        self.yenile()  # İlk yüklemede listele

    def yenile(self):
        # Scroll alanındaki önceki widget'ları temizle
        for widget in self.scroll.winfo_children():
            widget.destroy()

        zip_klasoru = "gecmis"
        if not os.path.exists(zip_klasoru):
            os.makedirs(zip_klasoru)

        # ZIP dosyalarını al ve ters sırala (en yeni en üstte)
        zipler = [f for f in os.listdir(zip_klasoru) if f.endswith(".zip")]
        zipler.sort(reverse=True)

        if not zipler:
            ctk.CTkLabel(self.scroll, text="ZIP arşivi bulunamadı.").pack(pady=10)
            return

        # Başlık çubuğu
        header = ctk.CTkFrame(self.scroll)
        header.pack(fill="x", padx=10)
        ctk.CTkLabel(header, text="Dosya Adı", width=300, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(header, text="Tarih", anchor="w").pack(side="left")

        # ZIP dosyalarını listele
        for zip_name in zipler:
            full_path = os.path.join(zip_klasoru, zip_name)
            tarih = datetime.datetime.fromtimestamp(os.path.getmtime(full_path)).strftime("%Y-%m-%d %H:%M:%S")

            row = ctk.CTkFrame(self.scroll)
            row.pack(fill="x", padx=10, pady=2)

            label = ctk.CTkLabel(row, text=zip_name, width=300, anchor="w", cursor="hand2")
            label.pack(side="left", padx=10)
            label.bind("<Double-Button-1>", lambda e, path=full_path: self.zip_ac(path))

            ctk.CTkLabel(row, text=tarih, anchor="w").pack(side="left")

    def zip_ac(self, path):
        # ZIP dosyasını sistemde varsayılan uygulamayla açar
        try:
            os.startfile(os.path.abspath(path))
        except Exception as e:
            print(f"❌ ZIP açılamadı: {e}")

    def show(self):
        # Sayfayı görünür yap
        self.lift()

    def hide(self):
        # Sayfayı gizle
        self.lower()
