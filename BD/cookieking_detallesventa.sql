-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: cookieking
-- ------------------------------------------------------
-- Server version	8.0.36

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `detallesventa`
--

DROP TABLE IF EXISTS `detallesventa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detallesventa` (
  `id` int NOT NULL AUTO_INCREMENT,
  `venta_id` int NOT NULL,
  `galleta_id` int NOT NULL,
  `cantidad` int NOT NULL,
  `precio_unitario` float NOT NULL,
  `subtotal` float NOT NULL,
  `tipo_venta` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `venta_id` (`venta_id`),
  KEY `galleta_id` (`galleta_id`),
  CONSTRAINT `detallesventa_ibfk_1` FOREIGN KEY (`venta_id`) REFERENCES `ventas` (`idVenta`),
  CONSTRAINT `detallesventa_ibfk_2` FOREIGN KEY (`galleta_id`) REFERENCES `galletas` (`idGalleta`)
) ENGINE=InnoDB AUTO_INCREMENT=64 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detallesventa`
--

LOCK TABLES `detallesventa` WRITE;
/*!40000 ALTER TABLE `detallesventa` DISABLE KEYS */;
INSERT INTO `detallesventa` VALUES (1,1,1,10,12.5,125,1),(2,1,3,10,15,150,1),(3,1,5,5,14,70,1),(4,1,2,2,45,90,0),(5,1,6,4,54,216,0),(6,2,3,20,15,300,1),(7,2,10,4,16,64,1),(8,2,2,2,43,86,0),(9,3,1,15,12.5,187.5,1),(10,3,9,9,12.5,112.5,1),(11,4,4,15,13.5,202.5,1),(12,4,7,12,13,156,1),(13,4,3,2,67.5,135,0),(14,4,5,1,46.5,46.5,0),(15,5,8,15,11.5,172.5,1),(16,5,11,5,18,90,1),(17,5,9,1,75,75,0),(18,6,12,10,9.5,95,1),(19,6,2,4,10,40,1),(20,6,9,1,40,40,0),(21,7,3,15,15,225,1),(22,7,6,10,12,120,1),(23,7,5,1,60,60,0),(24,8,1,10,12.5,125,1),(25,8,4,20,13.5,270,1),(26,8,8,2,50,100,0),(27,9,5,15,14,210,1),(28,9,10,10,16,160,1),(29,9,3,3,67.5,202.5,0),(30,10,2,15,10,150,1),(31,10,9,6,12.5,75,1),(32,10,8,1,45,45,0),(33,11,7,5,13,65,1),(34,11,12,10,9.5,95,1),(35,11,4,1,35,35,0),(36,12,6,10,12,120,1),(37,12,10,10,16,160,1),(38,12,2,3,45,135,0),(39,12,4,1,5,5,0),(40,13,3,15,15,225,1),(41,13,8,5,11.5,57.5,1),(42,13,6,1,32.5,32.5,0),(43,14,1,10,12.5,125,1),(44,14,5,10,14,140,1),(45,14,9,10,12.5,125,1),(46,15,4,10,13.5,135,1),(47,15,11,5,18,90,1),(48,15,12,1,37.5,37.5,0),(49,16,2,20,10,200,1),(50,16,4,15,13.5,202.5,1),(51,16,9,10,12.5,125,1),(52,16,3,1,22.5,22.5,0),(53,17,1,4,12.5,50,1),(54,17,6,2,54,108,0),(55,17,8,1,11.5,11.5,1),(56,18,1,1,12.5,12.5,1),(57,18,2,1,10,10,1),(58,18,3,1,67.5,67.5,0),(59,18,4,2,13.5,27,1),(60,18,5,2,63,126,0),(61,18,6,1,12,12,1),(62,18,7,3,58.5,175.5,0),(63,18,8,1,11.5,11.5,1);
/*!40000 ALTER TABLE `detallesventa` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-11  0:53:27
