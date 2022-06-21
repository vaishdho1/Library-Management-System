
-- create the tables for the database
-- create the tables for the database

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username       VARCHAR(50) NOT NULL,
  password      VARCHAR(500) NOT NULL
);

INSERT INTO user(username,password)
VALUES
("emelie12",'Saturday123@'),
("john15","Sunday123#"),
('naina13','Monday123@'),
('nimesh12','Tuesday456#');

CREATE TABLE floor(
floor_no INT PRIMARY KEY NOT NULL
);
INSERT INTO floor
VALUES
(1),
(2),
(3);

CREATE TABLE shelf(
shelf_no INT PRIMARY KEY NOT NULL,
floor_no INT NOT NULL,
exact_loc INT NOT NULL,
CONSTRAINT shelf_fk_floor
    FOREIGN KEY (floor_no)
    REFERENCES floor (floor_no) ON UPDATE CASCADE ON DELETE CASCADE
);



INSERT INTO shelf (shelf_no,floor_no,exact_loc)
VALUES
(111,1,1),
(321,3,1),
(311,3,2),
(312,3,1),
(232,2,2),
(211,2,3),
(212,2,1),
(131,1,3),
(121,1,2),
(112,1,1),
(231,2,2),
(222,2,1),
(322,3,1),
(132,1,2),
(122,1,1);




CREATE TABLE book(
ISBN char(10) PRIMARY KEY NOT NULL,
Title VARCHAR(100) NOT NULL,
Price DECIMAL(5,2) NOT NULL,
Edition INT NOT NULL,
Publisher VARCHAR(50) NOT NULL,
Shelf_no INT NOT NULL,
Subname VARCHAR(50) NOT NULL,
CONSTRAINT book_fk_shelf
    FOREIGN KEY (Shelf_no)
    REFERENCES shelf(shelf_no) ON UPDATE CASCADE ON DELETE CASCADE
);
INSERT INTO `book` (`ISBN`, `Title`, `Price`, `Edition`, `Publisher`, `Shelf_no`, `Subname`)
VALUES
('0201100886', 'Compilers: Principles, Techniques, and Tools',664.0,2,'Pearson',321,'Computer Basics' ),
('0132126958','Computer Networks: Computer Networks',665.0,5,'Pearson',311,'Computer Basics'),
('1118063333','Operating System Concepts',568.0,9,'John Wiley & Sons Inc',312,'Computer Basics'),
('8120340078','Introduction to Algorithms',1550.0 ,3,'The MIT Press',232,'Programming and Datastructures'),
('8173716064','Fundamentals of Data Structures in C++',415.0,2,'Universities Press',211,'Programming and Datastructures'),
('0321884078', 'Thomas'' Calculus: Early Transcendentals', 198.89, 13, 'Pearson',111, 'Calculus'),
('1285057090', 'Calculus', 245.84, 10,'Cengage Learning', 112, 'Calculus'),
('9385889559', 'SQL Cookbook: Query Solutions and Techniques for All SQL Users',1800,2,'Shroff OReilly',132,'Data Science'),
('0133970779','Fundamentals of Database Systems',10567.0,7,'Pearson Education India',122,'Data Science'),
('1259005275','Computer Organization',390,5,'McGraw Hill Education',212,'Computer Architecture'),
('0124077269', 'Computer Organization and Design', 5000.0, 5, 'Morgan Kaufmann',322, 'Computer Architecture');


CREATE TABLE author(
ISBN char(10) NOT NULL ,
Author VARCHAR(50) NOT NULL,
PRIMARY KEY(ISBN,Author),
CONSTRAINT author_fk_book
    FOREIGN KEY (ISBN)
    REFERENCES book(ISBN) ON UPDATE CASCADE ON DELETE CASCADE
);
INSERT INTO `author` (`ISBN`, `Author`) VALUES
('0201100886', 'Alfred V.Aho'),
('0201100886', 'Ravi Sethi'),
('0201100886','Jeffrey D.Ullman'),
('0132126958','Andrew S. Tanenbaum'),
('1118063333', 'Abraham Silberschatz'),
('1118063333', 'Peter Baer Galvin'),
('1118063333','Greg Gagne'),
('8120340078','Thomas H. Cormen'),
('8120340078','Charles E. Leiserson'),
('8173716064','Ellis Horowitz'),
('8173716064', 'Sartaj Sahni'),
('8173716064', 'Dinesh Mehta'),
('0321884078', 'George B. Thomas Jr'),
('0321884078', 'Joel R. Hass'),
('0321884078', 'Maurice D. Weir'),
('1285057090', 'Bruce H. Edwards'),
('1285057090', 'Ron Larson'),
('9385889559','Anthony Molinaro'),
('9385889559', 'Robert de Graaf'),
('0133970779','Ramez Elmasri'),
('0133970779', 'Shamkant B. Navathe'),
('1259005275', 'Carl Hamacher'),
('1259005275', 'Zvonko Vranesic'),
('1259005275', 'Safwat Zaky'),
('0124077269', 'David A. Patterson'),
('0124077269', 'John L. Hennessy');


