CREATE DATABASE tlmdb;

\c tlmdb

CREATE USER postgres SUPERUSER;

CREATE TABLE systems (
  id VARCHAR(32) PRIMARY KEY,
  name TEXT,
  client TEXT,
  password TEXT
);

CREATE TABLE flights (
  id serial PRIMARY KEY,
  system_id VARCHAR(32) REFERENCES systems(id),
  name TEXT,
  start_time TIMESTAMP,
  launch_time TIMESTAMP,
  end_time TIMESTAMP,
  data TEXT
);

CREATE TABLE packets (
  id serial PRIMARY KEY,
  flight_id INTEGER REFERENCES flights(id),
  time TIMESTAMP,
  source VARCHAR(8),
  type SMALLINT,
  from_ SMALLINT,
  raw BYTEA
);
