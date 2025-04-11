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
-- Table structure for table `movimientosinsumos`
--

DROP TABLE IF EXISTS `movimientosinsumos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimientosinsumos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ingrediente_id` int NOT NULL,
  `tipo_movimiento` int NOT NULL,
  `cantidad` float NOT NULL,
  `fecha_movimiento` date NOT NULL,
  `referencia` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ingrediente_id` (`ingrediente_id`),
  CONSTRAINT `movimientosinsumos_ibfk_1` FOREIGN KEY (`ingrediente_id`) REFERENCES `ingredientes` (`idIngrediente`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimientosinsumos`
--

LOCK TABLES `movimientosinsumos` WRITE;
/*!40000 ALTER TABLE `movimientosinsumos` DISABLE KEYS */;
INSERT INTO `movimientosinsumos` VALUES (1,1,0,100,'2025-03-11','Compra inicial'),(2,2,0,80,'2025-03-11','Compra inicial'),(3,3,0,50,'2025-03-11','Compra inicial'),(4,4,0,800,'2025-03-11','Compra inicial'),(5,5,0,25,'2025-03-11','Compra inicial'),(6,6,0,30,'2025-03-11','Compra inicial'),(7,7,0,10,'2025-03-11','Compra inicial'),(8,8,0,10,'2025-03-11','Compra inicial'),(9,9,0,15,'2025-03-11','Compra inicial'),(10,10,0,20,'2025-03-11','Compra inicial'),(11,1,1,2.5,'2025-03-27','Producción #1'),(12,2,1,1.5,'2025-03-27','Producción #1'),(13,3,1,1,'2025-03-27','Producción #1'),(14,4,1,20,'2025-03-27','Producción #1'),(15,5,1,1,'2025-03-27','Producción #1'),(16,8,1,0.1,'2025-03-27','Producción #1'),(17,9,1,0.05,'2025-03-27','Producción #1'),(18,1,1,2,'2025-03-28','Producción #2'),(19,2,1,1.2,'2025-03-28','Producción #2'),(20,3,1,0.8,'2025-03-28','Producción #2'),(21,4,1,15,'2025-03-28','Producción #2'),(22,7,1,0.1,'2025-03-28','Producción #2'),(23,8,1,0.08,'2025-03-28','Producción #2'),(24,9,1,0.04,'2025-03-28','Producción #2'),(25,4,2,5,'2025-03-31','Merma: Rotos por manipulación'),(26,3,2,0.2,'2025-04-02','Merma: Caducidad del producto'),(27,6,2,0.5,'2025-04-05','Merma: Caída accidental');
/*!40000 ALTER TABLE `movimientosinsumos` ENABLE KEYS */;
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
