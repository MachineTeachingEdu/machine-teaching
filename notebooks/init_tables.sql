-- problems table
CREATE TABLE
IF NOT EXISTS problem (
 id integer PRIMARY KEY,
 title text NOT NULL,
 content text NOT NULL,
 difficulty text NULL,
 link text NOT NULL,
 retrieved_date timestamp,
 crawler text NOT NULL,
 hint text NULL,
 unique (title, content)
);

-- solutions table
CREATE TABLE
IF NOT EXISTS solution (
 id integer PRIMARY KEY,
 content text,
 problem_id integer NOT NULL,
 link text NOT NULL,
 retrieved_date timestamp NOT NULL,
 ignore boolean default 0 check(ignore in (0,1)),
 FOREIGN KEY (problem_id) REFERENCES problem (id)
 unique (problem_id, content)
);

-- alter problems table
-- alter table problem add column hint text NULL;
-- CREATE TABLE
-- IF NOT EXISTS problem2 (
 -- id integer PRIMARY KEY,
 -- title text NOT NULL,
 -- content text NOT NULL,
 -- difficulty text NULL,
 -- link text NOT NULL,
 -- retrieved_date timestamp,
 -- crawler text NOT NULL,
 -- hint text NULL,
 -- unique (title, content)
-- );
-- INSERT INTO problem2 SELECT * FROM problem;
-- DROP TABLE problem;
-- ALTER TABLE problem2 RENAME TO problem;
