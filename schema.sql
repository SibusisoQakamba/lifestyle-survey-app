DROP TABLE IF EXISTS responses;

CREATE TABLE responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    age INTEGER,
    gender TEXT, -- e.g., Male, Female, Non-binary, Prefer not to say
    preferred_activity TEXT, -- e.g., Reading, Sports, Movies, Travel, Gaming
    preferred_environment TEXT, -- e.g., Urban, Suburban, Rural
    social_preference TEXT, -- e.g., Introvert, Extrovert, Ambivert
    tech_usage TEXT -- e.g., Low, Medium, High
);