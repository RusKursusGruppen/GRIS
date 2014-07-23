BEGIN;
-- Run this to reset/create the database.
-- PRAGMA foreign_keys = ON;

--- USERS ---
DROP TABLE IF EXISTS Users;
CREATE TABLE Users(
    username            text PRIMARY KEY,
    password            text NOT NULL,

    name                text DEFAULT 'RUS',
    driverslicence      int NOT NULL default 0,
    address             text,
    zipcode             text,
    city                text,
    phone               text,
    email               text,
    birthday            text,

    diku_age            text,
    earlier_tours       text, --sepererat med semicolaer (pepsi)
    about_me            text,

    deleted             int DEFAULT 0 -- Field for marking a user as deleted
);

DROP TABLE IF EXISTS Groups;
CREATE TABLE Groups(
       groupname        text PRIMARY KEY
);
INSERT INTO Groups(groupname) VALUES('all');
INSERT INTO Groups(groupname) VALUES('admin');
INSERT INTO Groups(groupname) VALUES('rkg');
INSERT INTO Groups(groupname) VALUES('tutor');
INSERT INTO Groups(groupname) VALUES('mentor');


DROP TABLE IF EXISTS User_groups;
CREATE TABLE User_groups(
       username         text REFERENCES Users(username),
       groupname        text REFERENCES Groups(groupname),
       PRIMARY KEY (username, groupname)
);


DROP TABLE IF EXISTS User_creation_keys;
CREATE TABLE User_creation_keys(
       key              text PRIMARY KEY,
       created          text NOT NULL
);



--- TOUR INFORMATION ---
DROP TABLE IF EXISTS Tours;
CREATE TABLE Tours(
    t_id                serial PRIMARY KEY,
    tour_name           text,
    type                text CHECK(type IN ('p', 't', 'm')),
    year                integer
);

DROP TABLE IF EXISTS Tours_tutors;
CREATE TABLE Tours_tutors(
   t_id                 serial REFERENCES Tours(t_id),
   username             text REFERENCES Users(username),
   PRIMARY KEY (t_id, username)
);

DROP TABLE IF EXISTS Dutyteams;
CREATE TABLE Dutyteams(
    tj_id               serial PRIMARY KEY,
    t_id                serial REFERENCES Tours(t_id) NOT NULL,
    name                text
);



--- RUSDATABASE ---
DROP TABLE IF EXISTS Russer;
CREATE TABLE Russer(
    r_id                serial PRIMARY KEY,

    name                text NOT NULL,
    filled_by           text,
    called              integer NOT NULL,
    co                  text,
    address             text,
    zipcode             text,
    city                text,

    move_time           text,
    new_address         text,
    new_zipcode         text,
    new_city            text,

    phone               text,
    email               text,

    birthday            text,

    vacation            text,
    priority            text,

    gymnasium           text,
    since_gymnasium     text,

    code_experience     text,
    special_needs       text,
    plays_instrument    text,
    other               text,
    tshirt              text,
    paid                integer NOT NULL default 0,

    attending_uniday    integer NOT NULL default 0,
    attending_campus    integer NOT NULL default 0,
    attending_rustour   integer NOT NULL default 0,

    rustour             serial REFERENCES Tours(t_id),
    dutyteam            serial REFERENCES Dutyteams(tj_id)
);

DROP TABLE IF EXISTS Friends;
CREATE TABLE Friends(
    r_id1               serial REFERENCES Russer(r_id),
    r_id2               serial REFERENCES Russer(r_id),
    CHECK (r_id1 < r_id2), -- we assume friendship is a symmetric relation, and can thus keep an order in the friendships.
    PRIMARY KEY (r_id1, r_id2)
);

DROP TABLE IF EXISTS Friends_of_us;
CREATE TABLE Friends_of_us(
    r_id                serial REFERENCES Russer(r_id),
    username            text REFERENCES Users(username),
    PRIMARY KEY(r_id, username)
);




--- FRONT PAGE ---
DROP TABLE IF EXISTS News;
CREATE TABLE News(
    n_id                serial PRIMARY KEY,
    creator             text REFERENCES Users(username),
    created             text NOT NULL,
    title               text,
    text                text
);

DROP TABLE IF EXISTS News_access;
CREATE TABLE News_access(
    n_id                serial REFERENCES News(n_id),
    groupname           text REFERENCES Groups(groupname),
    PRIMARY KEY (n_id, groupname)
);

-- --- SCHEDULE ---
-- DROP TABLE IF EXISTS Schedule;
-- CREATE TABLE Schedule(
--     s_id                serial PRIMARY KEY,

--     title               text,
--     description         text,

--     created             text,
--     closes              text
-- );

-- DROP TABLE IF EXISTS Schedule_cols;
-- CREATE TABLE Schedule_cols(
--     c_id                serial PRIMARY KEY,
--     s_id                integer,
--     parent              integer,
--     label               text,
--     type                integer NOT NULL default 0,
--     FOREIGN KEY(parent) REFERENCES Schedule_cols(s_id),
--     FOREIGN KEY(c_id) REFERENCES Schedule(s_id)
-- );

-- DROP TABLE IF EXISTS Schedule_answers;
-- CREATE TABLE Schedule_answers(
--     user                text REFERENCES Users(username),
--     c_id                serial REFERENCES Schedule_cols(c_id),
--     answer              int
-- );



--- BOOKKEEPER ---
DROP TABLE IF EXISTS Books;
CREATE TABLE Books(
    b_id                serial PRIMARY KEY,
    creator             text REFERENCES Users(username),
    created             text,
    title               text,
    description         text
);

DROP TABLE IF EXISTS Entries;
CREATE TABLE Entries(
    e_id                serial PRIMARY KEY,
    b_id                serial REFERENCES Books(b_id) NOT NULL,
    date                text,
    creditor            text REFERENCES Users(username),
    description         text,
    amount_text       text, -- The unevaluated text,
    amount              integer -- and its result.
);


DROP TABLE IF EXISTS Debts;
CREATE TABLE Debts(
    e_id                serial REFERENCES Entries(e_id),
    debtor              text REFERENCES Users(username),
    share_text        text,  -- The unevaluated text,
    share               integer, -- and its result.
    PRIMARY KEY (e_id, debtor)
);

DROP TABLE IF EXISTS Book_participants;
CREATE TABLE Book_participants(
    b_id                serial REFERENCES Books(b_id),
    participant         text REFERENCES Users(username),
    PRIMARY KEY (b_id, participant)
);

DROP TABLE IF EXISTS Payments;
CREATE TABLE Payments(
    b_id                serial REFERENCES Books(b_id),
    date                text,
    creditor            text REFERENCES Users(username),
    debtor              text REFERENCES Users(users),
    amount              integer,
    confirmed           integer NOT NULL default 0, --0 not confirmed, -1 rejected, 1 confirmed
    PRIMARY KEY (b_id, creditor, debtor)
);

COMMIT;
