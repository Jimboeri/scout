DROP TABLE groupdef;
DROP SEQUENCE group_seq;

CREATE TABLE groupdef (
  group_id	integer PRIMARY KEY,
  dist_id	integer REFERENCES district,
  name		varchar(60),
  addr1		varchar(60),
  addr2		varchar(60),
  addr3		varchar(60),
  p_code	char(4),
  telephone	varchar(40),
  curr_memb	integer
);

CREATE SEQUENCE group_seq start 1

GRANT SELECT,UPDATE,INSERT,DELETE ON groupdef TO apache;
GRANT SELECT,UPDATE,INSERT,DELETE ON group_seq TO apache;

INSERT INTO groupdef VALUES (nextval('group_seq'), 1, 'Taiotea Scouts');
