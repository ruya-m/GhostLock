import customtkinter as ctk
from PIL import Image, ImageTk
import os
import pandas as pd

class LastDetectPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # Başlık etiketi
        self.label = ctk.CTkLabel(self, text="Son Tespit", font=("Arial", 24))
        self.label.pack(pady=20)

        # Görsel alanı (son tespit fotoğrafı)
        self.image_label = ctk.CTkLabel(self, text="Son tespit görseli burada görünecek.")
        self.image_label.pack(pady=10)
        self.image_label.bind("<Double-Button-1>", self.popup_ac)  # Çift tıklamada detay penceresi

        # Zaman ve güven oranı bilgisi
        self.info_label = ctk.CTkLabel(self, text="")
        self.info_label.pack(pady=5)

        # Yenile butonu
        self.refresh_button = ctk.CTkButton(self, text="Yenile", command=self.yenile)
        self.refresh_button.pack(pady=10)

        self.yenile()

    def yenile(self):
        # log_report.csv'den son "riskli" tespiti alır ve görseli yükler
        if not os.path.exists("log_report.csv"):
            self.info_label.configure(text="log_report.csv bulunamadı.")
            return

        df = pd.read_csv("log_report.csv")
        if df.empty:
            self.info_label.configure(text="Kayıt bulunamadı.")
            return

        # Son kayıttan geriye doğru tarar
        for _, row in df.iloc[::-1].iterrows():
            result = str(row.get("Sonuç", "")).lower()
            if "düşük" in result or "tespit yok" in result:
                image_name = row["Görsel"]
                timestamp = row["Zaman"]
                confidence = row["Confidence (%)"]
                self.gorseli_yukle(image_name)
                self.last_log_data = (image_name, timestamp, confidence, row["Sonuç"])
                self.info_label.configure(text=f"Tespit Zamanı: {timestamp} | Confidence: {confidence}")
                return

        # Hiç riskli kayıt bulunamadıysa
        self.image_label.configure(image=None, text="Riskli tespit bulunamadı.")
        self.info_label.configure(text="")

    def gorseli_yukle(self, image_name):
        # control klasöründen fotoğrafı yükler
        image_path = os.path.join("control", image_name)
        if not os.path.exists(image_path):
            self.image_label.configure(text="Görsel bulunamadı.")
            return

        try:
            img = Image.open(image_path)
            img = img.resize((400, 300))
            self.tk_img = ImageTk.PhotoImage(img)
            self.image_label.configure(image=self.tk_img, text="")
        except:
            self.image_label.configure(text="Görsel yüklenemedi.")

    def show(self):
        # Sayfayı görünür yapar
        self.lift()

    def hide(self):
        # Sayfayı gizler
        self.lower()

    def popup_ac(self, event=None):
        # Son tespitin detaylarını gösteren pencere açar
        if not hasattr(self, "last_log_data"):
            return

        image_name, timestamp, confidence, result = self.last_log_data

        popup = ctk.CTkToplevel(self)
        popup.geometry("500x500")
        popup.title("Tespit Detayı")

        ctk.CTkLabel(popup, text="Tespit Detayı", font=("Arial", 20, "bold")).pack(pady=10)

        img_path = os.path.join("control", image_name)
        if os.path.exists(img_path):
            try:
                img = Image.open(img_path).resize((400, 300))
                tk_img = ImageTk.PhotoImage(img)
                img_label = ctk.CTkLabel(popup, image=tk_img, text="")
                img_label.image = tk_img  # referans tutulmalı!
                img_label.pack(pady=10)
            except:
                ctk.CTkLabel(popup, text="Görsel yüklenemedi.").pack()
        else:
            ctk.CTkLabel(popup, text="Görsel bulunamadı.").pack()

        # Bilgi metni
        info = f"""
Zaman: {timestamp}
Confidence: {confidence}
Sonuç: {result}
"""
        ctk.CTkLabel(popup, text=info.strip(), justify="left").pack(pady=10)
