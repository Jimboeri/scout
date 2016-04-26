DROP TABLE district;
DROP SEQUENCE dist_seq;

CREATE TABLE district (
  dist_id	integer PRIMARY KEY,
  area_id	integer REFERENCES area,
  name		varchar(60),
  curr_memb	integer
);

CREATE SEQUENCE group_seq start 1

GRANT SELECT,UPDATE,INSERT,DELETE ON district TO apache;
GRANT SELECT,UPDATE,INSERT,DELETE ON dist_seq TO apache;

INSERT INTO district VALUES (nextval('dist_seq'), 1, 'Moananui');
INSERT INTO district VALUES (nextval('dist_seq'), 1, 'North Harbour');

