from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTabWidget, QTreeWidget, QTreeWidgetItem, 
                             QHeaderView, QMessageBox, QFrame, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush

class OgrenciDetayPenceresi(QWidget):
    def __init__(self, uid, db, callback):
        super().__init__()
        self.uid = uid
        self.db = db
        self.callback = callback
        
        self.ogrenci_bilgi = self.db.ogrenci_bilgi_getir(self.uid)
        self.isim = self.ogrenci_bilgi[1]
        
        self.setWindowTitle(f"Detaylar: {self.isim}")
        self.resize(900, 600)
        
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        self.tab_genel = QWidget()
        self.tab_repertuvar = QWidget()
        
        self.tabs.addTab(self.tab_genel, "📋 Genel Bilgiler & Geçmiş")
        self.tabs.addTab(self.tab_repertuvar, "🎸 Repertuvar & Şarkılar")
        
        self.setup_genel_tab()
        self.setup_repertuvar_tab()

    def setup_genel_tab(self):
        layout = QVBoxLayout(self.tab_genel)
        
        kart_frame = QFrame()
        kart_frame.setStyleSheet("background-color: #333; border-radius: 8px;")
        kart_layout = QVBoxLayout(kart_frame)
        
        row1 = QHBoxLayout()
        self.input_yas = QLineEdit()
        self.input_yas.setPlaceholderText("Yaş")
        if self.ogrenci_bilgi[5]: self.input_yas.setText(self.ogrenci_bilgi[5])
        
        self.input_tecrube = QLineEdit()
        self.input_tecrube.setPlaceholderText("Tecrübe")
        if self.ogrenci_bilgi[6]: self.input_tecrube.setText(self.ogrenci_bilgi[6])
        
        row1.addWidget(QLabel("Yaş:"))
        row1.addWidget(self.input_yas)
        row1.addWidget(QLabel("Tecrübe:"))
        row1.addWidget(self.input_tecrube)
        
        row2 = QHBoxLayout()
        self.input_hedef = QLineEdit()
        self.input_hedef.setPlaceholderText("Hedef")
        if self.ogrenci_bilgi[7]: self.input_hedef.setText(self.ogrenci_bilgi[7])
        row2.addWidget(QLabel("Hedef:"))
        row2.addWidget(self.input_hedef)
        
        btn_kaydet = QPushButton("Bilgileri Güncelle")
        btn_kaydet.setObjectName("btn_info")
        btn_kaydet.clicked.connect(self.detay_kaydet)
        
        kart_layout.addLayout(row1)
        kart_layout.addLayout(row2)
        kart_layout.addWidget(btn_kaydet)
        layout.addWidget(kart_frame)
        
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("İşlem Geçmişi:"))
        
        self.combo_filter = QComboBox()
        self.combo_filter.addItems(["Tümü", "Sadece Dersler", "Sadece Ödemeler"])
        self.combo_filter.currentIndexChanged.connect(self.gecmis_yukle)
        filter_row.addWidget(self.combo_filter)
        filter_row.addStretch()
        
        layout.addLayout(filter_row)
        
        self.tree_gecmis = QTreeWidget()
        self.tree_gecmis.setHeaderLabels(["ID", "Tarih", "İşlem", "Detay", "Tutar"])
        self.tree_gecmis.header().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tree_gecmis.header().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.tree_gecmis)
        
        btn_sil = QPushButton("Seçili İşlemi Sil")
        btn_sil.setObjectName("btn_danger")
        btn_sil.clicked.connect(self.islem_sil)
        layout.addWidget(btn_sil)
        
        self.gecmis_yukle()

    def gecmis_yukle(self):
        self.tree_gecmis.clear()
        secilen_filtre = self.combo_filter.currentText()
        
        veriler = self.db.gecmis_getir(self.uid, secilen_filtre)
        for row in veriler:
            tutar_str = f"{row[4]} TL" if row[4] > 0 else "-"
            QTreeWidgetItem(self.tree_gecmis, [str(row[0]), row[1], row[2], row[3], tutar_str])

    def detay_kaydet(self):
        self.db.ogrenci_guncelle(self.uid, self.ogrenci_bilgi[1], self.ogrenci_bilgi[2], self.ogrenci_bilgi[3],
                                 self.input_yas.text(), self.input_tecrube.text(), self.input_hedef.text())
        self.callback()
        QMessageBox.information(self, "Bilgi", "Kaydedildi.")

    def islem_sil(self):
        item = self.tree_gecmis.currentItem()
        if not item: return
        if QMessageBox.question(self, "Sil", "Silinsin mi?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.db.islem_sil(int(item.text(0)))
            self.gecmis_yukle()
            self.callback()

    def setup_repertuvar_tab(self):
        pass
    
    def setup_repertuvar_tab(self):
        layout = QVBoxLayout(self.tab_repertuvar)
        layout.setContentsMargins(15, 15, 15, 15)
        
        input_row = QHBoxLayout()
        self.input_sarki = QLineEdit()
        self.input_sarki.setPlaceholderText("Yeni Şarkı Adı...")
        
        btn_ekle = QPushButton("➕ Ekle")
        btn_ekle.setObjectName("btn_save") 
        btn_ekle.clicked.connect(self.sarki_ekle)
        
        input_row.addWidget(self.input_sarki)
        input_row.addWidget(btn_ekle)
        layout.addLayout(input_row)
        
        self.tree_rep = QTreeWidget()
        self.tree_rep.setHeaderLabels(["ID", "Şarkı Adı", "Durum (Çift Tıkla)"])
        self.tree_rep.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tree_rep.itemDoubleClicked.connect(self.durum_degistir)
        
        layout.addWidget(self.tree_rep)
        
        btn_rep_sil = QPushButton("Seçili Şarkıyı Sil")
        btn_rep_sil.setObjectName("btn_delete")
        btn_rep_sil.clicked.connect(self.sarki_sil)
        layout.addWidget(btn_rep_sil)
        
        self.repertuvar_yukle()

    def gecmis_yukle(self):
        self.tree_gecmis.clear()
        veriler = self.db.gecmis_getir(self.uid)
        for row in veriler:
            QTreeWidgetItem(self.tree_gecmis, [str(row[0]), row[1], row[2], row[3]])

    def detay_kaydet(self):
        self.db.ogrenci_guncelle(self.uid, self.ogrenci_bilgi[1], self.ogrenci_bilgi[2], self.ogrenci_bilgi[3],
                                 self.input_yas.text(), self.input_tecrube.text(), self.input_hedef.text())
        self.ogrenci_bilgi = self.db.ogrenci_bilgi_getir(self.uid)
        self.callback()
        QMessageBox.information(self, "Bilgi", "Kaydedildi.")

    def islem_sil(self):
        item = self.tree_gecmis.currentItem()
        if not item: return
        if QMessageBox.question(self, "Sil", "Silinsin mi?") == QMessageBox.StandardButton.Yes:
            self.db.islem_sil(int(item.text(0)))
            self.gecmis_yukle()
            self.callback()

    def repertuvar_yukle(self):
        self.tree_rep.clear()
        veriler = self.db.repertuvar_getir(self.uid)
        for row in veriler:
            item = QTreeWidgetItem(self.tree_rep, [str(row[0]), row[1], row[2]])
            if row[2] == "Tamamlandı ✅":
                item.setForeground(2, QBrush(QColor("#69f0ae")))
            else:
                item.setForeground(2, QBrush(QColor("#ffb74d")))
                
    def sarki_ekle(self):
        sarki = self.input_sarki.text()
        if sarki:
            self.db.repertuvar_ekle(self.uid, sarki)
            self.input_sarki.clear()
            self.repertuvar_yukle()

    def durum_degistir(self, item, col):
        rep_id = int(item.text(0))
        yeni = "Tamamlandı ✅" if item.text(2) == "Çalışılıyor" else "Çalışılıyor"
        self.db.repertuvar_durum_degistir(rep_id, yeni)
        self.repertuvar_yukle()

    def sarki_sil(self):
        item = self.tree_rep.currentItem()
        if not item: return
        self.db.repertuvar_sil(int(item.text(0)))
        self.repertuvar_yukle()