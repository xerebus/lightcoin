-- MySQL dump 10.13  Distrib 5.7.16, for Linux (x86_64)
--
-- Host: 192.168.0.105    Database: store
-- ------------------------------------------------------
-- Server version	5.7.16-0ubuntu0.16.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `product`
--

DROP TABLE IF EXISTS `product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `product` (
  `upc` int(11) NOT NULL,
  `pack_size` int(11) NOT NULL,
  `product_line_id` int(11) NOT NULL,
  `sale_price` decimal(7,2) NOT NULL,
  `cost_price` decimal(7,2) NOT NULL,
  `in_stock` int(11) NOT NULL,
  `restock_min` int(11) DEFAULT NULL,
  PRIMARY KEY (`upc`),
  KEY `product_line_id` (`product_line_id`),
  CONSTRAINT `product_ibfk_1` FOREIGN KEY (`product_line_id`) REFERENCES `product_line` (`product_line_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product`
--

LOCK TABLES `product` WRITE;
/*!40000 ALTER TABLE `product` DISABLE KEYS */;
INSERT INTO `product` VALUES (12333,1,2348882,1.99,0.50,-1,50),(12334,2,2348882,2.99,1.00,1,50),(12335,12,2348882,9.99,6.00,0,50),(12448,2,2348991,6.99,3.00,42,50),(12449,4,2348991,10.99,6.00,26,50),(13001,50,2349000,4.99,2.00,3,NULL),(13002,100,2349000,7.99,3.50,0,NULL),(13051,30,2349500,7.99,5.00,0,NULL),(13052,60,2349500,16.99,10.00,20,NULL);
/*!40000 ALTER TABLE `product` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-01-06 14:23:04
