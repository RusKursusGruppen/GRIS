-- Run this to reset/create the database.

DROP TABLE if EXISTS Russer;
CREATE TABLE Russer(
     uid             integer PRIMARY KEY AUTOINCREMENT,

     navn            string NOT NULL,
     udfyldt_af      string,
     opringet        integer NOT NULL,
     co              string,
     addrese         string,
     postnummer      integer,
     by              string,

     flyttedato      string,
     ny_adresse      string,
     ny_postnummer   integer,
     ny_by           string,

     tlf             string,
     email           string,

     foedselsdato    string,

     ferie           string,
     prioritet       string,

     gymnasie        string,
     lavet_efter     string,

     kodeerfaring    string,
     saerlige_behov  string,
     spiller_musik   string,
     andet           string,

     deltager_unidag integer,
     deltager_campus integer,
     deltager_hytte  integer,

     rustur          REFERENCES Ture(tid),
     tjansehold      REFERENCES Tjansehold(tj_id)
);


DROP TABLE if EXISTS Kender;
CREATE TABLE Kender(
       uid1          REFERENCES Russer(uid),
       uid2          REFERENCES Russer(uid)
);

DROP TABLE if EXISTS Ture;
CREATE TABLE Ture(
       tid           integer PRIMARY KEY AUTOINCREMENT,
       tur_navn      string
);

DROP TABLE if EXISTS Tjansehold;
CREATE TABLE Tjansehold(
       tj_id        integer PRIMARY KEY AUTOINCREMENT,
       tid           REFERENCES Ture(tid),
       navn          string

);

DROP TABLE if EXISTS Vejledere;
CREATE TABLE Vejledere(
       vid           integer PRIMARY KEY AUTOINCREMENT,
       navn          string,
       rustur        REFERENCES Ture(tid)
);
