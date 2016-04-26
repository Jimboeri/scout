DROP TABLE unit;
DROP SEQUENCE unit_seq;

CREATE TABLE unit (
  unit_id	integer PRIMARY KEY,
  group_id	integer REFERENCES groupdef,
  name		varchar(60),
  sect_cd	char(1) REFERENCES section,
  meet_time	varchar(60),
  curr_memb	integer,
  start_age	real,
  end_age	real,
  award_remind	date
);

CREATE SEQUENCE unit_seq start 1;

GRANT SELECT,UPDATE,INSERT,DELETE ON unit TO apache;
GRANT SELECT,UPDATE,INSERT,DELETE ON unit_seq TO apache;

INSERT INTO unit VALUES (nextval('unit_seq'), 1, 'Taiotea Keas', 'K', 'Monday at 6:00 p.m.', 6.0, 8.0);
INSERT INTO unit VALUES (nextval('unit_seq'), 1, 'Taiotea Cubs', 'C');
INSERT INTO unit VALUES (nextval('unit_seq'), 1, 'Taiotea Scouts', 'S');
