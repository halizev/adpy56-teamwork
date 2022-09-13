CREATE TABLE IF NOT EXISTS client (
    id INTEGER PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
	last_name VARCHAR(50),    
    sex INTEGER NOT NULL,
	bdate VARCHAR(10) NOT NULL,
    city_id INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS candidate (
    id INTEGER PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    profile_link VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS client_candidate (
    client_id INTEGER REFERENCES client(id),
    candidate_id INTEGER REFERENCES candidate(id),
    CONSTRAINT clc PRIMARY KEY (client_id, candidate_id),
    favourite boolean,
    has_seen boolean   
);

CREATE TABLE IF NOT EXISTS photo (       
    id serial PRIMARY KEY,
    photo_link varchar NOT NULL,
    candidate_id INTEGER REFERENCES candidate(id)
);