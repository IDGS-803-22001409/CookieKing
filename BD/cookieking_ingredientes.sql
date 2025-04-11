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
-- Table structure for table `ingredientes`
--

DROP TABLE IF EXISTS `ingredientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ingredientes` (
  `idIngrediente` int NOT NULL AUTO_INCREMENT,
  `nombreIngrediente` varchar(255) NOT NULL,
  `stock` float NOT NULL,
  `unidad` varchar(50) DEFAULT NULL,
  `stock_minimo` float NOT NULL,
  `precio_unitario` float NOT NULL,
  `fecha_expiracion` date DEFAULT NULL,
  PRIMARY KEY (`idIngrediente`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ingredientes`
--

LOCK TABLES `ingredientes` WRITE;
/*!40000 ALTER TABLE `ingredientes` DISABLE KEYS */;
INSERT INTO `ingredientes` VALUES (1,'Harina de Trigo',150,'kg',25,18.5,'2025-10-10'),(2,'Azúcar Refinada',90,'kg',20,22.75,'2026-04-10'),(3,'Mantequilla',45,'kg',10,85,'2025-07-10'),(4,'Huevo',500,'unidad',100,2.5,'2025-05-10'),(5,'Chocolate Amargo',35,'kg',8,120,'2025-12-10'),(6,'Chispas de Chocolate',40,'kg',10,95,'2025-12-10'),(7,'Extracto de Vainilla',10,'l',2,180,'2026-04-10'),(8,'Polvo para Hornear',8,'kg',2,65,'2026-02-10'),(9,'Sal',15,'kg',3,12,'2027-04-10'),(10,'Nueces',25,'kg',5,160,'2025-09-10'),(11,'Avena',50,'kg',10,25,'2026-01-10'),(12,'Coco Rallado',12,'kg',3,110,'2025-10-10'),(13,'Fresas Deshidratadas',8,'kg',2,200,'2025-10-10'),(14,'Limón (Ralladura)',5,'kg',1,80,'2025-07-10'),(15,'Canela Molida',4,'kg',1,200,'2026-04-10');
/*!40000 ALTER TABLE `ingredientes` ENABLE KEYS */;
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
