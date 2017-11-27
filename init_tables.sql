-- problems table
CREATE TABLE
IF NOT EXISTS problem (
 id integer PRIMARY KEY,
 title text NULL,
 content text NOT NULL,
 difficulty text NULL,
 link text NOT NULL,
 retrieved_date timestamp,
 crawler text NOT NULL,
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
