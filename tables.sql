DROP DATABASE IF EXISTS lib1;

create database lib1;
use lib1;

CREATE TABLE `lib1`.`schools` (
`schoolID` INT NOT NULL AUTO_INCREMENT , 
`name` VARCHAR(30) NOT NULL UNIQUE, 
`email` VARCHAR(30) NOT NULL UNIQUE, 
`phone` INT NOT NULL , 
`str_name` VARCHAR(20) NOT NULL , 
`str_number` INT NOT NULL , 
`zip_code` INT NOT NULL , 
`city` VARCHAR(20) NOT NULL , 
PRIMARY KEY (`schoolID`)) ENGINE = InnoDB;

CREATE TABLE `lib1`.`books` (
`ISBN` BIGINT NOT NULL , 
`schoolID` INT NOT NULL , 
`title` TINYTEXT NOT NULL , 
`publisher` VARCHAR(30) NOT NULL , 
`num_pages` INT NOT NULL , 
`lang` VARCHAR(18) NOT NULL , 
`copies` INT NOT NULL , 
`image` TEXT NOT NULL , 
`summary` TEXT NOT NULL , 
`available_copies` INT NOT NULL DEFAULT `copies`,
PRIMARY KEY (`ISBN`, `schoolID`)) ENGINE = InnoDB;

ALTER TABLE `books` ADD FOREIGN KEY (`schoolID`) REFERENCES `schools`(`schoolID`) ON DELETE RESTRICT ON UPDATE RESTRICT;

CREATE TABLE `lib1`.`author` (
`authorID` INT NOT NULL AUTO_INCREMENT , 
`name` VARCHAR(30) NOT NULL , 
PRIMARY KEY (`authorID`)) ENGINE = InnoDB;

CREATE TABLE `lib1`.`is_author` (
`ISBN` BIGINT NOT NULL , 
`authorID` INT NOT NULL , 
PRIMARY KEY (`ISBN`, `authorID`)) ENGINE = InnoDB;

ALTER TABLE `is_author` ADD FOREIGN KEY (`authorID`) REFERENCES `author`(`authorID`) ON DELETE RESTRICT ON UPDATE RESTRICT; 
ALTER TABLE `is_author` ADD FOREIGN KEY (`ISBN`) REFERENCES `books`(`ISBN`) ON DELETE RESTRICT ON UPDATE RESTRICT;

CREATE TABLE `lib1`.`subjects` (
`subID` INT NOT NULL AUTO_INCREMENT , 
`subject` VARCHAR(30) NOT NULL , 
PRIMARY KEY (`subID`)) ENGINE = InnoDB;

CREATE TABLE `lib1`.`has_subject` (
`ISBN` BIGINT NOT NULL , 
`subID` INT NOT NULL , 
PRIMARY KEY (`ISBN`, `subID`)) ENGINE = InnoDB;

ALTER TABLE `has_subject` ADD FOREIGN KEY (`ISBN`) REFERENCES `books`(`ISBN`) ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE `has_subject` ADD FOREIGN KEY (`subID`) REFERENCES `subjects`(`subID`) ON DELETE RESTRICT ON UPDATE RESTRICT;


CREATE TABLE `lib1`.`keywords` (
`keyword_ID` INT NOT NULL AUTO_INCREMENT , 
`keyword` VARCHAR(30) NOT NULL , 
PRIMARY KEY (`keyword_ID`)) ENGINE = InnoDB;

CREATE TABLE has_keywords (
    ISBN BIGINT NOT NULL,
    keyword_id INT NOT NULL,
    PRIMARY KEY (ISBN, keyword_id),
    FOREIGN KEY (ISBN) REFERENCES books(ISBN),
    FOREIGN KEY (keyword_id) REFERENCES keywords(keyword_id)
);

CREATE TABLE `lib1`.`users` (
`userID` INT NOT NULL AUTO_INCREMENT , 
`schoolID` INT NOT NULL , 
`name` VARCHAR(30) NOT NULL ,
`surname` VARCHAR(20) NOT NULL, 
`email` VARCHAR(30) NOT NULL , 
`username` VARCHAR(20) NOT NULL , 
`password` VARCHAR(30) NOT NULL , 
PRIMARY KEY (`userID`)) ENGINE = InnoDB;

ALTER TABLE `users` ADD `active` BOOLEAN NOT NULL DEFAULT FALSE AFTER `password`;
ALTER TABLE `users` ADD `birthdate` DATE NOT NULL DEFAULT '2000-01-01' AFTER `active`;
ALTER TABLE `users` ADD FOREIGN KEY (`schoolID`) REFERENCES `schools`(`schoolID`) ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE `users` ADD UNIQUE(`email`);

