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
-- Table structure for table `recetas`
--

DROP TABLE IF EXISTS `recetas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recetas` (
  `idReceta` int NOT NULL AUTO_INCREMENT,
  `nombreReceta` varchar(150) NOT NULL,
  `instruccionesReceta` text,
  `galletasProducidas` int DEFAULT NULL,
  `estatus` int NOT NULL,
  `idGalleta` int NOT NULL,
  PRIMARY KEY (`idReceta`),
  KEY `idGalleta` (`idGalleta`),
  CONSTRAINT `recetas_ibfk_1` FOREIGN KEY (`idGalleta`) REFERENCES `galletas` (`idGalleta`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recetas`
--

LOCK TABLES `recetas` WRITE;
/*!40000 ALTER TABLE `recetas` DISABLE KEYS */;
INSERT INTO `recetas` VALUES (1,'Receta Galleta de Chocolate','Mezclar los ingredientes secos. Añadir mantequilla y huevos. Incorporar el chocolate. Hornear a 180°C por 12 minutos.',50,1,1),(2,'Receta Galleta de Vainilla','Mezclar harina, polvo de hornear y sal. Batir mantequilla y azúcar. Añadir extracto de vainilla y huevos. Incorporar mezcla seca. Hornear a 175°C por 10 minutos.',60,1,2),(3,'Receta Galleta de Chispas','Cremar mantequilla y azúcar. Añadir huevos y vainilla. Incorporar secos tamizados. Agregar chispas de chocolate. Hornear 15 minutos a 170°C.',45,1,3),(4,'Receta Galleta de Avena','Mezclar avena, harina, azúcar y pasas. Añadir mantequilla derretida y huevos. Hornear por 15 minutos a 170°C.',50,1,4),(5,'Receta Galleta de Nuez','Cremar mantequilla con azúcar. Añadir huevos. Incorporar harina y nueces picadas. Hornear a 175°C por 12 minutos.',55,1,5),(6,'Receta Galleta de Coco','Batir mantequilla y azúcar. Añadir huevos y vainilla. Incorporar harina y coco rallado. Hornear a 165°C por 12 minutos.',50,1,6),(7,'Receta Galleta de Fresa','Mezclar ingredientes secos. Batir mantequilla y azúcar. Incorporar huevos. Añadir fresas deshidratadas. Hornear a 170°C por 12 minutos.',55,1,7),(8,'Receta Galleta de Limón','Cremar mantequilla y azúcar. Añadir ralladura y jugo de limón. Incorporar huevos y mezcla seca. Hornear a 170°C por 10 minutos.',60,1,8),(9,'Receta Galleta de Canela','Mezclar harina, canela y polvo de hornear. Batir mantequilla, azúcar y huevo. Incorporar secos. Hornear a 175°C por 12 minutos.',55,1,9),(10,'Receta Galleta Integral','Mezclar harina integral y trigo. Añadir avena. Incorporar huevos y mantequilla. Hornear a 165°C por 15 minutos.',40,1,10),(11,'Receta Galleta sin Gluten','Mezclar harinas sin gluten. Añadir polvo de hornear y sal. Incorporar mantequilla y huevos. Hornear a 160°C por 15 minutos.',35,1,11),(12,'Receta Galleta de Mantequilla','Batir mantequilla con azúcar. Añadir huevo y vainilla. Incorporar harina. Refrigerar 30 minutos. Hornear a 180°C por 10 minutos.',70,1,12);
/*!40000 ALTER TABLE `recetas` ENABLE KEYS */;
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
