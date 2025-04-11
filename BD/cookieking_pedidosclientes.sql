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
-- Table structure for table `pedidosclientes`
--

DROP TABLE IF EXISTS `pedidosclientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedidosclientes` (
  `idPedido` int NOT NULL AUTO_INCREMENT,
  `idCliente` int NOT NULL,
  `fechaPedido` datetime NOT NULL,
  `fechaEntrega` date DEFAULT NULL,
  `instrucciones` text,
  `estatus` int NOT NULL,
  `total` float NOT NULL,
  PRIMARY KEY (`idPedido`),
  KEY `idCliente` (`idCliente`),
  CONSTRAINT `pedidosclientes_ibfk_1` FOREIGN KEY (`idCliente`) REFERENCES `cliente` (`idCliente`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedidosclientes`
--

LOCK TABLES `pedidosclientes` WRITE;
/*!40000 ALTER TABLE `pedidosclientes` DISABLE KEYS */;
INSERT INTO `pedidosclientes` VALUES (1,1,'2025-03-21 00:00:00','2025-03-27','Entregar en la mañana. Paquetes individuales.',2,625),(2,2,'2025-03-25 00:00:00','2025-03-28','Evento corporativo. Incluir servilletas.',2,450),(3,3,'2025-03-26 00:00:00','2025-03-30','Reunion familiar. Asegurarse que estén frescas.',2,540),(4,4,'2025-03-27 00:00:00','2025-03-31','Cumpleaños infantil. Empaquetar colorido.',2,337.5),(5,5,'2025-03-29 00:00:00','2025-04-02','Reunión oficina. Entregar antes de las 10am.',2,405),(6,6,'2025-03-31 00:00:00','2025-04-03','Para cafetería escolar. Empaquetar en cajas de 20.',2,495),(7,7,'2025-04-01 00:00:00','2025-04-04','Fiesta de té. Presentación elegante.',2,562.5),(8,8,'2025-04-02 00:00:00','2025-04-05','Merienda familiar. Galletas de tamaño regular.',2,270),(9,1,'2025-04-03 00:00:00','2025-04-07','Para evento empresarial. Logos corporativos en empaque.',2,420),(10,2,'2025-04-05 00:00:00','2025-04-08','Reunión semanal. Empaquetar por tipos.',2,315),(11,3,'2025-04-07 00:00:00','2025-04-09','Para cafetería. Entregar temprano.',2,390),(12,5,'2025-04-08 00:00:00','2025-04-12','Evento familiar. Paquetes individuales.',1,480),(13,6,'2025-04-09 00:00:00','2025-04-13','Para venta en tienda. Surtido variado.',1,525),(14,8,'2025-04-10 00:00:00','2025-04-15','Fiesta infantil. Empaquetar por colores.',2,375),(15,11,'2025-04-10 23:03:24','2025-04-12','Hola',2,169.5);
/*!40000 ALTER TABLE `pedidosclientes` ENABLE KEYS */;
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
