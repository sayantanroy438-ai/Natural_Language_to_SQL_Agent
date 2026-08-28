CREATE DATABASE IF NOT EXISTS school_db;

USE school_db;

CREATE TABLE bridge (
    Class TEXT,
    FullName TEXT,
    ID INT,
    Sex TEXT
);

CREATE TABLE chess (
    Class TEXT,
    FullName TEXT,
    ID INT,
    Sex TEXT
);

CREATE TABLE music (
    ID INT,
    Type TEXT
);

CREATE TABLE student (
    Class TEXT,
    DCode TEXT,
    DOB TEXT,
    FullName TEXT,
    HCode TEXT,
    ID INT,
    MTest INT,
    New_DOB DATETIME,
    PTest INT,
    Remission INT,
    Sex TEXT
);
