DROP TABLE IF EXISTS responses;

CREATE TABLE responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Personal Details
    full_names TEXT,
    email TEXT,
    dob TEXT, -- Storing as TEXT, can be DATE if DB supports well
    contact_number TEXT,

    -- Favorite Food
    favorite_food_pizza INTEGER DEFAULT 0, -- 1 if checked, 0 if not
    favorite_food_pasta INTEGER DEFAULT 0,
    favorite_food_pap_wors INTEGER DEFAULT 0,
    favorite_food_other INTEGER DEFAULT 0,
    favorite_food_other_text TEXT, -- Text for "Other" food

    -- Likert Scale (1=Strongly Agree, 2=Agree, 3=Neutral, 4=Disagree, 5=Strongly Disagree)
    movies_rating INTEGER,
    radio_rating INTEGER,
    eat_out_rating INTEGER,
    tv_rating INTEGER
);