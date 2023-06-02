DROP DATABASE IF EXISTS lib1;

create database lib1;
use lib1;

-- Schools, primary key: schoolID


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

-- books
-- primary key: ISBN
-- foreign key: schoolID

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


-- Author, because there can be more than one authors for a book
-- primary key: authorID


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


-- subjects, there can be multiple subjects for a book
-- primary key:subID

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


-- keywords, there can be multiple keywords for a book
-- primary key:keyword_ID

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


-- users
-- primary key: userID
-- foreign key: schoolID

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


-- school director
-- is a user -> foreign keys schoolID, userID
-- primary key : directorID


CREATE TABLE `lib1`.`school_director` (
`directorID` INT NOT NULL AUTO_INCREMENT , 
`schoolID` INT NOT NULL , 
`name` VARCHAR(30) NOT NULL , 
`surname` VARCHAR(20) NOT NULL,
`userID` INT NOT NULL , 
PRIMARY KEY (`directorID`)) ENGINE = InnoDB;

ALTER TABLE `school_director` ADD FOREIGN KEY (`schoolID`) REFERENCES `schools`(`schoolID`) ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE `school_director` ADD FOREIGN KEY (`userID`) REFERENCES `users`(`userID`) ON DELETE RESTRICT ON UPDATE RESTRICT;


-- admin
-- primary key : adminID


CREATE TABLE `lib1`.`admin` (`adminID` INT NOT NULL AUTO_INCREMENT , 
`name` VARCHAR(30) NOT NULL , 
`surname` VARCHAR(20) NOT NULL,
`email` VARCHAR(30) NOT NULL , 
`username` VARCHAR(12) NOT NULL , 
`password` VARCHAR(20) NOT NULL , 
PRIMARY KEY (`adminID`)) ENGINE = InnoDB;

ALTER TABLE `admin` ADD UNIQUE(`email`);


-- handler
-- primary key : handlerID
-- responsible for a school -> foreign key: schoolID

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


-- loans 
-- primary key: loanID


CREATE TABLE `lib1`.`loans` (
`loanID` INT NOT NULL AUTO_INCREMENT , 
`ISBN` BIGINT NOT NULL , 
`loan_date` DATE NOT NULL DEFAULT CURRENT_TIMESTAMP , 
`end_date` DATE NOT NULL DEFAULT CURRENT_TIMESTAMP, 
PRIMARY KEY (`loanID`)) ENGINE = InnoDB;

ALTER TABLE `loans` ADD `active` BOOLEAN NOT NULL DEFAULT TRUE AFTER `end_date`;
ALTER TABLE `loans` ADD `pending` BOOLEAN NOT NULL DEFAULT TRUE AFTER `active`;
ALTER TABLE `loans` ADD FOREIGN KEY (`ISBN`) REFERENCES `books`(`ISBN`) ON DELETE RESTRICT ON UPDATE RESTRICT; 

-- reservations
-- primary key: resID

CREATE TABLE `lib1`.`reservations` (
`resID` INT NOT NULL AUTO_INCREMENT , 
`ISBN` BIGINT NOT NULL , 
`res_date` DATE NOT NULL DEFAULT CURRENT_TIMESTAMP , 
`end_date` DATE NOT NULL DEFAULT CURRENT_TIMESTAMP, 
PRIMARY KEY (`resID`)) ENGINE = InnoDB;

ALTER TABLE `reservations` ADD FOREIGN KEY (`ISBN`) REFERENCES `books`(`ISBN`) ON DELETE RESTRICT ON UPDATE RESTRICT;


-- review
-- primary key: review_ID


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


-- student is a user
-- primary key and foreign key: userID
-- num_loans refers to active loans

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


-- teacher is a user
-- primary key and foreign key: userID
-- num_loans refers to active loans


CREATE TABLE `lib1`.`teacher` (
`userID` INT NOT NULL , 
`num_loans` INT NOT NULL DEFAULT '0',
 `num_reserv` INT NOT NULL DEFAULT '0' , 
 `can_loan` BOOLEAN NOT NULL DEFAULT '1', 
 `can_reserve` BOOLEAN NOT NULL DEFAULT '1', 
 PRIMARY KEY (`userID`)) ENGINE = InnoDB;
 
 ALTER TABLE `teacher` ADD FOREIGN KEY (`userID`) REFERENCES `users`(`userID`) ON DELETE RESTRICT ON UPDATE RESTRICT;
 ALTER TABLE `teacher`
ADD CONSTRAINT `check_num_loans` CHECK (`num_loans` < 2);
ALTER TABLE `teacher`
ADD CONSTRAINT `chk_num_res` CHECK (`num_reserv` < 2);

-- has_loan

CREATE TABLE `lib1`.`has_loan` (
`loanID` INT NOT NULL , 
`userID` INT NOT NULL , 
PRIMARY KEY (`loanID`, `userID`)) ENGINE = InnoDB;

