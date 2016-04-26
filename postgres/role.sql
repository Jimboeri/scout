DROP INDEX role_indiv;
DROP TABLE role;
DROP SEQUENCE role_seq;

CREATE TABLE role (
  role_id	integer PRIMARY KEY,
  level_ref	char(1),
  level_id	integer,
  scout_id	integer REFERENCES scout ON DELETE CASCADE,
  security	integer,
  title		varchar(100),
  last_update	date,
  dt_appt	date,
  role_ref	integer
);

CREATE SEQUENCE role_seq START 1;
CREATE UNIQUE INDEX role_indiv ON role (level_ref, level_id, scout_id);

GRANT SELECT,UPDATE,INSERT,DELETE ON role TO apache;
GRANT SELECT,UPDATE,INSERT,DELETE ON role_seq TO apache;

INSERT INTO role VALUES (nextval('role_seq'), 'U', 1, 1, 1, 'Kea leader');
INSERT INTO role VALUES (nextval('role_seq'), 'G', 1, 1, 1, 'Committee member');

