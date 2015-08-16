-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Create the tournament db and connect to it
DROP DATABASE IF EXISTS restaurants;
CREATE DATABASE restaurants;
\c restaurants;

-- Create the Players table
DROP TABLE IF EXISTS Restaurants;
CREATE TABLE Restaurants (
  Id SERIAL PRIMARY KEY,
  Name varchar(255) NOT NULL UNIQUE
);
