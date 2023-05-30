
# Inventaris Barang

Pengelolaan dan pemantauan keseluruhan tentang bahan baku yang digunakan dalam produksi roti.


## Data Format
Tabel Barang

| Field            | Type            | Description       |
|------------------|-----------------|-------------------|
| id (Primary Key) | varchar(255)    | Primary Key       |
| nama             | varchar(255)    |                   |
| tgl_beli         | date            |                   |
| harga_beli       | bigint(20)      |                   |
| date_expired     | date            |                   |
| quantity_barang  | int(255)        |                   |
| lokasi           | varchar(255)    |Foreign Key        |
| supplier         | varchar(255)    |Foreign Key        |
| status           | varchar(255)    |                   |

Tabel Lokasi
| Field            | Type            | Description                           |
|------------------|-----------------|---------------------------------------|
| id | varchar(255)    | Primary Key                     |
| capacity         | bigint(20)      | |


Tabel Pengeluaran Barang
| Field          | Type             | Description                           |
|----------------|------------------|---------------------------------------|
| id| varchar(255)     | Primary Key              |
| id_barang (Foreign Key) | varchar(255) |Foreign Key        |
| kategori       | varchar(255)     |               |
| jml_keluar     | int(11)          |        |
| tgl_keluar     | date             |        |


## Isi Kegiatan Program
**Read**
* Tampil Semua Data Barang
* Cari Barang Berdasarkan Nama
* Tampil Semua Data Supplier
* Cari Supplier Berdasarkan Nama
* Tampil Data Kapasitas Storage
* Tampil Data Pengeluaran Barang
* Tampil Status Expired Barang

**Add**

* Add Barang
* Add Supplier

**Update**

* Update Barang
* Update Supplier

**Delete**

* Delete Barang
* Pengeluaran Barang
* Delete Supplier
## Features

* Store data in mysql
* Sorting date expired (Bubble Sort Algorithm)
* Realtime availability datastorage by referencing a product id

## Authors
Fariz Ikhsan Aditya
- [@fariz.ikhsan](https://github.com/farizikhsann)

