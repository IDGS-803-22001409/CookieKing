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
-- Table structure for table `recetaingredientes`
--

DROP TABLE IF EXISTS `recetaingredientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recetaingredientes` (
  `receta_id` int NOT NULL,
  `ingrediente_id` int NOT NULL,
  `cantidad` float NOT NULL,
  PRIMARY KEY (`receta_id`,`ingrediente_id`),
  KEY `ingrediente_id` (`ingrediente_id`),
  CONSTRAINT `recetaingredientes_ibfk_1` FOREIGN KEY (`receta_id`) REFERENCES `recetas` (`idReceta`),
  CONSTRAINT `recetaingredientes_ibfk_2` FOREIGN KEY (`ingrediente_id`) REFERENCES `ingredientes` (`idIngrediente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recetaingredientes`
--

LOCK TABLES `recetaingredientes` WRITE;
/*!40000 ALTER TABLE `recetaingredientes` DISABLE KEYS */;
INSERT INTO `recetaingredientes` VALUES (1,1,2.5),(1,2,1.5),(1,3,1),(1,4,20),(1,5,1),(1,8,0.1),(1,9,0.05),(2,1,2),(2,2,1.2),(2,3,0.8),(2,4,15),(2,7,0.1),(2,8,0.08),(2,9,0.04),(3,1,2.2),(3,2,1.3),(3,3,1),(3,4,18),(3,6,1),(3,7,0.05),(3,8,0.09),(3,9,0.05),(4,1,1.5),(4,2,1),(4,3,0.8),(4,4,15),(4,8,0.07),(4,9,0.04),(4,11,1),(5,1,2),(5,2,1.2),(5,3,0.9),(5,4,16),(5,8,0.08),(5,9,0.04),(5,10,0.8);
/*!40000 ALTER TABLE `recetaingredientes` ENABLE KEYS */;
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