CREATE TABLE `lib1`.`school_director` (
`directorID` INT NOT NULL AUTO_INCREMENT , 
`schoolID` INT NOT NULL , 
`name` VARCHAR(30) NOT NULL , 
`surname` VARCHAR(20) NOT NULL,
`userID` INT NOT NULL , 
PRIMARY KEY (`directorID`)) ENGINE = InnoDB;

ALTER TABLE `school_director` ADD FOREIGN KEY (`schoolID`) REFERENCES `schools`(`schoolID`) ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE `school_director` ADD FOREIGN KEY (`userID`) REFERENCES `users`(`userID`) ON DELETE RESTRICT ON UPDATE RESTRICT;

CREATE TABLE `lib1`.`admin` (`adminID` INT NOT NULL AUTO_INCREMENT , 
`name` VARCHAR(30) NOT NULL , 
`surname` VARCHAR(20) NOT NULL,
`email` VARCHAR(30) NOT NULL , 
`username` VARCHAR(12) NOT NULL , 
`password` VARCHAR(20) NOT NULL , 
PRIMARY KEY (`adminID`)) ENGINE = InnoDB;

ALTER TABLE `admin` ADD UNIQUE(`email`);

CREATE TABLE `lib1`.`handler` (
`handlerID` INT NOT NULL AUTO_INCREMENT , 
`schoolID` INT NOT NULL , 
`firstname` VARCHAR(30) NOT NULL , 
`lastname` VARCHAR(30) NOT NULL , 
`username` VARCHAR(30) NOT NULL , 
`password` VARCHAR(30) NOT NULL , 
`email` VARCHAR(30) NOT NULL , 
PRIMARY KEY (`handlerID`), 
UNIQUE (`username`), 
UNIQUE (`email`)) ENGINE = InnoDB;

ALTER TABLE `handler` ADD `active` BOOLEAN NOT NULL DEFAULT FALSE AFTER `email`;
ALTER TABLE `handler` ADD FOREIGN KEY (`schoolID`) REFERENCES `schools`(`schoolID`) ON DELETE RESTRICT ON UPDATE RESTRICT;


CREATE TABLE `lib1`.`loans` (
`loanID` INT NOT NULL AUTO_INCREMENT , 
`ISBN` BIGINT NOT NULL , 
`loan_date` DATE NOT NULL DEFAULT CURRENT_TIMESTAMP , 
`end_date` DATE NOT NULL DEFAULT CURRENT_TIMESTAMP, 
PRIMARY KEY (`loanID`)) ENGINE = InnoDB;

ALTER TABLE `loans` ADD `active` BOOLEAN NOT NULL DEFAULT TRUE AFTER `end_date`;
ALTER TABLE `loans` ADD `pending` BOOLEAN NOT NULL DEFAULT TRUE AFTER `active`;
ALTER TABLE `loans` ADD FOREIGN KEY (`ISBN`) REFERENCES `books`(`ISBN`) ON DELETE RESTRICT ON UPDATE RESTRICT; 

CREATE TABLE `lib1`.`reservations` (
`resID` INT NOT NULL AUTO_INCREMENT , 
`ISBN` BIGINT NOT NULL , 
`res_date` DATE NOT NULL DEFAULT CURRENT_TIMESTAMP , 
`end_date` DATE NOT NULL DEFAULT CURRENT_TIMESTAMP, 
PRIMARY KEY (`resID`)) ENGINE = InnoDB;

ALTER TABLE `reservations` ADD FOREIGN KEY (`ISBN`) REFERENCES `books`(`ISBN`) ON DELETE RESTRICT ON UPDATE RESTRICT;

CREATE TABLE `lib1`.`review` (
`review_ID` INT NOT NULL AUTO_INCREMENT , 
`ISBN` BIGINT NOT NULL , 
`userID` INT NOT NULL , 
`date` DATE NOT NULL DEFAULT CURRENT_TIMESTAMP, 
`rating` INT NOT NULL , 
`comments` TEXT NOT NULL , 
PRIMARY KEY (`review_ID`)) ENGINE = InnoDB;

ALTER TABLE `review` ADD FOREIGN KEY (`ISBN`) REFERENCES `books`(`ISBN`) ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE `review` ADD FOREIGN KEY (`userID`) REFERENCES `users`(`userID`) ON DELETE RESTRICT ON UPDATE RESTRICT;

CREATE TABLE `lib1`.`student` (
`userID` INT NOT NULL ,
`num_loans` INT NOT NULL DEFAULT '0', 
`num_reserv` INT NOT NULL DEFAULT '0', 
`can_loan` BOOLEAN NOT NULL DEFAULT '1', 
`can_reserve` BOOLEAN NOT NULL DEFAULT '1', 
PRIMARY KEY (`userID`)) ENGINE = InnoDB;

