# Cake Shop
Jalankan:
    pip install -r requirements.txt
    python app.py
Buka http://localhost:5000  |  Admin: http://localhost:5000/admin (password default: admin123,
ganti dengan variabel lingkungan ADMIN_PASSWORD dan SECRET_KEY).
Foto produk yang sudah tersedia di folder `gambar/` otomatis dipasangkan ke menu yang sesuai. Admin juga bisa mengunggah foto langsung saat menambah produk (JPG, PNG, atau WEBP, maksimal 5 MB).
Tanpa foto, kue tampil sebagai ilustrasi sesuai warna yang dipilih.
