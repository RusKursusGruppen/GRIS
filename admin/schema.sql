-- Run this to reset/create the database.

DROP TABLE if EXISTS Russer;
CREATE TABLE Russer(
     rid              integer PRIMARY KEY AUTOINCREMENT,

     navn             string NOT NULL,
     udfyldt_af       string,
     opringet         integer NOT NULL,
     co               string,
     addrese          string,
     postnummer       string,
     by               string,

     flytte_tidspunkt string,
     ny_adresse       string,
     ny_postnummer    string,
     ny_by            string,

     tlf              string,
     email            string,

     foedselsdato     string,

     ferie            string,
     prioritet        string,

     gymnasie         string,
     lavet_efter      string,

     kodeerfaring     string,
     saerlige_behov   string,
     spiller_musik    string,
     andet            string,

     deltager_unidag  integer,
     deltager_campus  integer,
     deltager_hytte   integer,

     rustur           REFERENCES Ture(tid),
     tjansehold       REFERENCES Tjansehold(tj_id)
);


-- It must hold that uid1 < uid2
DROP TABLE if EXISTS Kender;
CREATE TABLE Kender(
       rid1           REFERENCES Russer(rid),
       rid2           REFERENCES Russer(rid)
);

DROP TABLE if EXISTS Ture;
CREATE TABLE Ture(
       tid            integer PRIMARY KEY AUTOINCREMENT,
       tur_navn       string
);

DROP TABLE if EXISTS Tjansehold;
CREATE TABLE Tjansehold(
       tj_id          integer PRIMARY KEY AUTOINCREMENT,
       tid            REFERENCES Ture(tid),
       navn           string

);


DROP TABLE if EXISTS Users;
CREATE TABLE Users(
       --vid            integer PRIMARY KEY AUTOINCREMENT,
       username       string PRIMARY KEY NOT NULL,
       password       string NOT NULL,
       admin          int NOT NULL default 0,
       vejleder       int NOT NULL default 0,
       mentor         int NOT NULL default 0,

       navn           string,
       koerekort      int NOT NULL default 0,
       addresse       string,
       postnummer     string,
       by             string,
       tlf            string,
       email          string,
       foedselsdato   string,

       diku_alder     int,
       tidligere_ture string, --sepererat med semicolaer

       rustur         REFERENCES Ture(tid)

);
