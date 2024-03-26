CREATE DATABASE user.db;

USE user.db;

CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    user_name VARCHAR(255),
    user_surname VARCHAR(255),
    user_phone INT,
    user_department VARCHAR(255),
    user_permission INT,
    user_pictures INT
);

CREATE TABLE user_times (
    entry_time DATETIME,
    leave_time DATETIME
);