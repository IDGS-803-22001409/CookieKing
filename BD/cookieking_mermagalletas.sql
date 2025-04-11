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
-- Table structure for table `mermagalletas`
--

DROP TABLE IF EXISTS `mermagalletas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mermagalletas` (
  `idMerma` int NOT NULL AUTO_INCREMENT,
  `galleta_id` int NOT NULL,
  `cantidad` int NOT NULL,
  `descripcion` text NOT NULL,
  `fecha_registro` datetime DEFAULT NULL,
  PRIMARY KEY (`idMerma`),
  KEY `galleta_id` (`galleta_id`),
  CONSTRAINT `mermagalletas_ibfk_1` FOREIGN KEY (`galleta_id`) REFERENCES `galletas` (`idGalleta`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mermagalletas`
--

LOCK TABLES `mermagalletas` WRITE;
/*!40000 ALTER TABLE `mermagalletas` DISABLE KEYS */;
INSERT INTO `mermagalletas` VALUES (1,1,5,'Galletas rotas durante el transporte','2025-04-03 00:00:00'),(2,3,8,'Galletas con defectos de cocción - muy oscuras','2025-04-04 00:00:00'),(3,5,3,'Galletas rotas durante el empaquetado','2025-04-05 00:00:00'),(4,2,6,'Galletas caducadas','2025-04-06 00:00:00'),(5,7,4,'Galletas con textura inadecuada - muy duras','2025-04-07 00:00:00');
/*!40000 ALTER TABLE `mermagalletas` ENABLE KEYS */;
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
