from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
                             QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox)
from PyQt6.QtCore import Qt
from datetime import datetime


class FinansWidget(QWidget):

    def __init__(self, db, detay_callback):
        super().__init__()
        self.db = db
        self.detay_callback = detay_callback
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        lbl_baslik = QLabel("Finansal Durum & İstatistikler")
        lbl_baslik.setStyleSheet("font-size: 22px; font-weight: bold; color: #40a7e3;")
        layout.addWidget(lbl_baslik)

        cards_layout = QHBoxLayout()
        self.card_aktif = self.create_info_card("AKTİF ÖĞRENCİ", "#00897b", "👥")
        self.card_ders = self.create_info_card("BU AY DERS", "#7cb342", "🎸")
        self.card_ciro = self.create_info_card("BU AY CİRO (TL)", "#fb8c00", "💰")

        cards_layout.addWidget(self.card_aktif)
        cards_layout.addWidget(self.card_ders)
        cards_layout.addWidget(self.card_ciro)
        layout.addLayout(cards_layout)

        filter_layout = QHBoxLayout()

        self.combo_ogr = QComboBox()
        self.combo_ogr.addItem("Tüm Öğrenciler", "Tümü")
        self.combo_ogr.currentIndexChanged.connect(self.verileri_guncelle)

        self.combo_ay = QComboBox()
        self.combo_ay.addItem("Tüm Aylar", "Tümü")
        aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım",
                 "Aralık"]
        for i, ay in enumerate(aylar, 1):
            self.combo_ay.addItem(ay, i)
        simdi = datetime.now()
        self.combo_ay.setCurrentIndex(simdi.month)
        self.combo_ay.currentIndexChanged.connect(self.verileri_guncelle)

        self.combo_yil = QComboBox()
        current_year = simdi.year
        for y in range(current_year, current_year - 5, -1):
            self.combo_yil.addItem(str(y), y)
        self.combo_yil.currentIndexChanged.connect(self.verileri_guncelle)

        filter_layout.addWidget(QLabel("Filtre:"))
        filter_layout.addWidget(self.combo_ogr)
        filter_layout.addWidget(self.combo_ay)
        filter_layout.addWidget(self.combo_yil)
        filter_layout.addStretch()

        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Tarih", "Öğrenci (Detay)", "Tutar", "Notlar"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self.satir_tiklandi)

        layout.addWidget(self.table)

        self.ogrenci_listesini_yenile()

    def create_info_card(self, title, color, icon):
        frame = QFrame()
        frame.setFixedHeight(120)
        frame.setStyleSheet(f"QFrame {{ background-color: {color}; border-radius: 12px; }}")
        vbox = QVBoxLayout(frame)

        top_row = QHBoxLayout()
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 24px; background: transparent;")
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: rgba(255,255,255,0.8); background: transparent;")

        top_row.addWidget(lbl_icon)
        top_row.addWidget(lbl_title)
        top_row.addStretch()

        lbl_val = QLabel("0")
        lbl_val.setStyleSheet("font-size: 36px; font-weight: bold; color: white; background: transparent;")
        lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)

        vbox.addLayout(top_row)
        vbox.addWidget(lbl_val)

        frame.value_label = lbl_val
        return frame

    def ogrenci_listesini_yenile(self):
        """Combobox'ı veritabanından doldurur"""
        mevcut_id = self.combo_ogr.currentData()
        self.combo_ogr.clear()
        self.combo_ogr.addItem("Tüm Öğrenciler", "Tümü")

        ogrenciler = self.db.ogrenci_isimleri_getir()
        for ogr in ogrenciler:
            self.combo_ogr.addItem(ogr[1], ogr[0])

        if mevcut_id:
            index = self.combo_ogr.findData(mevcut_id)
            if index >= 0: self.combo_ogr.setCurrentIndex(index)

    def verileri_guncelle(self):
        aktif, ders, ciro = self.db.istatistik_getir()
        self.card_aktif.value_label.setText(str(aktif))
        self.card_ders.value_label.setText(str(ders))
        self.card_ciro.value_label.setText(f"{ciro:,.0f} ₺")

        ogr_id = self.combo_ogr.currentData()
        ay = self.combo_ay.currentData()
        yil = self.combo_yil.currentData()

        veriler = self.db.odemeleri_filtreli_getir(ogr_id, ay, yil)

        self.table.setRowCount(len(veriler))
        for i, row in enumerate(veriler):
            self.table.setItem(i, 0, QTableWidgetItem(str(row[0])))
            self.table.setItem(i, 1, QTableWidgetItem(str(row[1])))
            self.table.setItem(i, 2, QTableWidgetItem(f"{row[2]} ₺"))
            self.table.setItem(i, 3, QTableWidgetItem(str(row[3])))

            self.table.item(i, 1).setData(Qt.ItemDataRole.UserRole, row[4])

    def satir_tiklandi(self, row, col):
        item = self.table.item(row, 1)
        ogrenci_id = item.data(Qt.ItemDataRole.UserRole)

        if ogrenci_id:
            self.detay_callback(ogrenci_id)