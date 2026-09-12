CREATE DATABASE IF NOT EXISTS streamflix;

USE streamflix;

CREATE TABLE IF NOT EXISTS movies (

    id INT AUTO_INCREMENT PRIMARY KEY,

    title VARCHAR(255) NOT NULL,

    genre VARCHAR(100) NOT NULL,

    release_year INT NOT NULL,

    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


INSERT INTO movies
(title, genre, release_year, description)
VALUES

(
    'The Beginning',
    'Drama',
    2026,
    'A story about a new beginning.'
),

(
    'Dark Horizon',
    'Action',
    2025,
    'A dangerous mission beyond the horizon.'
),

(
    'Last Mission',
    'Thriller',
    2026,
    'One final mission changes everything.'
),

(
    'Beyond Earth',
    'Science Fiction',
    2025,
    'Humanity searches for a new home.'
),

(
    'Code Zero',
    'Technology',
    2026,
    'A programmer discovers a dangerous secret.'
),

(
    'The Chase',
    'Action',
    2024,
    'A race against time begins.'
),

(
    'Lost City',
    'Adventure',
    2025,
    'An ancient city hides an impossible secret.'
),

(
    'Final Signal',
    'Science Fiction',
    2026,
    'A mysterious signal reaches Earth.'
);
