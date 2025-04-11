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
-- Table structure for table `pagosproveedores`
--

DROP TABLE IF EXISTS `pagosproveedores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pagosproveedores` (
  `idPago` int NOT NULL AUTO_INCREMENT,
  `idProveedor` int NOT NULL,
  `fechaPago` date NOT NULL,
  `monto` float NOT NULL,
  `referencia` varchar(100) DEFAULT NULL,
  `idCompra` int DEFAULT NULL,
  `estatus` int NOT NULL,
  PRIMARY KEY (`idPago`),
  KEY `idProveedor` (`idProveedor`),
  KEY `idCompra` (`idCompra`),
  CONSTRAINT `pagosproveedores_ibfk_1` FOREIGN KEY (`idProveedor`) REFERENCES `proveedores` (`idProveedor`),
  CONSTRAINT `pagosproveedores_ibfk_2` FOREIGN KEY (`idCompra`) REFERENCES `comprasinsumos` (`idCompra`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pagosproveedores`
--

LOCK TABLES `pagosproveedores` WRITE;
/*!40000 ALTER TABLE `pagosproveedores` DISABLE KEYS */;
INSERT INTO `pagosproveedores` VALUES (1,1,'2023-02-15',8150,'TRANS-001',1,1),(2,2,'2023-02-25',4575,'TRANS-002',2,1),(3,3,'2023-03-10',2275,'TRANS-003',3,1),(4,4,'2023-03-20',4250,'TRANS-004',4,1),(5,5,'2023-03-30',1800,'TRANS-005',5,1),(6,1,'2023-04-10',3600,'TRANS-006',6,1),(7,2,'2023-04-20',5000,'TRANS-007',7,1),(8,3,'2023-05-05',4800,'TRANS-008',8,1),(9,4,'2023-05-15',5100,'TRANS-009',9,1),(10,1,'2023-06-01',3000,'ANTICIPO-001',10,1);
/*!40000 ALTER TABLE `pagosproveedores` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-11  0:53:28
