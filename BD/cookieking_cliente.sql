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
-- Table structure for table `cliente`
--

DROP TABLE IF EXISTS `cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cliente` (
  `idCliente` int NOT NULL AUTO_INCREMENT,
  `nombreCliente` varchar(250) NOT NULL,
  `fechaNacimiento` datetime DEFAULT NULL,
  `telefono` varchar(25) NOT NULL,
  `correo` varchar(150) DEFAULT NULL,
  `estatus` int NOT NULL,
  PRIMARY KEY (`idCliente`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cliente`
--

LOCK TABLES `cliente` WRITE;
/*!40000 ALTER TABLE `cliente` DISABLE KEYS */;
INSERT INTO `cliente` VALUES (1,'Juan Pérez','1985-06-15 00:00:00','5512345678','juan.perez@email.com',1),(2,'María González','1990-03-22 00:00:00','5587654321','maria.gonzalez@email.com',1),(3,'Carlos Rodríguez','1978-09-10 00:00:00','5523456789','carlos.rodriguez@email.com',1),(4,'Ana Martínez','1992-12-05 00:00:00','5534567890','ana.martinez@email.com',1),(5,'Roberto Sánchez','1982-04-18 00:00:00','5545678901','roberto.sanchez@email.com',1),(6,'Laura López','1995-07-30 00:00:00','5556789012','laura.lopez@email.com',1),(7,'Miguel Ramírez','1987-11-25 00:00:00','5567890123','miguel.ramirez@email.com',1),(8,'Sofía Torres','1993-02-08 00:00:00','5578901234','sofia.torres@email.com',1),(9,'Jorge Fernández','1975-08-20 00:00:00','5589012345','jorge.fernandez@email.com',0),(10,'Patricia Díaz','1989-01-12 00:00:00','5590123456','patricia.diaz@email.com',1),(11,'Hugo',NULL,'Sin especificar','vazquezcor@hotmail.com',1);
/*!40000 ALTER TABLE `cliente` ENABLE KEYS */;
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
