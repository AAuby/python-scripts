/*
	1. 分区字段必学是主键或主键一部分(联合主键)
	2. 分区表不能存在外建
	3. 使用方法： mysql -uuser -ppassword < auto_create_partitions.sql
*/ 
-- 创建存储过程
DELIMITER $$
USE `db1`$$
DROP PROCEDURE IF EXISTS `create_partition_by_month`$$
CREATE PROCEDURE `create_partition_by_month` (in schema_name varchar(64), in table_name varchar(64)) 
BEGIN
	DECLARE is_partition_able int;
	DECLARE months int;
	DECLARE target_date datetime;
	DECLARE partition_name varchar(7);
	DECLARE partition_add_month varchar(10);

	SET months = 0;

	SELECT COUNT(*) INTO is_partition_able FROM information_schema.partitions
	WHERE table_schema=schema_name
	AND table_name=table_name
	AND partition_name<>NULL;
	IF is_partition_able = 0 THEN
		SET months = 1;
		SET @SQL=CONCAT('ALTER TABLE `', schema_name, '`.`', table_name, '` PARTITION BY RANGE COLUMNS(created_at) (PARTITION ', 
			DATE_FORMAT(NOW(), 'p%Y%m'), ' VALUES LESS THAN ("', DATE_FORMAT(NOW()+INTERVAL 1 MONTH, '%Y-%m-01'), '"));');
		PREPARE INIT_PARTITION FROM @SQL;
		EXECUTE INIT_PARTITION;
		DEALLOCATE PREPARE INIT_PARTITION;
	END IF;
	WHILE months < 12 DO
		SET @rows=0;
		SET target_date = NOW() + INTERVAL months MONTH;
		SET partition_name = DATE_FORMAT(target_date, 'p%Y%m');
		SET target_date = target_date + INTERVAL 1 MONTH;
		SET partition_add_month = DATE_FORMAT(target_date, '%Y-%m-01');
		SET @SQL=CONCAT('SELECT COUNT(*) INTO @rows FROM information_schema.partitions WHERE table_schema="', schema_name, '" AND table_name="', table_name, '" AND partition_name="', partition_name, '";');
		PREPARE PARTITION_IS_EXISTS FROM @SQL;
		EXECUTE PARTITION_IS_EXISTS;
		DEALLOCATE PREPARE PARTITION_IS_EXISTS;
		IF @rows = 0 THEN
			SET @SQL=CONCAT('ALTER TABLE `', schema_name, '`.`', table_name, '` ADD PARTITION ( PARTITION ', partition_name, 
				' VALUES LESS THAN ("', partition_add_month, '"));');
			PREPARE STMT FROM @SQL;
			EXECUTE STMT;
			DEALLOCATE PREPARE STMT;
		END IF;
		SET months = months + 1;
	END WHILE;
END$$
DELIMITER ;

-- 创建事件调度
DELIMITER $$
USE `db1`$$
DROP EVENT IF EXISTS `auto_generate_partitions`$$
CREATE EVENT `auto_generate_partitions` 
ON SCHEDULE EVERY 1 YEAR 
STARTS NOW() + INTERVAL 5 MINUTE 
ON COMPLETION PRESERVE
ENABLE
COMMENT 'auto generate partitions'
DO BEGIN
	CALL create_partition_by_month('db1', 'tb1');
END$$
DELIMITER ;
