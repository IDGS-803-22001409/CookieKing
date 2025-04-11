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
-- Table structure for table `comprasdetalles`
--

DROP TABLE IF EXISTS `comprasdetalles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comprasdetalles` (
  `idCompraDetalle` int NOT NULL AUTO_INCREMENT,
  `idCompra` int NOT NULL,
  `idIngrediente` int NOT NULL,
  `cantidad` float NOT NULL,
  `precio_unitario` float NOT NULL,
  `subtotal` float NOT NULL,
  `fecha_expiracion` date DEFAULT NULL,
  PRIMARY KEY (`idCompraDetalle`),
  KEY `idCompra` (`idCompra`),
  KEY `idIngrediente` (`idIngrediente`),
  CONSTRAINT `comprasdetalles_ibfk_1` FOREIGN KEY (`idCompra`) REFERENCES `comprasinsumos` (`idCompra`),
  CONSTRAINT `comprasdetalles_ibfk_2` FOREIGN KEY (`idIngrediente`) REFERENCES `ingredientes` (`idIngrediente`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comprasdetalles`
--

LOCK TABLES `comprasdetalles` WRITE;
/*!40000 ALTER TABLE `comprasdetalles` DISABLE KEYS */;
INSERT INTO `comprasdetalles` VALUES (1,1,1,100,18.5,1850,'2025-10-10'),(2,1,2,80,22.75,1820,'2026-04-10'),(3,1,8,30,65,1950,'2026-02-10'),(4,1,9,50,12,600,'2027-04-10'),(5,1,11,50,25,1250,'2026-01-10'),(6,1,15,3,250,750,'2026-04-10'),(7,2,1,200,18.5,3700,'2025-10-10'),(8,2,8,10,65,650,'2026-02-10'),(9,2,9,15,15,225,'2027-04-10'),(10,3,2,100,22.75,2275,'2026-04-10'),(11,4,3,50,85,4250,'2025-07-10'),(12,5,7,10,180,1800,'2026-04-10'),(13,6,4,800,2.5,2000,'2025-05-10'),(14,6,10,10,160,1600,'2025-09-10'),(15,7,5,25,120,3000,'2025-12-10'),(16,7,6,20,100,2000,'2025-12-10'),(17,8,12,20,110,2200,'2025-10-10'),(18,8,13,13,200,2600,'2025-10-10'),(19,9,3,30,85,2550,'2025-07-10'),(20,9,14,10,80,800,'2025-07-10'),(21,9,15,7,250,1750,'2026-04-10'),(22,10,1,100,18.5,1850,'2025-10-10'),(23,10,2,80,22.75,1820,'2026-04-10'),(24,10,5,15,120,1800,'2025-12-10'),(25,10,10,10,160,1600,'2025-09-10');
/*!40000 ALTER TABLE `comprasdetalles` ENABLE KEYS */;
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
