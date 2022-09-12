CREATE TABLE IF NOT EXISTS user_vk (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    age INTEGER NOT NULL,
    gender INTEGER NOT NULL,
    city INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS candidate (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    surname VARCHAR(50) NOT NULL,
    profile_link VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS user_vk_candidate (
    user_vk_id INTEGER REFERENCES user_vk(id),
    candidate_id INTEGER REFERENCES candidate(id),
    CONSTRAINT uc PRIMARY KEY (user_vk_id, candidate_id),
    favourite boolean,
    has_seen boolean   
);

CREATE TABLE IF NOT EXISTS photo (       
    id serial PRIMARY KEY,
    photo_link varchar NOT NULL,
    candidate_id INTEGER REFERENCES candidate(id)
);