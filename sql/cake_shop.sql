-- Cake Shop database for MySQL/MariaDB (InfinityFree phpMyAdmin).
-- In phpMyAdmin, select the database created in InfinityFree, then import this file.
-- Product images are stored separately in the website's gambar/ folder.

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS `produk` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `nama` VARCHAR(150) NOT NULL,
  `kategori` VARCHAR(100) NOT NULL,
  `harga` INT UNSIGNED NOT NULL,
  `deskripsi` TEXT NOT NULL,
  `warna` CHAR(7) NOT NULL DEFAULT '#FFB3C6',
  `isi` CHAR(7) NOT NULL DEFAULT '#FFE6A7',
  `gambar` VARCHAR(255) NOT NULL DEFAULT '',
  `tersedia` TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `pesanan` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `kode` VARCHAR(20) NOT NULL,
  `nama` VARCHAR(150) NOT NULL,
  `telepon` VARCHAR(30) NOT NULL,
  `alamat` TEXT NOT NULL,
  `tanggal` DATE NOT NULL,
  `catatan` VARCHAR(300) NOT NULL DEFAULT '',
  `items` LONGTEXT NOT NULL,
  `total` BIGINT UNSIGNED NOT NULL,
  `status` VARCHAR(20) NOT NULL DEFAULT 'baru',
  `dibuat` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_pesanan_kode` (`kode`),
  KEY `idx_pesanan_status` (`status`),
  KEY `idx_pesanan_dibuat` (`dibuat`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO `produk`
  (`id`, `nama`, `kategori`, `harga`, `deskripsi`, `warna`, `isi`, `gambar`, `tersedia`)
VALUES
  (1, 'Red Velvet', 'Kue Tart', 285000, 'Sponge merah beludru, krim keju lembut.', '#F4F0EC', '#B3203E', 'Slice Of Classic Red Velvet Cake With Cream Cheese Frosting.jpeg', 1),
  (2, 'Cokelat Lava', 'Kue Tart', 265000, 'Tiga lapis cokelat pekat dengan ganache hangat.', '#6B3A2A', '#3E2018', 'Chocolate Lava Cake.jpeg', 1),
  (3, 'Strawberry Shortcake', 'Kue Tart', 295000, 'Krim segar, stroberi manis, bolu seputih awan.', '#FFB3C6', '#FFE6A7', 'The Ultimate Strawberry Shortcake Cake Recipe You Need to Try!.jpeg', 1),
  (4, 'Cheesecake Blueberry', 'Cheesecake', 245000, 'Panggang pelan, saus blueberry asam manis.', '#8E7CC3', '#F6E3B4', '1008102697847795669.jpeg', 1),
  (5, 'Cheesecake Matcha', 'Cheesecake', 255000, 'Matcha Uji yang tidak terlalu manis.', '#9CCB86', '#F6E3B4', 'Japanese Matcha Cheesecake _The perfect mix of creamy and earthy_ 🍵✨ Who’s a matcha fan_ #MatchaCheesecake_.jpeg', 1),
  (6, 'Lapis Legit', 'Kue Tradisional', 320000, 'Dua puluh lapis, wangi rempah dan mentega.', '#D9A441', '#8A4B1F', 'Lapis Legit.jpeg', 1),
  (7, 'Bolu Pandan', 'Kue Tradisional', 110000, 'Empuk, wangi pandan asli, parutan kelapa.', '#B7E4A0', '#6FA85A', '', 1),
  (8, 'Brownies Panggang', 'Brownies', 95000, 'Pinggir renyah, tengah fudgy, kacang almond.', '#5A3425', '#3A1F14', '', 1);
