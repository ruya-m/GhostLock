import customtkinter as ctk
from tkinter import ttk
import pandas as pd
import os

class ReportPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.df = pd.DataFrame()
        self.df_full = pd.DataFrame()  # Tüm veriler (filtrelenmemiş)
        self.search_var = ctk.StringVar()
        self.page_size_var = ctk.StringVar(value="25")

        self.page = 0
        self.page_size = 25

        # Sayfa başlığı
        self.label = ctk.CTkLabel(self, text="Raporlar", font=("Arial", 24))
        self.label.pack(pady=10)

        # Arama ve sayfa boyutu alanı
        self.filter_frame = ctk.CTkFrame(self)
        self.filter_frame.pack(pady=5)

        self.search_entry = ctk.CTkEntry(self.filter_frame, placeholder_text="Ara...", textvariable=self.search_var)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda e: self.apply_filter())

        self.clear_btn = ctk.CTkButton(self.filter_frame, text="Filtreyi Temizle", command=self.clear_filter)
        self.clear_btn.pack(side="left", padx=5)

        self.page_size_menu = ctk.CTkOptionMenu(
            self.filter_frame,
            values=["10", "25", "50", "100"],
            variable=self.page_size_var,
            command=self.update_page_size
        )
        self.page_size_menu.pack(side="left", padx=5)

        # Yenile butonu
        self.refresh_btn = ctk.CTkButton(self, text="Yenile", command=self.load_csv)
        self.refresh_btn.pack(pady=5)

        # Tablo görünüm alanı
        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.pack(pady=10, fill="both", expand=True)

        self.tree = ttk.Treeview(self.tree_frame, show="headings")
        self.tree.pack(fill="both", expand=True)

        # Sayfalama butonları
        self.nav_frame = ctk.CTkFrame(self)
        self.nav_frame.pack(pady=10)

        self.prev_btn = ctk.CTkButton(self.nav_frame, text="← Geri", command=self.prev_page)
        self.prev_btn.pack(side="left", padx=10)

        self.page_label = ctk.CTkLabel(self.nav_frame, text="Sayfa: 1")
        self.page_label.pack(side="left", padx=10)

        self.next_btn = ctk.CTkButton(self.nav_frame, text="İleri →", command=self.next_page)
        self.next_btn.pack(side="left", padx=10)

        self.load_csv()

        # Tablo stil ayarları
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="#ffffff",
                        fieldbackground="#2b2b2b",
                        rowheight=28,
                        font=("Segoe UI", 11))
        style.map("Treeview",
                  background=[('selected', '#3e3e42')],
                  foreground=[('selected', 'white')])
        style.configure("Treeview.Heading",
                        background="#1f1f1f",
                        foreground="white",
                        relief="flat",
                        font=("Segoe UI", 11, "bold"))

    def load_csv(self):
        # CSV'den veriyi yükler, sıralar ve sayfalar
        if not os.path.exists("log_report.csv"):
            self.df = pd.DataFrame()
            return

        self.df_full = pd.read_csv("log_report.csv")
        self.df_full = self.df_full.sort_values(by="Zaman", ascending=False).reset_index(drop=True)
        self.df = self.df_full.copy()
        self.page = 0

        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(self.df.columns)

        for col in self.df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

        self.render_page()

    def render_page(self):
        # Aktif sayfadaki verileri tabloya basar
        try:
            self.page_size = int(self.page_size_var.get())
        except:
            self.page_size = 25

        self.tree.delete(*self.tree.get_children())
        start = self.page * self.page_size
        end = start + self.page_size

        for _, row in self.df.iloc[start:end].iterrows():
            self.tree.insert("", "end", values=list(row))

        total_pages = max(1, (len(self.df) - 1) // self.page_size + 1)
        self.page_label.configure(text=f"Sayfa: {self.page + 1} / {total_pages}")

    def next_page(self):
        # Bir sonraki sayfaya geçer
        if (self.page + 1) * self.page_size < len(self.df):
            self.page += 1
            self.render_page()

    def prev_page(self):
        # Önceki sayfaya döner
        if self.page > 0:
            self.page -= 1
            self.render_page()

    def show(self):
        # Sayfayı görünür yap
        self.lift()

    def hide(self):
        # Sayfayı gizle
        self.lower()

    def apply_filter(self):
        # Arama çubuğundaki kelimeye göre filtre uygular
        keyword = self.search_var.get().lower().strip()
        if not keyword:
            self.df = self.df_full.copy()
        else:
            self.df = self.df_full[self.df_full.apply(
                lambda row: row.astype(str).str.lower().str.contains(keyword).any(), axis=1)]

        self.page = 0
        self.render_page()

    def clear_filter(self):
        # Arama filtresini temizler
        self.search_var.set("")
        self.df = self.df_full.copy()
        self.page = 0
        self.render_page()

    def update_page_size(self, _):
        # Sayfa boyutu seçimi değiştiğinde yeniden başlatır
        self.page = 0
        self.render_page()
