CREATE TABLE IF NOT EXISTS disease (
	id integer PRIMARY KEY,
	name text NOT NULL
);

CREATE TABLE IF NOT EXISTS article (
    id integer PRIMARY KEY,
    pmid text NOT NULL,
    title text,
	abstract text,
    year integer,
    doi text
);

CREATE TABLE IF NOT EXISTS disease_article (
	idDisease integer,
	idArticle integer,
	FOREIGN KEY(idDisease) REFERENCES disease(id),
	FOREIGN KEY(idArticle) REFERENCES article(id)
);

CREATE TABLE IF NOT EXISTS author (
    id integer PRIMARY KEY,
    name text NOT NULL,
    affiliation text
);

CREATE TABLE IF NOT EXISTS author_article (
	idAuthor integer,
	idArticle integer,
	FOREIGN KEY(idAuthor) REFERENCES author(id),
	FOREIGN KEY(idArticle) REFERENCES article(id)
);

