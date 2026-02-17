import shutil  
import os      
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QComboBox, QPushButton, QTreeWidget,
                             QTreeWidgetItem, QHeaderView, QMessageBox, QInputDialog,
                             QFrame, QTabWidget, QFileDialog) 
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush, QFont
from datetime import datetime
from database import DatabaseManager
from details_window import OgrenciDetayPenceresi
from finance_window import FinansWidget


class GitarTakipApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("BerkayShred - Studio Pro")
        self.resize(1150, 800)
        self.db = DatabaseManager()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tab_ogrenci = QWidget()
        self.setup_ogrenci_tab()
        self.tabs.addTab(self.tab_ogrenci, "👥 Öğrenci Yönetimi")

        self.finans_widget = FinansWidget(self.db, self.detay_ac_id_ile) 
        self.tabs.addTab(self.finans_widget, "📊 Finans Dashboard")

        self.tab_ayarlar = QWidget()
        self.setup_ayarlar_tab()
        self.tabs.addTab(self.tab_ayarlar, "⚙️ Ayarlar") 
        
        self.tabs.currentChanged.connect(self.sekme_degisti)
        self.listele_ve_guncelle()
    
    def filtreleri_temizle(self):
        self.txt_filtre_isim.clear()
        self.cmb_filtre_enstruman.setCurrentIndex(0)
        self.cmb_filtre_mod.setCurrentIndex(0)
        self.cmb_filtre_durum.setCurrentIndex(0)
        self.listele_ve_guncelle()

    def setup_ayarlar_tab(self):
        """Ayarlar ve Yedekleme arayüzünü oluşturur"""
        layout = QVBoxLayout(self.tab_ayarlar)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        grp_backup = QFrame()
        grp_backup.setStyleSheet("background-color: #2b2b2b; border-radius: 12px; border: 1px solid #444;")
        bak_layout = QVBoxLayout(grp_backup)
        bak_layout.setContentsMargins(30, 30, 30, 30)
        bak_layout.setSpacing(15)
        
        lbl_icon = QLabel("💾")
        lbl_icon.setStyleSheet("font-size: 48px; border: none; background: transparent;")
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_info = QLabel("Veritabanı Yedekleme Merkezi")
        lbl_info.setStyleSheet("font-size: 20px; font-weight: bold; color: #40a7e3; border: none; background: transparent;")
        lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_desc = QLabel("Verilerinizi güvende tutmak için düzenli aralıklarla yedek almanız önerilir.\n"
                          "Bilgisayar değişikliği veya veri kaybı durumunda 'Yedek Yükle' ile verilerinizi geri getirebilirsiniz.")
        lbl_desc.setStyleSheet("color: #aaa; border: none; font-size: 14px; background: transparent;")
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_desc.setWordWrap(True)
        
        btn_yedek_al = QPushButton("📥 Yedek Al (Bilgisayara Kaydet)")
        btn_yedek_al.setStyleSheet("""
            QPushButton { background-color: #2e7d32; padding: 15px; font-size: 15px; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background-color: #388e3c; }
        """)
        btn_yedek_al.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_yedek_al.clicked.connect(self.yedek_al)
        
        btn_yedek_yukle = QPushButton("📤 Yedek Yükle (Geri Getir)")
        btn_yedek_yukle.setStyleSheet("""
            QPushButton { background-color: #c62828; padding: 15px; font-size: 15px; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background-color: #d32f2f; }
        """)
        btn_yedek_yukle.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_yedek_yukle.clicked.connect(self.yedek_yukle)

        bak_layout.addWidget(lbl_icon)
        bak_layout.addWidget(lbl_info)
        bak_layout.addWidget(lbl_desc)
        bak_layout.addSpacing(20)
        bak_layout.addWidget(btn_yedek_al)
        bak_layout.addWidget(btn_yedek_yukle)
        
        layout.addStretch()
        layout.addWidget(grp_backup)
        layout.addStretch()

    def yedek_al(self):
        """Mevcut veritabanı dosyasını seçilen konuma kopyalar"""
        source = "ders_takip_v2.db"
        if not os.path.exists(source):
            QMessageBox.warning(self, "Hata", "Veritabanı dosyası bulunamadı! Henüz hiç veri girmemiş olabilirsiniz.")
            return

        tarih = datetime.now().strftime("%Y-%m-%d_%H-%M")
        default_name = f"gitar_takip_yedek_{tarih}.db"
        
        dest, _ = QFileDialog.getSaveFileName(self, "Yedeği Kaydet", default_name, "SQLite Veritabanı (*.db)")
        
        if dest:
            try:
                shutil.copy2(source, dest)
                QMessageBox.information(self, "Başarılı", f"Yedek başarıyla alındı:\n{dest}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Yedekleme sırasında hata oluştu:\n{str(e)}")

    def yedek_yukle(self):
        """Seçilen yedek dosyasını mevcut veritabanının üzerine yazar"""
        source, _ = QFileDialog.getOpenFileName(self, "Yedek Dosyası Seç", "", "SQLite Veritabanı (*.db)")
        
        if source:
            confirm = QMessageBox.warning(self, "Dikkat! Veriler Değişecek",
                                          "Bu işlem şu anki verilerinizi KALICI OLARAK SİLECEK ve seçtiğiniz yedeği yükleyecektir.\n\n"
                                          "Emin misiniz?",
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if confirm == QMessageBox.StandardButton.Yes:
                try:
                    target = "ders_takip_v2.db"
                    shutil.copy2(source, target)
                    
                    self.listele_ve_guncelle()
                    if hasattr(self, 'finans_widget'):
                        self.finans_widget.ogrenci_listesini_yenile()
                        self.finans_widget.verileri_guncelle()
                        
                    QMessageBox.information(self, "Başarılı", "Veritabanı başarıyla geri yüklendi!\nTüm veriler güncellendi.")
                except Exception as e:
                    QMessageBox.critical(self, "Hata", f"Geri yükleme sırasında hata oluştu:\n{str(e)}")

    def setup_ogrenci_tab(self):
        layout = QVBoxLayout(self.tab_ogrenci)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #2b2b2b; border-radius: 8px; border: 1px solid #3d3d3d;")
        form_layout = QHBoxLayout(form_frame)
        
        self.input_isim = QLineEdit()
        self.input_isim.setPlaceholderText("Ad Soyad Giriniz...")
        self.input_isim.setMinimumWidth(200)
        
        self.combo_gitar = QComboBox()
        self.combo_gitar.addItems(["Elektro", "Klasik", "Akustik"])
        
        self.combo_mod = QComboBox()
        self.combo_mod.addItems(["Yüzyüze", "Online"])
        
        btn_ekle = QPushButton("💾 Yeni Kayıt")
        btn_ekle.setObjectName("btn_success")
        btn_ekle.clicked.connect(self.ogrenci_ekle)
        
        btn_guncelle = QPushButton("✏️ Düzenle")
        btn_guncelle.setObjectName("btn_warning")
        btn_guncelle.clicked.connect(self.ogrenci_guncelle)

        form_layout.addWidget(QLabel("Öğrenci:"))
        form_layout.addWidget(self.input_isim)
        form_layout.addWidget(self.combo_gitar)
        form_layout.addWidget(self.combo_mod)
        form_layout.addWidget(btn_ekle)
        form_layout.addWidget(btn_guncelle)
        layout.addWidget(form_frame)

        action_layout = QHBoxLayout()
        btn_ders = QPushButton("🎸 DERS İŞLENDİ (-1)")
        btn_ders.setMinimumHeight(55)
        btn_ders.setObjectName("btn_info")
        btn_ders.clicked.connect(lambda: self.islem_yap("Ders"))
        
        btn_odeme = QPushButton("💰 ÖDEME ALINDI (+4)")
        btn_odeme.setMinimumHeight(55)
        btn_odeme.setObjectName("btn_success")
        btn_odeme.clicked.connect(lambda: self.islem_yap("Odeme"))

        btn_manuel = QPushButton("➕ Manuel Ekle (+?)")
        btn_manuel.setMinimumHeight(55)
        btn_manuel.setObjectName("btn_warning") 
        btn_manuel.clicked.connect(lambda: self.islem_yap("Manuel"))
        
        btn_detay = QPushButton("📜 Detaylar")
        btn_detay.setMinimumHeight(55)
        btn_detay.clicked.connect(self.detay_ac)
        
        btn_sil = QPushButton("🗑️ Sil")
        btn_sil.setMinimumHeight(55)
        btn_sil.setObjectName("btn_danger")
        btn_sil.clicked.connect(self.ogrenci_sil)

        action_layout.addWidget(btn_ders, 2)
        action_layout.addWidget(btn_odeme, 2)
        action_layout.addWidget(btn_manuel, 1)
        action_layout.addWidget(btn_detay, 1)
        action_layout.addWidget(btn_sil, 1)
        layout.addLayout(action_layout)

        filter_frame = QFrame()
        filter_frame.setStyleSheet("background-color: #2b2b2b; border-radius: 8px; border: 1px solid #444;")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(10, 5, 10, 5)
        
        self.txt_filtre_isim = QLineEdit()
        self.txt_filtre_isim.setPlaceholderText("🔍 İsimle Ara...")
        self.txt_filtre_isim.textChanged.connect(self.listele_ve_guncelle)
        
        self.cmb_filtre_enstruman = QComboBox()
        self.cmb_filtre_enstruman.addItem("Tüm Enstrümanlar", "Tümü")
        self.cmb_filtre_enstruman.addItems(["Elektro", "Klasik", "Akustik"])
        self.cmb_filtre_enstruman.currentIndexChanged.connect(self.listele_ve_guncelle)

        self.cmb_filtre_mod = QComboBox()
        self.cmb_filtre_mod.addItem("Tüm Modlar", "Tümü")
        self.cmb_filtre_mod.addItems(["Yüzyüze", "Online"])
        self.cmb_filtre_mod.currentIndexChanged.connect(self.listele_ve_guncelle)

        self.cmb_filtre_durum = QComboBox()
        self.cmb_filtre_durum.addItem("Tüm Durumlar", "Tümü")
        self.cmb_filtre_durum.addItem("Borcu Olanlar (<=0)", "Borcu Olanlar (<=0)")
        self.cmb_filtre_durum.addItem("Az Kalanlar (1-3)", "Az Kalanlar (1-3)")
        self.cmb_filtre_durum.addItem("Aktif (4+)", "Aktif (4+)")
        self.cmb_filtre_durum.currentIndexChanged.connect(self.listele_ve_guncelle)
        
        btn_filtre_temizle = QPushButton("❌")
        btn_filtre_temizle.setFixedWidth(40)
        btn_filtre_temizle.setToolTip("Filtreleri Temizle")
        btn_filtre_temizle.clicked.connect(self.filtreleri_temizle)

        filter_layout.addWidget(self.txt_filtre_isim, 3)
        filter_layout.addWidget(self.cmb_filtre_enstruman, 2)
        filter_layout.addWidget(self.cmb_filtre_mod, 2)
        filter_layout.addWidget(self.cmb_filtre_durum, 2)
        filter_layout.addWidget(btn_filtre_temizle)
        
        layout.addWidget(filter_frame) 

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["ID", "İsim", "Enstrüman", "Mod", "Kalan Ders"])
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.setAlternatingRowColors(True)
        self.tree.itemClicked.connect(self.satir_secildi)
        self.tree.itemDoubleClicked.connect(self.detay_ac)
        layout.addWidget(self.tree)

    def listele_ve_guncelle(self):
        self.tree.clear()
        
        try:
            isim = self.txt_filtre_isim.text()
            enstruman = self.cmb_filtre_enstruman.currentText() 
            if self.cmb_filtre_enstruman.currentIndex() == 0: enstruman = "Tümü"
            
            mod = self.cmb_filtre_mod.currentText()
            if self.cmb_filtre_mod.currentIndex() == 0: mod = "Tümü"
            
            durum = self.cmb_filtre_durum.currentText()
            if self.cmb_filtre_durum.currentIndex() == 0: durum = "Tümü"
            
            veriler = self.db.ogrencileri_filtreli_getir(isim, enstruman, mod, durum)
            
        except AttributeError:
            veriler = self.db.ogrencileri_getir()

        for row in veriler:
            item = QTreeWidgetItem([str(row[0]), row[1], row[2], row[3], str(row[4])])
            kalan = row[4]
            
            if kalan <= 0:
                item.setForeground(4, QBrush(QColor("#ff5252")))
                item.setFont(4, QFont("Segoe UI", 9, QFont.Weight.Bold))
            elif kalan == 1:
                item.setForeground(4, QBrush(QColor("#ffb74d")))
            elif kalan >= 4:
                item.setForeground(4, QBrush(QColor("#69f0ae")))
            
            self.tree.addTopLevelItem(item)
        
        if hasattr(self, 'finans_widget'):
            self.finans_widget.ogrenci_listesini_yenile()
            self.finans_widget.verileri_guncelle()

    def sekme_degisti(self, index):
        if index == 1:
            self.finans_widget.verileri_guncelle()

    def satir_secildi(self, item, col):
        self.input_isim.setText(item.text(1))
        self.combo_gitar.setCurrentText(item.text(2))
        self.combo_mod.setCurrentText(item.text(3))

    def ogrenci_ekle(self):
        isim = self.input_isim.text()
        if not isim: return
        self.db.ogrenci_ekle(isim, self.combo_gitar.currentText(), self.combo_mod.currentText())
        self.input_isim.clear()
        self.listele_ve_guncelle()

    def ogrenci_guncelle(self):
        item = self.tree.currentItem()
        if not item: return
        uid = int(item.text(0))
        mevcut = self.db.ogrenci_bilgi_getir(uid)
        self.db.ogrenci_guncelle(uid, self.input_isim.text(), self.combo_gitar.currentText(),
                                 self.combo_mod.currentText(), mevcut[5], mevcut[6], mevcut[7])
        self.listele_ve_guncelle()

    def islem_yap(self, tip):
        item = self.tree.currentItem()
        if not item:
            QMessageBox.warning(self, "Uyarı", "Lütfen listeden bir öğrenci seçin!")
            return
            
        uid = int(item.text(0))
        simdi = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        tarih, ok1 = QInputDialog.getText(self, "Tarih", "İşlem Tarihi:", text=simdi)
        if not ok1: return
        
        ders_sayisi = None
        if tip == "Manuel":
            adet, ok_adet = QInputDialog.getInt(self, "Ders Ekle", "Eklenecek Ders Sayısı (Negatif girilebilir):", 1, -100, 100)
            if not ok_adet: return
            ders_sayisi = adet

        tutar = 0
        if tip == "Odeme":
            tutar_str, ok_tutar = QInputDialog.getText(self, "Tutar", "Alınan Miktar (TL):", text="0")
            if ok_tutar and tutar_str:
                try:
                    tutar = float(tutar_str)
                except ValueError:
                    tutar = 0
        
        not_mesaji, ok2 = QInputDialog.getText(self, "Not", f"{tip} Notu (Opsiyonel):")
        if not ok2: return 
        
        if tip == "Ders":
            prefix = "Ders İşlendi"
        elif tip == "Odeme":
            prefix = "Ödeme Alındı"
        elif tip == "Manuel":
            prefix = f"Manuel İşlem ({ders_sayisi} Ders)"
        else:
            prefix = "İşlem"

        final_not = f"{prefix} - {not_mesaji}"
        
        self.db.islem_yap(uid, tip, tarih, final_not, tutar, ders_adedi=ders_sayisi)
        self.listele_ve_guncelle()
        
        QMessageBox.information(self, "Kayıt", f"{tip} işlemi kaydedildi.\nTutar: {tutar} TL")

    def detay_ac(self):
        item = self.tree.currentItem()
        if not item: return
        uid = int(item.text(0))
        self.detay_window = OgrenciDetayPenceresi(uid, self.db, self.listele_ve_guncelle)
        self.detay_window.show()

    def detay_ac_id_ile(self, uid):
        """Finans sayfasından ID ile detay açmak için"""
        self.detay_window = OgrenciDetayPenceresi(uid, self.db, self.listele_ve_guncelle)
        self.detay_window.show()

    def ogrenci_sil(self):
        item = self.tree.currentItem()
        if not item: return
        if QMessageBox.question(self, "Sil", "Emin misin?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.db.ogrenci_sil(int(item.text(0)))
            self.listele_ve_guncelle()
