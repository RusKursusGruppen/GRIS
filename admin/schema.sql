-- Run this to reset/create the database.
PRAGMA foreign_keys = ON;

--- RUSDATABASE ---
DROP TABLE IF EXISTS Russer;
CREATE TABLE Russer(
    r_id                integer PRIMARY KEY AUTOINCREMENT,

    name                string NOT NULL,
    filled_by           string,
    called              integer NOT NULL,
    co                  string,
    address             string,
    zipcode             string,
    city                string,

    move_time           string,
    new_address         string,
    new_zipcode         string,
    new_city            string,

    phone               string,
    email               string,

    birthday            string,

    vacation            string,
    priority            string,

    gymnasium           string,
    since_gymnasium     string,

    code_experience     string,
    special_needs       string,
    plays_instrument    string,
    other               string,
    tshirt              string,
    paid                integer NOT NULL default 0,

    uniday              integer,
    campus              integer,
    tour                integer,

    rustour             REFERENCES Tours(t_id),
    dutyteam            REFERENCES Dutyteams(tj_id)
);


-- It must hold that uid1 < uid2
DROP TABLE IF EXISTS Friends;
CREATE TABLE Friends(
    r_id1               REFERENCES Russer(r_id),
    r_id2               REFERENCES Russer(r_id)
);

DROP TABLE IF EXISTS Tours;
CREATE TABLE Tours(
    t_id                integer PRIMARY KEY AUTOINCREMENT,
    tour_name           string
);

DROP TABLE IF EXISTS Dutyteams;
CREATE TABLE Dutyteams(
    tj_id               integer PRIMARY KEY AUTOINCREMENT,
    t_id                REFERENCES Tours(t_id),
    name                string

);



--- USERS ---
DROP TABLE IF EXISTS Users;
CREATE TABLE Users(
    username            string PRIMARY KEY NOT NULL,
    password            string NOT NULL,
    admin               int NOT NULL default 0,
    rkg                 int NOT NULL default 0,
    tutor               int NOT NULL default 0,
    mentor              int NOT NULL default 0,

    name                string DEFAULT "RUS",
    driverslicence      int NOT NULL default 0,
    address             string,
    zipcode             string,
    city                string,
    phone               string,
    email               string,
    birthday            string,

    diku_age            string,
    earlier_tours       string, --sepererat med semicolaer (pepsi)
    about_me            string

    rustour             REFERENCES Tours(t_id),

    deleted             int -- Field for marking a user as deleted
);

DROP TABLE IF EXISTS User_creation_keys;
CREATE TABLE User_creation_keys(
       key              string UNIQUE NOT NULL,
       created          string NOT NULL
);

--- FRONT PAGE ---
DROP TABLE IF EXISTS News;
CREATE TABLE News(
    creator             REFERENCES Users(username),
    created             string NOT NULL,
    for_tutors          int NOT NULL default 1,
    for_mentors         int NOT NULL default 0,
    title               string,
    text                string
);

--- SCHEDULE ---
DROP TABLE IF EXISTS Schedule;
CREATE TABLE Schedule(
    s_id                integer PRIMARY KEY AUTOINCREMENT,

    title               string,
    description         string,

    created             string,
    closes              string
);

DROP TABLE IF EXISTS Schedule_cols;
CREATE TABLE Schedule_cols(
    c_id                integer PRIMARY KEY AUTOINCREMENT,
    s_id                REFERENCES Schedule(s_id),
    parent              REFERENCES Schedule_cols(s_id),
    label               string,
    type                integer NOT NULL default 0
);

DROP TABLE IF EXISTS Schedule_answers;
CREATE TABLE Schedule_answers(
    user                REFERENCES Users(username),
    c_id                REFERENCES Schedule_cols(c_id),
    answer              int
);



--- BOOKKEEPER ---
DROP TABLE IF EXISTS Books;
CREATE TABLE Books(
    b_id                integer PRIMARY KEY AUTOINCREMENT,
    creator             REFERENCES Users(username),
    created             string,
    title               string,
    description         string
);

DROP TABLE IF EXISTS Entries;
CREATE TABLE Entries(
    e_id                integer PRIMARY KEY AUTOINCREMENT,
    b_id                REFERENCES Books(b_id) NOT NULL,
    created             string,
    creditor            REFERENCES Users(username),
    description         string,
    amount              integer
);


DROP TABLE IF EXISTS Debts;
CREATE TABLE Debts(
    e_id                REFERENCES Entries(e_id),
    debtor              REFERENCES Users(username),
    share               integer,
    UNIQUE(e_id, debtor) ON CONFLICT REPLACE
);

DROP TABLE If EXISTS Book_participants;
CREATE TABLE Book_participants(
    b_id                integer, -- REFERENCES Books(b_id),
    participant         REFERENCES Users(username),
    UNIQUE(b_id, participant) ON CONFLICT IGNORE
);
