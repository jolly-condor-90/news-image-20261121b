# Audit — entri 3 (news-image-20261121b)

Perbaikan dibatasi pada panel peta entri 2; 35 berita, kartu, dan daftar tidak diubah.

## 1. Geometri

| Pemeriksaan | Hasil |
| --- | --- |
| Format berkas | PNG, 1024 × 1024 |
| Ukuran | 228.112 byte (< 1.048.576 byte) |
| Salinan deterministik | `main.ts` menghasilkan byte identik dua kali |
| Badge di dalam panel | 35/35,radius 6,5 px,garis tepi putih |
| Jarak antar badge | minimum 16,07 px (≥ 2 × 6,5 = 13) |
| Offset dari titik | maksimum 23,0 px (≤ 42) |
| Garis vs badge lain | 0 persilangan |
| Garis vs garis | 0 persilangan |
| Legenda + caption | di dalam panel, tidak terpotong |

## 2. Semantik

| Pemeriksaan | Hasil |
| --- | --- |
| Nomor berita | 1..35 tepat sekali |
| Jumlah badge | 35 = jumlah berita |
| Warna badge | sesuai region (7 warna) |
| Proyeksi | equirectangular, LAT_ATAS 83, LAT_BAWAH −58 |
| Benua | GeoJSON Natural Earth, Antarctica dilewati |
| Graticule | tiap 30°, warna #C6DEEA |
| 5 koordinat uji | Antalya, Riyadh, Peru, Brussels, Wellington — benar |

Warna region: Eropa #2C6FB0, Timur Tengah #D2691E, Afrika #2F8B5B, Asia #B43A2E, Amerika #7748A8, Oseania #118A8E, World #5A6472. Samudra #D8E8F1, daratan #EADCB9, garis pantai #B8A175.

## 3. Font setelah diskalakan ke 300 px (faktor 0,293)

| Elemen | Ukuran asli | @300 px |
| --- | --- | --- |
| Judul tanggal | 54 | 15,82 |
| Headline kartu utama | 19 | 5,57 |
| Headline kartu kecil | 17 | 4,98 |
| Nomor badge peta | 8 | 2,34 |
| Legenda peta | 8 | 2,34 |
| Caption peta | 8 | 2,34 |
| Teks daftar | 10 | 2,93 |

Semua elemen berada di atas ambang keterbacaan.

## Status

Lolos semua pemeriksaan lokal (`audit.py`, `verify.py`, `makefun check`). **Belum disubmit** — menunggu persetujuan.
