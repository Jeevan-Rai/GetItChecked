create database getitchecked;
use getitchecked;

CREATE TABLE student (
	name VARCHAR(50) NOT NULL,
	email VARCHAR(50) NOT NULL,
    usn varchar(50) NOT NULL,
    phonenum varchar(50) NOT NULL,
	password VARCHAR(50) NOT NULL,
    branch varchar(10) NOT NULL,
	PRIMARY KEY(usn),
    unique key usn_UNIQUE(usn),
    unique key email_UNIQUE(email)
);

CREATE TABLE faculty (
	name VARCHAR(50) NOT NULL,
	email VARCHAR(50) NOT NULL,
    facultyId varchar(50) NOT NULL,
    phonenum varchar(50) NOT NULL,
	password VARCHAR(50) NOT NULL,
    branch varchar(10) NOT NULL,
	PRIMARY KEY(facultyId),
    unique key usn_UNIQUE(facultyId),
    unique key email_UNIQUE(email)
);
