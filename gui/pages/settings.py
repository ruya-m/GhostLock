import customtkinter as ctk
import json
import os

class SettingsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.ayarlar_dosyasi = "ayarlar.json"  # Ayarların kaydedildiği JSON dosyası
        self.varsayilan_ayarlar = {
            "idle_threshold": 15,
            "mode": "main.py"
        }

        self.config = self.ayar_yukle()  # Ayarları yükle

        # Sayfa başlığı
        self.label = ctk.CTkLabel(self, text="Ayarlar", font=("Arial", 24))
        self.label.pack(pady=20)

        # Hareketsizlik süresi ayarı
        self.threshold_label = ctk.CTkLabel(self, text="Hareketsizlik süresi (saniye):")
        self.threshold_label.pack(pady=(10, 0))

        self.threshold_slider = ctk.CTkSlider(self, from_=5, to=60, number_of_steps=55, command=self.slider_guncelle)
        self.threshold_slider.set(self.config["idle_threshold"])
        self.threshold_slider.pack()

        self.slider_value_label = ctk.CTkLabel(self, text=f"{self.config['idle_threshold']} saniye")
        self.slider_value_label.pack(pady=(0, 10))

        # ort_sure.txt dosyasından öneri
        self.ort_label = ctk.CTkLabel(self, text=self.ort_sure_oku(), text_color="gray")
        self.ort_label.pack(pady=5)

        # Mod seçimi (main.py çalıştır vs ekran kilidi)
        self.mode_label = ctk.CTkLabel(self, text="Mod seçimi:")
        self.mode_label.pack(pady=(20, 0))

        self.mode_var = ctk.StringVar(value=self.config["mode"])
        self.radio_main = ctk.CTkRadioButton(self, text="main.py çalışsın", variable=self.mode_var, value="main.py")
        self.radio_lock = ctk.CTkRadioButton(self, text="Sadece ekranı kilitle", variable=self.mode_var, value="lock")

        self.radio_main.pack()
        self.radio_lock.pack()

        # Ayarları kaydetme butonu
        self.save_button = ctk.CTkButton(self, text="Ayarları Kaydet", command=self.ayar_kaydet)
        self.save_button.pack(pady=20)

    def slider_guncelle(self, value):
        # Slider değeri değiştikçe etiketi güncelle
        self.slider_value_label.configure(text=f"{int(value)} saniye")

    def ort_sure_oku(self):
        # ort_sure.txt dosyasından ilk satırı (öneri) oku
        try:
            with open("ort_sure.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
                if lines:
                    return lines[0].strip()
        except:
            return "Ortalama süre dosyası bulunamadı."
        return ""

    def ayar_yukle(self):
        # ayarlar.json varsa oku, yoksa varsayılanı kullan
        if os.path.exists(self.ayarlar_dosyasi):
            try:
                with open(self.ayarlar_dosyasi, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass  # Hatalıysa varsayılanla devam et
        return self.varsayilan_ayarlar.copy()

    def ayar_kaydet(self):
        # Kullanıcının ayarlarını JSON'a yaz
        ayarlar = {
            "idle_threshold": int(self.threshold_slider.get()),
            "mode": self.mode_var.get()
        }
        try:
            with open(self.ayarlar_dosyasi, "w", encoding="utf-8") as f:
                json.dump(ayarlar, f, indent=4)
            self.save_button.configure(text="✅ Kaydedildi", fg_color="green")
        except:
            self.save_button.configure(text="❌ Hata!", fg_color="red")

    def show(self):
        # Sayfayı görünür yap
        self.lift()

    def hide(self):
        # Sayfayı gizle
        self.lower()
