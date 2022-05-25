CREATE DATABASE  IF NOT EXISTS `projectonedb` /*!40100 DEFAULT CHARACTER SET utf8 */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `projectonedb`;
-- MySQL dump 10.13  Distrib 8.0.28, for Win64 (x86_64)
--
-- Host: localhost    Database: projectonedb
-- ------------------------------------------------------
-- Server version	8.0.28

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
-- Table structure for table `acties`
--

DROP TABLE IF EXISTS `acties`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `acties` (
  `ActieID` int NOT NULL AUTO_INCREMENT,
  `actiebeschrijving` varchar(145) DEFAULT NULL,
  PRIMARY KEY (`ActieID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `acties`
--

LOCK TABLES `acties` WRITE;
/*!40000 ALTER TABLE `acties` DISABLE KEYS */;
INSERT INTO `acties` VALUES (1,'relay toggle'),(2,'raspi/toggle'),(3,'login'),(4,'toggle lcd info'),(5,'inlezen sensor');
/*!40000 ALTER TABLE `acties` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device`
--

DROP TABLE IF EXISTS `device`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `device` (
  `DeviceID` int NOT NULL AUTO_INCREMENT,
  `naam` varchar(45) NOT NULL,
  `merk` varchar(85) DEFAULT NULL,
  `beschrijving` varchar(150) DEFAULT NULL,
  `type` varchar(45) DEFAULT NULL,
  `aankoopkost` float DEFAULT NULL,
  `meeteenheid` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`DeviceID`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device`
--

LOCK TABLES `device` WRITE;
/*!40000 ALTER TABLE `device` DISABLE KEYS */;
INSERT INTO `device` VALUES (1,'ldr1','null','ldr voor detectie','Sensor',0.96,'Ohm'),(2,'ldr2','null','ldr voor detectie','Sensor',0.96,'Ohm'),(3,'ldr3','null','ldr voor detectie','Sensor',0.96,'Ohm'),(4,'ldr4','null','ldr voor detectie','Sensor',0.96,'Ohm'),(5,'ldr5','null','ldr voor detectie','Sensor',0.96,'Ohm'),(6,'ldr6','null','ldr voor detectie','Sensor',0.96,'Ohm'),(7,'rfid_scanner','null','rfid voor verificatie','RFID-Scanner',6.52,'null'),(8,'knop1','null','knop voor aan/uitzetten raspberry','Sensor',2.55,'null'),(9,'knop2','null','knop voor toggelen ip','Sensor',2.55,'null'),(10,'transistor','null','voor ledstrip','Actuator',1.96,'null'),(11,'relay','null','voor doorlock','Actuator',12.36,'null');
/*!40000 ALTER TABLE `device` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gebruiker`
--

DROP TABLE IF EXISTS `gebruiker`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gebruiker` (
  `gebruikersID` int NOT NULL,
  `naam` varchar(45) DEFAULT NULL,
  `wachtwoord` varchar(45) DEFAULT NULL,
  `rfid_code` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`gebruikersID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gebruiker`
--

LOCK TABLES `gebruiker` WRITE;
/*!40000 ALTER TABLE `gebruiker` DISABLE KEYS */;
INSERT INTO `gebruiker` VALUES (1,'Kobe','FvaA007','vVf56m9lK0');
/*!40000 ALTER TABLE `gebruiker` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historiek`
--

DROP TABLE IF EXISTS `historiek`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historiek` (
  `historiekID` int NOT NULL AUTO_INCREMENT,
  `actiedatum` datetime NOT NULL,
  `waarde` varchar(45) NOT NULL,
  `commentaar` varchar(160) DEFAULT NULL,
  `DeviceID` int NOT NULL,
  `ActieID` int DEFAULT NULL,
  PRIMARY KEY (`historiekID`),
  KEY `fk_historiek_Device_idx` (`DeviceID`),
  KEY `fk_historiek_Acties1_idx` (`ActieID`),
  CONSTRAINT `fk_historiek_Acties1` FOREIGN KEY (`ActieID`) REFERENCES `acties` (`ActieID`),
  CONSTRAINT `fk_historiek_Device` FOREIGN KEY (`DeviceID`) REFERENCES `device` (`DeviceID`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historiek`
--

LOCK TABLES `historiek` WRITE;
/*!40000 ALTER TABLE `historiek` DISABLE KEYS */;
INSERT INTO `historiek` VALUES (1,'2022-03-24 00:00:00','905','null',1,5),(2,'2022-03-30 00:00:00','74','null',1,5),(3,'2022-03-31 00:00:00','1006','null',2,5),(4,'2022-04-02 00:00:00','649','null',2,5),(5,'2022-04-04 00:00:00','36','null',3,5),(6,'2022-04-13 00:00:00','648','null',4,5),(7,'2022-04-14 00:00:00','1','toggle relay',11,1),(8,'2022-04-18 00:00:00','0','toggle raspi',8,2),(9,'2022-04-19 00:00:00','1','toggle raspi',8,2),(10,'2022-04-25 00:00:00','VdTPDNtd','RFID-Value',7,3),(11,'2022-04-26 00:00:00','ychYxrF2','RFID-Value',7,3),(12,'2022-04-28 00:00:00','Pec5XvZd','RFID-Value',7,3),(13,'2022-04-29 00:00:00','ZwKmnrCM','RFID-Value',7,3),(14,'2022-04-30 00:00:00','208','null',6,5),(15,'2022-05-01 00:00:00','774','null',5,5),(16,'2022-05-06 00:00:00','246','null',1,5),(17,'2022-05-08 00:00:00','258','null',2,5),(18,'2022-05-09 00:00:00','333','transistor value',10,5),(19,'2022-05-10 00:00:00','543','transistor value',10,5),(20,'2022-05-11 00:00:00','25','transistor value',10,5),(21,'2022-05-13 00:00:00','43','transistor value',10,5),(22,'2022-05-18 00:00:00','83','transistor value',10,5),(23,'2022-05-26 00:00:00','164','null',5,5),(24,'2022-05-28 00:00:00','850','null',4,5),(25,'2022-05-30 00:00:00','682','null',6,5),(26,'2022-03-12 00:00:00','668','null',2,5),(27,'2022-03-15 00:00:00','880','null',3,5),(28,'2022-03-18 00:00:00','891','null',1,5),(29,'2022-03-20 00:00:00','445','null',5,5),(30,'2022-03-22 00:00:00','107','null',6,5),(31,'2022-03-28 00:00:00','fBQkXzFM','RFID-Value',7,3),(32,'2022-03-29 00:00:00','B42EsBfz','RFID-Value',7,3),(33,'2022-03-30 00:00:00','SSXZZ4zw','RFID-Value',7,3),(34,'2022-04-01 00:00:00','dVxRXLSd','RFID-Value',7,3),(35,'2022-04-03 00:00:00','55UR7XDc','RFID-Value',7,3),(36,'2022-04-04 00:00:00','ePe3C9pK','RFID-Value',7,3),(37,'2022-04-05 00:00:00','U28JAEhp','RFID-Value',7,3),(38,'2022-04-08 00:00:00','PF7LetM3','RFID-Value',7,3),(39,'2022-04-11 00:00:00','359','null',1,5),(40,'2022-04-13 00:00:00','31','null',2,5),(41,'2022-04-17 00:00:00','687','null',4,5),(42,'2022-04-18 00:00:00','1','toggle relay',11,1),(43,'2022-04-20 00:00:00','875','null',1,5),(44,'2022-04-21 00:00:00','453','null',5,5),(45,'2022-04-23 00:00:00','239','null',6,5),(46,'2022-05-03 00:00:00','423','null',3,5),(47,'2022-05-11 00:00:00','357','null',2,5),(48,'2022-05-12 00:00:00','943','null',2,5),(49,'2022-05-29 00:00:00','eWtHcVRs','RFID-Value',7,3),(50,'2022-05-31 00:00:00','757','null',2,5);
/*!40000 ALTER TABLE `historiek` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-05-25 11:02:03
