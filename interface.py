import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from datetime import datetime
from database import DatabaseManager

class GitarTakipApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BerkayShred - Stüdyo Yönetim v3.0")
        self.root.geometry("950x700")
        
        self.style = ttk.Style()
        self.style.theme_use('clam') # 'alt', 'default', 'classic' 
        
        self.style.configure("Treeview", 
                             background="white",
                             foreground="black", 
                             rowheight=25,
                             fieldbackground="white",
                             font=('Calibri', 11))
        self.style.configure("Treeview.Heading", font=('Calibri', 11, 'bold'), background="#E0E0E0")
        
        self.db = DatabaseManager()
        self.arayuz_olustur()
        self.listele()

    def arayuz_olustur(self):
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        frame_yonetim = tk.LabelFrame(main_frame, text="Öğrenci Yönetimi", font=('Arial', 10, 'bold'), padx=10, pady=10)
        frame_yonetim.pack(fill="x", pady=(0, 15))

        tk.Label(frame_yonetim, text="Öğrenci Adı:").grid(row=0, column=0, padx=5, sticky="e")
        self.ent_isim = tk.Entry(frame_yonetim, width=20)
        self.ent_isim.grid(row=0, column=1, padx=5)
        
        tk.Label(frame_yonetim, text="Gitar:").grid(row=0, column=2, padx=5, sticky="e")
        self.combo_tur = ttk.Combobox(frame_yonetim, values=["Klasik", "Akustik", "Elektro", "Bas"], width=10, state="readonly")
        self.combo_tur.current(0)
        self.combo_tur.grid(row=0, column=3, padx=5)
        
        tk.Label(frame_yonetim, text="Mod:").grid(row=0, column=4, padx=5, sticky="e")
        self.combo_mod = ttk.Combobox(frame_yonetim, values=["Yüzyüze", "Online"], width=10, state="readonly")
        self.combo_mod.current(0)
        self.combo_mod.grid(row=0, column=5, padx=5)
        
        btn_ekle = tk.Button(frame_yonetim, text="💾 Kaydet", command=self.ogrenci_ekle_ui, bg="#4CAF50", fg="white", font=('Arial', 9, 'bold'), padx=10)
        btn_ekle.grid(row=0, column=6, padx=10)
        
        btn_guncelle = tk.Button(frame_yonetim, text="✏️ Güncelle", command=self.ogrenci_guncelle_ui, bg="#FFC107", fg="black", font=('Arial', 9), padx=5)
        btn_guncelle.grid(row=0, column=7, padx=5)

        frame_islem = tk.Frame(main_frame)
        frame_islem.pack(fill="x", pady=5)
        
        tk.Button(frame_islem, text="🎸 DERS İŞLENDİ (-1)", command=lambda: self.islem_yap_ui("Ders"), 
                  bg="#FF9800", fg="black", font=('Arial', 10, 'bold'), height=2, width=20).pack(side=tk.LEFT, padx=(0,10))
                  
        tk.Button(frame_islem, text="💰 ÖDEME ALINDI (+4)", command=lambda: self.islem_yap_ui("Odeme"), 
                  bg="#2196F3", fg="white", font=('Arial', 10, 'bold'), height=2, width=20).pack(side=tk.LEFT, padx=10)
        
        frame_araclar = tk.Frame(frame_islem)
        frame_araclar.pack(side=tk.RIGHT)
        
        tk.Button(frame_araclar, text="📜 Geçmiş / Düzelt", command=self.gecmis_goster_ui, bg="#607D8B", fg="white", width=15).pack(side=tk.TOP, pady=2)
        tk.Button(frame_araclar, text="❌ Öğrenci Sil", command=self.ogrenci_sil_ui, bg="#D32F2F", fg="white", width=15).pack(side=tk.TOP, pady=2)

        frame_liste = tk.Frame(main_frame)
        frame_liste.pack(fill=tk.BOTH, expand=True, pady=10)

        scrollbar = ttk.Scrollbar(frame_liste)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(frame_liste, columns=("ID", "İsim", "Gitar Türü", "Ders Türü", "Kalan Ders"), 
                                 show='headings', height=15, yscrollcommand=scrollbar.set)
        
        scrollbar.config(command=self.tree.yview)
        
        self.tree.tag_configure('borclu', background='#ffcccc') 
        self.tree.tag_configure('sinirda', background='#fff4cc') 
        self.tree.tag_configure('zengin', background='#e8f5e9') 
        self.tree.tag_configure('normal', background='white')

        headers = ["ID", "İsim", "Gitar Türü", "Ders Türü", "Kalan Ders"]
        widths = [40, 250, 120, 120, 100]
        
        for i, col in enumerate(headers):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths[i], anchor="center")
            
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.satir_secildi)

    def listele(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        veriler = self.db.ogrencileri_getir()
        for row in veriler:
            kalan_ders = row[4]
            if kalan_ders <= 0: etiket = 'borclu'
            elif kalan_ders == 1: etiket = 'sinirda'
            elif kalan_ders >= 4: etiket = 'zengin'
            else: etiket = 'normal'
                
            self.tree.insert("", "end", values=row, tags=(etiket,))

    def satir_secildi(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected)['values']
            self.ent_isim.delete(0, tk.END)
            self.ent_isim.insert(0, values[1])
            self.combo_tur.set(values[2])
            self.combo_mod.set(values[3])

    def ogrenci_ekle_ui(self):
        isim = self.ent_isim.get()
        if isim:
            self.db.ogrenci_ekle(isim, self.combo_tur.get(), self.combo_mod.get())
            self.ent_isim.delete(0, tk.END)
            self.listele()
        else:
            messagebox.showwarning("Hata", "İsim boş olamaz.")

    def ogrenci_guncelle_ui(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Hata", "Güncellemek için seçim yapın.")
            return
        uid = self.tree.item(selected)['values'][0]
        self.db.ogrenci_guncelle(uid, self.ent_isim.get(), self.combo_tur.get(), self.combo_mod.get())
        self.listele()
        messagebox.showinfo("Bilgi", "Güncellendi.")

    def islem_yap_ui(self, islem_tipi):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen öğrenci seçin!")
            return

        ogrenci_id = self.tree.item(selected)['values'][0]
        ogrenci_isim = self.tree.item(selected)['values'][1]
        simdi = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        if islem_tipi == "Ders":
            varsayilan = "Ders İşlendi"
        else:
            varsayilan = "Ödeme Alındı (+4)"

        not_text = simpledialog.askstring("Not", f"{islem_tipi} notu (Opsiyonel):", initialvalue="")
        if not_text is None: return 
        
        final_not = f"{varsayilan} - {not_text}" if not_text else varsayilan
        self.db.islem_yap(ogrenci_id, islem_tipi, simdi, final_not)
        self.listele()
        messagebox.showinfo("Başarılı", f"{ogrenci_isim} işlendi.")

    def gecmis_goster_ui(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Geçmiş için öğrenci seçin!")
            return
            
        ogrenci_id = self.tree.item(selected)['values'][0]
        ogrenci_isim = self.tree.item(selected)['values'][1]
        
        top = tk.Toplevel(self.root)
        top.title(f"Detaylar: {ogrenci_isim}")
        top.geometry("700x450")
        
        lbl_info = tk.Label(top, text="Hatalı işlemleri silmek için satırı seçip aşağıdaki butona basın.", 
                            fg="gray", font=("Arial", 9, "italic"))
        lbl_info.pack(pady=5)
        
        cols = ("RefID", "Tarih", "İşlem", "Detay")
        tree_gecmis = ttk.Treeview(top, columns=cols, show='headings', height=12)
        
        tree_gecmis.heading("RefID", text="Ref") 
        tree_gecmis.heading("Tarih", text="Tarih")
        tree_gecmis.heading("İşlem", text="İşlem")
        tree_gecmis.heading("Detay", text="Notlar")
        
        tree_gecmis.column("RefID", width=40, anchor="center")
        tree_gecmis.column("Tarih", width=130, anchor="center")
        tree_gecmis.column("İşlem", width=100, anchor="center")
        tree_gecmis.column("Detay", width=350)
        
        tree_gecmis.pack(fill=tk.BOTH, expand=True, padx=10)

        def gecmis_yenile():
            for i in tree_gecmis.get_children(): tree_gecmis.delete(i)
            rows = self.db.gecmis_getir(ogrenci_id)
            for row in rows:
                tree_gecmis.insert("", "end", values=row)

        gecmis_yenile()

        def secili_islemi_sil():
            selected_item = tree_gecmis.selection()
            if not selected_item:
                messagebox.showwarning("Uyarı", "Silinecek işlemi seçmelisiniz!")
                return
            
            degerler = tree_gecmis.item(selected_item)['values']
            islem_id = degerler[0] 
            islem_tipi = degerler[2]
            
            if messagebox.askyesno("İptal Et", f"Bu '{islem_tipi}' işlemini silip, bakiyeyi geri almak istiyor musunuz?"):
                self.db.islem_sil(islem_id)
                gecmis_yenile() 
                self.listele()  
                messagebox.showinfo("Başarılı", "İşlem geri alındı.")

        btn_sil = tk.Button(top, text="🗑️ Seçili İşlemi Geri Al (Sil)", command=secili_islemi_sil, bg="#e53935", fg="white", font=('Arial', 10, 'bold'))
        btn_sil.pack(pady=10)

    def ogrenci_sil_ui(self):
        selected = self.tree.selection()
        if selected:
            if messagebox.askyesno("Sil", "Öğrenciyi silmek istediğine emin misin?"):
                ogrenci_id = self.tree.item(selected)['values'][0]
                self.db.ogrenci_sil(ogrenci_id)
                self.listele()