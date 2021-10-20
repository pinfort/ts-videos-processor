CREATE TABLE `executed_file` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `FILE` text COLLATE utf8mb4_bin NOT NULL,
 `drops` int(11) NOT NULL,
 `size` bigint(20) NOT NULL,
 `recorded_at` datetime NOT NULL,
 `channel` text COLLATE utf8mb4_bin NOT NULL,
 `title` text COLLATE utf8mb4_bin NOT NULL,
 `channelName` text COLLATE utf8mb4_bin NOT NULL,
 `duration` double NOT NULL,
 PRIMARY KEY (`id`),
 UNIQUE KEY `FILE` (`FILE`) USING HASH
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin

CREATE TABLE `splitted_file` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `executed_file_id` bigint(20) NOT NULL,
 `file` text COLLATE utf8mb4_bin NOT NULL,
 `size` bigint(20) NOT NULL,
 `duration` double NOT NULL,
 PRIMARY KEY (`id`),
 UNIQUE KEY `file` (`file`) USING HASH,
 KEY `executed_file_id` (`executed_file_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin
