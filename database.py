import sqlite3
from datetime import datetime

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
                         (id INTEGER PRIMARY KEY, isim TEXT, tur TEXT, mod TEXT, kalan_ders INTEGER, 
                          yas TEXT, tecrube TEXT, hedef TEXT)''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS gecmis
                         (id INTEGER PRIMARY KEY, ogrenci_id INTEGER, islem_tipi TEXT, tarih TEXT, notlar TEXT, tutar REAL)''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS repertuvar
                         (id INTEGER PRIMARY KEY, ogrenci_id INTEGER, sarki TEXT, durum TEXT)''')
            
            try: c.execute("ALTER TABLE ogrenciler ADD COLUMN yas TEXT")
            except: pass
            try: c.execute("ALTER TABLE ogrenciler ADD COLUMN tecrube TEXT")
            except: pass
            try: c.execute("ALTER TABLE ogrenciler ADD COLUMN hedef TEXT")
            except: pass
            try: c.execute("ALTER TABLE gecmis ADD COLUMN tutar REAL DEFAULT 0") 
            except: pass
            conn.commit()

    def ogrenci_ekle(self, isim, tur, mod):
        with self.baglan() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO ogrenciler (isim, tur, mod, kalan_ders) VALUES (?, ?, ?, ?)", (isim, tur, mod, 0))
            conn.commit()

    def ogrenci_guncelle(self, uid, isim, tur, mod, yas, tecrube, hedef):
        with self.baglan() as conn:
            c = conn.cursor()
            c.execute("UPDATE ogrenciler SET isim=?, tur=?, mod=?, yas=?, tecrube=?, hedef=? WHERE id=?", 
                      (isim, tur, mod, yas, tecrube, hedef, uid))
            conn.commit()

    def ogrencileri_getir(self):
        with self.baglan() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM ogrenciler")
            return c.fetchall()

    def ogrenci_bilgi_getir(self, uid):
        with self.baglan() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM ogrenciler WHERE id=?", (uid,))
            return c.fetchone()
            
    def ogrenci_isimleri_getir(self):
        """Filtreleme kutusu için sadece isim ve id döner"""
        with self.baglan() as conn:
            c = conn.cursor()
            c.execute("SELECT id, isim FROM ogrenciler ORDER BY isim ASC")
            return c.fetchall()

    def ogrenci_sil(self, ogrenci_id):
        with self.baglan() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM ogrenciler WHERE id=?", (ogrenci_id,))
            c.execute("DELETE FROM gecmis WHERE ogrenci_id=?", (ogrenci_id,))
            c.execute("DELETE FROM repertuvar WHERE ogrenci_id=?", (ogrenci_id,))
            conn.commit()

    def islem_yap(self, ogrenci_id, islem_tipi, tarih_saat, not_mesaji, tutar=0):
        with self.baglan() as conn:
            c = conn.cursor()
            if islem_tipi == "Ders":
                c.execute("UPDATE ogrenciler SET kalan_ders = kalan_ders - 1 WHERE id=?", (ogrenci_id,))
            elif islem_tipi == "Odeme":
                c.execute("UPDATE ogrenciler SET kalan_ders = kalan_ders + 4 WHERE id=?", (ogrenci_id,))
            
            c.execute("INSERT INTO gecmis (ogrenci_id, islem_tipi, tarih, notlar, tutar) VALUES (?, ?, ?, ?, ?)",
                      (ogrenci_id, islem_tipi, tarih_saat, not_mesaji, tutar))
            conn.commit()

    def islem_sil(self, islem_id):
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

    def gecmis_getir(self, ogrenci_id, filtre_tipi="Tümü"):
        """Detay sayfasında filtreleme için güncellendi"""
        with self.baglan() as conn:
            c = conn.cursor()
            query = "SELECT id, tarih, islem_tipi, notlar, tutar FROM gecmis WHERE ogrenci_id=?"
            params = [ogrenci_id]
            
            if filtre_tipi != "Tümü":
                if filtre_tipi == "Sadece Dersler":
                    query += " AND islem_tipi = 'Ders'"
                elif filtre_tipi == "Sadece Ödemeler":
                    query += " AND islem_tipi = 'Odeme'"
            
            query += " ORDER BY id DESC"
            c.execute(query, params)
            return c.fetchall()

    def repertuvar_ekle(self, ogrenci_id, sarki, durum="Çalışılıyor"):
        with self.baglan() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO repertuvar (ogrenci_id, sarki, durum) VALUES (?, ?, ?)", (ogrenci_id, sarki, durum))
            conn.commit()

    def repertuvar_getir(self, ogrenci_id):
        with self.baglan() as conn:
            c = conn.cursor()
            c.execute("SELECT id, sarki, durum FROM repertuvar WHERE ogrenci_id=?", (ogrenci_id,))
            return c.fetchall()

    def repertuvar_sil(self, rep_id):
        with self.baglan() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM repertuvar WHERE id=?", (rep_id,))
            conn.commit()
            
    def repertuvar_durum_degistir(self, rep_id, yeni_durum):
        with self.baglan() as conn:
            c = conn.cursor()
            c.execute("UPDATE repertuvar SET durum=? WHERE id=?", (yeni_durum, rep_id))
            conn.commit()

    def istatistik_getir(self):
        simdi = datetime.now()
        bu_ay = simdi.strftime(".%m.%Y")
        
        with self.baglan() as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM ogrenciler WHERE kalan_ders > 0")
            aktif_ogrenci = c.fetchone()[0]
            
            c.execute("SELECT COUNT(*) FROM gecmis WHERE islem_tipi='Ders' AND tarih LIKE ?", ('%' + bu_ay + '%',))
            aylik_ders = c.fetchone()[0]
            
            c.execute("SELECT SUM(tutar) FROM gecmis WHERE islem_tipi='Odeme' AND tarih LIKE ?", ('%' + bu_ay + '%',))
            result = c.fetchone()[0]
            aylik_ciro = result if result else 0
            
            return aktif_ogrenci, aylik_ders, aylik_ciro

    def odemeleri_filtreli_getir(self, ogrenci_id=None, ay=None, yil=None):
        """Finans sayfasındaki gelişmiş filtreleme sorgusu"""
        with self.baglan() as conn:
            c = conn.cursor()
            query = """
                SELECT g.tarih, o.isim, g.tutar, g.notlar, o.id 
                FROM gecmis g 
                JOIN ogrenciler o ON g.ogrenci_id = o.id 
                WHERE g.islem_tipi = 'Odeme'
            """
            params = []

            if ogrenci_id and ogrenci_id != "Tümü":
                query += " AND g.ogrenci_id = ?"
                params.append(ogrenci_id)
            
            if ay and ay != "Tümü":
                ay_str = f"{int(ay):02d}" 
                search_str = f"%.{ay_str}.{yil}%"
                query += " AND g.tarih LIKE ?"
                params.append(search_str)
            elif yil: 
                 query += " AND g.tarih LIKE ?"
                 params.append(f"%{yil}%")

            query += " ORDER BY g.id DESC"
            
            c.execute(query, params)
            return c.fetchall()