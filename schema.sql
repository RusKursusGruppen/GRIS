BEGIN;
-- Run this to reset/create the database.
-- PRAGMA foreign_keys = ON;

--- USERS ---
DROP TABLE IF EXISTS Users CASCADE;
CREATE TABLE Users(
    user_id             serial PRIMARY KEY,
    username            text UNIQUE NOT NULL,
    loginname           text UNIQUE NOT NULL,
    created             timestamp NOT NULL default CURRENT_TIMESTAMP,
    name                text DEFAULT 'RUS',
    email               text,
    phone               text,
    driverslicence      boolean,
    address             text,
    zipcode             text,
    city                text,
    birthday            date,

    diku_age            text, -- Might be better as a nullable reference to the rus instance of this user
    about_me            text,

    password            text NOT NULL,
    deleted             boolean NOT NULL DEFAULT FALSE -- Field for marking a user as deleted
);

DROP TABLE IF EXISTS Groups CASCADE;
CREATE TABLE Groups(
    group_id            serial PRIMARY KEY,
    groupname           text UNIQUE NOT NULL
);
INSERT INTO Groups(groupname) VALUES('admin');
INSERT INTO Groups(groupname) VALUES('admin_mail_log');
INSERT INTO Groups(groupname) VALUES('rkg');
INSERT INTO Groups(groupname) VALUES('mentor');


DROP TABLE IF EXISTS User_groups CASCADE;
CREATE TABLE Group_users(
    user_id             integer REFERENCES Users(user_id),
    group_id            integer REFERENCES Groups(group_id),
    PRIMARY KEY (user_id, group_id)
);


DROP TABLE IF EXISTS User_creation_keys CASCADE;
CREATE TABLE User_creation_keys(
    key                 text PRIMARY KEY,
    email               text,
    created             timestamp NOT NULL
);

DROP TABLE IF EXISTS User_forgotten_password_keys CASCADE;
CREATE TABLE User_forgotten_password_keys(
    key                 text PRIMARY KEY,
    user_id             integer REFERENCES Users(user_id),
    created             timestamp NOT NULL
);

--- TOUR INFORMATION ---
DROP TABLE IF EXISTS Tours CASCADE;
CREATE TABLE Tours(
    tour_id             serial PRIMARY KEY,
    tour_name           text,
    theme               text,
    type                text CHECK(type IN ('p', 't', 'm')),
    year                integer,
    notes               text
);

DROP TABLE IF EXISTS Tours_tutors CASCADE;
CREATE TABLE Tours_tutors(
    tour_id             integer REFERENCES Tours(tour_id),
    user_id             integer REFERENCES Users(user_id),
    PRIMARY KEY (tour_id, user_id)
);

DROP TABLE IF EXISTS Team_categories CASCADE;
CREATE TABLE Team_categories(
    team_category_id    serial PRIMARY KEY,
    tour_id             integer REFERENCES Tours(tour_id) NOT NULL,
    category            text NOT NULL,
    UNIQUE (tour_id, category)
);

DROP TABLE IF EXISTS Teams CASCADE;
CREATE TABLE Teams(
    team_id             serial PRIMARY KEY,
    team_category_id    integer REFERENCES Team_categories(team_category_id),
    team_name           text,
    UNIQUE (team_category_id, team_name)

);


--- MENTOR TEAMS ---
DROP TABLE IF EXISTS Mentor_teams CASCADE;
CREATE TABLE Mentor_teams(
    mentor_id           serial PRIMARY KEY,
    mentor_team_name    text,
    notes               text,
    year                integer
);

DROP TABLE IF EXISTS Mentors CASCADE;
CREATE TABLE Mentors(
    mentor_id           integer REFERENCES Mentor_teams(mentor_id),
    user_id             integer REFERENCES Users(user_id),
    PRIMARY KEY (mentor_id, user_id)
);


--- RUSDATABASE ---
DROP TABLE IF EXISTS Russer CASCADE;
CREATE TABLE Russer(
    rus_id              serial PRIMARY KEY,
    year                int NOT NULL,

    filled_by           integer REFERENCES Users(user_id),
    last_updated        timestamp DEFAULT NULL,

    can_contact         boolean DEFAULT TRUE,
    called              boolean DEFAULT FALSE,

    name                text NOT NULL,
    ku_id               int,
    gender              text CHECK (gender IN ('male', 'female', 'other')),
    birthday            date,
    phone               text,
    email               text,
    co                  text,
    address             text,
    zipcode             text,
    city                text,

    moving              boolean DEFAULT FALSE,
    move_time           text,
    new_address         text,
    new_zipcode         text,
    new_city            text,

    vacation            text,
    priority            text,

    gymnasium           text,
    since_gymnasium     text,
    supplementary_exams text,
    merit               text,

    code_experience     text,
    special_needs       text,
    plays_instrument    text,
    other               text,
    tshirt              text,
    paid                boolean DEFAULT FALSE,

    attending_uniday    boolean,
    attending_campus    boolean,
    attending_rustour   boolean,

    rustour             integer REFERENCES Tours(tour_id),
    mentor              integer REFERENCES Mentor_teams(mentor_id)
);