CREATE TABLE book_copy(
ISBN char(10) NOT NULL,
copy_id INT NOT NULL,
Ischecked Tinyint DEFAULT 0,
Isonhold Tinyint DEFAULT 0,
Isdamaged Tinyint Default 0,
Fut_req VARCHAR(50) DEFAULT NULL,
PRIMARY KEY(ISBN,copy_id),
CONSTRAINT book_copy_fk_book
    FOREIGN KEY (ISBN)
    REFERENCES book(ISBN) ON UPDATE CASCADE ON DELETE CASCADE
);
INSERT INTO book_copy
VALUES
('0201100886', 1, 1, 0, 0, NULL),
('0201100886', 2, 0, 0, 0, NULL),
('0201100886', 3, 0, 0, 0, NULL),
('0132126958', 1, 1, 0, 0, NULL),
('0132126958', 2, 0, 0, 0, NULL),
('0132126958', 3, 1, 0, 0, NULL),
('1118063333', 1, 0, 0, 0, NULL),
('1118063333', 2, 0, 0, 0, NULL),
('8120340078', 1, 0, 0, 0, NULL),
('8120340078', 2, 0, 0, 0, 'nimesh12'),
('8120340078', 3, 0, 0, 0, NULL),
('8173716064', 1, 0, 0, 0, NULL),
('8173716064', 2, 0, 0, 0, NULL),
('0321884078', 1, 0, 1, 0, NULL),
('0321884078', 2, 0, 0, 0, NULL),
('0321884078', 3, 0, 0, 0, NULL),
('1285057090', 1, 0, 0, 0, NULL),
('1285057090', 2, 0, 0, 0, NULL),
('9385889559', 1, 0, 0, 0, NULL),
('9385889559', 2, 1, 0, 0, NULL),
('0133970779', 1, 0, 0, 0, NULL),
('0133970779', 2, 1, 0, 0, NULL),
('0133970779', 3, 0, 0, 0, NULL),
('1259005275', 1, 0, 0, 0, NULL),
('1259005275', 2, 1, 0, 0, NULL),
('0124077269', 1, 0, 0, 0, NULL),
('0124077269', 2, 1, 0, 0, NULL),
('0124077269', 3, 0, 0, 0, NULL);

CREATE TABLE issue(
user_id INT NOT NULL,
issue_id INT NOT NULL,
ISBN char(10) ,
copy_id INT NOT NULL,
Issuedate DATE NOT NULL,
Returndate DATE NOT NULL,
Extendate DATE DEFAULT NULL,
Numext INT DEFAULT 0,
PRIMARY KEY (issue_id,copy_id,ISBN),
CONSTRAINT issue_fk_user
    FOREIGN KEY (user_id)
    REFERENCES user (id) ON UPDATE CASCADE ON DELETE CASCADE,
CONSTRAINT issue_fk_cpy
    FOREIGN KEY (ISBN,copy_id)
    REFERENCES book_copy (ISBN,copy_id) ON UPDATE CASCADE ON DELETE CASCADE
);
INSERT INTO issue
VALUES
(3,1,'0201100886',1,'2022-06-18','2022-07-03',NULL,0),
(4,2,'0132126958',1,'2022-06-06','2022-06-20',NULL,0),
(3,3,'0132126958',3,'2022-05-31','2022-06-21','2022-05-07',1),
(4,4,'0321884078',1,'2022-06-18','2022-06-18',NULL,0);

CREATE TABLE lib_members(
user_id INT NOT NULL PRIMARY KEY,
Name VARCHAR(50) NOT NULL,
DOB DATE,
Email VARCHAR(50) NOT NULL,
Isdebarred Tinyint DEFAULT 0,
Gender CHAR(1) NOT NULL,
Isfaculty Tinyint(1) NOT NULL,
Penlity Decimal(8,2) NOT NULL DEFAULT 0,
Dept VARCHAR(50),
CONSTRAINT lib_members_fk_user
    FOREIGN KEY (user_id)
    REFERENCES user (id) ON UPDATE CASCADE ON DELETE CASCADE
);

INSERT INTO lib_members
VALUES
(3, 'Naina Sinha', '1975-04-19', 'naina@nitk.edu', 0, 'F', 1, '0.00', 'College of Computing'),
(4, 'Nimesh Sharma', '1999-06-12', 'nimesh@nitk.edu', 0, 'M',  0, '5.00', NULL);

CREATE TABLE subject(
Subname VARCHAR(50) NOT NULL PRIMARY KEY,
floor_no INT NOT NULL,
Num_books INT NOT NULL,
CONSTRAINT subject_fk_floor
    FOREIGN KEY (floor_no)
    REFERENCES floor (floor_no) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE staff(
user_id INT NOT NULL,
username VARCHAR(50) PRIMARY KEY NOT NULL,
CONSTRAINT faculty_fk_user
    FOREIGN KEY (user_id)
    REFERENCES user (id) ON UPDATE CASCADE ON DELETE CASCADE
);
INSERT INTO staff
VALUES
(1,"emelie12"),
(2,"john15");










