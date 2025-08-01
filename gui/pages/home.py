import threading
import sys
import customtkinter as ctk
from PIL import Image, ImageTk
import os
import glob
import time

# Üst dizindeki detect.py fonksiyonlarına erişim
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from detect import start_monitoring, stop_monitoring, model_yolunu_yukle
import detect
from tkinter import messagebox

class HomePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.monitor_thread = None
        self.stop_event = threading.Event()
        self.monitoring = False
        self.idle_seconds = 0

        # Başlık etiketi
        self.title = ctk.CTkLabel(self, text="Ana Sayfa", font=("Arial", 24))
        self.title.place(relx=0.5, rely=0.05, anchor="center")

        # Başlat/Durdur butonu
        self.toggle_button = ctk.CTkButton(self, text="Başlat", command=self.toggle_monitor)
        self.toggle_button.place(relx=0.5, rely=0.15, anchor="center")

        # Hareketsizlik süresi etiketi (canlı güncellenir)
        self.idle_label = ctk.CTkLabel(self, text="Anlık hareketsizlik süresi: 0 saniye")
        self.idle_label.place(relx=0.5, rely=0.25, anchor="center")

        # Ortalama süre etiketi (ort_sure.txt dosyasından okunur)
        self.avg_label = ctk.CTkLabel(self, text="Oturum ortalaması: yükleniyor...")
        self.avg_label.place(relx=0.5, rely=0.30, anchor="center")

        # Son çekilen fotoğraf alanı
        self.image_label = ctk.CTkLabel(self, text="Fotoğraf yükleniyor...")
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")

        # Güven oranı bilgisi
        self.conf_label = ctk.CTkLabel(self, text="Confidence: -")
        self.conf_label.place(relx=0.5, rely=0.75, anchor="center")

        # Arayüz düzenli olarak güncellenir
        self.after(1000, self.update_ui)

    def toggle_monitor(self):
        # İzleme başlatılır veya durdurulur
        if not self.monitoring:
            model_path = model_yolunu_yukle()
            if not model_path or not os.path.exists(model_path):
                messagebox.showwarning("Model Seçilmedi", "Lütfen önce bir .pt model dosyası seçin.")
                return

            self.monitoring = True
            self.toggle_button.configure(text="Durdur")
            start_monitoring()
        else:
            self.monitoring = False
            self.toggle_button.configure(text="Başlat")
            stop_monitoring()

    def update_ui(self):
        # Canlı arayüzü her saniye günceller
        idle_time = time.time() - detect.last_activity_time
        if idle_time < 1.5:
            self.idle_seconds = 0
        elif self.monitoring:
            self.idle_seconds += 1

        self.idle_label.configure(text=f"Anlık hareketsizlik süresi: {self.idle_seconds} saniye")

        # Ortalama süre dosyasından okunur
        try:
            with open("ort_sure.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
                if lines:
                    self.avg_label.configure(text=lines[0].strip())
        except FileNotFoundError:
            self.avg_label.configure(text="Ortalama süre dosyası bulunamadı.")

        # Son çekilen fotoğraf ve güven değeri
        photo_path, conf = self.get_last_photo_info()
        if photo_path:
            try:
                image = Image.open(photo_path)
                image = image.resize((320, 240))
                self.photo = ImageTk.PhotoImage(image)
                self.image_label.configure(image=self.photo, text="")
            except:
                self.image_label.configure(text="Fotoğraf yüklenemedi.")
        else:
            self.image_label.configure(text="Fotoğraf bulunamadı.")

        self.conf_label.configure(text=f"Confidence: {conf if conf else '-'}")

        self.after(1000, self.update_ui)

    def get_last_photo_info(self):
        # control klasöründen son fotoğrafı ve log bilgilerini döndürür
        folder = "control"
        if not os.path.exists(folder):
            return None, None

        files = sorted(glob.glob(os.path.join(folder, "*.jpg")), reverse=True)
        if not files:
            return None, None

        latest = files[0]
        txt_path = latest.replace(".jpg", ".txt")
        confidence = "-"
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if lines:
                    confidence = lines[0].strip()

        return latest, confidence

    def show(self):
        # Sayfayı görünür yapar
        self.lift()

    def hide(self):
        # Sayfayı gizler
        self.lower()
