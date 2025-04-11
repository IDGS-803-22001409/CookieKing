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
-- Table structure for table `producciondetalles`
--

DROP TABLE IF EXISTS `producciondetalles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `producciondetalles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `produccion_id` int NOT NULL,
  `ingrediente_id` int NOT NULL,
  `cantidad_requerida` float NOT NULL,
  `cantidad_usada` float NOT NULL,
  `estado` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `produccion_id` (`produccion_id`),
  KEY `ingrediente_id` (`ingrediente_id`),
  CONSTRAINT `producciondetalles_ibfk_1` FOREIGN KEY (`produccion_id`) REFERENCES `produccion` (`idProduccion`),
  CONSTRAINT `producciondetalles_ibfk_2` FOREIGN KEY (`ingrediente_id`) REFERENCES `ingredientes` (`idIngrediente`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producciondetalles`
--

LOCK TABLES `producciondetalles` WRITE;
/*!40000 ALTER TABLE `producciondetalles` DISABLE KEYS */;
INSERT INTO `producciondetalles` VALUES (1,1,1,2.5,2.5,1),(2,1,2,1.5,1.5,1),(3,1,3,1,1,1),(4,1,4,20,20,1),(5,1,5,1,1,1),(6,1,8,0.1,0.1,1),(7,1,9,0.05,0.05,1),(8,2,1,2,2,1),(9,2,2,1.2,1.2,1),(10,2,3,0.8,0.8,1),(11,2,4,15,15,1),(12,2,7,0.1,0.1,1),(13,2,8,0.08,0.08,1),(14,2,9,0.04,0.04,1),(15,3,1,2.2,2.2,1),(16,3,2,1.3,1.3,1),(17,3,3,1,1,1),(18,3,4,18,18,1),(19,3,6,1,1,1),(20,3,7,0.05,0.05,1),(21,3,8,0.09,0.09,1),(22,3,9,0.05,0.05,1);
/*!40000 ALTER TABLE `producciondetalles` ENABLE KEYS */;
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
