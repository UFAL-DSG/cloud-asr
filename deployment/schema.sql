-- Adminer 4.2.0 MySQL dump

SET NAMES utf8mb4;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

DROP TABLE IF EXISTS `hypothesis`;
CREATE TABLE `hypothesis` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `recording_id` binary(16) DEFAULT NULL,
  `text` text COLLATE utf8_unicode_ci,
  `confidence` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `recording_id` (`recording_id`),
  CONSTRAINT `hypothesis_ibfk_1` FOREIGN KEY (`recording_id`) REFERENCES `recording` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


DROP TABLE IF EXISTS `recording`;
CREATE TABLE `recording` (
  `id` binary(16) NOT NULL,
  `uuid` binary(16) DEFAULT NULL,
  `part` int(11) DEFAULT NULL,
  `model` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL,
  `path` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `url` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `best_transcription` text COLLATE utf8_unicode_ci,
  `score` float DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `model` (`model`),
  CONSTRAINT `recording_ibfk_1` FOREIGN KEY (`model`) REFERENCES `worker_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


DROP TABLE IF EXISTS `transcription`;
CREATE TABLE `transcription` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `recording_id` binary(16) DEFAULT NULL,
  `user_id` binary(16) DEFAULT NULL,
  `text` text COLLATE utf8_unicode_ci,
  `created` datetime DEFAULT NULL,
  `has_been_played` tinyint(1) DEFAULT NULL,
  `native_speaker` tinyint(1) DEFAULT NULL,
  `offensive_language` tinyint(1) DEFAULT NULL,
  `not_a_speech` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `recording_id` (`recording_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `transcription_ibfk_1` FOREIGN KEY (`recording_id`) REFERENCES `recording` (`id`),
  CONSTRAINT `transcription_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` binary(16) NOT NULL,
  `email` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `name` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `avatar` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `admin` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


DROP TABLE IF EXISTS `worker_type`;
CREATE TABLE `worker_type` (
  `id` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
  `lang` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL,
  `name` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8_unicode_ci,
  `visible` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


DROP TABLE IF EXISTS `language_model`;
CREATE TABLE `language_model` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `key` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
  `name` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
  `worker_type` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `worker_type` (`worker_type`),
  CONSTRAINT `language_model_ibfk_1` FOREIGN KEY (`worker_type`) REFERENCES `worker_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


INSERT INTO `worker_type` (`id`, `visible`, `lang`, `name`, `description`) VALUES
('en-sports-betting',	1, NULL,	'English (Librispeech+VCTK AM / SportsBetting LM)',	'Try sentences such as: ten quid on Manchester United.'),
('en-train-ticketing',	1, NULL,	'English (Librispeech+VCTK AM / TrainTicketing LM)',	'Try sentences such as: leaving London going to Cambridge.');
-- 2015-05-06 13:57:06
