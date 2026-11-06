Cake Shop — impor database untuk InfinityFree

1. Buat database MySQL dari panel InfinityFree.
2. Buka phpMyAdmin, pilih database tersebut, lalu pilih Import.
3. Pilih cake_shop.sql dan jalankan impor.
4. Unggah folder gambar/ ke hosting; nama file foto produk harus tetap sama.

File SQL ini membuat tabel produk dan pesanan, lalu mengisi delapan produk katalog.
Data pesanan pelanggan yang tersimpan di toko.db tidak disertakan.

Catatan penting: aplikasi saat ini menggunakan Flask/Python dan SQLite (toko.db).
Impor SQL ini menyiapkan struktur dan data produk MySQL, tetapi tidak mengubah
aplikasi Flask menjadi aplikasi PHP/MySQL. Pastikan paket hosting Anda mendukung
Python/Flask, atau backend perlu dikonversi sebelum situs dapat berjalan di
InfinityFree.
