DROP TABLE if EXISTS Vejledere;
CREATE TABLE Vejledere(
       --vid            integer PRIMARY KEY AUTOINCREMENT,
       username       string PRIMARY KEY NOT NULL,
       password       string NOT NULL,
       admin          int NOT NULL,

       navn           string
);
