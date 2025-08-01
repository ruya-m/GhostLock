import customtkinter as ctk
from pages.home import HomePage
from pages.settings import SettingsPage
from pages.model import ModelPage
from pages.report import ReportPage
from pages.last_detect import LastDetectPage
from pages.archive import ArchivePage
import sys
import os

# Proje dizinine üst klasörden erişim sağlanır (detect.py içindeki fonksiyonlar için)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from detect import archive_control_folder

# Görsel tema ve görünüm ayarları
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Uygulama başlatıldığında control klasörü arşivlenir
        archive_control_folder()

        # Pencere boyutlandırmaları
        self.geometry("1000x600")
        self.minsize(800, 500)
        self.resizable(True, True)

        # Sol kenarda sayfa butonlarını içeren menü çubuğu
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")

        # Tüm sayfaları oluşturan ve sözlükte tutan yapı
        self.pages = {
            "Ana Sayfa": HomePage(self),
            "Ayarlar": SettingsPage(self),
            "Model": ModelPage(self),
            "Rapor": ReportPage(self),
            "Son Tespit": LastDetectPage(self),
            "Geçmiş": ArchivePage(self)
        }

        # Menüdeki her bir buton tanımlanır
        for name in self.pages:
            btn = ctk.CTkButton(self.sidebar, text=name, command=lambda n=name: self.show_page(n))
            btn.pack(pady=5, padx=10, fill="x")

        # Sayfa bileşenleri oluşturulup gizlenir
        for frame in self.pages.values():
            frame.place(x=200, y=0, relwidth=1.0, relheight=1.0)
            frame.hide()

        # Uygulama başladığında varsayılan olarak ana sayfa görünür
        self.show_page("Ana Sayfa")

    def show_page(self, name):
        # Belirtilen sayfayı gösterir, diğerlerini gizler
        for page_name, page in self.pages.items():
            if page_name == name:
                page.show()
            else:
                page.hide()

# Uygulama bağımsız çalıştırıldığında buradan başlar
if __name__ == "__main__":
    app = App()
    app.mainloop()
