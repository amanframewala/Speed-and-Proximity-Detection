-- MySQL dump 10.13  Distrib 5.7.23, for Linux (x86_64)
--
-- Host: localhost    Database: SPD
-- ------------------------------------------------------
-- Server version	5.7.23-0ubuntu0.18.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `speeds`
--

DROP TABLE IF EXISTS `speeds`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `speeds` (
  `speed` float DEFAULT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `speeds`
--

LOCK TABLES `speeds` WRITE;
/*!40000 ALTER TABLE `speeds` DISABLE KEYS */;
INSERT INTO `speeds` (`speed`, `time`) VALUES (10,'2018-10-21 10:05:04'),(45,'2018-10-21 10:05:36'),(61,'2018-10-21 10:05:47'),(61,'2018-10-21 10:05:51'),(68,'2018-10-21 10:06:00'),(68,'2018-10-21 10:06:16'),(68,'2018-10-21 10:06:21'),(90,'2018-10-21 10:06:50'),(90,'2018-10-21 10:06:56'),(90,'2018-10-21 10:07:03'),(90,'2018-10-21 10:07:24'),(60,'2018-10-21 10:12:35'),(60,'2018-10-21 10:12:55'),(61,'2018-10-21 10:13:21');
/*!40000 ALTER TABLE `speeds` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER newEntryCheck 
AFTER INSERT ON speeds FOR EACH ROW
BEGIN

DECLARE current_speed FLOAT;
DECLARE current_timevalue TIMESTAMP;
DECLARE prev_warningRecorded TIMESTAMP;
DECLARE prev_warningsSent INT;
DECLARE prev_offenceRecorded TIMESTAMP;
DECLARE prev_offenceRegistered INT;

SELECT speed, time
INTO current_speed, current_timevalue
FROM speeds
ORDER BY time DESC
LIMIT 1;

SELECT warningRecorded, warningsSent, offenceRecorded, offenceRegistered
INTO prev_warningRecorded, prev_warningsSent, prev_offenceRecorded, prev_offenceRegistered
FROM speed
ORDER BY recordedTime DESC
LIMIT 1;

IF current_speed > 80 AND current_timevalue - prev_offenceRecorded > 15 THEN
INSERT INTO speed(speedValue, recordedTime, warningRecorded, warningsSent, offenceRecorded, offenceRegistered) VALUES (current_speed, current_timevalue, prev_warningRecorded, prev_warningsSent, current_timevalue, prev_offenceRegistered + 1);

ELSEIF current_speed > 60 AND current_speed < 81 AND current_timevalue - prev_warningRecorded > 15 THEN
INSERT INTO speed(speedValue, recordedTime, warningRecorded, warningsSent, offenceRecorded, offenceRegistered) VALUES (current_speed, current_timevalue, current_timevalue, prev_warningsSent + 1, prev_offenceRecorded, prev_offenceRegistered);

ELSE
INSERT INTO speed(speedValue, recordedTime, warningRecorded, warningsSent, offenceRecorded, offenceRegistered) VALUES (current_speed, current_timevalue, prev_warningRecorded, prev_warningsSent, prev_offenceRecorded, prev_offenceRegistered);

END IF;

END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-10-21 17:02:38
