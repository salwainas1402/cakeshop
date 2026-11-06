import os, json, sqlite3, secrets, datetime
from flask import Flask, g, jsonify, request, send_from_directory, session
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "toko.db")
app = Flask(__name__, static_folder=None)
app.secret_key = os.environ.get("SECRET_KEY", "ganti-ini-di-produksi")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
STATUS = ["baru", "diproses", "siap", "selesai", "batal"]
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

SEED = [
 ("Red Velvet", "Kue Tart", 285000, "Sponge merah beludru, krim keju lembut.", "#F4F0EC", "#B3203E", "Slice Of Classic Red Velvet Cake With Cream Cheese Frosting.jpeg"),
 ("Cokelat Lava", "Kue Tart", 265000, "Tiga lapis cokelat pekat dengan ganache hangat.", "#6B3A2A", "#3E2018", "Chocolate Lava Cake.jpeg"),
 ("Strawberry Shortcake", "Kue Tart", 295000, "Krim segar, stroberi manis, bolu seputih awan.", "#FFB3C6", "#FFE6A7", "The Ultimate Strawberry Shortcake Cake Recipe You Need to Try!.jpeg"),
 ("Cheesecake Blueberry", "Cheesecake", 245000, "Panggang pelan, saus blueberry asam manis.", "#8E7CC3", "#F6E3B4", "1008102697847795669.jpeg"),
 ("Cheesecake Matcha", "Cheesecake", 255000, "Matcha Uji yang tidak terlalu manis.", "#9CCB86", "#F6E3B4", "Japanese Matcha Cheesecake _The perfect mix of creamy and earthy_ 🍵✨ Who’s a matcha fan_ #MatchaCheesecake_.jpeg"),
 ("Lapis Legit", "Kue Tradisional", 320000, "Dua puluh lapis, wangi rempah dan mentega.", "#D9A441", "#8A4B1F", "Lapis Legit.jpeg"),
 ("Bolu Pandan", "Kue Tradisional", 110000, "Empuk, wangi pandan asli, parutan kelapa.", "#B7E4A0", "#6FA85A", ""),
 ("Brownies Panggang", "Brownies", 95000, "Pinggir renyah, tengah fudgy, kacang almond.", "#5A3425", "#3A1F14", ""),
]

def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB); g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close(_):
    d = g.pop("db", None)
    if d: d.close()

def init():
    c = sqlite3.connect(DB)
    c.executescript("""
    CREATE TABLE IF NOT EXISTS produk(id INTEGER PRIMARY KEY, nama TEXT NOT NULL, kategori TEXT NOT NULL,
      harga INTEGER NOT NULL, deskripsi TEXT DEFAULT '', warna TEXT DEFAULT '#FFB3C6', isi TEXT DEFAULT '#FFE6A7',
      gambar TEXT DEFAULT '', tersedia INTEGER DEFAULT 1);
    CREATE TABLE IF NOT EXISTS pesanan(id INTEGER PRIMARY KEY, kode TEXT UNIQUE, nama TEXT, telepon TEXT,
      alamat TEXT, tanggal TEXT, catatan TEXT, items TEXT, total INTEGER, status TEXT DEFAULT 'baru', dibuat TEXT);""")
    if not c.execute("SELECT 1 FROM produk").fetchone():
        c.executemany("INSERT INTO produk(nama,kategori,harga,deskripsi,warna,isi,gambar) VALUES(?,?,?,?,?,?,?)", SEED)
    for product in SEED:
        if product[6]:
            c.execute("UPDATE produk SET gambar=? WHERE nama=? AND (gambar='' OR gambar IS NULL)",
                      (product[6], product[0]))
    c.commit(); c.close()

def admin_only():
    if not session.get("admin"):
        return jsonify(error="Silakan masuk sebagai admin."), 401

@app.errorhandler(RequestEntityTooLarge)
def request_too_large(_):
    if request.path.startswith("/api/"):
        return jsonify(error="Ukuran foto maksimal 5 MB."), 413
    return "Ukuran berkas terlalu besar.", 413

@app.get("/")
def home(): return send_from_directory(os.path.join(BASE, "web"), "index.html")
@app.get("/admin")
def admin_page(): return send_from_directory(os.path.join(BASE, "web"), "admin.html")
@app.get("/gambar/<path:f>")
def gambar(f): return send_from_directory(os.path.join(BASE, "gambar"), f)

@app.get("/api/produk")
def produk():
    sql = "SELECT * FROM produk" + ("" if session.get("admin") and request.args.get("semua") else " WHERE tersedia=1") + " ORDER BY id"
    return jsonify([dict(r) for r in db().execute(sql)])

