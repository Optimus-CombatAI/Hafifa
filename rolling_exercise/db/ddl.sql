SET search_path TO rolling_exercise;


DROP TABLE IF EXISTS Cities CASCADE;

CREATE TABLE Cities (
    id SERIAL PRIMARY KEY,
    name varchar(255)
);


DROP TABLE IF EXISTS Reports CASCADE;


CREATE TABLE Reports(
    id SERIAL PRIMARY KEY,
    date DATE,
	city_id int,
    name varchar(255),
	pm2_5 int,
	no_2 int,
	co_2 int,
	aqi int,
	FOREIGN KEY (city_id) REFERENCES Cities(id)
);

