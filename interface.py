from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QComboBox, QPushButton, QTreeWidget, 
                             QTreeWidgetItem, QHeaderView, QMessageBox, QInputDialog, QFrame, QTabWidget)
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
        
        self.tabs.currentChanged.connect(self.sekme_degisti)
        self.listele_ve_guncelle()

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
        self.combo_gitar.addItems(["Elektro Gitar", "Klasik Gitar", "Akustik Gitar", "Bas Gitar"])
        
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
        
        btn_detay = QPushButton("📜 Detaylar")
        btn_detay.setMinimumHeight(55)
        btn_detay.clicked.connect(self.detay_ac)
        
        btn_sil = QPushButton("🗑️ Sil")
        btn_sil.setMinimumHeight(55)
        btn_sil.setObjectName("btn_danger")
        btn_sil.clicked.connect(self.ogrenci_sil)

        action_layout.addWidget(btn_ders, 2)
        action_layout.addWidget(btn_odeme, 2)
        action_layout.addWidget(btn_detay, 1)
        action_layout.addWidget(btn_sil, 1)
        layout.addLayout(action_layout)

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
        
        final_not = f"{'Ders İşlendi' if tip == 'Ders' else 'Ödeme Alındı'} - {not_mesaji}"
        
        self.db.islem_yap(uid, tip, tarih, final_not, tutar)
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