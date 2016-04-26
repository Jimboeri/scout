DROP TABLE message;
DROP SEQUENCE msg_seq;

CREATE TABLE message (
  msg_id	integer PRIMARY KEY,
  create_tm	timestamp without time zone, 
  from_id	integer,
  to_id		integer,
  for_sysadmin	integer,
  for_developer	integer,
  status	char,
  notify	integer,
  name		varchar(80),
  email		varchar(80),
  telephone	varchar(80),
  subject	varchar(80),
  body		text,
  last_update	timestamp without time zone,
  msg_response	text
);

CREATE SEQUENCE msg_seq START 1;

GRANT SELECT,UPDATE,INSERT,DELETE ON message TO apache;
GRANT SELECT,UPDATE,INSERT,DELETE ON msg_seq TO apache;