ALTER TABLE `student` ADD FOREIGN KEY (`userID`) REFERENCES `users`(`userID`) ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE `student`
ADD CONSTRAINT `check_num_loans` CHECK (`num_loans` < 3);
ALTER TABLE `student`
ADD CONSTRAINT `chk_num_res` CHECK (`num_reserv` < 3);


CREATE TABLE `lib1`.`teacher` (
`userID` INT NOT NULL , 
`num_loans` INT NOT NULL DEFAULT '0',
 `num_reserv` INT NOT NULL DEFAULT '0' , 
 `can_loan` BOOLEAN NOT NULL DEFAULT '1', 
 `can_reserve` BOOLEAN NOT NULL DEFAULT '1', 
 PRIMARY KEY (`userID`)) ENGINE = InnoDB;
 
 ALTER TABLE `teacher` ADD FOREIGN KEY (`userID`) REFERENCES `users`(`userID`) ON DELETE RESTRICT ON UPDATE RESTRICT;
 ALTER TABLE `teacher`
ADD CONSTRAINT `check_num_loans` CHECK (`num_loans` < 3);
ALTER TABLE `teacher`
ADD CONSTRAINT `chk_num_res` CHECK (`num_reserv` < 3);

CREATE TABLE `lib1`.`has_loan` (
`loanID` INT NOT NULL , 
`userID` INT NOT NULL , 
PRIMARY KEY (`loanID`, `userID`)) ENGINE = InnoDB;

ALTER TABLE `has_loan` ADD FOREIGN KEY (`loanID`) REFERENCES `loans`(`loanID`) ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE `has_loan` ADD FOREIGN KEY (`userID`) REFERENCES `users`(`userID`) ON DELETE RESTRICT ON UPDATE RESTRICT;

CREATE TABLE `lib1`.`has_reserv` (
`resID` INT NOT NULL , 
`userID` INT NOT NULL , 
PRIMARY KEY (`resID`, `userID`)) ENGINE = InnoDB;

ALTER TABLE `has_reserv` ADD FOREIGN KEY (`resID`) REFERENCES `reservations`(`resID`) ON DELETE RESTRICT ON UPDATE RESTRICT; 
ALTER TABLE `has_reserv` ADD FOREIGN KEY (`userID`) REFERENCES `users`(`userID`) ON DELETE RESTRICT ON UPDATE RESTRICT;



CREATE INDEX subs ON subjects (subject);
CREATE INDEX unames ON users (username);
CREATE INDEX pasrs ON users (password);
CREATE INDEX surs ON users (surname);
CREATE INDEX auths ON author (name);

SET GLOBAL event_scheduler = ON;



DELIMITER //
CREATE TRIGGER `increase_num_reserv_trigger` AFTER INSERT ON `has_reserv`
 FOR EACH ROW BEGIN
    DECLARE user_type VARCHAR(10);
    SET user_type = (
        SELECT CASE
            WHEN EXISTS(SELECT * FROM student WHERE userID = NEW.userID) THEN 'student'
            WHEN EXISTS(SELECT * FROM teacher WHERE userID = NEW.userID) THEN 'teacher'
        END
    );

    IF user_type = 'student' THEN
        UPDATE student SET num_reserv = num_reserv + 1 WHERE userID = NEW.userID;
    ELSEIF user_type = 'teacher' THEN
        UPDATE teacher SET num_reserv = num_reserv + 1 WHERE userID = NEW.userID;
    END IF;
END//


CREATE EVENT delete_expired_reservations_event
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP + INTERVAL 1 DAY
DO
BEGIN
    DECLARE user_type VARCHAR(10);
    DECLARE user_id INT;
    
    DELETE hr
    FROM has_reserv hr
    JOIN reservations r ON hr.resID = r.resID
    WHERE DATEDIFF(CURRENT_DATE, r.res_date) > 7;
    
    SELECT r.userID, CASE
        WHEN EXISTS(SELECT * FROM student WHERE userID = r.userID) THEN 'student'
        WHEN EXISTS(SELECT * FROM teacher WHERE userID = r.userID) THEN 'teacher'
    END INTO user_id, user_type
    FROM reservations r
    WHERE DATEDIFF(CURRENT_DATE, r.res_date) > 7;
    
    DELETE FROM reservations WHERE DATEDIFF(CURRENT_DATE, res_date) > 7;
    
    IF user_type = 'student' THEN
        UPDATE student SET num_reserv = num_reserv + 1 WHERE userID = user_id;
    ELSEIF user_type = 'teacher' THEN
        UPDATE teacher SET num_reserv = num_reserv + 1 WHERE userID = user_id;
    END IF;
END //

DELIMITER ;

