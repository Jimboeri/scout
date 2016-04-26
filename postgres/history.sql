DROP TABLE history;
DROP SEQUENCE hist_seq;

CREATE TABLE history (
  hist_id	integer PRIMARY KEY,
  conn_id	integer,
  action	integer,
  update_tm	timestamp without time zone, 
  scout_id	integer,
  id1		integer,
  id2		integer,
  id3		integer
);

CREATE SEQUENCE hist_seq START 1;

GRANT SELECT,UPDATE,INSERT,DELETE ON history TO apache;
GRANT SELECT,UPDATE,INSERT,DELETE ON hist_seq TO apache;

