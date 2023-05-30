/*
SQLyog Ultimate v12.5.1 (32 bit)
MySQL - 10.4.28-MariaDB : Database - capstone_1
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`capstone_1` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;

USE `capstone_1`;

/*Table structure for table `barang` */

DROP TABLE IF EXISTS `barang`;

CREATE TABLE `barang` (
  `id` varchar(255) NOT NULL,
  `nama` varchar(255) DEFAULT NULL,
  `tgl_beli` date DEFAULT NULL,
  `harga_beli` bigint(20) DEFAULT NULL,
  `date_expired` date DEFAULT NULL,
  `quantity_barang` int(255) DEFAULT NULL,
  `lokasi` varchar(255) DEFAULT NULL,
  `supplier` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_barang_lokasi` (`lokasi`),
  KEY `fk_barang_supplier` (`supplier`),
  CONSTRAINT `fk_barang_lokasi` FOREIGN KEY (`lokasi`) REFERENCES `storage` (`id`),
  CONSTRAINT `fk_barang_supplier` FOREIGN KEY (`supplier`) REFERENCES `supplier` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `barang` */

insert  into `barang`(`id`,`nama`,`tgl_beli`,`harga_beli`,`date_expired`,`quantity_barang`,`lokasi`,`supplier`) values 
('brg-1','Gula','2020-09-01',1500,'2023-06-15',500,'lok-2','supp-1'),
('brg-2','Tepung','2020-11-05',2500,'2023-06-02',3500,'lok-2','supp-2'),
('brg-3','Telur','2023-05-25',1100,'2024-05-25',50,'lok-1','supp-1'),
('brg-4','Mentega','2023-05-27',2100,'2023-05-18',75,'lok-3','supp-2');

/*Table structure for table `pengeluaran` */

DROP TABLE IF EXISTS `pengeluaran`;

CREATE TABLE `pengeluaran` (
  `id` varchar(255) NOT NULL,
  `id_barang` varchar(255) DEFAULT NULL,
  `kategori` varchar(255) DEFAULT NULL,
  `jml_keluar` int(11) DEFAULT NULL,
  `tgl_keluar` date DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `pengeluaran` */

insert  into `pengeluaran`(`id`,`id_barang`,`kategori`,`jml_keluar`,`tgl_keluar`) values 
('out-2','brg-100','expired',300,'2023-05-28');

/*Table structure for table `storage` */

DROP TABLE IF EXISTS `storage`;

CREATE TABLE `storage` (
  `id` varchar(255) NOT NULL,
  `capacity` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `storage` */

insert  into `storage`(`id`,`capacity`) values 
('lok-1',5000),
('lok-2',10000),
('lok-3',20000);

/*Table structure for table `supplier` */

DROP TABLE IF EXISTS `supplier`;

CREATE TABLE `supplier` (
  `id` varchar(255) NOT NULL,
  `nama` varchar(255) DEFAULT NULL,
  `alamat` varchar(255) DEFAULT NULL,
  `kontak` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `supplier` */

insert  into `supplier`(`id`,`nama`,`alamat`,`kontak`) values 
('supp-1','PT SugarManis','Bandung','012345'),
('supp-2','PT TepungIndo','Jakarta','01234'),
('supp-3','NoRelation','Surabaya','212323');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
