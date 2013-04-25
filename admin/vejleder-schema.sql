DROP TABLE if EXISTS Vejledere;
CREATE TABLE Vejledere(
       vid            integer PRIMARY KEY AUTOINCREMENT,
       username       string UNIQUE NOT NULL,
       password       string NOT NULL,
       navn           string,
       admin          int NOT NULL
);
