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
-- Table structure for table `historial_reportes`
--

DROP TABLE IF EXISTS `historial_reportes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historial_reportes` (
  `idHistorial` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `tipo` varchar(50) NOT NULL,
  `formato` varchar(20) NOT NULL,
  `fechaGeneracion` datetime NOT NULL,
  `usuario` varchar(100) DEFAULT NULL,
  `rutaArchivo` varchar(255) DEFAULT NULL,
  `exitoso` tinyint(1) NOT NULL,
  `error` text,
  PRIMARY KEY (`idHistorial`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historial_reportes`
--

LOCK TABLES `historial_reportes` WRITE;
/*!40000 ALTER TABLE `historial_reportes` DISABLE KEYS */;
INSERT INTO `historial_reportes` VALUES (1,'Reporte de Ventas Abril 2023','ventas_diarias','PDF','2025-03-26 00:00:00','admin','/static/reportes/ventas_diarias_20230416123045.pdf',1,NULL),(2,'Ventas por Cliente Q1 2023','ventas_por_cliente','PDF','2025-03-29 00:00:00','admin','/static/reportes/ventas_por_cliente_20230419154233.pdf',1,NULL),(3,'Inventario Actual Mayo 2023','inventario_stock_actual','PDF','2025-04-02 00:00:00','empleado1','/static/reportes/inventario_actual_20230423093055.pdf',1,NULL),(4,'Productos Más Vendidos Abril 2023','ventas_por_producto','PDF','2025-04-05 00:00:00','admin','/static/reportes/ventas_por_producto_20230426142211.pdf',1,NULL),(5,'Alertas de Caducidad Mayo 2023','inventario_caducidad','PDF','2025-04-07 00:00:00','empleado1','/static/reportes/caducidad_20230428112532.pdf',1,NULL),(6,'VentasDiarias','ventas_ventas_diarias','PDF','2025-04-10 22:52:16','Admin','C:\\Users\\checo\\Desktop\\Phyton\\CookieKing\\modulos\\reportes\\..\\..\\static\\reportes\\ventas_diarias_20250410225215.pdf',1,NULL),(7,'jhecjh','ventas_ventas_por_cliente','PDF','2025-04-10 23:00:00','Admin','C:\\Users\\checo\\Desktop\\Phyton\\CookieKing\\modulos\\reportes\\..\\..\\static\\reportes\\ventas_por_cliente_20250410230000.pdf',1,NULL),(8,'hh','inventario_stock_actual','PDF','2025-04-10 23:00:18','Admin','C:\\Users\\checo\\Desktop\\Phyton\\CookieKing\\modulos\\reportes\\..\\..\\static\\reportes\\inventario_actual_20250410230018.pdf',1,NULL),(9,'hh','inventario_caducidad','PDF','2025-04-10 23:00:25','Admin','C:\\Users\\checo\\Desktop\\Phyton\\CookieKing\\modulos\\reportes\\..\\..\\static\\reportes\\caducidad_20250410230025.pdf',1,NULL);
/*!40000 ALTER TABLE `historial_reportes` ENABLE KEYS */;
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