ALTER TABLE `has_loan` ADD FOREIGN KEY (`loanID`) REFERENCES `loans`(`loanID`) ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE `has_loan` ADD FOREIGN KEY (`userID`) REFERENCES `users`(`userID`) ON DELETE RESTRICT ON UPDATE RESTRICT;

-- has_reserv


CREATE TABLE `lib1`.`has_reserv` (
`resID` INT NOT NULL , 
`userID` INT NOT NULL , 
PRIMARY KEY (`resID`, `userID`)) ENGINE = InnoDB;

ALTER TABLE `has_reserv` ADD FOREIGN KEY (`resID`) REFERENCES `reservations`(`resID`) ON DELETE RESTRICT ON UPDATE RESTRICT; 
ALTER TABLE `has_reserv` ADD FOREIGN KEY (`userID`) REFERENCES `users`(`userID`) ON DELETE RESTRICT ON UPDATE RESTRICT;


-- INDEXES


CREATE INDEX subs ON subjects (subject);
CREATE INDEX unames ON users (username);
CREATE INDEX surs ON users (surname);
CREATE INDEX auths ON author (name);
CREATE INDEX ldate ON loans (loan_date);

SET GLOBAL event_scheduler = ON;

-- trigger to increase num_reserv in student or teacher after reservation

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
END //


-- event to delete reservations after 7 days

CREATE EVENT delete_expired_reservations_event
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP + INTERVAL 1 DAY
DO
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE res_id INT;
    DECLARE user_id INT;
    DECLARE user_type VARCHAR(10);

    DECLARE cur CURSOR FOR
        SELECT r.resID , hr.userID , CASE
            WHEN EXISTS(SELECT * FROM student s WHERE s.userID = hr.userID) THEN 'student'
            WHEN EXISTS(SELECT * FROM teacher t WHERE t.userID = hr.userID) THEN 'teacher'
        END AS user_type
        FROM reservations r
        JOIN has_reserv hr ON r.resID = hr.resID
        WHERE DATEDIFF(CURRENT_DATE, r.res_date) > 7;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO res_id, user_id, user_type;

        IF done THEN
            LEAVE read_loop;
        END IF;

        DELETE FROM has_reserv WHERE resID = res_id;

        IF user_type = 'student' THEN
            UPDATE student SET num_reserv = num_reserv - 1 WHERE userID = user_id;
        ELSEIF user_type = 'teacher' THEN
            UPDATE teacher SET num_reserv = num_reserv - 1 WHERE userID = user_id;
        END IF;

        DELETE FROM reservations WHERE resID = res_id;
    END LOOP;

    CLOSE cur;
END //


-- stored procedure to insert reservation on a user, checking if he already reserves the same book


CREATE PROCEDURE `insert_has_reserv`(IN p_resID INT, IN p_userID INT)
BEGIN
    DECLARE existing_reservations INT;

    SELECT COUNT(*) INTO existing_reservations
    FROM reservations r
    JOIN has_reserv hs ON r.resID = hs.resID
    WHERE hs.userID = p_userID
      AND r.ISBN = (
        SELECT ISBN FROM reservations WHERE resID = p_resID
      );

    IF existing_reservations > 0 THEN
        DELETE FROM reservations WHERE resID = p_resID;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Duplicate reservation not allowed for the same book and user. The previous reservation has been deleted.';
    ELSE 
		INSERT INTO has_reserv (resID, userID) VALUES (p_resID, p_userID);
	END IF;
END //


-- stored procedure to insert loans on a user, checking if he has delayed loans


CREATE PROCEDURE `insert_has_loan`(IN p_loanID INT, IN p_userID INT)
BEGIN
    DECLARE existing_delayed_loans INT;
    DECLARE existing_same_book_loan INT;

    -- Check for delayed loans
    SELECT COUNT(*) INTO existing_delayed_loans
    FROM loans l
    JOIN has_loan hl ON hl.loanID = l.loanID
    WHERE hl.userID = p_userID AND l.active = 1 AND DATEDIFF(CURRENT_DATE, l.loan_date) > 7;

    IF existing_delayed_loans > 0 THEN
        CALL delete_loan(p_loanID);
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Delayed loan detected. The loan has been deleted.';
    ELSE
        -- Check for loan of the same book
        SELECT COUNT(*) INTO existing_same_book_loan
        FROM loans l
		join has_loan hs on hs.loanID = l.loanID
        WHERE hs.userID = p_userID AND ISBN = (SELECT ISBN FROM loans WHERE loanID = p_loanID) AND l.active = 1;

        IF existing_same_book_loan > 0 THEN
            CALL delete_loan(p_loanID);
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'You already have this book. The loan has been deleted.';
        ELSE
            INSERT INTO has_loan (loanID, userID) VALUES (p_loanID, p_userID);
        END IF;
    END IF;
END //


CREATE PROCEDURE `delete_loan`(IN p_loanID INT)
BEGIN
    DELETE FROM loans WHERE loanID = p_loanID;
END //

DELIMITER ;
