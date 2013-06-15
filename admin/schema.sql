-- Run this to reset/create the database.

DROP TABLE IF EXISTS Russer;
CREATE TABLE Russer(
    rid                 integer PRIMARY KEY AUTOINCREMENT,

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

    uniday              integer,
    campus              integer,
    tour                integer,

    rustour             REFERENCES Ture(tid),
    dutyteam            REFERENCES Tjansehold(tj_id)
);


-- It must hold that uid1 < uid2
DROP TABLE IF EXISTS Friends;
CREATE TABLE Friends(
    rid1                REFERENCES Russer(rid),
    rid2                REFERENCES Russer(rid)
);

DROP TABLE IF EXISTS Tours;
CREATE TABLE Tours(
    tid                 integer PRIMARY KEY AUTOINCREMENT,
    tour_name           string
);

DROP TABLE IF EXISTS Dutyteams;
CREATE TABLE Dutyteams(
    tjid                integer PRIMARY KEY AUTOINCREMENT,
    tid                 REFERENCES Ture(tid),
    name                string

);


DROP TABLE IF EXISTS Users;
CREATE TABLE Users(
    --vid               integer PRIMARY KEY AUTOINCREMENT,
    username            string PRIMARY KEY NOT NULL,
    password            string NOT NULL,
    admin               int NOT NULL default 0,
    tutor               int NOT NULL default 0,
    mentor              int NOT NULL default 0,

    name                string,
    driverslicence      int NOT NULL default 0,
    address             string,
    zipcode             string,
    city                string,
    phone               string,
    email               string,
    birthday            string,

    diku_age            int,
    earlier_tours       string, --sepererat med semicolaer (pepsi)

    rustour             REFERENCES Ture(tid)
);

DROP TABLE IF EXISTS News;
CREATE TABLE News(
    creator             REFERENCES Users(username),
    created             string NOT NULL,
    for_tutors          int NOT NULL default 1,
    for_mentors         int NOT NULL default 0,
    title               string,
    text                string
);

DROP TABLE IF EXISTS Schedule;
CREATE TABLE Schedule(
    s_id                integer PRIMARY KEY AUTOINCREMENT,

    title               string,
    description         string,

    created             string,
    closes              string
);