@app.post("/api/pesanan")
def buat_pesanan():
    d = request.get_json(silent=True) or {}
    nama, telp = str(d.get("nama", "")).strip(), str(d.get("telepon", "")).strip()
    tgl, alamat = str(d.get("tanggal", "")).strip(), str(d.get("alamat", "")).strip()
    if not nama or len(telp) < 8: return jsonify(error="Isi nama dan nomor telepon yang valid."), 400
    try:
        if datetime.date.fromisoformat(tgl) < datetime.date.today(): raise ValueError
    except ValueError:
        return jsonify(error="Pilih tanggal ambil/antar mulai hari ini."), 400
    items, total = [], 0
    for it in d.get("items", []):
        p = db().execute("SELECT * FROM produk WHERE id=? AND tersedia=1", (it.get("id"),)).fetchone()
        try: q = int(it.get("qty", 0))
        except (TypeError, ValueError): q = 0
        if not p or not 1 <= q <= 50: return jsonify(error="Ada produk yang tidak tersedia."), 400
        items.append({"id": p["id"], "nama": p["nama"], "harga": p["harga"], "qty": q}); total += p["harga"] * q
    if not items: return jsonify(error="Keranjang masih kosong."), 400
    kode = "RM-" + secrets.token_hex(3).upper()
    db().execute("INSERT INTO pesanan(kode,nama,telepon,alamat,tanggal,catatan,items,total,dibuat) VALUES(?,?,?,?,?,?,?,?,?)",
        (kode, nama, telp, alamat, tgl, str(d.get("catatan", ""))[:300], json.dumps(items), total, datetime.datetime.now().isoformat(timespec="minutes")))
    db().commit()
    return jsonify(kode=kode, total=total), 201

@app.get("/api/pesanan/<kode>")
def cek_pesanan(kode):
    r = db().execute("SELECT kode,tanggal,items,total,status FROM pesanan WHERE kode=?", (kode.upper(),)).fetchone()
    if not r: return jsonify(error="Kode pesanan tidak ditemukan."), 404
    return jsonify({**dict(r), "items": json.loads(r["items"])})

@app.post("/api/admin/login")
def login():
    if (request.get_json(silent=True) or {}).get("password") == ADMIN_PASSWORD:
        session["admin"] = True; return jsonify(ok=True)
    return jsonify(error="Password salah."), 401

@app.post("/api/admin/logout")
def logout(): session.clear(); return jsonify(ok=True)

@app.get("/api/admin/pesanan")
def admin_pesanan():
    if (e := admin_only()): return e
    return jsonify([{**dict(r), "items": json.loads(r["items"])} for r in db().execute("SELECT * FROM pesanan ORDER BY id DESC")])

@app.patch("/api/admin/pesanan/<int:i>")
def ubah_status(i):
    if (e := admin_only()): return e
    s = (request.get_json(silent=True) or {}).get("status")
    if s not in STATUS: return jsonify(error="Status tidak dikenal."), 400
    db().execute("UPDATE pesanan SET status=? WHERE id=?", (s, i)); db().commit(); return jsonify(ok=True)

@app.post("/api/admin/produk")
def tambah_produk():
    if (e := admin_only()): return e
    d = request.form if request.form else (request.get_json(silent=True) or {})
    nama = str(d.get("nama", "")).strip()
    try: harga = int(d.get("harga"))
    except (TypeError, ValueError): harga = 0
    if not nama or harga <= 0: return jsonify(error="Nama dan harga wajib diisi."), 400
    gambar = ""
    image = request.files.get("gambar")
    if image and image.filename:
        extension = os.path.splitext(secure_filename(image.filename))[1].lower()
        if extension not in ALLOWED_IMAGE_EXTENSIONS:
            return jsonify(error="Format foto harus JPG, PNG, atau WEBP."), 400
        gambar = secrets.token_hex(12) + extension
        image.save(os.path.join(BASE, "gambar", gambar))
    elif d.get("gambar"):
        gambar = os.path.basename(str(d.get("gambar", "")))
        extension = os.path.splitext(gambar)[1].lower()
        if extension not in ALLOWED_IMAGE_EXTENSIONS or not os.path.isfile(os.path.join(BASE, "gambar", gambar)):
            return jsonify(error="Foto produk tidak ditemukan atau formatnya tidak didukung."), 400
    db().execute("INSERT INTO produk(nama,kategori,harga,deskripsi,warna,isi,gambar) VALUES(?,?,?,?,?,?,?)",
        (nama, d.get("kategori") or "Kue Tart", harga, d.get("deskripsi", ""), d.get("warna") or "#FFB3C6",
         d.get("isi") or "#FFE6A7", gambar))
    db().commit(); return jsonify(ok=True), 201

@app.patch("/api/admin/produk/<int:i>")
def toggle_produk(i):
    if (e := admin_only()): return e
    db().execute("UPDATE produk SET tersedia=1-tersedia WHERE id=?", (i,)); db().commit(); return jsonify(ok=True)

@app.delete("/api/admin/produk/<int:i>")
def hapus_produk(i):
    if (e := admin_only()): return e
    db().execute("DELETE FROM produk WHERE id=?", (i,)); db().commit(); return jsonify(ok=True)

init()
if __name__ == "__main__":
    app.run(debug=True, port=5000)
