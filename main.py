import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import sqlite3
from datetime import datetime


# Veritabanı Kurulumu
def veri_tabani_kur():
    conn = sqlite3.connect('ders_takip_v2.db')
    c = conn.cursor()
    
    # Öğrenci Tablosu
    c.execute('''CREATE TABLE IF NOT EXISTS ogrenciler
                 (id INTEGER PRIMARY KEY, isim TEXT, tur TEXT, mod TEXT, kalan_ders INTEGER)''')
    
    # GEÇMİŞ TABLOSU
    c.execute('''CREATE TABLE IF NOT EXISTS gecmis
                 (id INTEGER PRIMARY KEY, ogrenci_id INTEGER, islem_tipi TEXT, tarih TEXT, notlar TEXT)''')
                 
    conn.commit()
    conn.close()


class GitarTakipApp:

    def _init_(self, root):
        self.root = root
        self.root.title("BerkayShred - Gitar Dersi Takip")
        self.root.geometry("700x500")
        
        veri_tabani_kur()
        
        # --- Üst Kısım: Giriş Alanları ---
        frame_giris = tk.LabelFrame(root, text="Yeni Öğrenci Ekle")
        frame_giris.pack(pady=10, padx=10, fill="x")

        tk.Label(frame_giris, text="Öğrenci Adı:").grid(row=0, column=0, padx=5, pady=5)
        self.ent_isim = tk.Entry(frame_giris)
        self.ent_isim.grid(row=0, column=1, padx=5)
        
        tk.Label(frame_giris, text="Gitar Türü:").grid(row=0, column=2, padx=5)
        self.combo_tur = ttk.Combobox(frame_giris, values=["Klasik", "Akustik", "Elektro"], width=10)
        self.combo_tur.grid(row=0, column=3, padx=5)
        
        tk.Label(frame_giris, text="Ders Türü:").grid(row=0, column=4, padx=5)
        self.combo_mod = ttk.Combobox(frame_giris, values=["Yüzyüze", "Online"], width=10)
        self.combo_mod.grid(row=0, column=5, padx=5)
        
        tk.Button(frame_giris, text="Kaydet", command=self.ogrenci_ekle, bg="#4CAF50", fg="white").grid(row=0, column=6, padx=15)
        
        # --- Butonlar Paneli ---
        frame_islem = tk.Frame(root)
        frame_islem.pack(pady=5)
        
        tk.Button(frame_islem, text="Ders İşlendi (-1)", command=lambda: self.islem_yap("Ders"), bg="#FF9800", width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_islem, text="Ödeme Alındı (+4)", command=lambda: self.islem_yap("Odeme"), bg="#2196F3", fg="white", width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_islem, text="GEÇMİŞİ GÖR", command=self.gecmis_goster, bg="#607D8B", fg="white", width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_islem, text="Öğrenciyi Sil", command=self.ogrenci_sil, bg="red", fg="white", width=12).pack(side=tk.LEFT, padx=20)

        # --- Liste (Tablo) ---
        self.tree = ttk.Treeview(root, columns=("ID", "İsim", "Gitar Türü", "Ders Türü", "Kalan Ders"), show='headings', height=15)
        
        self.tree.heading("ID", text="ID") 
        self.tree.heading("İsim", text="İsim")
        self.tree.heading("Gitar Türü", text="Gitar Türü")
        self.tree.heading("Ders Türü", text="Ders Türü")
        self.tree.heading("Kalan Ders", text="Kalan Ders")
        
        self.tree.column("ID", width=30, anchor="center")
        self.tree.column("İsim", width=150, anchor="center")
        self.tree.column("Kalan Ders", width=80, anchor="center")
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.listele()

    def veritabani_baglan(self):
        return sqlite3.connect('ders_takip_v2.db')

    def ogrenci_ekle(self):
        isim, tur, mod = self.ent_isim.get(), self.combo_tur.get(), self.combo_mod.get()
        if isim:
            conn = self.veritabani_baglan()
            c = conn.cursor()
            c.execute("INSERT INTO ogrenciler (isim, tur, mod, kalan_ders) VALUES (?, ?, ?, ?)", (isim, tur, mod, 0))
            conn.commit()
            conn.close()
            self.ent_isim.delete(0, tk.END)
            self.listele()
        else:
            messagebox.showwarning("Hata", "Lütfen isim girin!")

    def listele(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        conn = self.veritabani_baglan()
        c = conn.cursor()
        c.execute("SELECT id, isim, tur, mod, kalan_ders FROM ogrenciler")
        for row in c.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    def islem_yap(self, islem_tipi):
        # Seçili öğrenciyi al
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen listeden bir öğrenci seçin!")
            return

        ogrenci_id = self.tree.item(selected)['values'][0]
        ogrenci_isim = self.tree.item(selected)['values'][1]

        # Tarih ve Saat sor (Otomatik doldur: Gün.Ay.Yıl Saat:Dakika)
        # Örnek: 05.01.2024 14:30
        simdi = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        tarih_saat = simpledialog.askstring("Zaman Gir", f"{islem_tipi} Zamanı:", initialvalue=simdi)
        
        if tarih_saat:
            conn = self.veritabani_baglan()
            c = conn.cursor()
            
            if islem_tipi == "Ders":
                # Bakiyeyi düş
                c.execute("UPDATE ogrenciler SET kalan_ders = kalan_ders - 1 WHERE id=?", (ogrenci_id,))
                not_mesaji = "Ders Yapıldı"
            elif islem_tipi == "Odeme":
                # Bakiyeyi artır
                c.execute("UPDATE ogrenciler SET kalan_ders = kalan_ders + 4 WHERE id=?", (ogrenci_id,))
                not_mesaji = "Ödeme Alındı (+4)"
            
            # GEÇMİŞE KAYDET (Tarih ve Saat ile)
            c.execute("INSERT INTO gecmis (ogrenci_id, islem_tipi, tarih, notlar) VALUES (?, ?, ?, ?)",
                      (ogrenci_id, islem_tipi, tarih_saat, not_mesaji))
            
            conn.commit()
            conn.close()
            self.listele()
            messagebox.showinfo("Başarılı", f"{ogrenci_isim} için işlem kaydedildi.\nZaman: {tarih_saat}")

    def gecmis_goster(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Geçmişini görmek için bir öğrenci seçin!")
            return
            
        ogrenci_id = self.tree.item(selected)['values'][0]
        ogrenci_isim = self.tree.item(selected)['values'][1]
        
        top = tk.Toplevel(self.root)
        top.title(f"{ogrenci_isim} - İşlem Geçmişi")
        top.geometry("450x300")  # Genişliği biraz artırdık çünkü saat de var
        
        # Geçmiş Listesi
        tree_gecmis = ttk.Treeview(top, columns=("TarihSaat", "İşlem", "Not"), show='headings')
        tree_gecmis.heading("TarihSaat", text="Tarih ve Saat")
        tree_gecmis.heading("İşlem", text="İşlem Tipi")
        tree_gecmis.heading("Not", text="Detay")
        
        tree_gecmis.column("TarihSaat", width=130)  # Saat için yer açtık
        tree_gecmis.column("İşlem", width=80)
        tree_gecmis.pack(fill=tk.BOTH, expand=True)
        
        # Verileri Çek
        conn = self.veritabani_baglan()
        c = conn.cursor()
        c.execute("SELECT tarih, islem_tipi, notlar FROM gecmis WHERE ogrenci_id=? ORDER BY id DESC", (ogrenci_id,))
        rows = c.fetchall()
        conn.close()
        
        for row in rows:
            tree_gecmis.insert("", "end", values=row)

    def ogrenci_sil(self):
        selected = self.tree.selection()
        if selected:
            cevap = messagebox.askyesno("Sil", "Öğrenciyi ve tüm geçmişini silmek istiyor musun?")
            if cevap:
                ogrenci_id = self.tree.item(selected)['values'][0]
                conn = self.veritabani_baglan()
                c = conn.cursor()
                c.execute("DELETE FROM ogrenciler WHERE id=?", (ogrenci_id,))
                c.execute("DELETE FROM gecmis WHERE ogrenci_id=?", (ogrenci_id,))
                conn.commit()
                conn.close()
                self.listele()


if _name_ == "_main_":
    root = tk.Tk()
    app = GitarTakipApp(root)
    root.mainloop()