DROP TABLE IF EXISTS Friends CASCADE;
CREATE TABLE Friends(
    rus_id1             integer REFERENCES Russer(rus_id),
    rus_id2             integer REFERENCES Russer(rus_id),
    CHECK (rus_id1 < rus_id2), -- we assume friendship is a symmetric relation, and can thus keep an order in the friendships.
    PRIMARY KEY (rus_id1, rus_id2)
);

DROP TABLE IF EXISTS Friends_of_us CASCADE;
CREATE TABLE Friends_of_us(
    rus_id              integer REFERENCES Russer(rus_id),
    user_id             integer REFERENCES Users(user_id),
    PRIMARY KEY(rus_id, user_id)
);


DROP TABLE IF EXISTS Team_members CASCADE;
CREATE TABLE Team_members(
    team_id             integer REFERENCES Teams(team_id),
    rus_id              integer REFERENCES Russer(rus_id),
    PRIMARY KEY (team_id, rus_id)
);


--- FRONT PAGE ---
DROP TABLE IF EXISTS News CASCADE;
CREATE TABLE News(
    news_id             serial PRIMARY KEY,
    creator             integer REFERENCES Users(user_id),
    created             timestamp NOT NULL,
    last_updated        timestamp DEFAULT NULL,
    title               text,
    body                text
);

DROP TABLE IF EXISTS News_access CASCADE;
CREATE TABLE News_access(
    news_id             integer REFERENCES News(news_id),
    groupname           text REFERENCES Groups(groupname),
    PRIMARY KEY (news_id, groupname)
);

-- --- SCHEDULE ---
-- DROP TABLE IF EXISTS Schedule CASCADE;
-- CREATE TABLE Schedule(
--     s_id                serial PRIMARY KEY,

--     title               text,
--     description         text,

--     created             text,
--     closes              text
-- );

-- DROP TABLE IF EXISTS Schedule_cols CASCADE;
-- CREATE TABLE Schedule_cols(
--     c_id                serial PRIMARY KEY,
--     s_id                integer,
--     parent              integer,
--     label               text,
--     type                integer NOT NULL default 0,
--     FOREIGN KEY(parent) REFERENCES Schedule_cols(s_id),
--     FOREIGN KEY(c_id) REFERENCES Schedule(s_id)
-- );

-- DROP TABLE IF EXISTS Schedule_answers CASCADE;
-- CREATE TABLE Schedule_answers(
--     user                text REFERENCES Users(username),
--     c_id                integer REFERENCES Schedule_cols(c_id),
--     answer              int
-- );



--- BOOKKEEPER ---
DROP TABLE IF EXISTS Books CASCADE;
CREATE TABLE Books(
    book_id             serial PRIMARY KEY,
    creator             integer REFERENCES Users(user_id),
    created             timestamp NOT NULL,
    title               text,
    description         text
);

DROP TABLE IF EXISTS Entries CASCADE;
CREATE TABLE Entries(
    entry_id            serial PRIMARY KEY,
    book_id             integer REFERENCES Books(book_id) NOT NULL,
    date                date,
    creditor            integer REFERENCES Users(user_id),
    description         text,
    amount_text         text, -- The unevaluated text,
    amount              integer -- and its result.
);


DROP TABLE IF EXISTS Debts CASCADE;
CREATE TABLE Debts(
    entry_id            integer REFERENCES Entries(entry_id),
    debtor              integer REFERENCES Users(user_id),
    share_text          text,  -- The unevaluated text,
    share               integer, -- and its result.
    PRIMARY KEY (entry_id, debtor)
);

DROP TABLE IF EXISTS Book_participants CASCADE;
CREATE TABLE Book_participants(
    book_id             integer REFERENCES Books(book_id),
    participant         integer REFERENCES Users(user_id),
    PRIMARY KEY (book_id, participant)
);

DROP TABLE IF EXISTS Payments CASCADE;
CREATE TABLE Payments(
    book_id             integer REFERENCES Books(book_id),
    date                date,
    creditor            integer REFERENCES Users(user_id),
    debtor              integer REFERENCES Users(user_id),
    amount              integer,
    confirmed           text CHECK (confirmed in ('confirmed', 'rejected', 'unconfirmed')),
    PRIMARY KEY (book_id, creditor, debtor)
);

COMMIT;
