import sqlite3

class DatabaseManager:
    def __init__(self, db_name='ders_takip_v2.db'):
        self.db_name = db_name
        self.kurulum_yap()

    def baglan(self):
        return sqlite3.connect(self.db_name)

    def kurulum_yap(self):
        with self.baglan() as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS ogrenciler
                         (id INTEGER PRIMARY KEY, isim TEXT, tur TEXT, mod TEXT, kalan_ders INTEGER)''')
            c.execute('''CREATE TABLE IF NOT EXISTS gecmis
                         (id INTEGER PRIMARY KEY, ogrenci_id INTEGER, islem_tipi TEXT, tarih TEXT, notlar TEXT)''')
            conn.commit()

    def ogrenci_ekle(self, isim, tur, mod):
        with self.baglan() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO ogrenciler (isim, tur, mod, kalan_ders) VALUES (?, ?, ?, ?)", 
                      (isim, tur, mod, 0))
            conn.commit()

    def ogrenci_guncelle(self, uid, isim, tur, mod):
        with self.baglan() as conn:
            c = conn.cursor()
            c.execute("UPDATE ogrenciler SET isim=?, tur=?, mod=? WHERE id=?", (isim, tur, mod, uid))
            conn.commit()

    def ogrencileri_getir(self):
        with self.baglan() as conn:
            c = conn.cursor()
            c.execute("SELECT id, isim, tur, mod, kalan_ders FROM ogrenciler")
            return c.fetchall()

    def islem_yap(self, ogrenci_id, islem_tipi, tarih_saat, not_mesaji):
        with self.baglan() as conn:
            c = conn.cursor()
            if islem_tipi == "Ders":
                c.execute("UPDATE ogrenciler SET kalan_ders = kalan_ders - 1 WHERE id=?", (ogrenci_id,))
            elif islem_tipi == "Odeme":
                c.execute("UPDATE ogrenciler SET kalan_ders = kalan_ders + 4 WHERE id=?", (ogrenci_id,))
            
            c.execute("INSERT INTO gecmis (ogrenci_id, islem_tipi, tarih, notlar) VALUES (?, ?, ?, ?)",
                      (ogrenci_id, islem_tipi, tarih_saat, not_mesaji))
            conn.commit()

    def islem_sil(self, islem_id):
        """
        Geçmişten bir kaydı siler ve bakiyeyi eski haline getirir.
        """
        with self.baglan() as conn:
            c = conn.cursor()
            
            c.execute("SELECT ogrenci_id, islem_tipi FROM gecmis WHERE id=?", (islem_id,))
            kayit = c.fetchone()
            
            if kayit:
                ogrenci_id, islem_tipi = kayit
                
                if islem_tipi == "Ders":
                    c.execute("UPDATE ogrenciler SET kalan_ders = kalan_ders + 1 WHERE id=?", (ogrenci_id,))
                elif islem_tipi == "Odeme":
                    c.execute("UPDATE ogrenciler SET kalan_ders = kalan_ders - 4 WHERE id=?", (ogrenci_id,))
                
                c.execute("DELETE FROM gecmis WHERE id=?", (islem_id,))
                conn.commit()
                return True
            return False
            
    def gecmis_getir(self, ogrenci_id):
        with self.baglan() as conn:
            c = conn.cursor()
            c.execute("SELECT id, tarih, islem_tipi, notlar FROM gecmis WHERE ogrenci_id=? ORDER BY id DESC", (ogrenci_id,))
            return c.fetchall()

    def ogrenci_sil(self, ogrenci_id):
        with self.baglan() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM ogrenciler WHERE id=?", (ogrenci_id,))
            c.execute("DELETE FROM gecmis WHERE ogrenci_id=?", (ogrenci_id,))
            conn.commit()