import customtkinter as ctk
from tkinter import filedialog
import os
import json

class ModelPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.model_path_file = "model.json"  # Model yolunun tutulduğu dosya
        self.selected_model_path = self.yolu_yukle()  # Mevcut kayıtlı model yolu (varsa)

        # Sayfa başlığı
        self.label = ctk.CTkLabel(self, text="Model Yükleme", font=("Arial", 24))
        self.label.pack(pady=20)

        # Seçilen model dosyasını gösteren etiket
        self.model_label = ctk.CTkLabel(self, text=f"Seçilen Model:\n{self.selected_model_path or 'Henüz yok'}", wraplength=600)
        self.model_label.pack(pady=10)

        # Model seçme butonu
        self.button = ctk.CTkButton(self, text="Model Seç (.pt)", command=self.model_sec)
        self.button.pack(pady=10)

    def model_sec(self):
        # Kullanıcıdan .pt uzantılı model dosyasını seçmesini ister
        file_path = filedialog.askopenfilename(filetypes=[("PyTorch Model", "*.pt")])
        if file_path:
            self.selected_model_path = file_path
            self.model_label.configure(text=f"Seçilen Model:\n{file_path}")
            self.yolu_kaydet(file_path)

    def yolu_yukle(self):
        # model.json varsa, model yolunu oradan alır
        if os.path.exists(self.model_path_file):
            try:
                with open(self.model_path_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("model_path")
            except:
                return None
        return None

    def yolu_kaydet(self, yol):
        # Seçilen model yolunu model.json dosyasına kaydeder
        with open(self.model_path_file, "w", encoding="utf-8") as f:
            json.dump({"model_path": yol}, f, indent=4)

    def show(self):
        # Sayfayı görünür yapar
        self.lift()

    def hide(self):
        # Sayfayı gizler
        self.lower()
